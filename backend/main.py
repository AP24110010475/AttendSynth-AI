"""
backend/main.py — FastAPI application entry point for AttendSynth AI.

Connects REST API routers, manages startup database initialization,
serves HTML/CSS/JavaScript frontend assets, and provides health monitoring.
"""

from __future__ import annotations
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    # Manual lightweight .env loader
    env_file = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

import config
from backend.services import cohort_service, ai_service
from backend.api import (
    generator_routes,
    analytics_routes,
    risk_routes,
    ml_routes,
    quality_routes,
    export_routes,
    ai_routes,
)

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite DB is initialized
    cohort_service.init_db()

    # If no cohort exists in DB, generate default cohort so dashboard opens ready
    if not cohort_service.has_cohort():
        from src.generator import generate_dataset
        default_df = generate_dataset(
            n_students=config.DEFAULT_N_STUDENTS,
            departments=config.DEFAULT_DEPARTMENTS,
            academic_year=config.DEFAULT_ACADEMIC_YEAR,
            semester=config.DEFAULT_SEMESTER,
            attendance_distribution=config.DEFAULT_ATTENDANCE_DISTRIBUTION,
            seed=config.DEFAULT_SEED,
        )
        cohort_service.save_cohort(default_df, {
            "n_students": config.DEFAULT_N_STUDENTS,
            "academic_year": config.DEFAULT_ACADEMIC_YEAR,
            "semester": config.DEFAULT_SEMESTER,
            "departments": config.DEFAULT_DEPARTMENTS,
            "attendance_distribution": config.DEFAULT_ATTENDANCE_DISTRIBUTION,
            "seed": config.DEFAULT_SEED,
        })
    yield
    # Shutdown logic if any


app = FastAPI(
    title=f"{config.APP_TITLE} API",
    description="Backend REST API and Generative AI service for AttendSynth AI synthetic student platform.",
    version=config.APP_VERSION,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(generator_routes.router)
app.include_router(analytics_routes.router)
app.include_router(risk_routes.router)
app.include_router(ml_routes.router)
app.include_router(quality_routes.router)
app.include_router(export_routes.router)
app.include_router(ai_routes.router)


@app.get("/api/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint providing application state and AI configuration status."""
    has_active = cohort_service.has_cohort()
    df, meta = cohort_service.get_cohort() if has_active else (None, None)
    gemini_status = ai_service.get_gemini_config()

    return {
        "status": "healthy",
        "app_title": config.APP_TITLE,
        "version": config.APP_VERSION,
        "active_cohort": {
            "loaded": has_active,
            "student_count": len(df) if df is not None else 0,
            "academic_year": meta.get("academic_year") if meta else None,
            "seed": meta.get("seed") if meta else None,
        },
        "gemini_ai": {
            "is_configured": gemini_status["is_configured"],
            "model": gemini_status["model"],
        },
    }


# Static and Frontend File Serving
if os.path.exists(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    pages_dir = os.path.join(FRONTEND_DIR, "pages")

    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir), name="pages")

    @app.get("/", include_in_schema=False)
    def serve_index():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": f"{config.APP_TITLE} API is running."})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
