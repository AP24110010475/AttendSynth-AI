"""
pages/5_Machine_Learning.py — ML Demonstration page for AttendSynth AI.
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header, render_kpi_card, render_empty_dataset_state
from src.ml_model import train_risk_classifier, FEATURE_COLUMNS

st.set_page_config(page_title=f"Machine Learning | {config.APP_TITLE}", page_icon="🤖", layout="wide")
load_styles()
render_sidebar("Machine Learning")

render_page_header(
    "Machine Learning Demonstration",
    "Synthetic-data classification benchmark using a Scikit-learn Random Forest model.",
)

df: pd.DataFrame | None = st.session_state.get("df")
if df is None or df.empty:
    render_empty_dataset_state()
    st.stop()

st.warning(
    "Synthetic-Data Evaluation Notice: This classifier is trained on synthetically generated "
    "student records whose risk labels derive from deterministic rules. Performance metrics reflect "
    "synthetic pattern adherence and do not establish real-world predictive accuracy."
)

if len(df) < 50:
    st.error("Dataset must contain at least 50 records for the machine learning demonstration.")
    st.stop()

# ---------------------------------------------------------------------------
# Model Information & Training Configuration Card
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("#### Model Information & Training Settings")
    c_info, c_ctrl = st.columns([1.2, 1.8])

    with c_info:
        st.markdown(
            f"""
            - **Algorithm:** Random Forest Classifier (`class_weight="balanced"`)
            - **Prediction Target:** `risk_category` (`Low`, `Medium`, `High`)
            - **Input Features ({len(FEATURE_COLUMNS)}):** `{'`, `'.join(FEATURE_COLUMNS)}`
            - **Target Leakage Guard:** `risk_score` is strictly excluded from inputs.
            """
        )

    with c_ctrl:
        p1, p2, p3 = st.columns(3)
        with p1:
            n_trees = st.slider("Number of Trees", 10, 300, config.ML_N_ESTIMATORS, 10)
        with p2:
            test_split = st.slider("Test Split (%)", 10, 40, 25, 5)
        with p3:
            ml_seed = st.number_input("Random Seed", 0, 99999, config.ML_RANDOM_STATE)

        train_btn = st.button(
            "Train Random Forest Classifier",
            type="primary",
            icon=":material/play_arrow:",
            use_container_width=True,
        )

if train_btn:
    with st.spinner("Training Random Forest on synthetic cohort..."):
        result = train_risk_classifier(
            df,
            test_size=test_split / 100,
            n_estimators=int(n_trees),
            random_state=int(ml_seed),
        )
    st.session_state["ml_result"] = result

# ---------------------------------------------------------------------------
# Results Dashboard
# ---------------------------------------------------------------------------
result = st.session_state.get("ml_result")

if result is None:
    st.info("Configure hyperparameters above and click **Train Random Forest Classifier** to view evaluation metrics.")
elif "error" in result:
    st.error(result["error"])
else:
    st.success(
        f"Synthetic-data evaluation complete · Trained on **{result['train_size']:,}** records, "
        f"tested on **{result['test_size']:,}** records ({result['n_estimators']} trees)."
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Accuracy (Synthetic)", f"{result['accuracy']}%", "Overall test accuracy", "🎯", "#3B82F6", "rgba(59,130,246,0.10)")
    with m2:
        render_kpi_card("Precision (Macro)", f"{result['precision_macro']}%", "Macro-averaged precision", "✓", "#14B8A6", "rgba(20,184,166,0.10)")
    with m3:
        render_kpi_card("Recall (Macro)", f"{result['recall_macro']}%", "Macro-averaged recall", "↻", "#60A5FA", "rgba(96,165,250,0.12)")
    with m4:
        render_kpi_card("F1-Score (Macro)", f"{result['f1_macro']}%", "Balanced precision & recall", "⚖️", "#10B981", "rgba(16,185,129,0.10)")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        with st.container(border=True):
            cm    = result["confusion_matrix"]
            names = result["class_names"]
            fig_cm = px.imshow(
                cm,
                labels=dict(x="Predicted Label", y="True Label", color="Count"),
                x=names,
                y=names,
                color_continuous_scale=["#EFF6FF", "#3B82F6"],
                text_auto=True,
                title="Confusion Matrix (Synthetic Test Set)",
            )
            fig_cm.update_layout(
                height=360,
                template=config.CHART_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title=dict(font=dict(size=15, color="#111827"), x=0.01),
                margin=dict(l=16, r=16, t=48, b=16),
            )
            st.plotly_chart(fig_cm, use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            fi_df = result["feature_importance"].sort_values("importance", ascending=True)
            fig_fi = px.bar(
                fi_df,
                x="importance",
                y="feature",
                orientation="h",
                color_discrete_sequence=[config.COLOUR_PRIMARY],
                labels={"importance": "Relative Importance", "feature": "Feature"},
                title="Feature Importance (Random Forest)",
            )
            fig_fi.update_layout(
                height=360,
                template=config.CHART_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title=dict(font=dict(size=15, color="#111827"), x=0.01),
                margin=dict(l=16, r=16, t=48, b=16),
                xaxis=dict(gridcolor="#F3F4F6", zeroline=False),
                yaxis=dict(showgrid=False),
                showlegend=False,
            )
            st.plotly_chart(fig_fi, use_container_width=True)

    with st.expander("Per-Class Classification Report"):
        report_dict = result["classification_report"]
        rows = []
        for label in result["class_names"]:
            r = report_dict.get(label, {})
            rows.append({
                "Risk Class": label,
                "Precision":  f"{r.get('precision', 0) * 100:.1f}%",
                "Recall":     f"{r.get('recall', 0) * 100:.1f}%",
                "F1-Score":   f"{r.get('f1-score', 0) * 100:.1f}%",
                "Support":    int(r.get("support", 0)),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Model Limitations & Synthetic Evaluation Notes"):
        st.markdown(
            """
            - **Synthetic Training Bias:** Patterns learned come from statistical generation rules rather than real student behavior.
            - **Rule Alignment:** High accuracy is expected because risk categories are derived from the underlying attributes.
            - **No Real-World Generalization:** Real institutional deployments require validation against historical student outcomes and ethical oversight.
            """
        )
