"""
src/ui.py — Shared UI components for AttendSynth AI's SaaS dashboard design.

Provides consistent CSS loading, dark navy sidebar navigation,
clean page headers, KPI cards, and empty-state prompts across all pages.
"""

from __future__ import annotations
import os
import streamlit as st
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV_ITEMS = [
    ("Overview",         "app.py",                        ":material/dashboard:"),
    ("Data Generator",   "pages/1_Generator.py",          ":material/tune:"),
    ("Dataset Explorer", "pages/2_Dataset_Explorer.py",   ":material/table_view:"),
    ("Analytics",        "pages/3_Analytics.py",          ":material/bar_chart:"),
    ("Early Warning",    "pages/4_Early_Warning.py",      ":material/warning:"),
    ("Machine Learning", "pages/5_Machine_Learning.py",   ":material/psychology:"),
    ("Data Quality",     "pages/6_Data_Quality.py",       ":material/verified:"),
    ("Export Center",    "pages/7_Export_Center.py",      ":material/download:"),
    ("AI Assistant",     "pages/9_AI_Assistant.py",       ":material/smart_toy:"),
    ("About",            "pages/8_About.py",              ":material/info:"),
]


def load_styles() -> None:
    """Inject the custom SaaS CSS stylesheet."""
    css_path = os.path.join(ROOT, "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar(active_label: str) -> None:
    """
    Render the dark navy sidebar with branding, custom navigation links,
    and active dataset status.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.25rem 0.5rem 0.75rem 0.5rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;">
                    AttendSynth AI
                </div>
                <div style="font-size: 0.78rem; color: #9CA3AF; margin-top: 2px;">
                    Synthetic Data Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<hr>", unsafe_allow_html=True)

        for label, page_path, icon in NAV_ITEMS:
            is_active = (label == active_label)
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            st.page_link(page_path, label=label, icon=icon, use_container_width=True)
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        df: pd.DataFrame | None = st.session_state.get("df")
        st.markdown("<hr>", unsafe_allow_html=True)
        if df is not None:
            seed = st.session_state.get("generation_seed", "—")
            year = st.session_state.get("generation_year", "—")
            st.markdown(
                f"""
                <div style="background:#1F2937; border:1px solid #374151; border-radius:10px; padding:0.85rem 0.9rem;">
                    <div style="font-size:0.72rem; font-weight:600; color:#60A5FA; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">
                        Active Dataset
                    </div>
                    <div style="font-size:0.85rem; color:#F9FAFB; font-weight:600;">
                        {len(df):,} Students
                    </div>
                    <div style="font-size:0.78rem; color:#9CA3AF; margin-top:2px;">
                        Seed: {seed} &middot; {year}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:#1F2937; border:1px solid #374151; border-radius:10px; padding:0.85rem 0.9rem;">
                    <div style="font-size:0.72rem; font-weight:600; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">
                        No Active Dataset
                    </div>
                    <div style="font-size:0.78rem; color:#9CA3AF;">
                        Open Data Generator to create a cohort.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_page_header(title: str, subtitle: str) -> None:
    """Render a clean, minimal SaaS page header."""
    st.markdown(
        f"""
        <div class="saas-header">
            <h1 class="saas-header-title">{title}</h1>
            <p class="saas-header-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    title: str,
    value: str,
    subtitle: str,
    icon: str,
    accent_color: str = "#3B82F6",
    icon_bg: str = "rgba(59, 130, 246, 0.1)",
) -> None:
    """Render a clean SaaS KPI card with icon, metric value, and explanatory subtitle."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-title">{title}</span>
                <span class="kpi-icon" style="background:{icon_bg}; color:{accent_color};">{icon}</span>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_dataset_state() -> None:
    """Render a clean empty state when no dataset is loaded in session state."""
    with st.container(border=True):
        st.markdown("#### No Dataset Generated Yet")
        st.markdown(
            "Generate a synthetic student engagement cohort first to unlock analytics, "
            "early-warning risk scoring, machine learning, and exports."
        )
        if st.button("Open Data Generator", type="primary", icon=":material/tune:"):
            st.switch_page("pages/1_Generator.py")
