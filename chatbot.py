"""
Topic Teaching Chatbot — ChatGPT-style UI, Gemini Pro backend.
"""
import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY, PRO_MODEL, FLASH_MODEL
import time

genai.configure(api_key=GEMINI_API_KEY)

TOPIC_INTROS = {
    "Data Structures":      "arrays, linked lists, stacks, queues, trees, graphs, heaps, hash maps",
    "Algorithms":           "sorting, searching, BFS, DFS, Dijkstra, greedy, divide & conquer",
    "System Design":        "scalability, load balancing, caching, databases, microservices, CAP theorem",
    "Dynamic Programming":  "memoization, tabulation, knapsack, LCS, coin change, longest paths",
    "OOP":                  "classes, inheritance, polymorphism, encapsulation, SOLID principles",
    "DBMS":                 "SQL, normalization, indexing, transactions, ACID, joins, query optimization",
    "Computer Networks":    "OSI model, TCP/IP, DNS, HTTP/HTTPS, sockets, routing, congestion control",
    "Operating Systems":    "processes, threads, scheduling, memory management, deadlocks, file systems",
    "Machine Learning":     "supervised/unsupervised, neural networks, overfitting, evaluation metrics",
    "Problem Solving":      "time/space complexity, Big-O notation, two pointers, sliding window, recursion",
    "Graph Algorithms":     "BFS, DFS, Dijkstra, Bellman-Ford, topological sort, MST, union-find",
    "Distributed Systems":  "CAP theorem, consistency, availability, partitioning, replication, consensus",
    "JavaScript":           "closures, promises, async/await, event loop, prototype chain, ES6+",
    "Python":               "decorators, generators, comprehensions, GIL, OOP in Python, standard library",
    "Java":                 "JVM, garbage collection, collections framework, multithreading, Spring basics",
    "C++":                  "pointers, memory management, STL, templates, RAII, move semantics",
    "SQL":                  "SELECT, JOIN types, GROUP BY, subqueries, indexes, stored procedures",
    "Web Development":      "HTTP, REST, HTML/CSS, JavaScript, frontend frameworks, backend APIs",
}

QUICK_PROMPTS = {
    "Data Structures":     ["Explain arrays vs linked lists", "How does a hash map work?", "What is a binary tree?"],
    "Algorithms":          ["What is time complexity?", "Explain BFS vs DFS", "How does quicksort work?"],
    "System Design":       ["What is load balancing?", "Explain caching with an example", "What is CAP theorem?"],
    "Dynamic Programming": ["What makes a problem DP?", "Explain memoization vs tabulation", "Solve coin change problem"],
    "OOP":                 ["What are the 4 pillars of OOP?", "Explain polymorphism with example", "What is SOLID?"],
    "Computer Networks":   ["Explain TCP vs UDP", "How does DNS work?", "What is the OSI model?"],
    "Graph Algorithms":    ["When to use BFS vs DFS?", "Explain Dijkstra's algorithm", "What is a topological sort?"],
}

DEFAULT_QUICK = [
    "Explain this topic like I'm a beginner",
    "Give me a common interview question",
    "What's the most important concept here?",
]

def _call_gemini_chat(messages: list, topic: str) -> str:
    system = f"""You are an expert placement preparation tutor for {topic}.
Topic areas: {TOPIC_INTROS.get(topic, topic)}
Rules:
- Max 180 words per response
- Use a real-world analogy for first explanation
- End EVERY response with one follow-up question
- Be encouraging but rigorous
- Correct mistakes gently
- No bullet points for main explanation — use flowing prose"""

    history_text = ""
    for msg in messages[-8:]:
        role = "Student" if msg["role"] == "user" else "Tutor"
        history_text += f"\n{role}: {msg['content']}"

    full_prompt = f"{system}\n\nConversation:{history_text}\n\nTutor:"

    errors = []
    # Try the most reliable current model strings
# Updated to active production models to resolve the 404 deprecation errors
    for model_name in ["gemini-3.5-flash", "gemini-3.1-flash-lite"]:
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            text     = response.text.strip()
            if text:
                return text
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    # Returns the exact error so you can see why it's failing
    return f"⚠️ API Error Details:\n" + "\n".join(errors)


def render_topic_chatbot(topic: str, key_prefix: str = ""):
    """Render a full ChatGPT-style chatbot for a topic."""
    chat_key = f"{key_prefix}chat_{topic.replace(' ','_')}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    history = st.session_state[chat_key]

    # ── Chat container ─────────────────────────────────────────────────
    st.markdown(f"""
<div style="
  background: #0a0f1e;
  border: 1px solid #1e3a5f;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 1rem;
">
  <!-- Header -->
  <div style="
    background: linear-gradient(135deg, #0d1f3d, #0a1628);
    padding: 1rem 1.4rem;
    border-bottom: 1px solid #1e3a5f;
    display: flex; align-items: center; gap: 0.8rem;
  ">
    <div style="
      width: 32px; height: 32px; border-radius: 50%;
      background: linear-gradient(135deg, #4285F4, #34A853);
      display: flex; align-items: center; justify-content: center;
      font-size: 1rem; flex-shrink: 0;
    ">🤖</div>
    <div>
      <div style="font-size: 0.88rem; font-weight: 700; color: #e2e8f0">
        Vanguard AI Tutor
      </div>
      <div style="font-size: 0.72rem; color: #34A853; display: flex; align-items: center; gap: 0.4rem">
        <div style="width:6px;height:6px;border-radius:50%;background:#34A853"></div>
        Teaching {topic}
      </div>
    </div>
    <div style="margin-left: auto; font-size: 0.72rem; color: #334155">
      {len(history)//2} exchanges
    </div>
  </div>

  <!-- Messages area -->
  <div style="
    min-height: 320px;
    max-height: 500px;
    overflow-y: auto;
    padding: 1.2rem 1.4rem;
    display: flex; flex-direction: column; gap: 0.8rem;
  " id="chat-messages">
""", unsafe_allow_html=True)

    # Welcome message
    if not history:
        intro = TOPIC_INTROS.get(topic, topic)
        st.markdown(f"""
<div style="display:flex; gap:0.8rem; align-items:flex-start">
  <div style="width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,#4285F4,#34A853);
    display:flex;align-items:center;justify-content:center;
    font-size:0.8rem;flex-shrink:0">🤖</div>
  <div style="background:#0d1f3d;border:1px solid #1e3a5f;
    border-radius:0 12px 12px 12px;padding:0.9rem 1.1rem;
    max-width:85%;font-size:0.88rem;color:#e2e8f0;line-height:1.65">
    Hey! I'm your AI tutor for <b style="color:#4285F4">{topic}</b>.<br><br>
    We'll cover: <i style="color:#94a3b8">{intro[:100]}...</i><br><br>
    <b>What do you already know about {topic}?</b> Even "nothing at all" is a perfect answer — we start from wherever you are.
  </div>
</div>
""", unsafe_allow_html=True)

    # Render conversation history
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"""
<div style="display:flex;justify-content:flex-end;gap:0.8rem;align-items:flex-start;margin-bottom:0.8rem;">
  <div style="background:linear-gradient(135deg,#1a4a8a,#1e3a6f);
    border:1px solid #2a5a9f;border-radius:12px 0 12px 12px;
    padding:0.85rem 1.1rem;max-width:85%;
    font-size:0.88rem;color:#e2e8f0;line-height:1.6">
    {msg["content"]}
  </div>
  <div style="width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,#34A853,#0d8a3d);
    display:flex;align-items:center;justify-content:center;
    font-size:0.75rem;font-weight:700;color:white;flex-shrink:0">
    {st.session_state.user_name[:1].upper() if 'user_name' in st.session_state else 'U'}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            content = msg["content"]
            st.markdown(f"""
<div style="display:flex;gap:0.8rem;align-items:flex-start;margin-bottom:0.8rem;">
  <div style="width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,#4285F4,#34A853);
    display:flex;align-items:center;justify-content:center;
    font-size:0.8rem;flex-shrink:0">🤖</div>
  <div style="background:#0d1f3d;border:1px solid #1e3a5f;
    border-radius:0 12px 12px 12px;padding:0.9rem 1.1rem;
    max-width:85%;font-size:0.88rem;color:#e2e8f0;line-height:1.65">
    {content.replace(chr(10), '<br>')}
  </div>
</div>
""", unsafe_allow_html=True)

    # Fixed: Containers close precisely after the history messages complete
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Quick prompts ──────────────────────────────────────────────────
    if len(history) < 6:
        prompts = QUICK_PROMPTS.get(topic, DEFAULT_QUICK)
        st.markdown(
            '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin:0.6rem 0">',
            unsafe_allow_html=True
        )
        for i, prompt in enumerate(prompts[:3]):
            if st.button(
                prompt,
                key=f"{key_prefix}qp_{topic}_{i}_{len(history)}",
                use_container_width=False,
            ):
                with st.spinner("Tutor is thinking..."):
                    response = _call_gemini_chat(
                        history + [{"role":"user","content":prompt}],
                        topic
                    )
                st.session_state[chat_key] = history + [
                    {"role":"user",    "content":prompt},
                    {"role":"assistant","content":response},
                ]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Input form ─────────────────────────────────────────────────────
    with st.form(
        key=f"{key_prefix}form_{topic}_{len(history)}",
        clear_on_submit=True
    ):
        cols = st.columns([5, 1])
        with cols[0]:
            user_input = st.text_input(
                "message",
                placeholder=f"Ask anything about {topic}...",
                label_visibility="collapsed",
                key=f"{key_prefix}inp_{topic}_{len(history)}"
            )
        with cols[1]:
            send = st.form_submit_button(
                "Send", use_container_width=True, type="primary"
            )

    if send and user_input.strip():
        new_history = history + [{"role":"user","content":user_input.strip()}]
        with st.spinner(""):
            response = _call_gemini_chat(new_history, topic)
        new_history.append({"role":"assistant","content":response})
        st.session_state[chat_key] = new_history
        st.rerun()

    # Reset + stats row
    col_r, col_s = st.columns([1, 3])
    with col_r:
        if history and st.button(
            "🔄 Clear chat",
            key=f"{key_prefix}reset_{topic}",
            use_container_width=True
        ):
            st.session_state[chat_key] = []
            st.rerun()
    with col_s:
        if len(history) >= 2:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#475569;padding:0.5rem 0">'
                f'📊 {len(history)//2} questions answered · '
                f'Keep going — consistency beats cramming</div>',
                unsafe_allow_html=True
            )