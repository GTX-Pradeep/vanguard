from typing import TypedDict, List, Optional, Dict, Any, Annotated
from pydantic import BaseModel
import operator

class GitHubRepo(BaseModel):
    name: str = ""
    language: str = ""
    description: str = ""
    stars: int = 0
    topics: List[str] = []
    readme_snippet: str = ""
    commit_count: int = 0

class SkillScore(BaseModel):
    skill: str
    score: int        # 0-100
    evidence: str     # what from GitHub proves this
    gap_topics: List[str] = []

class CompanyAlignment(BaseModel):
    company: str
    tier: int
    is_eligible: bool
    cgpa_ok: bool
    skill_match_pct: float
    missing_skills: List[str] = []
    matched_skills: List[str] = []
    recommended_action: str = ""
    ctc_range: str = ""

class DailyTask(BaseModel):
    day: int
    topic: str
    task: str
    leetcode_problems: List[str] = []
    youtube_links: List[str] = []
    estimated_hours: float = 2.0
    completed: bool = False

class VanguardState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────
    github_username:     str
    target_companies:    List[str]
    student_name:        str
    student_cgpa:        float
    student_phone:       str
    weeks_available:     int

    # ── GitHub Analysis ────────────────────────────────────────────────
    github_repos:        List[Dict[str, Any]]
    github_languages:    Dict[str, int]   # language → lines of code
    detected_skills:     List[str]
    github_raw_data:     Dict[str, Any]

    # ── Web Intelligence ───────────────────────────────────────────────
    web_search_results:  List[Dict[str, Any]]
    live_company_data:   Dict[str, Any]

    # ── Gap Analysis ───────────────────────────────────────────────────
    skill_scores:        List[Dict[str, Any]]
    company_alignments:  List[Dict[str, Any]]
    top_gaps:            List[str]
    eligible_companies:  List[str]
    stretch_companies:   List[str]

    # ── Resources ──────────────────────────────────────────────────────
    youtube_resources:   Dict[str, List[str]]   # topic → [video URLs]
    leetcode_problems:   Dict[str, List[str]]   # topic → [problem URLs]

    # ── Plan ───────────────────────────────────────────────────────────
    daily_plan:          List[Dict[str, Any]]
    priority_topics:     List[str]
    total_study_hours:   float

    # ── Mock Interview ─────────────────────────────────────────────────
    mock_company:        str
    mock_questions:      List[str]
    mock_answers:        List[str]
    mock_scores:         List[Dict[str, Any]]
    mock_overall_score:  float

    # ── Notifications ──────────────────────────────────────────────────
    whatsapp_sent:       bool
    notification_log:    List[str]

    # ── Control ────────────────────────────────────────────────────────
    current_agent:       str
    completed_agents:    List[str]
    agent_logs:          List[str]
    errors:              List[str]
    total_tokens_used:   int


    _intake_data:        Dict[str, Any] 