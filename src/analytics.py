"""
analytics.py — Chart and insight generation helpers for AttendSynth AI.

All charts use Plotly and are styled with the app colour palette.
All insight strings are derived from actual data — no hardcoded values.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

T  = config.CHART_TEMPLATE
RC = config.RISK_COLOURS
CP = config.COLOUR_PRIMARY
CS = config.COLOUR_SECONDARY
CT = config.COLOUR_TEAL


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _apply_layout(fig: go.Figure, title: str = "", height: int = 360) -> go.Figure:
    fig.update_layout(
        template=T,
        title=dict(text=title, font=dict(size=15, color="#111827", family="Inter, sans-serif"), x=0.01),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=48, b=16),
        font=dict(family="Inter, sans-serif", size=12, color="#6B7280"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        xaxis=dict(showgrid=False, linecolor="#E5E7EB", zeroline=False),
        yaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zeroline=False),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart functions
# ---------------------------------------------------------------------------

def chart_attendance_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of attendance percentages."""
    fig = px.histogram(
        df, x="attendance_percentage",
        nbins=30,
        color_discrete_sequence=[CP],
        labels={"attendance_percentage": "Attendance (%)"},
        title="Attendance Distribution",
    )
    fig.add_vline(x=df["attendance_percentage"].mean(),
                  line_dash="dash", line_color=CS,
                  annotation_text=f"Mean: {df['attendance_percentage'].mean():.1f}%",
                  annotation_position="top right")
    return _apply_layout(fig)


def chart_engagement_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of engagement scores."""
    fig = px.histogram(
        df, x="engagement_score",
        nbins=30,
        color_discrete_sequence=[CT],
        labels={"engagement_score": "Engagement Score"},
        title="Engagement Score Distribution",
    )
    fig.add_vline(x=df["engagement_score"].mean(),
                  line_dash="dash", line_color=CP,
                  annotation_text=f"Mean: {df['engagement_score'].mean():.1f}",
                  annotation_position="top right")
    return _apply_layout(fig)


def chart_academic_performance_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of academic performance scores."""
    fig = px.histogram(
        df, x="academic_performance_score",
        nbins=30,
        color_discrete_sequence=[CS],
        labels={"academic_performance_score": "Academic Performance"},
        title="Academic Performance Distribution",
    )
    return _apply_layout(fig)


def chart_department_attendance(df: pd.DataFrame) -> go.Figure:
    """Bar chart: mean attendance by department."""
    dept_avg = (
        df.groupby("department")["attendance_percentage"]
        .mean()
        .reset_index()
        .sort_values("attendance_percentage", ascending=True)
    )
    fig = px.bar(
        dept_avg,
        x="attendance_percentage",
        y="department",
        orientation="h",
        color_discrete_sequence=[CP],
        labels={"attendance_percentage": "Avg Attendance (%)", "department": "Department"},
        title="Department-wise Average Attendance",
    )
    fig.update_layout(xaxis_range=[0, 100])
    return _apply_layout(fig, height=360)


def chart_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart: risk category distribution."""
    counts = df["risk_category"].value_counts().reset_index()
    counts.columns = ["risk_category", "count"]
    # Ensure consistent order
    order = ["Low", "Medium", "High"]
    counts["risk_category"] = pd.Categorical(counts["risk_category"], categories=order, ordered=True)
    counts = counts.sort_values("risk_category")

    fig = go.Figure(go.Pie(
        labels=counts["risk_category"],
        values=counts["count"],
        hole=0.62,
        marker=dict(colors=[RC.get(c, "#9CA3AF") for c in counts["risk_category"]],
                    line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
    ))
    fig.update_layout(
        template=T,
        title=dict(text="Risk Category Distribution", font=dict(size=15, color="#111827", family="Inter, sans-serif"), x=0.01),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=48, b=24),
        font=dict(family="Inter, sans-serif", size=12, color="#6B7280"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.08, xanchor="center", x=0.5),
    )
    return fig


def chart_attendance_vs_engagement(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: attendance vs engagement coloured by risk category."""
    fig = px.scatter(
        df,
        x="attendance_percentage",
        y="engagement_score",
        color="risk_category",
        color_discrete_map=RC,
        opacity=0.6,
        size_max=8,
        labels={
            "attendance_percentage": "Attendance (%)",
            "engagement_score": "Engagement Score",
        },
        title="Attendance vs Engagement (by Risk Category)",
        hover_data=["student_id", "department", "academic_performance_score"],
    )
    return _apply_layout(fig, height=430)


def chart_assignment_completion(df: pd.DataFrame) -> go.Figure:
    """Box plot: assignment completion by attendance pattern."""
    order = ["Regular", "Moderate", "Irregular", "Low"]
    fig = px.box(
        df,
        x="attendance_pattern",
        y="assignment_completion_percentage",
        color="attendance_pattern",
        category_orders={"attendance_pattern": order},
        color_discrete_sequence=[config.COLOUR_SUCCESS, config.COLOUR_PRIMARY,
                                  config.COLOUR_WARNING, config.COLOUR_DANGER],
        labels={
            "assignment_completion_percentage": "Assignment Completion (%)",
            "attendance_pattern": "Attendance Pattern",
        },
        title="Assignment Completion by Attendance Pattern",
    )
    fig.update_traces(showlegend=False)
    return _apply_layout(fig)


def chart_engagement_behaviour_distribution(df: pd.DataFrame) -> go.Figure:
    """Stacked bar: engagement score bands by department."""
    df2 = df.copy()
    df2["eng_band"] = pd.cut(
        df2["engagement_score"],
        bins=[0, 40, 70, 100],
        labels=["Low (0-40)", "Medium (40-70)", "High (70-100)"],
    )
    grouped = df2.groupby(["department", "eng_band"], observed=True).size().reset_index(name="count")
    fig = px.bar(
        grouped,
        x="department",
        y="count",
        color="eng_band",
        color_discrete_map={
            "Low (0-40)":    config.COLOUR_DANGER,
            "Medium (40-70)":config.COLOUR_WARNING,
            "High (70-100)": config.COLOUR_SUCCESS,
        },
        barmode="stack",
        labels={"count": "Student Count", "eng_band": "Engagement Band"},
        title="Engagement Level Distribution by Department",
    )
    return _apply_layout(fig, height=420)


# ---------------------------------------------------------------------------
# KPI / Insight helpers
# ---------------------------------------------------------------------------

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of KPI values computed from actual data."""
    total = len(df)
    high_risk = int((df["risk_category"] == "High").sum())
    med_risk  = int((df["risk_category"] == "Medium").sum())
    low_risk  = int((df["risk_category"] == "Low").sum())
    return {
        "total_students":       total,
        "avg_attendance":       round(df["attendance_percentage"].mean(), 1),
        "avg_engagement":       round(df["engagement_score"].mean(), 1),
        "avg_academic":         round(df["academic_performance_score"].mean(), 1),
        "avg_assignment":       round(df["assignment_completion_percentage"].mean(), 1),
        "high_risk_count":      high_risk,
        "medium_risk_count":    med_risk,
        "low_risk_count":       low_risk,
        "high_risk_pct":        round(high_risk / total * 100, 1) if total else 0,
        "departments":          df["department"].nunique(),
    }


def generate_insights(df: pd.DataFrame) -> List[str]:
    """Return a list of automatically derived insight strings."""
    kpi = compute_kpis(df)
    insights = []

    att = kpi["avg_attendance"]
    if att >= 85:
        insights.append(f"✅ Excellent average attendance of **{att}%** across the cohort.")
    elif att >= 70:
        insights.append(f"📊 Moderate average attendance of **{att}%** — room for improvement.")
    else:
        insights.append(f"⚠️ Low average attendance of **{att}%** — requires attention.")

    if kpi["high_risk_pct"] >= 20:
        insights.append(
            f"🔴 **{kpi['high_risk_pct']}%** of students are High-risk — "
            f"structured intervention is recommended."
        )
    else:
        insights.append(
            f"🟢 High-risk proportion is **{kpi['high_risk_pct']}%** — relatively contained."
        )

    corr = df["attendance_percentage"].corr(df["engagement_score"])
    insights.append(
        f"📈 Pearson correlation between attendance and engagement: **{corr:.2f}** "
        f"({'strong' if abs(corr) > 0.6 else 'moderate' if abs(corr) > 0.4 else 'weak'} positive relationship)."
    )

    top_dept = df.groupby("department")["attendance_percentage"].mean().idxmax()
    insights.append(
        f"🏆 Highest average attendance department: **{top_dept}**."
    )

    return insights
