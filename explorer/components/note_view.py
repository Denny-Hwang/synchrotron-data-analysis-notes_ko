"""Note detail view component for eBERlight Explorer.

Renders a single note: breadcrumb, title, markdown body, and a
right-side metadata panel with tags, modality, and beamline info.

Ref: DS-001 (design_system.md) — MetadataPanel, CodeBlock specs.
Ref: FR-004 — Note detail view renders markdown.
Ref: FR-006 — Metadata panel with beamline/modality tags.
Ref: FR-013 — Code blocks with syntax highlighting.
"""

import markdown
import streamlit as st
from pygments.formatters import HtmlFormatter

from .breadcrumb import render_breadcrumb


def render_note_view(
    title: str,
    body: str,
    cluster_name: str,
    tags: list[str],
    modality: str | None,
    beamline: list[str],
    related_publications: list[str],
    related_tools: list[str],
) -> None:
    """Render a full note detail view with metadata panel.

    Args:
        title: Note title.
        body: Markdown body content.
        cluster_name: Human-readable cluster name for breadcrumb.
        tags: List of tag labels.
        modality: Modality value or None.
        beamline: List of beamline identifiers.
        related_publications: List of related publication filenames.
        related_tools: List of related tool names.
    """
    # Breadcrumb
    render_breadcrumb([
        ("Home", "/"),
        (cluster_name, "#"),
        (title, None),
    ])

    # Two-column layout: main content + metadata panel
    col_main, col_meta = st.columns([3, 1])

    with col_main:
        st.markdown(f"# {title}")

        # Render markdown with code highlighting
        formatter = HtmlFormatter(style="monokai", noclasses=True)
        highlight_css = formatter.get_style_defs(".highlight")

        html_body = markdown.markdown(
            body,
            extensions=["fenced_code", "tables", "toc", "codehilite"],
            extension_configs={
                "codehilite": {"css_class": "highlight", "linenums": False}
            },
        )

        st.markdown(
            f"<style>{highlight_css}</style>{html_body}",
            unsafe_allow_html=True,
        )

    with col_meta:
        _render_metadata_panel(tags, modality, beamline, related_publications, related_tools)


def _render_metadata_panel(
    tags: list[str],
    modality: str | None,
    beamline: list[str],
    related_publications: list[str],
    related_tools: list[str],
) -> None:
    """Render the right-side metadata panel."""
    sections: list[str] = []

    if beamline:
        badges = " ".join(
            f'<span style="background:#0033A0;color:white;padding:4px 12px;'
            f'border-radius:12px;font-size:12px;font-weight:600;">{bl}</span>'
            for bl in beamline
        )
        sections.append(
            f'<div style="margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;color:#555;margin-bottom:8px;">Beamlines</div>'
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;">{badges}</div></div>'
        )

    if modality:
        sections.append(
            f'<div style="margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;color:#555;margin-bottom:8px;">Modality</div>'
            f'<span class="eberlight-tag">{modality}</span></div>'
        )

    if tags:
        tags_html = " ".join(f'<span class="eberlight-tag">{t}</span>' for t in tags)
        sections.append(
            f'<div style="margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;color:#555;margin-bottom:8px;">Tags</div>'
            f'<div>{tags_html}</div></div>'
        )

    if related_publications:
        links = "".join(
            f'<div style="font-size:14px;color:#0033A0;margin-bottom:4px;">{p}</div>'
            for p in related_publications
        )
        sections.append(
            f'<div style="margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;color:#555;margin-bottom:8px;">Publications</div>'
            f'{links}</div>'
        )

    if related_tools:
        links = "".join(
            f'<div style="font-size:14px;color:#0033A0;margin-bottom:4px;">{t}</div>'
            for t in related_tools
        )
        sections.append(
            f'<div style="margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;color:#555;margin-bottom:8px;">Related Tools</div>'
            f'{links}</div>'
        )

    if sections:
        panel_html = (
            '<aside aria-label="Note metadata" style="background:#FFFFFF;'
            'border:1px solid #E0E0E0;border-radius:8px;padding:24px;">'
            + "".join(sections)
            + "</aside>"
        )
        st.markdown(panel_html, unsafe_allow_html=True)
