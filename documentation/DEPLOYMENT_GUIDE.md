# AttendSynth AI — Deployment & Configuration Guide

This guide covers local environment setup, Google Gemini API key configuration, automated testing, and cloud deployment using Render.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.14)
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/AttendSynth-AI.git
   cd "AttendSynth AI"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   PORT=8000
   ```

5. **Run the Application:**
   ```bash
   python backend/main.py
   # Or with uvicorn:
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Open your browser at:
   - **Web Application Dashboard:** `http://localhost:8000`
   - **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
   - **Alternative ReDoc API Docs:** `http://localhost:8000/redoc`

---

## 2. Google Gemini API Configuration

AttendSynth AI integrates with **Google Gemini 3.8 Flash** via the official `google-genai` Python SDK to provide:
1. **AI Dataset Analysis:** Grounded multi-dimensional executive overview.
2. **Support Recommendations:** Actionable academic interventions.
3. **Cohort Chatbot:** Natural language dataset querying.
4. **AI Institutional Report:** Formal Markdown assessment report.
5. **Student Risk Explanation:** Counselor-level individual risk factor plan.

### Obtaining a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API key**.
4. Copy the key into your `.env` file as `GEMINI_API_KEY`.

### Security Note
- The API key is loaded securely in the Python backend via `backend/services/ai_service.py`.
- **The API key is never exposed to the frontend JavaScript.**
- All Gemini queries are strictly grounded on calculated Python statistics to eliminate hallucinations.
- If no key is set, the UI gracefully displays configuration guidance without crashing.

---

## 3. Running Automated Tests

AttendSynth AI includes a full Pytest suite covering generation math, bounds, ML pipelines, API endpoints, and mocked Gemini responses:

```bash
python -m pytest tests/ -v
```

All 82 tests run without requiring a paid Gemini API key.

---

## 4. Deploying to Render

[Render](https://render.com) is the recommended deployment platform for AttendSynth AI because it natively supports FastAPI and serves static frontend assets simultaneously.

### Step-by-Step Render Deployment

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Upgrade to full-stack FastAPI and Gemini AI"
   git push origin main
   ```

2. **Create a Web Service on Render:**
   - Log into [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository.

3. **Configure the Web Service Settings:**
   - **Name:** `attendsynth-ai`
   - **Region:** Choose the region nearest to your users.
   - **Branch:** `main`
   - **Root Directory:** Leave blank (root).
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```

4. **Set Environment Variables on Render:**
   Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `GEMINI_MODEL`: `gemini-3.8-flash`
   - `PYTHONUNBUFFERED`: `1`

5. **Deploy:**
   - Click **Create Web Service**.
   - Render will build the environment, run the service, and provide an HTTPS URL (e.g., `https://attendsynth-ai.onrender.com`).
   - The root URL `/` automatically serves the responsive dashboard, and `/api/*` serves the REST API.
