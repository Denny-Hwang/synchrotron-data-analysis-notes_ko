"""시각화를 위한 교차 참조 그래프 데이터 구축."""

from utils.content_parser import load_yaml


def build_knowledge_graph() -> tuple[list[dict], list[dict]]:
    """지식 그래프의 노드와 엣지를 구축합니다.

    (노드, 엣지)를 반환합니다. 각 노드는 {id, label, group, size, color, level}
    각 엣지는 {from, to, label, dashes?}를 가집니다.
    """
    modalities = load_yaml("modality_metadata.yaml")["modalities"]
    methods = load_yaml("method_taxonomy.yaml")["categories"]
    papers = load_yaml("publication_catalog.yaml")["publications"]
    tools = load_yaml("tool_catalog.yaml")["tools"]
    cross_refs = load_yaml("cross_references.yaml")

    nodes = []
    edges = []

    # 모달리티 노드 — 최상위 수준
    for m in modalities:
        nodes.append({
            "id": m["id"],
            "label": m["short_name"],
            "group": "modality",
            "size": 30,
            "color": "#00D4AA",
            "level": 0,
        })

    # 방법 카테고리 노드 — 중간 수준
    for cat in methods:
        nodes.append({
            "id": cat["id"],
            "label": cat["name"],
            "group": "method",
            "size": 25,
            "color": "#FFB800",
            "level": 1,
        })

    # 논문 노드 — 하위 수준
    for p in papers:
        nodes.append({
            "id": p["id"],
            "label": f"{p['year']} {p['title'][:30]}...",
            "group": "paper",
            "size": 15,
            "color": "#1B3A5C",
            "level": 2,
        })

    # 도구 노드 — 하위 수준
    for t in tools:
        if t["id"] == "aps_github_repos":
            continue
        nodes.append({
            "id": t["id"],
            "label": t["name"],
            "group": "tool",
            "size": 20,
            "color": "#E8515D",
            "level": 2,
        })

    # 모달리티 -> 방법 엣지
    mod_method = cross_refs.get("modality_method", {})
    for mod_id, method_ids in mod_method.items():
        for method_id in method_ids:
            edges.append({
                "from": mod_id,
                "to": method_id,
                "label": "uses",
            })

    # 방법 -> 논문 엣지
    method_paper = cross_refs.get("method_paper", {})
    for method_id, paper_ids in method_paper.items():
        for cat in methods:
            for m in cat["methods"]:
                if m["id"] == method_id or method_id in m["id"]:
                    for pid in paper_ids:
                        edges.append({
                            "from": cat["id"],
                            "to": pid,
                            "label": "reviewed in",
                        })

    # 도구 -> 모달리티 엣지 (점선)
    for t in tools:
        if t.get("pipeline_stage"):
            for mod_id in t.get("modalities", []):
                edges.append({
                    "from": t["id"],
                    "to": mod_id,
                    "label": "supports",
                    "dashes": True,
                })

    return nodes, edges
