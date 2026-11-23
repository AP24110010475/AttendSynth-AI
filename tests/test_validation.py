"""
tests/test_validation.py — Unit tests for the data validation module.
"""

import pytest
import pandas as pd
import numpy as np
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.generator import generate_dataset
from src.validation import validate_dataset
import config


@pytest.fixture(scope="module")
def clean_df():
    return generate_dataset(n_students=200, seed=42)


# ---------------------------------------------------------------------------
# 1. Clean dataset passes all checks
# ---------------------------------------------------------------------------

def test_clean_dataset_passes_all_checks(clean_df):
    result = validate_dataset(clean_df)
    assert result["passed_all"] is True


def test_clean_dataset_quality_100(clean_df):
    result = validate_dataset(clean_df)
    assert result["quality_pct"] == 100.0


def test_clean_dataset_no_invalid(clean_df):
    result = validate_dataset(clean_df)
    assert result["invalid_records"] == 0


# ---------------------------------------------------------------------------
# 2. Empty DataFrame handling
# ---------------------------------------------------------------------------

def test_empty_df_returns_zero_quality():
    result = validate_dataset(pd.DataFrame())
    assert result["total_records"] == 0
    assert result["quality_pct"] == 0.0
    assert result["passed_all"] is False


def test_none_df_handled():
    result = validate_dataset(None)
    assert result["total_records"] == 0


# ---------------------------------------------------------------------------
# 3. Injected errors are caught
# ---------------------------------------------------------------------------

def test_detects_invalid_attendance(clean_df):
    df_bad = clean_df.copy()
    df_bad.loc[0, "attendance_percentage"] = 150.0   # > 100
    result = validate_dataset(df_bad)
    # At least the attendance range check should fail
    att_check = next(c for c in result["checks"] if "Attendance % Range" in c["check"])
    assert att_check["passed"] is False


def test_detects_invalid_engagement(clean_df):
    df_bad = clean_df.copy()
    df_bad.loc[0, "engagement_score"] = -5.0
    result = validate_dataset(df_bad)
    eng_check = next(c for c in result["checks"] if "Engagement Score" in c["check"])
    assert eng_check["passed"] is False


def test_detects_duplicate_ids(clean_df):
    df_bad = clean_df.copy()
    df_bad.loc[1, "student_id"] = df_bad.loc[0, "student_id"]   # inject dupe
    result = validate_dataset(df_bad)
    dupe_check = next(c for c in result["checks"] if "Duplicate" in c["check"])
    assert dupe_check["passed"] is False


def test_detects_classes_exceeded(clean_df):
    df_bad = clean_df.copy()
    df_bad.loc[0, "classes_attended"] = df_bad.loc[0, "total_classes"] + 10
    result = validate_dataset(df_bad)
    cls_check = next(c for c in result["checks"] if "Classes Attended" in c["check"])
    assert cls_check["passed"] is False


def test_detects_invalid_risk_category(clean_df):
    df_bad = clean_df.copy()
    df_bad.loc[0, "risk_category"] = "Critical"   # invalid category
    result = validate_dataset(df_bad)
    risk_check = next(c for c in result["checks"] if "Risk Categories" in c["check"])
    assert risk_check["passed"] is False


# ---------------------------------------------------------------------------
# 4. Summary structure
# ---------------------------------------------------------------------------

def test_summary_keys_present(clean_df):
    result = validate_dataset(clean_df)
    for key in ["total_records", "valid_records", "invalid_records",
                "missing_values", "quality_pct", "passed_all"]:
        assert key in result["summary"]


def test_checks_list_non_empty(clean_df):
    result = validate_dataset(clean_df)
    assert len(result["checks"]) > 0
