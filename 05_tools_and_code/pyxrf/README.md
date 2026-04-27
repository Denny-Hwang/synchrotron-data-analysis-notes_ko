# PyXRF

## 개요

PyXRF는 NSLS-II, Brookhaven National Laboratory에서 개발한 Python 기반 X-선 형광 (XRF) 분석 패키지입니다. 스펙트럼 피팅 및 원소 매핑을 위한 대화형 GUI와 함께, 싱크로트론 빔라인에서 수집된 대규모 XRF 데이터셋을 위한 배치 처리 기능을 제공합니다.

## 주요 기능

- **대화형 GUI** -- XRF 스펙트럼 시각화, 피크 피팅, 원소 맵 생성을 위한 그래픽 인터페이스.
- **자동 스펙트럼 피팅** -- 다중 형광선, 이스케이프 피크, Compton/Rayleigh 산란을 지원하는 XRF 스펙트럼의 비선형 최소제곱 피팅.
- **원소 매핑** -- 스캐닝 XRF 데이터셋에서 정량적 원소 분포 맵을 생성합니다.
- **배치 처리** -- 구성 가능한 피팅 매개변수로 대규모 XRF 데이터셋의 자동 처리를 지원합니다.
- **표준 기반 정량화** -- 정량적 원소 농도 매핑을 위한 참조 표준에 대한 보정.
- **HDF5 I/O** -- Bluesky/Databroker 생태계와 호환되는 표준 싱크로트론 데이터 형식을 읽고 씁니다.

## 지원 알고리즘

| 알고리즘 | 설명 |
|-----------|-------------|
| NNLS fitting | 비음수 최소제곱 스펙트럼 분해 |
| ROI integration | 관심 영역 기반 원소 매핑 |
| Per-pixel fitting | 각 스캔 위치에서의 전체 스펙트럼 피팅 |
| Background subtraction | 자동 배경 추정 및 제거 |
| Escape peak correction | 검출기 이스케이프 피크 모델링 |

## 일반적인 성능

대규모 XRF 맵 (1000x1000 픽셀, 4096 채널)의 배치 처리는 표준 워크스테이션에서 수 분 내에 완료됩니다. 픽셀별 피팅은 처리량을 위해 CPU 코어 전반에 걸쳐 병렬화됩니다.

## 저장소

- GitHub: <https://github.com/NSLS2/PyXRF>
- 라이선스: BSD-3-Clause
- 언어: Python
- 주요 유지 관리자: NSLS-II, Brookhaven National Laboratory

## 참고 문헌

Li, L. et al. (2017). PyXRF: Python-based X-ray fluorescence analysis package.
*Proc. SPIE 10389, X-Ray Nanoimaging: Instruments and Methods III*, 103890U.
DOI: [10.1117/12.2272585](https://doi.org/10.1117/12.2272585)

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| XRF 분석 노트 | 싱크로트론 기법 문서 참조 |
