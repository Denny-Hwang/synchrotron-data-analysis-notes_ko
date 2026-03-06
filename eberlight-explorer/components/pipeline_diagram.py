"""인터랙티브 파이프라인 다이어그램 컴포넌트."""

import streamlit as st
from utils.content_parser import load_yaml


def render_pipeline_diagram():
    """데이터 파이프라인을 화살표가 있는 시각적 흐름으로 렌더링합니다."""
    cross_refs = load_yaml("cross_references.yaml")
    stages = cross_refs.get("pipeline_stages", [])

    # Build an HTML-based pipeline with arrows
    html_parts = []
    for i, stage in enumerate(stages):
        tools_html = "<br>".join(stage.get("tools", []) or ["—"])
        html_parts.append(
            f"<div style='flex:1; text-align:center; padding:14px 8px; "
            f"background:linear-gradient(135deg, #E8EEF6, #D4DFEF); border-radius:12px; "
            f"min-height:130px; display:flex; flex-direction:column; "
            f"justify-content:center; align-items:center; "
            f"border: 2px solid #C0D0E0;'>"
            f"<div style='font-size:2rem;'>{stage['icon']}</div>"
            f"<div style='font-weight:700; font-size:1.05rem; margin:4px 0;'>{stage['name']}</div>"
            f"<div style='font-size:0.88rem; color:#555;'>{tools_html}</div>"
            f"</div>"
        )
        if i < len(stages) - 1:
            html_parts.append(
                "<div style='display:flex; align-items:center; padding:0 2px; "
                "font-size:1.5rem; color:#00D4AA; font-weight:bold;'>→</div>"
            )

    full_html = (
        "<div style='display:flex; align-items:stretch; gap:0; width:100%;'>"
        + "".join(html_parts)
        + "</div>"
    )
    st.markdown(full_html, unsafe_allow_html=True)
