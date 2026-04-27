# 싱크로트론 데이터 분석 노트

아르곤 국립연구소(Argonne National Laboratory) 첨단광자원(Advanced Photon Source, APS)에서의
싱크로트론 X선 데이터 분석 및 AI/ML 방법론에 대한 개인 학습 노트.

## 소개

이 저장소는 2024년 APS-U 완공 이후 **500배 밝아진 X선**을 제공하는 업그레이드된 APS 시설에서의
DOE BER(생물·환경 연구) 프로그램 통합 X선 역량을 문서화합니다. 다음 내용을 다룹니다:

- **6가지 X선 모달리티** — 토모그래피, XRF 현미경, 타이코그래피, 분광학, 결정학, 산란
- **18가지 AI/ML 방법** — 5개 카테고리(분할, 노이즈 제거, 재구성, 자율 실험, 다중모달 통합)
- **19편의 논문 리뷰** — 싱크로트론 AI/ML 분야 주요 출판물의 상세 분석
- **10개 오픈소스 도구** — ROI-Finder, TomocuPy, TomoPy, MAPS, MLExchange, Bluesky/EPICS, HTTomo, PyXRF, Tike의 리버스 엔지니어링된 아키텍처
- **HDF5 데이터 스키마** — EDA 노트북 및 샘플 데이터 링크 포함
- **엔드투엔드 데이터 파이프라인** — 수집부터 저장까지 아키텍처 다이어그램 포함
- **47종 노이즈/아티팩트 유형** — 5개 도메인(토모그래피, XRF, 분광학, 타이코그래피/산란/회절, 의료영상, 전자현미경, 교차 분야)에 걸쳐 탐지 코드 및 보정 전후 예시 포함

## 문서

![notes-v0.1.0](https://img.shields.io/badge/notes-v0.1.0-blue)
![explorer-v0.3.0](https://img.shields.io/badge/explorer-v0.3.0-green)

전체 프로젝트 문서는 [`docs/README.md`](docs/README.md)에서 확인할 수 있으며 다음을 포함합니다:

- **제품 레이어**: Vision, 페르소나, 로드맵, PRD, 사용자 스토리, 비기능 요구사항
- **디자인 레이어**: 정보 아키텍처, 디자인 시스템, 와이어프레임
- **아키텍처 결정**: 프레임워크, IA, 스키마, 토큰, 버저닝을 다루는 7개 ADR
- **구현**: 셋업 가이드, 코딩 표준, 데이터 계약(data contracts)
- **테스트**: 테스트 계획, 접근성 감사 체크리스트

### 정적 사이트 (GitHub Pages)

GitHub Pages에서 Streamlit Explorer의 읽기 전용 **정적 미러**가 호스팅됩니다.
[`.github/workflows/pages.yml`](.github/workflows/pages.yml)이 `main` 브랜치 푸시마다
[`scripts/build_static_site.py`](scripts/build_static_site.py)를 실행해 자동 재생성합니다.
미러는 `explorer/lib/ia.py`, `explorer/lib/notes.py`, `explorer/assets/styles.css`를 그대로
재사용해 두 표면(surface)이 어긋나지 않도록 합니다. 동기화 계약은
[`docs/03_implementation/github_pages_sync.md`](docs/03_implementation/github_pages_sync.md),
근거(rationale)는 [ADR-007](docs/02_design/decisions/ADR-007.md)을 참조하세요.

게시되는 사이트 구성:
- 3개 클러스터 카드를 가진 랜딩 페이지 (`explorer/app.py` 미러링)
- Discover / Explore / Build 클러스터 페이지 (`explorer/pages/` 미러링)
- 노트별 상세 페이지(176개 노트), 마크다운/코드 하이라이트/메타데이터 패널 포함
- `/wireframes/`에 디자인 와이어프레임 (이전 Pages 설정에서 보존)

### 와이어프레임 미리보기

미러 사이트의 `/wireframes/`에도 게시되는 정적 HTML 와이어프레임:
- [랜딩 페이지](docs/02_design/wireframes/html/landing_v0.1.html)
- [섹션 페이지](docs/02_design/wireframes/html/section_v0.1.html)
- [도구 상세 페이지](docs/02_design/wireframes/html/tool_v0.1.html)

## Explorer (재설계됨)

`explorer/` 디렉토리의 **eBERlight Explorer**는 ANL 디자인 시스템에 정렬된 3-클러스터
정보 아키텍처와 런타임 노트 렌더링을 제공하는 재설계된 Streamlit 포털입니다.

### Explorer 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/Denny-Hwang/synchrotron-data-analysis-notes_ko.git
cd synchrotron-data-analysis-notes_ko

# 2. 의존성 설치
pip install -r explorer/requirements.txt

# 3. 앱 실행
streamlit run explorer/app.py
```

브라우저에서 `http://localhost:8501`로 열립니다.

### 클러스터 구조 (3-클러스터 IA)

새 Explorer는 9개 노트 폴더를 3개의 사용자 의도 기반 클러스터로 매핑합니다(ADR-004):

| 클러스터 | 포함 폴더 | 목적 |
|----------|-----------|------|
| **Discover** | `01_program_overview/`, `02_xray_modalities/` | BER 프로그램·시설·X선 기법 학습 |
| **Explore** | `03_ai_ml_methods/`, `04_publications/`, `09_noise_catalog/` | AI/ML 방법, 논문 리뷰, 노이즈 카탈로그 탐색 |
| **Build** | `05_tools_and_code/`, `06_data_structures/`, `07_data_pipeline/`, `08_references/` | 도구·HDF5 스키마·파이프라인·참고자료 활용 |

### 레거시 Explorer

기존 다중 페이지 Streamlit 앱은 [`eberlight-explorer/`](eberlight-explorer/)에 그대로 보존되어
지식 그래프, 모달리티/방법/논문/도구별 상세 뷰, 데이터 파이프라인 시각화를 제공합니다.

```bash
streamlit run eberlight-explorer/app.py
```

## 저장소 구조

```
synchrotron-data-analysis-notes_ko/
├── 01_program_overview/     # BER 프로그램 미션, APS 시설, 15개 빔라인, 파트너 기관
├── 02_xray_modalities/      # 6가지 X선 기법: 원리, 데이터 형식, AI/ML 응용
├── 03_ai_ml_methods/        # AI/ML 분류체계: 분할, 노이즈 제거, 재구성, 자율 실험, PINN, 확산 모델
├── 04_publications/         # 19편 논문 리뷰: 상세 분석 및 주요 발견
├── 05_tools_and_code/       # 도구 분석: ROI-Finder, TomocuPy, TomoPy, Bluesky, HTTomo, PyXRF, Tike 등
├── 06_data_structures/      # HDF5 스키마, EDA 노트북, 샘플 데이터 링크
├── 07_data_pipeline/        # 엔드투엔드 파이프라인: 수집 → 스트리밍 → 처리 → 저장
├── 08_references/           # 참고문헌(BibTeX), 용어집(A-Z), 유용한 링크
├── 09_noise_catalog/        # 47종 노이즈/아티팩트 카탈로그(7개 도메인): 탐지·예시·트러블슈터
├── docs/                    # 제품·디자인·구현·테스트·릴리스 문서 + 7개 ADR
├── explorer/                # 재설계된 3-클러스터 Streamlit Explorer
├── eberlight-explorer/      # 레거시 다중 페이지 Streamlit Explorer
├── scripts/                 # 정적 사이트 생성기(build_static_site.py)
├── .github/workflows/       # GitHub Pages 자동 배포 워크플로우
└── CLAUDE.md                # Claude Code 협업 규약 및 불변조건
```

## 빠른 시작

### 싱크로트론 과학이 처음이신가요?

1. [`01_program_overview/`](01_program_overview/)에서 BER 프로그램과 APS 시설 이해하기
2. [`02_xray_modalities/`](02_xray_modalities/)에서 X선 측정 기법 배우기
3. [`08_references/glossary.md`](08_references/glossary.md)에서 용어 확인하기

### AI/ML을 적용하고 싶으신가요?

1. [`03_ai_ml_methods/`](03_ai_ml_methods/)에서 방법 분류체계 탐색하기
2. [`04_publications/`](04_publications/)에서 상세 논문 리뷰 읽기
3. [`05_tools_and_code/`](05_tools_and_code/)에서 도구 구현 살펴보기

### 실습 코드가 필요하신가요?

1. [`05_tools_and_code/roi_finder/notebooks/`](05_tools_and_code/roi_finder/notebooks/)에서 Jupyter 노트북 실행하기
2. [`06_data_structures/hdf5_structure/notebooks/`](06_data_structures/hdf5_structure/notebooks/)에서 HDF5 데이터 탐색하기
3. [`06_data_structures/eda/notebooks/`](06_data_structures/eda/notebooks/)에서 EDA 노트북 시도하기

### 노이즈가 많은 데이터를 다루고 계신가요?

1. **모달리티를 알고 있다면?** [`09_noise_catalog/`](09_noise_catalog/)에서 기법별 탐색
2. **뭔가 이상한데 원인을 모르겠다면?** [증상 기반 트러블슈터](09_noise_catalog/troubleshooter.md) 사용
3. **빠른 참조**: [요약 표](09_noise_catalog/summary_table.md)에서 47종 유형 한눈에 보기

### 그냥 둘러보고 싶으신가요?

시각적이고 인터랙티브한 경험을 위해 [eBERlight Explorer](#explorer-재설계됨)를 실행하세요.

## 주요 자료

| 자료 | 링크 |
|------|------|
| APS BER 프로그램 | [eberlight.aps.anl.gov](https://eberlight.aps.anl.gov) |
| APS 시설 | [aps.anl.gov](https://www.aps.anl.gov) |
| APS GitHub 조직 | [github.com/AdvancedPhotonSource](https://github.com/AdvancedPhotonSource) |
| ROI-Finder | [github.com/arshadzahangirchowdhury/ROI-Finder](https://github.com/arshadzahangirchowdhury/ROI-Finder) |
| TomoPy | [tomopy.readthedocs.io](https://tomopy.readthedocs.io) |
| TomocuPy | [github.com/nikitinvv/tomocupy](https://github.com/nikitinvv/tomocupy) |
| Bluesky 프로젝트 | [blueskyproject.io](https://blueskyproject.io) |
| MLExchange | [mlexchange.als.lbl.gov](https://mlexchange.als.lbl.gov) |
| HTTomo | [diamondlightsource.github.io/httomo](https://diamondlightsource.github.io/httomo/) |
| PyXRF | [github.com/NSLS-II/PyXRF](https://github.com/NSLS-II/PyXRF) |
| Tike | [github.com/AdvancedPhotonSource/tike](https://github.com/AdvancedPhotonSource/tike) |

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다 — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---
