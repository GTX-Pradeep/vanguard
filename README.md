# 🛡️ Vanguard

> **Autonomous Multi-Agent AI Platform for Placement Preparation**

Vanguard is an AI-powered placement preparation platform designed to help engineering students bridge the gap between their current skillset and industry expectations. Using autonomous AI agents, GitHub portfolio analysis, live hiring trend intelligence, adaptive study planning, and conversational tutoring, Vanguard provides a personalized roadmap toward software engineering interviews.

---

## 🚀 Features

### 🔍 GitHub Portfolio Analysis
- Connects to a user's GitHub profile.
- Analyzes repositories and code contributions.
- Identifies programming languages, frameworks, and technologies used.
- Builds a comprehensive technical skill profile.

### 📈 Live Placement Intelligence
- Tracks current hiring trends.
- Monitors in-demand technologies and interview topics.
- Aligns preparation with Tier-1 company expectations.

### 🧠 AI Skill Gap Analysis
- Compares a student's current skills with target company requirements.
- Detects missing technologies and weak areas.
- Generates actionable recommendations for improvement.

### 📅 Adaptive 14-Day Study Planner
- Creates personalized learning schedules.
- Uses structured Pydantic schemas for reliable planning.
- Dynamically adapts based on user progress and goals.

### 🎤 AI Mock Interview
- Conducts technical and behavioral interview simulations.
- Provides feedback and improvement suggestions.
- Helps users practice real interview scenarios.

### 💬 AI Tutor
- ChatGPT-style conversational assistant.
- Explains programming concepts.
- Assists with debugging.
- Answers interview-related questions.
- Supports continuous learning.

---

# 🏗️ System Architecture

```text
                   GitHub Profile
                         │
                         ▼
               Repository Analysis Agent
                         │
                         ▼
                Skill Extraction Agent
                         │
                         ▼
              Placement Trend Agent
                         │
                         ▼
                 Gap Analysis Agent
                         │
                         ▼
             Adaptive Study Planner
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      Mock Interview Agent      AI Tutor
             │                       │
             └───────────┬───────────┘
                         ▼
               Streamlit User Interface
```

---

# ⚙️ Tech Stack

| Category | Technology |
|----------|------------|
| Multi-Agent Framework | LangGraph |
| LLM | Google Gemini API |
| Frontend | Streamlit |
| UI | Custom HTML + CSS (Dark Theme) |
| Database | Supabase (PostgreSQL) |
| Data Validation | Pydantic |
| Language | Python |

---

# 📂 Project Structure

```text
Vanguard/
│
├── app.py
├── main.py
├── chatbot.py
├── agents.py
├── config.py
├── database.py
├── intake.py
├── state.py
├── tools.py
│
├── src/
│   └── __init__.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠️ Installation

## Clone the Repository

```bash
git clone https://github.com/GTX-Pradeep/vanguard.git
```

```bash
cd vanguard
```

---

## Create a Virtual Environment

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key

GITHUB_TOKEN=your_github_token
```

---

## Run the Application

```bash
streamlit run app.py
```

---

# 🧩 Workflow

1. User connects GitHub account.
2. Vanguard analyzes repositories.
3. AI agents extract technical skills.
4. Placement trends are collected.
5. Skill gap analysis is generated.
6. Personalized study roadmap is created.
7. AI tutor and mock interview modules assist the user throughout preparation.

---

# 🔒 Security

Sensitive files are excluded using `.gitignore`.

Ignored files include:

```text
.env
.env.*
venv/
.venv/
__pycache__/
.vscode/
```

Never commit:

- API Keys
- Database Credentials
- Tokens
- Virtual Environments
- Secret Configuration Files

---

# 🎯 Future Enhancements

- Resume ATS Analyzer
- Company-specific preparation plans
- Coding contest integration
- Voice-based AI interviews
- Learning analytics dashboard
- Personalized project recommendations
- Real-time placement notifications

---

# 👨‍💻 Contributors

**Pradeep**  
Hackathon Project Developer

---

# 📜 License

This project was developed for educational and hackathon purposes.

---

# ⭐ Acknowledgements

Built using:

- LangGraph
- Google Gemini API
- Streamlit
- Supabase
- Pydantic

---

> **Vanguard empowers engineering students with AI-driven guidance, adaptive learning, and intelligent interview preparation to bridge the gap between academic learning and industry expectations.**