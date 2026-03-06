"""도구 비교 카드 컴포넌트."""

import streamlit as st


def render_tool_card(tool: dict, show_detail: bool = False):
    """도구 정보 카드를 렌더링합니다."""
    with st.container(border=True):
        st.markdown(f"{tool['icon']} **{tool['name']}**")
        st.caption(f"{tool['category']} | {tool['language']} | {'GPU' if tool.get('gpu') else 'CPU'}")

        cols = st.columns(3)
        with cols[0]:
            st.metric("성숙도", tool.get("maturity", "N/A"))
        with cols[1]:
            stage = tool.get("pipeline_stage", "N/A") or "N/A"
            st.metric("단계", stage.title())
        with cols[2]:
            mod_count = len(tool.get("modalities", []))
            st.metric("모달리티", mod_count)

        if show_detail:
            tag_str = " ".join(f"`{t}`" for t in tool.get("tags", []))
            if tag_str:
                st.markdown(tag_str)

            modalities = ", ".join(tool.get("modalities", []))
            if modalities:
                st.markdown(f"**지원 모달리티:** {modalities}")
