"""Card component for eBERlight Explorer.

Renders a navigation card for cluster pages, showing title, summary,
and tags. Used on landing and cluster landing pages.

Ref: DS-001 (design_system.md) — Card component spec.
Ref: FR-003 — Cluster pages list notes as cards.
"""

import streamlit as st


def render_card(title: str, summary: str, tags: list[str], href: str = "#") -> None:
    """Render a content card with title, summary, and tags.

    Args:
        title: Card title (H4).
        summary: Brief description (max ~2 lines).
        tags: List of tag labels to display as chips.
        href: Link URL for the card title.
    """
    tags_html = "".join(f'<span class="eberlight-tag">{tag}</span>' for tag in tags[:5])

    card_html = f"""
    <div class="eberlight-card" style="margin-bottom: 16px;">
        <h4 style="margin: 0 0 8px 0;">
            <a href="{href}" style="color: #1A1A1A; text-decoration: none;">{title}</a>
        </h4>
        <p style="font-size: 14px; color: #555555; margin: 0 0 12px 0;
                  display: -webkit-box; -webkit-line-clamp: 2;
                  -webkit-box-orient: vertical; overflow: hidden;">
            {summary}
        </p>
        <div>{tags_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
