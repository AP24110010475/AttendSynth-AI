"""
pages/1_Generator.py — Synthetic Data Generator page for AttendSynth AI.
"""

import os
import sys
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.generator import generate_dataset
from src.validation import validate_dataset
from src.ui import load_styles, render_sidebar, render_page_header

st.set_page_config(page_title=f"Data Generator | {config.APP_TITLE}", page_icon="🎛️", layout="wide")
load_styles()
render_sidebar("Data Generator")

render_page_header(
    "Synthetic Data Generator",
    "Configure and generate realistic synthetic student datasets.",
)

# ---------------------------------------------------------------------------
# Form-based Interface organized into visual cards
# ---------------------------------------------------------------------------
with st.form("generator_form"):
    col_left, col_right = st.columns(2)

    # A. Dataset Configuration
    with col_left:
        with st.container(border=True):
            st.markdown("#### A. Dataset Configuration")
            st.caption("Define cohort size, academic term, and participating departments.")

            n_students = st.number_input(
                "Number of Students",
                min_value=50,
                max_value=10_000,
                value=config.DEFAULT_N_STUDENTS,
                step=50,
                help="Total synthetic student records to generate (50 – 10,000).",
            )

            c_yr, c_sem = st.columns(2)
            with c_yr:
                academic_year = st.selectbox(
                    "Academic Year",
                    ["2022-23", "2023-24", "2024-25", "2025-26"],
                    index=2,
                )
            with c_sem:
                semester = st.selectbox("Semester", ["Odd", "Even", "Summer"])

            dept_input = st.text_area(
                "Department Selection (one per line)",
                value="\n".join(config.DEFAULT_DEPARTMENTS),
                height=130,
                help="Enter each academic department on a separate line.",
            )

    # B. Behavioral Configuration
    with col_right:
        with st.container(border=True):
            st.markdown("#### B. Behavioral Configuration")
            st.caption("Adjust student attendance patterns and behavioral distribution.")

            st.markdown("**Attendance Pattern Mix (%)**")
            pct_regular   = st.slider("Regular Attendance (82–100%)",   0, 100, 40)
            pct_moderate  = st.slider("Moderate Attendance (63–85%)",  0, 100, 30)
            pct_irregular = st.slider("Irregular Attendance (42–65%)", 0, 100, 20)
            pct_low       = st.slider("Low Attendance (18–45%)",       0, 100, 10)
            total_pct = pct_regular + pct_moderate + pct_irregular + pct_low

            st.caption(
                f"Total weight: **{total_pct}%** (automatically normalized) · "
                "Engagement & academic scores correlate with attendance."
            )

            with st.expander("Engagement Pattern Baseline"):
                eng_cols = st.columns(3)
                eng_cols[0].metric("High Engagement", f"{int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION['High']*100)}%")
                eng_cols[1].metric("Medium Engagement", f"{int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION['Medium']*100)}%")
                eng_cols[2].metric("Low Engagement", f"{int(config.DEFAULT_ENGAGEMENT_DISTRIBUTION['Low']*100)}%")

    # C. Advanced Settings
    with st.container(border=True):
        st.markdown("#### C. Advanced Settings")
        adv1, adv2 = st.columns([1, 2])
        with adv1:
            seed = st.number_input(
                "Random Seed",
                min_value=0,
                max_value=99_999,
                value=config.DEFAULT_SEED,
                help="Use the same seed to reproduce an identical dataset.",
            )
        with adv2:
            auto_validate = st.checkbox(
                "Run automated 11-point data quality validation after generation",
                value=True,
                help="Verifies value bounds, uniqueness, and attendance math consistency.",
            )

    btn_col, reset_col = st.columns([4, 1])
    with btn_col:
        generate_btn = st.form_submit_button(
            "Generate Dataset",
            type="primary",
            icon=":material/play_arrow:",
            use_container_width=True,
        )
    with reset_col:
        reset_btn = st.form_submit_button(
            "Reset Defaults",
            icon=":material/restart_alt:",
            use_container_width=True,
        )

if reset_btn:
    st.rerun()

# ---------------------------------------------------------------------------
# Validation & Generation Execution
# ---------------------------------------------------------------------------
if generate_btn:
    errors = []
    departments = [d.strip() for d in dept_input.strip().splitlines() if d.strip()]
    if len(departments) == 0:
        errors.append("Please enter at least one department name.")
    if total_pct == 0:
        errors.append("Attendance pattern proportions must sum to more than 0.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        att_dist = {
            "Regular":   pct_regular   / max(total_pct, 1),
            "Moderate":  pct_moderate  / max(total_pct, 1),
            "Irregular": pct_irregular / max(total_pct, 1),
            "Low":       pct_low       / max(total_pct, 1),
        }

        progress_bar = st.progress(0, text="Initializing synthetic generator...")
        try:
            progress_bar.progress(25, text="Generating correlated student profiles...")
            df = generate_dataset(
                n_students=int(n_students),
                departments=departments,
                academic_year=academic_year,
                semester=semester,
                attendance_distribution=att_dist,
                seed=int(seed),
            )
            progress_bar.progress(70, text="Running data quality validation...")
            validation = validate_dataset(df) if auto_validate else validate_dataset(df)
            progress_bar.progress(95, text="Saving cohort to session...")

            st.session_state["df"]              = df
            st.session_state["validation"]      = validation
            st.session_state["generation_seed"] = int(seed)
            st.session_state["generation_year"] = academic_year
            st.session_state["generation_meta"] = {
                "n_students":    int(n_students),
                "departments":   departments,
                "academic_year": academic_year,
                "semester":      semester,
                "seed":          int(seed),
                "att_dist":      att_dist,
            }
            st.session_state.pop("ml_result", None)
            st.session_state.pop("filtered_df", None)

            progress_bar.progress(100, text="Complete")
            st.success(f"Generated **{len(df):,}** synthetic student records successfully (Seed: {int(seed)}).")
        except Exception as ex:
            progress_bar.empty()
            st.error(f"Generation failed: {ex}")
            raise

# ---------------------------------------------------------------------------
# Cohort Preview
# ---------------------------------------------------------------------------
df = st.session_state.get("df")
if df is not None:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Generated Cohort Overview</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Records",  f"{len(df):,}")
    s2.metric("Departments",    df["department"].nunique())
    s3.metric("Avg Attendance", f"{df['attendance_percentage'].mean():.1f}%")
    s4.metric("High-Risk",      int((df["risk_category"] == "High").sum()))

    with st.container(border=True):
        st.markdown("**Sample Records (First 10 Rows)**")
        st.dataframe(df.head(10), use_container_width=True)

    validation = st.session_state.get("validation", {})
    summary    = validation.get("summary", {})
    if summary:
        qpct = summary.get("quality_pct", 0)
        if qpct == 100:
            st.success(f"Data Quality Score: **{qpct}%** — All validation checks passed.")
        elif qpct >= 95:
            st.warning(f"Data Quality Score: **{qpct}%** — Minor issues detected.")
        else:
            st.error(f"Data Quality Score: **{qpct}%** — Issues found. Review on Data Quality page.")
