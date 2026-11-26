"""
backend/services/cohort_service.py — Cohort management & SQLite persistence service.

Maintains an in-memory cached DataFrame for sub-millisecond API responses
while persisting the active cohort and generation metadata to SQLite so datasets
survive server reboots and multiple worker processes.
"""

from __future__ import annotations
import os
import sys
import json
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config

DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "cohort.db")

_lock = threading.Lock()
_cached_df: Optional[pd.DataFrame] = None
_cached_meta: Optional[Dict[str, Any]] = None


def _get_db_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite schema if not present."""
    with _lock:
        with _get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    academic_year TEXT,
                    semester TEXT,
                    seed INTEGER,
                    n_students INTEGER,
                    departments_json TEXT,
                    attendance_dist_json TEXT,
                    generated_at TEXT
                )
            """)
            conn.commit()


def save_cohort(df: pd.DataFrame, meta: Dict[str, Any]) -> None:
    """Save generated cohort and metadata to SQLite and memory cache."""
    global _cached_df, _cached_meta
    init_db()

    with _lock:
        _cached_df = df.copy()
        _cached_meta = dict(meta)
        if "generated_at" not in _cached_meta:
            _cached_meta["generated_at"] = datetime.now().isoformat()

        with _get_db_connection() as conn:
            # Save DataFrame directly using pandas
            df.to_sql("students", conn, if_exists="replace", index=False)

            # Upsert metadata
            conn.execute("""
                INSERT OR REPLACE INTO metadata (
                    id, academic_year, semester, seed, n_students,
                    departments_json, attendance_dist_json, generated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """, (
                _cached_meta.get("academic_year", config.DEFAULT_ACADEMIC_YEAR),
                _cached_meta.get("semester", config.DEFAULT_SEMESTER),
                int(_cached_meta.get("seed", config.DEFAULT_SEED)),
                len(df),
                json.dumps(_cached_meta.get("departments", config.DEFAULT_DEPARTMENTS)),
                json.dumps(_cached_meta.get("attendance_distribution", config.DEFAULT_ATTENDANCE_DISTRIBUTION)),
                _cached_meta.get("generated_at")
            ))
            conn.commit()


def get_cohort() -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """Retrieve active cohort DataFrame and metadata, loading from SQLite if necessary."""
    global _cached_df, _cached_meta
    with _lock:
        if _cached_df is not None:
            return _cached_df.copy(), dict(_cached_meta or {})

        # Try to load from SQLite
        if not os.path.exists(DB_PATH):
            return None, None

        try:
            with _get_db_connection() as conn:
                meta_row = conn.execute("SELECT * FROM metadata WHERE id = 1").fetchone()
                if meta_row is None:
                    return None, None

                df = pd.read_sql_query("SELECT * FROM students", conn)
                meta = {
                    "academic_year": meta_row["academic_year"],
                    "semester": meta_row["semester"],
                    "seed": meta_row["seed"],
                    "n_students": meta_row["n_students"],
                    "departments": json.loads(meta_row["departments_json"] or "[]"),
                    "attendance_distribution": json.loads(meta_row["attendance_dist_json"] or "{}"),
                    "generated_at": meta_row["generated_at"]
                }
                _cached_df = df.copy()
                _cached_meta = meta
                return df, meta
        except Exception:
            return None, None


def has_cohort() -> bool:
    """Return True if an active cohort is loaded or stored."""
    df, _ = get_cohort()
    return df is not None and not df.empty


def filter_cohort(
    search_id: Optional[str] = None,
    department: Optional[str] = None,
    year_of_study: Optional[str] = None,
    semester: Optional[str] = None,
    risk_category: Optional[str] = None,
) -> pd.DataFrame:
    """Apply search and category filters on the active cohort."""
    df, _ = get_cohort()
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()
    if search_id and search_id.strip():
        filtered = filtered[filtered["student_id"].astype(str).str.contains(search_id.strip(), case=False)]
    if department and department != "All":
        filtered = filtered[filtered["department"] == department]
    if year_of_study and year_of_study != "All":
        filtered = filtered[filtered["year_of_study"] == year_of_study]
    if semester and semester != "All":
        filtered = filtered[filtered["semester"] == semester]
    if risk_category and risk_category != "All":
        filtered = filtered[filtered["risk_category"] == risk_category]

    return filtered


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a single student record by student_id."""
    df, _ = get_cohort()
    if df is None or df.empty:
        return None
    matches = df[df["student_id"].astype(str).str.upper() == student_id.strip().upper()]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def clear_cohort() -> None:
    """Clear memory cache and SQLite records."""
    global _cached_df, _cached_meta
    with _lock:
        _cached_df = None
        _cached_meta = None
        if os.path.exists(DB_PATH):
            try:
                with _get_db_connection() as conn:
                    conn.execute("DROP TABLE IF EXISTS students")
                    conn.execute("DROP TABLE IF EXISTS metadata")
                    conn.commit()
            except Exception:
                pass
