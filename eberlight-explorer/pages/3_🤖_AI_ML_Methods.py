"""AI/ML 방법 분류 체계 지도 (F3)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import load_yaml, read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.markdown_viewer import render_markdown
from components.mermaid_diagram import render_mermaid
from components.visjs_graph import render_visjs_graph

st.set_page_config(page_title="AI/ML 방법", page_icon="🤖", layout="wide")

inject_styles()

level = render_level_selector(key="aiml_level")
categories = load_yaml("method_taxonomy.yaml")["categories"]
modalities = load_yaml("modality_metadata.yaml")["modalities"]
papers = load_yaml("publication_catalog.yaml")["publications"]

st.title("🤖 AI/ML 방법")
st.markdown("싱크로트론 데이터 분석에 적용되는 머신러닝 및 AI 방법.")

# ── 카테고리-논문 매핑 ────────────────────────────────
_cat_paper_map = {}
for p in papers:
    _cat_paper_map.setdefault(p["category"], []).append(p)

# ── 카테고리별 대표 다이어그램 ─────────────────────────
CATEGORY_DIAGRAMS = {
    "image_segmentation": {
        "code": """graph LR
    A["원본 이미지\\n2D/3D 볼륨"] --> B["인코더\\n특징 추출"]
    B --> C["병목\\n압축된 특징"]
    C --> D["디코더\\n업샘플링 + Skip"]
    D --> E["픽셀별\\n클래스 맵"]
    F["정답 레이블\\n마스크"] -.->|"Dice + CE Loss"| D
    style E fill:#00D4AA,color:#fff""",
        "caption": "U-Net 분할 파이프라인: 인코더가 다중 스케일 특징을 추출하고, Skip 연결이 있는 디코더가 픽셀 수준의 분류를 생성합니다.",
        "height": 280,
    },
    "denoising": {
        "code": """graph LR
    A["저선량\\n노이즈 입력"] --> B["생성자\\nU-Net"]
    B --> C["노이즈 제거\\n출력"]
    D["판별자\\nPatchGAN"] -.->|"적대적"| B
    E["VGG-16"] -.->|"지각적"| B
    F["깨끗한\\n목표"] -.->|"L1 픽셀"| B
    style C fill:#FFB800,color:#fff""",
        "caption": "GAN 기반 노이즈 제거: 생성자가 깨끗한 이미지를 생성하고, 판별자와 지각적 손실이 텍스처의 사실성을 보존합니다.",
        "height": 280,
    },
    "reconstruction": {
        "code": """graph LR
    A["회절\\n패턴"] --> B["CNN\\n인코더-디코더"]
    B --> C["위상 +\\n진폭"]
    C --> D["오버랩\\n스티칭"]
    D --> E["선택적\\n반복 정제"]
    E --> F["재구성된\\n객체"]
    style F fill:#1B3A5C,color:#fff""",
        "caption": "CNN이 반복적 위상 복원을 대체: 단일 순전파로 초기 재구성을 생성하고, 선택적 정제가 세부 사항을 복원합니다.",
        "height": 280,
    },
    "autonomous_experiment": {
        "code": """graph LR
    A["측정"] --> B["특징\\n추출"]
    B --> C["AI 결정\\n엔진"]
    C --> D["다음 동작:\\n스캔 / 이동 / 중지"]
    D -->|"피드백 루프"| A
    E["사전\\n지식"] -.-> C
    style C fill:#E8515D,color:#fff""",
        "caption": "자율 실험 루프: AI가 실시간 측정 데이터를 분석하고 사람의 개입 없이 다음 실험 동작을 결정합니다.",
        "height": 280,
    },
    "multimodal_integration": {
        "code": """graph TB
    A["XRF 맵"] --> D["결합\\n특징 공간"]
    B["타이코그래피"] --> D
    C["분광법"] --> D
    D --> E["상관관계\\n분석"]
    E --> F["융합된\\n통찰"]
    style D fill:#9B59B6,color:#fff""",
        "caption": "다중모달 통합은 여러 X선 기법의 데이터를 공유 표현으로 융합하여 더 풍부한 과학적 통찰을 제공합니다.",
        "height": 300,
    },
}

# ── 방법별 다이어그램 ──────────────────────────────────
METHOD_DIAGRAMS = {
    "unet_variants": {
        "code": """graph TB
    A["입력 이미지"] --> B["Conv+BN+ReLU x2"]
    B --> C["MaxPool"]
    C --> D["Conv+BN+ReLU x2"]
    D --> E["MaxPool"]
    E --> F["병목"]
    F --> G["UpConv + Skip"]
    G --> H["Conv+BN+ReLU x2"]
    H --> I["UpConv + Skip"]
    I --> J["Conv 1x1"]
    J --> K["분할 맵"]
    B -.->|skip| I
    D -.->|skip| G""",
        "height": 400,
    },
    "tomogan": {
        "code": """graph LR
    A["노이즈 슬라이스"] --> B["U-Net 생성자"]
    B --> C["노이즈 제거 슬라이스"]
    D["PatchGAN\\n판별자"] -.-> B
    E["VGG 지각적"] -.-> B
    F["L1 손실"] -.-> B""",
        "height": 250,
    },
    "deep_residual_xrf": {
        "code": """graph LR
    A["저해상도 XRF"] --> B["Bicubic 업스케일"]
    B --> C["Deep Residual\\n블록 x16"]
    C --> D["잔차\\n학습"]
    D --> E["초해상도\\nXRF 맵"]""",
        "height": 250,
    },
    "ptychonet": {
        "code": """graph LR
    A["회절 패턴"] --> B["CNN 인코더"]
    B --> C["잠재 4x4x512"]
    C --> D["CNN 디코더"]
    D --> E["위상 + 진폭"]
    E --> F["ePIE 정제 5-20 iter"]""",
        "height": 250,
    },
    "ai_nerd": {
        "code": """graph LR
    A["XPCS 스펙클"] --> B["특징 추출"]
    B --> C["비지도\\n핑거프린팅"]
    C --> D["동역학 맵"]
    D --> E["결정 엔진"]
    E -->|"다음"| A""",
        "height": 250,
    },
    "roi_finder": {
        "code": """graph LR
    A["XRF 서베이"] --> B["PCA k=3-5"]
    B --> C["퍼지 C-평균"]
    C --> D["멤버십 맵"]
    D --> E["ROI 점수화"]
    E --> F["바운딩 박스"]""",
        "height": 250,
    },
    "bayesian_opt": {
        "code": """graph LR
    A["초기 샘플"] --> B["대리 모델\\nGaussian Process"]
    B --> C["획득\\n함수"]
    C --> D["다음 샘플\\n포인트"]
    D --> E["실험"]
    E -->|"업데이트"| B""",
        "height": 250,
    },
    "ki_bo_xanes": {
        "code": """graph LR
    A["시드 포인트"] --> B["GP 서로게이트"]
    B --> C["지식 주입\\n획득 함수"]
    C --> D["다음 에너지 E*"]
    D --> E["XANES 측정"]
    E -->|"GP 업데이트"| B
    F["에지 사전확률"] -.-> C
    G["기울기 ∂μ/∂E"] -.-> C""",
        "height": 280,
    },
}


def _build_method_graph():
    """방법 분류 체계를 위한 vis.js 그래프 노드/엣지를 구축합니다."""
    nodes = []
    edges = []
    mod_map = {m["id"]: m for m in modalities}

    # 중앙 루트 노드
    nodes.append({
        "id": "root", "label": "싱크로트론을 위한\nAI/ML",
        "group": "root", "size": 35,
        "color": "#1A1A2E", "level": 0,
        "font_size": 14,
    })

    # 카테고리 노드
    for cat in categories:
        nodes.append({
            "id": cat["id"], "label": cat["name"],
            "group": "category", "size": 28,
            "color": {"image_segmentation": "#00D4AA", "denoising": "#FFB800",
                      "reconstruction": "#1B3A5C", "autonomous_experiment": "#E8515D",
                      "multimodal_integration": "#9B59B6"}.get(cat["id"], "#888"),
            "level": 1, "font_size": 13,
        })
        edges.append({"from": "root", "to": cat["id"], "label": ""})

    # 방법 노드
    for cat in categories:
        for m in cat["methods"]:
            nodes.append({
                "id": m["id"], "label": m["name"],
                "group": "method", "size": 18,
                "color": {"image_segmentation": "#66E8CC", "denoising": "#FFD566",
                          "reconstruction": "#4D7A9E", "autonomous_experiment": "#F08A90",
                          "multimodal_integration": "#C39BD3"}.get(cat["id"], "#AAA"),
                "level": 2, "font_size": 11,
            })
            edges.append({"from": cat["id"], "to": m["id"], "label": ""})

    # 모달리티 노드
    for cat in categories:
        for mod_id in cat.get("modalities", []):
            if mod_id in mod_map:
                mod = mod_map[mod_id]
                # 이미 추가된 경우 중복 방지
                if not any(n["id"] == mod_id for n in nodes):
                    nodes.append({
                        "id": mod_id, "label": mod["short_name"],
                        "group": "modality", "size": 22,
                        "color": "#FF6B6B", "level": 3,
                        "shape": "diamond", "font_size": 11,
                    })
                edges.append({
                    "from": cat["id"], "to": mod_id,
                    "label": "적용 대상", "dashes": True,
                })

    return nodes, edges


# ── 인터랙티브 방법 분류 체계 그래프 ──────────────────
st.markdown("---")
st.subheader("🗺️ 방법 분류 체계 지도")
st.caption("싱크로트론 과학을 위한 AI/ML 방법의 전체 지형을 탐색하세요. "
           "노드를 클릭하면 연결 관계가 강조됩니다. 계층 구조 보기를 전환할 수 있습니다.")

method_nodes, method_edges = _build_method_graph()
render_visjs_graph(method_nodes, method_edges, hierarchical=True, height=550)

# ── 레벨별 콘텐츠 ──────────────────────────────────────
if level == "L0":
    st.markdown("---")
    cols = st.columns(len(categories))
    for col, cat in zip(cols, categories):
        with col:
            with st.container(border=True):
                st.markdown(f"### {cat['icon']}")
                st.markdown(f"**{cat['name']}**")
                st.caption(cat["description"])
                st.metric("방법", len(cat["methods"]))

elif level == "L1":
    # 카테고리 개요 및 대표 다이어그램
    st.markdown("---")
    st.subheader("방법 카테고리")
    for cat in categories:
        with st.expander(f"{cat['icon']} {cat['name']} ({len(cat['methods'])}개 방법)", expanded=True):
            desc_col, diag_col = st.columns([1, 1])
            with desc_col:
                st.markdown(cat["description"])
                st.markdown("**방법:**")
                for m in cat["methods"]:
                    st.markdown(f"- **{m['name']}**")
                applicable = ", ".join(cat["modalities"])
                st.caption(f"적용 가능한 모달리티: {applicable}")

                # 관련 논문 표시
                cat_papers = _cat_paper_map.get(cat["id"], [])
                if cat_papers:
                    st.markdown("**관련 논문:**")
                    for p in cat_papers[:3]:
                        doi = p.get("doi", "")
                        link = f" — [DOI](https://doi.org/{doi})" if doi else ""
                        st.markdown(f"- [{p['year']}] {p['title']}{link}")

            with diag_col:
                diag = CATEGORY_DIAGRAMS.get(cat["id"])
                if diag:
                    render_mermaid(diag["code"], height=diag["height"])
                    st.caption(diag["caption"])

    # 히트맵
    st.markdown("---")
    st.subheader("모달리티 × 방법 매트릭스")
    import pandas as pd

    mod_names = [f"{m['icon']} {m['short_name']}" for m in modalities]
    matrix = []
    for m in modalities:
        row = {}
        for c in categories:
            row[c["name"]] = "Y" if m["id"] in c["modalities"] else "-"
        matrix.append(row)
    df = pd.DataFrame(matrix, index=mod_names)
    st.dataframe(df, use_container_width=True)

elif level == "L2":
    # 방법 상세 카드 및 다이어그램
    st.markdown("---")
    cat_names = [f"{c['icon']} {c['name']}" for c in categories]
    selected_cat_name = st.selectbox("카테고리 선택", options=cat_names)
    cat_idx = cat_names.index(selected_cat_name)
    cat = categories[cat_idx]

    st.subheader(f"{cat['icon']} {cat['name']}")
    st.markdown(cat["description"])

    # 카테고리 다이어그램 표시
    cat_diag = CATEGORY_DIAGRAMS.get(cat["id"])
    if cat_diag:
        with st.expander("📊 카테고리 개요 다이어그램", expanded=True):
            render_mermaid(cat_diag["code"], height=cat_diag["height"])
            st.caption(cat_diag["caption"])

    method_names = [m["name"] for m in cat["methods"]]
    selected_method = st.selectbox("방법 선택", options=method_names)
    method = next(m for m in cat["methods"] if m["name"] == selected_method)

    st.markdown("---")

    # 방법별 다이어그램이 있으면 표시
    m_diag = METHOD_DIAGRAMS.get(method["id"])
    if m_diag:
        diag_col, content_col = st.columns([1, 1])
        with diag_col:
            st.markdown(f"#### {method['name']} 아키텍처")
            render_mermaid(m_diag["code"], height=m_diag["height"])
        with content_col:
            render_markdown(method["file"], show_title=True)
    else:
        render_markdown(method["file"], show_title=True)

    # 관련 논문 및 주요 결과 표시
    cat_papers = _cat_paper_map.get(cat["id"], [])
    if cat_papers:
        st.markdown("---")
        st.subheader("📚 관련 논문 결과")
        for p in cat_papers:
            from utils.content_parser import read_local_file, extract_section
            content = read_local_file(p["file"])
            if not content:
                continue
            with st.expander(f"[{p['year']}] {p['title']}", expanded=False):
                key_results = extract_section(content, "Key Results")
                if key_results:
                    st.markdown(key_results)
                doi = p.get("doi", "")
                if doi:
                    st.markdown(f"[전체 논문 (DOI)](https://doi.org/{doi})")

elif level == "L3":
    # 소스 보기
    all_files = []
    for cat in categories:
        for m in cat["methods"]:
            all_files.append((f"{cat['icon']} {cat['name']} / {m['name']}", m["file"]))

    selected = st.selectbox("파일 선택", options=all_files, format_func=lambda x: x[0])
    content = read_local_file(selected[1])
    if content:
        st.code(content, language="markdown")
