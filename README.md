# 싱크로트론 데이터 분석 노트

아르곤 국립연구소(Argonne National Laboratory) 첨단광자원(Advanced Photon Source, APS)에서의
싱크로트론 X선 데이터 분석 및 AI/ML 방법론에 대한 개인 학습 노트.

## 소개

업그레이드된 APS(2024년 이후 500배 밝아진 X선)를 활용한 DOE BER 프로그램의 생물학 및 환경과학 분야
통합 X선 역량에 관한 노트.

## 저장소 구조

| 디렉토리 | 내용 |
|-----------|------|
| `01_program_overview/` | 프로그램 연혁, APS 시설, 빔라인, 파트너 기관 |
| `02_xray_modalities/` | X선 기법: 원리, 데이터 형식, AI/ML 응용 |
| `03_ai_ml_methods/` | AI/ML 방법 분류체계: 분할, 노이즈 제거, 재구성, 자율 실험 |
| `04_publications/` | 논문 아카이브: 상세 리뷰 및 주요 발견 |
| `05_tools_and_code/` | 오픈소스 도구 분석: ROI-Finder, TomocuPy, TomoPy, Bluesky |
| `06_data_structures/` | HDF5 스키마, EDA 노트북, 샘플 데이터 링크 |
| `07_data_pipeline/` | 엔드투엔드 파이프라인: 수집 → 스트리밍 → 처리 → 분석 |
| `08_references/` | 참고문헌, 용어집, 유용한 링크 |
| `eberlight-explorer/` | Streamlit 기반 인터랙티브 연구 탐색기 웹 앱 |

## 빠른 시작

- 싱크로트론 과학이 처음이신가요? `01_program_overview/`부터 시작하세요
- AI/ML 방법에 관심이 있으신가요? `03_ai_ml_methods/`를 참고하세요
- 실습 코드를 원하시나요? `05_tools_and_code/`와 `06_data_structures/notebooks/`를 확인하세요
- 논문 리뷰를 찾으시나요? `04_publications/ai_ml_synchrotron/`을 둘러보세요

## 관련 자료

- [APS BER 프로그램](https://eberlight.aps.anl.gov)
- [APS GitHub 조직](https://github.com/AdvancedPhotonSource)
- [ROI-Finder](https://github.com/arshadzahangirchowdhury/ROI-Finder)
