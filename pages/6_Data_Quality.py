"""
pages/6_Data_Quality.py — Data Quality Report page for AttendSynth AI.
"""

import streamlit as st
import pandas as pd
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
from src.validation import validate_dataset
from src.export import quality_report_to_csv_bytes, quality_report_to_json_bytes

st.set_page_config(page_title="Data Quality | AttendSynth AI", page_icon="✅", layout="wide")

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
    <h1>✅ Data Quality Report</h1>
    <p>Automated validation checks on the generated synthetic dataset.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

if df is None:
    st.warning("⚠️ No dataset found.  Please generate one on the **🔧 Generator** page first.")
    st.stop()

# Always run fresh validation
validation = validate_dataset(df)
st.session_state["validation"] = validation

summary = validation["summary"]
checks  = validation["checks"]

# ── Summary KPIs ──────────────────────────────────────────────────────────────
st.markdown("### 📊 Quality Summary")
q1, q2, q3, q4, q5 = st.columns(5)
q1.metric("Total Records",   f"{summary['total_records']:,}")
q2.metric("Valid Records",   f"{summary['valid_records']:,}")
q3.metric("Invalid Records", f"{summary['invalid_records']:,}")
q4.metric("Missing Values",  f"{summary['missing_values']}")
q5.metric("Quality Score",   f"{summary['quality_pct']}%")

st.markdown("---")

# Quality badge
qpct = summary["quality_pct"]
if qpct == 100.0:
    st.success(f"✅ **Data Quality: {qpct}%** — All {len(checks)} validation checks passed.")
elif qpct >= 95.0:
    st.warning(f"⚠️ **Data Quality: {qpct}%** — Minor issues detected.")
else:
    st.error(f"❌ **Data Quality: {qpct}%** — Significant issues found.")

st.markdown("---")

# ── Individual check results ───────────────────────────────────────────────────
st.markdown("### 🔍 Validation Checks")

for check in checks:
    icon  = "✅" if check["passed"] else "❌"
    color = "#34C98A" if check["passed"] else "#F77066"
    status_text = "PASSED" if check["passed"] else f"FAILED — {check['count']} record(s) affected"

    with st.expander(f"{icon} {check['check']}  —  `{status_text}`"):
        c1, c2 = st.columns(2)
        c1.markdown(f"**Status:** {'✅ Passed' if check['passed'] else '❌ Failed'}")
        c2.markdown(f"**Records affected:** {check['count']}")
        if check.get("detail"):
            st.markdown("**Details:**")
            st.json(check["detail"])

st.markdown("---")

# ── Attribute-level null check ─────────────────────────────────────────────────
st.markdown("### 🧪 Column-Level Missing Value Analysis")
null_counts = df.isnull().sum().reset_index()
null_counts.columns = ["Column", "Missing Count"]
null_counts["Missing %"] = (null_counts["Missing Count"] / len(df) * 100).round(2)
null_counts["Status"] = null_counts["Missing Count"].apply(lambda x: "✅ OK" if x == 0 else "❌ Missing")
st.dataframe(null_counts, use_container_width=True)

st.markdown("---")

# ── Download buttons ───────────────────────────────────────────────────────────
st.markdown("### 📥 Download Report")
dl1, dl2 = st.columns(2)

with dl1:
    st.download_button(
        label="⬇️ Download Quality Report (CSV)",
        data=quality_report_to_csv_bytes(validation),
        file_name=config.EXPORT_QUALITY_REPORT,
        mime="text/csv",
    )

with dl2:
    st.download_button(
        label="⬇️ Download Quality Report (JSON)",
        data=quality_report_to_json_bytes(validation),
        file_name="attendsynth_quality_report.json",
        mime="application/json",
    )
