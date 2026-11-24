"""
pages/2_Dataset_Explorer.py — Interactive Dataset Explorer for AttendSynth AI.
"""

import math
import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_empty_dataset_state

st.set_page_config(page_title=f"Dataset Explorer | {config.APP_TITLE}", page_icon="🔎", layout="wide")
load_styles()
render_sidebar("Dataset Explorer")

render_page_header(
    "Dataset Explorer",
    "Search, filter, sort, and paginate through synthetic student records.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

# ---------------------------------------------------------------------------
# Filter Controls Card
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("**Filter Records**")
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

# Apply filters
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

# Persist filtered dataset for Export Center
st.session_state["filtered_df"] = filtered

# ---------------------------------------------------------------------------
# Record Count Summary
# ---------------------------------------------------------------------------
rc1, rc2, rc3 = st.columns(3)
rc1.metric("Matching Records", f"{len(filtered):,}")
rc2.metric("Total Cohort",     f"{len(df):,}")
rc3.metric("Filtered Out",     f"{len(df) - len(filtered):,}")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Table & Pagination
# ---------------------------------------------------------------------------
all_cols = df.columns.tolist()
default_cols = [
    "student_id", "age", "department", "year_of_study", "semester",
    "attendance_percentage", "engagement_score",
    "academic_performance_score", "risk_score", "risk_category",
]

with st.container(border=True):
    ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 1])
    with ctrl1:
        selected_cols = st.multiselect(
            "Visible Columns",
            options=all_cols,
            default=default_cols,
        )
        if not selected_cols:
            selected_cols = default_cols

    with ctrl2:
        page_size = st.selectbox("Rows per page", [15, 25, 50, 100], index=1)

    total_rows = len(filtered)
    total_pages = max(1, math.ceil(total_rows / page_size))

    with ctrl3:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    if filtered.empty:
        st.info("No student records match the current filters.")
    else:
        start_idx = (page_num - 1) * page_size
        end_idx   = min(start_idx + page_size, total_rows)
        st.caption(f"Showing records **{start_idx + 1:,}–{end_idx:,}** of **{total_rows:,}** (Page {page_num} of {total_pages})")

        st.dataframe(
            filtered[selected_cols].iloc[start_idx:end_idx].reset_index(drop=True),
            use_container_width=True,
            height=480,
        )

if not filtered.empty:
    with st.expander("Filtered Cohort Descriptive Statistics"):
        st.dataframe(
            filtered[[
                "attendance_percentage", "engagement_score",
                "assignment_completion_percentage", "academic_performance_score",
                "risk_score",
            ]].describe().round(2),
            use_container_width=True,
        )
