"""데이터 파이프라인 시각화 도구 (F6)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.pipeline_diagram import render_pipeline_diagram
from components.markdown_viewer import render_markdown, render_content

st.set_page_config(page_title="데이터 파이프라인", page_icon="🔄", layout="wide")

inject_styles()

level = render_level_selector(key="pipe_level")
cross_refs = load_yaml("cross_references.yaml")
stages = cross_refs.get("pipeline_stages", [])

st.title("🔄 데이터 파이프라인")
st.markdown("빔라인 수집부터 장기 저장까지의 엔드투엔드 데이터 흐름.")

if level == "L0":
    render_pipeline_diagram()

    st.markdown("---")
    st.subheader("파이프라인 단계")
    for s in stages:
        tools_str = ", ".join(s.get("tools", [])) or "—"
        st.markdown(f"- {s['icon']} **{s['name']}** — 도구: {tools_str}")

elif level in ("L1", "L2"):
    render_pipeline_diagram()

    st.markdown("---")

    # Overview from README
    readme_content = read_local_file("07_data_pipeline/README.md")
    if readme_content and level == "L1":
        render_content(readme_content)

    if level == "L2":
        # Architecture diagram
        arch_content = read_local_file("07_data_pipeline/architecture_diagram.md")
        if arch_content:
            with st.expander("🏗️ 아키텍처 다이어그램", expanded=True):
                render_content(arch_content)

        # Individual stage tabs
        tab_names = [f"{s['icon']} {s['name']}" for s in stages]
        tabs = st.tabs(tab_names)
        for tab, stage in zip(tabs, stages):
            with tab:
                render_markdown(stage["file"], show_title=True)

elif level == "L3":
    all_files = ["07_data_pipeline/README.md", "07_data_pipeline/architecture_diagram.md"]
    all_files += [s["file"] for s in stages]

    selected = st.selectbox("파일 선택", options=all_files)
    content = read_local_file(selected)
    if content:
        st.code(content, language="markdown")
