"""
pages/3_Analytics.py — Analytics Dashboard for AttendSynth AI.
"""

import streamlit as st
import pandas as pd
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
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

st.set_page_config(page_title="Analytics | AttendSynth AI", page_icon="📊", layout="wide")

css_path = os.path.join(ROOT, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
        <span style='font-size:2rem;'>🎓</span>
        <h2 style='margin:0.3rem 0 0;font-size:1.1rem;color:#3a3a6e;font-weight:700;'>AttendSynth AI</h2>
    </div><hr style='margin:0.8rem 0;'>
    """, unsafe_allow_html=True)

st.markdown("""
<div class='page-header'>
    <h1>📊 Analytics Dashboard</h1>
    <p>Interactive visualisations and automatically generated insights from the synthetic dataset.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

if df is None:
    st.warning("⚠️ No dataset found.  Please generate one on the **🔧 Generator** page first.")
    st.stop()

# ── Optional department filter ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔎 Filter")
    dept_opts = ["All Departments"] + sorted(df["department"].unique().tolist())
    dept_sel  = st.selectbox("Department", dept_opts)

if dept_sel != "All Departments":
    df_view = df[df["department"] == dept_sel].copy()
else:
    df_view = df.copy()

if df_view.empty:
    st.warning("No data for the selected filter.")
    st.stop()

# ── KPI cards ─────────────────────────────────────────────────────────────────
kpi = compute_kpis(df_view)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("👥 Students",           f"{kpi['total_students']:,}")
k2.metric("📅 Avg Attendance",     f"{kpi['avg_attendance']}%")
k3.metric("💡 Avg Engagement",     f"{kpi['avg_engagement']}/100")
k4.metric("🎓 Avg Academic",       f"{kpi['avg_academic']}/100")
k5.metric("🔴 High-Risk",          f"{kpi['high_risk_count']:,} ({kpi['high_risk_pct']}%)",
          delta_color="inverse")

st.markdown("---")

# ── Auto-generated insights ────────────────────────────────────────────────────
st.markdown("### 💡 Automated Insights")
insights = generate_insights(df_view)
for insight in insights:
    st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Charts row 1 ──────────────────────────────────────────────────────────────
st.markdown("### 📈 Distributions")
c1, c2, c3 = st.columns(3)
with c1:
    st.plotly_chart(chart_attendance_distribution(df_view), use_container_width=True)
with c2:
    st.plotly_chart(chart_engagement_distribution(df_view), use_container_width=True)
with c3:
    st.plotly_chart(chart_academic_performance_distribution(df_view), use_container_width=True)

# ── Charts row 2 ──────────────────────────────────────────────────────────────
st.markdown("### 🏢 Department & Risk")
c4, c5 = st.columns([3, 2])
with c4:
    st.plotly_chart(chart_department_attendance(df_view), use_container_width=True)
with c5:
    st.plotly_chart(chart_risk_distribution(df_view), use_container_width=True)

# ── Scatter ───────────────────────────────────────────────────────────────────
st.markdown("### 🔵 Attendance vs Engagement")
st.plotly_chart(chart_attendance_vs_engagement(df_view), use_container_width=True)

# ── Charts row 3 ──────────────────────────────────────────────────────────────
st.markdown("### 📚 Assignment & Engagement Patterns")
c6, c7 = st.columns(2)
with c6:
    st.plotly_chart(chart_assignment_completion(df_view), use_container_width=True)
with c7:
    st.plotly_chart(chart_engagement_behaviour_distribution(df_view), use_container_width=True)
