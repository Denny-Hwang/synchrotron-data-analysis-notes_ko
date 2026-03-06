"""AI/ML 방법 분류 체계 지도 (F3)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.markdown_viewer import render_markdown
from components.mermaid_diagram import render_mermaid

st.set_page_config(page_title="AI/ML 방법", page_icon="🤖", layout="wide")

inject_styles()

level = render_level_selector(key="aiml_level")
categories = load_yaml("method_taxonomy.yaml")["categories"]
modalities = load_yaml("modality_metadata.yaml")["modalities"]

st.title("🤖 AI/ML 방법")
st.markdown("싱크로트론 데이터 분석에 적용되는 머신러닝 및 AI 방법.")

TAXONOMY_CODE = """graph TD
    ROOT["싱크로트론 데이터를 위한 AI/ML"] --> SEG["분할"]
    ROOT --> DEN["노이즈 제거"]
    ROOT --> REC["재구성"]
    ROOT --> AUT["자율 실험"]
    ROOT --> MUL["다중모달 통합"]
    SEG --> S1["U-Net Variants"]
    SEG --> S2["토모 분할"]
    SEG --> S3["XRF 세포 분할"]
    DEN --> D1["TomoGAN"]
    DEN --> D2["Deep Residual XRF"]
    DEN --> D3["Noise2Noise"]
    REC --> R1["PtychoNet"]
    REC --> R2["TomocuPy"]
    REC --> R3["INR Dynamic"]
    AUT --> A1["AI-NERD"]
    AUT --> A2["ROI-Finder"]
    AUT --> A3["베이지안 최적화"]
    MUL --> M1["XRF + 타이코그래피"]
    MUL --> M2["CT-XAS 상관관계"]
    MUL --> M3["광학-X선"]"""

if level == "L0":
    render_mermaid(TAXONOMY_CODE, height=500)

    st.markdown("---")
    cols = st.columns(len(categories))
    for col, cat in zip(cols, categories):
        with col:
            with st.container(border=True):
                st.markdown(f"### {cat['icon']}")
                st.markdown(f"**{cat['name']}**")
                st.caption(cat["description"])
                st.metric("방법", len(cat["methods"]))

elif level == "L1":
    render_mermaid(TAXONOMY_CODE, height=500)

    # Category overview
    st.markdown("---")
    st.subheader("방법 카테고리")
    for cat in categories:
        with st.expander(f"{cat['icon']} {cat['name']} ({len(cat['methods'])}개 방법)", expanded=True):
            st.markdown(cat["description"])
            st.markdown("**방법:**")
            for m in cat["methods"]:
                st.markdown(f"- **{m['name']}**")
            applicable = ", ".join(cat["modalities"])
            st.caption(f"적용 가능한 모달리티: {applicable}")

    # Heatmap
    st.markdown("---")
    st.subheader("모달리티 × 방법 매트릭스")
    import pandas as pd

    mod_names = [f"{m['icon']} {m['short_name']}" for m in modalities]
    matrix = []
    for m in modalities:
        row = {}
        for c in categories:
            row[c["name"]] = "Y" if m["id"] in c["modalities"] else "-"
        matrix.append(row)
    df = pd.DataFrame(matrix, index=mod_names)
    st.dataframe(df, use_container_width=True)

elif level == "L2":
    # Method detail cards
    cat_names = [f"{c['icon']} {c['name']}" for c in categories]
    selected_cat_name = st.selectbox("카테고리 선택", options=cat_names)
    cat_idx = cat_names.index(selected_cat_name)
    cat = categories[cat_idx]

    st.subheader(f"{cat['icon']} {cat['name']}")
    st.markdown(cat["description"])

    method_names = [m["name"] for m in cat["methods"]]
    selected_method = st.selectbox("방법 선택", options=method_names)
    method = next(m for m in cat["methods"] if m["name"] == selected_method)

    st.markdown("---")
    render_markdown(method["file"], show_title=True)

elif level == "L3":
    # Source view
    all_files = []
    for cat in categories:
        for m in cat["methods"]:
            all_files.append((f"{cat['icon']} {cat['name']} / {m['name']}", m["file"]))

    selected = st.selectbox("파일 선택", options=all_files, format_func=lambda x: x[0])
    content = read_local_file(selected[1])
    if content:
        st.code(content, language="markdown")
