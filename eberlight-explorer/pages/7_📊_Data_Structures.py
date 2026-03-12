"""데이터 구조 및 EDA 플레이그라운드 (F7)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.markdown_viewer import render_markdown

st.set_page_config(page_title="데이터 구조", page_icon="📊", layout="wide")

inject_styles()

level = render_level_selector(key="data_level")

st.title("📊 데이터 구조")
st.markdown("싱크로트론 데이터셋을 위한 HDF5 스키마, 데이터 형식, 데이터 규모 분석, 탐색적 데이터 분석.")

HDF5_SCHEMAS = {
    "토모그래피": "06_data_structures/hdf5_structure/tomo_hdf5_schema.md",
    "XRF 현미경": "06_data_structures/hdf5_structure/xrf_hdf5_schema.md",
    "타이코그래피": "06_data_structures/hdf5_structure/ptychography_hdf5_schema.md",
}

DEEP_DIVE_FILES = {
    "HDF5 심층 분석 (SWMR, 병렬 I/O, 한계점)": "06_data_structures/hdf5_deep_dive.md",
    "데이터 형식 비교 (HDF5 vs Zarr vs TIFF)": "06_data_structures/data_formats_comparison.md",
    "APS-U 데이터 과제 (100+ TB/일)": "06_data_structures/data_challenges_apsu.md",
    "데이터 규모 분석 (APS-U 전후)": "06_data_structures/data_scale_analysis.md",
}

EDA_FILES = {
    "XRF EDA": "06_data_structures/eda/xrf_eda.md",
    "토모그래피 EDA": "06_data_structures/eda/tomo_eda.md",
    "분광학 EDA": "06_data_structures/eda/spectroscopy_eda.md",
}

NOTEBOOKS = [
    "06_data_structures/hdf5_structure/notebooks/01_hdf5_exploration.ipynb",
    "06_data_structures/hdf5_structure/notebooks/02_data_visualization.ipynb",
    "06_data_structures/eda/notebooks/01_xrf_eda.ipynb",
    "06_data_structures/eda/notebooks/02_tomo_eda.ipynb",
    "06_data_structures/eda/notebooks/03_spectral_eda.ipynb",
]

if level == "L0":
    cols = st.columns(3)
    with cols[0]:
        with st.container(border=True):
            st.markdown("### 📁 HDF5 스키마")
            st.metric("모달리티", len(HDF5_SCHEMAS))
            for name in HDF5_SCHEMAS:
                st.markdown(f"- {name}")
    with cols[1]:
        with st.container(border=True):
            st.markdown("### 📈 EDA 보고서")
            st.metric("보고서", len(EDA_FILES))
            for name in EDA_FILES:
                st.markdown(f"- {name}")
    with cols[2]:
        with st.container(border=True):
            st.markdown("### 📓 노트북")
            st.metric("노트북", len(NOTEBOOKS))
            for nb in NOTEBOOKS:
                st.markdown(f"- `{os.path.basename(nb)}`")

    # Data scale overview
    st.markdown("---")
    st.subheader("데이터 규모 개요")
    render_markdown("06_data_structures/data_scale_analysis.md", show_title=False)

elif level == "L1":
    render_markdown("06_data_structures/README.md", show_title=False)

    st.markdown("---")
    st.subheader("데이터 규모 분석")
    render_markdown("06_data_structures/data_scale_analysis.md", show_title=False)

    st.markdown("---")
    st.subheader("APS-U 데이터 과제")
    render_markdown("06_data_structures/data_challenges_apsu.md", show_title=False)

elif level == "L2":
    tab_names = ["HDF5 및 데이터 형식", "HDF5 스키마", "EDA 보고서", "노트북"]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        selected_topic = st.selectbox(
            "주제 선택", options=list(DEEP_DIVE_FILES.keys())
        )
        render_markdown(DEEP_DIVE_FILES[selected_topic], show_title=True)

    with tabs[1]:
        selected_schema = st.selectbox("스키마 선택", options=list(HDF5_SCHEMAS.keys()))
        render_markdown(HDF5_SCHEMAS[selected_schema], show_title=True)

    with tabs[2]:
        selected_eda = st.selectbox("EDA 선택", options=list(EDA_FILES.keys()))
        render_markdown(EDA_FILES[selected_eda], show_title=True)

    with tabs[3]:
        st.subheader("사용 가능한 노트북")
        for nb in NOTEBOOKS:
            st.markdown(f"- `{nb}`")
        st.info("노트북 렌더링에는 nbconvert가 필요합니다. 파일은 저장소에서 확인할 수 있습니다.")

elif level == "L3":
    all_files = (
        list(HDF5_SCHEMAS.values()) +
        list(DEEP_DIVE_FILES.values()) +
        list(EDA_FILES.values()) +
        ["06_data_structures/README.md"]
    )
    selected = st.selectbox("파일 선택", options=all_files)
    content = read_local_file(selected)
    if content:
        st.code(content, language="markdown")
