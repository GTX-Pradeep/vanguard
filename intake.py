"""
Pre-analysis intake module.
Asks smart questions before running agents.
Collects info Gemini can't get from GitHub alone.
"""
import streamlit as st
from config import COMPANY_REQUIREMENTS


def render_intake_form(saved_profile: dict = None) -> dict:
    """
    Renders a multi-step intake form.
    Returns collected data dict when complete, else None.
    """
    saved = saved_profile or {}

    # Step tracker
    if "intake_step" not in st.session_state:
        st.session_state.intake_step = 1

    total_steps = 4
    step = st.session_state.intake_step

    # Progress bar
    pct = int((step - 1) / total_steps * 100)
    st.markdown(f"""
<div style="margin-bottom:1.5rem">
  <div style="display:flex; justify-content:space-between;
       font-size:0.75rem; color:#475569; margin-bottom:6px">
    <span>Step {step} of {total_steps}</span>
    <span>{pct}% complete</span>
  </div>
  <div style="background:#1e2d3d; border-radius:10px; height:6px">
    <div style="width:{pct}%; height:6px; border-radius:10px;
         background:linear-gradient(90deg,#4285F4,#34A853);
         transition:width 0.4s ease"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── STEP 1: Basic Details ──────────────────────────────────────────────
    if step == 1:
        st.markdown("""
<div style="margin-bottom:1.5rem">
  <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0">
    👋 Let's start with the basics
  </div>
  <div style="color:#475569; font-size:0.88rem; margin-top:0.3rem">
    We need a few details to personalize your analysis
  </div>
</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            github = st.text_input(
                "GitHub Username *",
                value=saved.get("github_username", ""),
                placeholder="GTX-Pradeep",
                help="We'll read your actual repositories to detect real skills"
            )
            cgpa = st.number_input(
                "CGPA *",
                min_value=0.0, max_value=10.0,
                value=float(saved.get("cgpa", 7.5)),
                step=0.1
            )
        with c2:
            branch = st.text_input(
                "Branch / Department",
                value=saved.get("branch", ""),
                placeholder="Computer Science (AIML)"
            )
            semester = st.selectbox(
                "Current Semester",
                list(range(1, 9)),
                index=int(saved.get("semester", 6)) - 1
            )

        phone = st.text_input(
            "WhatsApp Number (for your report)",
            value=saved.get("phone", ""),
            placeholder="+91XXXXXXXXXX"
        )
        weeks = st.slider(
            "Weeks until placement season",
            4, 24,
            value=int(saved.get("weeks_available", 12))
        )

        if st.button("Next →", type="primary", use_container_width=True):
            if not github:
                st.error("GitHub username is required.")
            else:
                st.session_state._intake_step1 = {
                    "github_username": github.strip(),
                    "cgpa":            float(cgpa),
                    "branch":          branch,
                    "semester":        int(semester),
                    "phone":           phone.strip(),
                    "weeks_available": int(weeks),
                }
                st.session_state.intake_step = 2
                st.rerun()

    # ── STEP 2: Skills Self-Assessment ────────────────────────────────────
    elif step == 2:
        st.markdown("""
<div style="margin-bottom:1.5rem">
  <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0">
    🧠 Rate your current skills
  </div>
  <div style="color:#475569; font-size:0.88rem; margin-top:0.3rem">
    Be honest — this helps us find your real gaps
  </div>
</div>
""", unsafe_allow_html=True)

        skill_categories = {
            "Programming Languages": [
                "Python", "Java", "C++", "C", "JavaScript", "SQL"
            ],
            "CS Fundamentals": [
                "Data Structures", "Algorithms",
                "Operating Systems", "Computer Networks",
                "DBMS", "OOP"
            ],
            "Advanced Topics": [
                "System Design", "Dynamic Programming",
                "Machine Learning", "Web Development",
                "Problem Solving"
            ]
        }

        self_rated = {}
        for category, skills in skill_categories.items():
            st.markdown(
                f'<div style="font-size:0.85rem; font-weight:600; '
                f'color:#4285F4; margin:1rem 0 0.5rem">{category}</div>',
                unsafe_allow_html=True
            )
            cols = st.columns(3)
            for i, skill in enumerate(skills):
                with cols[i % 3]:
                    rating = st.select_slider(
                        skill,
                        options=["None", "Beginner", "Intermediate", "Advanced"],
                        value="None",
                        key=f"skill_{skill}"
                    )
                    if rating != "None":
                        self_rated[skill] = rating

        col_b, col_n = st.columns([1, 1])
        with col_b:
            if st.button("← Back", use_container_width=True):
                st.session_state.intake_step = 1
                st.rerun()
        with col_n:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state._intake_step2 = {
                    "self_rated_skills": self_rated,
                    "known_skills": [
                        s for s, r in self_rated.items()
                        if r in ["Intermediate", "Advanced"]
                    ]
                }
                st.session_state.intake_step = 3
                st.rerun()

    # ── STEP 3: Projects & Experience ─────────────────────────────────────
    elif step == 3:
        st.markdown("""
<div style="margin-bottom:1.5rem">
  <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0">
    🚀 Tell us about your work
  </div>
  <div style="color:#475569; font-size:0.88rem; margin-top:0.3rem">
    Projects and experience that aren't on GitHub
  </div>
</div>
""", unsafe_allow_html=True)

        projects_text = st.text_area(
            "Your key projects (one per line)",
            height=100,
            placeholder="""YOLOv8 waste detection robot with autonomous navigation
Graph-theoretic document summarizer (Python + FastAPI)
College event manager (JavaScript + Node)""",
            value=saved.get("projects_text", "")
        )

        internship = st.selectbox(
            "Have you done any internship?",
            ["No internship yet", "Yes — technical internship",
             "Yes — non-technical internship"]
        )

        competitive = st.selectbox(
            "Competitive programming experience?",
            ["None", "Solved <50 LeetCode problems",
             "Solved 50-150 problems", "Solved 150+ problems",
             "Codeforces/CodeChef rated"]
        )

        backlogs = st.radio(
            "Any active backlogs?",
            ["No", "Yes — 1-2", "Yes — 3+"],
            horizontal=True
        )

        col_b, col_n = st.columns([1, 1])
        with col_b:
            if st.button("← Back", use_container_width=True):
                st.session_state.intake_step = 2
                st.rerun()
        with col_n:
            if st.button("Next →", type="primary", use_container_width=True):
                project_list = [
                    p.strip() for p in projects_text.split("\n")
                    if p.strip()
                ]
                st.session_state._intake_step3 = {
                    "projects":    project_list,
                    "internship":  internship,
                    "competitive": competitive,
                    "backlogs":    backlogs,
                }
                st.session_state.intake_step = 4
                st.rerun()

    # ── STEP 4: Target & Preferences ─────────────────────────────────────
    elif step == 4:
        st.markdown("""
<div style="margin-bottom:1.5rem">
  <div style="font-size:1.3rem; font-weight:700; color:#e2e8f0">
    🎯 What are you aiming for?
  </div>
  <div style="color:#475569; font-size:0.88rem; margin-top:0.3rem">
    Select companies and role preferences
  </div>
</div>
""", unsafe_allow_html=True)

        companies = st.multiselect(
            "Target companies *",
            list(COMPANY_REQUIREMENTS.keys()),
            default=["Google", "Microsoft", "Amazon"],
            help="Select all companies you want to target"
        )

        role = st.selectbox(
            "Preferred role",
            ["Software Development Engineer (SDE)",
             "Data Scientist / ML Engineer",
             "Full Stack Developer",
             "DevOps / Cloud Engineer",
             "Product / Business Analyst",
             "Open to anything"]
        )

        strength = st.text_area(
            "What do you consider your biggest strength for placements?",
            height=80,
            placeholder="E.g. Strong in ML projects, good at web development..."
        )

        concern = st.text_area(
            "What worries you most about placements?",
            height=80,
            placeholder="E.g. DSA is weak, haven't done system design..."
        )

        col_b, col_n = st.columns([1, 1])
        with col_b:
            if st.button("← Back", use_container_width=True):
                st.session_state.intake_step = 3
                st.rerun()
        with col_n:
            if st.button(
                "⚡ Launch Vanguard Analysis",
                type="primary", use_container_width=True
            ):
                if not companies:
                    st.error("Select at least one company.")
                else:
                    st.session_state._intake_step4 = {
                        "target_companies": companies,
                        "preferred_role":   role,
                        "strength":         strength,
                        "concern":          concern,
                    }

                    # Merge all steps
                    final = {}
                    for key in ["_intake_step1", "_intake_step2",
                                "_intake_step3", "_intake_step4"]:
                        final.update(st.session_state.get(key, {}))

                    # Reset intake step for next time
                    st.session_state.intake_step = 1
                    return final

    return None   # not done yet