"""
tests/test_ai_service.py — Unit tests for Gemini AI Academic Insights Assistant service.
Uses unittest.mock to test mocked Gemini API responses without paid network calls,
and verifies graceful handling when GEMINI_API_KEY is unconfigured.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services import ai_service
from src.generator import generate_dataset


@pytest.fixture
def sample_cohort():
    return generate_dataset(n_students=60, seed=42)


def test_ai_status_unconfigured(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    status = ai_service.get_gemini_config()
    assert status["is_configured"] is False
    assert status["model"] == "gemini-3.8-flash"


def test_dataset_analysis_unconfigured(sample_cohort, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    res = ai_service.generate_dataset_analysis(sample_cohort, {"academic_year": "2024-25", "semester": "Odd"})
    assert res["status"] == "unconfigured"
    assert "Gemini API key is not configured" in res["message"]
    assert res["stats"]["total_students"] == 60


def test_chatbot_unconfigured(sample_cohort, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    res = ai_service.chatbot_query("What is the average attendance?", sample_cohort)
    assert res["status"] == "unconfigured"
    assert "Gemini API key is not configured" in res["message"]


def test_chatbot_empty_query(sample_cohort):
    res = ai_service.chatbot_query("   ", sample_cohort)
    assert res["status"] == "error"


def test_dataset_analysis_mocked(sample_cohort, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "mock_fake_api_key_for_testing")

    mock_response = MagicMock()
    mock_response.text = "### Executive Overview\nThe cohort exhibits strong attendance."

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("backend.services.ai_service._get_genai_client", return_value=(mock_client, "gemini-3.8-flash")):
        res = ai_service.generate_dataset_analysis(sample_cohort, {"academic_year": "2024-25", "semester": "Odd"})
        assert res["status"] == "success"
        assert res["model"] == "gemini-3.8-flash"
        assert "Institutional Advisory Notice" in res["analysis"]
        assert "The cohort exhibits strong attendance." in res["analysis"]


def test_chatbot_mocked(sample_cohort, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "mock_fake_api_key_for_testing")

    mock_response = MagicMock()
    mock_response.text = "Computer Science has the highest average attendance at 78.5%."

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("backend.services.ai_service._get_genai_client", return_value=(mock_client, "gemini-3.8-flash")):
        res = ai_service.chatbot_query("Which department has the highest attendance?", sample_cohort)
        assert res["status"] == "success"
        assert "Computer Science" in res["reply"]


def test_student_risk_explanation_mocked(sample_cohort, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "mock_fake_api_key_for_testing")

    mock_response = MagicMock()
    mock_response.text = "This student requires targeted tutoring in assignment completion."

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    student_dict = sample_cohort.iloc[0].to_dict()

    with patch("backend.services.ai_service._get_genai_client", return_value=(mock_client, "gemini-3.8-flash")):
        res = ai_service.explain_student_risk(student_dict)
        assert res["status"] == "success"
        assert res["student_id"] == student_dict["student_id"]
        assert len(res["calculated_factors"]) > 0
        assert "This student requires targeted tutoring" in res["explanation"]
