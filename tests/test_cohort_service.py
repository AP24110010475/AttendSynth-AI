"""
tests/test_cohort_service.py — Unit tests for SQLite cohort persistence and caching.
"""

import os
import sys
import pytest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services import cohort_service
from src.generator import generate_dataset


def test_cohort_save_and_retrieve():
    df = generate_dataset(n_students=60, seed=123)
    meta = {
        "n_students": 60,
        "academic_year": "2024-25",
        "semester": "Odd",
        "seed": 123,
    }

    cohort_service.save_cohort(df, meta)
    assert cohort_service.has_cohort() is True

    loaded_df, loaded_meta = cohort_service.get_cohort()
    assert loaded_df is not None
    assert len(loaded_df) == 60
    assert loaded_meta["seed"] == 123
    assert loaded_meta["academic_year"] == "2024-25"


def test_cohort_filtering():
    df = generate_dataset(n_students=100, seed=42)
    cohort_service.save_cohort(df, {"n_students": 100, "seed": 42})

    depts = df["department"].unique().tolist()
    chosen_dept = depts[0]

    filtered = cohort_service.filter_cohort(department=chosen_dept)
    assert not filtered.empty
    assert (filtered["department"] == chosen_dept).all()

    first_id = df.iloc[0]["student_id"]
    single_student = cohort_service.get_student(first_id)
    assert single_student is not None
    assert single_student["student_id"] == first_id

    missing_student = cohort_service.get_student("NONEXISTENT_99999")
    assert missing_student is None
