"""
pages/9_AI_Assistant.py — Gemini AI Academic Insights Assistant for AttendSynth AI.

Provides five AI features powered by Google Gemini, grounded strictly on
the actual computed cohort statistics (no hallucinations):

  Tab 1 — 💬 AI Chatbot         : Natural language Q&A about the dataset
  Tab 2 — 📊 Dataset Analysis   : Full AI cohort analysis
  Tab 3 — 🎯 Recommendations    : Targeted student support strategies
  Tab 4 — 📝 Cohort Report      : Formal institutional-grade report
  Tab 5 — 👤 Student Explainer  : Individual student risk explanation
"""

import os
import sys
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from src.ui import load_styles, render_sidebar, render_page_header

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=f"AI Assistant | {config.APP_TITLE}",
    page_icon="🤖",
    layout="wide",
)
load_styles()
render_sidebar("AI Assistant")

render_page_header(
    "AI Academic Insights Assistant",
    "Powered by Google Gemini — grounded exclusively on your generated cohort statistics.",
)

# ---------------------------------------------------------------------------
# Helper: load AI service (lazy, so Streamlit can run without backend deps)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _load_ai_service():
    """Import ai_service only once per session."""
    try:
        from backend.services import ai_service
        return ai_service
    except ImportError:
        return None


def _get_df_and_meta():
    """Return (df, meta) from session state, or (None, None)."""
    df = st.session_state.get("df")
    meta = st.session_state.get("generation_meta", {})
    return df, meta


def _status_badge(result: dict) -> None:
    """Show a coloured badge based on AI result status."""
    s = result.get("status", "")
    if s == "success":
        model = result.get("model", "gemini")
        st.success(f"✅ Gemini AI response generated  |  Model: `{model}`", icon="🤖")
    elif s == "unconfigured":
        st.warning(result.get("message", "API key not configured."), icon="🔑")
    elif s == "error":
        st.error(result.get("message", "An error occurred."), icon="❌")


def _api_key_sidebar():
    """Allow user to set Gemini API key in sidebar for this session."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔑 Gemini API Key")
        key_in_env = bool(os.environ.get("GEMINI_API_KEY", "").strip())
        if key_in_env:
            st.success("API key loaded from environment ✅")
        else:
            user_key = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                placeholder="AIza...",
                help="Your key is only stored in this browser session. Get one at aistudio.google.com",
            )
            if user_key.strip():
                os.environ["GEMINI_API_KEY"] = user_key.strip()
                st.success("API key set for this session ✅")
        st.caption("[Get a free API key →](https://aistudio.google.com/app/apikey)")


# ---------------------------------------------------------------------------
# Draw sidebar API key widget
# ---------------------------------------------------------------------------
_api_key_sidebar()

# ---------------------------------------------------------------------------
# Guard: dataset must be generated first
# ---------------------------------------------------------------------------
df, meta = _get_df_and_meta()

if df is None or df.empty:
    st.info(
        "⚠️ **No dataset loaded yet.**  \n"
        "Go to **Data Generator** and generate a cohort first, "
        "then return here for AI-powered academic insights.",
        icon="📊",
    )
    if st.button("Go to Data Generator →", type="primary"):
        st.switch_page("pages/1_Generator.py")
    st.stop()

# ---------------------------------------------------------------------------
# AI service guard
# ---------------------------------------------------------------------------
ai = _load_ai_service()
if ai is None:
    st.error(
        "Could not import the AI service module.  \n"
        "Make sure `backend/services/ai_service.py` exists in the project root.",
        icon="🚨",
    )
    st.stop()

# ---------------------------------------------------------------------------
# KPI banner — show cohort snapshot at top
# ---------------------------------------------------------------------------
from src.analytics import compute_kpis
kpi = compute_kpis(df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Students", f"{kpi['total_students']:,}")
k2.metric("📅 Avg Attendance", f"{kpi['avg_attendance']}%")
k3.metric("⚠️ High Risk", f"{kpi['high_risk_count']:,}")
k4.metric("💡 Avg Engagement", f"{kpi['avg_engagement']}/100")

st.markdown("---")

# ---------------------------------------------------------------------------
# 5 AI Feature Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 AI Chatbot",
    "📊 Dataset Analysis",
    "🎯 Recommendations",
    "📝 Cohort Report",
    "👤 Student Explainer",
])


# ── TAB 1: AI CHATBOT ──────────────────────────────────────────────────────
with tab1:
    st.markdown("#### 💬 Natural Language Dataset Chatbot")
    st.caption(
        "Ask anything about your cohort — attendance patterns, risk distribution, "
        "department breakdowns, correlations, or recommendations."
    )

    # Initialise chat history in session state
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # Display message history
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested starter questions
    if not st.session_state.ai_chat_history:
        st.markdown("**💡 Try asking:**")
        starter_cols = st.columns(2)
        starters = [
            "Which department has the highest attendance?",
            "How many students are at high risk?",
            "What is the correlation between attendance and engagement?",
            "Suggest interventions for low-performing students.",
        ]
        for i, q in enumerate(starters):
            if starter_cols[i % 2].button(q, key=f"starter_{i}"):
                st.session_state.ai_chat_history.append({"role": "user", "content": q})
                with st.spinner("Gemini is thinking..."):
                    result = ai.chatbot_query(
                        q, df, meta,
                        conversation_history=st.session_state.ai_chat_history[:-1],
                    )
                reply = result.get("reply") or result.get("message", "No response.")
                st.session_state.ai_chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask about your cohort..."):
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Gemini is thinking..."):
                result = ai.chatbot_query(
                    prompt, df, meta,
                    conversation_history=st.session_state.ai_chat_history[:-1],
                )
            if result["status"] == "success":
                st.markdown(result["reply"])
                st.session_state.ai_chat_history.append(
                    {"role": "assistant", "content": result["reply"]}
                )
            else:
                msg = result.get("message", "An error occurred.")
                st.warning(msg, icon="⚠️")
                st.session_state.ai_chat_history.append(
                    {"role": "assistant", "content": f"⚠️ {msg}"}
                )

    # Clear chat button
    if st.session_state.ai_chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.ai_chat_history = []
            st.rerun()


# ── TAB 2: DATASET ANALYSIS ────────────────────────────────────────────────
with tab2:
    st.markdown("#### 📊 AI Dataset Analysis")
    st.caption(
        "Gemini performs a full structured analysis of your cohort: attendance dynamics, "
        "engagement patterns, departmental disparities, and risk vulnerabilities."
    )

    if st.button("🔍 Generate AI Analysis", type="primary", key="btn_analysis"):
        with st.spinner("Gemini is analyzing your cohort..."):
            result = ai.generate_dataset_analysis(df, meta)

        _status_badge(result)

        if result.get("analysis"):
            with st.expander("📈 Computed Statistics Used for Grounding", expanded=False):
                st.json(result["stats"])
            st.markdown("---")
            st.markdown(result["analysis"])
        elif result.get("message"):
            st.warning(result["message"])


# ── TAB 3: RECOMMENDATIONS ─────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🎯 AI Student Support Recommendations")
    st.caption(
        "Data-driven, actionable academic interventions tailored to your cohort's "
        "risk profile, department metrics, and engagement gaps."
    )

    if st.button("💡 Generate Recommendations", type="primary", key="btn_recs"):
        with st.spinner("Gemini is crafting targeted interventions..."):
            result = ai.generate_support_recommendations(df, meta)

        _status_badge(result)

        if result.get("recommendations"):
            with st.expander("📈 Computed Statistics Used for Grounding", expanded=False):
                st.json(result["stats"])
            st.markdown("---")
            st.markdown(result["recommendations"])
        elif result.get("message"):
            st.warning(result["message"])


# ── TAB 4: COHORT REPORT ───────────────────────────────────────────────────
with tab4:
    st.markdown("#### 📝 Full AI Cohort Report")
    st.caption(
        "Generates a formal, institutional-grade Markdown report covering all aspects "
        "of your synthetic cohort — suitable for academic submissions or presentations."
    )

    if st.button("📄 Generate Full Report", type="primary", key="btn_report"):
        with st.spinner("Gemini is writing your cohort report..."):
            result = ai.generate_cohort_report(df, meta)

        _status_badge(result)

        if result.get("report"):
            with st.expander("📈 Computed Statistics Used for Grounding", expanded=False):
                st.json(result["stats"])
            st.markdown("---")
            st.markdown(result["report"])

            # Download button for the report
            st.download_button(
                label="⬇️ Download Report as Markdown",
                data=result["report"],
                file_name="attendsynth_ai_cohort_report.md",
                mime="text/markdown",
                key="download_report",
            )
        elif result.get("message"):
            st.warning(result["message"])


# ── TAB 5: STUDENT EXPLAINER ───────────────────────────────────────────────
with tab5:
    st.markdown("#### 👤 Individual Student Risk Explainer")
    st.caption(
        "Select a student from your cohort and get a detailed AI explanation of "
        "their risk factors, with a personalised academic counselling plan."
    )

    # Student selector
    student_ids = df["student_id"].tolist() if "student_id" in df.columns else []
    if not student_ids:
        st.warning("No student_id column found in dataset.", icon="⚠️")
    else:
        # Let user filter by risk category first
        risk_filter = st.selectbox(
            "Filter by Risk Category",
            ["All", "High", "Medium", "Low"],
            key="student_risk_filter",
        )

        filtered_df = df if risk_filter == "All" else df[df["risk_category"] == risk_filter]

        if filtered_df.empty:
            st.info(f"No {risk_filter} risk students in this cohort.")
        else:
            selected_id = st.selectbox(
                f"Select Student ({len(filtered_df)} available)",
                filtered_df["student_id"].tolist(),
                key="selected_student_id",
            )

            student_row = filtered_df[filtered_df["student_id"] == selected_id].iloc[0]
            student_dict = student_row.to_dict()

            # Show student summary card
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🎓 Department", student_dict.get("department", "N/A"))
                c2.metric("📅 Attendance", f"{student_dict.get('attendance_percentage', 0):.1f}%")
                c3.metric("⚠️ Risk", student_dict.get("risk_category", "N/A"))
                c4.metric("🏆 Academic Score", f"{student_dict.get('academic_performance_score', 0):.1f}/100")

                d1, d2, d3 = st.columns(3)
                d1.metric("💡 Engagement", f"{student_dict.get('engagement_score', 0):.1f}/100")
                d2.metric("📝 Assignment Completion", f"{student_dict.get('assignment_completion_percentage', 0):.1f}%")
                d3.metric("🔢 Risk Score", f"{student_dict.get('risk_score', 0):.1f}/100")

            if st.button("🤖 Explain Risk & Generate Counselling Plan", type="primary", key="btn_explain"):
                with st.spinner(f"Gemini is analyzing student {selected_id}..."):
                    result = ai.explain_student_risk(student_dict)

                _status_badge(result)

                if result.get("calculated_factors"):
                    with st.expander("🔎 Deterministic Risk Flags (Python-Computed)", expanded=True):
                        for flag in result["calculated_factors"]:
                            severity_color = "🔴" if "high" in flag.lower() or "low" in flag.lower() else "🟡"
                            st.markdown(f"{severity_color} {flag}")

                if result.get("explanation"):
                    st.markdown("---")
                    st.markdown(result["explanation"])
                elif result.get("message"):
                    st.warning(result["message"])

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f"<div style='text-align:center; color:#9CA3AF; font-size:0.8rem; margin-top:2rem;'>"
    f"AttendSynth AI v{config.APP_VERSION} &middot; AI features powered by Google Gemini"
    f"</div>",
    unsafe_allow_html=True,
)
