"""
backend/services/ai_service.py — Generative AI Academic Insights Assistant service.

Uses the official Google GenAI Python SDK with model `gemini-3.8-flash`.
Enforces strict grounding on calculated Python statistics — never allows the model
to hallucinate or invent numbers. Transparently distinguishes facts from advice
and adds an institutional advisory disclaimer.
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any, List, Optional
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.analytics import compute_kpis, generate_insights
from src.risk_engine import summarise_risk_distribution, get_contributing_factors

DISCLAIMER = (
    "\n\n*Institutional Advisory Notice: Generative AI suggestions are for educational "
    "simulation and academic decision support only. All statistical metrics reflect synthetically "
    "generated student data.*"
)


def get_gemini_config() -> Dict[str, Any]:
    """Retrieve Gemini API configuration from environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
    return {
        "api_key": api_key,
        "model": model,
        "is_configured": bool(api_key),
    }


def _get_genai_client():
    """Initialize and return the official Google GenAI Client if API key is present."""
    config_info = get_gemini_config()
    if not config_info["is_configured"]:
        return None, None
    try:
        from google import genai
        client = genai.Client(api_key=config_info["api_key"])
        return client, config_info["model"]
    except Exception as e:
        return None, str(e)


def build_cohort_stats_summary(df: pd.DataFrame, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compute deterministic Python statistical profile for grounding Gemini prompts."""
    kpi = compute_kpis(df)
    risk_dist = summarise_risk_distribution(df)

    dept_stats = (
        df.groupby("department")
        .agg(
            students=("student_id", "count"),
            avg_attendance=("attendance_percentage", "mean"),
            avg_engagement=("engagement_score", "mean"),
            avg_academic=("academic_performance_score", "mean"),
            high_risk_count=("risk_category", lambda s: int((s == "High").sum())),
        )
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )

    corr_att_eng = float(df["attendance_percentage"].corr(df["engagement_score"]))
    corr_att_acad = float(df["attendance_percentage"].corr(df["academic_performance_score"]))

    python_insights = generate_insights(df)

    return {
        "total_students": kpi["total_students"],
        "academic_year": meta.get("academic_year", "N/A") if meta else "N/A",
        "semester": meta.get("semester", "N/A") if meta else "N/A",
        "avg_attendance": kpi["avg_attendance"],
        "avg_engagement": kpi["avg_engagement"],
        "avg_academic_performance": kpi["avg_academic"],
        "avg_assignment_completion": kpi["avg_assignment"],
        "risk_breakdown": {
            "Low": f"{risk_dist['low_risk_count']} ({risk_dist['percentages'].get('Low', 0)}%)",
            "Medium": f"{risk_dist['medium_risk_count']} ({risk_dist['percentages'].get('Medium', 0)}%)",
            "High": f"{risk_dist['high_risk_count']} ({risk_dist['percentages'].get('High', 0)}%)",
        },
        "department_metrics": dept_stats,
        "correlations": {
            "attendance_to_engagement": round(corr_att_eng, 2),
            "attendance_to_academic": round(corr_att_acad, 2),
        },
        "calculated_observations": python_insights,
    }


def generate_dataset_analysis(df: pd.DataFrame, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Feature A: Generate AI Dataset Analysis grounded strictly on computed stats."""
    stats = build_cohort_stats_summary(df, meta)
    client, model_or_err = _get_genai_client()

    if client is None:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not configured. Set GEMINI_API_KEY in your environment or .env file to enable AI insights.",
            "stats": stats,
            "analysis": None,
        }

    prompt = f"""You are the senior Academic Analytics AI for AttendSynth AI.
Your task is to analyze the following calculated student cohort dataset statistics:

=== CALCULATED DATASET STATISTICS (SOURCE OF TRUTH) ===
Total Students: {stats['total_students']} (Term: {stats['academic_year']}, Semester: {stats['semester']})
Average Attendance: {stats['avg_attendance']}%
Average Engagement Score: {stats['avg_engagement']}/100
Average Academic Score: {stats['avg_academic_performance']}/100
Average Assignment Completion: {stats['avg_assignment_completion']}%
Risk Distribution: Low={stats['risk_breakdown']['Low']}, Medium={stats['risk_breakdown']['Medium']}, High={stats['risk_breakdown']['High']}
Pearson Correlation (Attendance & Engagement): {stats['correlations']['attendance_to_engagement']}
Department Breakdown:
{stats['department_metrics']}

Grounding Rules:
1. ONLY cite the exact numbers provided above. DO NOT invent or extrapolate different numerical values.
2. Structure your analysis into clear sections:
   - Executive Overview & Health Score
   - Attendance & Engagement Dynamics
   - Academic Performance & Risk Vulnerability
   - Departmental Disparities
   - Critical Observations
3. Clearly distinguish calculated facts from pedagogical recommendations.
"""
    try:
        response = client.models.generate_content(model=model_or_err, contents=prompt)
        text = response.text + DISCLAIMER
        return {
            "status": "success",
            "model": model_or_err,
            "stats": stats,
            "analysis": text,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API request failed: {str(e)}",
            "stats": stats,
            "analysis": None,
        }


def generate_support_recommendations(df: pd.DataFrame, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Feature B: Generate AI Student Support Recommendations based on cohort state."""
    stats = build_cohort_stats_summary(df, meta)
    client, model_or_err = _get_genai_client()

    if client is None:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not configured. Please set GEMINI_API_KEY.",
            "stats": stats,
            "recommendations": None,
        }

    prompt = f"""You are an educational psychologist and academic intervention specialist.
Provide targeted, actionable institutional support recommendations based on the following cohort metrics:

Total Students: {stats['total_students']}
Average Attendance: {stats['avg_attendance']}%
Average Engagement: {stats['avg_engagement']}/100
Average Assignment Completion: {stats['avg_assignment_completion']}%
High-Risk Students: {stats['risk_breakdown']['High']}
Medium-Risk Students: {stats['risk_breakdown']['Medium']}
Department Metrics: {stats['department_metrics']}

Provide structured recommendations categorized into:
1. Immediate Interventions for High-Risk Cohort (Attendance < 50%, High Risk)
2. Preventative Measures for Medium-Risk Segment
3. Strategies to Boost Digital LMS Engagement & Assignment Completion
4. Department-Specific Targeted Support Programs
5. Long-term Retention & Student Success Frameworks

Rules: Reference the supplied statistics accurately. Do not invent contradictory numbers."""

    try:
        response = client.models.generate_content(model=model_or_err, contents=prompt)
        text = response.text + DISCLAIMER
        return {
            "status": "success",
            "model": model_or_err,
            "stats": stats,
            "recommendations": text,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API request failed: {str(e)}",
            "stats": stats,
            "recommendations": None,
        }


def chatbot_query(query: str, df: pd.DataFrame, meta: Optional[Dict[str, Any]] = None, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Feature C: Natural Language Dataset Chatbot grounded on actual cohort data."""
    if not query or not query.strip():
        return {"status": "error", "message": "Query cannot be empty."}

    stats = build_cohort_stats_summary(df, meta)
    client, model_or_err = _get_genai_client()

    if client is None:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not configured. Add GEMINI_API_KEY to your environment to chat with AttendSynth AI.",
            "reply": None,
        }

    history_text = ""
    if conversation_history:
        for turn in conversation_history[-6:]:
            role = "User" if turn.get("role") == "user" else "Assistant"
            history_text += f"{role}: {turn.get('content', '')}\n"

    prompt = f"""You are the conversational assistant for the AttendSynth AI student dataset platform.
Answer the user's question using ONLY the calculated dataset statistics provided below.

=== GROUND TRUTH DATASET SUMMARY ===
Cohort Size: {stats['total_students']} students ({stats['academic_year']}, {stats['semester']} semester)
Average Attendance: {stats['avg_attendance']}%
Average Engagement: {stats['avg_engagement']}/100
Average Academic Score: {stats['avg_academic_performance']}/100
Average Assignment Completion: {stats['avg_assignment_completion']}%
Risk Tiers: Low = {stats['risk_breakdown']['Low']}, Medium = {stats['risk_breakdown']['Medium']}, High = {stats['risk_breakdown']['High']}
Attendance-to-Engagement Pearson Correlation: {stats['correlations']['attendance_to_engagement']}
Department Breakdown:
{stats['department_metrics']}

Key Observations:
{stats['calculated_observations']}

Recent Chat History:
{history_text}

User Question: {query.strip()}

Instructions:
1. Answer directly and concisely based strictly on the facts provided above.
2. If asked which department has the highest attendance or how many high-risk students exist, quote the exact numbers from the stats.
3. If the user asks for suggestions or interventions, provide practical academic guidance grounded in the data.
4. If a question asks about information not in the dataset summary, state politely that the dataset does not record that metric."""

    try:
        response = client.models.generate_content(model=model_or_err, contents=prompt)
        return {
            "status": "success",
            "model": model_or_err,
            "reply": response.text,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API request failed: {str(e)}",
            "reply": None,
        }


def generate_cohort_report(df: pd.DataFrame, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Feature D: Generate Full AI Cohort Report with standard institutional structure."""
    stats = build_cohort_stats_summary(df, meta)
    client, model_or_err = _get_genai_client()

    if client is None:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not configured. Please set GEMINI_API_KEY.",
            "stats": stats,
            "report": None,
        }

    prompt = f"""You are an institutional research director drafting a formal Academic Cohort Evaluation Report.
Compile an exhaustive, professionally formatted Markdown report based on these real computed statistics:

Cohort Details: {stats['total_students']} students, Academic Year {stats['academic_year']}, Semester {stats['semester']}
Overall Metrics:
- Attendance: {stats['avg_attendance']}%
- Engagement: {stats['avg_engagement']}/100
- Assignment Completion: {stats['avg_assignment_completion']}%
- Academic Performance: {stats['avg_academic_performance']}/100
- Risk Tiers: {stats['risk_breakdown']}
- Pearson Correlation (Att vs Eng): {stats['correlations']['attendance_to_engagement']}
- Department Data: {stats['department_metrics']}

Required Report Structure (Use standard Markdown headers):
# Executive Summary
# Key Findings & Cohort Baseline
# Attendance Analysis
# Engagement & Platform Activity Analysis
# Academic Performance Evaluation
# Early-Warning & Risk Vulnerability Analysis
# Departmental Comparative Analysis
# Strategic Recommendations (Immediate, Short-Term, Policy)
# Conclusion & Next Steps

Adhere strictly to the supplied numbers. Never invent divergent figures."""

    try:
        response = client.models.generate_content(model=model_or_err, contents=prompt)
        text = response.text + DISCLAIMER
        return {
            "status": "success",
            "model": model_or_err,
            "stats": stats,
            "report": text,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API request failed: {str(e)}",
            "stats": stats,
            "report": None,
        }


def explain_student_risk(student: Dict[str, Any]) -> Dict[str, Any]:
    """Feature E: Explain risk factors of an individual synthetic student."""
    factors = get_contributing_factors(pd.Series(student))
    client, model_or_err = _get_genai_client()

    if client is None:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not configured. Please configure GEMINI_API_KEY.",
            "student_id": student.get("student_id"),
            "calculated_factors": factors,
            "explanation": None,
        }

    prompt = f"""You are an academic counselor analyzing a specific synthetic student profile:
Student ID: {student.get('student_id')}
Department: {student.get('department')}
Year of Study: {student.get('year_of_study')}
Semester: {student.get('semester')}
Attendance: {student.get('attendance_percentage')}% ({student.get('classes_attended')}/{student.get('total_classes')} classes)
Engagement Score: {student.get('engagement_score')}/100
Assignment Completion: {student.get('assignment_completion_percentage')}%
Platform Activity: {student.get('learning_platform_activity')}/100
Participation: {student.get('participation_score')}/100
Academic Score: {student.get('academic_performance_score')}/100
Risk Score: {student.get('risk_score')}/100
Risk Category: {student.get('risk_category')}

Identified Deterministic Flags:
{factors}

Please provide:
1. Student Profile Assessment: Narrative summary of their current engagement posture.
2. Root Factor Breakdown: Detailed explanation of why their risk score reached {student.get('risk_score')}.
3. Tailored Academic Counseling Plan: 3-4 concrete interventions specific to this student's lowest metric.
4. Faculty Advisory Note: What instructors should observe in the next 2-3 weeks.

Rules: Use exact numbers from the profile. Keep tone professional, constructive, and empathetic."""

    try:
        response = client.models.generate_content(model=model_or_err, contents=prompt)
        text = response.text + DISCLAIMER
        return {
            "status": "success",
            "model": model_or_err,
            "student_id": student.get("student_id"),
            "calculated_factors": factors,
            "explanation": text,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API request failed: {str(e)}",
            "student_id": student.get("student_id"),
            "calculated_factors": factors,
            "explanation": None,
        }
