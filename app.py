"""
app.py — AttendSynth AI main Streamlit application entry point (Overview / Home Dashboard).

This file serves dual purpose:
  1. Classic Streamlit dashboard (retained fully for Streamlit Cloud deployment).
  2. Portal hero banner that links users to the new full-stack FastAPI + HTML frontend
     deployed on Render (update RENDER_URL once Render deployment is live).
"""

from datetime import datetime
import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_kpi_card, render_empty_dataset_state
from src.analytics import (
    compute_kpis,
    chart_attendance_distribution,
    chart_engagement_distribution,
    chart_risk_distribution,
    chart_department_attendance,
)

# ---------------------------------------------------------------------------
# Page config — MUST be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=f"Overview | {config.APP_TITLE}",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_styles()
render_sidebar("Overview")

# ---------------------------------------------------------------------------
# NEW PLATFORM PORTAL BANNER
# ---------------------------------------------------------------------------
# Update this URL once your Render deployment is live and tested.
def _get_render_url() -> str:
    """Safely read RENDER_URL from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, "secrets") and "RENDER_URL" in st.secrets:
            return str(st.secrets["RENDER_URL"]).strip()
    except Exception:
        pass
    return os.environ.get("RENDER_URL", "").strip()


RENDER_URL = _get_render_url()
NEW_PLATFORM_AVAILABLE = bool(RENDER_URL)

if NEW_PLATFORM_AVAILABLE:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e3a5f 0%, #0f1e35 100%);
            border: 1px solid #3B82F6;
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        ">
            <div style="font-size: 2.5rem;">🚀</div>
            <div style="flex: 1;">
                <div style="color: #60A5FA; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">
                    AttendSynth AI — Full-Stack Platform Now Live!
                </div>
                <div style="color: #94A3B8; font-size: 0.9rem;">
                    The new platform features a modern HTML/CSS/JS frontend with Gemini AI Academic Insights, 
                    advanced analytics, and real-time risk assessment.
                </div>
            </div>
            <a href="{RENDER_URL}" target="_blank" style="
                background: #3B82F6;
                color: white;
                padding: 0.6rem 1.4rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.95rem;
                white-space: nowrap;
            ">Open New Platform →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info(
        "🚀 **Full-Stack Platform Coming Soon!** A new HTML/CSS/JS frontend with Gemini AI is under deployment. "
        "Set the `RENDER_URL` secret in Streamlit Cloud once the Render deployment is live.",
        icon="🔧",
    )

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    if hour < 17:
        return "Good Afternoon"
    return "Good Evening"


render_page_header(
    f"{_greeting()} — Welcome to AttendSynth AI",
    "Generate, explore and analyze realistic synthetic student engagement data.",
)

df: pd.DataFrame | None = st.session_state.get("df")

# ---------------------------------------------------------------------------
# 4 KPI Cards
# ---------------------------------------------------------------------------
if df is not None and not df.empty:
    kpi = compute_kpis(df)
    total_val   = f"{kpi['total_students']:,}"
    total_sub   = f"Across {kpi['departments']} department(s)"
    att_val     = f"{kpi['avg_attendance']}%"
    att_sub     = f"Avg assignment completion: {kpi['avg_assignment']}%"
    eng_val     = f"{kpi['avg_engagement']}/100"
    eng_sub     = f"Avg academic score: {kpi['avg_academic']}/100"
    risk_val    = f"{kpi['high_risk_count']:,}"
    risk_sub    = f"{kpi['high_risk_pct']}% of cohort requires attention"
else:
    total_val, total_sub = "—", "No cohort generated yet"
    att_val,   att_sub   = "—", "Waiting for dataset"
    eng_val,   eng_sub   = "—", "Waiting for dataset"
    risk_val,  risk_sub  = "—", "Waiting for dataset"

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card(
        "Total Students Generated",
        total_val,
        total_sub,
        icon="👥",
        accent_color="#3B82F6",
        icon_bg="rgba(59, 130, 246, 0.10)",
    )
with k2:
    render_kpi_card(
        "Average Attendance",
        att_val,
        att_sub,
        icon="📅",
        accent_color="#14B8A6",
        icon_bg="rgba(20, 184, 166, 0.10)",
    )
with k3:
    render_kpi_card(
        "Average Engagement",
        eng_val,
        eng_sub,
        icon="💡",
        accent_color="#60A5FA",
        icon_bg="rgba(96, 165, 250, 0.12)",
    )
with k4:
    render_kpi_card(
        "High Risk Students",
        risk_val,
        risk_sub,
        icon="⚠️",
        accent_color="#EF4444",
        icon_bg="rgba(239, 68, 68, 0.10)",
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Quick Actions
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)
qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    if st.button("Generate Dataset", type="primary", icon=":material/tune:", use_container_width=True):
        st.switch_page("pages/1_Generator.py")
with qa2:
    if st.button("Explore Dataset", icon=":material/table_view:", use_container_width=True):
        st.switch_page("pages/2_Dataset_Explorer.py")
with qa3:
    if st.button("View Analytics", icon=":material/bar_chart:", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")
with qa4:
    if st.button("Download Dataset", icon=":material/download:", use_container_width=True):
        st.switch_page("pages/7_Export_Center.py")

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Analytics Overview
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Analytics Overview</div>', unsafe_allow_html=True)

if df is not None and not df.empty:
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        with st.container(border=True):
            st.plotly_chart(chart_attendance_distribution(df), use_container_width=True)
    with row1_col2:
        with st.container(border=True):
            st.plotly_chart(chart_engagement_distribution(df), use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        with st.container(border=True):
            st.plotly_chart(chart_risk_distribution(df), use_container_width=True)
    with row2_col2:
        with st.container(border=True):
            st.plotly_chart(chart_department_attendance(df), use_container_width=True)

    # Recent Generation Details
    gen_meta = st.session_state.get("generation_meta", {})
    with st.container(border=True):
        st.markdown("**Active Cohort Summary**")
        m1, m2, m3, m4 = st.columns(4)
        m1.caption(f"Academic Year: **{gen_meta.get('academic_year', '—')}**")
        m2.caption(f"Semester: **{gen_meta.get('semester', '—')}**")
        m3.caption(f"Random Seed: **{gen_meta.get('seed', '—')}**")
        m4.caption(f"Low / Med / High Risk: **{kpi['low_risk_count']} / {kpi['medium_risk_count']} / {kpi['high_risk_count']}**")
else:
    render_empty_dataset_state()

st.markdown(
    f"<div style='text-align:center; color:#9CA3AF; font-size:0.8rem; margin-top:2rem;'>"
    f"AttendSynth AI v{config.APP_VERSION} &middot; 100% Synthetic Student Data Platform"
    f"</div>",
    unsafe_allow_html=True,
)
