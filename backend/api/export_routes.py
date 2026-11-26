"""
backend/api/export_routes.py — API endpoints for CSV and JSON cohort and quality report downloads.
"""

from __future__ import annotations
import os
import sys
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import StreamingResponse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from src.export import (
    to_csv_bytes,
    to_json_bytes,
    quality_report_to_csv_bytes,
    quality_report_to_json_bytes,
)
from src.validation import validate_dataset
from backend.services import cohort_service

router = APIRouter(prefix="/api/export", tags=["Export Center"])


@router.get("/csv")
def export_dataset_csv(
    search_id: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    year_of_study: Optional[str] = Query(default=None),
    semester: Optional[str] = Query(default=None),
    risk_category: Optional[str] = Query(default=None),
    filtered: bool = Query(default=False),
) -> Response:
    """Download full or filtered cohort as CSV."""
    df, _ = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active dataset available for export.")

    if filtered:
        export_df = cohort_service.filter_cohort(
            search_id=search_id,
            department=department,
            year_of_study=year_of_study,
            semester=semester,
            risk_category=risk_category,
        )
        filename = config.EXPORT_CSV_FILTERED
    else:
        export_df = df
        filename = config.EXPORT_CSV_FULL

    csv_data = to_csv_bytes(export_df)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/json")
def export_dataset_json(
    search_id: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    year_of_study: Optional[str] = Query(default=None),
    semester: Optional[str] = Query(default=None),
    risk_category: Optional[str] = Query(default=None),
    filtered: bool = Query(default=False),
) -> Response:
    """Download full or filtered cohort as JSON."""
    df, _ = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active dataset available for export.")

    if filtered:
        export_df = cohort_service.filter_cohort(
            search_id=search_id,
            department=department,
            year_of_study=year_of_study,
            semester=semester,
            risk_category=risk_category,
        )
        filename = "attendsynth_dataset_filtered.json"
    else:
        export_df = df
        filename = config.EXPORT_JSON_FULL

    json_data = to_json_bytes(export_df)
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/quality/csv")
def export_quality_report_csv() -> Response:
    """Download data quality audit report as CSV."""
    df, _ = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active dataset available to audit.")

    val_res = validate_dataset(df)
    csv_bytes = quality_report_to_csv_bytes(val_res)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{config.EXPORT_QUALITY_REPORT}"'},
    )


@router.get("/quality/json")
def export_quality_report_json() -> Response:
    """Download data quality audit report as JSON."""
    df, _ = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active dataset available to audit.")

    val_res = validate_dataset(df)
    json_bytes = quality_report_to_json_bytes(val_res)
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="attendsynth_quality_report.json"'},
    )
