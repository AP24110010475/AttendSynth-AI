"""
pages/8_About.py — About Project page for AttendSynth AI.
"""

import os
import sys
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header

st.set_page_config(page_title=f"About | {config.APP_TITLE}", page_icon="ℹ️", layout="wide")
load_styles()
render_sidebar("About")

render_page_header(
    "About AttendSynth AI",
    "Platform architecture, statistical data generation methodology, and ethical guidelines.",
)

# ---------------------------------------------------------------------------
# Abstract & Objectives
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### Abstract")
    st.markdown(
        """
        **AttendSynth AI** is a synthetic student engagement generator built to support the
        development and prototyping of academic early-warning systems. The platform produces
        statistically plausible datasets with realistic correlations across attendance, LMS activity,
        assignment completion, and academic performance — without exposing real student records.
        """
    )

o1, o2, o3 = st.columns(3)
with o1:
    with st.container(border=True):
        st.markdown("**Research Support**")
        st.caption("Provide safe, ethically unrestricted synthetic datasets for academic engagement research.")
with o2:
    with st.container(border=True):
        st.markdown("**Privacy Protection**")
        st.caption("Prototype early-warning models without handling real student PII or institutional records.")
with o3:
    with st.container(border=True):
        st.markdown("**Realistic Simulation**")
        st.caption("Generate correlated, bounded distributions rather than independent random noise.")

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Methodology & Architecture
# ---------------------------------------------------------------------------
c_left, c_right = st.columns(2)

with c_left:
    with st.container(border=True):
        st.markdown("#### Data Generation Methodology")
        st.markdown(
            """
            Each student is assigned a **latent behavioral profile** drawn from configurable priors:

            | Profile | Attendance Range |
            |---|---|
            | Regular | 82–100% |
            | Moderate | 63–85% |
            | Irregular | 42–65% |
            | Low | 18–45% |

            All downstream attributes derive hierarchically from this profile using bounded normal distributions:
            `Profile → Attendance → Engagement Components → Academic Performance → Risk Score`
            """
        )

with c_right:
    with st.container(border=True):
        st.markdown("#### Early-Warning Risk Formula")
        st.markdown(
            """
            Risk scoring uses a **transparent deterministic formula** (not a trained ML model):

            ```
            risk_score = 100 − (
                0.35 × attendance_percentage +
                0.25 × engagement_score +
                0.25 × assignment_completion_percentage +
                0.15 × academic_performance_score
            )
            ```

            - **Low Risk:** `0 – 34`
            - **Medium Risk:** `35 – 59`
            - **High Risk:** `60 – 100`
            """
        )

# ---------------------------------------------------------------------------
# Technology Stack & Limitations
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### Technology Stack")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            """
            | Component | Technology |
            |---|---|
            | Language | Python 3.11+ |
            | Frontend | Streamlit |
            | Data Processing | Pandas & NumPy |
            | Synthetic Profiles | Faker |
            """
        )
    with t2:
        st.markdown(
            """
            | Component | Technology |
            |---|---|
            | Visualizations | Plotly |
            | Machine Learning | Scikit-learn |
            | Testing | Pytest |
            | Deployment | Streamlit Community Cloud |
            """
        )

with st.container(border=True):
    st.markdown("#### Limitations & Ethical Notice")
    st.markdown(
        """
        - All generated data is **100% synthetic**; insights do not represent real student populations.
        - The Machine Learning demonstration trains on synthetic labels generated from deterministic rules and does not establish real-world predictive accuracy.
        - Fixed heuristic weights in the early-warning engine may differ from institutional grading or intervention policies.
        """
    )

st.markdown(
    f"<div style='text-align:center; color:#9CA3AF; font-size:0.8rem; margin-top:1.5rem;'>"
    f"AttendSynth AI v{config.APP_VERSION} &middot; Built with Python & Streamlit"
    f"</div>",
    unsafe_allow_html=True,
)
