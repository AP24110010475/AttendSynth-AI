"""
tests/test_ml_model.py — Unit tests for machine learning demonstration pipeline.
"""

import pytest
import pandas as pd
import numpy as np
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.generator import generate_dataset
from src.ml_model import train_risk_classifier, FEATURE_COLUMNS, TARGET_COLUMN


@pytest.fixture(scope="module")
def sample_df():
    return generate_dataset(n_students=150, seed=42)


def test_ml_pipeline_success(sample_df):
    result = train_risk_classifier(sample_df, test_size=0.2, n_estimators=20, random_state=42)
    assert "error" not in result
    assert "model" in result
    assert result["accuracy"] >= 0.0 and result["accuracy"] <= 100.0
    assert result["f1_macro"] >= 0.0 and result["f1_macro"] <= 100.0
    assert result["precision_macro"] >= 0.0 and result["precision_macro"] <= 100.0
    assert result["recall_macro"] >= 0.0 and result["recall_macro"] <= 100.0


def test_target_leakage_prevention():
    """Ensure risk_score is NOT in feature columns."""
    assert "risk_score" not in FEATURE_COLUMNS
    assert "risk_category" not in FEATURE_COLUMNS


def test_feature_importance_format(sample_df):
    result = train_risk_classifier(sample_df, test_size=0.2, n_estimators=10, random_state=42)
    fi = result["feature_importance"]
    assert isinstance(fi, pd.DataFrame)
    assert "feature" in fi.columns
    assert "importance" in fi.columns
    assert len(fi) == len(FEATURE_COLUMNS)
    assert np.isclose(fi["importance"].sum(), 1.0, atol=1e-3)


def test_confusion_matrix_shape(sample_df):
    result = train_risk_classifier(sample_df, test_size=0.2, n_estimators=10, random_state=42)
    cm = result["confusion_matrix"]
    classes = result["class_names"]
    assert cm.shape == (len(classes), len(classes))


def test_small_dataset_handled():
    tiny_df = pd.DataFrame({"a": [1, 2]})
    result = train_risk_classifier(tiny_df)
    assert "error" in result
