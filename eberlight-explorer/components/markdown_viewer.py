"""향상된 마크다운 뷰어 컴포넌트."""

import streamlit as st
from utils.content_parser import read_local_file, extract_title


def render_markdown(file_path: str, show_title: bool = True):
    """저장소에서 마크다운 파일을 렌더링합니다."""
    content = read_local_file(file_path)
    if content is None:
        st.warning(f"파일을 찾을 수 없습니다: `{file_path}`")
        return

    if show_title:
        title = extract_title(content)
        st.subheader(title)

    st.markdown(content, unsafe_allow_html=False)


def render_markdown_card(file_path: str, title: str | None = None, expanded: bool = False):
    """확장 가능한 카드 내부에 마크다운 콘텐츠를 렌더링합니다."""
    content = read_local_file(file_path)
    if content is None:
        return

    display_title = title or extract_title(content)
    with st.expander(display_title, expanded=expanded):
        st.markdown(content, unsafe_allow_html=False)
