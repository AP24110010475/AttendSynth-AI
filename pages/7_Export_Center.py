"""
pages/7_Export_Center.py — Export Centre page for AttendSynth AI.
"""

import streamlit as st
import pandas as pd
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
from src.export import (
    to_csv_bytes,
    to_json_bytes,
    quality_report_to_csv_bytes,
    quality_report_to_json_bytes,
)

st.set_page_config(page_title="Export Center | AttendSynth AI", page_icon="📥", layout="wide")

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
    <h1>📥 Export Center</h1>
    <p>Download the complete or filtered dataset, and the data quality report.</p>
</div>
""", unsafe_allow_html=True)

df: pd.DataFrame | None = st.session_state.get("df")

if df is None:
    st.warning("⚠️ No dataset found.  Please generate one on the **🔧 Generator** page first.")
    st.stop()

filtered_df: pd.DataFrame | None = st.session_state.get("filtered_df", df)
validation = st.session_state.get("validation")

st.markdown(f"**Active dataset:** `{len(df):,}` records  |  "
            f"**Filtered dataset:** `{len(filtered_df):,}` records")

st.markdown("---")

# ── Section 1: Full Dataset ────────────────────────────────────────────────────
st.markdown("### 📦 Full Dataset")
st.markdown(f"Complete synthetic dataset with **{len(df):,}** student records and **{len(df.columns)}** columns.")

e1, e2 = st.columns(2)
with e1:
    st.download_button(
        label="⬇️ Download Full Dataset (CSV)",
        data=to_csv_bytes(df),
        file_name=config.EXPORT_CSV_FULL,
        mime="text/csv",
        use_container_width=True,
    )
with e2:
    st.download_button(
        label="⬇️ Download Full Dataset (JSON)",
        data=to_json_bytes(df),
        file_name=config.EXPORT_JSON_FULL,
        mime="application/json",
        use_container_width=True,
    )

st.markdown("---")

# ── Section 2: Filtered Dataset ───────────────────────────────────────────────
st.markdown("### 🔎 Filtered Dataset")
st.markdown(
    f"Use the **Dataset Explorer** page to apply filters.  "
    f"Currently **{len(filtered_df):,}** records are selected."
)

if filtered_df is not None and not filtered_df.empty:
    e3, e4 = st.columns(2)
    with e3:
        st.download_button(
            label="⬇️ Download Filtered Dataset (CSV)",
            data=to_csv_bytes(filtered_df),
            file_name=config.EXPORT_CSV_FILTERED,
            mime="text/csv",
            use_container_width=True,
        )
    with e4:
        st.download_button(
            label="⬇️ Download Filtered Dataset (JSON)",
            data=to_json_bytes(filtered_df),
            file_name="attendsynth_dataset_filtered.json",
            mime="application/json",
            use_container_width=True,
        )
else:
    st.info("No filtered records available.  Visit the Dataset Explorer page to apply filters.")

st.markdown("---")

# ── Section 3: Quality Report ─────────────────────────────────────────────────
st.markdown("### ✅ Data Quality Report")

if validation:
    e5, e6 = st.columns(2)
    with e5:
        st.download_button(
            label="⬇️ Download Quality Report (CSV)",
            data=quality_report_to_csv_bytes(validation),
            file_name=config.EXPORT_QUALITY_REPORT,
            mime="text/csv",
            use_container_width=True,
        )
    with e6:
        st.download_button(
            label="⬇️ Download Quality Report (JSON)",
            data=quality_report_to_json_bytes(validation),
            file_name="attendsynth_quality_report.json",
            mime="application/json",
            use_container_width=True,
        )
else:
    st.info("Run validation on the **Data Quality** page first to enable quality report download.")

st.markdown("---")

# ── Preview ────────────────────────────────────────────────────────────────────
with st.expander("👀 Preview — Full Dataset (first 10 rows)"):
    st.dataframe(df.head(10), use_container_width=True)

with st.expander("👀 Preview — Filtered Dataset (first 10 rows)"):
    if filtered_df is not None and not filtered_df.empty:
        st.dataframe(filtered_df.head(10), use_container_width=True)
    else:
        st.info("No filtered data available.")
