"""출판물 리뷰 카드 컴포넌트."""

import streamlit as st
from utils.content_parser import read_local_file, extract_tldr, extract_section


def render_paper_card(paper: dict, show_detail: bool = False):
    """논문 리뷰 카드를 렌더링합니다."""
    priority_colors = {
        "High": "🔴",
        "Medium-High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
    }
    priority_icon = priority_colors.get(paper.get("priority", ""), "⚪")

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{paper['title']}**")
            # Build metadata line with link
            meta = f"{paper.get('authors', 'N/A')} | {paper['journal']} ({paper['year']})"
            doi = paper.get("doi")
            url = paper.get("url")
            if doi:
                meta += f" | [DOI](https://doi.org/{doi})"
            elif url:
                meta += f" | [Link]({url})"
            st.caption(meta)
        with col2:
            st.markdown(f"{priority_icon} **{paper.get('priority', 'N/A')}**")

        # Tags
        tag_str = " ".join(f"`{t}`" for t in paper.get("tags", [])[:5])
        if tag_str:
            st.markdown(tag_str)

        if show_detail:
            content = read_local_file(paper["file"])
            if content:
                tldr = extract_tldr(content)
                if tldr:
                    st.info(tldr)

                with st.expander("전체 리뷰", expanded=False):
                    st.markdown(content, unsafe_allow_html=False)
