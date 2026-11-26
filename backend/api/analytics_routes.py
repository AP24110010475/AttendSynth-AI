"""
backend/api/analytics_routes.py — API endpoints for Dataset Explorer and Analytics Dashboard.
"""

from __future__ import annotations
import math
import os
import sys
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from fastapi import APIRouter, Query, HTTPException

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from src.analytics import compute_kpis, generate_insights
from backend.services import cohort_service

router = APIRouter(prefix="/api", tags=["Analytics & Explorer"])


def _compute_histogram(series: pd.Series, bins: int = 15, range_min: float = 0, range_max: float = 100) -> Dict[str, Any]:
    """Calculate bucket counts and labels for Chart.js bar/histogram charts."""
    counts, bin_edges = np.histogram(series.dropna(), bins=bins, range=(range_min, range_max))
    labels = [f"{int(bin_edges[i])}–{int(bin_edges[i+1])}" for i in range(len(counts))]
    return {
        "labels": labels,
        "counts": counts.tolist(),
        "mean": round(float(series.mean()), 2) if not series.empty else 0.0,
    }


@router.get("/dataset")
def get_dataset(
    search_id: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    year_of_study: Optional[str] = Query(default=None),
    semester: Optional[str] = Query(default=None),
    risk_category: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=500),
    columns: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Retrieve filtered, paginated student records and descriptive stats."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        return {
            "has_cohort": False,
            "total_cohort": 0,
            "filtered_records": 0,
            "page": 1,
            "page_size": page_size,
            "total_pages": 0,
            "columns": [],
            "available_columns": [],
            "records": [],
            "descriptive_stats": {},
            "filter_options": {},
        }

    total_cohort = len(df)
    filtered = cohort_service.filter_cohort(
        search_id=search_id,
        department=department,
        year_of_study=year_of_study,
        semester=semester,
        risk_category=risk_category,
    )

    filtered_count = len(filtered)
    total_pages = max(1, math.ceil(filtered_count / page_size))
    current_page = min(page, total_pages)

    all_cols = df.columns.tolist()
    default_cols = [
        "student_id", "age", "department", "year_of_study", "semester",
        "attendance_percentage", "engagement_score",
        "academic_performance_score", "risk_score", "risk_category",
    ]
    if columns:
        requested = [c.strip() for c in columns.split(",") if c.strip() in all_cols]
        chosen_cols = requested if requested else default_cols
    else:
        chosen_cols = default_cols

    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    records = filtered[chosen_cols].iloc[start_idx:end_idx].to_dict(orient="records")

    numeric_cols = [
        "attendance_percentage", "engagement_score",
        "assignment_completion_percentage", "academic_performance_score",
        "risk_score",
    ]
    stats_dict = {}
    if not filtered.empty:
        desc = filtered[numeric_cols].describe().round(2).to_dict()
        stats_dict = desc

    return {
        "has_cohort": True,
        "total_cohort": total_cohort,
        "filtered_records": filtered_count,
        "filtered_out": total_cohort - filtered_count,
        "page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "columns": chosen_cols,
        "available_columns": all_cols,
        "records": records,
        "descriptive_stats": stats_dict,
        "filter_options": {
            "departments": sorted(df["department"].unique().tolist()),
            "years_of_study": sorted(df["year_of_study"].unique().tolist()),
            "semesters": sorted(df["semester"].unique().tolist()),
            "risk_categories": config.RISK_CATEGORIES,
        },
    }


@router.get("/analytics")
def get_analytics(department: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Calculate KPIs, automated insights, and chart-ready distributions."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        return {
            "has_cohort": False,
            "kpis": {},
            "insights": [],
            "charts": {},
        }

    df_view = df.copy()
    if department and department != "All Departments" and department != "All":
        df_view = df_view[df_view["department"] == department]
        if df_view.empty:
            raise HTTPException(status_code=404, detail=f"No records found for department '{department}'.")

    kpis = compute_kpis(df_view)
    insights = generate_insights(df_view)

    # 1. Attendance histogram
    att_hist = _compute_histogram(df_view["attendance_percentage"], bins=10)
    # 2. Engagement histogram
    eng_hist = _compute_histogram(df_view["engagement_score"], bins=10)
    # 3. Academic performance histogram
    acad_hist = _compute_histogram(df_view["academic_performance_score"], bins=10)

    # 4. Department average attendance (for the full cohort or view)
    dept_avg = (
        df.groupby("department")["attendance_percentage"]
        .mean()
        .round(2)
        .reset_index()
        .sort_values("attendance_percentage", ascending=False)
    )
    dept_chart = {
        "departments": dept_avg["department"].tolist(),
        "averages": dept_avg["attendance_percentage"].tolist(),
    }

    # 5. Risk distribution donut chart
    risk_counts = df_view["risk_category"].value_counts().to_dict()
    risk_chart = {
        "labels": ["Low", "Medium", "High"],
        "counts": [risk_counts.get("Low", 0), risk_counts.get("Medium", 0), risk_counts.get("High", 0)],
        "colors": [config.RISK_COLOURS["Low"], config.RISK_COLOURS["Medium"], config.RISK_COLOURS["High"]],
    }

    # 6. Scatter sample for Attendance vs Engagement
    sample_df = df_view.sample(n=min(len(df_view), 250), random_state=42) if len(df_view) > 250 else df_view
    scatter_points = []
    for _, row in sample_df.iterrows():
        scatter_points.append({
            "x": round(float(row["attendance_percentage"]), 1),
            "y": round(float(row["engagement_score"]), 1),
            "student_id": row["student_id"],
            "department": row["department"],
            "risk_category": row["risk_category"],
            "color": config.RISK_COLOURS.get(row["risk_category"], "#3B82F6"),
        })

    # 7. Assignment completion by attendance pattern
    pattern_order = ["Regular", "Moderate", "Irregular", "Low"]
    pattern_stats = []
    for pat in pattern_order:
        sub = df_view[df_view["attendance_pattern"] == pat]["assignment_completion_percentage"]
        pattern_stats.append({
            "pattern": pat,
            "avg": round(float(sub.mean()), 1) if not sub.empty else 0.0,
            "count": len(sub),
        })

    # 8. Engagement level distribution by department
    df_bands = df.copy()
    df_bands["eng_band"] = pd.cut(
        df_bands["engagement_score"],
        bins=[0, 40, 70, 100],
        labels=["Low (0-40)", "Medium (40-70)", "High (70-100)"],
    )
    dept_band_grouped = (
        df_bands.groupby(["department", "eng_band"], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    all_depts = dept_band_grouped.index.tolist()
    engagement_bands = {
        "departments": all_depts,
        "low": dept_band_grouped["Low (0-40)"].tolist() if "Low (0-40)" in dept_band_grouped else [0]*len(all_depts),
        "medium": dept_band_grouped["Medium (40-70)"].tolist() if "Medium (40-70)" in dept_band_grouped else [0]*len(all_depts),
        "high": dept_band_grouped["High (70-100)"].tolist() if "High (70-100)" in dept_band_grouped else [0]*len(all_depts),
    }

    return {
        "has_cohort": True,
        "selected_department": department or "All Departments",
        "available_departments": ["All Departments"] + sorted(df["department"].unique().tolist()),
        "kpis": kpis,
        "insights": insights,
        "charts": {
            "attendance_histogram": att_hist,
            "engagement_histogram": eng_hist,
            "academic_histogram": acad_hist,
            "department_attendance": dept_chart,
            "risk_distribution": risk_chart,
            "attendance_vs_engagement": scatter_points,
            "assignment_patterns": pattern_stats,
            "engagement_bands": engagement_bands,
        },
    }
