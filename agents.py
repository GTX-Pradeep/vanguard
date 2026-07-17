from langgraph.graph import StateGraph, END
from state import VanguardState
from tools import (
    fetch_github_profile, extract_skills_from_github,
    score_skills_against_company, web_search,
    search_youtube, get_leetcode_problems,
    send_whatsapp, get_flash, get_pro,
    call_gemini, safe_json
)
from config import COMPANY_REQUIREMENTS
from typing import Dict, Any
import json

# ── AGENT 1: GitHub Intelligence ──────────────────────────────────────────
def github_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    # Merge intake data into known_skills for better gap analysis
    intake = s.get("_intake_data", {})
    known  = intake.get("known_skills", [])
    if known:
        existing = list(s.get("detected_skills", []))
        for sk in known:
            if sk not in existing:
                existing.append(sk)
        s["detected_skills"] = existing
    # ... rest stays same
    s["current_agent"] = "GitHub Intelligence Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("🔍 GitHub Agent: Fetching your repositories...")

    username = s.get("github_username", "")
    if not username:
        s["errors"] = list(s.get("errors", [])) + ["No GitHub username provided"]
        s["completed_agents"] = list(s.get("completed_agents", [])) + ["github_agent"]
        s["agent_logs"] = logs
        return s

    # Fetch from GitHub API
    github_data = fetch_github_profile(username)
    if github_data.get("error"):
        logs.append(f"⚠️ GitHub warning: {github_data['error']}")

    # Extract skills using Gemini
    detected = extract_skills_from_github(github_data)

    s["github_raw_data"]  = github_data
    s["github_repos"]     = github_data.get("repos", [])
    s["github_languages"] = github_data.get("languages", {})
    s["detected_skills"]  = detected
    s["completed_agents"] = list(s.get("completed_agents", [])) + ["github_agent"]

    logs.append(
        f"✅ GitHub Agent: Found {len(github_data.get('repos', []))} repos, "
        f"detected {len(detected)} skills"
    )
    s["agent_logs"] = logs
    return s

# ── AGENT 2: Web Intelligence ──────────────────────────────────────────────
def web_intelligence_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    s["current_agent"] = "Web Intelligence Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("🌐 Web Agent: Searching live company data...")

    companies = s.get("target_companies", [])
    live_data: Dict[str, Any] = {}
    all_results = []

    for company in companies[:5]:  # limit to 5 to save API credits
        results = web_search(
            f"{company} software engineer placement interview questions 2025 India"
        )
        live_data[company] = results
        all_results.extend(results)
        logs.append(f"  ✅ Searched: {company} ({len(results)} results)")

    # General placement search
    results2 = web_search("top tier 1 company coding interview tips India 2025")
    all_results.extend(results2)

    s["web_search_results"] = all_results
    s["live_company_data"]  = live_data
    s["completed_agents"]   = list(s.get("completed_agents", [])) + ["web_agent"]
    logs.append(f"✅ Web Agent: Gathered {len(all_results)} live data points")
    s["agent_logs"] = logs
    return s

# ── AGENT 3: Gap Analysis ──────────────────────────────────────────────────
def gap_analysis_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    s["current_agent"] = "Gap Analysis Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("🧠 Gap Agent: Analyzing skill gaps with Gemini Pro...")

    detected  = s.get("detected_skills", [])
    companies = s.get("target_companies", [])
    cgpa      = float(s.get("student_cgpa", 0))

    alignments   = []
    eligible     = []
    stretch      = []
    all_gaps     = []

    for company in companies:
        alignment = score_skills_against_company(detected, company, cgpa)
        if alignment:
            alignments.append(alignment)
            if alignment["is_eligible"]:
                if alignment["skill_match_pct"] >= 70:
                    eligible.append(company)
                else:
                    stretch.append(company)
            all_gaps.extend(alignment["missing_skills"])

    # Use Gemini Pro for deep gap synthesis
    model  = get_pro()
    prompt = f"""
You are a senior placement expert at a top Indian engineering college.

Student's detected skills from GitHub: {detected}
Target companies: {companies}
CGPA: {cgpa}

Company alignments (computed): {json.dumps(alignments, indent=2)}
Live web data about these companies: {s.get('web_search_results', [])[:5]}

Synthesize this and return ONLY this JSON:
{{
  "top_5_critical_gaps": ["gap1", "gap2", "gap3", "gap4", "gap5"],
  "immediate_actions": ["action1", "action2", "action3"],
  "realistic_timeline_weeks": <integer>,
  "honest_assessment": "2-3 sentence honest assessment of the student's readiness",
  "hidden_strengths": ["strength1", "strength2"]
}}
"""
    synthesis = safe_json(call_gemini(model, prompt))

    top_gaps = list(set(all_gaps))[:8]
    if synthesis.get("top_5_critical_gaps"):
        top_gaps = synthesis["top_5_critical_gaps"]

    s["company_alignments"] = alignments
    s["eligible_companies"] = eligible
    s["stretch_companies"]  = stretch
    s["top_gaps"]           = top_gaps
    s["completed_agents"]   = list(s.get("completed_agents", [])) + ["gap_agent"]

    logs.append(
        f"✅ Gap Agent: {len(eligible)} eligible, "
        f"{len(stretch)} stretch. Top gaps: {top_gaps[:3]}"
    )
    s["agent_logs"] = logs
    return s

# ── AGENT 4: Resource Finder ───────────────────────────────────────────────
def resource_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    s["current_agent"] = "Resource Finder Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("📚 Resource Agent: Finding YouTube videos and LeetCode problems...")

    gaps    = s.get("top_gaps", [])
    youtube = {}
    lc_probs= {}

    companies = s.get("target_companies", [])
    lc_tags   = []
    for co in companies:
        if co in COMPANY_REQUIREMENTS:
            lc_tags.extend(COMPANY_REQUIREMENTS[co]["leetcode_tags"])
    lc_tags = list(set(lc_tags))

    for gap in gaps[:5]:  # limit API calls
        # YouTube
        videos = search_youtube(gap, max_results=2)
        youtube[gap] = [v["url"] for v in videos if v.get("url")]
        logs.append(f"  📺 Found {len(videos)} videos for: {gap}")

    for tag in lc_tags[:5]:
        problems = get_leetcode_problems(tag, "Medium")
        lc_probs[tag] = [p["url"] for p in problems if p.get("url")]

    s["youtube_resources"] = youtube
    s["leetcode_problems"] = lc_probs
    s["completed_agents"]  = list(s.get("completed_agents", [])) + ["resource_agent"]
    logs.append(
        f"✅ Resource Agent: {sum(len(v) for v in youtube.values())} videos, "
        f"{sum(len(v) for v in lc_probs.values())} LeetCode problems"
    )
    s["agent_logs"] = logs
    return s

# ── AGENT 5: Planner ───────────────────────────────────────────────────────
def planning_agent(state: VanguardState) -> VanguardState:
    """Agent 5: Generate personalized day-by-day prep plan."""
    s    = state.copy()
    s["current_agent"] = "Adaptive Planning Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("📅 Planner Agent: Building your personalized day-by-day plan...")

    model   = get_pro()
    gaps    = s.get("top_gaps", [])
    weeks   = int(s.get("weeks_available", 8))
    name    = s.get("student_name", "Student")
    eligible= s.get("eligible_companies", [])
    stretch = s.get("stretch_companies", [])
    detected= s.get("detected_skills", [])
    projects= s.get("_intake_data", {}).get("projects", [])
    competitive = s.get("_intake_data", {}).get("competitive", "None")
    concern = s.get("_intake_data", {}).get("concern", "")
    rated   = s.get("_intake_data", {}).get("self_rated_skills", {})

    # Fallback gaps if analysis found nothing
    if not gaps:
        all_company_skills = []
        for co in s.get("target_companies", []):
            if co in COMPANY_REQUIREMENTS:
                all_company_skills.extend(
                    COMPANY_REQUIREMENTS[co]["skills_required"]
                )
        gaps = list(set(all_company_skills) - set(detected))[:8]
        if not gaps:
            gaps = [
                "Data Structures", "Algorithms",
                "System Design", "Dynamic Programming", "OOP"
            ]
        s["top_gaps"] = gaps

    prompt = f"""
You are a senior placement prep coach at a top Indian engineering college.

Student: {name}
Weeks available: {weeks}
Known skills: {detected}
Self-assessed skills: {rated}
Projects built: {projects}
Competitive programming: {competitive}
Concern: {concern}
Target companies: {eligible + stretch}
Critical gaps to fix: {gaps}

Create a realistic day-by-day study plan.
Rules:
- Max 3-4 hours study per day (students have classes too)
- Start from their current level (don't assume they know nothing)
- First 2 weeks should be the most detailed
- Focus on gaps first, then polish strengths
- Each day must have a specific, actionable task
- Reference actual LeetCode patterns (e.g., "two-pointer", "sliding window")

Return ONLY this JSON — no other text:
{{
  "priority_order": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "total_study_hours": <float>,
  "daily_plan": [
    {{
      "day": 1,
      "topic": "Topic name",
      "morning_task": "Specific 2-hour study task",
      "evening_task": "Specific 1-2 hour practice task",
      "leetcode_target": "Specific LeetCode pattern or problem name to practice",
      "daily_goal": "What you should be able to do by end of day"
    }}
  ],
  "week3_onwards": "Brief description of focus from week 3 onwards"
}}

Generate plans for all {min(weeks * 7, 14)} days (up to 14 days detailed).
"""
    result    = call_gemini(model, prompt)
    plan_data = safe_json(result)

    if not plan_data or not plan_data.get("daily_plan"):
        # Hard fallback — basic plan
        fallback_topics = gaps[:5] or ["Data Structures","Algorithms","OOP"]
        plan_data = {
            "priority_order": fallback_topics,
            "total_study_hours": weeks * 7 * 3.0,
            "daily_plan": [
                {
                    "day": i + 1,
                    "topic": fallback_topics[i % len(fallback_topics)],
                    "morning_task": f"Study {fallback_topics[i % len(fallback_topics)]} — read theory and watch 1 video",
                    "evening_task": "Solve 3 LeetCode Easy problems on today's topic",
                    "leetcode_target": "Easy level problems on topic",
                    "daily_goal": f"Understand basic concepts of {fallback_topics[i % len(fallback_topics)]}"
                }
                for i in range(14)
            ],
            "week3_onwards": f"Continue with {', '.join(fallback_topics)} and add mock interviews"
        }

    yt    = s.get("youtube_resources", {})
    lc    = s.get("leetcode_problems", {})
    daily = plan_data.get("daily_plan", [])

    for day in daily:
        topic = day.get("topic", "")
        day["youtube_links"]     = yt.get(topic, [])[:2]
        day["leetcode_problems"] = []
        for tag, problems in lc.items():
            if tag.lower() in topic.lower() or topic.lower() in tag.lower():
                day["leetcode_problems"] = problems[:3]
                break

    s["daily_plan"]        = daily
    s["priority_topics"]   = plan_data.get("priority_order", gaps[:5])
    s["total_study_hours"] = float(plan_data.get("total_study_hours", 0))
    s["completed_agents"]  = list(s.get("completed_agents", [])) + ["planning_agent"]
    logs.append(
        f"✅ Planner Agent: {len(daily)}-day plan created, "
        f"{s['total_study_hours']:.0f} total study hours"
    )
    s["agent_logs"] = logs
    return s

# ── AGENT 6: Mock Interviewer ──────────────────────────────────────────────
def mock_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    s["current_agent"] = "Mock Interview Agent"
    logs = list(s.get("agent_logs", []))

    eligible  = s.get("eligible_companies", [])
    stretch   = s.get("stretch_companies", [])
    all_cos   = eligible + stretch
    company   = all_cos[0] if all_cos else "Google"

    model = get_pro()
    req   = COMPANY_REQUIREMENTS.get(company, {})

    prompt = f"""
You are a senior {company} interviewer (SDE-2 level).
Generate exactly 5 interview questions for this company.

Company pattern: {req.get('pattern', 'standard')}
Typical questions style: {req.get('typical_questions', [])}
Candidate skills: {s.get('detected_skills', [])}

Mix: 3 DSA/Technical + 1 System Design concept + 1 Behavioural
Return ONLY a JSON array of 5 question strings.
Example: ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"]
"""
    result = call_gemini(model, prompt)
    questions = safe_json(result)
    if not isinstance(questions, list):
        questions = req.get("typical_questions", ["Tell me about yourself."])[:5]

    s["mock_company"]     = company
    s["mock_questions"]   = questions
    s["completed_agents"] = list(s.get("completed_agents", [])) + ["mock_agent"]
    logs.append(f"✅ Mock Agent: {len(questions)} questions ready for {company}")
    s["agent_logs"] = logs
    return s

# ── AGENT 7: Notification ──────────────────────────────────────────────────
def notification_agent(state: VanguardState) -> VanguardState:
    s = state.copy()
    s["current_agent"] = "Proactive Notification Agent"
    logs = list(s.get("agent_logs", []))
    logs.append("📱 Notification Agent: Sending WhatsApp summary...")

    name      = s.get("student_name", "Student")
    eligible  = s.get("eligible_companies", [])
    gaps      = s.get("top_gaps", [])[:3]
    plan      = s.get("daily_plan", [])
    day1      = plan[0] if plan else {}

    message = f"""
🎯 *Vanguard Placement Report*
Hey {name}! Your analysis is ready.

✅ *Eligible for:* {', '.join(eligible) if eligible else 'Focus on skill building first'}

🔥 *Top 3 gaps to fix:*
{chr(10).join(f'• {g}' for g in gaps)}

📅 *Today's task:*
{day1.get('morning_task', 'Start with Data Structures basics')}

Practice: {day1.get('leetcode_target', 'LeetCode Easy problems')}

💪 You have {s.get('weeks_available', 8)} weeks. Let's go!
*Powered by Vanguard AI*
""".strip()

    phone  = s.get("student_phone", "")
    to_num = f"whatsapp:{phone}" if phone and not phone.startswith("whatsapp") else phone
    sent   = send_whatsapp(message, to_num if phone else None)

    notif_log = list(s.get("notification_log", []))
    notif_log.append(f"WhatsApp {'sent' if sent else 'skipped (not configured)'}")

    s["whatsapp_sent"]    = sent
    s["notification_log"] = notif_log
    s["completed_agents"] = list(s.get("completed_agents", [])) + ["notification_agent"]
    logs.append(f"✅ Notification Agent: WhatsApp {'sent' if sent else 'skipped'}")
    s["agent_logs"] = logs
    return s

# ── Build LangGraph ────────────────────────────────────────────────────────
def build_vanguard_graph():
    graph = StateGraph(VanguardState)

    graph.add_node("github",       github_agent)
    graph.add_node("web_intel",    web_intelligence_agent)
    graph.add_node("gap_analysis", gap_analysis_agent)
    graph.add_node("resources",    resource_agent)
    graph.add_node("planning",     planning_agent)
    graph.add_node("mock",         mock_agent)
    graph.add_node("notification", notification_agent)

    graph.set_entry_point("github")
    graph.add_edge("github",       "web_intel")
    graph.add_edge("web_intel",    "gap_analysis")
    graph.add_edge("gap_analysis", "resources")
    graph.add_edge("resources",    "planning")
    graph.add_edge("planning",     "mock")
    graph.add_edge("mock",         "notification")
    graph.add_edge("notification", END)

    return graph.compile()

vanguard_graph = build_vanguard_graph()