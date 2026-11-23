"""
pages/2_Dataset_Explorer.py — Interactive dataset explorer for AttendSynth AI.
"""

import streamlit as st
import pandas as pd
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config

st.set_page_config(page_title="Explorer | AttendSynth AI", page_icon="🔍", layout="wide")

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
    <h1>🔍 Dataset Explorer</h1>
    <p>Search, filter and sort synthetic student records.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

if df is None:
    st.warning("⚠️ No dataset found.  Please generate one on the **🔧 Generator** page first.")
    st.stop()

# ── Filters ──────────────────────────────────────────────────────────────────
st.markdown("### 🔎 Filters")
fc1, fc2, fc3, fc4, fc5 = st.columns(5)

with fc1:
    search_id = st.text_input("Search Student ID", placeholder="e.g. STU-12345")

with fc2:
    all_depts = ["All"] + sorted(df["department"].unique().tolist())
    dept_filter = st.selectbox("Department", all_depts)

with fc3:
    all_years = ["All"] + sorted(df["year_of_study"].unique().tolist())
    year_filter = st.selectbox("Year of Study", all_years)

with fc4:
    all_semesters = ["All"] + sorted(df["semester"].unique().tolist())
    sem_filter = st.selectbox("Semester", all_semesters)

with fc5:
    all_risk = ["All"] + config.RISK_CATEGORIES
    risk_filter = st.selectbox("Risk Category", all_risk)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()

if search_id.strip():
    filtered = filtered[filtered["student_id"].str.contains(search_id.strip(), case=False)]

if dept_filter != "All":
    filtered = filtered[filtered["department"] == dept_filter]

if year_filter != "All":
    filtered = filtered[filtered["year_of_study"] == year_filter]

if sem_filter != "All":
    filtered = filtered[filtered["semester"] == sem_filter]

if risk_filter != "All":
    filtered = filtered[filtered["risk_category"] == risk_filter]

# Persist filtered dataset for export
st.session_state["filtered_df"] = filtered

st.markdown("---")

# ── Record count ──────────────────────────────────────────────────────────────
rc1, rc2, rc3 = st.columns(3)
rc1.metric("Showing Records",   f"{len(filtered):,}")
rc2.metric("Total in Dataset",  f"{len(df):,}")
rc3.metric("Filtered Out",      f"{len(df) - len(filtered):,}")

st.markdown("### 📋 Student Records")

# Column selector
all_cols = df.columns.tolist()
default_cols = [
    "student_id", "age", "department", "year_of_study", "semester",
    "attendance_percentage", "engagement_score",
    "academic_performance_score", "risk_score", "risk_category",
]
selected_cols = st.multiselect(
    "Columns to display",
    options=all_cols,
    default=default_cols,
)

if not selected_cols:
    selected_cols = default_cols

if filtered.empty:
    st.info("No records match the selected filters.")
else:
    st.dataframe(
        filtered[selected_cols].reset_index(drop=True),
        use_container_width=True,
        height=520,
    )

    # Quick per-filter stats
    with st.expander("📊 Filtered Dataset Statistics"):
        st.dataframe(
            filtered[[
                "attendance_percentage", "engagement_score",
                "assignment_completion_percentage", "academic_performance_score",
                "risk_score",
            ]].describe().round(2),
            use_container_width=True,
        )
