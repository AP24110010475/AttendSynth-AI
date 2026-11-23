"""
validation.py — Data quality checks for AttendSynth AI generated datasets.

Runs a suite of deterministic checks and returns a structured report.
Does not modify the original DataFrame.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    missing = df.isnull().sum()
    total_missing = int(missing.sum())
    return {
        "check": "Missing Values",
        "passed": total_missing == 0,
        "count": total_missing,
        "detail": missing[missing > 0].to_dict() if total_missing > 0 else {},
    }


def check_duplicate_ids(df: pd.DataFrame) -> Dict[str, Any]:
    dupes = int(df["student_id"].duplicated().sum())
    return {
        "check": "Duplicate Student IDs",
        "passed": dupes == 0,
        "count": dupes,
        "detail": {},
    }


def check_attendance_percentage(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[
        (df["attendance_percentage"] < 0) | (df["attendance_percentage"] > 100)
    ]
    return {
        "check": "Attendance % Range (0-100)",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {"invalid_ids": invalid["student_id"].tolist()[:10]},
    }


def check_attendance_calculation(df: pd.DataFrame) -> Dict[str, Any]:
    """classes_attended / total_classes should match attendance_percentage (±1 %)."""
    computed = (df["classes_attended"] / df["total_classes"] * 100).round(2)
    mismatch = df[np.abs(computed - df["attendance_percentage"]) > 1.0]
    return {
        "check": "Attendance Calculation Consistency",
        "passed": len(mismatch) == 0,
        "count": len(mismatch),
        "detail": {"mismatched_ids": mismatch["student_id"].tolist()[:10]},
    }


def check_classes_not_exceeded(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[df["classes_attended"] > df["total_classes"]]
    return {
        "check": "Classes Attended ≤ Total Classes",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


def check_engagement_score(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[
        (df["engagement_score"] < 0) | (df["engagement_score"] > 100)
    ]
    return {
        "check": "Engagement Score Range (0-100)",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


def check_academic_performance(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[
        (df["academic_performance_score"] < 0)
        | (df["academic_performance_score"] > 100)
    ]
    return {
        "check": "Academic Performance Range (0-100)",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


def check_risk_score(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[(df["risk_score"] < 0) | (df["risk_score"] > 100)]
    return {
        "check": "Risk Score Range (0-100)",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


def check_risk_category(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[~df["risk_category"].isin(config.RISK_CATEGORIES)]
    return {
        "check": "Valid Risk Categories",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {"unexpected_values": df["risk_category"].unique().tolist()},
    }


def check_assignment_completion(df: pd.DataFrame) -> Dict[str, Any]:
    invalid = df[
        (df["assignment_completion_percentage"] < 0)
        | (df["assignment_completion_percentage"] > 100)
    ]
    return {
        "check": "Assignment Completion Range (0-100)",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


def check_ages(df: pd.DataFrame) -> Dict[str, Any]:
    lo, hi = config.AGE_RANGE
    invalid = df[(df["age"] < lo) | (df["age"] > hi)]
    return {
        "check": f"Age Range ({lo}-{hi})",
        "passed": len(invalid) == 0,
        "count": len(invalid),
        "detail": {},
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run all validation checks on the generated DataFrame.

    Returns
    -------
    dict with keys:
        total_records   : int
        checks          : list of individual check results
        invalid_records : int
        valid_records   : int
        quality_pct     : float (0-100)
        passed_all      : bool
        summary         : dict of key metrics
    """
    if df is None or df.empty:
        return {
            "total_records":   0,
            "checks":          [],
            "invalid_records": 0,
            "valid_records":   0,
            "quality_pct":     0.0,
            "passed_all":      False,
            "summary":         {},
        }

    checks = [
        check_missing_values(df),
        check_duplicate_ids(df),
        check_attendance_percentage(df),
        check_attendance_calculation(df),
        check_classes_not_exceeded(df),
        check_engagement_score(df),
        check_academic_performance(df),
        check_risk_score(df),
        check_risk_category(df),
        check_assignment_completion(df),
        check_ages(df),
    ]

    total  = len(df)
    # Count records flagged by at least one check
    flagged_ids: set = set()
    for c in checks:
        for ids in c.get("detail", {}).values():
            if isinstance(ids, list):
                flagged_ids.update(ids)
        if not c["passed"] and c["count"] > 0:
            # Use count as upper-bound proxy when IDs aren't tracked
            pass

    # A simpler invalid count: union of rows failing any range/consistency check
    invalid_mask = (
        (df["attendance_percentage"] < 0) | (df["attendance_percentage"] > 100) |
        (df["engagement_score"] < 0)      | (df["engagement_score"] > 100)      |
        (df["risk_score"] < 0)            | (df["risk_score"] > 100)             |
        (df["classes_attended"] > df["total_classes"])                            |
        (~df["risk_category"].isin(config.RISK_CATEGORIES))                      |
        df["student_id"].duplicated(keep=False)
    )
    invalid_count = int(invalid_mask.sum())
    valid_count   = total - invalid_count
    quality_pct   = round(valid_count / total * 100, 2) if total > 0 else 0.0
    passed_all    = all(c["passed"] for c in checks)

    summary = {
        "total_records":   total,
        "valid_records":   valid_count,
        "invalid_records": invalid_count,
        "missing_values":  int(df.isnull().sum().sum()),
        "duplicate_ids":   int(df["student_id"].duplicated().sum()),
        "quality_pct":     quality_pct,
        "passed_all":      passed_all,
    }

    return {
        "total_records":   total,
        "checks":          checks,
        "invalid_records": invalid_count,
        "valid_records":   valid_count,
        "quality_pct":     quality_pct,
        "passed_all":      passed_all,
        "summary":         summary,
    }
