"""
pages/7_Export_Center.py — Export Centre page for AttendSynth AI.
"""

import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_empty_dataset_state
from src.export import (
    to_csv_bytes,
    to_json_bytes,
    quality_report_to_csv_bytes,
    quality_report_to_json_bytes,
)

st.set_page_config(page_title=f"Export Center | {config.APP_TITLE}", page_icon="📥", layout="wide")
load_styles()
render_sidebar("Export Center")

render_page_header(
    "Export Center",
    "Download complete cohorts, filtered subsets, and automated data quality reports.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

filtered_df: pd.DataFrame | None = st.session_state.get("filtered_df", df)
validation = st.session_state.get("validation")

# ---------------------------------------------------------------------------
# 4 Download Cards (2x2 Grid)
# ---------------------------------------------------------------------------
row1_c1, row1_c2 = st.columns(2)

with row1_c1:
    with st.container(border=True):
        st.markdown("#### CSV Dataset (Full Cohort)")
        st.caption(f"Download all **{len(df):,}** student records and **{len(df.columns)}** attributes as a standard CSV file.")
        st.download_button(
            label="Download Full CSV",
            data=to_csv_bytes(df),
            file_name=config.EXPORT_CSV_FULL,
            mime="text/csv",
            type="primary",
            icon=":material/download:",
            use_container_width=True,
        )

with row1_c2:
    with st.container(border=True):
        st.markdown("#### JSON Dataset (Full Cohort)")
        st.caption(f"Download all **{len(df):,}** student records formatted as structured JSON records.")
        st.download_button(
            label="Download Full JSON",
            data=to_json_bytes(df),
            file_name=config.EXPORT_JSON_FULL,
            mime="application/json",
            type="primary",
            icon=":material/download:",
            use_container_width=True,
        )

row2_c1, row2_c2 = st.columns(2)

with row2_c1:
    with st.container(border=True):
        st.markdown("#### Filtered Dataset")
        if filtered_df is not None and not filtered_df.empty:
            st.caption(f"Download the **{len(filtered_df):,}** records currently selected in Dataset Explorer.")
            fc1, fc2 = st.columns(2)
            with fc1:
                st.download_button(
                    label="Filtered CSV",
                    data=to_csv_bytes(filtered_df),
                    file_name=config.EXPORT_CSV_FILTERED,
                    mime="text/csv",
                    icon=":material/download:",
                    use_container_width=True,
                )
            with fc2:
                st.download_button(
                    label="Filtered JSON",
                    data=to_json_bytes(filtered_df),
                    file_name="attendsynth_dataset_filtered.json",
                    mime="application/json",
                    icon=":material/download:",
                    use_container_width=True,
                )
        else:
            st.caption("No records match your current Dataset Explorer filters.")
            st.info("Adjust filters on the Dataset Explorer page to export a subset.")

with row2_c2:
    with st.container(border=True):
        st.markdown("#### Data Quality Report")
        if validation:
            qpct = validation.get("summary", {}).get("quality_pct", 0)
            st.caption(f"Export the 11-point validation audit results (Quality Score: **{qpct}%**).")
            qc1, qc2 = st.columns(2)
            with qc1:
                st.download_button(
                    label="Report CSV",
                    data=quality_report_to_csv_bytes(validation),
                    file_name=config.EXPORT_QUALITY_REPORT,
                    mime="text/csv",
                    icon=":material/download:",
                    use_container_width=True,
                )
            with qc2:
                st.download_button(
                    label="Report JSON",
                    data=quality_report_to_json_bytes(validation),
                    file_name="attendsynth_quality_report.json",
                    mime="application/json",
                    icon=":material/download:",
                    use_container_width=True,
                )
        else:
            st.caption("Validation report not yet generated.")
            st.info("Visit the Data Quality page to run validation.")

st.markdown("<hr>", unsafe_allow_html=True)

with st.expander("Preview — Full Dataset (First 10 Rows)"):
    st.dataframe(df.head(10), use_container_width=True)

with st.expander("Preview — Filtered Dataset (First 10 Rows)"):
    if filtered_df is not None and not filtered_df.empty:
        st.dataframe(filtered_df.head(10), use_container_width=True)
    else:
        st.info("No filtered records available.")
