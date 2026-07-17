from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import json
from typing import Dict, Any, List, Optional

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_student(email: str, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        existing = (
            supabase.table("students")
            .select("*").eq("email", email).execute()
        )
        if existing.data:
            result = (
                supabase.table("students")
                .update({**data, "updated_at": "now()"})
                .eq("email", email).execute()
            )
            return result.data[0] if result.data else {}
        else:
            result = (
                supabase.table("students")
                .insert({"email": email, **data}).execute()
            )
            return result.data[0] if result.data else {}
    except Exception as e:
        print(f"DB error upsert_student: {e}")
        return {}

def get_student(email: str) -> Optional[Dict[str, Any]]:
    try:
        result = (
            supabase.table("students")
            .select("*").eq("email", email).execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"DB error get_student: {e}")
        return None

def save_analysis(student_id: str, analysis: Dict[str, Any]) -> bool:
    try:
        supabase.table("analyses").insert({
            "student_id":        student_id,
            "detected_skills":   analysis.get("detected_skills", []),
            "top_gaps":          analysis.get("top_gaps", []),
            "eligible_companies": analysis.get("eligible_companies", []),
            "company_alignments": analysis.get("company_alignments", []),
            "daily_plan":        analysis.get("daily_plan", []),
            "mock_questions":    analysis.get("mock_questions", []),
            "overall_mock_score": float(analysis.get("mock_overall_score", 0)),
        }).execute()
        return True
    except Exception as e:
        print(f"DB error save_analysis: {e}")
        return False

def get_latest_analysis(student_id: str) -> Optional[Dict[str, Any]]:
    try:
        result = (
            supabase.table("analyses")
            .select("*")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(1).execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"DB error get_latest_analysis: {e}")
        return None

def save_progress(
    student_id: str, day: int,
    topic: str, completed: bool = False
) -> bool:
    try:
        supabase.table("daily_progress").upsert({
            "student_id": student_id,
            "day_number": day,
            "topic":      topic,
            "completed":  completed,
        }).execute()
        return True
    except Exception as e:
        print(f"DB error save_progress: {e}")
        return False

def get_progress(student_id: str) -> List[Dict[str, Any]]:
    try:
        result = (
            supabase.table("daily_progress")
            .select("*")
            .eq("student_id", student_id)
            .order("day_number").execute()
        )
        return result.data or []
    except Exception as e:
        print(f"DB error get_progress: {e}")
        return []