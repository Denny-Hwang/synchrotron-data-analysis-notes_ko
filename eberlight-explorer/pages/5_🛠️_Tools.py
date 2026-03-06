"""도구 및 코드 생태계 (F5)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.tool_card import render_tool_card
from components.markdown_viewer import render_markdown

st.set_page_config(page_title="도구 및 코드", page_icon="🛠️", layout="wide")

inject_styles()

level = render_level_selector(key="tool_level")
tools = load_yaml("tool_catalog.yaml")["tools"]
# Filter out catalog entry for card display
display_tools = [t for t in tools if t["id"] != "aps_github_repos"]

st.title("🛠️ 도구 및 코드 생태계")
st.markdown("싱크로트론 데이터 처리 및 분석을 위한 오픈소스 도구 및 소프트웨어.")

if level == "L0":
    # Tool landscape
    cols = st.columns(3)
    stages = {"acquisition": [], "processing": [], "analysis": []}
    for t in display_tools:
        stage = t.get("pipeline_stage")
        if stage and stage in stages:
            stages[stage].append(t)

    stage_info = [
        ("📡 수집", stages["acquisition"]),
        ("⚙️ 처리", stages["processing"]),
        ("🧠 분석", stages["analysis"]),
    ]
    for col, (title, stage_tools) in zip(cols, stage_info):
        with col:
            with st.container(border=True):
                st.markdown(f"### {title}")
                for t in stage_tools:
                    st.markdown(f"- {t['icon']} **{t['name']}** ({t['language']})")

elif level == "L1":
    # Comparison table
    import pandas as pd
    data = []
    for t in display_tools:
        data.append({
            "": t["icon"],
            "도구": t["name"],
            "카테고리": t["category"],
            "언어": t["language"],
            "GPU": "✅" if t.get("gpu") else "❌",
            "성숙도": t.get("maturity", "N/A"),
            "단계": (t.get("pipeline_stage") or "N/A").title(),
            "모달리티": len(t.get("modalities", [])),
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    for t in display_tools:
        render_tool_card(t, show_detail=True)

elif level == "L2":
    # Individual tool detail
    tool_names = [f"{t['icon']} {t['name']}" for t in display_tools]
    selected_idx = st.selectbox(
        "도구 선택",
        options=range(len(display_tools)),
        format_func=lambda i: tool_names[i],
    )
    tool = display_tools[selected_idx]

    st.subheader(f"{tool['icon']} {tool['name']}")
    render_tool_card(tool, show_detail=True)

    # Show available files as tabs
    files = tool.get("files", {})
    tab_names = []
    tab_files = []
    for key, path in files.items():
        if key == "readme":
            continue
        tab_names.append(key.replace("_", " ").title())
        tab_files.append(path)

    # README first
    st.markdown("---")
    render_markdown(files.get("readme", ""), show_title=False)

    if tab_names:
        tabs = st.tabs(tab_names)
        for tab, fpath in zip(tabs, tab_files):
            with tab:
                render_markdown(fpath, show_title=False)

    # Notebooks
    notebooks = tool.get("notebooks", [])
    if notebooks:
        st.markdown("---")
        st.subheader("📓 노트북")
        for nb_path in notebooks:
            st.markdown(f"- `{nb_path}`")

elif level == "L3":
    tool_names = [f"{t['icon']} {t['name']}" for t in display_tools]
    selected_idx = st.selectbox(
        "도구 선택",
        options=range(len(display_tools)),
        format_func=lambda i: tool_names[i],
    )
    tool = display_tools[selected_idx]

    all_files = list(tool.get("files", {}).values())
    selected_file = st.selectbox("파일 선택", options=all_files)
    content = read_local_file(selected_file)
    if content:
        st.code(content, language="markdown")
