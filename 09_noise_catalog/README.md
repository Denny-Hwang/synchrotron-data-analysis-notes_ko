# 노이즈 및 아티팩트 카탈로그

싱크로트론 X선 데이터 분석에서 발생하는 **29종 노이즈 및 아티팩트 유형**의 실용적 카탈로그입니다. 각 항목에는 탐지 코드, 보정 방법, 보정 전후 예시, 그리고 이 저장소의 심화 자료 링크가 포함되어 있습니다.

## 카탈로그 사용법

이 카탈로그는 상황에 따라 **두 가지 접근 모드**를 제공합니다:

### 모드 1: 분류 기반 탐색

**"어떤 모달리티에서 작업하는지 알고 있습니다."**

아래 하위 디렉토리를 기법별로 탐색하세요. 각 파일은 탐지 코드, 보정 레시피, 시각적 예시와 함께 하나의 특정 노이즈 유형을 문서화합니다.

### 모드 2: 증상 기반 트러블슈팅

**"뭔가 이상한데 원인을 모르겠습니다."**

**[증상 기반 트러블슈터](troubleshooter.md)**를 사용하세요 — 문제가 *어떻게 보이는지*에서 시작하여 올바른 진단으로 안내하는 대화형 결정 트리입니다.

## 3축 분류 체계

```
싱크로트론 노이즈 & 아티팩트 카탈로그
│
├── 모달리티별 (디렉토리)
│   ├── 토모그래피 (9종)
│   ├── XRF 현미경 (8종)
│   ├── 분광학 (6종)
│   ├── 타이코그래피 (3종)
│   └── 공통 (3종)
│
├── 노이즈 유형별 (각 문서의 속성)
│   ├── 통계적 — 광자 계수, 포아송, 열잡음
│   ├── 체계적 — 자기흡수, 빔 드리프트, 보정
│   ├── 기기적 — 검출기 결함, 데드타임, 광학계
│   └── 계산적 — 재구성 아티팩트, DL 환각
│
└── 증상별 (troubleshooter.md)
    ├── "원형/링이 보입니다"
    ├── "밝은 점이 보입니다"
    ├── "줄무늬/줄이 보입니다"
    ├── "이미지가 거칠고/노이즈가 있습니다"
    ├── "특징이 흐릿하거나/이동했습니다"
    ├── "스펙트럼이 이상합니다"
    └── "데이터 값이 이상합니다"
```

## 빠른 참조 테이블

| # | 노이즈/아티팩트 | 모달리티 | 유형 | 심각도 | 빈도 | 한 줄 해결법 |
|---|---------------|----------|------|--------|------|-------------|
| 1 | [링 아티팩트](tomography/ring_artifact.md) | 토모 | 기기적 | 심각 | 흔함 | 사이노그램에서 푸리에 스트라이프 제거 |
| 2 | [징거](tomography/zinger.md) | 토모 | 기기적 | 주요 | 간헐적 | 투영에 메디안 필터 적용 |
| 3 | [줄무늬 아티팩트](tomography/streak_artifact.md) | 토모 | 체계적 | 심각 | 흔함 | 금속 아티팩트 저감(MAR) |
| 4 | [저선량 노이즈](tomography/low_dose_noise.md) | 토모 | 통계적 | 주요 | 흔함 | TomoGAN / BM3D 디노이징 |
| 5 | [희소각 아티팩트](tomography/sparse_angle_artifact.md) | 토모 | 계산적 | 주요 | 간헐적 | 반복 재구성(TV, SIRT) |
| 6 | [모션 아티팩트](tomography/motion_artifact.md) | 토모 | 체계적 | 심각 | 간헐적 | 모션 보상 재구성 |
| 7 | [플랫필드 문제](tomography/flatfield_issues.md) | 토모 | 기기적 | 주요 | 흔함 | 적절한 플랫/다크 취득 및 정규화 |
| 8 | [회전 중심 오류](tomography/rotation_center_error.md) | 토모 | 체계적 | 심각 | 흔함 | 자동 중심 탐색 알고리즘 |
| 9 | [빔 강도 저하](tomography/beam_intensity_drop.md) | 토모 | 기기적 | 주요 | 간헐적 | 투영별 I0 정규화 |
| 10 | [광자 계수 노이즈](xrf_microscopy/photon_counting_noise.md) | XRF | 통계적 | 주요 | 항상 | 더 긴 체류 시간 또는 반복 스캔 |
| 11 | [데드/핫 픽셀](xrf_microscopy/dead_hot_pixel.md) | XRF | 기기적 | 주요 | 흔함 | 메디안 필터 이상값 대체 |
| 12 | [피크 중첩](xrf_microscopy/peak_overlap.md) | XRF | 체계적 | 주요 | 흔함 | 디컨볼루션을 통한 스펙트럼 피팅 |
| 13 | [자기흡수](xrf_microscopy/self_absorption.md) | XRF | 체계적 | 주요 | 흔함 | 흡수 보정 모델 |
| 14 | [데드타임 포화](xrf_microscopy/dead_time_saturation.md) | XRF | 기기적 | 심각 | 흔함 | ICR/OCR을 통한 데드타임 보정 |
| 15 | [I0 정규화](xrf_microscopy/i0_normalization.md) | XRF | 체계적 | 주요 | 흔함 | I0으로 원소 맵 정규화 |
| 16 | [프로브 블러링](xrf_microscopy/probe_blurring.md) | XRF | 기기적 | 경미 | 항상 | 디컨볼루션 / 초해상도 DL |
| 17 | [스캔 줄무늬](xrf_microscopy/scan_stripe.md) | XRF | 체계적 | 주요 | 간헐적 | 행별 정규화 |
| 18 | [통계적 노이즈(EXAFS)](spectroscopy/statistical_noise_exafs.md) | 분광 | 통계적 | 주요 | 항상 | 다중 스캔 평균화 |
| 19 | [에너지 교정 드리프트](spectroscopy/energy_calibration_drift.md) | 분광 | 체계적 | 심각 | 간헐적 | 스캔별 엣지 위치 정렬 |
| 20 | [고조파 오염](spectroscopy/harmonics_contamination.md) | 분광 | 기기적 | 주요 | 간헐적 | 단색화장치 디튜닝 또는 고조파 차단 미러 |
| 21 | [자기흡수(XAS)](spectroscopy/self_absorption_xas.md) | 분광 | 체계적 | 주요 | 흔함 | 시료 희석 또는 보정 알고리즘 |
| 22 | [방사선 손상](spectroscopy/radiation_damage.md) | 분광 | 체계적 | 심각 | 간헐적 | 선량률 감소, 빠른 스캔, 극저온 냉각 |
| 23 | [이상 스펙트럼](spectroscopy/outlier_spectra.md) | 분광 | 통계적 | 경미 | 간헐적 | PCA 기반 이상값 탐지 및 제거 |
| 24 | [위치 오류](ptychography/position_error.md) | 타이코 | 체계적 | 심각 | 흔함 | 재구성에서 결합 위치 정제 |
| 25 | [부분 결맞음](ptychography/partial_coherence.md) | 타이코 | 기기적 | 주요 | 흔함 | 혼합 상태 재구성 |
| 26 | [스티칭 아티팩트](ptychography/stitching_artifact.md) | 타이코 | 계산적 | 경미 | 간헐적 | 중첩 가중 블렌딩 |
| 27 | [DL 환각](cross_cutting/dl_hallucination.md) | 공통 | 계산적 | 심각 | 간헐적 | 불확실성 정량화, 잔차 분석 |
| 28 | [리청킹 데이터 무결성](cross_cutting/rechunking_data_integrity.md) | 공통 | 계산적 | 주요 | 간헐적 | 리청킹 후 체크섬 검증 |
| 29 | [검출기 공통 문제](cross_cutting/detector_common_issues.md) | 공통 | 기기적 | 주요 | 흔함 | 정기적 검출기 교정 |

## 디렉토리 구성

```
09_noise_catalog/
├── README.md                          # 이 파일
├── troubleshooter.md                  # 증상 기반 결정 트리
├── summary_table.md                   # 전체 노이즈 × 탐지 × 해결 매트릭스
├── tomography/
│   ├── ring_artifact.md
│   ├── zinger.md
│   ├── streak_artifact.md
│   ├── low_dose_noise.md
│   ├── sparse_angle_artifact.md
│   ├── motion_artifact.md
│   ├── flatfield_issues.md
│   ├── rotation_center_error.md
│   └── beam_intensity_drop.md
├── xrf_microscopy/
│   ├── photon_counting_noise.md
│   ├── dead_hot_pixel.md
│   ├── peak_overlap.md
│   ├── self_absorption.md
│   ├── dead_time_saturation.md
│   ├── i0_normalization.md
│   ├── probe_blurring.md
│   └── scan_stripe.md
├── spectroscopy/
│   ├── statistical_noise_exafs.md
│   ├── energy_calibration_drift.md
│   ├── harmonics_contamination.md
│   ├── self_absorption_xas.md
│   ├── radiation_damage.md
│   └── outlier_spectra.md
├── ptychography/
│   ├── position_error.md
│   ├── partial_coherence.md
│   └── stitching_artifact.md
├── cross_cutting/
│   ├── dl_hallucination.md
│   ├── rechunking_data_integrity.md
│   └── detector_common_issues.md
└── images/
    ├── README.md                      # 이미지 출처 및 라이선스 정보
    └── generate_examples.py           # 합성 예시 생성 스크립트
```

## 관련 섹션

- [AI/ML 방법 — 디노이징](../03_ai_ml_methods/denoising/) — TomoGAN, Noise2Noise, 딥 잔차 XRF
- [EDA 노트북](../06_data_structures/eda/) — 노이즈 탐지 코드가 포함된 탐색적 데이터 분석
- [TomoPy 도구](../05_tools_and_code/tomopy/) — 스트라이프 제거 및 전처리 함수
- [X선 모달리티](../02_xray_modalities/) — 기법별 데이터 형식 및 과제

---
