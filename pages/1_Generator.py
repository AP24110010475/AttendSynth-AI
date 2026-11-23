"""
pages/1_Generator.py — Synthetic Data Generator page for AttendSynth AI.
"""

import streamlit as st
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.generator import generate_dataset
from src.validation import validate_dataset

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Generator | AttendSynth AI", page_icon="🔧", layout="wide")

css_path = os.path.join(ROOT, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
        <span style='font-size:2rem;'>🎓</span>
        <h2 style='margin:0.3rem 0 0;font-size:1.1rem;color:#3a3a6e;font-weight:700;'>AttendSynth AI</h2>
    </div><hr style='margin:0.8rem 0;'>
    """, unsafe_allow_html=True)

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class='page-header'>
    <h1>🔧 Synthetic Data Generator</h1>
    <p>Configure parameters and generate a correlated synthetic student engagement dataset.</p>
</div>
""", unsafe_allow_html=True)

# ── Settings form ─────────────────────────────────────────────────────────────
with st.form("generator_form"):
    st.markdown("### ⚙️ Dataset Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        n_students = st.number_input(
            "Number of Students",
            min_value=50, max_value=10_000, value=config.DEFAULT_N_STUDENTS, step=50,
            help="How many synthetic student records to generate (50–10,000).",
        )
        academic_year = st.selectbox(
            "Academic Year",
            ["2022-23", "2023-24", "2024-25", "2025-26"],
            index=2,
        )
        semester = st.selectbox("Semester", ["Odd", "Even", "Summer"])

    with col2:
        seed = st.number_input(
            "Random Seed",
            min_value=0, max_value=99_999, value=config.DEFAULT_SEED,
            help="Set the same seed to reproduce identical datasets.",
        )
        dept_input = st.text_area(
            "Department Names (one per line)",
            value="\n".join(config.DEFAULT_DEPARTMENTS),
            height=140,
            help="Enter each department on a new line.",
        )

    with col3:
        st.markdown("**Attendance Pattern Distribution**")
        st.caption("Proportions should sum to 100 %")
        pct_regular   = st.slider("Regular (%)",   0, 100, 40)
        pct_moderate  = st.slider("Moderate (%)",  0, 100, 30)
        pct_irregular = st.slider("Irregular (%)", 0, 100, 20)
        pct_low       = st.slider("Low (%)",        0, 100, 10)
        total_pct = pct_regular + pct_moderate + pct_irregular + pct_low

    st.markdown("---")
    gen_col, reset_col = st.columns([3, 1])
    with gen_col:
        generate_btn = st.form_submit_button("🚀 Generate Dataset", use_container_width=True, type="primary")
    with reset_col:
        reset_btn = st.form_submit_button("🔄 Reset to Defaults", use_container_width=True)

# ── Handle Reset ──────────────────────────────────────────────────────────────
if reset_btn:
    st.rerun()

# ── Validation & Generation ───────────────────────────────────────────────────
if generate_btn:
    # Input validation
    errors = []
    departments = [d.strip() for d in dept_input.strip().splitlines() if d.strip()]
    if len(departments) == 0:
        errors.append("Please enter at least one department name.")
    if total_pct == 0:
        errors.append("Attendance pattern proportions must sum to more than 0.")

    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        # Normalise distribution (doesn't need to exactly equal 100)
        att_dist = {
            "Regular":   pct_regular   / max(total_pct, 1),
            "Moderate":  pct_moderate  / max(total_pct, 1),
            "Irregular": pct_irregular / max(total_pct, 1),
            "Low":       pct_low       / max(total_pct, 1),
        }

        progress_bar = st.progress(0, text="Initialising generator...")

        try:
            progress_bar.progress(20, text="Generating student profiles...")
            df = generate_dataset(
                n_students=int(n_students),
                departments=departments,
                academic_year=academic_year,
                semester=semester,
                attendance_distribution=att_dist,
                seed=int(seed),
            )
            progress_bar.progress(60, text="Validating dataset...")
            validation = validate_dataset(df)
            progress_bar.progress(90, text="Finalising...")

            # Persist to session state
            st.session_state["df"]              = df
            st.session_state["validation"]      = validation
            st.session_state["generation_seed"] = seed
            st.session_state["generation_year"] = academic_year
            st.session_state["generation_meta"] = {
                "n_students":    int(n_students),
                "departments":   departments,
                "academic_year": academic_year,
                "semester":      semester,
                "seed":          int(seed),
                "att_dist":      att_dist,
            }

            progress_bar.progress(100, text="Done!")
            st.success(f"✅ Successfully generated **{len(df):,}** synthetic student records!")

        except Exception as ex:
            progress_bar.empty()
            st.error(f"❌ Generation failed: {ex}")
            raise

# ── Show preview if dataset exists ────────────────────────────────────────────
df = st.session_state.get("df")
if df is not None:
    st.markdown("---")
    st.markdown("### 📊 Generation Summary")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Records",   f"{len(df):,}")
    s2.metric("Departments",     df["department"].nunique())
    s3.metric("Avg Attendance",  f"{df['attendance_percentage'].mean():.1f}%")
    s4.metric("High-Risk Count", int((df["risk_category"] == "High").sum()))

    st.markdown("### 🔍 Preview (first 10 rows)")
    st.dataframe(df.head(10), use_container_width=True)

    validation = st.session_state.get("validation", {})
    summary    = validation.get("summary", {})
    if summary:
        qpct = summary.get("quality_pct", 0)
        if qpct == 100:
            st.success(f"✅ Data Quality: **{qpct}%** — All validation checks passed.")
        elif qpct >= 95:
            st.warning(f"⚠️ Data Quality: **{qpct}%** — Minor issues detected. See Data Quality page.")
        else:
            st.error(f"❌ Data Quality: **{qpct}%** — Issues found. See Data Quality page.")
else:
    st.info("👆 Configure the parameters above and click **Generate Dataset** to get started.")
