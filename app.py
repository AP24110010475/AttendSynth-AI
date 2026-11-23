"""
app.py — AttendSynth AI main Streamlit application entry point.

This is the Home Dashboard page.  Other pages live in the /pages directory.
Streamlit automatically discovers them and adds them to the sidebar.
"""

import streamlit as st
import pandas as pd
import os
import sys

# Make src importable regardless of working directory
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import config

# ---------------------------------------------------------------------------
# Page config — MUST be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load custom CSS
# ---------------------------------------------------------------------------
css_path = os.path.join(ROOT, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar branding
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <span style='font-size:2.5rem;'>🎓</span>
        <h2 style='margin:0.3rem 0 0; font-size:1.2rem; color:#3a3a6e; font-weight:700;'>AttendSynth AI</h2>
        <p style='margin:0; font-size:0.78rem; color:#7a8aab;'>Synthetic Engagement Generator</p>
    </div>
    <hr style='margin:0.8rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Navigation")
    st.markdown("""
    Use the **pages** in the sidebar to explore:
    - **🔧 Generator** – Configure & generate data
    - **🔍 Explorer** – Browse student records
    - **📊 Analytics** – Charts & insights
    - **⚠️ Early Warning** – Risk analysis
    - **🤖 Machine Learning** – ML demo
    - **✅ Data Quality** – Validation report
    - **📥 Export Center** – Download data
    - **ℹ️ About** – Project info
    """)

    # Quick dataset status in sidebar
    df: pd.DataFrame | None = st.session_state.get("df")
    if df is not None:
        st.markdown("---")
        st.markdown("**📦 Active Dataset**")
        st.markdown(f"- Students: **{len(df):,}**")
        st.markdown(f"- Seed: **{st.session_state.get('generation_seed', '—')}**")
        st.markdown(f"- Year: **{st.session_state.get('generation_year', '—')}**")


# ---------------------------------------------------------------------------
# Home Dashboard
# ---------------------------------------------------------------------------
st.markdown("""
<div class='page-header'>
    <h1>🎓 AttendSynth AI</h1>
    <p>Synthetic Student Engagement Generator — Generate realistic datasets for prototyping early-warning systems.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

# ── Intro ──────────────────────────────────────────────────────────────────
st.markdown("## 👋 Welcome")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
**AttendSynth AI** generates **statistically plausible synthetic student records** for academic 
research and early-warning system prototyping — without exposing real student data.

**Key capabilities:**
- 📐 Correlated, realistic synthetic datasets (up to 10,000 students)
- 📊 Interactive analytics and visualisations
- ⚠️ Rule-based early-warning risk classification
- 🤖 Machine learning demonstration (Random Forest)
- ✅ Automated data quality validation
- 📥 CSV and JSON exports

> *All data is entirely synthetic.  No real student information is used or generated.*
    """)

with col2:
    st.markdown("""
    <div class='card' style='text-align:center;'>
        <span style='font-size:3rem;'>🧪</span>
        <h3 style='color:#4F8EF7; margin:0.5rem 0 0;'>100% Synthetic</h3>
        <p style='color:#7a8aab; margin:0;'>No real student data</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── KPI Metrics ────────────────────────────────────────────────────────────
st.markdown("## 📈 Dataset Metrics")

if df is not None:
    from src.analytics import compute_kpis
    kpi = compute_kpis(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Students",     f"{kpi['total_students']:,}")
    c2.metric("📅 Avg Attendance",     f"{kpi['avg_attendance']}%")
    c3.metric("💡 Avg Engagement",     f"{kpi['avg_engagement']}/100")
    c4.metric("🎓 Avg Academic Score", f"{kpi['avg_academic']}/100")
    c5.metric("🔴 High-Risk Students", f"{kpi['high_risk_count']:,}",
              delta=f"{kpi['high_risk_pct']}% of cohort",
              delta_color="inverse")

    st.markdown("---")

    # ── Recent Generation Details ───────────────────────────────────────────
    st.markdown("## 📋 Last Generated Dataset")
    gen_meta = st.session_state.get("generation_meta", {})
    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(f"""
    <div class='card'>
        <b>🗂 Configuration</b><br>
        Students: <b>{kpi['total_students']:,}</b><br>
        Departments: <b>{kpi['departments']}</b><br>
        Academic Year: <b>{gen_meta.get('academic_year', '—')}</b><br>
        Semester: <b>{gen_meta.get('semester', '—')}</b>
    </div>""", unsafe_allow_html=True)

    col_b.markdown(f"""
    <div class='card'>
        <b>⚠️ Risk Summary</b><br>
        🔴 High Risk: <b>{kpi['high_risk_count']:,}</b> ({kpi['high_risk_pct']}%)<br>
        🟡 Medium Risk: <b>{kpi['medium_risk_count']:,}</b><br>
        🟢 Low Risk: <b>{kpi['low_risk_count']:,}</b>
    </div>""", unsafe_allow_html=True)

    col_c.markdown(f"""
    <div class='card'>
        <b>📊 Score Averages</b><br>
        Attendance: <b>{kpi['avg_attendance']}%</b><br>
        Engagement: <b>{kpi['avg_engagement']}/100</b><br>
        Assignment: <b>{kpi['avg_assignment']}%</b>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # Quick preview
    st.markdown("## 🔍 Quick Preview (first 5 rows)")
    st.dataframe(df.head(5), use_container_width=True)

else:
    # No dataset yet — show placeholder metrics
    st.info("🚀 No dataset generated yet.  Go to **🔧 Generator** in the sidebar to create your first dataset.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Students",     "—")
    c2.metric("📅 Avg Attendance",     "—")
    c3.metric("💡 Avg Engagement",     "—")
    c4.metric("🎓 Avg Academic Score", "—")
    c5.metric("🔴 High-Risk Students", "—")

    st.markdown("---")

st.markdown("## 🎯 Project Objectives")
obj_cols = st.columns(3)

with obj_cols[0]:
    st.markdown("""
    <div class='card'>
        <b>🧪 Synthetic Data Generation</b><br>
        Generate realistic, correlated student profiles using statistical behavioural models without real data.
    </div>""", unsafe_allow_html=True)

with obj_cols[1]:
    st.markdown("""
    <div class='card'>
        <b>⚠️ Early-Warning Systems</b><br>
        Prototype risk-classification models using entirely synthetic datasets for safe development.
    </div>""", unsafe_allow_html=True)

with obj_cols[2]:
    st.markdown("""
    <div class='card'>
        <b>📚 Research & Education</b><br>
        Enable academic research on student engagement patterns without ethical or privacy constraints.
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#9aabbf; font-size:0.85rem;'>"
    f"AttendSynth AI v{config.APP_VERSION} &nbsp;|&nbsp; All data is 100% synthetic"
    "</div>",
    unsafe_allow_html=True,
)
