"""Streamlit HTML 컴포넌트를 통한 mermaid.js CDN을 사용하는 Mermaid 다이어그램 렌더러."""

import streamlit as st
import streamlit.components.v1 as components
import hashlib


def render_mermaid(mermaid_code: str, height: int = 400):
    """Render a Mermaid diagram using mermaid.js via an iframe HTML component.

    Args:
        mermaid_code: Raw Mermaid diagram code (without ```mermaid fences).
        height: Height of the rendered diagram in pixels.
    """
    # Clean up the code - remove markdown fences if present
    code = mermaid_code.strip()
    if code.startswith("```mermaid"):
        code = code[len("```mermaid"):].strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()

    # Generate unique ID for this diagram
    diagram_id = "mermaid_" + hashlib.md5(code.encode()).hexdigest()[:8]

    html = f"""
    <div style="background: white; border-radius: 8px; padding: 16px; border: 1px solid #E8EEF6;">
        <div id="{diagram_id}" class="mermaid">
{code}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#E8EEF6',
                primaryBorderColor: '#00D4AA',
                primaryTextColor: '#1A1A2E',
                lineColor: '#1B3A5C',
                secondaryColor: '#F0F4FA',
                tertiaryColor: '#FFF8E1',
                fontSize: '14px'
            }},
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
    """
    components.html(html, height=height, scrolling=False)
