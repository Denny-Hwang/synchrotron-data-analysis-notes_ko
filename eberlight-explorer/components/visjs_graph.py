"""계층 토글이 있는 vis.js 기반 지식 그래프 렌더러."""

import json
import hashlib
import streamlit as st
import streamlit.components.v1 as components


def render_visjs_graph(nodes: list[dict], edges: list[dict],
                       hierarchical: bool = False, height: int = 650):
    """vis.js Network를 사용하여 인터랙티브 지식 그래프를 렌더링합니다.

    Args:
        nodes: list of {id, label, group, size, color, level?}
        edges: list of {from, to, label?, dashes?}
        hierarchical: if True, use hierarchical layout
        height: height in pixels
    """
    # Convert nodes for vis.js format
    vis_nodes = []
    for n in nodes:
        node = {
            "id": n["id"],
            "label": n["label"],
            "group": n.get("group", "default"),
            "size": n.get("size", 20),
            "color": {
                "background": n.get("color", "#97C2FC"),
                "border": _darken(n.get("color", "#97C2FC")),
                "highlight": {
                    "background": _lighten(n.get("color", "#97C2FC")),
                    "border": n.get("color", "#97C2FC"),
                },
            },
            "font": {
                "size": n.get("font_size", 13),
                "color": "#1A1A2E",
                "face": "sans-serif",
                "bold": {"color": "#1A1A2E"},
            },
            "shadow": {
                "enabled": True,
                "color": "rgba(0,0,0,0.15)",
                "size": 8,
                "x": 3,
                "y": 3,
            },
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "shape": n.get("shape", "dot"),
        }
        if "level" in n:
            node["level"] = n["level"]
        vis_nodes.append(node)

    # Convert edges
    vis_edges = []
    for e in edges:
        edge = {
            "from": e["from"],
            "to": e["to"],
            "color": {"color": "#B0B0B0", "highlight": "#00D4AA", "opacity": 0.6},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.6}},
            "smooth": {"type": "cubicBezier", "roundness": 0.4},
            "width": 1.5,
        }
        if e.get("label"):
            edge["label"] = e["label"]
            edge["font"] = {"size": 10, "color": "#888", "strokeWidth": 0}
        if e.get("dashes"):
            edge["dashes"] = True
        vis_edges.append(edge)

    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)

    layout_config = ""
    if hierarchical:
        layout_config = """
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 120,
                    nodeSpacing: 180,
                    treeSpacing: 200,
                    blockShifting: true,
                    edgeMinimization: true,
                }
            },
        """
    else:
        layout_config = """
            layout: {
                hierarchical: false,
                improvedLayout: true,
            },
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; font-family: sans-serif; }}
            #graph {{ width: 100%; height: {height}px; border: 1px solid #E8EEF6; border-radius: 12px; background: #FAFCFF; }}
            #controls {{ padding: 8px 12px; display: flex; gap: 12px; align-items: center; }}
            #controls label {{ font-size: 13px; color: #555; cursor: pointer; }}
            #controls input {{ cursor: pointer; }}
            #legend {{ display: flex; gap: 16px; padding: 6px 12px; flex-wrap: wrap; }}
            .legend-item {{ display: flex; align-items: center; gap: 5px; font-size: 13px; color: #444; }}
            .legend-dot {{ width: 14px; height: 14px; border-radius: 50%; box-shadow: 2px 2px 4px rgba(0,0,0,0.15); }}
        </style>
    </head>
    <body>
        <div id="controls">
            <label><input type="checkbox" id="hierToggle" {"checked" if hierarchical else ""}
                   onchange="toggleLayout()"> 계층적 레이아웃</label>
            <label><input type="checkbox" id="physToggle" {"" if hierarchical else "checked"}
                   onchange="togglePhysics()"> 물리 시뮬레이션</label>
            <label style="margin-left:auto; font-size:12px; color:#999;">
                노드를 드래그하여 재배치 &middot; 스크롤하여 확대/축소 &middot; 클릭하여 강조
            </label>
        </div>
        <div id="graph"></div>
        <div id="legend">
            <div class="legend-item"><div class="legend-dot" style="background:#00D4AA;"></div> 모달리티 (6)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#FFB800;"></div> AI/ML 방법 (5)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#1B3A5C;"></div> 논문 (13)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#E8515D;"></div> 도구 (6)</div>
            <div class="legend-item" style="margin-left:auto; font-size:12px; color:#aaa;">― 실선 = 사용 &nbsp; - - 점선 = 지원</div>
        </div>
        <script>
            // Store original colors for highlight reset
            var nodeList = {nodes_json};
            var edgeList = {edges_json};
            var originalColors = {{}};
            nodeList.forEach(function(n) {{ originalColors[n.id] = JSON.parse(JSON.stringify(n.color)); }});

            var nodesData = new vis.DataSet(nodeList);
            var edgesData = new vis.DataSet(edgeList);
            var container = document.getElementById('graph');

            var options = {{
                {layout_config}
                physics: {{
                    enabled: {"false" if hierarchical else "true"},
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -60,
                        centralGravity: 0.008,
                        springLength: 160,
                        springConstant: 0.04,
                        damping: 0.4,
                        avoidOverlap: 0.8,
                    }},
                    stabilization: {{ iterations: 200 }},
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200,
                    zoomView: true,
                    dragNodes: true,
                    dragView: true,
                    navigationButtons: false,
                    keyboard: false,
                    multiselect: true,
                }},
                nodes: {{
                    scaling: {{ min: 12, max: 40 }},
                }},
                edges: {{
                    selectionWidth: 2,
                    hoverWidth: 2,
                }},
            }};

            var network = new vis.Network(container, {{ nodes: nodesData, edges: edgesData }}, options);

            // Highlight neighbors on click
            network.on("click", function(params) {{
                if (params.nodes.length > 0) {{
                    var selectedNode = params.nodes[0];
                    var connectedNodes = network.getConnectedNodes(selectedNode);

                    nodesData.get().forEach(function(n) {{
                        if (n.id === selectedNode || connectedNodes.indexOf(n.id) !== -1) {{
                            nodesData.update({{ id: n.id, color: originalColors[n.id], font: {{ color: '#1A1A2E' }} }});
                        }} else {{
                            nodesData.update({{ id: n.id, color: {{ background: '#E0E0E0', border: '#CCC' }}, font: {{ color: '#CCC' }} }});
                        }}
                    }});
                }} else {{
                    // Reset all
                    nodesData.get().forEach(function(n) {{
                        nodesData.update({{ id: n.id, color: originalColors[n.id], font: {{ color: '#1A1A2E' }} }});
                    }});
                }}
            }});

            function toggleLayout() {{
                var hier = document.getElementById('hierToggle').checked;
                var physEl = document.getElementById('physToggle');

                if (hier) {{
                    physEl.checked = false;
                    network.setOptions({{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'UD',
                                sortMethod: 'directed',
                                levelSeparation: 120,
                                nodeSpacing: 180,
                            }}
                        }},
                        physics: {{ enabled: false }},
                    }});
                }} else {{
                    physEl.checked = true;
                    network.setOptions({{
                        layout: {{ hierarchical: false }},
                        physics: {{
                            enabled: true,
                            solver: 'forceAtlas2Based',
                        }},
                    }});
                }}
            }}

            function togglePhysics() {{
                var phys = document.getElementById('physToggle').checked;
                var hierEl = document.getElementById('hierToggle');
                if (phys) {{
                    hierEl.checked = false;
                    network.setOptions({{
                        layout: {{ hierarchical: false }},
                        physics: {{ enabled: true }},
                    }});
                }} else {{
                    network.setOptions({{ physics: {{ enabled: false }} }});
                }}
            }}
        </script>
    </body>
    </html>
    """
    components.html(html, height=height + 80, scrolling=False)


def _darken(hex_color: str) -> str:
    """16진수 색상을 20% 어둡게 합니다."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color: str) -> str:
    """16진수 색상을 20% 밝게 합니다."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * 0.3))
    g = min(255, int(g + (255 - g) * 0.3))
    b = min(255, int(b + (255 - b) * 0.3))
    return f"#{r:02x}{g:02x}{b:02x}"
