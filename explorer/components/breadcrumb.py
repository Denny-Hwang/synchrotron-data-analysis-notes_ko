"""Breadcrumb navigation component for eBERlight Explorer.

Renders a horizontal breadcrumb bar showing the user's position in
the information architecture. Each segment except the last is a
clickable link.

Ref: IA-001 (information_architecture.md) — Navigation rules.
Ref: DS-001 (design_system.md) — Breadcrumb component spec.
Ref: FR-005 — Breadcrumb on every detail view.
"""

import streamlit as st


def render_breadcrumb(items: list[tuple[str, str | None]]) -> None:
    """Render a breadcrumb navigation bar.

    Produces an HTML breadcrumb via st.markdown with each item as a
    clickable link except the last (current page, rendered as bold
    plain text).

    Args:
        items: List of (label, href) tuples. If href is None, the
            item is rendered as the current page (not linked).
    """
    if not items:
        return

    parts: list[str] = []
    for label, href in items:
        if href is not None:
            parts.append(f'<a href="{href}">{label}</a>')
        else:
            parts.append(f'<span class="current">{label}</span>')

    separator = '<span class="separator">&gt;</span>'
    breadcrumb_html = (
        f'<nav class="eberlight-breadcrumb" aria-label="Breadcrumb">'
        f'{separator.join(parts)}'
        f'</nav>'
    )
    st.markdown(breadcrumb_html, unsafe_allow_html=True)
