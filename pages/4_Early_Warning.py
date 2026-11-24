"""
pages/4_Early_Warning.py — Early Warning Analysis for AttendSynth AI.

Uses a transparent rule-based risk engine (NOT a trained ML model).
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_kpi_card, render_empty_dataset_state
from src.risk_engine import (
    summarise_risk_distribution,
    get_high_risk_students,
    get_contributing_factors,
    RISK_CATEGORY_EXPLANATIONS,
)

st.set_page_config(page_title=f"Early Warning | {config.APP_TITLE}", page_icon="⚠️", layout="wide")
load_styles()
render_sidebar("Early Warning")

render_page_header(
    "Early Warning Analysis",
    "Transparent rule-based student risk classification and factor breakdown.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

st.info(
    "Methodology Note: Risk scores are calculated using a deterministic weighted formula "
    "across attendance, engagement, assignment completion, and academic performance — not a trained ML model."
)

# ---------------------------------------------------------------------------
# Risk Summary Cards
# ---------------------------------------------------------------------------
dist = summarise_risk_distribution(df)
total = dist["total"]

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card(
        "Total Evaluated",
        f"{total:,}",
        "100% of active cohort",
        icon="👥",
        accent_color="#3B82F6",
        icon_bg="rgba(59, 130, 246, 0.10)",
    )
with k2:
    render_kpi_card(
        "Low Risk",
        f"{dist['low_risk_count']:,}",
        f"{dist['percentages'].get('Low', 0):.1f}% of cohort (Score < 35)",
        icon="✓",
        accent_color="#10B981",
        icon_bg="rgba(16, 185, 129, 0.12)",
    )
with k3:
    render_kpi_card(
        "Medium Risk",
        f"{dist['medium_risk_count']:,}",
        f"{dist['percentages'].get('Medium', 0):.1f}% of cohort (Score 35–59)",
        icon="!",
        accent_color="#F59E0B",
        icon_bg="rgba(245, 158, 11, 0.12)",
    )
with k4:
    render_kpi_card(
        "High Risk",
        f"{dist['high_risk_count']:,}",
        f"{dist['percentages'].get('High', 0):.1f}% of cohort (Score ≥ 60)",
        icon="⚠",
        accent_color="#EF4444",
        icon_bg="rgba(239, 68, 68, 0.12)",
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Risk Distribution Charts
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        categories = ["Low", "Medium", "High"]
        values     = [dist["percentages"].get(c, 0) for c in categories]
        colours    = [config.RISK_COLOURS[c] for c in categories]

        fig = go.Figure(go.Bar(
            x=categories,
            y=values,
            marker_color=colours,
            text=[f"{v:.1f}%" for v in values],
            textposition="auto",
        ))
        fig.update_layout(
            title=dict(text="Risk Category Proportions", font=dict(size=15, color="#111827"), x=0.01),
            yaxis_title="% of Students",
            template=config.CHART_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=330,
            margin=dict(l=16, r=16, t=48, b=16),
            yaxis=dict(gridcolor="#F3F4F6", zeroline=False),
        )
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with st.container(border=True):
        fig2 = px.histogram(
            df,
            x="risk_score",
            nbins=30,
            color="risk_category",
            color_discrete_map=config.RISK_COLOURS,
            category_orders={"risk_category": ["Low", "Medium", "High"]},
            labels={"risk_score": "Risk Score (0–100)", "risk_category": "Category"},
            title="Risk Score Distribution",
            template=config.CHART_TEMPLATE,
        )
        fig2.update_layout(
            title=dict(font=dict(size=15, color="#111827"), x=0.01),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=330,
            margin=dict(l=16, r=16, t=48, b=16),
            yaxis=dict(gridcolor="#F3F4F6", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Risk Factor Explanations
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Risk Category Definitions</div>', unsafe_allow_html=True)
e1, e2, e3 = st.columns(3)
for col, cat, label in [
    (e1, "Low", "Low Risk"),
    (e2, "Medium", "Medium Risk"),
    (e3, "High", "High Risk"),
]:
    colour = config.RISK_COLOURS[cat]
    with col:
        st.markdown(
            f"""
            <div class="saas-card" style="border-left: 4px solid {colour}; height: 100%;">
                <div style="font-weight: 600; color: {colour}; margin-bottom: 0.4rem;">{label}</div>
                <div style="font-size: 0.88rem; color: #4B5563; line-height: 1.5;">
                    {RISK_CATEGORY_EXPLANATIONS[cat]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# High-Risk Student Table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">High-Risk Student Records</div>', unsafe_allow_html=True)
high_risk_df = get_high_risk_students(df)

with st.container(border=True):
    if high_risk_df.empty:
        st.success("No students are classified as High-risk in this cohort.")
    else:
        st.caption(f"**{len(high_risk_df):,} students** flagged for immediate academic support (sorted by highest risk score).")
        display_cols = [
            "student_id", "department", "year_of_study",
            "attendance_percentage", "engagement_score",
            "assignment_completion_percentage", "academic_performance_score",
            "risk_score",
        ]
        st.dataframe(
            high_risk_df[display_cols].sort_values("risk_score", ascending=False).reset_index(drop=True),
            use_container_width=True,
            height=380,
        )

# ---------------------------------------------------------------------------
# Individual Student Risk Lookup
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Individual Student Factor Lookup</div>', unsafe_allow_html=True)
with st.container(border=True):
    student_ids = df["student_id"].tolist()
    selected_id = st.selectbox("Select a Student ID to inspect", options=["—"] + student_ids)

    if selected_id != "—":
        row = df[df["student_id"] == selected_id].iloc[0]
        factors = get_contributing_factors(row)
        cat = row["risk_category"]
        colour = config.RISK_COLOURS.get(cat, "#6B7280")

        info_col, factor_col = st.columns([1, 2])
        with info_col:
            st.markdown(
                f"""
                <div class="saas-card" style="border-left: 4px solid {colour}; margin-bottom: 0;">
                    <div style="font-size: 1rem; font-weight: 700; color: #111827;">{row['student_id']}</div>
                    <div style="font-size: 0.84rem; color: #6B7280; margin-bottom: 0.75rem;">
                        {row['department']} &middot; {row['year_of_study']}
                    </div>
                    <div style="font-size: 0.88rem; line-height: 1.7; color: #374151;">
                        Attendance: <b>{row['attendance_percentage']}%</b><br>
                        Engagement: <b>{row['engagement_score']}/100</b><br>
                        Assignments: <b>{row['assignment_completion_percentage']}%</b><br>
                        Academic Score: <b>{row['academic_performance_score']}/100</b><br>
                        Risk Score: <b>{row['risk_score']}/100</b>
                    </div>
                    <div style="margin-top: 0.6rem; font-weight: 600; color: {colour};">
                        Category: {cat} Risk
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with factor_col:
            st.markdown("**Contributing Risk Factors**")
            for f in factors:
                st.markdown(f"<div class='insight-item'>{f}</div>", unsafe_allow_html=True)

with st.expander("Risk Scoring Formula Reference"):
    st.markdown(
        """
        ```
        risk_score = 100 − (
            0.35 × attendance_percentage +
            0.25 × engagement_score +
            0.25 × assignment_completion_percentage +
            0.15 × academic_performance_score
        )
        ```
        - **Low Risk:** `0 – 34`
        - **Medium Risk:** `35 – 59`
        - **High Risk:** `60 – 100`
        """
    )
