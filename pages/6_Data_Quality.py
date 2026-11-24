"""
pages/6_Data_Quality.py — Data Quality Report page for AttendSynth AI.
"""

import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_kpi_card, render_empty_dataset_state
from src.validation import validate_dataset
from src.export import quality_report_to_csv_bytes, quality_report_to_json_bytes

st.set_page_config(page_title=f"Data Quality | {config.APP_TITLE}", page_icon="✅", layout="wide")
load_styles()
render_sidebar("Data Quality")

render_page_header(
    "Data Quality Report",
    "Automated 11-point validation audit for schema integrity, bounds, and mathematical consistency.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

validation = validate_dataset(df)
st.session_state["validation"] = validation

summary = validation["summary"]
checks  = validation["checks"]

# ---------------------------------------------------------------------------
# 5 Summary Cards
# ---------------------------------------------------------------------------
q1, q2, q3, q4, q5 = st.columns(5)
with q1:
    render_kpi_card("Total Records", f"{summary['total_records']:,}", "Evaluated rows", "📄", "#3B82F6", "rgba(59,130,246,0.10)")
with q2:
    render_kpi_card("Valid Records", f"{summary['valid_records']:,}", f"{summary['quality_pct']}% quality score", "✓", "#10B981", "rgba(16,185,129,0.12)")
with q3:
    render_kpi_card("Invalid Records", f"{summary['invalid_records']:,}", "Flagged anomalies", "✕", "#EF4444", "rgba(239,68,68,0.10)")
with q4:
    render_kpi_card("Missing Values", f"{summary['missing_values']:,}", "Null cell count", "∅", "#F59E0B", "rgba(245,158,11,0.12)")
with q5:
    render_kpi_card("Duplicate Records", f"{summary['duplicate_ids']:,}", "Duplicate IDs", "⧉", "#60A5FA", "rgba(96,165,250,0.12)")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

qpct = summary["quality_pct"]
if qpct == 100.0:
    st.success(f"Data Quality Score: **{qpct}%** — All {len(checks)} validation checks passed.")
elif qpct >= 95.0:
    st.warning(f"Data Quality Score: **{qpct}%** — Minor anomalies detected.")
else:
    st.error(f"Data Quality Score: **{qpct}%** — Significant validation failures detected.")

# ---------------------------------------------------------------------------
# Clean Validation Results Table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Validation Results Table</div>', unsafe_allow_html=True)
with st.container(border=True):
    check_rows = []
    for c in checks:
        detail_str = str(c.get("detail", {})) if c.get("detail") else "—"
        check_rows.append({
            "Validation Check": c["check"],
            "Status":           "Passed" if c["passed"] else "Failed",
            "Affected Records": c["count"],
            "Details":          detail_str,
        })
    st.dataframe(pd.DataFrame(check_rows), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Column-Level Missing Value Analysis
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Attribute-Level Completeness</div>', unsafe_allow_html=True)
with st.container(border=True):
    null_counts = df.isnull().sum().reset_index()
    null_counts.columns = ["Column", "Missing Count"]
    null_counts["Missing %"] = (null_counts["Missing Count"] / len(df) * 100).round(2)
    null_counts["Status"] = null_counts["Missing Count"].apply(lambda x: "OK" if x == 0 else "Missing")
    st.dataframe(null_counts, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Report Downloads
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Export Quality Report</div>', unsafe_allow_html=True)
dl1, dl2 = st.columns(2)
with dl1:
    st.download_button(
        label="Download Quality Report (CSV)",
        data=quality_report_to_csv_bytes(validation),
        file_name=config.EXPORT_QUALITY_REPORT,
        mime="text/csv",
        icon=":material/download:",
        use_container_width=True,
    )
with dl2:
    st.download_button(
        label="Download Quality Report (JSON)",
        data=quality_report_to_json_bytes(validation),
        file_name="attendsynth_quality_report.json",
        mime="application/json",
        icon=":material/download:",
        use_container_width=True,
    )
