import os
import json
import requests
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import (
    PRO_MODEL, FLASH_MODEL,
    GITHUB_TOKEN, SERPER_API_KEY,
    YOUTUBE_API_KEY, TWILIO_SID,
    TWILIO_AUTH, TWILIO_FROM, TWILIO_TO,
    COMPANY_REQUIREMENTS
)

# ── Model helpers ──────────────────────────────────────────────────────────
def get_flash(): return genai.GenerativeModel(FLASH_MODEL)
def get_pro():   return genai.GenerativeModel(PRO_MODEL)

def call_gemini(model, prompt: str) -> str:
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def safe_json(text: str) -> Any:
    """Parse JSON from Gemini response safely."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except Exception:
                continue
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{") if "{" in text else text.find("[")
        end   = text.rfind("}") if "{" in text else text.rfind("]")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    return {}

# ── TOOL 1: GitHub API ─────────────────────────────────────────────────────
def fetch_github_profile(username: str) -> Dict[str, Any]:
    """Fetch user profile, repos, and languages from GitHub API."""
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    headers["Accept"] = "application/vnd.github.v3+json"

    base = "https://api.github.com"
    result = {
        "username": username, "repos": [],
        "languages": {}, "total_stars": 0,
        "profile": {}, "error": None
    }

    # User profile
    try:
        r = requests.get(f"{base}/users/{username}", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            result["profile"] = {
                "name":       data.get("name", username),
                "bio":        data.get("bio", ""),
                "public_repos": data.get("public_repos", 0),
                "followers":  data.get("followers", 0),
            }
        else:
            result["error"] = f"GitHub user not found: {r.status_code}"
            return result
    except Exception as e:
        result["error"] = str(e)
        return result

    # Repos
    try:
        r = requests.get(
            f"{base}/users/{username}/repos",
            headers=headers,
            params={"sort": "updated", "per_page": 30},
            timeout=10
        )
        if r.status_code == 200:
            repos = r.json()
            for repo in repos[:15]:  # top 15
                if repo.get("fork"):
                    continue

                repo_data = {
                    "name":        repo["name"],
                    "description": repo.get("description") or "",
                    "language":    repo.get("language") or "Unknown",
                    "stars":       repo.get("stargazers_count", 0),
                    "topics":      repo.get("topics", []),
                    "updated":     repo.get("updated_at", ""),
                    "url":         repo.get("html_url", ""),
                }

                # Get languages breakdown
                try:
                    lr = requests.get(
                        repo["languages_url"],
                        headers=headers, timeout=5
                    )
                    if lr.status_code == 200:
                        langs = lr.json()
                        for lang, lines in langs.items():
                            result["languages"][lang] = (
                                result["languages"].get(lang, 0) + lines
                            )
                        repo_data["languages"] = list(langs.keys())
                except Exception:
                    repo_data["languages"] = [repo.get("language", "Unknown")]

                # Get README
                try:
                    rr = requests.get(
                        f"{base}/repos/{username}/{repo['name']}/readme",
                        headers={**headers, "Accept": "application/vnd.github.raw"},
                        timeout=5
                    )
                    if rr.status_code == 200:
                        repo_data["readme"] = rr.text[:800]
                except Exception:
                    repo_data["readme"] = ""

                result["total_stars"] += repo.get("stargazers_count", 0)
                result["repos"].append(repo_data)
    except Exception as e:
        result["error"] = str(e)

    return result

# ── TOOL 2: Web Search (Serper) ────────────────────────────────────────────
def web_search(query: str, num: int = 5) -> List[Dict[str, Any]]:
    """Search the web using Serper API."""
    if not SERPER_API_KEY:
        return [{"title": "Serper key missing", "snippet": "", "link": ""}]
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY":   SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            json={"q": query, "num": num},
            timeout=10
        )
        data = r.json()
        return [
            {
                "title":   item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link":    item.get("link", "")
            }
            for item in data.get("organic", [])[:num]
        ]
    except Exception as e:
        return [{"title": f"Search error: {e}", "snippet": "", "link": ""}]

# ── TOOL 3: YouTube Search ─────────────────────────────────────────────────
def search_youtube_rich(
    topic: str,
    max_results: int = 8
) -> List[Dict[str, Any]]:
    """
    Search YouTube for long-form (60min+) educational videos.
    Returns rich data including duration, views, thumbnail.
    """
    if not YOUTUBE_API_KEY:
        return []

    try:
        # Step 1: Search
        search_r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part":          "snippet",
                "q":             f"{topic} complete tutorial concepts explained 2024",
                "type":          "video",
                "maxResults":    max_results,
                "order":         "relevance",
                "key":           YOUTUBE_API_KEY,
                "videoDuration": "long",      # YouTube API = 20min+
                "relevanceLanguage": "en",
                "videoDefinition": "high",
            },
            timeout=10
        )
        search_data = search_r.json()
        items = search_data.get("items", [])
        if not items:
            return []

        # Step 2: Get video details (duration, views)
        video_ids = [item["id"]["videoId"] for item in items]
        details_r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part":  "contentDetails,statistics,snippet",
                "id":    ",".join(video_ids),
                "key":   YOUTUBE_API_KEY,
            },
            timeout=10
        )
        details_data = details_r.json()

        results = []
        for detail in details_data.get("items", []):
            vid_id   = detail["id"]
            snippet  = detail.get("snippet", {})
            content  = detail.get("contentDetails", {})
            stats    = detail.get("statistics", {})

            # Parse ISO 8601 duration
            duration_str = content.get("duration", "PT0M")
            minutes = _parse_duration_minutes(duration_str)

            # Only keep videos >= 45 minutes
            if minutes < 45:
                continue

            hours   = minutes // 60
            mins    = minutes % 60
            dur_lbl = (
                f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
            )

            views = int(stats.get("viewCount", 0))
            views_lbl = (
                f"{views/1_000_000:.1f}M views"
                if views >= 1_000_000
                else f"{views//1_000}K views"
                if views >= 1_000
                else f"{views} views"
            )

            results.append({
                "title":     snippet.get("title", ""),
                "channel":   snippet.get("channelTitle", ""),
                "url":       f"https://youtube.com/watch?v={vid_id}",
                "thumbnail": (
                    snippet.get("thumbnails", {})
                           .get("high", {})
                           .get("url", "")
                ),
                "duration":  dur_lbl,
                "minutes":   minutes,
                "views":     views_lbl,
                "published": snippet.get("publishedAt", "")[:10],
                "video_id":  vid_id,
            })

        # Sort by views descending
        results.sort(key=lambda x: x.get("minutes", 0), reverse=True)
        return results[:max_results]

    except Exception as e:
        print(f"YouTube error: {e}")
        return []


def _parse_duration_minutes(duration: str) -> int:
    """Parse ISO 8601 duration (PT1H30M) to total minutes."""
    import re
    hours   = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    total   = 0
    if hours:
        total += int(hours.group(1)) * 60
    if minutes:
        total += int(minutes.group(1))
    return total


# Keep old one as alias for backward compat
def search_youtube(topic: str, max_results: int = 3) -> List[Dict[str, Any]]:
    results = search_youtube_rich(topic, max_results * 2)
    return results[:max_results]

# ── TOOL 4: LeetCode Problems ──────────────────────────────────────────────
def get_leetcode_problems(tag: str, difficulty: str = "Medium") -> List[Dict[str, Any]]:
    """Fetch LeetCode problems by tag using GraphQL API."""
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        filters: $filters
      ) {
        questions: data {
          frontendQuestionId: questionFrontendId
          title
          titleSlug
          difficulty
          topicTags { name slug }
        }
      }
    }
    """
    try:
        r = requests.post(
            "https://leetcode.com/graphql",
            json={
                "query": query,
                "variables": {
                    "categorySlug": "",
                    "limit": 5,
                    "filters": {
                        "tags": [tag],
                        "difficulty": difficulty.upper()
                    }
                }
            },
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com"
            },
            timeout=10
        )
        data = r.json()
        questions = (
            data.get("data", {})
                .get("problemsetQuestionList", {})
                .get("questions", [])
        )
        return [
            {
                "id":         q["frontendQuestionId"],
                "title":      q["title"],
                "difficulty": q["difficulty"],
                "url":        f"https://leetcode.com/problems/{q['titleSlug']}/",
                "tags":       [t["name"] for t in q.get("topicTags", [])]
            }
            for q in questions
        ]
    except Exception as e:
        return [{"title": f"LeetCode error: {e}", "url": "https://leetcode.com"}]

# ── TOOL 5: WhatsApp (Twilio) ──────────────────────────────────────────────
def send_whatsapp(message: str, to_number: str = None) -> bool:
    """Send WhatsApp message via Twilio."""
    if not all([TWILIO_SID, TWILIO_AUTH, TWILIO_FROM]):
        print("Twilio not configured — skipping WhatsApp")
        return False
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_AUTH)
        to = to_number or TWILIO_TO
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=to
        )
        return True
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False

# ── TOOL 6: Skill Extractor (Gemini) ──────────────────────────────────────
def extract_skills_from_github(github_data: Dict[str, Any]) -> List[str]:
    """
    Aggressively extract placement-relevant skills from GitHub data.
    Maps actual languages/repos to skills companies look for.
    """
    # Step 1: Rule-based extraction (fast, reliable)
    detected = set()
    langs = list(github_data.get("languages", {}).keys())
    repos = github_data.get("repos", [])

    # Language → skill mapping
    lang_skill_map = {
        "Python":          ["Python", "Problem Solving"],
        "JavaScript":      ["JavaScript", "Web Development", "Problem Solving"],
        "TypeScript":      ["JavaScript", "TypeScript", "Web Development"],
        "Java":            ["Java", "OOP", "Problem Solving"],
        "C++":             ["C++", "Data Structures", "Problem Solving"],
        "C":               ["C", "Data Structures", "System Programming"],
        "Jupyter Notebook":["Python", "Machine Learning", "Data Analysis"],
        "HTML":            ["Web Development", "Frontend"],
        "CSS":             ["Web Development", "Frontend"],
        "Shell":           ["Linux", "System Programming"],
        "PowerShell":      ["Scripting", "System Programming"],
        "Makefile":        ["Build Systems", "System Programming"],
        "Go":              ["Go", "System Design"],
        "Rust":            ["Rust", "System Programming"],
        "Kotlin":          ["Kotlin", "Android Development", "OOP"],
        "Swift":           ["Swift", "iOS Development"],
        "SQL":             ["SQL", "Database"],
        "R":               ["R", "Data Analysis"],
    }

    for lang in langs:
        if lang in lang_skill_map:
            for skill in lang_skill_map[lang]:
                detected.add(skill)

    # Repo name / description / topic keyword mapping
    keyword_skill_map = {
        "machine learning":   ["Machine Learning", "Python", "Data Structures"],
        "deep learning":      ["Machine Learning", "Python"],
        "neural":             ["Machine Learning", "Python"],
        "yolo":               ["Machine Learning", "Computer Vision", "Python"],
        "robot":              ["Python", "Problem Solving"],
        "detection":          ["Machine Learning", "Python"],
        "web":                ["Web Development", "JavaScript"],
        "api":                ["Backend Development", "System Design basics"],
        "firewall":           ["Computer Networks", "System Programming"],
        "network":            ["Computer Networks"],
        "database":           ["DBMS", "SQL"],
        "sql":                ["SQL", "DBMS"],
        "sorting":            ["Data Structures", "Algorithms"],
        "tree":               ["Data Structures", "Algorithms"],
        "graph":              ["Data Structures", "Algorithms"],
        "version control":    ["Git", "Problem Solving"],
        "vcs":                ["Git", "Problem Solving"],
        "task manager":       ["OOP", "Problem Solving"],
        "manager":            ["OOP", "Problem Solving"],
        "event":              ["Web Development", "JavaScript"],
        "college":            ["Web Development"],
        "crop":               ["Machine Learning", "Python"],
        "weed":               ["Machine Learning", "Computer Vision"],
        "chat":               ["Web Development", "Backend Development"],
        "mininet":            ["Computer Networks", "Python"],
        "vpn":                ["Computer Networks", "Security"],
        "os":                 ["Operating Systems"],
        "scheduler":          ["Operating Systems", "Algorithms"],
        "compiler":           ["Data Structures", "Algorithms", "OOP"],
    }

    for repo in repos:
        combined = (
            f"{repo.get('name','')} "
            f"{repo.get('description','')} "
            f"{' '.join(repo.get('topics', []))} "
            f"{repo.get('readme','')[:300]}"
        ).lower()

        for keyword, skills in keyword_skill_map.items():
            if keyword in combined:
                for s in skills:
                    detected.add(s)

    # Always add basics if they have any repos at all
    if repos:
        detected.add("Basic Programming")
        detected.add("Git")
        detected.add("Problem Solving")

    # If they have Jupyter notebooks, they definitely know Python
    if "Jupyter Notebook" in langs or "Python" in langs:
        detected.add("Python")
        detected.add("Machine Learning")

    # Step 2: Use Gemini Flash to supplement (not replace) rule-based
    try:
        model = get_flash()
        repos_summary = []
        for repo in repos[:8]:
            repos_summary.append(
                f"- {repo.get('name','')} "
                f"({repo.get('language','')}) "
                f"Topics:{repo.get('topics',[])} "
                f"Desc:{repo.get('description','')}"
            )

        prompt = f"""
Student's GitHub profile:
Languages: {langs}
Repos: {chr(10).join(repos_summary)}
Already detected skills: {list(detected)}

Add any additional placement-relevant skills I might have missed.
Focus on: DSA, System Design, OOP, DBMS, OS, CN, specific languages, frameworks.
Return ONLY a JSON array of additional skill strings. Max 10.
Example: ["OOP", "DBMS", "Algorithms"]
Return [] if nothing to add.
"""
        result = call_gemini(model, prompt)
        extra  = safe_json(result)
        if isinstance(extra, list):
            for s in extra:
                if isinstance(s, str):
                    detected.add(s)
    except Exception as e:
        print(f"Gemini skill extraction warning: {e}")

    return sorted(list(detected))

# ── TOOL 7: Gap Scorer ─────────────────────────────────────────────────────
def score_skills_against_company(
    detected_skills: List[str],
    company: str,
    cgpa: float
) -> Dict[str, Any]:
    """Score detected skills against a company's requirements."""
    if company not in COMPANY_REQUIREMENTS:
        return {}

    req = COMPANY_REQUIREMENTS[company]
    required = req["skills_required"]
    detected_lower = [s.lower() for s in detected_skills]

    matched, missing = [], []
    for skill in required:
        if any(skill.lower() in d or d in skill.lower() for d in detected_lower):
            matched.append(skill)
        else:
            missing.append(skill)

    match_pct    = (len(matched) / len(required) * 100) if required else 0
    cgpa_ok      = cgpa >= req["min_cgpa"]
    is_eligible  = cgpa_ok and match_pct >= 40

    return {
        "company":         company,
        "tier":            req["tier"],
        "is_eligible":     is_eligible,
        "cgpa_ok":         cgpa_ok,
        "skill_match_pct": round(match_pct, 1),
        "matched_skills":  matched,
        "missing_skills":  missing,
        "ctc_range":       req["ctc_range"],
        "difficulty":      req["difficulty"],
        "pattern":         req["pattern"],
        "leetcode_tags":   req["leetcode_tags"],
        "typical_questions": req["typical_questions"],
        "recommended_action": (
            "Ready to apply — polish your projects"
            if is_eligible and match_pct > 70
            else "Need 4-6 weeks focused prep"
            if is_eligible
            else f"Work on CGPA (need {req['min_cgpa']}) and core skills"
        )
    }