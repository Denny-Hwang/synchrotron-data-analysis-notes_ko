"""Static site generator for eBERlight Explorer — GitHub Pages mirror.

Reads the same note folders and IA mapping the Streamlit explorer uses
(`explorer/lib/ia.py`, `explorer/lib/notes.py`) and emits a fully static
HTML site that mirrors the Streamlit app's pages 1:1:

- Landing (hero + 3 cluster cards)     ← explorer/app.py
- Discover cluster page                ← explorer/pages/1_Discover.py
- Explore cluster page (grouped)       ← explorer/pages/2_Explore.py
- Build cluster page (grouped)         ← explorer/pages/3_Build.py
- Note detail pages (markdown + aside) ← explorer/components/note_view.py

The generator also copies the design wireframes under /wireframes/ so
the existing wireframe preview keeps working.

Ref: ADR-007 — Static site mirror for GitHub Pages.
Ref: DS-001 — Design system tokens (reuses explorer/assets/styles.css).
Ref: IA-001, ADR-004 — 3-cluster IA reused via explorer.lib.ia.
"""

from __future__ import annotations

import argparse
import html as html_escape_mod
import logging
import re
import shutil
import subprocess
import sys
from datetime import datetime
from itertools import groupby
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

_REPO_ROOT = Path(__file__).resolve().parent.parent
_EXPLORER_DIR = _REPO_ROOT / "explorer"
if str(_EXPLORER_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPLORER_DIR))

from lib.ia import CLUSTER_META, FOLDER_TO_CLUSTER, get_folders_for_cluster  # noqa: E402
from lib.notes import Note, load_notes  # noqa: E402

logger = logging.getLogger("build_static_site")

# Cluster → file slug used in URLs.
CLUSTER_SLUG = {"discover": "discover", "explore": "explore", "build": "build"}

# Cluster → target page file path (relative to site root).
CLUSTER_PAGE = {cid: f"clusters/{slug}.html" for cid, slug in CLUSTER_SLUG.items()}

# Cluster → display order on the landing page.
CLUSTER_ORDER = ["discover", "explore", "build"]

SITE_LAYOUT_CSS = """
/* === Static site layout (GitHub Pages mirror) === */
html, body { margin: 0; padding: 0; background: #F5F5F5; }
body {
    font-family: 'Source Sans 3', system-ui, -apple-system, 'Segoe UI',
                 Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: #1A1A1A;
    line-height: 1.6;
}
a { color: #0033A0; }
.site-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px 48px 24px;
}
.site-container.narrow { max-width: 960px; }

/* Re-enable the cluster links on the static site header (Streamlit stubbed them). */
.eberlight-header-nav a {
    pointer-events: auto !important;
    opacity: 1 !important;
}
.eberlight-header-nav a:hover { background: #F5F5F5; }
.eberlight-header-nav a.active {
    color: #0033A0;
    background: rgba(0, 51, 160, 0.08);
}

/* Hero on the landing page */
.hero { text-align: center; padding: 48px 0; }
.hero h1 {
    color: #0033A0;
    font-size: 36px;
    margin: 0 0 12px 0;
    font-weight: 700;
}
.hero p {
    color: #555555;
    font-size: 18px;
    max-width: 720px;
    margin: 0 auto;
}

/* Cluster card grid on the landing page */
.cluster-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-top: 16px;
}
@media (max-width: 900px) {
    .cluster-grid { grid-template-columns: 1fr; }
}
.cluster-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 24px;
    min-height: 200px;
    border-top-width: 4px;
    border-top-style: solid;
    display: flex;
    flex-direction: column;
    text-decoration: none;
    color: inherit;
    transition: box-shadow 0.2s, transform 0.2s;
}
.cluster-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}
.cluster-card h4 { margin: 0 0 12px 0; font-size: 20px; font-weight: 700; }
.cluster-card p { font-size: 14px; color: #555555; margin: 0 0 16px 0; flex: 1; }
.cluster-card .enter { font-weight: 600; font-size: 15px; }

/* Cluster / section hero heading */
.cluster-heading h1 { margin: 0 0 8px 0; font-size: 32px; }
.cluster-heading p {
    color: #555;
    font-size: 16px;
    margin: 0 0 24px 0;
    max-width: 800px;
}

/* Card grid on cluster pages */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}
.card-grid .eberlight-card {
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
}
.card-grid .eberlight-card h4 a { color: #1A1A1A; text-decoration: none; }
.card-grid .eberlight-card h4 a:hover { color: #0033A0; text-decoration: underline; }
.card-grid .eberlight-card p {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.folder-section h2 {
    margin: 32px 0 12px 0;
    font-size: 20px;
    font-weight: 700;
    color: #1A1A1A;
    padding-bottom: 6px;
    border-bottom: 1px solid #E0E0E0;
}

/* Note detail two-column layout */
.note-layout {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
    gap: 32px;
    align-items: start;
}
@media (max-width: 900px) {
    .note-layout { grid-template-columns: 1fr; }
}
.note-main h1 {
    font-size: 32px;
    margin: 0 0 16px 0;
    color: #1A1A1A;
}
.note-main h2 { font-size: 24px; margin-top: 28px; }
.note-main h3 { font-size: 20px; margin-top: 24px; }
.note-main p, .note-main li { font-size: 16px; }
.note-main pre {
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.5;
}
.note-main code {
    font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.92em;
}
.note-main table {
    border-collapse: collapse;
    margin: 16px 0;
    width: 100%;
    font-size: 14px;
}
.note-main th, .note-main td {
    border: 1px solid #E0E0E0;
    padding: 8px 12px;
    text-align: left;
}
.note-main th { background: #F5F5F5; font-weight: 600; }
.note-main img { max-width: 100%; height: auto; }
.note-main blockquote {
    border-left: 4px solid #00A3E0;
    margin: 16px 0;
    padding: 4px 16px;
    color: #555;
    background: #F5F5F5;
}

/* Empty state banner (like Streamlit st.info) */
.info-box {
    background: #E6F3FB;
    border-left: 4px solid #00A3E0;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 16px 0;
    color: #1A1A1A;
}
""".strip()


def _rel(from_path: str, to_path: str) -> str:
    """Compute a relative URL from one site-relative path to another.

    Both arguments are POSIX-style paths relative to the site root (no
    leading slash).  Returns a relative URL suitable for an href.
    """
    from_parts = from_path.split("/")[:-1]  # strip filename
    to_parts = to_path.split("/")
    # Common prefix length
    i = 0
    while i < len(from_parts) and i < len(to_parts) - 1 and from_parts[i] == to_parts[i]:
        i += 1
    ups = [".."] * (len(from_parts) - i)
    tail = to_parts[i:]
    return "/".join(ups + tail) if ups or tail else "."


def _note_output_path(note: Note) -> str:
    """Return the site-relative HTML path for a note (POSIX-style)."""
    rel = note.path.relative_to(_REPO_ROOT).with_suffix(".html")
    return "notes/" + rel.as_posix()


def _md_link_rewrite(body_html: str) -> str:
    """Rewrite href="...md" links to href="...html" inside rendered HTML.

    Conservative: only rewrites href attributes that end in .md (with or
    without a fragment), and never touches absolute URLs that would confuse
    the rewrite.  Absolute URLs with .md in them are rare, and we still
    want them rewritten when they point to the repo.
    """
    return re.sub(
        r'(href="[^"]*?)\.md((?:#[^"]*)?")',
        r"\1.html\2",
        body_html,
    )


def _git_iso_date() -> str:
    """Best-effort HEAD commit date (YYYY-MM-DD)."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=_REPO_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return datetime.now().strftime("%Y-%m-%d")


def _folder_label(folder: str) -> str:
    """Human-friendly folder label, e.g. '02_xray_modalities' → 'Xray Modalities'."""
    return folder.split("_", 1)[1].replace("_", " ").title() if "_" in folder else folder


# ---------------------------------------------------------------------------
# HTML fragments
# ---------------------------------------------------------------------------


def _header_html(page_path: str, active_cluster: str | None = None) -> str:
    """Site header with logo + 3 cluster links. Mirrors explorer/components/header.py."""
    def link(cid: str, label: str) -> str:
        href = _rel(page_path, CLUSTER_PAGE[cid])
        cls = "active" if active_cluster == cid else ""
        return f'<a href="{href}" class="{cls}">{label}</a>'

    home_href = _rel(page_path, "index.html")
    return f"""
<div class="eberlight-header">
    <div class="eberlight-header-brand">
        <div class="eberlight-header-logo">eB</div>
        <a href="{home_href}" style="text-decoration:none;">
            <span class="eberlight-header-title">eBERlight Explorer</span>
        </a>
    </div>
    <nav class="eberlight-header-nav" aria-label="Main navigation">
        {link('discover', 'Discover')}
        {link('explore', 'Explore')}
        {link('build', 'Build')}
    </nav>
</div>
""".strip()


def _breadcrumb_html(page_path: str, items: list[tuple[str, str | None]]) -> str:
    """Mirrors explorer/components/breadcrumb.py but with real anchor targets."""
    parts: list[str] = []
    for label, target in items:
        esc = html_escape_mod.escape(label)
        if target is None:
            parts.append(f'<span class="current">{esc}</span>')
        else:
            href = _rel(page_path, target) if not target.startswith("http") else target
            parts.append(f'<a href="{href}">{esc}</a>')
    sep = '<span class="separator">&gt;</span>'
    return f'<nav class="eberlight-breadcrumb" aria-label="Breadcrumb">{sep.join(parts)}</nav>'


def _footer_html(last_updated: str) -> str:
    """Mirrors explorer/components/footer.py."""
    return f"""
<div class="eberlight-footer">
    <p>
        This research used resources of the Advanced Photon Source,
        a U.S. Department of Energy (DOE) Office of Science user facility
        operated for the DOE Office of Science by Argonne National
        Laboratory under Contract No. DE-AC02-06CH11357.
    </p>
    <p>
        eBERlight is the integrated BER (Biological and Environmental Research)
        program at the Advanced Photon Source, combining multiple X-ray
        techniques for biological and environmental science.
    </p>
    <div class="eberlight-footer-links">
        <a href="https://www.aps.anl.gov/" target="_blank" rel="noopener">APS</a>
        <a href="https://eberlight.aps.anl.gov/" target="_blank" rel="noopener">eBERlight</a>
        <a href="https://github.com/Denny-Hwang/synchrotron-data-analysis-notes" target="_blank" rel="noopener">Repository</a>
    </div>
    <div class="eberlight-footer-updated">Last updated: {last_updated}</div>
</div>
""".strip()


def _card_html(title: str, summary: str, tags: list[str], href: str) -> str:
    """Mirrors explorer/components/card.py."""
    tags_html = "".join(
        f'<span class="eberlight-tag">{html_escape_mod.escape(t)}</span>' for t in tags[:5]
    )
    return f"""
<div class="eberlight-card">
    <h4><a href="{href}">{html_escape_mod.escape(title)}</a></h4>
    <p>{html_escape_mod.escape(summary)}</p>
    <div>{tags_html}</div>
</div>
""".strip()


def _metadata_panel_html(note: Note) -> str:
    """Mirrors explorer/components/note_view.py._render_metadata_panel."""
    sections: list[str] = []

    def section(label: str, body: str) -> str:
        return (
            '<div style="margin-bottom:20px;">'
            '<div style="font-size:12px;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.5px;color:#555;margin-bottom:8px;">'
            f"{label}</div>{body}</div>"
        )

    if note.beamline:
        badges = " ".join(
            f'<span style="background:#0033A0;color:white;padding:4px 12px;'
            f'border-radius:12px;font-size:12px;font-weight:600;">'
            f"{html_escape_mod.escape(bl)}</span>"
            for bl in note.beamline
        )
        sections.append(
            section("Beamlines", f'<div style="display:flex;gap:6px;flex-wrap:wrap;">{badges}</div>')
        )

    if note.modality:
        sections.append(
            section(
                "Modality",
                f'<span class="eberlight-tag">{html_escape_mod.escape(note.modality)}</span>',
            )
        )

    if note.tags:
        tags_html = " ".join(
            f'<span class="eberlight-tag">{html_escape_mod.escape(t)}</span>' for t in note.tags
        )
        sections.append(section("Tags", tags_html))

    if note.related_publications:
        links = "".join(
            f'<div style="font-size:14px;color:#0033A0;margin-bottom:4px;">'
            f"{html_escape_mod.escape(p)}</div>"
            for p in note.related_publications
        )
        sections.append(section("Publications", links))

    if note.related_tools:
        links = "".join(
            f'<div style="font-size:14px;color:#0033A0;margin-bottom:4px;">'
            f"{html_escape_mod.escape(t)}</div>"
            for t in note.related_tools
        )
        sections.append(section("Related Tools", links))

    # Always surface cluster + source path so users can jump back to the repo.
    cluster_meta = CLUSTER_META.get(note.cluster)
    if cluster_meta:
        sections.append(
            section(
                "Cluster",
                f'<span class="eberlight-tag" style="background:{cluster_meta["color"]}1A;'
                f'color:{cluster_meta["color"]};border-color:{cluster_meta["color"]}33;">'
                f"{html_escape_mod.escape(cluster_meta['name'])}</span>",
            )
        )

    rel_source = note.path.relative_to(_REPO_ROOT).as_posix()
    sections.append(
        section(
            "Source",
            f'<a href="https://github.com/Denny-Hwang/synchrotron-data-analysis-notes/'
            f'blob/main/{rel_source}" target="_blank" rel="noopener" '
            f'style="font-size:13px;word-break:break-all;">{html_escape_mod.escape(rel_source)}</a>',
        )
    )

    if not sections:
        return ""
    return (
        '<aside aria-label="Note metadata" style="background:#FFFFFF;'
        'border:1px solid #E0E0E0;border-radius:8px;padding:24px;">'
        + "".join(sections)
        + "</aside>"
    )


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------


def _page_shell(
    page_path: str,
    title: str,
    body: str,
    *,
    active_cluster: str | None = None,
    extra_head: str = "",
    narrow: bool = False,
) -> str:
    css_href = _rel(page_path, "assets/styles.css")
    container_cls = "site-container narrow" if narrow else "site-container"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_escape_mod.escape(title)}</title>
<meta name="description" content="eBERlight Explorer — static mirror of the Streamlit app.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_href}">
{extra_head}
</head>
<body>
<div class="{container_cls}">
    {_header_html(page_path, active_cluster=active_cluster)}
    <main>
{body}
    </main>
    {_footer_html(_git_iso_date())}
</div>
</body>
</html>
"""


def _render_landing(out_dir: Path) -> None:
    page_path = "index.html"
    cards: list[str] = []
    for cid in CLUSTER_ORDER:
        meta = CLUSTER_META[cid]
        href = _rel(page_path, CLUSTER_PAGE[cid])
        cards.append(
            f'<a class="cluster-card" href="{href}" '
            f'style="border-top-color: {meta["color"]};">'
            f'<h4 style="color: {meta["color"]};">{html_escape_mod.escape(meta["name"])}</h4>'
            f'<p>{html_escape_mod.escape(meta["description"])}</p>'
            f'<span class="enter" style="color: {meta["color"]};">Enter →</span>'
            f"</a>"
        )
    body = f"""
    {_breadcrumb_html(page_path, [("Home", None)])}
    <section class="hero">
        <h1>eBERlight Research Explorer</h1>
        <p>Navigate synchrotron data analysis knowledge at Argonne's Advanced Photon Source</p>
    </section>
    <section class="cluster-grid">
        {"".join(cards)}
    </section>
"""
    html = _page_shell(page_path, "eBERlight Explorer", body)
    (out_dir / page_path).write_text(html, encoding="utf-8")


def _render_cluster(
    out_dir: Path,
    cluster_id: str,
    notes: list[Note],
    *,
    group_by_folder: bool,
) -> None:
    page_path = CLUSTER_PAGE[cluster_id]
    meta = CLUSTER_META[cluster_id]
    cluster_notes = [n for n in notes if n.folder in set(get_folders_for_cluster(cluster_id))]

    def card_for(note: Note) -> str:
        summary = note.description or note.body[:200].strip().replace("\n", " ")
        href = _rel(page_path, _note_output_path(note))
        return _card_html(note.title, summary, note.tags, href)

    if not cluster_notes:
        content = '<div class="info-box">No notes found in this cluster.</div>'
    elif group_by_folder:
        blocks: list[str] = []
        for folder, folder_notes_iter in groupby(cluster_notes, key=lambda n: n.folder):
            folder_notes = list(folder_notes_iter)
            cards = "\n".join(card_for(n) for n in folder_notes)
            blocks.append(
                f'<section class="folder-section">'
                f"<h2>{html_escape_mod.escape(_folder_label(folder))}</h2>"
                f'<div class="card-grid">{cards}</div>'
                f"</section>"
            )
        content = "\n".join(blocks)
    else:
        cards = "\n".join(card_for(n) for n in cluster_notes)
        content = f'<div class="card-grid">{cards}</div>'

    body = f"""
    {_breadcrumb_html(page_path, [("Home", "index.html"), (meta["name"], None)])}
    <section class="cluster-heading">
        <h1 style="color: {meta['color']};">{html_escape_mod.escape(meta['name'])}</h1>
        <p>{html_escape_mod.escape(meta['description'])}</p>
    </section>
    {content}
"""
    html = _page_shell(
        page_path,
        f"{meta['name']} — eBERlight Explorer",
        body,
        active_cluster=cluster_id,
    )
    target = out_dir / page_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def _render_note(out_dir: Path, note: Note, highlight_css: str) -> None:
    page_path = _note_output_path(note)
    cluster_meta = CLUSTER_META.get(note.cluster, CLUSTER_META["explore"])

    body_html = markdown.markdown(
        note.body,
        extensions=["fenced_code", "tables", "toc", "codehilite"],
        extension_configs={"codehilite": {"css_class": "highlight", "linenums": False}},
    )
    body_html = _md_link_rewrite(body_html)

    breadcrumb = _breadcrumb_html(
        page_path,
        [
            ("Home", "index.html"),
            (cluster_meta["name"], CLUSTER_PAGE[note.cluster]),
            (note.title, None),
        ],
    )

    aside = _metadata_panel_html(note)

    body = f"""
    {breadcrumb}
    <div class="note-layout">
        <article class="note-main">
            <h1>{html_escape_mod.escape(note.title)}</h1>
            {body_html}
        </article>
        {aside}
    </div>
"""
    extra_head = f"<style>{highlight_css}</style>"
    html = _page_shell(
        page_path,
        f"{note.title} — eBERlight Explorer",
        body,
        active_cluster=note.cluster,
        extra_head=extra_head,
        narrow=False,
    )
    target = out_dir / page_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def _render_404(out_dir: Path) -> None:
    page_path = "404.html"
    body = """
    <section class="hero">
        <h1>404 — Not Found</h1>
        <p>The page you requested does not exist. Try the <a href="index.html">home page</a>.</p>
    </section>
"""
    html = _page_shell(page_path, "Not Found — eBERlight Explorer", body, narrow=True)
    (out_dir / page_path).write_text(html, encoding="utf-8")


def _render_wireframe_index(out_dir: Path) -> None:
    page_path = "wireframes/index.html"
    body = """
    <section class="cluster-heading">
        <h1>Design Wireframes</h1>
        <p>Static HTML mockups from <code>docs/02_design/wireframes/html/</code>.
        These are design references produced before the Streamlit app and kept
        here for continuity.</p>
    </section>
    <ul>
        <li><a href="landing_v0.1.html">Landing page (v0.1)</a></li>
        <li><a href="section_v0.1.html">Section page (v0.1)</a></li>
        <li><a href="tool_v0.1.html">Tool detail page (v0.1)</a></li>
    </ul>
"""
    target = out_dir / page_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        _page_shell(page_path, "Wireframes — eBERlight Explorer", body, narrow=True),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Static assets
# ---------------------------------------------------------------------------


def _write_styles(out_dir: Path) -> None:
    """Concatenate explorer CSS + site-layout CSS → site/assets/styles.css."""
    explorer_css = (_EXPLORER_DIR / "assets" / "styles.css").read_text(encoding="utf-8")
    target = out_dir / "assets" / "styles.css"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(explorer_css + "\n\n" + SITE_LAYOUT_CSS + "\n", encoding="utf-8")


def _copy_note_assets(out_dir: Path) -> None:
    """Copy non-markdown files (images etc.) alongside notes into site/notes/.

    We only mirror the files the Streamlit app and markdown links actually
    reference: anything inside a note folder that is not a .md file.
    """
    exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf"}
    for folder in FOLDER_TO_CLUSTER:
        src = _REPO_ROOT / folder
        if not src.is_dir():
            continue
        for path in src.rglob("*"):
            if path.is_file() and path.suffix.lower() in exts:
                rel = path.relative_to(_REPO_ROOT)
                dst = out_dir / "notes" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dst)


def _copy_wireframes(out_dir: Path) -> None:
    src = _REPO_ROOT / "docs" / "02_design" / "wireframes" / "html"
    if not src.is_dir():
        return
    dst = out_dir / "wireframes"
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.iterdir():
        if path.is_file() and path.suffix.lower() == ".html":
            shutil.copy2(path, dst / path.name)


def _write_nojekyll(out_dir: Path) -> None:
    """Disable Jekyll so filenames with underscores are served as-is."""
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build(out_dir: Path) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    notes = load_notes(_REPO_ROOT)
    logger.info("Loaded %d notes", len(notes))

    _write_styles(out_dir)
    _write_nojekyll(out_dir)

    _render_landing(out_dir)
    _render_cluster(out_dir, "discover", notes, group_by_folder=False)
    _render_cluster(out_dir, "explore", notes, group_by_folder=True)
    _render_cluster(out_dir, "build", notes, group_by_folder=True)
    _render_404(out_dir)

    highlight_css = HtmlFormatter(style="monokai", noclasses=False).get_style_defs(".highlight")
    for note in notes:
        _render_note(out_dir, note, highlight_css)

    _copy_note_assets(out_dir)
    _copy_wireframes(out_dir)
    _render_wireframe_index(out_dir)

    logger.info("Static site written to %s", out_dir)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build the eBERlight static site.")
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO_ROOT / "site",
        help="Output directory (default: ./site)",
    )
    args = parser.parse_args()
    build(args.out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(_main())
