import streamlit as st
import time
from datetime import datetime
from config import COMPANY_REQUIREMENTS
from intake import render_intake_form
from chatbot import render_topic_chatbot

st.set_page_config(
    page_title="Vanguard — Placement Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════
# MASTER CSS
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after {
  box-sizing: border-box;
  font-family: 'Inter', sans-serif !important;
}

.stApp { background: #050810; color: #e2e8f0; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1380px; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

/* ── Gradient background ── */
.stApp::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 20%, rgba(66,133,244,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(52,168,83,0.05) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
.main .block-container { position: relative; z-index: 1; }

/* ── Hero ── */
.vg-hero {
  background: linear-gradient(135deg, #0a0f1e 0%, #0d1428 100%);
  border: 1px solid rgba(66,133,244,0.2);
  border-radius: 18px;
  padding: 2.2rem 3rem;
  margin-bottom: 1.5rem;
  position: relative; overflow: hidden;
}
.vg-hero::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335, #4285F4);
  background-size: 300%;
  animation: hShimmer 4s linear infinite;
}
@keyframes hShimmer { 0%{background-position:0%} 100%{background-position:300%} }

.vg-title {
  font-size: clamp(1.8rem, 3.5vw, 3rem);
  font-weight: 900; letter-spacing: -0.02em;
  background: linear-gradient(135deg, #fff 0%, #60a5fa 50%, #34d399 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; line-height: 1.1;
}
.vg-sub { font-size: 0.9rem; color: #475569; margin-top: 0.4rem; }
.vg-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(66,133,244,0.1); border: 1px solid rgba(66,133,244,0.25);
  padding: 3px 10px; border-radius: 20px;
  font-size: 0.7rem; color: #60a5fa; font-weight: 600;
  margin: 0.2rem 0.2rem 0 0;
}

/* ── Metric cards ── */
.vg-metric {
  background: linear-gradient(145deg, #0a0f1e, #0d1428);
  border: 1px solid #1e3a5f; border-radius: 14px;
  padding: 1.3rem 1rem; text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.vg-metric:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(66,133,244,0.12);
}
.vg-metric-val {
  font-size: 1.9rem; font-weight: 800;
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.vg-metric-lbl {
  font-size: 0.65rem; color: #475569;
  text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.25rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #0a0f1e !important;
  border-bottom: 1px solid #1e2d3d !important;
  gap: 0.2rem; padding: 0 0.5rem;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: #475569 !important;
  border: none !important; font-size: 0.82rem !important;
  font-weight: 500 !important; padding: 0.7rem 1rem !important;
  border-radius: 8px 8px 0 0 !important;
  transition: all 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #94a3b8 !important; }
.stTabs [aria-selected="true"] {
  background: rgba(66,133,244,0.1) !important;
  color: #60a5fa !important;
  border-bottom: 2px solid #4285F4 !important;
  font-weight: 600 !important;
}

/* ── Progress bar ── */
.vg-prog-wrap {
  background: #1e2d3d; border-radius: 10px; height: 5px; margin: 3px 0 6px;
}
.vg-prog-fill {
  height: 5px; border-radius: 10px;
  background: linear-gradient(90deg, #4285F4, #34A853);
  transition: width 0.5s ease;
}

/* ── Pills ── */
.vg-gap {
  display: inline-block;
  background: rgba(234,67,53,0.1); border: 1px solid rgba(234,67,53,0.3);
  color: #fca5a5; padding: 3px 11px; border-radius: 20px;
  font-size: 0.73rem; margin: 2px 2px; font-weight: 500;
}
.vg-skill {
  display: inline-block;
  background: rgba(52,168,83,0.1); border: 1px solid rgba(52,168,83,0.3);
  color: #86efac; padding: 3px 11px; border-radius: 20px;
  font-size: 0.73rem; margin: 2px 2px; font-weight: 500;
}

/* ── REPO CARD — fixed overlap ── */
.vg-repo {
  display: flex; align-items: center; gap: 0.9rem;
  background: #0a0f1e; border: 1px solid #1e2d3d;
  border-radius: 10px; padding: 0.85rem 1.1rem;
  margin: 0.4rem 0; transition: border-color 0.15s;
  overflow: hidden;                    /* ← key */
}
.vg-repo:hover { border-color: #4285F4; }
.vg-repo-info {
  flex: 1; min-width: 0;              /* ← key: prevents flex child overflow */
}
.vg-repo-name {
  font-size: 0.88rem; font-weight: 600; color: #e2e8f0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  display: block;
}
.vg-repo-desc {
  font-size: 0.74rem; color: #475569; margin-top: 0.15rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  display: block;
}
.vg-repo-tag {
  flex-shrink: 0;
  background: rgba(66,133,244,0.1); border: 1px solid rgba(66,133,244,0.25);
  color: #60a5fa; font-size: 0.68rem; padding: 2px 8px;
  border-radius: 8px; white-space: nowrap;
}

/* ── DUOLINGO-STYLE DAY CARD ── */
.vg-week-header {
  background: linear-gradient(135deg, #0d1f3d, #0a1628);
  border: 1px solid #1e3a5f; border-radius: 14px;
  padding: 1.1rem 1.5rem; margin: 1rem 0 0.5rem;
  display: flex; align-items: center; gap: 1rem;
}
.vg-week-label {
  font-size: 0.7rem; font-weight: 700; color: #4285F4;
  text-transform: uppercase; letter-spacing: 0.1em;
  background: rgba(66,133,244,0.1); border: 1px solid rgba(66,133,244,0.25);
  padding: 3px 10px; border-radius: 20px; white-space: nowrap;
}
.vg-week-title {
  font-size: 1rem; font-weight: 700; color: #e2e8f0;
}
.vg-week-sub { font-size: 0.78rem; color: #475569; }

.vg-day {
  background: #0a0f1e;
  border: 1px solid #1e2d3d;
  border-left: 4px solid #4285F4;
  border-radius: 0 12px 12px 0;
  padding: 1rem 1.3rem;
  margin: 0.4rem 0 0.4rem 1.5rem;
  position: relative;
}
.vg-day::before {
  content: '';
  position: absolute; left: -1.5rem; top: 50%;
  transform: translateY(-50%);
  width: 0.85rem; height: 0.85rem; border-radius: 50%;
  background: #4285F4; border: 2px solid #050810;
}
.vg-day.done { border-left-color: #34A853; }
.vg-day.done::before { background: #34A853; }
.vg-day-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem; color: #4285F4; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.2rem;
}
.vg-day-topic {
  font-size: 0.95rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.4rem;
}
.vg-day-task {
  font-size: 0.82rem; color: #94a3b8; line-height: 1.55;
}
.vg-day-goal {
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: rgba(52,168,83,0.1); border: 1px solid rgba(52,168,83,0.25);
  color: #86efac; font-size: 0.75rem; padding: 3px 10px;
  border-radius: 20px; margin-top: 0.5rem;
}
.vg-day-lc {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.73rem; color: #FBBC05;
  background: rgba(251,188,5,0.08); border: 1px solid rgba(251,188,5,0.2);
  padding: 2px 8px; border-radius: 6px; margin-top: 0.4rem;
  display: inline-block;
}

/* ── Video card — fixed overlap ── */
.vg-yt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem; margin-top: 0.8rem;
}
.vg-yt-card {
  background: #0a0f1e; border: 1px solid #1e2d3d;
  border-radius: 12px; overflow: hidden;
  transition: border-color 0.2s, transform 0.2s;
}
.vg-yt-card:hover { border-color: #EA4335; transform: translateY(-3px); }
.vg-yt-thumb-wrap { position: relative; overflow: hidden; }
.vg-yt-thumb { width: 100%; height: 140px; object-fit: cover; display: block; }
.vg-yt-dur {
  position: absolute; bottom: 6px; right: 6px;
  background: rgba(0,0,0,0.85); color: #fff;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem; font-weight: 600;
  padding: 2px 7px; border-radius: 4px;
}
.vg-yt-body { padding: 0.8rem 0.9rem; }
.vg-yt-title {
  font-size: 0.82rem; font-weight: 600; color: #e2e8f0;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
  line-height: 1.4; margin-bottom: 0.4rem;
}
.vg-yt-channel { font-size: 0.72rem; color: #60a5fa; font-weight: 500; }
.vg-yt-meta { font-size: 0.68rem; color: #475569; margin-top: 0.2rem; }
.vg-yt-badge {
  display: inline-block;
  background: rgba(234,67,53,0.1); border: 1px solid rgba(234,67,53,0.25);
  color: #fca5a5; font-size: 0.62rem; padding: 1px 6px;
  border-radius: 6px; margin-top: 0.3rem;
}

/* ── Company card ── */
.vg-co {
  border-radius: 12px; padding: 1.1rem 1.4rem; margin: 0.4rem 0;
  transition: transform 0.15s;
}
.vg-co:hover { transform: translateX(4px); }
.vg-co-g { background: rgba(52,168,83,0.07); border: 1px solid rgba(52,168,83,0.3); }
.vg-co-y { background: rgba(251,188,5,0.07);  border: 1px solid rgba(251,188,5,0.3); }
.vg-co-r { background: rgba(234,67,53,0.07);  border: 1px solid rgba(234,67,53,0.2); }
.vg-co-name-g { font-size: 1rem; font-weight: 700; color: #34A853; }
.vg-co-name-y { font-size: 1rem; font-weight: 700; color: #FBBC05; }
.vg-co-sub { font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }

/* ── Login card ── */
.vg-login {
  background: linear-gradient(145deg, #0a0f1e, #0d1428);
  border: 1px solid #1e3a5f; border-radius: 20px;
  padding: 3rem 3.5rem; position: relative; overflow: hidden;
}
.vg-login::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335);
}

/* ── Score ring ── */
.score-ring {
  width: 90px; height: 90px; border-radius: 50%;
  border: 6px solid;
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; margin: 0 auto 0.8rem;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > textarea {
  background: #0a0f1e !important; border: 1px solid #1e2d3d !important;
  color: #e2e8f0 !important; border-radius: 8px !important;
}
.stTextInput > div > div > input:focus {
  border-color: #4285F4 !important;
  box-shadow: 0 0 0 2px rgba(66,133,244,0.15) !important;
}
.stSelectbox > div, .stMultiSelect > div {
  background: #0a0f1e !important; border: 1px solid #1e2d3d !important;
  color: #e2e8f0 !important;
}
.stButton > button {
  border-radius: 10px !important; font-weight: 600 !important;
  font-size: 0.88rem !important; transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4285F4, #1a73e8) !important;
  border: none !important; color: white !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 4px 16px rgba(66,133,244,0.4) !important;
  transform: translateY(-1px) !important;
}

/* ── Expander overrides ── */
.streamlit-expanderHeader {
  background: #0a0f1e !important; border: 1px solid #1e2d3d !important;
  border-radius: 10px !important; color: #e2e8f0 !important;
  font-size: 0.88rem !important; font-weight: 600 !important;
}
.streamlit-expanderContent {
  background: #050810 !important; border: 1px solid #1e2d3d !important;
  border-top: none !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: #0a0f1e !important;
  border-right: 1px solid #1e2d3d !important;
}

/* ── Log line ── */
.vg-log {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem; padding: 3px 0;
  border-bottom: 1px solid #0d1117;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════
def init():
    defaults = {
        "logged_in": False, "user_email": "", "user_name": "",
        "analysis_done": False, "vanguard_state": None,
        "mock_active": False, "mock_idx": 0,
        "mock_answers": [], "mock_scores": [],
        "yt_cache": {}, "intake_step": 1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init()

# ══════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown('<div class="vg-login">', unsafe_allow_html=True)
        st.markdown("""
<div style="font-size:2.2rem;font-weight:900;
  background:linear-gradient(135deg,#60a5fa,#34d399);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;margin-bottom:0.3rem">⚡ VANGUARD</div>
<div style="color:#475569;font-size:0.88rem;margin-bottom:2rem">
  Autonomous Placement Intelligence Agent</div>
""", unsafe_allow_html=True)
        name_in  = st.text_input("Your Name",  placeholder="John Doe")
        email_in = st.text_input("Email",       placeholder="you@pes.edu")
        c1, c2   = st.columns(2)
        with c1:
            if st.button("🚀 Sign In", type="primary", use_container_width=True):
                if name_in and email_in:
                    st.session_state.logged_in  = True
                    st.session_state.user_name  = name_in
                    st.session_state.user_email = email_in
                    st.rerun()
                else:
                    st.error("Enter name and email.")
        with c2:
            if st.button("👁 Demo", use_container_width=True):
                st.session_state.logged_in  = True
                st.session_state.user_name  = "Demo Student"
                st.session_state.user_email = "demo@vanguard.ai"
                st.rerun()
        st.markdown("""
<div style="text-align:center;font-size:0.72rem;color:#334155;margin-top:1.5rem">
  No password needed · Progress saves to your session
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
<div style="padding:1rem 0.5rem">
  <div style="font-size:1.1rem;font-weight:800;
    background:linear-gradient(135deg,#60a5fa,#34d399);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent">
    ⚡ VANGUARD</div>
  <div style="font-size:0.78rem;color:#475569;margin-top:0.3rem">
    {st.session_state.user_name}</div>
  <div style="font-size:0.68rem;color:#334155">{st.session_state.user_email}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🏠 New Analysis", use_container_width=True):
        keys_to_reset = [
            "analysis_done", "vanguard_state", "mock_active",
            "mock_idx", "mock_answers", "mock_scores", "yt_cache"
        ]
        for k in keys_to_reset:
            v = st.session_state.get(k)
            st.session_state[k] = (
                False if isinstance(v, bool)
                else None if v is None or k == "vanguard_state"
                else [] if isinstance(v, list)
                else {} if isinstance(v, dict)
                else 0
            )
        st.session_state.intake_step = 1
        st.rerun()
    if st.button("🚪 Sign Out", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem;color:#334155;line-height:2">
<b style="color:#475569">Powered by</b><br>
🤖 Gemini 1.5 Pro<br>
🔀 LangGraph<br>
🐙 GitHub API<br>
🔍 Serper Search<br>
📺 YouTube API<br>
💻 LeetCode GraphQL<br>
📱 Twilio WhatsApp<br>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# INTAKE
# ══════════════════════════════════════════════════════════════════════
if not st.session_state.analysis_done:
    st.markdown(f"""
<div class="vg-hero">
  <div class="vg-title">⚡ VANGUARD</div>
  <div class="vg-sub">
    Autonomous Placement Intelligence · Welcome,
    <b style="color:#e2e8f0">{st.session_state.user_name}</b>
  </div>
  <div style="margin-top:0.8rem">
    <span class="vg-badge">🤖 7 AI Agents</span>
    <span class="vg-badge">📡 GitHub API</span>
    <span class="vg-badge">🔍 Live Web Search</span>
    <span class="vg-badge">📺 YouTube 45min+</span>
    <span class="vg-badge">💻 LeetCode Problems</span>
    <span class="vg-badge">📱 WhatsApp Report</span>
  </div>
</div>
""", unsafe_allow_html=True)

    intake_result = render_intake_form()

    if intake_result:
        st.markdown("---")
        st.markdown("### 🤖 Agent Execution")

        AGENTS = [
            ("🔍", "GitHub Intelligence",    "Reading your repositories..."),
            ("🌐", "Web Intelligence",        "Searching live company data..."),
            ("🧠", "Gap Analyzer",            "Comparing skills vs requirements..."),
            ("📚", "Resource Finder",         "Finding videos & problems..."),
            ("📅", "Adaptive Planner",        "Building your study plan..."),
            ("🎤", "Mock Interviewer",         "Preparing interview questions..."),
            ("📱", "Notification Agent",       "Sending WhatsApp report..."),
        ]

        ph = st.empty()

        def render_agents(current: int, done: bool = False):
            html = '<div style="display:flex;flex-direction:column;gap:0.4rem;padding:0.5rem 0">'
            for i, (icon, name, msg) in enumerate(AGENTS):
                if done or i < current:
                    bg, bc, dot, lbl = "#0d2b1a","#34A853","✓","#34A853"
                elif i == current:
                    bg, bc, dot, lbl = "#0a1628","#4285F4","●","#60a5fa"
                else:
                    bg, bc, dot, lbl = "#0a0f1e","#1e2d3d","○","#334155"
                html += f"""
<div style="display:flex;align-items:center;gap:0.8rem;
  padding:0.65rem 1rem;background:{bg};
  border:1px solid {bc};border-radius:10px;transition:all 0.3s">
  <div style="font-size:1rem;flex-shrink:0">{icon}</div>
  <div style="flex:1">
    <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0">{name}</div>
  </div>
  <div style="font-size:0.75rem;color:{lbl};font-weight:600">{dot}</div>
</div>"""
            html += "</div>"
            ph.markdown(html, unsafe_allow_html=True)

        render_agents(0)

        from agents import vanguard_graph
        initial = {
            "github_username":    intake_result.get("github_username",""),
            "target_companies":   intake_result.get("target_companies",[]),
            "student_name":       st.session_state.user_name,
            "student_cgpa":       float(intake_result.get("cgpa",0)),
            "student_phone":      intake_result.get("phone",""),
            "weeks_available":    int(intake_result.get("weeks_available",12)),
            "_intake_data":       intake_result,
            "github_repos":       [],
            "github_languages":   {},
            "detected_skills":    intake_result.get("known_skills",[]),
            "github_raw_data":    {},
            "web_search_results": [],
            "live_company_data":  {},
            "skill_scores":       [],
            "company_alignments": [],
            "top_gaps":           [],
            "eligible_companies": [],
            "stretch_companies":  [],
            "youtube_resources":  {},
            "leetcode_problems":  {},
            "daily_plan":         [],
            "priority_topics":    [],
            "total_study_hours":  0.0,
            "mock_company":       "",
            "mock_questions":     [],
            "mock_answers":       [],
            "mock_scores":        [],
            "mock_overall_score": 0.0,
            "whatsapp_sent":      False,
            "notification_log":   [],
            "current_agent":      "",
            "completed_agents":   [],
            "agent_logs":         [],
            "errors":             [],
            "total_tokens_used":  0,
        }

        try:
            with st.spinner(""):
                for i in range(len(AGENTS)):
                    render_agents(i)
                    time.sleep(0.15)
                result = vanguard_graph.invoke(initial)
                render_agents(0, done=True)

            # Fetch YouTube for all gaps
            from tools import search_youtube_rich
            yt_cache = {}
            for gap in result.get("top_gaps",[])[:6]:
                videos = search_youtube_rich(gap, max_results=8)
                yt_cache[gap] = videos

            result["_yt_cache"]    = yt_cache
            result["_intake_data"] = intake_result
            st.session_state.vanguard_state = result
            st.session_state.analysis_done  = True
            time.sleep(0.5)
            st.rerun()

        except Exception as e:
            st.error(f"Agent error: {e}")
            import traceback
            st.code(traceback.format_exc())

    st.stop()

# ══════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════
S        = st.session_state.vanguard_state
eligible = S.get("eligible_companies", [])
stretch  = S.get("stretch_companies",  [])
gaps     = S.get("top_gaps",           [])
yt_cache = S.get("_yt_cache",          {})
intake   = S.get("_intake_data",       {})
plan     = S.get("daily_plan",         [])
priority = S.get("priority_topics",    [])

# Hero
badges = "".join(
    f'<span style="background:rgba(52,168,83,0.12);border:1px solid rgba(52,168,83,0.35);'
    f'color:#34A853;padding:3px 10px;border-radius:20px;font-size:0.72rem;'
    f'font-weight:600;margin:2px">✅ {c}</span>'
    for c in eligible
) + "".join(
    f'<span style="background:rgba(251,188,5,0.12);border:1px solid rgba(251,188,5,0.35);'
    f'color:#FBBC05;padding:3px 10px;border-radius:20px;font-size:0.72rem;'
    f'font-weight:600;margin:2px">🔥 {c}</span>'
    for c in stretch
)

st.markdown(f"""
<div class="vg-hero" style="padding:1.8rem 2.5rem;margin-bottom:1.5rem">
  <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
    <div>
      <div class="vg-title" style="font-size:1.9rem">
        ⚡ {S.get('student_name','Student')}'s Placement Report
      </div>
      <div class="vg-sub">{datetime.now().strftime('%B %d, %Y · %H:%M')}</div>
    </div>
    <div style="margin-left:auto;display:flex;flex-wrap:wrap;gap:0.3rem">
      {badges}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Metrics
m_vals = [
    (len(S.get("github_repos",[])),    "Repos"),
    (len(S.get("detected_skills",[])), "Skills"),
    (len(eligible),                     "Eligible"),
    (len(stretch),                      "Stretch"),
    (len(gaps),                         "Gaps"),
]
mc = st.columns(5)
for col, (val, lbl) in zip(mc, m_vals):
    col.markdown(f"""
<div class="vg-metric">
  <div class="vg-metric-val">{val}</div>
  <div class="vg-metric-lbl">{lbl}</div>
</div>
""", unsafe_allow_html=True)
st.markdown("")

# ── TABS ──────────────────────────────────────────────────────────────
(tab_gh, tab_co, tab_yt, tab_plan,
 tab_tutor, tab_mock, tab_skills, tab_logs) = st.tabs([
    "🔍 GitHub", "🏢 Companies", "📺 Videos",
    "📅 Study Plan", "🤖 AI Tutor", "🎤 Mock",
    "📊 Skills", "📋 Logs"
])

# ── GITHUB ────────────────────────────────────────────────────────────
with tab_gh:
    gh    = S.get("github_raw_data", {})
    repos = S.get("github_repos", [])
    langs = S.get("github_languages", {})

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        prof = gh.get("profile", {})
        st.markdown(f"""
<div class="vg-metric" style="text-align:left;margin-bottom:1rem;padding:1.3rem 1.5rem">
  <div style="font-size:1.15rem;font-weight:700;color:#e2e8f0">
    {prof.get('name', S.get('student_name',''))}
  </div>
  <div style="color:#475569;font-size:0.8rem;margin:0.3rem 0 0.7rem">
    {prof.get('bio','GitHub Developer')}
  </div>
  <span style="color:#60a5fa;font-weight:700;font-size:1.3rem">
    {prof.get('public_repos', len(repos))}
  </span>
  <span style="color:#475569;font-size:0.78rem"> repos</span>
</div>
""", unsafe_allow_html=True)
        st.markdown("**Languages**")
        total = sum(langs.values()) or 1
        for lang, lines in sorted(langs.items(), key=lambda x:-x[1])[:8]:
            pct = int(lines / total * 100)
            st.markdown(f"""
<div style="margin:4px 0">
  <div style="display:flex;justify-content:space-between;
    font-size:0.76rem;margin-bottom:2px">
    <span style="color:#e2e8f0">{lang}</span>
    <span style="color:#475569">{pct}%</span>
  </div>
  <div class="vg-prog-wrap">
    <div class="vg-prog-fill" style="width:{pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    with c2:
        skills = S.get("detected_skills", [])
        st.markdown("**Detected Skills**")
        if skills:
            st.markdown(
                "".join(f'<span class="vg-skill">{s}</span>' for s in skills),
                unsafe_allow_html=True
            )
        else:
            st.warning("No skills detected from GitHub — check if repos are public.")

        st.markdown("**Repositories**")
        for repo in repos[:10]:
            name_r = repo.get("name","unknown") or "unknown"
            lang_r = repo.get("language","?") or "?"
            desc_r = (repo.get("description","") or "No description")[:65]
            url_r  = repo.get("url","")
            stars  = repo.get("stars",0)

            # No expander — clean card layout avoids ALL overlap
            st.markdown(f"""
<div class="vg-repo">
  <div style="font-size:1.1rem;flex-shrink:0">📁</div>
  <div class="vg-repo-info">
    <span class="vg-repo-name">{name_r}</span>
    <span class="vg-repo-desc">{desc_r}</span>
  </div>
  <span class="vg-repo-tag">{lang_r}</span>
  <span style="font-size:0.72rem;color:#475569;flex-shrink:0">⭐{stars}</span>
</div>
""", unsafe_allow_html=True)
            if url_r:
                st.markdown(
                    f'<div style="margin:-0.2rem 0 0.3rem 3rem">'
                    f'<a href="{url_r}" target="_blank" '
                    f'style="font-size:0.7rem;color:#4285F4">View on GitHub →</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )

# ── COMPANIES ─────────────────────────────────────────────────────────
with tab_co:
    alignments = S.get("company_alignments", [])

    if eligible:
        st.markdown(f"### ✅ Eligible ({len(eligible)})")
        for co in eligible:
            al  = next((a for a in alignments if a["company"]==co), {})
            req = COMPANY_REQUIREMENTS.get(co, {})
            pct = al.get("skill_match_pct", 0)

            # Collapsible using session state — no st.expander
            key = f"co_open_{co}"
            if key not in st.session_state:
                st.session_state[key] = False

            # Header row (clickable)
            hcol1, hcol2 = st.columns([6, 1])
            with hcol1:
                st.markdown(f"""
<div style="background:#0a0f1e;border:1px solid rgba(52,168,83,0.35);
  border-radius:10px;padding:0.9rem 1.2rem;margin:0.4rem 0;cursor:pointer">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
    <span style="color:#34A853;font-weight:700;font-size:1rem">✅ {co}</span>
    <span style="color:#64748b;font-size:0.8rem">{pct:.0f}% match</span>
    <span style="color:#64748b;font-size:0.8rem">·</span>
    <span style="color:#64748b;font-size:0.8rem">{req.get('ctc_range','')}</span>
    <span style="color:#64748b;font-size:0.8rem">·</span>
    <span style="color:#64748b;font-size:0.8rem">{req.get('difficulty','')}</span>
  </div>
</div>
""", unsafe_allow_html=True)
            with hcol2:
                if st.button(
                    "▼ Details" if not st.session_state[key] else "▲ Hide",
                    key=f"btn_{co}",
                    use_container_width=True
                ):
                    st.session_state[key] = not st.session_state[key]
                    st.rerun()

            if st.session_state[key]:
                st.markdown(f"""
<div style="background:#050810;border:1px solid rgba(52,168,83,0.2);
  border-top:none;border-radius:0 0 10px 10px;
  padding:1.2rem 1.5rem;margin-top:-0.4rem;margin-bottom:0.4rem">
""", unsafe_allow_html=True)
                pc1, pc2 = st.columns(2)
                with pc1:
                    st.markdown("**Your strengths:**")
                    matched = al.get("matched_skills", [])
                    st.markdown(
                        "".join(f'<span class="vg-skill">✅ {s}</span>'
                                for s in matched) or "—",
                        unsafe_allow_html=True
                    )
                with pc2:
                    st.markdown("**Gaps to fill:**")
                    missing = al.get("missing_skills", [])
                    st.markdown(
                        "".join(f'<span class="vg-gap">❌ {s}</span>'
                                for s in missing) or "—",
                        unsafe_allow_html=True
                    )
                st.info(f"💡 {al.get('recommended_action','')}")
                st.markdown(f"**Interview Pattern:** {req.get('pattern','')}")
                if req.get("typical_questions"):
                    st.markdown("**Typical Questions:**")
                    for q in req["typical_questions"][:4]:
                        st.write(f"• {q}")
                st.markdown("</div>", unsafe_allow_html=True)

    if stretch:
        st.markdown(f"### 🔥 Stretch Goals ({len(stretch)})")
        for co in stretch:
            al  = next((a for a in alignments if a["company"]==co), {})
            req = COMPANY_REQUIREMENTS.get(co, {})
            missing_preview = ', '.join(al.get('missing_skills',[])[:3])
            st.markdown(f"""
<div style="background:rgba(251,188,5,0.07);border:1px solid rgba(251,188,5,0.3);
  border-radius:10px;padding:1rem 1.4rem;margin:0.4rem 0">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
    <span style="color:#FBBC05;font-weight:700;font-size:1rem">🔥 {co}</span>
    <span style="color:#64748b;font-size:0.8rem">{al.get('skill_match_pct',0):.0f}% match</span>
    <span style="color:#64748b;font-size:0.8rem">·</span>
    <span style="color:#64748b;font-size:0.8rem">{req.get('ctc_range','')}</span>
  </div>
  <div style="color:#475569;font-size:0.78rem;margin-top:0.4rem">
    Missing: {missing_preview}
  </div>
  <div style="color:#475569;font-size:0.75rem;margin-top:0.2rem">
    {req.get('pattern','')}
  </div>
</div>
""", unsafe_allow_html=True)

    ineligible = [
        a for a in alignments
        if a["company"] not in eligible and a["company"] not in stretch
    ]
    if ineligible:
        st.markdown("### ❌ Not Eligible Yet")
        for a in ineligible:
            co  = a["company"]
            req = COMPANY_REQUIREMENTS.get(co, {})
            st.markdown(f"""
<div style="background:rgba(234,67,53,0.05);border:1px solid rgba(234,67,53,0.15);
  border-radius:10px;padding:0.8rem 1.2rem;margin:0.3rem 0">
  <span style="color:#EA4335;font-weight:600">❌ {co}</span>
  <span style="color:#475569;font-size:0.78rem;margin-left:1rem">
    CGPA issue or too many missing skills
  </span>
</div>
""", unsafe_allow_html=True)

    st.markdown("### ❌ Critical Gaps to Fix")
    st.markdown(
        "".join(f'<span class="vg-gap">❌ {g}</span>' for g in gaps) or "No gaps found",
        unsafe_allow_html=True
    )

# ── VIDEOS ────────────────────────────────────────────────────────────
with tab_yt:
    st.markdown("### 📺 Full Course Videos")
    st.markdown(
        '<div style="color:#475569;font-size:0.82rem;margin-bottom:1rem">'
        'Only 45min+ English videos · Click to watch on YouTube</div>',
        unsafe_allow_html=True
    )

    if not gaps:
        st.info("Run analysis first to see video recommendations.")
    else:
        topic_sel = st.selectbox("Select topic:", gaps[:8], key="yt_sel")

        def render_yt_grid(videos: list):
            if not videos:
                st.info("No long-form videos found for this topic.")
                return
            # Render grid using columns to avoid HTML/Streamlit conflicts
            cols = st.columns(4)
            for i, vid in enumerate(videos):
                col = cols[i % 4]
                thumb = vid.get("thumbnail","")
                url   = vid.get("url","")
                title = vid.get("title","")
                chan  = vid.get("channel","")
                dur   = vid.get("duration","?")
                views = vid.get("views","")
                pub   = vid.get("published","")

                with col:
                    st.markdown(f"""
<div class="vg-yt-card">
  <div class="vg-yt-thumb-wrap">
    {'<img class="vg-yt-thumb" src="'+thumb+'">' if thumb else
     '<div style="height:140px;background:#1e2d3d;display:flex;'
     'align-items:center;justify-content:center;color:#334155">No thumbnail</div>'}
    <div class="vg-yt-dur">{dur}</div>
  </div>
  <div class="vg-yt-body">
    <div class="vg-yt-title">{title}</div>
    <div class="vg-yt-channel">{chan}</div>
    <div class="vg-yt-meta">{views} · {pub}</div>
    <div class="vg-yt-badge">🎓 Full Course</div>
  </div>
</div>
""", unsafe_allow_html=True)
                    if url:
                        st.markdown(f"[▶ Watch]({url})")

        if topic_sel:
            vids = yt_cache.get(topic_sel, [])
            if not vids:
                with st.spinner(f"Finding {topic_sel} videos..."):
                    from tools import search_youtube_rich
                    vids = search_youtube_rich(topic_sel, max_results=8)
                    yt_cache[topic_sel] = vids
                    S["_yt_cache"] = yt_cache
            render_yt_grid(vids)

        st.markdown("---")
        st.markdown("### 📚 All Gap Topics")
        for gap in gaps[:6]:
            gap_key = f"yt_gap_open_{gap.replace(' ','_')}"
            if gap_key not in st.session_state:
                st.session_state[gap_key] = False

            gh1, gh2 = st.columns([5, 1])
            with gh1:
                st.markdown(f"""
<div style="background:#0a0f1e;border:1px solid #1e2d3d;
  border-radius:10px;padding:0.75rem 1.1rem;margin:0.35rem 0">
  <span style="font-size:0.88rem;font-weight:600;color:#e2e8f0">📖 {gap}</span>
</div>
""", unsafe_allow_html=True)
            with gh2:
                if st.button(
                    "▼" if not st.session_state[gap_key] else "▲",
                    key=f"yt_btn_{gap}",
                    use_container_width=True
                ):
                    st.session_state[gap_key] = not st.session_state[gap_key]
                    st.rerun()

            if st.session_state[gap_key]:
                gv = yt_cache.get(gap, [])
                if not gv:
                    with st.spinner(f"Loading {gap}..."):
                        from tools import search_youtube_rich
                        gv = search_youtube_rich(gap, max_results=4)
                        yt_cache[gap] = gv
                        S["_yt_cache"] = yt_cache
                st.markdown(
                    '<div style="background:#050810;border:1px solid #1e2d3d;'
                    'border-top:none;border-radius:0 0 10px 10px;'
                    'padding:0.8rem 1.1rem;margin-top:-0.35rem;margin-bottom:0.3rem">',
                    unsafe_allow_html=True
                )
                for vid in gv:
                    dur   = vid.get("duration","?")
                    title = vid.get("title","")[:65]
                    chan  = vid.get("channel","")
                    url   = vid.get("url","")
                    if url:
                        st.markdown(
                            f'<div style="padding:0.35rem 0;border-bottom:1px solid #1e2d3d">'
                            f'<a href="{url}" target="_blank" style="color:#60a5fa;'
                            f'font-size:0.82rem;font-weight:500">▶ {title}...</a>'
                            f'<span style="color:#475569;font-size:0.72rem"> · {dur} · {chan}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                st.markdown("</div>", unsafe_allow_html=True)

# ── STUDY PLAN — ───────────────────────────────────────
with tab_plan:
    st.markdown("### 📅 Your Study Plan")

    if not plan:
        st.warning(
            "Study plan is empty — make sure to fill in the skills "
            "self-assessment in the intake form."
        )
    else:
        # Summary bar
        total_h = S.get("total_study_hours", 0)
        weeks_n = intake.get("weeks_available", 8)
        st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem">
  <div class="vg-metric">
    <div class="vg-metric-val">{len(plan)}</div>
    <div class="vg-metric-lbl">Days Planned</div>
  </div>
  <div class="vg-metric">
    <div class="vg-metric-val">{total_h:.0f}h</div>
    <div class="vg-metric-lbl">Total Study Hours</div>
  </div>
  <div class="vg-metric">
    <div class="vg-metric-val">{weeks_n}</div>
    <div class="vg-metric-lbl">Weeks Available</div>
  </div>
  <div class="vg-metric">
    <div class="vg-metric-val">{len(gaps)}</div>
    <div class="vg-metric-lbl">Topics to Cover</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Priority order
        if priority:
            prio_html = " → ".join(
                f'<span style="background:rgba(66,133,244,0.12);'
                f'border:1px solid rgba(66,133,244,0.3);color:#60a5fa;'
                f'padding:3px 12px;border-radius:20px;font-size:0.75rem;'
                f'font-weight:600">{p}</span>'
                for p in priority[:6]
            )
            st.markdown("**Study in this order:**")
            st.markdown(prio_html, unsafe_allow_html=True)
            st.markdown("")

        # Group days into weeks
        weeks_map: dict = {}
        for day in plan:
            w = (day.get("day", 1) - 1) // 7 + 1
            weeks_map.setdefault(w, []).append(day)

        for week_num, week_days in sorted(weeks_map.items()):
            topic_set = list(set(d.get("topic","") for d in week_days))
            st.markdown(f"""
<div class="vg-week-header">
  <div class="vg-week-label">Week {week_num}</div>
  <div>
    <div class="vg-week-title">Focus: {', '.join(topic_set[:2])}</div>
    <div class="vg-week-sub">{len(week_days)} days · ~{len(week_days)*3}hrs</div>
  </div>
</div>
""", unsafe_allow_html=True)

            for day in week_days:
                d_num  = day.get("day", 0)
                topic  = day.get("topic", "")
                morn   = day.get("morning_task", "")
                eve    = day.get("evening_task", "")
                lc_tgt = day.get("leetcode_target", "")
                goal   = day.get("daily_goal", "")
                probs  = day.get("leetcode_problems", [])
                day_vids = yt_cache.get(topic, [])

                goal_html = f'<div class="vg-day-goal">🎯 {goal}</div>' if goal else ""
                lc_html   = f'<div class="vg-day-lc">💻 {lc_tgt}</div>'   if lc_tgt else ""

                # Render day card — NO expander (that caused _arr overlap)
                task_text = ""
                if morn:  task_text += f"☀️ <b>Morning:</b> {morn}<br>"
                if eve:   task_text += f"🌙 <b>Evening:</b> {eve}"

                st.markdown(f"""
<div class="vg-day">
  <div class="vg-day-num">Day {d_num}</div>
  <div class="vg-day-topic">{topic}</div>
  <div class="vg-day-task">{task_text}</div>
  {lc_html}
  {goal_html}
</div>
""", unsafe_allow_html=True)

                # Resources inline (no nested expander)
                if day_vids or probs:
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if day_vids:
                            for vid in day_vids[:2]:
                                t = vid.get("title","Video")[:45]
                                u = vid.get("url","")
                                d = vid.get("duration","?")
                                if u:
                                    st.markdown(
                                        f'<div style="margin-left:1.5rem;'
                                        f'font-size:0.75rem;color:#60a5fa">'
                                        f'📺 <a href="{u}" target="_blank" '
                                        f'style="color:#60a5fa">{t}... [{d}]</a>'
                                        f'</div>',
                                        unsafe_allow_html=True
                                    )
                    with rc2:
                        if probs:
                            for url in probs[:2]:
                                if url:
                                    nm = url.split("/problems/")[-1].strip("/").replace("-"," ").title()
                                    st.markdown(
                                        f'<div style="margin-left:1.5rem;'
                                        f'font-size:0.75rem;color:#FBBC05">'
                                        f'💻 <a href="{url}" target="_blank" '
                                        f'style="color:#FBBC05">{nm}</a>'
                                        f'</div>',
                                        unsafe_allow_html=True
                                    )

# ── AI TUTOR ──────────────────────────────────────────────────────────
with tab_tutor:
    st.markdown("### 🤖 AI Topic Tutor")
    st.markdown(
        '<div style="color:#475569;font-size:0.82rem;margin-bottom:1rem">'
        'Chat with your AI tutor to learn any topic — '
        'ask questions, get explanations, practice interview answers</div>',
        unsafe_allow_html=True
    )

    all_topics = sorted(set(
        gaps + priority + [
            "Data Structures", "Algorithms", "System Design",
            "Dynamic Programming", "OOP", "DBMS",
            "Computer Networks", "Operating Systems",
            "Graph Algorithms", "Problem Solving"
        ]
    ))

    tutor_topic = st.selectbox(
        "What do you want to learn?",
        all_topics, key="tutor_sel"
    )
    if tutor_topic:
        render_topic_chatbot(tutor_topic, key_prefix="v_")

# ── MOCK ──────────────────────────────────────────────────────────────
with tab_mock:
    mock_co   = S.get("mock_company", "Google")
    questions = S.get("mock_questions", [])
    req_m     = COMPANY_REQUIREMENTS.get(mock_co, {})

    st.markdown(f"### 🎤 Mock Interview — {mock_co}")
    st.markdown(
        f'<div style="color:#475569;font-size:0.82rem;margin-bottom:1rem">'
        f'{req_m.get("pattern","")} · {req_m.get("difficulty","")} difficulty</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.mock_active:
        # Preview blurred
        for i, q in enumerate(questions[:5], 1):
            st.markdown(f"""
<div style="background:#0a0f1e;border:1px solid #1e2d3d;
  border-left:4px solid #4285F4;border-radius:8px;
  padding:0.85rem 1.2rem;margin:0.4rem 0;
  filter:blur(3px);opacity:0.4;font-size:0.88rem;color:#e2e8f0">
  Q{i}: [Hidden until you start]
</div>
""", unsafe_allow_html=True)
        sc, _ = st.columns([1,3])
        with sc:
            if st.button(f"▶️ Start Mock — {mock_co}",
                         type="primary", use_container_width=True):
                st.session_state.mock_active  = True
                st.session_state.mock_idx     = 0
                st.session_state.mock_answers = []
                st.session_state.mock_scores  = []
                st.rerun()
    else:
        idx = st.session_state.mock_idx
        if idx < len(questions):
            st.progress(idx / len(questions))
            st.markdown(f"*Question {idx+1} of {len(questions)}*")
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#0a1628,#0d1f3d);
  border:1px solid #1e3a5f;border-left:4px solid #4285F4;
  border-radius:12px;padding:1.5rem;font-size:1rem;
  color:#e2e8f0;line-height:1.7;margin:1rem 0">
  {questions[idx]}
</div>
""", unsafe_allow_html=True)
            ans = st.text_area(
                "Your Answer:", key=f"ma_{idx}", height=150,
                placeholder="Answer as you would in a real interview. Be specific and detailed."
            )
            ac1, ac2 = st.columns([2,1])
            with ac1:
                if st.button("Submit →", type="primary", use_container_width=True):
                    if ans.strip():
                        with st.spinner("Scoring with Gemini..."):
                            from tools import get_pro, call_gemini, safe_json
                            scored = safe_json(call_gemini(get_pro(), f"""
Score this {mock_co} interview answer 1-10.
Q: {questions[idx]}
A: {ans}
Return ONLY valid JSON:
{{"score":<1-10>,"feedback":"<2 sentences>","what_was_good":"<1 sentence>","what_to_improve":"<1 sentence>"}}
"""))
                            if not scored:
                                scored = {"score":5,"feedback":"Keep practicing.","what_was_good":"Good attempt.","what_to_improve":"Add more technical depth."}
                        st.session_state.mock_answers.append(ans)
                        st.session_state.mock_scores.append(scored)
                        st.session_state.mock_idx += 1
                        st.rerun()
                    else:
                        st.warning("Write your answer first.")
            with ac2:
                if st.button("Skip →", use_container_width=True):
                    st.session_state.mock_answers.append("[Skipped]")
                    st.session_state.mock_scores.append({"score":0,"feedback":"Skipped","what_was_good":"-","what_to_improve":"Attempt all questions"})
                    st.session_state.mock_idx += 1
                    st.rerun()
        else:
            scores = st.session_state.mock_scores
            avg    = sum(s.get("score",0) for s in scores)/len(scores) if scores else 0
            col    = "#34A853" if avg>=7 else "#FBBC05" if avg>=5 else "#EA4335"
            ring_c = "#34A853" if avg>=7 else "#FBBC05" if avg>=5 else "#EA4335"
            verdict = ("Ready to apply! 🎉" if avg>=7
                      else "2-3 weeks more prep needed 💪" if avg>=5
                      else "Focus on fundamentals first 📚")
            st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem">
  <div class="score-ring" style="border-color:{ring_c}">
    <div style="font-size:1.6rem;font-weight:800;color:{ring_c}">{avg:.1f}</div>
    <div style="font-size:0.6rem;color:#475569">out of 10</div>
  </div>
  <div style="font-size:1rem;font-weight:600;color:#e2e8f0">{mock_co} Mock Complete</div>
  <div style="font-size:0.85rem;color:#475569;margin-top:0.3rem">{verdict}</div>
</div>
""", unsafe_allow_html=True)
            for i, (q, r) in enumerate(zip(questions, st.session_state.mock_scores)):
                sc  = r.get("score", 0)
                c   = "#34A853" if sc>=7 else "#FBBC05" if sc>=5 else "#EA4335"
                st.markdown(f"""
<div style="background:#0a0f1e;border:1px solid #1e2d3d;
  border-left:4px solid {c};border-radius:0 10px 10px 0;
  padding:1rem 1.3rem;margin:0.5rem 0">
  <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.6rem">
    <span style="color:#475569;font-size:0.75rem;font-weight:600">Q{i+1}</span>
    <span style="color:{c};font-weight:700;font-size:0.95rem">{sc}/10</span>
    <span style="color:#94a3b8;font-size:0.82rem">{q[:70]}...</span>
  </div>
</div>
""", unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    if r.get("what_was_good"):
                        st.success(f"✅ {r['what_was_good']}")
                with rc2:
                    if r.get("what_to_improve"):
                        st.warning(f"⚠️ {r['what_to_improve']}")
                if r.get("feedback"):
                    st.info(f"💡 {r['feedback']}")
            if st.button("🔄 Redo Mock Interview"):
                st.session_state.mock_active  = False
                st.session_state.mock_idx     = 0
                st.session_state.mock_answers = []
                st.session_state.mock_scores  = []
                st.rerun()

# ── SKILLS ────────────────────────────────────────────────────────────
with tab_skills:
    alignments = S.get("company_alignments", [])
    c1s, c2s   = st.columns([1,1], gap="large")

    with c1s:
        st.markdown("**Company Match Scores**")
        for a in sorted(alignments, key=lambda x:x.get("skill_match_pct",0), reverse=True):
            co  = a["company"]
            pct = min(a.get("skill_match_pct",0), 100)
            c   = "#34A853" if pct>=70 else "#FBBC05" if pct>=40 else "#EA4335"
            st.markdown(f"""
<div style="margin:6px 0">
  <div style="display:flex;justify-content:space-between;font-size:0.83rem;margin-bottom:2px">
    <span style="color:#e2e8f0;font-weight:500">{co}</span>
    <span style="color:{c};font-weight:700">{pct:.0f}%</span>
  </div>
  <div class="vg-prog-wrap">
    <div class="vg-prog-fill" style="width:{pct}%;background:{c}"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    with c2s:
        st.markdown("**Your Skills**")
        detected = S.get("detected_skills",[])
        st.markdown(
            "".join(f'<span class="vg-skill">{s}</span>' for s in detected) or "—",
            unsafe_allow_html=True
        )
        st.markdown("<br>**Critical Gaps**", unsafe_allow_html=True)
        st.markdown(
            "".join(f'<span class="vg-gap">{g}</span>' for g in gaps) or "—",
            unsafe_allow_html=True
        )

    lc = S.get("leetcode_problems",{})
    if lc:
        st.markdown("---")
        st.markdown("**LeetCode Problems by Tag**")
        for tag, urls in lc.items():
            if urls:
                st.markdown(f"*{tag}:*")
                for url in urls[:3]:
                    nm = url.split("/problems/")[-1].strip("/").replace("-"," ").title()
                    st.markdown(f"  [→ {nm}]({url})")

# ── LOGS ──────────────────────────────────────────────────────────────
with tab_logs:
    st.markdown("### 📋 Agent Execution Logs")
    for log in S.get("agent_logs",[]):
        c = "#34A853" if "✅" in log else "#FBBC05" if "⚠️" in log else "#60a5fa"
        st.markdown(
            f'<div class="vg-log" style="color:{c}">{log}</div>',
            unsafe_allow_html=True
        )
    if S.get("errors"):
        for e in S.get("errors",[]):
            st.error(e)

# Reset
st.markdown("---")
if st.button("🔄 Start New Analysis"):
    for k in ["analysis_done","vanguard_state","mock_active",
              "mock_idx","mock_answers","mock_scores","yt_cache"]:
        v = st.session_state.get(k)
        st.session_state[k] = (
            False if isinstance(v, bool)
            else None if k in ("vanguard_state",)
            else [] if isinstance(v, list)
            else {} if isinstance(v, dict)
            else 0
        )
    st.session_state.intake_step = 1
    st.rerun()