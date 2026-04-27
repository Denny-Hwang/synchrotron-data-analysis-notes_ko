"""eBERlight Explorer — Main application entry point.

A Streamlit-based interactive portal over synchrotron-data-analysis-notes,
aligned with ANL/APS design standards.

Ref: PRD-001 — Product Requirements Document.
Ref: ADR-001 — Choose Streamlit.
Ref: DS-001 — Design system tokens.
Ref: FR-001 — Landing page with hero, search, 3 cluster cards.
"""

from pathlib import Path

import streamlit as st

from components.breadcrumb import render_breadcrumb
from components.footer import render_footer
from components.header import render_header
from lib.ia import CLUSTER_META

# --- Page Config ---
st.set_page_config(
    page_title="eBERlight Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Load Custom CSS ---
_CSS_PATH = Path(__file__).parent / "assets" / "styles.css"
if _CSS_PATH.exists():
    st.markdown(f"<style>{_CSS_PATH.read_text()}</style>", unsafe_allow_html=True)

# --- Header ---
render_header()

# --- Breadcrumb ---
render_breadcrumb([("Home", None)])

# --- Hero ---
st.markdown(
    """
    <div style="text-align: center; padding: 48px 0;">
        <h1 style="color: #0033A0; font-size: 36px; margin-bottom: 12px;">
            eBERlight Research Explorer
        </h1>
        <p style="color: #555555; font-size: 18px; max-width: 600px; margin: 0 auto;">
            Navigate synchrotron data analysis knowledge at
            Argonne's Advanced Photon Source
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Cluster Cards ---
cols = st.columns(3)
cluster_order = ["discover", "explore", "build"]
cluster_pages = {"discover": "1_Discover", "explore": "2_Explore", "build": "3_Build"}

for col, cluster_id in zip(cols, cluster_order):
    meta = CLUSTER_META[cluster_id]
    with col:
        st.markdown(
            f"""
            <div class="eberlight-card" style="border-top: 4px solid {meta['color']}; min-height: 200px;">
                <h4 style="color: {meta['color']}; margin: 0 0 12px 0;">{meta['name']}</h4>
                <p style="font-size: 14px; color: #555555; margin: 0 0 16px 0;">{meta['description']}</p>
                <span style="color: {meta['color']}; font-weight: 600; font-size: 15px;">Enter →</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Footer ---
render_footer()
