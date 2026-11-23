"""
pages/4_Early_Warning.py — Early Warning Analysis for AttendSynth AI.

This page uses the rule-based risk engine (NOT a trained ML model).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
from src.risk_engine import (
    summarise_risk_distribution,
    get_high_risk_students,
    get_risk_insights,
    get_contributing_factors,
    RISK_CATEGORY_EXPLANATIONS,
)

st.set_page_config(page_title="Early Warning | AttendSynth AI", page_icon="⚠️", layout="wide")

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
    <h1>⚠️ Early Warning Analysis</h1>
    <p>Transparent rule-based risk classification — not a trained machine learning model.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

if df is None:
    st.warning("⚠️ No dataset found.  Please generate one on the **🔧 Generator** page first.")
    st.stop()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.info(
    "ℹ️ **Methodology Note:** Risk scores are computed using a **deterministic weighted formula** "
    "applied to each student's attendance, engagement, assignment completion, and academic performance. "
    "This is a transparent rule-based system — not a trained machine learning model."
)

# ── Risk distribution KPIs ────────────────────────────────────────────────────
dist = summarise_risk_distribution(df)
st.markdown("### 📊 Risk Distribution")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Students",  f"{dist['total']:,}")
k2.metric("🔴 High Risk",    f"{dist['high_risk_count']:,}  ({dist['percentages'].get('High',0):.1f}%)")
k3.metric("🟡 Medium Risk",  f"{dist['medium_risk_count']:,} ({dist['percentages'].get('Medium',0):.1f}%)")
k4.metric("🟢 Low Risk",     f"{dist['low_risk_count']:,}  ({dist['percentages'].get('Low',0):.1f}%)")

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    # Gauge-style bar chart for risk proportions
    categories = ["Low", "Medium", "High"]
    values     = [dist["percentages"].get(c, 0) for c in categories]
    colours    = [config.RISK_COLOURS[c] for c in categories]

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=colours,
        text=[f"{v:.1f}%" for v in values],
        textposition="auto",
    ))
    fig.update_layout(
        title="Risk Category Proportions",
        yaxis_title="% of Students",
        template=config.CHART_TEMPLATE,
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Risk score histogram
    fig2 = px.histogram(
        df, x="risk_score", nbins=30,
        color="risk_category",
        color_discrete_map=config.RISK_COLOURS,
        labels={"risk_score": "Risk Score (0-100)", "risk_category": "Category"},
        title="Risk Score Distribution",
        template=config.CHART_TEMPLATE,
    )
    fig2.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ── Risk Insights ─────────────────────────────────────────────────────────────
st.markdown("### 💡 Automated Risk Insights")
for insight in get_risk_insights(df):
    st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Category Explanations ─────────────────────────────────────────────────────
st.markdown("### 📖 Risk Category Definitions")
e1, e2, e3 = st.columns(3)

with e1:
    st.markdown(f"""
    <div class='card' style='border-left: 4px solid {config.RISK_COLOURS["Low"]};'>
        <b style='color:{config.RISK_COLOURS["Low"]};'>🟢 Low Risk</b><br>
        {RISK_CATEGORY_EXPLANATIONS["Low"]}
    </div>""", unsafe_allow_html=True)

with e2:
    st.markdown(f"""
    <div class='card' style='border-left: 4px solid {config.RISK_COLOURS["Medium"]};'>
        <b style='color:{config.RISK_COLOURS["Medium"]};'>🟡 Medium Risk</b><br>
        {RISK_CATEGORY_EXPLANATIONS["Medium"]}
    </div>""", unsafe_allow_html=True)

with e3:
    st.markdown(f"""
    <div class='card' style='border-left: 4px solid {config.RISK_COLOURS["High"]};'>
        <b style='color:{config.RISK_COLOURS["High"]};'>🔴 High Risk</b><br>
        {RISK_CATEGORY_EXPLANATIONS["High"]}
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── High-Risk Student Records ─────────────────────────────────────────────────
st.markdown("### 🔴 High-Risk Student Records")
high_risk_df = get_high_risk_students(df)

if high_risk_df.empty:
    st.success("🎉 No students classified as High-risk in this dataset!")
else:
    st.markdown(f"**{len(high_risk_df):,} students** require immediate attention:")

    display_cols = [
        "student_id", "department", "year_of_study",
        "attendance_percentage", "engagement_score",
        "assignment_completion_percentage", "academic_performance_score",
        "risk_score",
    ]
    st.dataframe(
        high_risk_df[display_cols].sort_values("risk_score", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

st.markdown("---")

# ── Individual student risk lookup ────────────────────────────────────────────
st.markdown("### 🔎 Individual Student Risk Lookup")
student_ids = df["student_id"].tolist()
selected_id = st.selectbox("Select a Student ID", options=["—"] + student_ids)

if selected_id != "—":
    row = df[df["student_id"] == selected_id].iloc[0]
    factors = get_contributing_factors(row)

    info_col, factor_col = st.columns([1, 2])
    with info_col:
        cat = row["risk_category"]
        colour = config.RISK_COLOURS.get(cat, "#aaa")
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {colour};'>
            <b>Student:</b> {row['student_id']}<br>
            <b>Department:</b> {row['department']}<br>
            <b>Year:</b> {row['year_of_study']}<br>
            <b>Attendance:</b> {row['attendance_percentage']}%<br>
            <b>Engagement:</b> {row['engagement_score']}/100<br>
            <b>Assignment Completion:</b> {row['assignment_completion_percentage']}%<br>
            <b>Academic Performance:</b> {row['academic_performance_score']}/100<br>
            <b>Risk Score:</b> {row['risk_score']}/100<br>
            <b>Risk Category:</b> <span style='color:{colour};font-weight:700;'>{cat}</span>
        </div>""", unsafe_allow_html=True)

    with factor_col:
        st.markdown("**Contributing Risk Factors:**")
        for f in factors:
            st.markdown(f"- {f}")

# ── Risk Formula Explanation ───────────────────────────────────────────────────
with st.expander("📐 Risk Score Formula"):
    st.markdown("""
    ```
    risk_score = 100 − (
        0.35 × attendance_percentage +
        0.25 × engagement_score +
        0.25 × assignment_completion_percentage +
        0.15 × academic_performance_score
    )
    ```

    | Range | Category |
    |---|---|
    | 0 – 34 | 🟢 Low |
    | 35 – 59 | 🟡 Medium |
    | 60 – 100 | 🔴 High |

    *All input variables are on a 0–100 scale, so the risk score is always within [0, 100].*
    """)
