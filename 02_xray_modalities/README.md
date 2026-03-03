# X선 모달리티

이 섹션은 APS BER 프로그램에서 사용되는 6가지 주요 X선 모달리티를 문서화합니다.
각 모달리티는 서로 다른 X선-물질 상호작용을 활용하여 시료 구조와 조성의
보완적인 측면을 보여줍니다.

## 모달리티 개요

| 모달리티 | 상호작용 | 측정 대상 | 공간 해상도 | 주요 빔라인 |
|----------|----------|----------|------------|------------|
| [결정학](crystallography/) | 회절 | 원자 구조 | Å (0.1 nm) | 21-ID-D/F/G |
| [토모그래피](tomography/) | 흡수/위상 | 3D 미세구조 | 50 nm – 1 µm | 2-BM-A, 7-BM-B, 32-ID |
| [XRF 현미경](xrf_microscopy/) | 형광 | 원소 분포 | 30 nm – 20 µm | 2-ID-D/E, 8-BM-B |
| [분광학](spectroscopy/) | 흡수 | 화학종 | 1 µm – 1 mm | 9-BM, 20-BM, 25-ID |
| [타이코그래피](ptychography/) | 결맞음 산란 | 위상 & 진폭 | 5–20 nm | 2-ID-E, 33-ID-C |
| [산란](scattering/) | 소각/광각 | 나노구조, 동역학 | 통계적 (nm) | 12-ID-B/E |

## X선-물질 상호작용

```
입사 X선 빔
        │
        ▼
   ┌─────────┐
   │   시료   │──→ 투과빔 (흡수 → 토모그래피)
   │          │──→ 형광 X선 (원소 조성 → XRF)
   │          │──→ 회절빔 (결정 구조 → 결정학)
   │          │──→ 산란빔 (나노구조 → SAXS/WAXS/XPCS)
   └─────────┘
        │
        ▼
   흡수 스펙트럼 (화학 상태 → XAS/XANES/EXAFS)
```

## 데이터 규모 비교

| 모달리티 | 일반적 스캔 시간 | 원시 데이터 크기 | 후처리 크기 |
|----------|----------------|-----------------|------------|
| MX 데이터셋 | 5–30분 | 10–100 GB | 1–10 GB (구조) |
| µCT 스캔 | 1–60분 | 10–500 GB | 1–50 GB (볼륨) |
| XRF 맵 | 30분 – 24시간 | 1–100 GB | 0.1–10 GB (맵) |
| XAS 스펙트럼 | 10–60분 | 10–100 MB | 1–10 MB |
| 타이코그래피 스캔 | 10–60분 | 10–500 GB | 1–50 GB (이미지) |
| SAXS/WAXS | 1–60초/프레임 | 0.1–10 GB | 10–100 MB (프로파일) |

## 공통 데이터 형식

- **HDF5**: 대부분의 모달리티에서 기본 형식 (계층적, 자기 기술적, 병렬 I/O)
- **TIFF**: 레거시 이미지 형식, 투영 및 재구성된 슬라이스에 여전히 사용
- **CBF**: 결정학 바이너리 파일 (레거시 회절 형식)
- **NeXus**: 싱크로트론 데이터를 위한 정의된 스키마가 있는 HDF5 기반 표준

## 디렉토리 내용

| 하위 디렉토리 | 모달리티 | 파일 |
|-------------|----------|------|
| [crystallography/](crystallography/) | MX, SSX | README, data_format, ai_ml_methods |
| [tomography/](tomography/) | µCT, 나노-CT | README, data_format, reconstruction, ai_ml_methods |
| [xrf_microscopy/](xrf_microscopy/) | XRF 매핑 | README, data_format, analysis_pipeline, ai_ml_methods |
| [spectroscopy/](spectroscopy/) | XANES, EXAFS | README, data_format, ai_ml_methods |
| [ptychography/](ptychography/) | 결맞음 이미징 | README, data_format, ai_ml_methods |
| [scattering/](scattering/) | SAXS, WAXS, XPCS | README, data_format, ai_ml_methods |
