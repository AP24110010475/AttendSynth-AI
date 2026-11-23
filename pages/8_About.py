"""
pages/8_About.py — About Project page for AttendSynth AI.
"""

import streamlit as st
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config

st.set_page_config(page_title="About | AttendSynth AI", page_icon="ℹ️", layout="wide")

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
    <h1>ℹ️ About AttendSynth AI</h1>
    <p>Project overview, methodology, and technology stack.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 📄 Abstract")
st.markdown("""
**AttendSynth AI** is a web-based synthetic student engagement generator designed to support
the development and prototyping of academic early-warning systems.  The application generates
statistically plausible datasets that exhibit realistic correlations between student attendance,
engagement, assignment completion, and academic performance — without using or exposing any
real student records.
""")

st.markdown("---")

st.markdown("## 🎯 Objectives")
o1, o2, o3 = st.columns(3)
with o1:
    st.markdown("""
    <div class='card'>
        <b>🔬 Research Support</b><br>
        Provide safe, ethically unrestricted synthetic datasets for academic research on student engagement patterns.
    </div>""", unsafe_allow_html=True)
with o2:
    st.markdown("""
    <div class='card'>
        <b>🛡️ Privacy Protection</b><br>
        Enable prototyping of early-warning models without handling real student PII or academic records.
    </div>""", unsafe_allow_html=True)
with o3:
    st.markdown("""
    <div class='card'>
        <b>📊 Realistic Simulation</b><br>
        Generate correlated, statistically plausible data rather than independent random noise.
    </div>""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 🏗️ System Architecture")
st.markdown("""
```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                      │
│  Home │ Generator │ Explorer │ Analytics │ Early Warning    │
│  ML Demo │ Data Quality │ Export Center │ About            │
└──────────────────────┬──────────────────────────────────────┘
                       │  st.session_state
┌──────────────────────▼──────────────────────────────────────┐
│                     Python Backend (src/)                    │
│                                                              │
│  generator.py     → Correlated synthetic data generation    │
│  validation.py    → Dataset quality checks                  │
│  analytics.py     → Plotly charts & insights                │
│  risk_engine.py   → Rule-based risk scoring                 │
│  ml_model.py      → Scikit-learn Random Forest demo         │
│  export.py        → CSV / JSON export helpers               │
└──────────────────────────────────────────────────────────────┘
```
""")

st.markdown("---")

st.markdown("## 🧠 Data Generation Methodology")
st.markdown("""
Each student is first assigned a **latent behavioural profile** drawn from the user-specified
distribution:

| Profile | Attendance Range | Description |
|---|---|---|
| Regular | 82–100% | Consistently attends classes |
| Moderate | 63–85% | Moderate attendance with occasional absences |
| Irregular | 42–65% | Frequently misses classes |
| Low | 18–45% | Critically low attendance |

All subsequent fields are **derived** from this profile and from each other, ensuring
realistic statistical correlations:

```
behavioural_profile → attendance_percentage
attendance_percentage → assignment_completion, platform_activity, participation_score
all above → engagement_score (weighted composite)
all above → academic_performance_score
all above → risk_score → risk_category
```

Bounded normal distributions ensure all values remain in valid ranges.
""")

st.markdown("---")

st.markdown("## ⚠️ Early-Warning Methodology")
st.markdown("""
Risk scoring uses a **transparent deterministic formula** — not a trained machine learning model:

```
risk_score = 100 − (
    0.35 × attendance_percentage +
    0.25 × engagement_score +
    0.25 × assignment_completion_percentage +
    0.15 × academic_performance_score
)
```

| Risk Score | Category |
|---|---|
| 0 – 34 | 🟢 Low |
| 35 – 59 | 🟡 Medium |
| 60 – 100 | 🔴 High |
""")

st.markdown("---")

st.markdown("## 🛠️ Technology Stack")
tech_col1, tech_col2 = st.columns(2)
with tech_col1:
    st.markdown("""
    | Technology | Version | Purpose |
    |---|---|---|
    | Python | 3.11+ | Core language |
    | Streamlit | ≥1.35 | Web frontend |
    | Pandas | ≥2.1 | Data processing |
    | NumPy | ≥1.26 | Numerical operations |
    """)
with tech_col2:
    st.markdown("""
    | Technology | Version | Purpose |
    |---|---|---|
    | Faker | ≥24 | Synthetic profiles |
    | Plotly | ≥5.20 | Interactive charts |
    | Scikit-learn | ≥1.4 | ML demonstration |
    | Pytest | ≥8.1 | Unit testing |
    """)

st.markdown("---")

st.markdown("## ⚠️ Limitations")
st.markdown("""
- All data is entirely synthetic.  Findings should not be generalised to real student populations.
- The machine learning demonstration is trained on synthetic data with known labels — high accuracy does not indicate real-world predictive power.
- The rule-based risk engine uses fixed weights that may not reflect all institutional policies.
- Faker generates synthetic names and IDs only; no demographic data beyond age is included.
""")

st.markdown("---")

st.markdown("## 🚀 Future Enhancements")
st.markdown("""
- Integration with anonymised institutional data for calibrated generation
- Longitudinal (multi-semester) dataset generation
- Additional ML algorithms (Gradient Boosting, Neural Networks)
- Customisable risk weight configuration
- REST API for programmatic data generation
- Role-specific dashboards (counsellor, faculty, administrator)
""")

st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#9aabbf;font-size:0.85rem;'>"
    f"AttendSynth AI v{config.APP_VERSION} &nbsp;|&nbsp; All data is 100% synthetic &nbsp;|&nbsp; "
    f"Built with Python & Streamlit"
    f"</div>",
    unsafe_allow_html=True,
)
