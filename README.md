# AttendSynth AI — Synthetic Student Engagement Generator

![AttendSynth AI](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

> **AttendSynth AI** is a state-of-the-art educational data synthesis platform built with Python and Streamlit. It generates realistic, correlated synthetic student attendance and engagement datasets for developing and prototyping academic early-warning systems without exposing sensitive, real-world student records.

---

## 📑 Table of Contents
1. [Abstract](#abstract)
2. [Introduction & Problem Statement](#introduction--problem-statement)
3. [Objectives](#objectives)
4. [Existing vs. Proposed System](#existing-vs-proposed-system)
5. [Technologies Used](#technologies-used)
6. [System Architecture](#system-architecture)
7. [Methodology & Data Generation](#methodology--data-generation)
8. [Data Validation Framework](#data-validation-framework)
9. [Early-Warning Methodology](#early-warning-methodology)
10. [Machine Learning Demonstration](#machine-learning-demonstration)
11. [Results & Analytical Capabilities](#results--analytical-capabilities)
12. [Advantages & Limitations](#advantages--limitations)
13. [Future Enhancements](#future-enhancements)
14. [Installation & Execution Guide](#installation--execution-guide)
15. [Deployment Guide (Streamlit Community Cloud)](#deployment-guide-streamlit-community-cloud)
16. [References](#references)

---

## 1. Abstract
Institutional early-warning systems are critical for identifying students at risk of academic failure or dropout. However, developing and testing machine learning models or rule-based heuristics requires access to student datasets, which are heavily restricted by student privacy regulations (such as FERPA, GDPR, and institutional data governance policies). **AttendSynth AI** resolves this bottleneck by generating synthetic datasets containing realistic multi-variable distributions and behavioral correlations (attendance, LMS activity, assignment completion, participation, and academic performance). The application features an interactive multi-page dashboard with real-time validation, analytics, ML benchmarking, and multi-format exports.

---

## 2. Introduction & Problem Statement
Data science teams and educational researchers often face strict barriers when prototyping student analytics:
- **Privacy Constraints:** Real student records contain Protected Personally Identifiable Information (PII) and academic history.
- **Data Scarcity & Cold Start:** New institutions lack historical digitized engagement metrics.
- **Unrealistic Random Mock Data:** Simple pseudo-random generators create uncorrelated features (e.g., a student with 10% attendance having 99% assignment completion and top grades), making models trained on them dysfunctional.

**AttendSynth AI** provides an end-to-end synthetic data generation pipeline grounded in educational behavioral models, yielding statistically plausible records with preserved feature dependencies.

---

## 3. Objectives
- Generate configurable, reproducible synthetic cohorts (from 50 up to 10,000 students).
- Model realistic behavioral distributions across attendance, platform activity, and assessments.
- Establish strict mathematical bounds ensuring absolute physical validity (e.g., classes attended $\le$ total classes).
- Provide automated data quality verification with zero tolerance for silent data corruption.
- Provide interactive visual exploration, early-warning risk scoring, and a benchmark ML classifier.
- Enable one-click export in CSV and JSON formats for filtered and full cohorts.

---

## 4. Existing vs. Proposed System

| Dimension | Traditional / Existing Approach | AttendSynth AI Platform |
|---|---|---|
| **Data Source** | Anonymized real data (privacy risk) or naive `np.random` | Statistically correlated synthetic behavioral models |
| **Feature Correlation** | Independent variables with zero correlation | Multi-tier dependency: Profile $\to$ Attendance $\to$ Engagement $\to$ Performance $\to$ Risk |
| **Privacy Compliance** | Requires NDAs, IRB approval, data sanitization | 100% synthetic; zero PII leakage risk |
| **Interactivity** | Static CSV scripts | Complete modern Streamlit web application |
| **Quality Control** | Manual inspection | Automated 11-point data validation suite |
| **Deployment** | Local command-line only | Cloud-ready for Streamlit Community Cloud & Docker |

---

## 5. Technologies Used
- **Language:** Python 3.11+
- **Frontend Framework:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Synthetic Profile Generation:** Faker
- **Interactive Visualizations:** Plotly Express & Plotly Graph Objects
- **Machine Learning Engine:** Scikit-learn (RandomForestClassifier, LabelEncoder, metrics)
- **Unit Testing:** Pytest
- **Styling:** Custom CSS with modern SaaS aesthetics

---

## 6. System Architecture

```
AttendSynth AI Architecture
│
├── Streamlit Frontend (Multi-Page UI)
│   ├── Home Dashboard (KPI metrics, cohort summary)
│   ├── 1. Synthetic Data Generator (Parameter controls, seed, distributions)
│   ├── 2. Dataset Explorer (Search, multi-dimensional filters, data viewer)
│   ├── 3. Analytics Dashboard (Plotly distributions, correlations, KPIs)
│   ├── 4. Early Warning Analysis (Rule-based heuristics, factor breakdown)
│   ├── 5. Machine Learning (Random Forest classifier, metrics, confusion matrix)
│   ├── 6. Data Quality Report (11 validation checks, missingness audit)
│   ├── 7. Export Center (CSV / JSON full and filtered downloads)
│   └── 8. About Project (Documentation, specs, and ethics)
│
├── Python Backend Engine (`src/`)
│   ├── generator.py     → Latent behavioral modeling & correlated simulation
│   ├── validation.py    → 11-point deterministic data validation engine
│   ├── risk_engine.py   → Transparent multi-criteria risk scoring system
│   ├── analytics.py     → Metric aggregation & Plotly visualization constructors
│   ├── ml_model.py      → Feature pipeline & Scikit-learn demonstration
│   └── export.py        → In-memory stream serialization (CSV/JSON)
│
└── Configuration & Tests
    ├── config.py        → Global parameters, weights, and styling tokens
    └── tests/           → Complete Pytest test suite
```

---

## 7. Methodology & Data Generation

### Latent Behavioral Profile Simulation
Each student $i$ is assigned a latent profile $P_i \in \{\text{Regular}, \text{Moderate}, \text{Irregular}, \text{Low}\}$ based on configurable prior probabilities.

1. **Attendance Modeling:**
   $$A_i \sim \mathcal{N}(\mu_{P}, \sigma_{P}^2) \quad \text{clamped to } [L_P, U_P]$$
   From attendance percentage $A_i$ and total classes $C_i$, integer attendance is computed:
   $$c_i = \min\left(\left\lfloor \frac{C_i \cdot A_i}{100} + 0.5 \right\rfloor, C_i\right)$$
   Actual percentage is recalculated from $c_i / C_i$ to ensure zero rounding discrepancy.

2. **Correlated Engagement Components:**
   - **Assignment Completion:** Strongly linked to base attendance:
     $$\text{Asgn}_i = \text{clip}\left(15 + 0.75 \cdot A_i + \epsilon_{\text{asgn}}, 0, 100\right)$$
   - **Platform Activity:**
     $$\text{Plat}_i = \text{clip}\left(10 + 0.80 \cdot A_i + \epsilon_{\text{plat}}, 0, 100\right)$$
   - **Participation Score:**
     $$\text{Part}_i = \text{clip}\left(10 + 0.70 \cdot A_i + \epsilon_{\text{part}}, 0, 100\right)$$

3. **Composite Engagement Score:**
   $$\text{Eng}_i = 0.40 \cdot \text{Asgn}_i + 0.35 \cdot \text{Plat}_i + 0.25 \cdot \text{Part}_i$$

4. **Academic Performance Simulation:**
   $$\text{Acad}_i = \text{clip}\left(0.50 \cdot \text{Eng}_i + 0.30 \cdot A_i + 0.20 \cdot \text{Asgn}_i + \epsilon_{\text{acad}}, 0, 100\right)$$

---

## 8. Data Validation Framework
The application runs an 11-point integrity audit:
1. **Missing Value Audit:** Zero nulls allowed.
2. **Uniqueness Audit:** Ensures zero duplicate student IDs.
3. **Attendance Bounds:** Enforces $0 \le A_i \le 100$.
4. **Attendance Consistency:** Verifies $\left|\frac{c_i}{C_i}\times 100 - A_i\right| \le 1.0\%$.
5. **Physical Class Constraint:** Asserts $c_i \le C_i$.
6. **Engagement Score Bounds:** $0 \le \text{Eng}_i \le 100$.
7. **Academic Performance Bounds:** $0 \le \text{Acad}_i \le 100$.
8. **Risk Score Bounds:** $0 \le \text{Risk}_i \le 100$.
9. **Categorical Domain Integrity:** $\text{RiskCat}_i \in \{\text{Low}, \text{Medium}, \text{High}\}$.
10. **Assignment Completion Bounds:** $0 \le \text{Asgn}_i \le 100$.
11. **Age Demographics:** Validates age falls within collegiate range $[17, 26]$.

---

## 9. Early-Warning Methodology
AttendSynth AI distinguishes between heuristic risk rules and trained ML models. The early-warning engine uses an **interpretable, weighted rule-based index**:

$$\text{Positive Index}_i = 0.35 \cdot A_i + 0.25 \cdot \text{Eng}_i + 0.25 \cdot \text{Asgn}_i + 0.15 \cdot \text{Acad}_i$$
$$\text{Risk Score}_i = 100 - \text{Positive Index}_i$$

- **Low Risk:** $\text{Risk Score} < 35$
- **Medium Risk:** $35 \le \text{Risk Score} < 60$
- **High Risk:** $\text{Risk Score} \ge 60$

Individual records display precise factor triggers (e.g., Attendance $< 50\%$, LMS Engagement $< 40$).

---

## 10. Machine Learning Demonstration
- **Target:** `risk_category`
- **Features Used:** `age`, `attendance_percentage`, `assignment_completion_percentage`, `learning_platform_activity`, `participation_score`, `engagement_score`, `academic_performance_score`.
- **Target Leakage Prevention:** `risk_score` is strictly excluded from feature inputs.
- **Algorithm:** Scikit-learn `RandomForestClassifier` with balanced class weighting.
- **Evaluation:** Precision, Recall, F1-Score (macro-averaged), and interactive Confusion Matrix.

> *Educational Notice: High model accuracy on synthetic data reflects adherence to the generative rules and does not imply real-world predictive validity.*

---

## 11. Results & Analytical Capabilities
The embedded analytics dashboard renders:
- Attendance, Engagement, and Academic score histograms with cohort means.
- Department-wise attendance ranking bar charts.
- Donut charts representing cohort risk distribution.
- Attendance vs. Engagement scatter plots categorized by risk tier.
- Box plots of assignment completion across behavioural cohorts.
- Departmental stacked engagement band distributions.

---

## 12. Advantages & Limitations

### Advantages
- Completely eliminates student data privacy risks.
- Reproducible datasets using deterministic random seeds.
- Fast generation (under 1.5 seconds for 10,000 records).
- Built-in validation guarantees data hygiene before modeling.

### Limitations
- Synthetically generated distributions cannot model non-linear socio-economic externalities.
- The default risk engine relies on predefined weights which may vary across institutions.

---

## 13. Future Enhancements
- Longitudinal multi-semester cohorts tracking retention across years.
- Custom weight configuration directly in the Early Warning UI.
- Direct export into relational databases (SQLite / PostgreSQL).
- REST API integration via FastAPI.

---

## 14. Installation & Execution Guide

### Prerequisites
- Python 3.11 or higher
- Git

### Local Setup
```bash
# Clone repository
git clone https://github.com/<your-username>/attendsynth-ai.git
cd attendsynth-ai

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run test suite
pytest -v

# Launch the Streamlit application
streamlit run app.py
```

---

## 15. Deployment Guide (Streamlit Community Cloud)
See [DEPLOYMENT_GUIDE.md](documentation/DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

---

## 16. References
1. Baker, R. S., & Inventado, P. S. (2014). *Educational Data Mining and Learning Analytics*.
2. Romero, C., & Ventura, S. (2020). *Educational Data Mining: A Review of the State of the Art*.
3. Streamlit Documentation: https://docs.streamlit.io/
4. Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.
