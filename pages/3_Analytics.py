"""
pages/3_Analytics.py — Analytics Dashboard for AttendSynth AI.
"""

import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_empty_dataset_state
from src.analytics import (
    chart_attendance_distribution,
    chart_engagement_distribution,
    chart_academic_performance_distribution,
    chart_department_attendance,
    chart_risk_distribution,
    chart_attendance_vs_engagement,
    chart_assignment_completion,
    chart_engagement_behaviour_distribution,
    compute_kpis,
    generate_insights,
)

st.set_page_config(page_title=f"Analytics | {config.APP_TITLE}", page_icon="📊", layout="wide")
load_styles()
render_sidebar("Analytics")

render_page_header(
    "Analytics Dashboard",
    "Interactive distributions, departmental benchmarks, and correlation analysis.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

# ---------------------------------------------------------------------------
# Filter Bar
# ---------------------------------------------------------------------------
f_col1, f_col2 = st.columns([1, 3])
with f_col1:
    dept_opts = ["All Departments"] + sorted(df["department"].unique().tolist())
    dept_sel  = st.selectbox("Filter by Department", dept_opts)

df_view = df[df["department"] == dept_sel].copy() if dept_sel != "All Departments" else df.copy()

if df_view.empty:
    st.warning("No records available for the selected department.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI Summary
# ---------------------------------------------------------------------------
kpi = compute_kpis(df_view)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Students",        f"{kpi['total_students']:,}")
k2.metric("Avg Attendance",  f"{kpi['avg_attendance']}%")
k3.metric("Avg Engagement",  f"{kpi['avg_engagement']}/100")
k4.metric("Avg Academic",    f"{kpi['avg_academic']}/100")
k5.metric("High Risk",       f"{kpi['high_risk_count']:,} ({kpi['high_risk_pct']}%)")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Automated Insights
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Key Cohort Insights</div>', unsafe_allow_html=True)
insights = generate_insights(df_view)
ins_cols = st.columns(2)
for idx, insight in enumerate(insights):
    with ins_cols[idx % 2]:
        st.markdown(f"<div class='insight-item'>{insight}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Core Distributions
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Score Distributions</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.plotly_chart(chart_attendance_distribution(df_view), use_container_width=True)
with c2:
    with st.container(border=True):
        st.plotly_chart(chart_engagement_distribution(df_view), use_container_width=True)
with c3:
    with st.container(border=True):
        st.plotly_chart(chart_academic_performance_distribution(df_view), use_container_width=True)

# ---------------------------------------------------------------------------
# Department Comparison & Risk Distribution
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Department & Risk Breakdown</div>', unsafe_allow_html=True)
c4, c5 = st.columns([3, 2])
with c4:
    with st.container(border=True):
        st.plotly_chart(chart_department_attendance(df_view), use_container_width=True)
with c5:
    with st.container(border=True):
        st.plotly_chart(chart_risk_distribution(df_view), use_container_width=True)

# ---------------------------------------------------------------------------
# Correlation Scatter
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Attendance vs Engagement Correlation</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.plotly_chart(chart_attendance_vs_engagement(df_view), use_container_width=True)

# ---------------------------------------------------------------------------
# Assignment & Behavioral Patterns
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Assignment & Behavioral Patterns</div>', unsafe_allow_html=True)
c6, c7 = st.columns(2)
with c6:
    with st.container(border=True):
        st.plotly_chart(chart_assignment_completion(df_view), use_container_width=True)
with c7:
    with st.container(border=True):
        st.plotly_chart(chart_engagement_behaviour_distribution(df_view), use_container_width=True)
