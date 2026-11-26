"""
backend/api/generator_routes.py — API endpoints for synthetic student data generation.
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

import config
from src.generator import generate_dataset
from src.validation import validate_dataset
from src.analytics import compute_kpis
from backend.services import cohort_service

router = APIRouter(prefix="/api", tags=["Generator"])


class GenerateRequest(BaseModel):
    n_students: int = Field(default=config.DEFAULT_N_STUDENTS, ge=50, le=10_000)
    academic_year: str = Field(default=config.DEFAULT_ACADEMIC_YEAR)
    semester: str = Field(default=config.DEFAULT_SEMESTER)
    departments: Optional[List[str]] = None
    attendance_distribution: Optional[Dict[str, float]] = None
    seed: int = Field(default=config.DEFAULT_SEED, ge=0)
    auto_validate: bool = Field(default=True)


@router.post("/generate")
def generate_cohort_endpoint(req: GenerateRequest) -> Dict[str, Any]:
    """Generate a new synthetic student cohort and persist it to SQLite."""
    depts = req.departments or config.DEFAULT_DEPARTMENTS
    if not depts:
        raise HTTPException(status_code=400, detail="At least one department must be specified.")

    dist = req.attendance_distribution or config.DEFAULT_ATTENDANCE_DISTRIBUTION
    total_weight = sum(dist.values())
    if total_weight <= 0:
        raise HTTPException(status_code=400, detail="Attendance distribution weights must sum to > 0.")
    # Normalize distribution
    normalized_dist = {k: v / total_weight for k, v in dist.items()}

    try:
        df = generate_dataset(
            n_students=req.n_students,
            departments=depts,
            academic_year=req.academic_year,
            semester=req.semester,
            attendance_distribution=normalized_dist,
            seed=req.seed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

    meta = {
        "n_students": req.n_students,
        "academic_year": req.academic_year,
        "semester": req.semester,
        "departments": depts,
        "attendance_distribution": normalized_dist,
        "seed": req.seed,
    }

    # Save to SQLite and in-memory cache
    cohort_service.save_cohort(df, meta)

    # Compute immediate summary
    kpis = compute_kpis(df)
    validation_summary = None
    if req.auto_validate:
        val_res = validate_dataset(df)
        validation_summary = val_res.get("summary")

    return {
        "status": "success",
        "message": f"Successfully generated {len(df):,} synthetic student records.",
        "metadata": meta,
        "kpis": kpis,
        "validation_summary": validation_summary,
        "sample_records": df.head(5).to_dict(orient="records"),
    }


@router.get("/generator/defaults")
def get_generator_defaults() -> Dict[str, Any]:
    """Return default configuration parameters for frontend forms."""
    return {
        "default_n_students": config.DEFAULT_N_STUDENTS,
        "default_seed": config.DEFAULT_SEED,
        "default_academic_year": config.DEFAULT_ACADEMIC_YEAR,
        "default_semester": config.DEFAULT_SEMESTER,
        "academic_years": ["2022-23", "2023-24", "2024-25", "2025-26"],
        "semesters": ["Odd", "Even", "Summer"],
        "default_departments": config.DEFAULT_DEPARTMENTS,
        "default_attendance_distribution": {
            "Regular": int(config.DEFAULT_ATTENDANCE_DISTRIBUTION["Regular"] * 100),
            "Moderate": int(config.DEFAULT_ATTENDANCE_DISTRIBUTION["Moderate"] * 100),
            "Irregular": int(config.DEFAULT_ATTENDANCE_DISTRIBUTION["Irregular"] * 100),
            "Low": int(config.DEFAULT_ATTENDANCE_DISTRIBUTION["Low"] * 100),
        },
        "default_engagement_distribution": {
            "High": int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION["High"] * 100),
            "Medium": int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION["Medium"] * 100),
            "Low": int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION["Low"] * 100),
        },
    }
