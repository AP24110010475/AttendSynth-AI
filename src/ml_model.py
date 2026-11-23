"""
ml_model.py — Machine learning demonstration module for AttendSynth AI.

Uses Scikit-learn Random Forest to classify student risk categories.
This module is for DEMONSTRATION purposes only on synthetic data.
Performance here does NOT indicate real-world predictive accuracy.

IMPORTANT: Risk score and risk category are excluded from features
to prevent target leakage.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.preprocessing import LabelEncoder


# Features used for classification — deliberately excludes risk_score / risk_category
FEATURE_COLUMNS: List[str] = [
    "age",
    "attendance_percentage",
    "assignment_completion_percentage",
    "learning_platform_activity",
    "participation_score",
    "engagement_score",
    "academic_performance_score",
]

TARGET_COLUMN = "risk_category"


def _encode_target(series: pd.Series) -> Tuple[np.ndarray, LabelEncoder]:
    le = LabelEncoder()
    encoded = le.fit_transform(series)
    return encoded, le


def train_risk_classifier(
    df: pd.DataFrame,
    test_size: float = config.ML_TEST_SIZE,
    n_estimators: int = config.ML_N_ESTIMATORS,
    random_state: int = config.ML_RANDOM_STATE,
) -> Dict[str, Any]:
    """
    Train a Random Forest classifier on the synthetic dataset.

    Parameters
    ----------
    df : pd.DataFrame
        The generated synthetic dataset.
    test_size : float
        Proportion of data for the test split.
    n_estimators : int
        Number of trees in the forest.
    random_state : int
        Reproducibility seed.

    Returns
    -------
    dict containing model, metrics, feature importances, and predictions.
    """
    if df is None or df.empty or len(df) < 50:
        return {"error": "Dataset too small for ML demonstration (need ≥ 50 records)."}

    # --- Prepare features and target ---
    missing_cols = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        return {"error": f"Missing columns: {missing_cols}"}

    X = df[FEATURE_COLUMNS].copy().fillna(0)
    y_raw = df[TARGET_COLUMN].copy()
    y, le = _encode_target(y_raw)

    # --- Split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # --- Train ---
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    # --- Predict ---
    y_pred = clf.predict(X_test)

    # --- Metrics ---
    labels_ordered = le.transform(le.classes_)   # numeric labels in sorted order
    report = classification_report(
        y_test, y_pred,
        target_names=le.classes_,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_test, y_pred, labels=labels_ordered)

    # Feature importances as a tidy DataFrame
    fi_df = pd.DataFrame({
        "feature":    FEATURE_COLUMNS,
        "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)

    return {
        "model":               clf,
        "label_encoder":       le,
        "feature_columns":     FEATURE_COLUMNS,
        "target_column":       TARGET_COLUMN,
        "accuracy":            round(accuracy_score(y_test, y_pred) * 100, 2),
        "f1_macro":            round(f1_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "precision_macro":     round(precision_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "recall_macro":        round(recall_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "classification_report": report,
        "confusion_matrix":    cm,
        "class_names":         list(le.classes_),
        "feature_importance":  fi_df,
        "train_size":          len(X_train),
        "test_size":           len(X_test),
        "n_estimators":        n_estimators,
    }
