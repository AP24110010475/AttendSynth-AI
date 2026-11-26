"""
backend/api/risk_routes.py — API endpoints for Early Warning rule-based risk analysis.
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from src.risk_engine import (
    summarise_risk_distribution,
    get_high_risk_students,
    get_contributing_factors,
    get_risk_insights,
    RISK_CATEGORY_EXPLANATIONS,
    THRESHOLDS,
)
from backend.services import cohort_service

router = APIRouter(prefix="/api/risk", tags=["Early Warning Risk"])


@router.get("")
def get_risk_analysis() -> Dict[str, Any]:
    """Retrieve full early-warning risk evaluation for the active cohort."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        return {
            "has_cohort": False,
            "total_evaluated": 0,
            "distribution": {},
            "high_risk_students": [],
            "risk_score_histogram": {},
            "insights": [],
            "formula_info": {},
            "explanations": {},
        }

    dist = summarise_risk_distribution(df)
    insights = get_risk_insights(df)
    high_risk_df = get_high_risk_students(df)

    # Risk score histogram (0-100 in 10 buckets)
    counts, edges = np.histogram(df["risk_score"], bins=10, range=(0, 100))
    hist_labels = [f"{int(edges[i])}–{int(edges[i+1])}" for i in range(len(counts))]
    score_hist = {
        "labels": hist_labels,
        "counts": counts.tolist(),
    }

    # Format high risk students with top factor
    high_risk_records = []
    for _, row in high_risk_df.head(100).iterrows():
        factors = get_contributing_factors(row)
        high_risk_records.append({
            "student_id": row["student_id"],
            "department": row["department"],
            "year_of_study": row["year_of_study"],
            "attendance_percentage": float(row["attendance_percentage"]),
            "engagement_score": float(row["engagement_score"]),
            "assignment_completion_percentage": float(row["assignment_completion_percentage"]),
            "academic_performance_score": float(row["academic_performance_score"]),
            "risk_score": float(row["risk_score"]),
            "primary_factors": factors,
        })

    return {
        "has_cohort": True,
        "total_evaluated": dist["total"],
        "distribution": dist,
        "risk_score_histogram": score_hist,
        "high_risk_count": dist["high_risk_count"],
        "high_risk_students": high_risk_records,
        "insights": insights,
        "formula_info": {
            "weights": config.RISK_WEIGHTS,
            "thresholds": {
                "low_max": config.RISK_LOW_MAX,
                "medium_max": config.RISK_MEDIUM_MAX,
            },
            "formula_string": "risk_score = 100 - (0.35 * attendance + 0.25 * engagement + 0.25 * assignment + 0.15 * academic_perf)",
        },
        "explanations": RISK_CATEGORY_EXPLANATIONS,
    }


@router.get("/student/{student_id}")
def get_student_risk_factors(student_id: str) -> Dict[str, Any]:
    """Retrieve individual student record with contributing risk factors and formula values."""
    student = cohort_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")

    row = pd.Series(student)
    factors = get_contributing_factors(row)

    w = config.RISK_WEIGHTS
    att_contrib = round(w["attendance"] * float(student["attendance_percentage"]), 2)
    eng_contrib = round(w["engagement"] * float(student["engagement_score"]), 2)
    asgn_contrib = round(w["assignment"] * float(student["assignment_completion_percentage"]), 2)
    acad_contrib = round(w["academic_perf"] * float(student["academic_performance_score"]), 2)
    positive_index = round(att_contrib + eng_contrib + asgn_contrib + acad_contrib, 2)

    return {
        "student": student,
        "contributing_factors": factors,
        "formula_breakdown": {
            "attendance_contribution": att_contrib,
            "engagement_contribution": eng_contrib,
            "assignment_contribution": asgn_contrib,
            "academic_contribution": acad_contrib,
            "positive_index": positive_index,
            "risk_score": student["risk_score"],
            "risk_category": student["risk_category"],
        },
    }
