# AttendSynth AI — Development Plan

## Project Summary
AttendSynth AI is a Synthetic Student Engagement Generator built with Python and Streamlit.
It generates realistic, correlated synthetic student attendance and engagement datasets for
prototyping early-warning systems — without using real student data.

---

## Architecture Decisions

| Decision | Choice | Reason |
|---|---|---|
| Frontend | Streamlit | Rapid UI, cloud-deployable, Python-native |
| Data generation | NumPy + Faker | Statistically correlated profiles |
| Visualisations | Plotly | Interactive, embeds in Streamlit |
| ML | Scikit-learn Random Forest | Simple, interpretable, no GPU |
| Testing | Pytest | Standard Python testing |
| State management | st.session_state | Cross-page data persistence |

---

## Phase Checklist

| Phase | Description | Status |
|---|---|---|
| 1 | Requirements & architecture | ✅ Done |
| 2 | Project structure & dependencies | ✅ Done |
| 3 | Synthetic data generation engine | ✅ Done |
| 4 | Data validation module | ✅ Done |
| 5 | Streamlit interface (app.py + pages) | ✅ Done |
| 6 | Dataset explorer | ✅ Done |
| 7 | Analytics & visualisations | ✅ Done |
| 8 | Early-warning analysis | ✅ Done |
| 9 | Machine learning demonstration | ✅ Done |
| 10 | Export centre & integration | ✅ Done |
| 11 | Testing & debugging | ✅ Done |
| 12 | Deployment preparation & docs | ✅ Done |

---

## Folder Structure

```
AttendSynth AI/
├── app.py                  # Streamlit entry point
├── config.py               # App-wide constants
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── DEVELOPMENT_PLAN.md     # This file
│
├── src/
│   ├── __init__.py
│   ├── generator.py        # Core data generation engine
│   ├── validation.py       # Data quality checks
│   ├── analytics.py        # Chart / insight helpers
│   ├── risk_engine.py      # Rule-based risk scoring
│   ├── ml_model.py         # Scikit-learn demo
│   └── export.py           # CSV / JSON export helpers
│
├── pages/                  # Streamlit multi-page app
│   ├── 1_Generator.py
│   ├── 2_Dataset_Explorer.py
│   ├── 3_Analytics.py
│   ├── 4_Early_Warning.py
│   ├── 5_Machine_Learning.py
│   ├── 6_Data_Quality.py
│   ├── 7_Export_Center.py
│   └── 8_About.py
│
├── assets/
│   └── style.css
│
├── data/
│   └── .gitkeep
│
├── models/
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_generator.py
│   ├── test_validation.py
│   └── test_risk_engine.py
│
└── documentation/
    ├── PROJECT_OVERVIEW.md
    ├── SYSTEM_ARCHITECTURE.md
    ├── DATA_GENERATION.md
    ├── TESTING_REPORT.md
    └── DEPLOYMENT_GUIDE.md
```

---

## Data Generation Strategy

Each student is assigned a **latent behavioural profile** (Regular / Moderate / Irregular / Low).
All correlated fields are derived from this profile using bounded normal distributions:

```
behavioural_profile → attendance_pct
attendance_pct      → engagement base
engagement base     → assignment_completion, participation, platform_activity
all above           → academic_performance
academic_performance + attendance → risk_score → risk_category
```

This ensures realistic correlations without independent random values.

---

## Risk Scoring Formula

```
risk_score = 100 − (
    0.35 × attendance_pct +
    0.25 × engagement_score +
    0.25 × assignment_completion +
    0.15 × academic_performance
)
```

Risk Category:
- Low    : risk_score < 35
- Medium : 35 ≤ risk_score < 60
- High   : risk_score ≥ 60
