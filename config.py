import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ── API Keys ───────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN     = os.getenv("GITHUB_TOKEN")
SERPER_API_KEY   = os.getenv("SERPER_API_KEY")
YOUTUBE_API_KEY  = os.getenv("YOUTUBE_API_KEY")
TWILIO_SID       = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH      = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM      = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_TO        = os.getenv("TWILIO_WHATSAPP_TO")
SUPABASE_URL     = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY     = os.getenv("SUPABASE_KEY", "")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing from .env")

genai.configure(api_key=GEMINI_API_KEY)

PRO_MODEL   = "gemini-1.5-pro"
FLASH_MODEL = "gemini-1.5-flash"

# ── Tier-1 Company Intelligence ────────────────────────────────────────────
COMPANY_REQUIREMENTS = {
    "Google": {
        "min_cgpa": 7.0,
        "tier": 1,
        "difficulty": "Extreme",
        "interview_rounds": 5,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Dynamic Programming", "Graph Algorithms",
            "Distributed Systems", "Python or C++"
        ],
        "pattern": "4 DSA rounds (LeetCode Hard) + 1 System Design + Googleyness",
        "typical_questions": [
            "Implement LRU Cache with O(1) get and put",
            "Find median of two sorted arrays in O(log n)",
            "Design Google Drive distributed file system",
            "Word Ladder II — all shortest paths",
            "Serialize and deserialize N-ary tree"
        ],
        "leetcode_tags": [
            "hash-table", "dynamic-programming", "graph",
            "binary-search", "tree", "design"
        ],
        "ctc_range": "40-60 LPA"
    },
    "Microsoft": {
        "min_cgpa": 7.0,
        "tier": 1,
        "difficulty": "Very High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms", "OOP",
            "System Design", "Problem Solving",
            "Python or Java or C++"
        ],
        "pattern": "3 DSA rounds + 1 Design/Behavioural",
        "typical_questions": [
            "Clone graph with random pointers",
            "LRU Cache implementation",
            "Number of islands — BFS/DFS",
            "Design parking lot system",
            "Maximum profit stock problem"
        ],
        "leetcode_tags": [
            "linked-list", "tree", "graph",
            "dynamic-programming", "design", "array"
        ],
        "ctc_range": "35-55 LPA"
    },
    "Amazon": {
        "min_cgpa": 6.5,
        "tier": 1,
        "difficulty": "High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms",
            "Leadership Principles", "System Design basics",
            "Java or Python"
        ],
        "pattern": "2 online assessments + 3 interviews (DSA + LP + System Design)",
        "typical_questions": [
            "Two Sum and variations",
            "Merge k sorted linked lists",
            "Implement stack using queues",
            "Design Amazon locker system",
            "Maximum subarray (Kadane's algorithm)"
        ],
        "leetcode_tags": [
            "array", "string", "linked-list",
            "tree", "design", "two-pointers"
        ],
        "ctc_range": "30-45 LPA"
    },
    "Meta": {
        "min_cgpa": 7.5,
        "tier": 1,
        "difficulty": "Extreme",
        "interview_rounds": 5,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Graph Algorithms", "Dynamic Programming",
            "Python or C++"
        ],
        "pattern": "2 coding + 1 system design + 1 behavioural + 1 reverse interview",
        "typical_questions": [
            "Minimum window substring",
            "Trapping rain water",
            "Design Facebook news feed",
            "Find all permutations of a string",
            "Binary tree right side view"
        ],
        "leetcode_tags": [
            "sliding-window", "two-pointers", "graph",
            "dynamic-programming", "tree", "design"
        ],
        "ctc_range": "50-80 LPA"
    },
    "Apple": {
        "min_cgpa": 7.5,
        "tier": 1,
        "difficulty": "Very High",
        "interview_rounds": 5,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Swift or Python or C++", "Low-level programming"
        ],
        "pattern": "Technical phone screen + 4-5 on-site rounds (coding + design + culture)",
        "typical_questions": [
            "Implement autocomplete system",
            "Design iCloud sync system",
            "Find kth largest element",
            "Valid parentheses with multiple types",
            "Spiral matrix traversal"
        ],
        "leetcode_tags": [
            "heap", "design", "string",
            "array", "tree", "system-design"
        ],
        "ctc_range": "45-70 LPA"
    },
    "Flipkart": {
        "min_cgpa": 6.5,
        "tier": 1,
        "difficulty": "High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Java or Python", "Database concepts"
        ],
        "pattern": "Online test + 3 technical rounds + 1 HR",
        "typical_questions": [
            "Design Flipkart's recommendation system",
            "Implement order tracking system",
            "Find top k frequent elements",
            "Detect cycle in directed graph",
            "Design rate limiter"
        ],
        "leetcode_tags": [
            "heap", "graph", "design",
            "hash-table", "tree", "array"
        ],
        "ctc_range": "25-40 LPA"
    },
    "Goldman Sachs": {
        "min_cgpa": 7.0,
        "tier": 1,
        "difficulty": "Very High",
        "interview_rounds": 5,
        "skills_required": [
            "Data Structures", "Algorithms", "Quantitative Aptitude",
            "Java or Python or C++", "System Design", "Finance basics"
        ],
        "pattern": "HackerRank test + 4-5 technical + behavioural rounds",
        "typical_questions": [
            "Implement order matching engine",
            "Find arbitrage opportunity in currency exchange",
            "Design trade settlement system",
            "Maximum profit with at most k transactions",
            "Implement trie for autocomplete"
        ],
        "leetcode_tags": [
            "dynamic-programming", "graph", "design",
            "math", "string", "array"
        ],
        "ctc_range": "30-50 LPA"
    },
    "Adobe": {
        "min_cgpa": 7.0,
        "tier": 1,
        "difficulty": "High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms", "OOP",
            "C++ or Java or Python", "System Design"
        ],
        "pattern": "Online coding test + 3 technical rounds + 1 HR",
        "typical_questions": [
            "Implement image rotation algorithm",
            "Design Adobe Acrobat rendering engine",
            "Clone binary tree with random pointers",
            "Find celebrity in a party",
            "Implement LFU cache"
        ],
        "leetcode_tags": [
            "array", "design", "tree",
            "matrix", "hash-table", "linked-list"
        ],
        "ctc_range": "20-35 LPA"
    },
    "Uber": {
        "min_cgpa": 6.5,
        "tier": 1,
        "difficulty": "High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Distributed Systems", "Python or Java or Go"
        ],
        "pattern": "Phone screen + 4 on-site rounds (coding + system design + culture)",
        "typical_questions": [
            "Design Uber surge pricing system",
            "Find nearest driver using geohashing",
            "Implement ride matching algorithm",
            "Design real-time location tracking",
            "Shortest path in city map graph"
        ],
        "leetcode_tags": [
            "graph", "heap", "design",
            "math", "tree", "greedy"
        ],
        "ctc_range": "25-45 LPA"
    },
    "Atlassian": {
        "min_cgpa": 7.0,
        "tier": 1,
        "difficulty": "High",
        "interview_rounds": 4,
        "skills_required": [
            "Data Structures", "Algorithms", "System Design",
            "Java or Python", "Distributed Systems"
        ],
        "pattern": "Take-home project + 4 technical interviews",
        "typical_questions": [
            "Design JIRA issue tracking system",
            "Implement collaborative text editor (OT/CRDT)",
            "Design Confluence page hierarchy",
            "Find connected components in dependency graph",
            "Implement webhook delivery system"
        ],
        "leetcode_tags": [
            "graph", "design", "tree",
            "string", "hash-table", "linked-list"
        ],
        "ctc_range": "25-40 LPA"
    }
}