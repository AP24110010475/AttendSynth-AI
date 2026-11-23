"""
risk_engine.py — Rule-based early-warning risk scoring for AttendSynth AI.

NOTE: This is a transparent rule-based system.
      It is NOT a trained machine-learning model.
      Risk scores are computed deterministically from the four input variables.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ---------------------------------------------------------------------------
# Risk factor analysis helpers
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "attendance_critical":   50.0,   # < 50 % → critical flag
    "attendance_low":        65.0,   # < 65 % → low flag
    "engagement_critical":   40.0,
    "engagement_low":        55.0,
    "assignment_critical":   50.0,
    "assignment_low":        65.0,
    "academic_critical":     45.0,
    "academic_low":          55.0,
}


def get_contributing_factors(row: pd.Series) -> List[str]:
    """Return a list of human-readable risk factor strings for one student."""
    factors = []

    att = row["attendance_percentage"]
    if att < THRESHOLDS["attendance_critical"]:
        factors.append(f"⚠️ Critical attendance: {att:.1f}% (below 50%)")
    elif att < THRESHOLDS["attendance_low"]:
        factors.append(f"📉 Low attendance: {att:.1f}% (below 65%)")

    eng = row["engagement_score"]
    if eng < THRESHOLDS["engagement_critical"]:
        factors.append(f"⚠️ Critical engagement: {eng:.1f} (below 40)")
    elif eng < THRESHOLDS["engagement_low"]:
        factors.append(f"📉 Low engagement: {eng:.1f} (below 55)")

    asgn = row["assignment_completion_percentage"]
    if asgn < THRESHOLDS["assignment_critical"]:
        factors.append(f"⚠️ Critical assignment completion: {asgn:.1f}% (below 50%)")
    elif asgn < THRESHOLDS["assignment_low"]:
        factors.append(f"📉 Low assignment completion: {asgn:.1f}% (below 65%)")

    acad = row["academic_performance_score"]
    if acad < THRESHOLDS["academic_critical"]:
        factors.append(f"⚠️ Critical academic performance: {acad:.1f} (below 45)")
    elif acad < THRESHOLDS["academic_low"]:
        factors.append(f"📉 Low academic performance: {acad:.1f} (below 55)")

    if not factors:
        factors.append("✅ No major risk factors identified")

    return factors


def summarise_risk_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return counts and percentages for each risk category.
    """
    total = len(df)
    counts = df["risk_category"].value_counts().to_dict()
    pcts   = {k: round(v / total * 100, 2) for k, v in counts.items()}

    return {
        "counts":      counts,
        "percentages": pcts,
        "total":       total,
        "high_risk_count":   counts.get("High", 0),
        "medium_risk_count": counts.get("Medium", 0),
        "low_risk_count":    counts.get("Low", 0),
    }


def get_high_risk_students(df: pd.DataFrame) -> pd.DataFrame:
    """Return a filtered DataFrame containing only High-risk students."""
    return df[df["risk_category"] == "High"].copy()


def get_risk_insights(df: pd.DataFrame) -> List[str]:
    """
    Generate automatic textual insights about the risk distribution.
    """
    dist  = summarise_risk_distribution(df)
    total = dist["total"]
    high  = dist["high_risk_count"]
    med   = dist["medium_risk_count"]
    low   = dist["low_risk_count"]
    insights = []

    high_pct = round(high / total * 100, 1) if total else 0
    med_pct  = round(med  / total * 100, 1) if total else 0

    if high_pct >= 20:
        insights.append(
            f"🔴 **{high_pct}%** of students ({high}) are classified as "
            f"**High-risk** — immediate intervention recommended."
        )
    elif high_pct >= 10:
        insights.append(
            f"🟠 **{high_pct}%** of students ({high}) are **High-risk** — "
            f"monitor closely."
        )
    else:
        insights.append(
            f"🟢 Only **{high_pct}%** of students ({high}) are **High-risk** — "
            f"the cohort is performing well overall."
        )

    if med_pct >= 40:
        insights.append(
            f"🟡 A large segment ({med_pct}%, n={med}) is at **Medium risk** — "
            f"consider proactive support measures."
        )

    avg_att = df["attendance_percentage"].mean()
    if avg_att < 70:
        insights.append(
            f"📉 Average attendance is **{avg_att:.1f}%**, which is below the 70% "
            f"recommended threshold."
        )
    else:
        insights.append(
            f"📈 Average attendance is **{avg_att:.1f}%** — healthy overall."
        )

    avg_eng = df["engagement_score"].mean()
    insights.append(
        f"💡 Average engagement score: **{avg_eng:.1f} / 100**."
    )

    return insights


RISK_CATEGORY_EXPLANATIONS = {
    "Low": (
        "Students with risk scores below **35** are classified as Low-risk.  "
        "They typically maintain high attendance (≥ 80%), complete most "
        "assignments, and have strong engagement scores.  Regular monitoring "
        "is still advisable."
    ),
    "Medium": (
        "Students with risk scores between **35 and 59** are classified as "
        "Medium-risk.  They exhibit inconsistent attendance or moderate "
        "engagement.  Targeted support and check-ins can prevent escalation."
    ),
    "High": (
        "Students with risk scores of **60 or above** are classified as "
        "High-risk.  They often show critically low attendance, poor "
        "assignment completion, or very low engagement.  Immediate academic "
        "counselling and intervention are recommended."
    ),
}
