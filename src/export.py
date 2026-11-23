"""
export.py — Data export helpers for AttendSynth AI.

Converts DataFrames to bytes for Streamlit download buttons.
"""

from __future__ import annotations
import pandas as pd
import json
import io
from typing import Optional


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Return a UTF-8 encoded CSV byte string of the DataFrame."""
    return df.to_csv(index=False).encode("utf-8")


def to_json_bytes(df: pd.DataFrame) -> bytes:
    """Return a UTF-8 encoded JSON byte string (records orientation)."""
    records = df.to_dict(orient="records")
    return json.dumps(records, indent=2, default=str).encode("utf-8")


def quality_report_to_csv_bytes(validation_result: dict) -> bytes:
    """
    Convert the validation report dict into a downloadable CSV.
    One row per check, with columns: check, passed, count, detail.
    """
    rows = []
    for c in validation_result.get("checks", []):
        rows.append({
            "check":   c["check"],
            "passed":  c["passed"],
            "count":   c["count"],
            "detail":  str(c.get("detail", "")),
        })
    summary = validation_result.get("summary", {})
    # Add summary rows
    for k, v in summary.items():
        rows.append({
            "check":  f"SUMMARY: {k}",
            "passed": "",
            "count":  v,
            "detail": "",
        })
    df_report = pd.DataFrame(rows)
    return df_report.to_csv(index=False).encode("utf-8")


def quality_report_to_json_bytes(validation_result: dict) -> bytes:
    """Return the full validation result as a JSON byte string."""
    # Make it JSON-serialisable
    safe = json.loads(json.dumps(validation_result, default=str))
    return json.dumps(safe, indent=2).encode("utf-8")
