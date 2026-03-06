"""단계별 공개를 위한 수준 선택 컴포넌트 (L0-L3)."""

import streamlit as st

LEVELS = {
    "🌍 개요": ("L0", "상위 수준 통계 및 프로그램 요약"),
    "📋 섹션": ("L1", "섹션 요약, 비교 테이블"),
    "🔎 상세": ("L2", "개별 방법, 도구 또는 논문 심층 분석"),
    "📄 소스": ("L3", "원시 마크다운 소스 및 코드"),
}


def render_level_selector(key: str = "level") -> str:
    """사이드바에 수준 선택기를 렌더링하고 선택된 수준을 반환합니다."""
    with st.sidebar:
        st.markdown("#### 🔎 상세 수준")
        level_name = st.radio(
            "상세 수준",
            options=list(LEVELS.keys()),
            index=1,
            key=key,
            label_visibility="collapsed",
        )
        code, desc = LEVELS[level_name]
        st.caption(f"_{desc}_")
        st.markdown("---")
    return code
