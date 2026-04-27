"""Build and Compute — cluster landing page.

Lists notes from 05_tools_and_code, 06_data_structures,
and 07_data_pipeline as cards.

Ref: IA-001 — Cluster mapping.
Ref: FR-003 — Cluster pages list notes as cards.
"""

import sys
from pathlib import Path

import streamlit as st

_EXPLORER_DIR = Path(__file__).resolve().parent.parent
if str(_EXPLORER_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPLORER_DIR))

from components.breadcrumb import render_breadcrumb
from components.card import render_card
from components.footer import render_footer
from components.header import render_header
from lib.ia import CLUSTER_META, get_folders_for_cluster
from lib.notes import load_notes

st.set_page_config(page_title="Build and Compute — eBERlight", page_icon="⚙️", layout="wide")

_CSS_PATH = _EXPLORER_DIR / "assets" / "styles.css"
if _CSS_PATH.exists():
    st.markdown(f"<style>{_CSS_PATH.read_text()}</style>", unsafe_allow_html=True)

render_header()
render_breadcrumb([("Home", "/"), ("Build and Compute", None)])

meta = CLUSTER_META["build"]
st.markdown(
    f'<h1 style="color:{meta["color"]};">{meta["name"]}</h1>'
    f'<p style="color:#555;font-size:16px;margin-bottom:24px;">{meta["description"]}</p>',
    unsafe_allow_html=True,
)

repo_root = _EXPLORER_DIR.parent
all_notes = load_notes(repo_root)
cluster_folders = set(get_folders_for_cluster("build"))
cluster_notes = [n for n in all_notes if n.folder in cluster_folders]

from itertools import groupby

for folder, folder_notes in groupby(cluster_notes, key=lambda n: n.folder):
    folder_label = folder.split("_", 1)[1].replace("_", " ").title() if "_" in folder else folder
    st.markdown(f"### {folder_label}")
    for note in folder_notes:
        summary = note.description or note.body[:150].strip().replace("\n", " ")
        render_card(title=note.title, summary=summary, tags=note.tags)

if not cluster_notes:
    st.info("No notes found in this cluster.")

render_footer()
