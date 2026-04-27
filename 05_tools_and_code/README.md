# 오픈소스 도구 생태계

## 개요

이 섹션에서는 BER 프로그램과 광범위한 APS 방사광 과학 생태계에서 사용되는 주요 오픈소스 소프트웨어 도구를 분석합니다. 각 도구의 아키텍처, 강점, 한계 및 개선 기회를 검토합니다.

## 도구 현황

```
┌─────────────────── Experiment Control ───────────────────┐
│  Bluesky (RunEngine) + EPICS (hardware) + ophyd (devices) │
└──────────────────────┬───────────────────────────────────┘
                       │ Data
                       ▼
┌──────────────── Data Analysis Tools ─────────────────────┐
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ TomoPy   │  │ TomocuPy │  │  MAPS    │  │ ROI-     │ │
│  │(CPU tomo)│  │(GPU tomo)│  │(XRF fit) │  │ Finder   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Larch   │  │  PyNX    │  │MLExchange│               │
│  │(XAS)     │  │(ptycho)  │  │(ML plat) │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└──────────────────────────────────────────────────────────┘
```

## 도구 비교

| 도구 | 분석 기법 | 언어 | GPU | 성숙도 | 활발한 개발 |
|------|----------|---------|-----|----------|-----------|
| **ROI-Finder** | XRF | Python | 아니오 | 연구 단계 | 낮음 |
| **TomocuPy** | 토모그래피 | Python/CuPy | 예 | 프로덕션 | 높음 |
| **TomoPy** | 토모그래피 | Python/C | 아니오 | 프로덕션 | 높음 |
| **HTTomo** | 토모그래피 | Python/CUDA | 예 | 프로덕션 | 높음 |
| **Tike** | 타이코그래피 | Python/CUDA | 예 | 프로덕션 | 높음 |
| **MAPS** | XRF | IDL/C++ | 아니오 | 프로덕션 | 중간 |
| **PyXRF** | XRF | Python | 아니오 | 프로덕션 | 높음 |
| **MLExchange** | 다중 | Python | 예 | 개발 중 | 높음 |
| **Bluesky** | 제어 | Python | 아니오 | 프로덕션 | 높음 |
| **EPICS** | 제어 | C/Python | 아니오 | 프로덕션 | 높음 |

## 디렉토리 내용

| 하위 디렉토리 | 도구 | 주제 |
|-------------|------|-------|
| [roi_finder/](roi_finder/) | ROI-Finder | XRF ROI 선택 (상세 역공학) |
| [tomocupy/](tomocupy/) | TomocuPy | GPU 가속 토모그래피 재구성 |
| [tomopy/](tomopy/) | TomoPy | 표준 토모그래피 재구성 |
| [httomo/](httomo/) | HTTomo | 모듈식 GPU 고처리량 토모그래피 파이프라인 |
| [tike/](tike/) | Tike | GPU 가속 타이코그래피 재구성(ePIE/DM/LSQ-ML) |
| [maps_software/](maps_software/) | MAPS | XRF 스펙트럼 분석 |
| [pyxrf/](pyxrf/) | PyXRF | NSLS-II XRF 스펙트럼 피팅 및 원소 매핑 |
| [mlexchange/](mlexchange/) | MLExchange | 광원 시설용 ML 플랫폼 |
| [aps_github_repos/](aps_github_repos/) | APS GitHub | 저장소 카탈로그 |
| [bluesky_epics/](bluesky_epics/) | Bluesky/EPICS | 실험 오케스트레이션 |
