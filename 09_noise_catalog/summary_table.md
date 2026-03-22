# 노이즈 및 아티팩트 요약 테이블

29종 노이즈/아티팩트 유형의 탐지 방법, 해결책, 관련 자료를 포함한 전체 매트릭스입니다.

## 전체 요약 매트릭스

| 노이즈/아티팩트 | 모달리티 | 유형 | 심각도 | 탐지 방법 | 전통적 해결법 | AI/ML 해결법 | 전후 비교 이미지 | 관련 문서 |
|---|---|---|---|---|---|---|---|---|
| [링 아티팩트](tomography/ring_artifact.md) | 토모그래피 | 기기적 | 심각 | 사이노그램 열 통계, 방사형 프로파일 분석 | `tomopy.prep.stripe.remove_stripe_fw()`, Sarepy | DL 기반 스트라이프 제거 | 예 (실제 데이터 — Sarepy) | [tomo_eda](../06_data_structures/eda/tomo_eda.md), [TomoPy stripe.py](../05_tools_and_code/tomopy/reverse_engineering.md) |
| [징거](tomography/zinger.md) | 토모그래피 | 기기적 | 주요 | 투영 스택 이상값 탐지 | 메디안 필터, `tomopy.prep.stripe.remove_outlier()` | — | 예 (합성) | [tomo_eda](../06_data_structures/eda/tomo_eda.md) |
| [줄무늬 아티팩트](tomography/streak_artifact.md) | 토모그래피 | 체계적 | 심각 | 방사형 강도 프로파일, 금속 영역 분할 | MAR (사이노그램 인페인팅), 반복 재구성 | DL 인페인팅 | 아니오 (외부 참조) | [ai_ml_methods](../02_xray_modalities/tomography/ai_ml_methods.md) |
| [저선량 노이즈](tomography/low_dose_noise.md) | 토모그래피 | 통계적 | 주요 | SNR 측정, 노이즈 파워 스펙트럼 | BM3D, NLM 필터링 | TomoGAN, Noise2Noise | 예 (실제 데이터 — TomoGAN) | [tomogan](../03_ai_ml_methods/denoising/tomogan.md), [noise2noise](../03_ai_ml_methods/denoising/noise2noise.md) |
| [희소각 아티팩트](tomography/sparse_angle_artifact.md) | 토모그래피 | 계산적 | 주요 | 전체 vs 희소 재구성 비교, 줄무늬 패턴 분석 | TV 정규화, SIRT | DL 기반 뷰 합성 | 예 (합성) | [ai_ml_methods](../02_xray_modalities/tomography/ai_ml_methods.md) |
| [모션 아티팩트](tomography/motion_artifact.md) | 토모그래피 | 체계적 | 심각 | 인접 투영 교차 상관 | 재정렬, 사이노그램 복구 | INR 기반 보정 | 아니오 (외부 참조) | [inr_dynamic](../03_ai_ml_methods/reconstruction/inr_dynamic.md) |
| [플랫필드 문제](tomography/flatfield_issues.md) | 토모그래피 | 기기적 | 주요 | 플랫필드 균일성 확인, 투과 히스토그램 | 적절한 플랫/다크 보정, 동적 플랫필드 | — | 예 (합성) | [tomo_eda](../06_data_structures/eda/tomo_eda.md) |
| [회전 중심 오류](tomography/rotation_center_error.md) | 토모그래피 | 체계적 | 심각 | 0°/180° 중첩 테스트, 이미지 선명도 메트릭 | `tomopy.recon.rotation.find_center()` | — | 예 (합성) | [tomo_eda](../06_data_structures/eda/tomo_eda.md) |
| [빔 강도 저하](tomography/beam_intensity_drop.md) | 토모그래피 | 기기적 | 주요 | I0 모니터 시계열, 사이노그램 행 통계 | 투영별 I0 정규화 | — | 예 (합성) | [tomo_eda](../06_data_structures/eda/tomo_eda.md) |
| [광자 계수 노이즈](xrf_microscopy/photon_counting_noise.md) | XRF | 통계적 | 주요 | 픽셀별 총 카운트 통계, SNR 맵 | 더 긴 체류 시간, 반복 평균화 | DL 디노이징 | 아니오 (외부 참조) | [xrf_eda](../06_data_structures/eda/xrf_eda.md) |
| [데드/핫 픽셀](xrf_microscopy/dead_hot_pixel.md) | XRF | 기기적 | 주요 | Z-score 이상값 맵, 이웃 비교 | 메디안 필터 대체 | — | 예 (합성) | [xrf_eda](../06_data_structures/eda/xrf_eda.md) |
| [피크 중첩](xrf_microscopy/peak_overlap.md) | XRF | 체계적 | 주요 | 피팅 후 잔차 분석, 카이제곱 맵 | 다중 피크 디컨볼루션 (MAPS, PyXRF) | — | 아니오 (ASCII 다이어그램) | [analysis_pipeline](../02_xray_modalities/xrf_microscopy/analysis_pipeline.md) |
| [자기흡수](xrf_microscopy/self_absorption.md) | XRF | 체계적 | 주요 | 얇은 vs 두꺼운 시료 영역 비교, 엣지점프 비율 | 기본 파라미터 보정 | — | 아니오 (ASCII 다이어그램) | — |
| [데드타임 포화](xrf_microscopy/dead_time_saturation.md) | XRF | 기기적 | 심각 | ICR/OCR 비율 확인 | 데드타임 보정 공식 | — | 아니오 (ASCII 다이어그램) | [workflow_analysis](../05_tools_and_code/maps_software/workflow_analysis.md) |
| [I0 정규화](xrf_microscopy/i0_normalization.md) | XRF | 체계적 | 주요 | I0 시계열, 정규화 vs 원시 맵 비교 | 픽셀별 I0으로 나누기 | — | 예 (합성) | [xrf_eda](../06_data_structures/eda/xrf_eda.md) |
| [프로브 블러링](xrf_microscopy/probe_blurring.md) | XRF | 기기적 | 경미 | 엣지 선명도 분석, PSF 추정 | 디컨볼루션 (Richardson-Lucy) | 딥 잔차 초해상도 | 아니오 (외부 참조) | [deep_residual_xrf](../03_ai_ml_methods/denoising/deep_residual_xrf.md) |
| [스캔 줄무늬](xrf_microscopy/scan_stripe.md) | XRF | 체계적 | 주요 | 행 평균 비교, 푸리에 분석 | 행별 정규화, 디스트라이핑 | — | 아니오 (ASCII 다이어그램) | — |
| [통계적 노이즈(EXAFS)](spectroscopy/statistical_noise_exafs.md) | 분광학 | 통계적 | 주요 | 고 k에서 chi(k) 노이즈 수준, 푸리에 변환 피크 SNR | 다중 스캔 병합, k-가중 | DL 디노이징 | 아니오 (ASCII 다이어그램) | [spectroscopy_eda](../06_data_structures/eda/spectroscopy_eda.md) |
| [에너지 교정 드리프트](spectroscopy/energy_calibration_drift.md) | 분광학 | 체계적 | 심각 | 스캔 간 엣지 위치 추적 | 스캔별 E0 정렬, 기준 포일 | — | 아니오 (ASCII 다이어그램) | [spectroscopy_eda](../06_data_structures/eda/spectroscopy_eda.md) |
| [고조파 오염](spectroscopy/harmonics_contamination.md) | 분광학 | 기기적 | 주요 | XANES 진폭 감쇠, 글리치 탐지 | 단색화장치 디튜닝, 고조파 차단 미러 | — | 아니오 (ASCII 다이어그램) | — |
| [자기흡수(XAS)](spectroscopy/self_absorption_xas.md) | 분광학 | 체계적 | 주요 | 평탄화된 화이트라인, 투과 vs 형광 비교 | 희석, Booth & Bridges 보정 | — | 아니오 (ASCII 다이어그램) | [spectroscopy_eda](../06_data_structures/eda/spectroscopy_eda.md) |
| [방사선 손상](spectroscopy/radiation_damage.md) | 분광학 | 체계적 | 심각 | 연속 스캔에서 엣지 이동 또는 특성 변화 | 빠른 스캔, 감쇠기, 극저온 냉각 | — | 아니오 (ASCII 다이어그램) | — |
| [이상 스펙트럼](spectroscopy/outlier_spectra.md) | 분광학 | 통계적 | 경미 | PCA 성분 분석, 스펙트럼별 카이제곱 | 병합 전 이상 스캔 제거 | — | 아니오 (ASCII 다이어그램) | [spectroscopy_eda](../06_data_structures/eda/spectroscopy_eda.md) |
| [위치 오류](ptychography/position_error.md) | 타이코그래피 | 체계적 | 심각 | 재구성 잔차, 위치 산점도 | 결합 정제 (어닐링, 그래디언트) | DL 위치 보정 | 아니오 (외부 참조) | — |
| [부분 결맞음](ptychography/partial_coherence.md) | 타이코그래피 | 기기적 | 주요 | 재구성에서 대비 손실, 모드 분해 | 혼합 상태 타이코그래피 | — | 아니오 (외부 참조) | — |
| [스티칭 아티팩트](ptychography/stitching_artifact.md) | 타이코그래피 | 계산적 | 경미 | 타일 경계에서 강도 불연속 | 중첩 블렌딩, 라플라시안 피라미드 | — | 아니오 (ASCII 다이어그램) | — |
| [DL 환각](cross_cutting/dl_hallucination.md) | 공통 | 계산적 | 심각 | 잔차 분석, 불확실성 맵, 기준 대비 비교 | 앙상블 방법, 드롭아웃 불확실성 | 불확실성 인식 아키텍처 | 아니오 (ASCII 다이어그램) | [tomogan](../03_ai_ml_methods/denoising/tomogan.md) |
| [리청킹 데이터 무결성](cross_cutting/rechunking_data_integrity.md) | 공통 | 계산적 | 주요 | 전후 체크섬, 슬라이스 비교 | 체크섬을 포함한 검증 파이프라인 | — | 아니오 (ASCII 다이어그램) | — |
| [검출기 공통 문제](cross_cutting/detector_common_issues.md) | 공통 | 기기적 | 주요 | 플랫필드 분석, 픽셀 응답 맵 | 정기적 검출기 교정 | — | 아니오 (ASCII 다이어그램) | — |
