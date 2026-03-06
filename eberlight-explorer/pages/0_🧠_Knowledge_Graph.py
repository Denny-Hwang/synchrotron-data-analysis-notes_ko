"""지식 그래프 및 교차 참조 탐색기 (F8)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles

st.set_page_config(page_title="지식 그래프", page_icon="🧠", layout="wide")

inject_styles()

level = render_level_selector(key="xref_level")

modalities = load_yaml("modality_metadata.yaml")["modalities"]
categories = load_yaml("method_taxonomy.yaml")["categories"]
papers = load_yaml("publication_catalog.yaml")["publications"]
tools = load_yaml("tool_catalog.yaml")["tools"]
cross_refs = load_yaml("cross_references.yaml")

st.title("🧠 지식 그래프")
st.markdown(
    "모달리티, AI/ML 방법, 도구, 출판물 간의 **연결**을 시각적으로 보여줍니다. "
    "싱크로트론 연구 생태계의 각 요소가 어떻게 관련되는지 탐색하세요."
)

# ── Knowledge Graph (always shown) ─────────────────────
st.markdown("---")
st.subheader("🔗 인터랙티브 연구 네트워크")

from utils.graph_builder import build_knowledge_graph
from components.visjs_graph import render_visjs_graph

raw_nodes, raw_edges = build_knowledge_graph()

# Layout toggle via Streamlit checkbox (drives initial state)
hier_col, info_col = st.columns([1, 3])
with hier_col:
    hierarchical = st.checkbox("계층적 레이아웃", value=False, key="kg_hier")
with info_col:
    st.caption("위의 레이아웃을 전환하거나 그래프 내 컨트롤을 사용하세요. 노드를 드래그하여 재배치, 스크롤하여 확대/축소, 클릭하여 연결 강조.")

render_visjs_graph(raw_nodes, raw_edges, hierarchical=hierarchical, height=650)

# ── Matrix Views ──────────────────────────────────────
if level in ("L0", "L1", "L2"):
    import pandas as pd

    st.markdown("---")
    st.subheader("📊 교차 참조 매트릭스")

    matrix_tabs = st.tabs([
        "모달리티 × 방법",
        "도구 × 파이프라인 단계",
        "논문 × 카테고리",
    ])

    with matrix_tabs[0]:
        st.markdown("어떤 AI/ML 방법 카테고리가 어떤 X선 모달리티에 적용되나요?")
        mod_names = [f"{m['icon']} {m['short_name']}" for m in modalities]
        cat_names = [c["name"] for c in categories]
        matrix = []
        for m in modalities:
            row = {}
            for c in categories:
                row[c["name"]] = "✅" if m["id"] in c["modalities"] else "—"
            matrix.append(row)
        st.dataframe(pd.DataFrame(matrix, index=mod_names), use_container_width=True)

    with matrix_tabs[1]:
        st.markdown("어떤 도구가 어떤 파이프라인 단계에서 작동하나요?")
        display_tools = [t for t in tools if t["id"] != "aps_github_repos"]
        stages = ["acquisition", "processing", "analysis"]
        tool_matrix = []
        for t in display_tools:
            row = {s.title(): "✅" if t.get("pipeline_stage") == s else "—" for s in stages}
            tool_matrix.append(row)
        st.dataframe(
            pd.DataFrame(tool_matrix, index=[f"{t['icon']} {t['name']}" for t in display_tools]),
            use_container_width=True,
        )

    with matrix_tabs[2]:
        st.markdown("어떤 논문이 어떤 AI/ML 카테고리에 속하나요?")
        seen_files = set()
        unique_papers = []
        for p in papers:
            if p["file"] not in seen_files:
                seen_files.add(p["file"])
                unique_papers.append(p)
        paper_matrix = []
        for p in unique_papers:
            row = {c["name"]: "✅" if p["category"] == c["id"] else "—" for c in categories}
            paper_matrix.append(row)
        st.dataframe(
            pd.DataFrame(
                paper_matrix,
                index=[f"[{p['year']}] {p['title'][:40]}" for p in unique_papers],
            ),
            use_container_width=True,
        )

# ── References & Glossary ─────────────────────────────
if level in ("L2", "L3"):
    st.markdown("---")

    ref_tabs = st.tabs(["📖 용어집", "📚 참고문헌", "🔗 유용한 링크"])

    with ref_tabs[0]:
        glossary_content = read_local_file("08_references/glossary.md")
        if glossary_content:
            if level == "L3":
                st.code(glossary_content, language="markdown")
            else:
                st.markdown(glossary_content)

    with ref_tabs[1]:
        bib_content = read_local_file("08_references/bibliography.bib")
        if bib_content:
            if level == "L3":
                st.code(bib_content, language="bibtex")
            else:
                from utils.content_parser import parse_bibtex
                entries = parse_bibtex(bib_content)
                for entry in entries:
                    title = entry.get("title", "Untitled")
                    author = entry.get("author", "Unknown")
                    year = entry.get("year", "N/A")
                    journal = entry.get("journal", "")
                    doi = entry.get("doi", "")
                    journal_str = f" — _{journal}_" if journal else ""
                    doi_str = f" | [DOI](https://doi.org/{doi})" if doi else ""
                    st.markdown(
                        f"- **{title}**{journal_str}\n"
                        f"  - {author} ({year}){doi_str}"
                    )

    with ref_tabs[2]:
        links_content = read_local_file("08_references/useful_links.md")
        if links_content:
            if level == "L3":
                st.code(links_content, language="markdown")
            else:
                st.markdown(links_content)
