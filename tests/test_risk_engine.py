"""
tests/test_risk_engine.py — Unit tests for the rule-based risk engine and exports.
"""

import pytest
import pandas as pd
import numpy as np
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.generator import generate_dataset
from src.risk_engine import (
    summarise_risk_distribution,
    get_high_risk_students,
    get_risk_insights,
    get_contributing_factors,
)
from src.export import to_csv_bytes, to_json_bytes
import config


@pytest.fixture(scope="module")
def df():
    return generate_dataset(n_students=300, seed=42)


# ---------------------------------------------------------------------------
# 1. Risk distribution summary
# ---------------------------------------------------------------------------

def test_risk_distribution_keys(df):
    dist = summarise_risk_distribution(df)
    for key in ["counts", "percentages", "total", "high_risk_count",
                "medium_risk_count", "low_risk_count"]:
        assert key in dist


def test_risk_distribution_total_matches(df):
    dist = summarise_risk_distribution(df)
    assert dist["total"] == len(df)


def test_risk_distribution_counts_sum(df):
    dist = summarise_risk_distribution(df)
    total_counted = sum(dist["counts"].values())
    assert total_counted == len(df)


# ---------------------------------------------------------------------------
# 2. High-risk filter
# ---------------------------------------------------------------------------

def test_high_risk_all_high(df):
    hr = get_high_risk_students(df)
    assert (hr["risk_category"] == "High").all()


def test_high_risk_is_subset(df):
    hr = get_high_risk_students(df)
    assert len(hr) <= len(df)


# ---------------------------------------------------------------------------
# 3. Risk insights
# ---------------------------------------------------------------------------

def test_risk_insights_non_empty(df):
    insights = get_risk_insights(df)
    assert isinstance(insights, list)
    assert len(insights) > 0


def test_risk_insights_are_strings(df):
    for insight in get_risk_insights(df):
        assert isinstance(insight, str)


# ---------------------------------------------------------------------------
# 4. Contributing factors
# ---------------------------------------------------------------------------

def test_contributing_factors_list(df):
    row = df.iloc[0]
    factors = get_contributing_factors(row)
    assert isinstance(factors, list)
    assert len(factors) >= 1


def test_contributing_factors_all_strings(df):
    row = df.iloc[0]
    for f in get_contributing_factors(row):
        assert isinstance(f, str)


# ---------------------------------------------------------------------------
# 5. Risk category thresholds
# ---------------------------------------------------------------------------

def test_low_risk_scores_below_threshold(df):
    low_risk = df[df["risk_category"] == "Low"]
    assert (low_risk["risk_score"] < config.RISK_LOW_MAX).all()


def test_high_risk_scores_above_threshold(df):
    high_risk = df[df["risk_category"] == "High"]
    assert (high_risk["risk_score"] >= config.RISK_MEDIUM_MAX).all()


# ---------------------------------------------------------------------------
# 6. Export — CSV
# ---------------------------------------------------------------------------

def test_csv_export_returns_bytes(df):
    result = to_csv_bytes(df)
    assert isinstance(result, bytes)


def test_csv_export_non_empty(df):
    result = to_csv_bytes(df)
    assert len(result) > 0


def test_csv_export_contains_header(df):
    result = to_csv_bytes(df)
    header_line = result.decode("utf-8").splitlines()[0]
    assert "student_id" in header_line


def test_csv_export_row_count(df):
    result = to_csv_bytes(df)
    lines = result.decode("utf-8").strip().splitlines()
    # Header + data rows
    assert len(lines) == len(df) + 1


# ---------------------------------------------------------------------------
# 7. Export — JSON
# ---------------------------------------------------------------------------

def test_json_export_returns_bytes(df):
    result = to_json_bytes(df)
    assert isinstance(result, bytes)


def test_json_export_valid_json(df):
    import json
    result = to_json_bytes(df)
    parsed = json.loads(result.decode("utf-8"))
    assert isinstance(parsed, list)
    assert len(parsed) == len(df)


def test_json_export_contains_student_id(df):
    import json
    result = to_json_bytes(df)
    parsed = json.loads(result.decode("utf-8"))
    assert "student_id" in parsed[0]


# ---------------------------------------------------------------------------
# 8. Empty dataset export
# ---------------------------------------------------------------------------

def test_csv_empty_df():
    empty = pd.DataFrame()
    result = to_csv_bytes(empty)
    assert isinstance(result, bytes)


def test_json_empty_df():
    empty = pd.DataFrame()
    result = to_json_bytes(empty)
    assert isinstance(result, bytes)
