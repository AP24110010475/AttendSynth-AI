"""
tests/test_generator.py — Unit tests for the synthetic data generation engine.
"""

import pytest
import pandas as pd
import numpy as np
import sys, os

# Ensure root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.generator import generate_dataset
import config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def small_df():
    """Small fixed-seed dataset for fast tests."""
    return generate_dataset(n_students=100, seed=42)


@pytest.fixture(scope="module")
def large_df():
    """Larger dataset to test edge cases."""
    return generate_dataset(n_students=500, seed=99)


# ---------------------------------------------------------------------------
# 1. Basic generation
# ---------------------------------------------------------------------------

def test_generate_returns_dataframe(small_df):
    assert isinstance(small_df, pd.DataFrame)


def test_correct_number_of_rows(small_df):
    assert len(small_df) == 100


def test_required_columns_present(small_df):
    required = [
        "student_id", "age", "department", "academic_year", "semester",
        "total_classes", "classes_attended", "attendance_percentage",
        "assignment_completion_percentage", "learning_platform_activity",
        "participation_score", "engagement_score",
        "academic_performance_score", "risk_score", "risk_category",
    ]
    for col in required:
        assert col in small_df.columns, f"Missing column: {col}"


# ---------------------------------------------------------------------------
# 2. Reproducibility
# ---------------------------------------------------------------------------

def test_reproducibility_same_seed():
    df1 = generate_dataset(n_students=50, seed=7)
    df2 = generate_dataset(n_students=50, seed=7)
    pd.testing.assert_frame_equal(df1, df2)


def test_different_seed_different_data():
    df1 = generate_dataset(n_students=50, seed=1)
    df2 = generate_dataset(n_students=50, seed=2)
    # At least some attendance values should differ
    assert not df1["attendance_percentage"].equals(df2["attendance_percentage"])


# ---------------------------------------------------------------------------
# 3. Unique IDs
# ---------------------------------------------------------------------------

def test_unique_student_ids(small_df):
    assert small_df["student_id"].is_unique, "Duplicate student IDs found"


def test_student_id_format(small_df):
    assert small_df["student_id"].str.startswith("STU-").all()


# ---------------------------------------------------------------------------
# 4. Attendance range
# ---------------------------------------------------------------------------

def test_attendance_pct_range(small_df):
    assert (small_df["attendance_percentage"] >= 0).all()
    assert (small_df["attendance_percentage"] <= 100).all()


def test_attendance_pct_range_large(large_df):
    assert (large_df["attendance_percentage"] >= 0).all()
    assert (large_df["attendance_percentage"] <= 100).all()


# ---------------------------------------------------------------------------
# 5. Classes attended never exceed total
# ---------------------------------------------------------------------------

def test_classes_attended_le_total(small_df):
    assert (small_df["classes_attended"] <= small_df["total_classes"]).all()


def test_classes_attended_non_negative(small_df):
    assert (small_df["classes_attended"] >= 0).all()


# ---------------------------------------------------------------------------
# 6. Engagement score range
# ---------------------------------------------------------------------------

def test_engagement_score_range(small_df):
    assert (small_df["engagement_score"] >= 0).all()
    assert (small_df["engagement_score"] <= 100).all()


def test_assignment_completion_range(small_df):
    assert (small_df["assignment_completion_percentage"] >= 0).all()
    assert (small_df["assignment_completion_percentage"] <= 100).all()


# ---------------------------------------------------------------------------
# 7. Academic performance range
# ---------------------------------------------------------------------------

def test_academic_performance_range(small_df):
    assert (small_df["academic_performance_score"] >= 0).all()
    assert (small_df["academic_performance_score"] <= 100).all()


# ---------------------------------------------------------------------------
# 8. Age range
# ---------------------------------------------------------------------------

def test_age_range(small_df):
    lo, hi = config.AGE_RANGE
    assert (small_df["age"] >= lo).all()
    assert (small_df["age"] <= hi).all()


# ---------------------------------------------------------------------------
# 9. Department assignment
# ---------------------------------------------------------------------------

def test_departments_assigned(small_df):
    assert small_df["department"].notna().all()
    for dept in small_df["department"].unique():
        assert dept in config.DEFAULT_DEPARTMENTS


def test_custom_departments():
    custom = ["Physics", "Chemistry"]
    df = generate_dataset(n_students=50, departments=custom, seed=1)
    for dept in df["department"].unique():
        assert dept in custom


# ---------------------------------------------------------------------------
# 10. Risk categories
# ---------------------------------------------------------------------------

def test_risk_categories_valid(small_df):
    assert set(small_df["risk_category"].unique()).issubset(set(config.RISK_CATEGORIES))


def test_risk_score_range(small_df):
    assert (small_df["risk_score"] >= 0).all()
    assert (small_df["risk_score"] <= 100).all()


# ---------------------------------------------------------------------------
# 11. No missing values
# ---------------------------------------------------------------------------

def test_no_missing_values(small_df):
    assert small_df.isnull().sum().sum() == 0


# ---------------------------------------------------------------------------
# 12. Minimum student count clamping
# ---------------------------------------------------------------------------

def test_minimum_students_clamped():
    df = generate_dataset(n_students=5)   # below minimum → clamped to 50
    assert len(df) == 50


def test_maximum_students_clamped():
    df = generate_dataset(n_students=20_000)   # above max → clamped to 10 000
    assert len(df) == 10_000
