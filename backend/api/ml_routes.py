"""
backend/api/ml_routes.py — API endpoints for Scikit-learn Random Forest ML demonstration.
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from src.ml_model import train_risk_classifier, FEATURE_COLUMNS
from backend.services import cohort_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


class MLTrainRequest(BaseModel):
    n_estimators: int = Field(default=config.ML_N_ESTIMATORS, ge=10, le=300)
    test_size: float = Field(default=config.ML_TEST_SIZE, ge=0.10, le=0.40)
    random_state: int = Field(default=config.ML_RANDOM_STATE, ge=0)


@router.post("/train")
def train_model(req: MLTrainRequest) -> Dict[str, Any]:
    """Train Random Forest classifier on active synthetic cohort and return evaluation metrics."""
    df, meta = cohort_service.get_cohort()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No active cohort found. Generate a dataset first.")

    if len(df) < 50:
        raise HTTPException(status_code=400, detail="Cohort must contain at least 50 students for ML benchmarking.")

    result = train_risk_classifier(
        df,
        test_size=req.test_size,
        n_estimators=req.n_estimators,
        random_state=req.random_state,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Format feature importance into JSON-serializable structure
    fi_df = result["feature_importance"]
    feature_importance_list = [
        {"feature": row["feature"], "importance": round(float(row["importance"]), 4)}
        for _, row in fi_df.iterrows()
    ]

    # Convert confusion matrix to list of lists
    cm_list = result["confusion_matrix"].tolist()

    return {
        "status": "success",
        "notice": (
            "Synthetic-Data Benchmark: Evaluated on synthetically generated student records "
            "with deterministic risk rules. Does not imply real-world predictive validity."
        ),
        "train_size": result["train_size"],
        "test_size": result["test_size"],
        "n_estimators": result["n_estimators"],
        "feature_columns": result["feature_columns"],
        "accuracy": result["accuracy"],
        "precision_macro": result["precision_macro"],
        "recall_macro": result["recall_macro"],
        "f1_macro": result["f1_macro"],
        "class_names": result["class_names"],
        "confusion_matrix": cm_list,
        "feature_importance": feature_importance_list,
        "classification_report": result["classification_report"],
    }
