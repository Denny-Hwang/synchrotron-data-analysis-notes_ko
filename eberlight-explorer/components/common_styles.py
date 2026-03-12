"""모든 페이지에 주입되는 공유 CSS 스타일."""

import streamlit as st

COMMON_CSS = """
<style>
    .block-container { padding-top: 1.5rem; }
    h1 { color: #0A1628; font-size: 2.4rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }

    /* Body text larger */
    .stMarkdown p, .stMarkdown li { font-size: 1.08rem; line-height: 1.7; }

    /* Metric cards */
    .stMetric > div { background: #E8EEF6; padding: 12px; border-radius: 8px; }

    /* Expanders */
    div[data-testid="stExpander"] { border: 1px solid #E8EEF6; border-radius: 8px; }
    div[data-testid="stExpander"] summary { font-size: 1.15rem; font-weight: 600; }

    /* Bullet list styling */
    .stMarkdown ul { padding-left: 1.4em; }
    .stMarkdown ul li { margin-bottom: 0.35em; }
    .stMarkdown ul li::marker { color: #00D4AA; font-size: 1.1em; }

    /* Tables */
    .stDataFrame { font-size: 1.02rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] > div { padding-top: 1rem; }
    section[data-testid="stSidebar"] .stMarkdown p { font-size: 1.0rem; }
    section[data-testid="stSidebar"] h4 { font-size: 1.1rem !important; margin-bottom: 0.3rem; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 1.05rem; }

    /* Captions a bit bigger */
    .stCaption, .stMarkdown small { font-size: 0.92rem !important; }

    /* Info boxes */
    .stAlert p { font-size: 1.05rem; }

    /* Tabs */
    button[data-baseweb="tab"] { font-size: 1.05rem; }

    /* Container spacing */
    div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    /* Prevent diagram/figure clipping in iframes and expanders */
    iframe { border: none; }
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] { overflow: visible; }
    .stMarkdown img, .stImage img { max-width: 100%; height: auto; }
</style>
"""


def inject_styles():
    st.markdown(COMMON_CSS, unsafe_allow_html=True)
