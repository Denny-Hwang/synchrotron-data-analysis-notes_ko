"""
eBERlight 연구 탐색기
싱크로트론 데이터 분석 연구를 탐색하기 위한 인터랙티브 Streamlit 앱.
"""

import streamlit as st

st.set_page_config(
    page_title="eBERlight 연구 탐색기",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS — 더 큰 폰트, 더 나은 간격, 불릿 스타일링
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    h1 { color: #0A1628; font-size: 2.4rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }

    /* Body text larger */
    .stMarkdown p, .stMarkdown li { font-size: 1.08rem; line-height: 1.7; }

    /* Metric cards */
    .stMetric > div { background: #E8EEF6; padding: 12px; border-radius: 8px; }

    /* Expanders */
    div[data-testid="stExpander"] { border: 1px solid #E8EEF6; border-radius: 8px; }
    div[data-testid="stExpander"] summary { font-size: 1.15rem; font-weight: 600; }

    /* Bullet list styling */
    .stMarkdown ul { padding-left: 1.4em; }
    .stMarkdown ul li { margin-bottom: 0.35em; }
    .stMarkdown ul li::marker { color: #00D4AA; font-size: 1.1em; }

    /* Tables */
    .stDataFrame { font-size: 1.02rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] > div { padding-top: 1rem; }
    section[data-testid="stSidebar"] .stMarkdown p { font-size: 1.0rem; }
    section[data-testid="stSidebar"] h4 { font-size: 1.1rem !important; margin-bottom: 0.3rem; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 1.05rem; }

    /* Captions a bit bigger */
    .stCaption, .stMarkdown small { font-size: 0.92rem !important; }

    /* Info boxes */
    .stAlert p { font-size: 1.05rem; }

    /* Tabs */
    button[data-baseweb="tab"] { font-size: 1.05rem; }

    /* Container borders */
    div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.content_parser import load_yaml
from components.level_selector import render_level_selector
from components.pipeline_diagram import render_pipeline_diagram

# ── 사이드바 ───────────────────────────────────────────
st.sidebar.markdown("## 🔬 eBERlight Explorer")
st.sidebar.caption("싱크로트론 데이터 분석 연구")
st.sidebar.markdown("---")

st.sidebar.markdown("#### 📂 탐색하기")
st.sidebar.markdown(
    "왼쪽 메뉴의 **페이지**를 사용하여 탐색하세요:\n"
    "- 🧠 **지식 그래프** — 시각적 연구 지도\n"
    "- 🔬 **모달리티** — X선 기법\n"
    "- 🤖 **AI/ML** — 방법 및 알고리즘\n"
    "- 📚 **논문** — 리뷰된 출판물\n"
    "- 🛠️ **도구** — 소프트웨어 생태계\n"
    "- 🔄 **파이프라인** — 데이터 흐름\n"
    "- 📊 **데이터** — 스키마 및 EDA\n"
    "- 📡 **노이즈 카탈로그** — 29종 아티팩트"
)
st.sidebar.markdown("---")
level = render_level_selector()

# ── 데이터 로드 ─────────────────────────────────────────
index = load_yaml("content_index.yaml")
modalities = load_yaml("modality_metadata.yaml")["modalities"]
methods = load_yaml("method_taxonomy.yaml")["categories"]
papers = load_yaml("publication_catalog.yaml")["publications"]
tools_data = load_yaml("tool_catalog.yaml")["tools"]

# ──────────────────────────────────────────────
# 홈 페이지
# ──────────────────────────────────────────────
st.title("🔬 eBERlight 연구 탐색기")
st.markdown(
    "**싱크로트론 데이터 분석 노트**를 인터랙티브하게 탐색합니다 — "
    "APS 빔라인, X선 모달리티, AI/ML 방법, 출판물, 도구를 다룹니다."
)

# 통계 카드
st.markdown("---")
cols = st.columns(5)
stats = [
    ("🔬", "모달리티", len(modalities)),
    ("🤖", "AI/ML 카테고리", len(methods)),
    ("📚", "논문 리뷰", len(papers)),
    ("🛠️", "도구", len([t for t in tools_data if t["id"] != "aps_github_repos"])),
    ("📊", "저장소 섹션", len(index["sections"])),
]
for col, (icon, label, value) in zip(cols, stats):
    with col:
        st.metric(label=f"{icon} {label}", value=value)

if level in ("L0", "L1"):
    # 빠른 탐색 가이드
    st.markdown("---")
    st.subheader("🧭 빠른 탐색 가이드")
    guide_cols = st.columns(3)
    guides = [
        ("🧪 싱크로트론이 처음이신가요?",
         "- **프로그램 개요**부터 시작하세요\n- 그런 다음 **X선 모달리티**를 탐색하세요\n- 용어는 **용어집**을 확인하세요"),
        ("🤖 AI/ML을 적용하고 싶으신가요?",
         "- **AI/ML 방법**으로 바로 이동하세요\n- **출판물**에서 리뷰를 찾아보세요\n- **도구**에서 구현 사례를 확인하세요"),
        ("📊 데이터를 이해해야 하나요?",
         "- **데이터 구조**에서 스키마를 확인하세요\n- **데이터 파이프라인** 흐름을 탐색하세요\n- **EDA 노트북**을 인터랙티브하게 실행하세요"),
    ]
    for col, (title, desc) in zip(guide_cols, guides):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(desc)

    # 섹션 개요 카드
    st.markdown("---")
    st.subheader("📂 저장소 섹션")
    section_cols = st.columns(4)
    for i, section in enumerate(index["sections"]):
        with section_cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"### {section['icon']} {section['name']}")
                st.markdown(section["description"])
                st.markdown(f"`{len(section['topics'])}개 주제`")

if level in ("L1", "L2"):
    # 모달리티 비교 테이블
    st.markdown("---")
    st.subheader("🔬 X선 모달리티 한눈에 보기")
    import pandas as pd
    mod_data = []
    for m in modalities:
        mod_data.append({
            "모달리티": f"{m['icon']} {m['short_name']}",
            "상호작용": m["interaction"],
            "측정 대상": m["measures"],
            "해상도": m["resolution"],
            "빔라인": ", ".join(m["beamlines"]),
            "AI 방법": len(m["ai_methods"]),
        })
    df = pd.DataFrame(mod_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # AI/ML 방법 개요
    st.markdown("---")
    st.subheader("🤖 AI/ML 방법 카테고리")
    method_cols = st.columns(len(methods))
    for col, cat in zip(method_cols, methods):
        with col:
            with st.container(border=True):
                st.markdown(f"### {cat['icon']}")
                st.markdown(f"**{cat['name']}**")
                st.caption(f"{len(cat['methods'])}개 방법")
                for m in cat["methods"]:
                    st.markdown(f"- {m['name']}")

    # 파이프라인 개요
    st.markdown("---")
    st.subheader("🔄 데이터 파이프라인 개요")
    render_pipeline_diagram()

st.markdown("---")
st.caption(
    "[synchrotron-data-analysis-notes](https://github.com/Denny-Hwang/synchrotron-data-analysis-notes)에서 빌드됨 | "
    "eBERlight Research Explorer v0.1.0"
)
