"""향상된 마크다운 뷰어 컴포넌트."""

import re
import streamlit as st
from utils.content_parser import read_local_file, extract_title
from components.mermaid_diagram import render_mermaid

# Pattern to split markdown on ```mermaid ... ``` blocks
_MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def render_content(content: str):
    """마크다운 콘텐츠를 렌더링하며, mermaid 블록을 추출하여 적절히 렌더링합니다."""
    parts = _MERMAID_RE.split(content)
    # parts alternates: [text, mermaid_code, text, mermaid_code, ...]
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular markdown text
            text = part.strip()
            if text:
                st.markdown(text, unsafe_allow_html=False)
        else:
            # Mermaid diagram code
            lines = part.strip().split("\n")
            height = max(300, len(lines) * 35 + 100)
            render_mermaid(part, height=min(height, 800))


def render_markdown(file_path: str, show_title: bool = True):
    """저장소에서 마크다운 파일을 렌더링합니다."""
    content = read_local_file(file_path)
    if content is None:
        st.warning(f"파일을 찾을 수 없습니다: `{file_path}`")
        return

    if show_title:
        title = extract_title(content)
        st.subheader(title)

    render_content(content)


def render_markdown_card(file_path: str, title: str | None = None, expanded: bool = False):
    """확장 가능한 카드 내부에 마크다운 콘텐츠를 렌더링합니다."""
    content = read_local_file(file_path)
    if content is None:
        return

    display_title = title or extract_title(content)
    with st.expander(display_title, expanded=expanded):
        render_content(content)
