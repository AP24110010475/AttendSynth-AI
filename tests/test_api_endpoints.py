"""
tests/test_api_endpoints.py — Comprehensive integration tests for FastAPI backend routes.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "active_cohort" in data
    assert "gemini_ai" in data


def test_generator_defaults_endpoint():
    res = client.get("/api/generator/defaults")
    assert res.status_code == 200
    data = res.json()
    assert "default_n_students" in data
    assert "default_departments" in data


def test_generate_endpoint_success():
    payload = {
        "n_students": 75,
        "academic_year": "2024-25",
        "semester": "Odd",
        "departments": ["CS", "ECE"],
        "seed": 99,
        "auto_validate": True,
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["kpis"]["total_students"] == 75
    assert len(data["sample_records"]) == 5


def test_generate_endpoint_validation_error():
    # Less than minimum 50 students
    payload = {
        "n_students": 10,
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 422  # Unprocessable Entity via Pydantic


def test_dataset_explorer_endpoint():
    # Ensure a cohort exists
    client.post("/api/generate", json={"n_students": 60, "seed": 42})

    res = client.get("/api/dataset?page=1&page_size=15")
    assert res.status_code == 200
    data = res.json()
    assert data["has_cohort"] is True
    assert len(data["records"]) == 15
    assert data["total_cohort"] == 60


def test_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["has_cohort"] is True
    assert "kpis" in data
    assert "charts" in data
    assert "attendance_histogram" in data["charts"]


def test_risk_analysis_endpoint():
    res = client.get("/api/risk")
    assert res.status_code == 200
    data = res.json()
    assert data["has_cohort"] is True
    assert "distribution" in data
    assert "formula_info" in data


def test_student_risk_factor_endpoint():
    # Get a valid student ID from dataset
    dataset_res = client.get("/api/dataset?page_size=1")
    student_id = dataset_res.json()["records"][0]["student_id"]

    res = client.get(f"/api/risk/student/{student_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["student"]["student_id"] == student_id
    assert "contributing_factors" in data
    assert "formula_breakdown" in data


def test_student_risk_factor_not_found():
    res = client.get("/api/risk/student/UNKNOWN_NONEXISTENT_ID")
    assert res.status_code == 404


def test_ml_train_endpoint():
    payload = {
        "n_estimators": 20,
        "test_size": 0.25,
        "random_state": 42,
    }
    res = client.post("/api/ml/train", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "accuracy" in data
    assert "confusion_matrix" in data
    assert "feature_importance" in data


def test_data_quality_endpoint():
    res = client.get("/api/quality")
    assert res.status_code == 200
    data = res.json()
    assert data["has_cohort"] is True
    assert len(data["checks"]) == 11
    assert data["quality_pct"] >= 95.0


def test_export_endpoints():
    res_csv = client.get("/api/export/csv")
    assert res_csv.status_code == 200
    assert res_csv.headers["content-type"].startswith("text/csv")

    res_json = client.get("/api/export/json")
    assert res_json.status_code == 200
    assert res_json.headers["content-type"].startswith("application/json")

    res_q_csv = client.get("/api/export/quality/csv")
    assert res_q_csv.status_code == 200

    res_q_json = client.get("/api/export/quality/json")
    assert res_q_json.status_code == 200


def test_ai_status_endpoint():
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_configured" in data
    assert data["model"] == "gemini-3.8-flash"


def test_ai_analyze_endpoint_mocked():
    mock_response = MagicMock()
    mock_response.text = "Grounded AI Analysis Summary: Cohort attendance is strong."
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("backend.services.ai_service._get_genai_client", return_value=(mock_client, "gemini-3.8-flash")):
        res = client.post("/api/ai/analyze")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "Grounded AI Analysis Summary" in data["analysis"]
