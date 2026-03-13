# 싱크로트론 데이터 분석 노트

아르곤 국립연구소(Argonne National Laboratory) 첨단광자원(Advanced Photon Source, APS)에서의
싱크로트론 X선 데이터 분석 및 AI/ML 방법론에 대한 개인 학습 노트.

## 소개

이 저장소는 2024년 APS-U 완공 이후 **500배 밝아진 X선**을 제공하는 업그레이드된 APS 시설에서의
DOE BER(생물·환경 연구) 프로그램 통합 X선 역량을 문서화합니다. 다음 내용을 다룹니다:

- **6가지 X선 모달리티** — 토모그래피, XRF 현미경, 타이코그래피, 분광학, 결정학, 산란
- **14가지 AI/ML 방법** — 5개 카테고리(분할, 노이즈 제거, 재구성, 자율 실험, 다중모달 통합)로 구성
- **14편의 논문 리뷰** — 싱크로트론 AI/ML 분야 주요 출판물의 상세 분석
- **7개 오픈소스 도구** — ROI-Finder, TomocuPy, TomoPy, MAPS, MLExchange, Bluesky/EPICS의 리버스 엔지니어링된 아키텍처
- **HDF5 데이터 스키마** — EDA 노트북 및 샘플 데이터 링크 포함
- **엔드투엔드 데이터 파이프라인** — 수집부터 저장까지 아키텍처 다이어그램 포함

## eBERlight Explorer (인터랙티브 웹 앱)

이 저장소에는 모든 콘텐츠를 시각적으로 탐색할 수 있는 인터랙티브 Streamlit 웹 애플리케이션
**eBERlight Research Explorer**가 포함되어 있습니다.

### Explorer 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/Denny-Hwang/synchrotron-data-analysis-notes_ko.git
cd synchrotron-data-analysis-notes_ko

# 2. 의존성 설치
pip install -r eberlight-explorer/requirements.txt

# 3. 앱 실행
streamlit run eberlight-explorer/app.py
```

앱이 브라우저에서 `http://localhost:8501`로 열립니다.

### Explorer 페이지

| 페이지 | 설명 |
|--------|------|
| **홈** | 통계 및 빠른 탐색 가이드가 포함된 개요 대시보드 |
| **지식 그래프** | 모달리티, 방법, 도구, 논문 간 관계의 인터랙티브 네트워크 시각화 |
| **모달리티** | 사양, 빔라인, 관련 AI 방법을 포함한 6가지 X선 기법 탐색 |
| **AI/ML 방법** | 카테고리별로 정리된 14가지 방법의 상세 문서 탐색 |
| **출판물** | TL;DR 요약 및 워크플로우 다이어그램이 포함된 14편의 논문 리뷰 아카이브 |
| **도구** | 아키텍처 분석 및 장단점이 포함된 7개 오픈소스 도구 카탈로그 |
| **파이프라인** | 엔드투엔드 데이터 파이프라인(수집 → 저장) 시각적 안내 |
| **데이터 구조** | HDF5 스키마, EDA 가이드, APS-U 전후 데이터 규모 분석 |

### 난이도 레벨

Explorer는 각 페이지에서 세 단계의 상세도를 제공합니다:

- **L0 (개요)** — 빠른 파악을 위한 상위 수준 요약
- **L1 (중급)** — 테이블 및 비교가 포함된 상세 콘텐츠
- **L2 (심층 분석)** — 전체 기술 세부사항, 코드 예제, 아키텍처 다이어그램

## 저장소 구조

```
synchrotron-data-analysis-notes_ko/
├── 01_program_overview/     # BER 프로그램 미션, APS 시설, 15개 빔라인, 파트너 기관
├── 02_xray_modalities/      # 6가지 X선 기법: 원리, 데이터 형식, AI/ML 응용
├── 03_ai_ml_methods/        # AI/ML 분류체계: 분할, 노이즈 제거, 재구성, 자율 실험
├── 04_publications/         # 14편 논문 리뷰: 상세 분석 및 주요 발견
├── 05_tools_and_code/       # 도구 분석: ROI-Finder, TomocuPy, TomoPy, Bluesky 등
├── 06_data_structures/      # HDF5 스키마, EDA 노트북, 샘플 데이터 링크
├── 07_data_pipeline/        # 엔드투엔드 파이프라인: 수집 → 스트리밍 → 처리 → 저장
├── 08_references/           # 참고문헌(BibTeX), 용어집(A-Z), 유용한 링크
└── eberlight-explorer/      # Streamlit 기반 인터랙티브 탐색 웹 앱
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

### 그냥 둘러보고 싶으신가요?

시각적이고 인터랙티브한 경험을 위해 [eBERlight Explorer](#eberlight-explorer-인터랙티브-웹-앱)를 실행하세요.

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

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다 — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---
