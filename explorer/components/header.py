"""Header component for eBERlight Explorer.

Renders the site header with logo placeholder, title, and top navigation.
Navigation links to the 3 clusters are stubs (disabled) in Phase A.

Ref: DS-001 (design_system.md) — Header component spec.
Ref: FR-011 — Header with site title and top navigation.
"""

import streamlit as st


def render_header() -> None:
    """Render the site header with logo, title, and navigation stub.

    Displays a horizontal bar with the eBERlight logo placeholder,
    site title, and links to the three task clusters. In Phase A,
    cluster links are disabled (rendered as non-interactive).
    """
    header_html = """
    <div class="eberlight-header">
        <div class="eberlight-header-brand">
            <div class="eberlight-header-logo">eB</div>
            <span class="eberlight-header-title">eBERlight Explorer</span>
        </div>
        <nav class="eberlight-header-nav" aria-label="Main navigation">
            <a href="#">Discover</a>
            <a href="#">Explore</a>
            <a href="#">Build</a>
        </nav>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
