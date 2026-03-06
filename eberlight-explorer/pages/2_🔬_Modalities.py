"""X선 모달리티 탐색기 (F2)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file, extract_section
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.markdown_viewer import render_markdown, render_markdown_card

st.set_page_config(page_title="X선 모달리티", page_icon="🔬", layout="wide")

inject_styles()

level = render_level_selector(key="mod_level")
modalities = load_yaml("modality_metadata.yaml")["modalities"]

st.title("🔬 X선 모달리티")
st.markdown("생물학 및 환경과학을 위해 APS 빔라인에서 사용되는 6가지 X선 측정 기법.")

if level == "L0":
    # High-level comparison
    import pandas as pd
    data = []
    for m in modalities:
        data.append({
            "": m["icon"],
            "모달리티": m["short_name"],
            "상호작용": m["interaction"],
            "측정 대상": m["measures"],
            "해상도": m["resolution"],
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

elif level == "L1":
    # Comparison table + per-modality summary
    import pandas as pd
    data = []
    for m in modalities:
        data.append({
            "": m["icon"],
            "모달리티": m["short_name"],
            "상호작용": m["interaction"],
            "측정 대상": m["measures"],
            "해상도": m["resolution"],
            "빔라인": ", ".join(m["beamlines"]),
            "AI 방법": ", ".join(m["ai_methods"]) if m["ai_methods"] else "—",
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    st.markdown("---")
    for m in modalities:
        with st.expander(f"{m['icon']} {m['name']}", expanded=False):
            cols = st.columns([2, 1])
            with cols[0]:
                content = read_local_file(m["files"]["readme"])
                if content:
                    # Show first few paragraphs
                    paragraphs = content.split("\n\n")
                    preview = "\n\n".join(paragraphs[:5])
                    st.markdown(preview)
            with cols[1]:
                st.markdown("**주요 정보**")
                st.markdown(f"- **해상도:** {m['resolution']}")
                st.markdown(f"- **빔라인:** {', '.join(m['beamlines'])}")
                st.markdown(f"- **태그:** {', '.join(m['tags'])}")
                if m["ai_methods"]:
                    st.markdown(f"- **AI 방법:** {', '.join(m['ai_methods'])}")

elif level == "L2":
    # Individual modality detail pages
    selected = st.selectbox(
        "모달리티 선택",
        options=[m["short_name"] for m in modalities],
        format_func=lambda x: next(f"{m['icon']} {m['name']}" for m in modalities if m["short_name"] == x),
    )
    mod = next(m for m in modalities if m["short_name"] == selected)

    st.subheader(f"{mod['icon']} {mod['name']}")

    info_cols = st.columns(4)
    with info_cols[0]:
        st.metric("해상도", mod["resolution"])
    with info_cols[1]:
        st.metric("빔라인", len(mod["beamlines"]))
    with info_cols[2]:
        st.metric("AI 방법", len(mod["ai_methods"]))
    with info_cols[3]:
        st.metric("상호작용", mod["interaction"])

    tabs = st.tabs(["원리", "데이터 형식", "AI/ML 방법"] +
                   [e["title"] for e in mod["files"].get("extra", [])])

    with tabs[0]:
        render_markdown(mod["files"]["readme"], show_title=False)

    with tabs[1]:
        if "data_format" in mod["files"]:
            render_markdown(mod["files"]["data_format"], show_title=False)

    with tabs[2]:
        if "ai_ml" in mod["files"]:
            render_markdown(mod["files"]["ai_ml"], show_title=False)

    for i, extra in enumerate(mod["files"].get("extra", [])):
        with tabs[3 + i]:
            render_markdown(extra["path"], show_title=False)

elif level == "L3":
    # Source view
    selected = st.selectbox(
        "모달리티 선택",
        options=[m["short_name"] for m in modalities],
    )
    mod = next(m for m in modalities if m["short_name"] == selected)

    all_files = [mod["files"]["readme"], mod["files"].get("data_format"), mod["files"].get("ai_ml")]
    all_files += [e["path"] for e in mod["files"].get("extra", [])]
    all_files = [f for f in all_files if f]

    selected_file = st.selectbox("파일 선택", options=all_files)
    content = read_local_file(selected_file)
    if content:
        st.code(content, language="markdown")
