"""
backend/api/quality_routes.py — API endpoints for 11-point data quality validation audit.
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.validation import validate_dataset
from backend.services import cohort_service

router = APIRouter(prefix="/api/quality", tags=["Data Quality"])


@router.get("")
def get_data_quality_report() -> Dict[str, Any]:
    """Execute 11-point data quality validation and attribute completeness audit."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        return {
            "has_cohort": False,
            "total_records": 0,
            "quality_pct": 0.0,
            "passed_all": False,
            "summary": {},
            "checks": [],
            "attribute_completeness": [],
        }

    validation = validate_dataset(df)

    # Attribute completeness analysis
    null_counts = df.isnull().sum()
    attribute_completeness = []
    for col in df.columns:
        cnt = int(null_counts[col])
        attribute_completeness.append({
            "column": col,
            "missing_count": cnt,
            "missing_percentage": round(cnt / len(df) * 100, 2),
            "status": "OK" if cnt == 0 else "Missing",
        })

    # Prepare string-safe check details for JSON serialization
    serialized_checks = []
    for c in validation["checks"]:
        detail_val = c.get("detail", {})
        serialized_checks.append({
            "check": c["check"],
            "passed": bool(c["passed"]),
            "count": int(c["count"]),
            "detail": str(detail_val) if detail_val else "None",
        })

    return {
        "has_cohort": True,
        "total_records": validation["total_records"],
        "valid_records": validation["valid_records"],
        "invalid_records": validation["invalid_records"],
        "quality_pct": validation["quality_pct"],
        "passed_all": validation["passed_all"],
        "summary": validation["summary"],
        "checks": serialized_checks,
        "attribute_completeness": attribute_completeness,
    }
