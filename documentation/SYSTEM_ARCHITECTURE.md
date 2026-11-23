# System Architecture — AttendSynth AI

## 1. High-Level Architecture Overview
AttendSynth AI is designed as a modular, decoupled web application. The frontend is built using Streamlit's multi-page architecture, supported by a specialized Python backend package (`src/`) that encapsulates generation, validation, risk heuristics, analytics, and machine learning.

```
+-------------------------------------------------------------------------+
|                           Streamlit User Interface                      |
|                                                                         |
|  [app.py (Home)]   [1_Generator]    [2_Explorer]      [3_Analytics]     |
|  [4_Early_Warning] [5_Machine_Learn] [6_Data_Quality] [7_Export_Center] |
+------------------------------------+------------------------------------+
                                     |
                                     | Reads/Writes Session State
                                     v
+-------------------------------------------------------------------------+
|                           st.session_state                              |
|   - df (Active cohort DataFrame)                                        |
|   - filtered_df (Explorer filtered subset)                              |
|   - validation (Data quality report dictionary)                         |
|   - generation_meta (Cohort parameters & seed)                          |
|   - ml_result (Trained model, metrics, feature importances)             |
+------------------------------------+------------------------------------+
                                     |
                                     | Calls Business Logic
                                     v
+-------------------------------------------------------------------------+
|                         Python Core Engine (src/)                       |
|                                                                         |
|   +-------------------+    +-------------------+   +------------------+ |
|   |   generator.py    |    |   validation.py   |   |  risk_engine.py  | |
|   |  - Profile assign |    |  - 11 Data checks |   |  - Rule score    | |
|   |  - NumPy bounds   |    |  - Anomaly report |   |  - Factor audit  | |
|   |  - Seed control   |    |  - Quality score  |   |  - Category map  | |
|   +-------------------+    +-------------------+   +------------------+ |
|                                                                         |
|   +-------------------+    +-------------------+   +------------------+ |
|   |   analytics.py    |    |    ml_model.py    |   |    export.py     | |
|   |  - Plotly graphs  |    |  - Random Forest  |   |  - CSV streamer  | |
|   |  - KPI aggregator |    |  - Metrics & CM   |   |  - JSON streamer | |
|   |  - Text insights  |    |  - Feature import |   |  - Report bytes  | |
|   +-------------------+    +-------------------+   +------------------+ |
+------------------------------------+------------------------------------+
                                     |
                                     | Config & Constants
                                     v
+-------------------------------------------------------------------------+
|                               config.py                                 |
|   - App metadata, defaults, bounds, color palette tokens, weights       |
+-------------------------------------------------------------------------+
```

---

## 2. Directory Structure and Responsibilities
- `app.py`: Entry point for Streamlit. Sets page config, loads CSS tokens, and serves the Home Dashboard.
- `config.py`: Single source of truth for numeric ranges, default weights, color codes, and export configurations.
- `pages/`: Streamlit's multi-page directory where each page script defines its user controls and reactive updates.
- `src/generator.py`: Generates synthetic student cohorts using bounded normal distributions and latent profiles.
- `src/validation.py`: Pure verification module; never mutates data; outputs structured validation dictionaries.
- `src/risk_engine.py`: Implements deterministic risk calculations and isolates rule-based heuristics from ML models.
- `src/analytics.py`: Encapsulates Plotly chart creation with consistent themes and computes statistical insights.
- `src/ml_model.py`: Implements machine learning workflows with strict leakage prevention.
- `src/export.py`: Handles in-memory binary encoding of datasets and quality reports for instant browser download.
- `assets/style.css`: Modern visual styling (rounded metric cards, subtle shadows, clean font families).
- `tests/`: Comprehensive Pytest automated test suite.
