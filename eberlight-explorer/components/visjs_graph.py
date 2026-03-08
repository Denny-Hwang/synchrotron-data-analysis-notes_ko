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
            .mode-btn {{
                padding: 6px 16px; border: 2px solid #ccc; border-radius: 8px;
                background: #fff; cursor: pointer; font-size: 13px; color: #555;
                transition: all 0.2s;
            }}
            .mode-btn.active {{ border-color: #00D4AA; background: #E6FFF9; color: #007A5E; font-weight: 600; }}
            .mode-btn:hover {{ border-color: #00D4AA; }}
        </style>
    </head>
    <body>
        <div id="controls">
            <button class="mode-btn {"active" if not hierarchical else ""}" id="btnPhysics" onclick="switchMode('physics')">
                🌀 힘 기반 배치
            </button>
            <button class="mode-btn {"active" if hierarchical else ""}" id="btnHier" onclick="switchMode('hierarchy')">
                📊 계층적 배치
            </button>
            <button class="mode-btn" id="btnFreeze" onclick="switchMode('freeze')">
                ❄️ 고정
            </button>
            <span style="margin-left:auto; font-size:12px; color:#999;">
                노드 드래그 &middot; 스크롤로 확대/축소 &middot; 클릭하여 강조
            </span>
        </div>
        <div id="graph"></div>
        <script>
            var nodeList = {nodes_json};
            var edgeList = {edges_json};
            var originalColors = {{}};
            nodeList.forEach(function(n) {{ originalColors[n.id] = JSON.parse(JSON.stringify(n.color)); }});

            var container = document.getElementById('graph');
            var network = null;
            var currentMode = '{"hierarchy" if hierarchical else "physics"}';

            function buildOptions(mode) {{
                var base = {{
                    interaction: {{
                        hover: true, tooltipDelay: 200, zoomView: true,
                        dragNodes: true, dragView: true,
                    }},
                    nodes: {{ scaling: {{ min: 12, max: 40 }} }},
                    edges: {{ selectionWidth: 2, hoverWidth: 2 }},
                }};

                if (mode === 'hierarchy') {{
                    base.layout = {{
                        hierarchical: {{
                            enabled: true, direction: 'UD', sortMethod: 'directed',
                            levelSeparation: 130, nodeSpacing: 160,
                            treeSpacing: 200, blockShifting: true,
                            edgeMinimization: true, parentCentralization: true,
                        }}
                    }};
                    base.physics = {{ enabled: false }};
                }} else if (mode === 'physics') {{
                    base.layout = {{ hierarchical: false, improvedLayout: false, randomSeed: 42 }};
                    base.physics = {{
                        enabled: true, solver: 'forceAtlas2Based',
                        forceAtlas2Based: {{
                            gravitationalConstant: -80, centralGravity: 0.01,
                            springLength: 180, springConstant: 0.04,
                            damping: 0.4, avoidOverlap: 0.8,
                        }},
                        stabilization: {{ iterations: 300, updateInterval: 25 }},
                    }};
                }} else {{ /* freeze */
                    base.layout = {{ hierarchical: false }};
                    base.physics = {{ enabled: false }};
                }}
                return base;
            }}

            function createNetwork(mode) {{
                /* 이전 네트워크를 파괴하여 위치를 완전히 초기화 */
                if (network) {{ network.destroy(); network = null; }}

                /* 노드를 깊은 복사하여 vis.js가 원본을 변경하지 않도록 함 */
                var freshNodes = JSON.parse(JSON.stringify(nodeList));
                /* x/y를 제거하여 위치가 재계산되도록 함 */
                freshNodes.forEach(function(n) {{ delete n.x; delete n.y; }});

                var nodesDS = new vis.DataSet(freshNodes);
                var edgesDS = new vis.DataSet(JSON.parse(JSON.stringify(edgeList)));
                var opts = buildOptions(mode);

                network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, opts);

                /* 클릭 시 이웃 노드 강조 */
                network.on("click", function(params) {{
                    if (params.nodes.length > 0) {{
                        var sel = params.nodes[0];
                        var conn = network.getConnectedNodes(sel);
                        nodesDS.get().forEach(function(n) {{
                            if (n.id === sel || conn.indexOf(n.id) !== -1) {{
                                nodesDS.update({{ id: n.id, color: originalColors[n.id], font: {{ color: '#1A1A2E' }} }});
                            }} else {{
                                nodesDS.update({{ id: n.id, color: {{ background: '#E0E0E0', border: '#CCC' }}, font: {{ color: '#CCC' }} }});
                            }}
                        }});
                    }} else {{
                        nodesDS.get().forEach(function(n) {{
                            nodesDS.update({{ id: n.id, color: originalColors[n.id], font: {{ color: '#1A1A2E' }} }});
                        }});
                    }}
                }});
            }}

            function switchMode(mode) {{
                currentMode = mode;
                document.getElementById('btnPhysics').className = 'mode-btn' + (mode === 'physics' ? ' active' : '');
                document.getElementById('btnHier').className = 'mode-btn' + (mode === 'hierarchy' ? ' active' : '');
                document.getElementById('btnFreeze').className = 'mode-btn' + (mode === 'freeze' ? ' active' : '');

                if (mode === 'freeze') {{
                    /* 물리만 비활성화하고 현재 위치 유지 */
                    if (network) network.setOptions({{ physics: {{ enabled: false }} }});
                }} else {{
                    /* 깨끗한 레이아웃을 위해 파괴 후 재생성 */
                    createNetwork(mode);
                }}
            }}

            /* 초기 렌더링 */
            createNetwork(currentMode);
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
