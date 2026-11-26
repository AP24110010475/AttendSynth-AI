# AttendSynth AI — Synthetic Student Engagement Platform & AI Insights Assistant

![AttendSynth AI](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-3.8--flash-8E24AA)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-green)

> **AttendSynth AI** is a professional full-stack educational web application and synthetic data platform. It pairs a statistically grounded synthetic student data generation engine with **Google Gemini 3.8 Flash** Generative AI and **Scikit-learn** machine learning to prototype, test, and audit academic early-warning systems without handling confidential student Personally Identifiable Information (PII).

---

## 📑 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Quickstart & Local Execution](#quickstart--local-execution)
6. [Generative AI Integration](#generative-ai-integration)
7. [REST API Documentation](#rest-api-documentation)
8. [Automated Testing](#automated-testing)
9. [Render Cloud Deployment](#render-cloud-deployment)
10. [Ethical Guidelines & Privacy](#ethical-guidelines--privacy)

---

## 1. Architecture Overview

AttendSynth AI is built on a clean decoupled full-stack architecture:
- **Frontend Presentation Layer:** Pure HTML5, CSS3, ES6+ JavaScript, Bootstrap 5, and Chart.js.
- **Backend Service Layer:** FastAPI asynchronous REST API, SQLite cross-request cohort persistence, and Pydantic schema validation.
- **Data & Statistical Layer:** NumPy, Pandas, Faker, and Scikit-learn for synthetic behavioral generation and Random Forest benchmarking.
- **Generative AI Layer:** Official Google GenAI Python SDK (`google-genai`) driving **Gemini 3.8 Flash** with strict factual grounding on calculated Python statistics.

---

## 2. Key Features

### 1. Synthetic Data Generator
- Configurable cohort size (50 – 10,000 students).
- Dynamic academic term, semester, and department list.
- Prior behavioral distribution controls (Regular, Moderate, Irregular, Low).
- Reproducible synthesis via random seed control.
- Immediate 11-point data quality verification.

### 2. Dataset Explorer
- Full-text search by Student ID.
- Multi-dimensional filters (Department, Year of Study, Semester, Risk Category).
- Client-side and server-side pagination with custom page sizes.
- Detailed student factor inspection modal with deterministic formula calculations.
- Cohort descriptive statistics summary.

### 3. Analytics Dashboard
- 5 Cohort KPIs (Total Students, Mean Attendance, Engagement, Academic Score, High Risk %).
- Automated cohort observations derived directly from data.
- 8 Chart.js interactive visualizations:
  - Attendance, Engagement, and Academic Score histograms.
  - Departmental average attendance rankings.
  - Donut risk category distribution.
  - Attendance vs. Engagement correlation scatter plot.
  - Engagement level tiers (Low, Medium, High) stacked by department.

### 4. Early-Warning Risk Engine
- Transparent, deterministic rule-based scoring (strictly marked as non-ML heuristic):
  $$\text{risk\_score} = 100 - (0.35 \times \text{att} + 0.25 \times \text{eng} + 0.25 \times \text{asgn} + 0.15 \times \text{acad})$$
- Categorical risk boundaries: Low ($<35$), Medium ($35\text{--}59$), High ($\ge 60$).
- Filtered high-risk student audit table with individualized contributing factors.

### 5. Machine Learning Demonstration
- Supervised classification benchmark using Scikit-learn's Random Forest.
- Strict target leakage avoidance (`risk_score` excluded from features).
- Configurable ensemble size (trees), test split, and seed.
- Confusion matrix heatmap and Gini feature importance bar chart.
- Complete per-class precision, recall, f1-score report.

### 6. Data Quality Audit
- Automated 11-point deterministic audit covering missing values, duplicate IDs, boundary constraints ($0\text{--}100\%$), physical class count validity ($\text{classes attended} \le \text{total classes}$), and categorical integrity.
- Attribute-level completeness analysis.

### 7. Export Center
- In-memory CSV and JSON downloads for full cohorts, filtered explorer subsets, and data quality reports.

### 8. AI Academic Insights Assistant (Google Gemini 3.8 Flash)
- **AI Dataset Analysis:** Grounded multi-dimensional analytical breakdown.
- **Support Recommendations:** Actionable academic interventions.
- **Natural Language Cohort Chatbot:** Freeform conversational Q&A answering questions like:
  - *"Which department has the highest average attendance?"*
  - *"How many students belong to the high-risk category?"*
  - *"Suggest interventions for high-risk students."*
- **Formal AI Cohort Report:** Comprehensive Markdown evaluation report with copy-to-clipboard functionality.
- **Student Risk Explanation:** Personalized academic counseling plan for individual students.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4, Markdown-it |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **Generative AI** | Google Gemini API (`gemini-3.8-flash`), Google GenAI Python SDK (`google-genai`) |
| **Machine Learning & Stats** | Scikit-learn, NumPy, Pandas, Faker |
| **Persistence** | SQLite (thread-safe cohort & metadata caching) |
| **Testing** | Pytest, FastAPI TestClient, unittest.mock |
| **Deployment** | Render Cloud, Uvicorn ASGI |

---

## 4. Project Structure

```text
AttendSynth AI/
├── backend/
│   ├── main.py                     # FastAPI application & asset mounting
│   ├── requirements.txt            # Backend dependencies
│   ├── api/
│   │   ├── generator_routes.py     # Data generation endpoints
│   │   ├── analytics_routes.py     # Explorer & analytics endpoints
│   │   ├── risk_routes.py          # Early warning risk endpoints
│   │   ├── ml_routes.py            # Random Forest ML training endpoints
│   │   ├── quality_routes.py       # 11-point quality audit endpoints
│   │   ├── export_routes.py        # CSV/JSON file download endpoints
│   │   └── ai_routes.py            # Google Gemini AI endpoints
│   └── services/
│       ├── cohort_service.py       # SQLite persistence & caching service
│       └── ai_service.py           # Gemini 3.8 Flash orchestration & grounding
│
├── frontend/
│   ├── index.html                  # Overview dashboard
│   ├── pages/
│   │   ├── generator.html          # Synthetic Data Generator page
│   │   ├── explorer.html           # Dataset Explorer page
│   │   ├── analytics.html          # Analytics Dashboard page
│   │   ├── early-warning.html      # Early Warning Analysis page
│   │   ├── machine-learning.html   # Machine Learning page
│   │   ├── data-quality.html       # Data Quality Report page
│   │   ├── export.html             # Export Center page
│   │   ├── ai-assistant.html       # AI Academic Assistant page
│   │   └── about.html              # About & methodology page
│   ├── css/
│   │   ├── style.css               # Modern academic dashboard stylesheet
│   │   └── responsive.css          # Mobile and tablet layouts
│   └── js/
│       ├── app.js                  # Shared UI, mobile toggle, toasts
│       ├── api.js                  # Centralized Fetch API client
│       ├── generator.js            # Generator controller
│       ├── explorer.js             # Explorer & modal controller
│       ├── analytics.js            # Chart.js analytics controller
│       ├── risk.js                 # Risk charts & audit controller
│       ├── ml.js                   # ML benchmarking controller
│       ├── quality.js              # Data quality audit controller
│       ├── export.js               # Export center controller
│       └── ai-assistant.js         # Gemini chat & analysis controller
│
├── src/                            # Preserved core business logic
│   ├── generator.py                # Synthetic generation logic
│   ├── validation.py               # 11-point data validation suite
│   ├── analytics.py                # Analytics & KPI calculators
│   ├── risk_engine.py              # Heuristic risk calculation
│   ├── ml_model.py                 # Random Forest pipeline
│   └── export.py                   # In-memory byte serializers
│
├── tests/                          # 82 automated unit & integration tests
│   ├── test_generator.py
│   ├── test_validation.py
│   ├── test_risk_engine.py
│   ├── test_ml_model.py
│   ├── test_cohort_service.py
│   ├── test_ai_service.py
│   └── test_api_endpoints.py
│
├── documentation/
│   ├── DEPLOYMENT_GUIDE.md         # Local & Render deployment guide
│   ├── DATA_GENERATION.md          # Statistical methodology
│   ├── PROJECT_OVERVIEW.md         # Comprehensive project documentation
│   └── SYSTEM_ARCHITECTURE.md      # Architecture diagrams & contracts
│
├── config.py                       # App constants, defaults, and boundaries
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── requirements.txt                # Unified Python requirements
└── DEVELOPMENT_LOG.md              # Phase-by-phase development record
```

---

## 5. Quickstart & Local Execution

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/your-username/AttendSynth-AI.git
cd "AttendSynth AI"
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to include your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
```
*(Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey). The platform runs fully even without a key; AI features will display helpful setup notices).*

### 3. Start the Server
```bash
python backend/main.py
# Or with uvicorn:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to **`http://localhost:8000`** in your browser.

---

## 6. Generative AI Integration

- **Model:** `gemini-3.8-flash` via the official `google-genai` Python SDK.
- **Grounding Guarantee:** All AI prompts are populated with computed Python summary statistics. The model is instructed to cite only the calculated truth to prevent hallucinations.
- **Security:** The API key is securely handled by the backend service and **is never exposed in frontend code**.
- **Transparency:** All AI outputs include institutional disclaimers stating suggestions are advisory.

---

## 7. REST API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Key Endpoints:
- `GET  /api/health` — System status, cohort metrics, and Gemini configuration.
- `POST /api/generate` — Generate and persist a synthetic student dataset.
- `GET  /api/dataset` — Query, filter, and paginate student records.
- `GET  /api/analytics` — Compute KPIs, insights, and Chart.js distributions.
- `GET  /api/risk` — Early warning risk analysis and high-risk cohort list.
- `POST /api/ml/train` — Train Random Forest model and return evaluation metrics.
- `GET  /api/quality` — Execute 11-point data quality audit.
- `GET  /api/export/csv` & `GET /api/export/json` — Download full or filtered cohort files.
- `POST /api/ai/analyze` — Generate comprehensive AI dataset analysis.
- `POST /api/ai/chat` — Conversational natural language chatbot.
- `POST /api/ai/recommend` — Generate institutional support recommendations.
- `POST /api/ai/report` — Compile structured formal cohort report.
- `POST /api/ai/explain-student` — Individual student risk counseling evaluation.

---

## 8. Automated Testing

Run the complete test suite:
```bash
python -m pytest tests/ -v
```
All **82 test cases** execute locally in under 6 seconds, using mocked Gemini responses so paid API calls are never required during test runs.

---

## 9. Render Cloud Deployment

AttendSynth AI is pre-configured for frictionless deployment to [Render](https://render.com):
1. Push repository to GitHub.
2. In Render, select **New + Web Service** and select your repository.
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variable `GEMINI_API_KEY` to your Gemini API key.
5. Deploy. Render will serve both the REST API and the frontend dashboard.

---

## 10. Ethical Guidelines & Privacy

1. **Zero Real Student PII:** All names, IDs, attendance records, and assessments are 100% synthetically generated.
2. **Deterministic Heuristic Transparency:** The rule-based early warning formula is explicitly separated from the Random Forest ML classifier.
3. **Advisory AI Boundaries:** Generative AI outputs are labeled as decision-support suggestions for simulated academic environments.
