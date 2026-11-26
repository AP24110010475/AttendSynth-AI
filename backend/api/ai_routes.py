"""
backend/api/ai_routes.py — API endpoints for AI Academic Insights Assistant.

Integrates with Google Gemini API (model `gemini-3.8-flash`) via `backend.services.ai_service`.
Supports:
- GET  /api/ai/status
- POST /api/ai/analyze
- POST /api/ai/recommend
- POST /api/ai/chat
- POST /api/ai/report
- POST /api/ai/explain-student
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services import cohort_service, ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Academic Insights Assistant"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    history: Optional[List[Dict[str, str]]] = None


class StudentExplainRequest(BaseModel):
    student_id: str = Field(..., min_length=1)


@router.get("/status")
def get_ai_status() -> Dict[str, Any]:
    """Check whether Gemini API key is configured and return model information."""
    config_info = ai_service.get_gemini_config()
    return {
        "is_configured": config_info["is_configured"],
        "model": config_info["model"],
        "setup_instructions": (
            "Set GEMINI_API_KEY in your environment or in a .env file located at the project root."
            if not config_info["is_configured"]
            else "Gemini API is configured and ready."
        ),
    }


@router.post("/analyze")
def generate_analysis() -> Dict[str, Any]:
    """Generate comprehensive AI analysis of the current cohort."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active cohort found. Generate a dataset first.")

    res = ai_service.generate_dataset_analysis(df, meta)
    return res


@router.post("/recommend")
def generate_recommendations() -> Dict[str, Any]:
    """Generate institutional support & pedagogical recommendations."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active cohort found. Generate a dataset first.")

    res = ai_service.generate_support_recommendations(df, meta)
    return res


@router.post("/chat")
def chat_with_assistant(req: ChatRequest) -> Dict[str, Any]:
    """Ask natural language questions about the synthetic student cohort."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active cohort found. Generate a dataset first.")

    res = ai_service.chatbot_query(
        query=req.query,
        df=df,
        meta=meta,
        conversation_history=req.history,
    )
    return res


@router.post("/report")
def generate_cohort_report() -> Dict[str, Any]:
    """Compile structured formal AI institutional evaluation report."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active cohort found. Generate a dataset first.")

    res = ai_service.generate_cohort_report(df, meta)
    return res


@router.post("/explain-student")
def explain_student_risk(req: StudentExplainRequest) -> Dict[str, Any]:
    """Counselor-level risk factor analysis and personalized intervention plan for an individual student."""
    student = cohort_service.get_student(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID '{req.student_id}' was not found in active cohort.")

    res = ai_service.explain_student_risk(student)
    return res
