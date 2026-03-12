# 데이터 구조 및 탐색적 분석

## 개요

방사광 광원은 매우 빠른 속도로 다차원, 다중 모달 데이터셋을 생성합니다.
APS-U 업그레이드는 이 과제를 더욱 심화시킵니다: 500배 밝아진 빔은 더 미세한 공간 분해능과
더 빠른 데이터 수집을 가능하게 하여, 실험당 데이터 볼륨을 기가바이트에서 테라바이트로 증가시킵니다.
효과적인 연구는 잘 정의된 데이터 구조, 표준화된 형식, 그리고 머신러닝이나 고급 처리를 시도하기 전
체계적인 탐색적 데이터 분석(EDA)에 달려 있습니다.

이 디렉토리는 방사광 데이터 형식, 각 모달리티별 스키마, APS-U 이후 운영을 위한 규모 예측,
그리고 실습 EDA 노트북에 대한 종합 가이드를 제공합니다.

## 데이터 구조가 중요한 이유

1. **재현성** -- 표준화된 스키마는 실험을 재현하고 시설 간(APS, NSLS-II, ESRF, Diamond)
   데이터를 공유할 수 있도록 보장합니다.
2. **상호 운용성** -- HDF5/NeXus와 같은 공통 형식은 도구(TomoPy, MAPS,
   Bluesky)들이 별도의 파서 없이 서로의 출력을 읽을 수 있게 합니다.
3. **확장성** -- 계층적이고 청크 기반의 저장은 가용 RAM을 초과하는
   데이터셋의 스트리밍 분석을 가능하게 합니다.
4. **출처 추적** -- 측정 배열과 함께 내장된 메타데이터는 완전한
   실험 맥락을 보존합니다.

## 방사광 데이터 특성

| 속성 | 일반적인 범위 | APS-U 이후 범위 |
|------|--------------|------------------|
| 차원수 | 2D--4D | 3D--5D (+ 시간, 에너지) |
| 단일 스캔 크기 | 0.5--10 GB | 5--200 GB |
| 수집 속도 | 10--500 MB/s | 1--20 GB/s |
| 검출기 픽셀 | 1--4 Mpx | 4--16 Mpx |
| 동적 범위 | 16-bit | 16--32-bit |
| 메타데이터 필드 | 50--200 | 200--500 |

## 핵심 데이터 형식: HDF5

Hierarchical Data Format version 5 (HDF5)는 전 세계 방사광 데이터 저장의 사실상
표준입니다. 주요 장점:

- **자기 기술적**: 메타데이터와 데이터가 단일 파일에 함께 위치
- **계층적**: POSIX 유사 그룹/데이터셋 트리 구조
- **압축 지원**: 내장 LZ4, gzip, Blosc 코덱으로 파일 크기 2--10배 감소
- **병렬 I/O**: HPC 시스템에서 MPI 기반 동시 읽기/쓰기 지원
- **언어 독립적**: Python (h5py), C/C++, Fortran, MATLAB, Julia 바인딩

HDF5 위에 구축된 방사광 전용 규약에는 **NeXus** (일반), **Data Exchange**
(단층촬영), **CXI** (코히어런트 이미징)가 있습니다.

## 방사광 데이터를 위한 탐색적 데이터 분석 (EDA)

AI/ML 모델을 적용하기 전에 체계적인 EDA가 필수적입니다:

- **품질 평가** -- 불량 픽셀, 포화된 채널, 링 아티팩트 식별
- **분포 분석** -- 강도 히스토그램, 이상치 분포 파악
- **상관관계 발견** -- 공동 국소화된 원소(XRF) 또는 구조적 특징 발견
- **잡음 특성화** -- SNR 측정, 체계적 잡음과 무작위 잡음 구분
- **차원 개요** -- 배열 형태 확인, 누락 프레임 점검

EDA는 데이터 품질 문제를 조기에 발견하고 하위 분석에 직접 영향을 미치는
전처리 결정(정규화, 배경 제거, 필터링)에 정보를 제공합니다.

## 디렉토리 내용

| 경로 | 설명 |
|------|------|
| [hdf5_structure/](hdf5_structure/) | HDF5 형식 개요, 모달리티별 스키마 |
| [hdf5_structure/xrf_hdf5_schema.md](hdf5_structure/xrf_hdf5_schema.md) | XRF / MAPS HDF5 스키마 |
| [hdf5_structure/tomo_hdf5_schema.md](hdf5_structure/tomo_hdf5_schema.md) | 단층촬영 Data Exchange 스키마 |
| [hdf5_structure/ptychography_hdf5_schema.md](hdf5_structure/ptychography_hdf5_schema.md) | 타이코그래피 CXI 스키마 |
| [hdf5_structure/notebooks/](hdf5_structure/notebooks/) | HDF5 탐색 및 시각화 노트북 |
| [data_scale_analysis.md](data_scale_analysis.md) | APS-U 전후 데이터 볼륨 예측 |
| [hdf5_deep_dive.md](hdf5_deep_dive.md) | HDF5 내부 구조: SWMR, 병렬 I/O, 청킹, 한계점 |
| [data_formats_comparison.md](data_formats_comparison.md) | HDF5 vs Zarr vs TIFF; areaDetector, Databroker, Tiled |
| [data_challenges_apsu.md](data_challenges_apsu.md) | APS-U 100+ TB/일: 인프라, 과제, 해결방안 |
| [eda/](eda/) | 탐색적 데이터 분석 가이드 및 노트북 |
| [eda/xrf_eda.md](eda/xrf_eda.md) | XRF 전용 EDA 기법 |
| [eda/tomo_eda.md](eda/tomo_eda.md) | 단층촬영 전용 EDA 기법 |
| [eda/spectroscopy_eda.md](eda/spectroscopy_eda.md) | 분광학 전용 EDA 기법 |
| [eda/notebooks/](eda/notebooks/) | 실습 EDA Jupyter 노트북 |
| [sample_data/](sample_data/) | 공개적으로 사용 가능한 샘플 데이터셋 링크 |

## 권장 읽기 순서

1. [hdf5_structure/README.md](hdf5_structure/README.md)에서 형식 기본 사항부터 시작
2. [hdf5_deep_dive.md](hdf5_deep_dive.md)에서 SWMR, 병렬 I/O, 성능 튜닝 심화 학습
3. [data_formats_comparison.md](data_formats_comparison.md)에서 형식 비교 (HDF5 vs Zarr vs TIFF)
4. 관심 있는 모달리티의 스키마 파일 탐색
5. HDF5 탐색 노트북을 실행하여 실습 경험 습득
6. [data_scale_analysis.md](data_scale_analysis.md)에서 데이터 볼륨에 대한 맥락 파악
7. [data_challenges_apsu.md](data_challenges_apsu.md)에서 APS-U 데이터 과제 이해
8. 데이터 처리 전에 해당 모달리티의 EDA 가이드 따르기

## 관련 디렉토리

- [02_xray_modalities/](../02_xray_modalities/) -- 기법 물리학 및 원리
- [05_tools_and_code/](../05_tools_and_code/) -- 방사광 데이터 처리 소프트웨어
- [07_data_pipeline/](../07_data_pipeline/) -- 수집에서 분석까지의 엔드투엔드 파이프라인
