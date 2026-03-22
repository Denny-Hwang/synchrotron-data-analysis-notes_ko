"""노이즈 & 아티팩트 카탈로그 탐색기 (F8)."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import read_local_file
from components.level_selector import render_level_selector
from components.common_styles import inject_styles
from components.markdown_viewer import render_markdown

st.set_page_config(page_title="노이즈 & 아티팩트 카탈로그", page_icon="📡", layout="wide")

inject_styles()

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

level = render_level_selector(key="noise_level")

st.title("📡 노이즈 & 아티팩트 카탈로그")
st.markdown("싱크로트론 모달리티 전반에 걸친 29종 노이즈 및 아티팩트 유형 — 탐지, 보정, 트러블슈팅.")

MODALITIES = {
    "토모그래피": {
        "icon": "🔬",
        "files": [
            ("링 아티팩트", "09_noise_catalog/tomography/ring_artifact.md"),
            ("징거", "09_noise_catalog/tomography/zinger.md"),
            ("스트릭 아티팩트", "09_noise_catalog/tomography/streak_artifact.md"),
            ("저선량 노이즈", "09_noise_catalog/tomography/low_dose_noise.md"),
            ("희소 각도 아티팩트", "09_noise_catalog/tomography/sparse_angle_artifact.md"),
            ("모션 아티팩트", "09_noise_catalog/tomography/motion_artifact.md"),
            ("플랫필드 문제", "09_noise_catalog/tomography/flatfield_issues.md"),
            ("회전 중심 오류", "09_noise_catalog/tomography/rotation_center_error.md"),
            ("빔 강도 저하", "09_noise_catalog/tomography/beam_intensity_drop.md"),
        ],
    },
    "XRF 현미경": {
        "icon": "🔍",
        "files": [
            ("광자 계수 노이즈", "09_noise_catalog/xrf_microscopy/photon_counting_noise.md"),
            ("데드/핫 픽셀", "09_noise_catalog/xrf_microscopy/dead_hot_pixel.md"),
            ("피크 겹침", "09_noise_catalog/xrf_microscopy/peak_overlap.md"),
            ("자기 흡수", "09_noise_catalog/xrf_microscopy/self_absorption.md"),
            ("데드타임 포화", "09_noise_catalog/xrf_microscopy/dead_time_saturation.md"),
            ("I0 정규화", "09_noise_catalog/xrf_microscopy/i0_normalization.md"),
            ("프로브 흐림", "09_noise_catalog/xrf_microscopy/probe_blurring.md"),
            ("스캔 줄무늬", "09_noise_catalog/xrf_microscopy/scan_stripe.md"),
        ],
    },
    "분광학": {
        "icon": "📊",
        "files": [
            ("EXAFS 통계 노이즈", "09_noise_catalog/spectroscopy/statistical_noise_exafs.md"),
            ("에너지 교정 드리프트", "09_noise_catalog/spectroscopy/energy_calibration_drift.md"),
            ("고조파 오염", "09_noise_catalog/spectroscopy/harmonics_contamination.md"),
            ("자기 흡수 (XAS)", "09_noise_catalog/spectroscopy/self_absorption_xas.md"),
            ("방사선 손상", "09_noise_catalog/spectroscopy/radiation_damage.md"),
            ("이상치 스펙트럼", "09_noise_catalog/spectroscopy/outlier_spectra.md"),
        ],
    },
    "타이코그래피": {
        "icon": "🔬",
        "files": [
            ("부분 코히어런스", "09_noise_catalog/ptychography/partial_coherence.md"),
            ("위치 오류", "09_noise_catalog/ptychography/position_error.md"),
            ("스티칭 아티팩트", "09_noise_catalog/ptychography/stitching_artifact.md"),
        ],
    },
    "교차 분야": {
        "icon": "🔗",
        "files": [
            ("검출기 공통 문제", "09_noise_catalog/cross_cutting/detector_common_issues.md"),
            ("DL 환각", "09_noise_catalog/cross_cutting/dl_hallucination.md"),
            ("리청킹 데이터 무결성", "09_noise_catalog/cross_cutting/rechunking_data_integrity.md"),
        ],
    },
}

# 보정 전후 이미지 매핑: 노이즈 이름 -> 이미지 파일 (저장소 루트 기준 상대 경로)
BEFORE_AFTER_IMAGES = {
    "링 아티팩트": "09_noise_catalog/images/ring_artifact_before_after.png",
    "징거": "09_noise_catalog/images/zinger_before_after.png",
    "저선량 노이즈": "09_noise_catalog/images/low_dose_noise_before_after.png",
    "희소 각도 아티팩트": "09_noise_catalog/images/sparse_angle_before_after.png",
    "플랫필드 문제": "09_noise_catalog/images/flatfield_before_after.png",
    "회전 중심 오류": "09_noise_catalog/images/rotation_center_error_before_after.png",
    "데드/핫 픽셀": "09_noise_catalog/images/dead_hot_pixel_before_after.png",
    "I0 정규화": "09_noise_catalog/images/i0_drop_before_after.png",
}

# 전체 노이즈 항목 조회용 (이름 -> 문서 경로)
ALL_NOISE_DOCS = {}
for mod_data in MODALITIES.values():
    for name, path in mod_data["files"]:
        ALL_NOISE_DOCS[name] = path

# ── 트러블슈터 결정 트리 데이터 ─────────────────────
TROUBLESHOOTER_TREE = {
    "원형/링 패턴": {
        "description": "재구성 이미지에서 동심원 링 또는 원형 특징",
        "branches": [
            {
                "question": "링이 회전축에 중심을 두고 있습니까?",
                "yes": [
                    {"condition": "선명하고 잘 정의된 링", "diagnosis": "링 아티팩트", "severity": "심각"},
                    {"condition": "넓거나 흐린 부분 호", "diagnosis": "플랫필드 문제", "severity": "주요"},
                ],
                "no": [
                    {"condition": "물체 엣지가 이중으로 보임", "diagnosis": "회전 중심 오류", "severity": "심각"},
                    {"condition": "조밀한 포함물 주위의 링", "diagnosis": "스트릭 아티팩트", "severity": "심각"},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
sinogram = data[data.shape[0]//2]
col_std = np.std(sinogram, axis=0)
suspect_cols = np.where(col_std < np.median(col_std) * 0.1)[0]
print(f"데드 컬럼 (링 소스): {suspect_cols}")
```""",
    },
    "고립된 밝은/어두운 점": {
        "description": "실제 특징에 해당하지 않는 랜덤한 밝거나 어두운 점",
        "branches": [
            {
                "question": "어디에서 점이 보입니까?",
                "options": [
                    {"label": "원시 투영 (단일 프레임만)", "diagnosis": "징거", "severity": "주요"},
                    {"label": "원시 투영 (모든 프레임에서 동일 픽셀)", "diagnosis": "검출기 공통 문제", "severity": "주요"},
                    {"label": "XRF 맵 (비정상적으로 밝거나 어두운)", "diagnosis": "데드/핫 픽셀", "severity": "주요"},
                    {"label": "재구성된 CT (징거에서 유래)", "diagnosis": "징거", "severity": "주요"},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
diff = np.abs(np.diff(projections, axis=0))
threshold = np.median(diff) + 10 * np.std(diff)
zingers = np.where(diff > threshold)
print(f"잠재적 징거 발견: {len(zingers[0])}")
```""",
    },
    "스트릭/줄무늬 패턴": {
        "description": "데이터의 선형 스트릭, 줄무늬 또는 밴딩",
        "branches": [
            {
                "question": "방향과 맥락은?",
                "options": [
                    {"label": "조밀한 물체에서의 밝은 스트릭 (CT)", "diagnosis": "스트릭 아티팩트", "severity": "심각"},
                    {"label": "재구성 전체의 별 모양 스트릭", "diagnosis": "희소 각도 아티팩트", "severity": "주요"},
                    {"label": "사이노그램의 수평 줄무늬 (I0 저하)", "diagnosis": "빔 강도 저하", "severity": "주요"},
                    {"label": "사이노그램의 수직 줄무늬", "diagnosis": "링 아티팩트", "severity": "심각"},
                    {"label": "XRF 맵의 줄무늬 (스캔 방향)", "diagnosis": "스캔 줄무늬", "severity": "주요"},
                    {"label": "XRF 맵의 줄무늬 (I0 상관)", "diagnosis": "I0 정규화", "severity": "주요"},
                    {"label": "타일 경계의 줄무늬 (타이코그래피)", "diagnosis": "스티칭 아티팩트", "severity": "경미"},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
n_projections = projections.shape[0]
detector_width = projections.shape[-1]
nyquist = int(np.pi/2 * detector_width)
print(f"투영 수: {n_projections}, 나이퀴스트 최소: {nyquist}")
print(f"{'과소 샘플링' if n_projections < nyquist else '정상'}")
```""",
    },
    "전체적인 입자감/노이즈": {
        "description": "이미지 전체가 입자감 있고, 반점이 있거나 노이즈가 많음",
        "branches": [
            {
                "question": "어떤 유형의 데이터입니까?",
                "options": [
                    {"label": "CT 재구성 (균일 노이즈)", "diagnosis": "저선량 노이즈", "severity": "주요"},
                    {"label": "CT 재구성 (조밀 영역에서 더 심함)", "diagnosis": "스트릭 아티팩트", "severity": "주요"},
                    {"label": "CT 재구성 (엣지에서 더 심함)", "diagnosis": "플랫필드 문제", "severity": "주요"},
                    {"label": "XRF 맵 (저농도 원소가 더 노이즈)", "diagnosis": "광자 계수 노이즈", "severity": "주요"},
                    {"label": "XRF 맵 (모든 원소가 노이즈)", "diagnosis": "데드타임 포화", "severity": "주요"},
                    {"label": "EXAFS (높은 k에서 노이즈)", "diagnosis": "EXAFS 통계 노이즈", "severity": "주요"},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
roi_signal = recon[100:150, 100:150]
roi_bg = recon[10:30, 10:30]
snr = np.mean(roi_signal) / np.std(roi_bg)
print(f"SNR 추정: {snr:.1f} (< 5 매우 노이즈, > 20 양호)")
```""",
    },
    "흐림/디테일 손실": {
        "description": "특징이 흐리거나, 뭉개지거나, 예상보다 크게 보임",
        "branches": [
            {
                "question": "어떤 유형의 데이터입니까?",
                "options": [
                    {"label": "CT — 방향성 흐림", "diagnosis": "모션 아티팩트", "severity": "심각"},
                    {"label": "CT — 균일한 부드러움 (적은 투영?)", "diagnosis": "희소 각도 아티팩트", "severity": "주요"},
                    {"label": "CT — 이중 엣지", "diagnosis": "회전 중심 오류", "severity": "심각"},
                    {"label": "XRF — 특징이 예상보다 큼", "diagnosis": "프로브 흐림", "severity": "경미"},
                    {"label": "XRF — 일부 원소는 선명, 다른 것은 흐림", "diagnosis": "피크 겹침", "severity": "주요"},
                    {"label": "타이코그래피 — 균일한 대비 손실", "diagnosis": "부분 코히어런스", "severity": "주요"},
                    {"label": "타이코그래피 — FOV에 따라 변함", "diagnosis": "위치 오류", "severity": "심각"},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
from scipy.signal import correlate
shift_series = []
for i in range(projections.shape[0]-1):
    cc = np.correlate(projections[i].mean(0), projections[i+1].mean(0), 'full')
    shift_series.append(np.argmax(cc) - projections.shape[-1] + 1)
print(f"최대 투영간 이동: {max(np.abs(shift_series))} 픽셀")
```""",
    },
    "의심스럽게 '너무 좋은' 특징": {
        "description": "DL/AI 처리 결과가 너무 깨끗하거나 예상치 못한 디테일 포함",
        "branches": [
            {
                "question": "신경망을 적용했습니까?",
                "options": [
                    {"label": "예 — 저SNR 영역에서 고주파 디테일", "diagnosis": "DL 환각", "severity": "심각"},
                    {"label": "예 — 주기적/반복적 패턴 출현", "diagnosis": "DL 환각", "severity": "심각"},
                    {"label": "예 — 결과가 입력과 동일", "diagnosis": None, "severity": None, "note": "네트워크가 이 데이터 분포에 대해 훈련되지 않았을 수 있습니다."},
                    {"label": "아니오 — 신경망 미사용", "diagnosis": None, "severity": None, "note": "다른 증상 카테고리를 재검토하세요."},
                ],
            },
        ],
        "quick_check": """```python
import numpy as np
residual = dl_output - conventional_recon
residual_std = np.std(residual)
signal_std = np.std(conventional_recon)
print(f"잔차/신호 비율: {residual_std/signal_std:.3f}")
print(f"> 0.1이면 DL이 상당한 콘텐츠를 추가하고 있음 — 신중히 검증")
```""",
    },
}

SEVERITY_COLORS = {
    "심각": "red",
    "주요": "orange",
    "경미": "blue",
}


def _render_before_after_viewer(noise_name: str):
    """해당 노이즈 유형의 보정 전후 이미지를 표시합니다."""
    img_path = BEFORE_AFTER_IMAGES.get(noise_name)
    if not img_path:
        return False
    full_path = os.path.join(REPO_ROOT, img_path)
    if not os.path.exists(full_path):
        return False
    st.image(full_path, caption=f"{noise_name} — 보정 전 / 보정 후", use_container_width=True)
    return True


def _render_summary_table_interactive():
    """클릭 가능한 보정 전후 이미지가 포함된 요약 표를 렌더링합니다."""
    import pandas as pd

    st.subheader("요약 표")
    st.markdown("29종 노이즈/아티팩트 유형의 전체 매트릭스. **보기**를 클릭하여 보정 전후 비교를 확인하세요.")

    rows = []
    for mod_name, mod_data in MODALITIES.items():
        for name, path in mod_data["files"]:
            has_ba = name in BEFORE_AFTER_IMAGES
            rows.append({
                "모달리티": f"{mod_data['icon']} {mod_name}",
                "노이즈/아티팩트": name,
                "보정 전후": "있음" if has_ba else "없음",
                "_path": path,
                "_has_ba": has_ba,
            })

    # 모달리티별 필터
    mod_options = ["전체"] + list(MODALITIES.keys())
    selected_filter = st.selectbox("모달리티별 필터", mod_options, key="summary_filter")
    if selected_filter != "전체":
        rows = [r for r in rows if selected_filter in r["모달리티"]]

    # 표 표시
    df = pd.DataFrame(rows)
    display_df = df[["모달리티", "노이즈/아티팩트", "보정 전후"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 보정 전후 뷰어 섹션
    ba_items = [r for r in rows if r["_has_ba"]]
    if ba_items:
        st.markdown("---")
        st.subheader("보정 전후 비교")
        selected_ba = st.selectbox(
            "보정 전후를 볼 노이즈 유형 선택",
            options=[r["노이즈/아티팩트"] for r in ba_items],
            key="ba_viewer",
        )
        if selected_ba:
            _render_before_after_viewer(selected_ba)
            with st.expander("전체 문서 보기"):
                doc_path = ALL_NOISE_DOCS.get(selected_ba)
                if doc_path:
                    render_markdown(doc_path, show_title=True)


def _render_interactive_troubleshooter():
    """Explorer에 내장된 인터랙티브 트러블슈터."""
    st.subheader("증상 기반 트러블슈터")
    st.markdown("관찰하는 증상을 선택하고 안내에 따라 진단하세요.")

    # 단계 1: 증상 카테고리 선택
    symptom_names = list(TROUBLESHOOTER_TREE.keys())
    selected_symptom = st.selectbox(
        "단계 1: 어떤 증상이 보입니까?",
        options=symptom_names,
        key="troubleshoot_symptom",
    )

    symptom = TROUBLESHOOTER_TREE[selected_symptom]
    st.info(f"**{selected_symptom}:** {symptom['description']}")

    # 단계 2: 분기 따라가기
    st.markdown("---")
    st.markdown("**단계 2: 진단 범위 좁히기**")

    for branch in symptom["branches"]:
        question = branch["question"]
        st.markdown(f"*{question}*")

        if "yes" in branch and "no" in branch:
            answer = st.radio(
                question,
                options=["예", "아니오"],
                key=f"branch_{selected_symptom}_{question}",
                horizontal=True,
                label_visibility="collapsed",
            )
            options = branch["yes"] if answer == "예" else branch["no"]
        elif "options" in branch:
            options = branch["options"]
        else:
            options = []

        if options:
            option_labels = [o.get("label") or o.get("condition", "") for o in options]
            selected_option = st.radio(
                "가장 일치하는 것을 선택하세요:",
                options=option_labels,
                key=f"option_{selected_symptom}_{question}",
            )

            matched = next(o for o in options
                           if (o.get("label") or o.get("condition")) == selected_option)

            diagnosis = matched.get("diagnosis")
            severity = matched.get("severity")
            note = matched.get("note")

            st.markdown("---")
            st.markdown("**단계 3: 진단**")

            if diagnosis:
                sev_color = SEVERITY_COLORS.get(severity, "gray")
                st.markdown(
                    f"### 진단: {diagnosis}\n"
                    f"**심각도:** :{sev_color}[{severity}]"
                )

                if diagnosis in BEFORE_AFTER_IMAGES:
                    with st.expander("보정 전후 비교 보기", expanded=True):
                        _render_before_after_viewer(diagnosis)

                doc_path = ALL_NOISE_DOCS.get(diagnosis)
                if doc_path:
                    with st.expander("전체 가이드 보기", expanded=False):
                        render_markdown(doc_path, show_title=True)
                else:
                    st.warning(f"'{diagnosis}'에 대한 상세 가이드를 찾을 수 없습니다.")
            else:
                if note:
                    st.info(note)
                else:
                    st.info("특정 진단을 결정할 수 없습니다. 다른 증상 카테고리를 시도하세요.")

    # 빠른 진단 코드
    st.markdown("---")
    with st.expander("빠른 진단 코드 스니펫"):
        st.markdown(symptom["quick_check"])


# ── 딥링크 via 쿼리 파라미터 ──────────────────────
_DOC_BY_BASENAME: dict[str, tuple[str, str, str]] = {}
for _mod_name, _mod_data in MODALITIES.items():
    for _name, _path in _mod_data["files"]:
        _DOC_BY_BASENAME[os.path.splitext(os.path.basename(_path))[0]] = (_name, _path, _mod_name)

_doc_param = st.query_params.get("doc", None)
_deep_link_target = None
if _doc_param:
    key = os.path.splitext(os.path.basename(_doc_param))[0]
    if key in _DOC_BY_BASENAME:
        _deep_link_target = _DOC_BY_BASENAME[key]
        level = "L2"

# ══════════════════════════════════════════════
# 메인 페이지 렌더링
# ══════════════════════════════════════════════

if level == "L0":
    # 모달리티별 개요 카드
    cols = st.columns(3)
    for i, (mod_name, mod_data) in enumerate(MODALITIES.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {mod_data['icon']} {mod_name}")
                st.metric("노이즈 유형", len(mod_data["files"]))
                for name, _ in mod_data["files"]:
                    ba_tag = " **[전/후]**" if name in BEFORE_AFTER_IMAGES else ""
                    st.markdown(f"- {name}{ba_tag}")

    st.markdown("---")
    st.subheader("빠른 접근")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 요약 표")
            st.markdown("보정 전후 비교가 포함된 29종 노이즈/아티팩트 유형의 전체 매트릭스.")
    with c2:
        with st.container(border=True):
            st.markdown("### 트러블슈터")
            st.markdown("인터랙티브 증상 기반 진단 — 보이는 것으로부터 문제를 찾으세요.")

elif level == "L1":
    render_markdown("09_noise_catalog/README.md", show_title=False)

    st.markdown("---")
    _render_summary_table_interactive()

elif level == "L2":
    # 딥링크 문서가 있으면 바로 표시
    if _deep_link_target:
        dl_name, dl_path, dl_mod = _deep_link_target
        st.info(f"표시 중: **{dl_name}** ({dl_mod})")
        if dl_name in BEFORE_AFTER_IMAGES:
            with st.expander("보정 전후 비교", expanded=True):
                _render_before_after_viewer(dl_name)
        render_markdown(dl_path, show_title=True)
        st.markdown("---")
        st.caption("아래에서 모든 문서를 탐색하세요:")

    tab_names = ["모달리티별", "요약 표", "트러블슈터"]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        _mod_keys = list(MODALITIES.keys())
        _mod_default = 0
        if _deep_link_target:
            _mod_default = _mod_keys.index(_deep_link_target[2]) if _deep_link_target[2] in _mod_keys else 0
        selected_mod = st.selectbox(
            "모달리티 선택",
            options=_mod_keys,
            index=_mod_default,
            format_func=lambda x: f"{MODALITIES[x]['icon']} {x}",
        )
        mod_data = MODALITIES[selected_mod]

        _noise_names = [name for name, _ in mod_data["files"]]
        _noise_default = 0
        if _deep_link_target and _deep_link_target[2] == selected_mod:
            _noise_default = _noise_names.index(_deep_link_target[0]) if _deep_link_target[0] in _noise_names else 0
        selected_noise = st.selectbox(
            "노이즈/아티팩트 선택",
            options=_noise_names,
            index=_noise_default,
        )
        noise_path = next(p for n, p in mod_data["files"] if n == selected_noise)

        if selected_noise in BEFORE_AFTER_IMAGES:
            with st.expander("보정 전후 비교", expanded=True):
                _render_before_after_viewer(selected_noise)

        render_markdown(noise_path, show_title=True)

    with tabs[1]:
        _render_summary_table_interactive()

    with tabs[2]:
        _render_interactive_troubleshooter()

elif level == "L3":
    # 소스 뷰 — 모든 노이즈 카탈로그 파일
    all_files = ["09_noise_catalog/README.md", "09_noise_catalog/summary_table.md",
                 "09_noise_catalog/troubleshooter.md"]
    for mod_data in MODALITIES.values():
        all_files.extend(p for _, p in mod_data["files"])

    selected = st.selectbox("파일 선택", options=all_files)
    content = read_local_file(selected)
    if content:
        st.code(content, language="markdown")
