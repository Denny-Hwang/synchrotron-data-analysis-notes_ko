# 방사광 과학을 위한 AI/ML -- 엄선된 논문 리뷰

## 개요

이 디렉토리에는 인공지능, 머신러닝, 방사광 X선 과학의 교차점에 있는 주요
출판물에 대한 심층 리뷰가 수록되어 있습니다. 각 리뷰는
`../template_paper_review.md`에 정의된 표준화된 템플릿을 따르며, Advanced
Photon Source (APS)의 APS BER 프로그램과의 관련성에 대한 명시적 평가를
포함합니다.

이 모음집은 기초 방법론(2013-2019), 성숙 기술(2020-2022), 최신 개발
(2023-2025)을 아우르며, 빔라인 과학에 적용 가능한 AI/ML 역량의 포괄적인
전경을 제공합니다.

---

## 카테고리별 리뷰

### 노이즈 제거 및 선량 감소

방사광 데이터의 노이즈를 줄여, 이미지 품질을 유지하면서 낮은 방사선량 또는
빠른 측정을 가능하게 하는 방법.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_tomogan_2020.md` | Liu et al., JOSA A (2020) | 방사광 토모그래피를 위한 GAN 기반 노이즈 제거; 4-10배 선량 감소 |
| `review_realtime_uct_hpc_2020.md` | McClure et al., SMC (2020) | 마이크로-CT를 위한 노이즈 제거를 포함한 엔드투엔드 AI+HPC 워크플로우 |

### 분할 및 클러스터링

관심 영역 식별, 물질 상 분류, 또는 하이퍼스펙트럴 데이터 분할을 위한 기술.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_roi_finder_2022.md` | Chowdhury et al., J. Synchrotron Rad. (2022) | 자동 XRF ROI 추천을 위한 PCA + 퍼지 k-평균 |
| `review_xrf_gmm_2013.md` | Ward et al., Microsc. Microanal. (2013) | 말라리아 연구를 위한 세포 하위 구조 XRF GMM 소프트 클러스터링 |

### 재구성 및 위상 복원

토모그래피 재구성과 타이코그래피 위상 복원의 속도, 품질 또는 둘 다를 개선하는
AI 기반 접근법.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_ai_edge_ptychography_2023.md` | Babu et al., Nature Comm. (2023) | 엣지 GPU/FPGA에서 2 kHz 실시간 스트리밍 타이코그래피 |
| `review_fullstack_dl_tomo_2023.md` | Zhang et al., The Innovation (2023) | 방사광 토모그래피 파이프라인을 위한 풀스택 DL 비전 |
| `review_ptychonet_2019.md` | Guan et al. (2019) | 반복적 방법 대비 90% 속도 향상의 CNN 위상 복원 |

### 자율 및 적응형 실험

빔타임 중 실시간 의사결정, 적응형 스캐닝, 또는 자율 실험 제어를 가능하게 하는
시스템.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_roi_finder_2022.md` | Chowdhury et al., J. Synchrotron Rad. (2022) | 빔타임 효율적 XRF 스캐닝을 위한 자동 ROI 추천 |
| `review_ai_nerd_2024.md` | Horwath et al., Nature Comm. (2024) | UMAP + HDBSCAN을 통한 비지도 XPCS 동역학 핑거프린팅 |
| `review_aiedge_ptycho_2023.md` | Babu et al., Nature Comm. (2023) | 타이코그래피 이미징을 위한 실시간 피드백 루프 |
| `review_aidriven_xanes_2025.md` | Du et al., npj Comput. Mater. (2025) | 베이지안 최적화를 활용한 AI 기반 동적 XANES 워크플로우 |

### 해상도 향상

광학 또는 검출기의 물리적 한계를 넘어 방사광 측정의 실효 공간 또는 스펙트럼
해상도를 향상시키는 방법.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_deep_residual_xrf_2023.md` | npj Comp. Mater. (2023) | 심층 잔차 네트워크를 통한 XRF 2-4배 실효 해상도 향상 |

### 구조 생물학

단백질 구조 예측 및 결정학적 분석을 위한 AI 방법.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_alphafold_2021.md` | Jumper et al., Nature (2021) | AlphaFold: 혁신적 단백질 구조 예측 |

### 다중 모달, 서베이 및 인프라

여러 모달리티에 걸친 광범위한 서베이, 워크숍 보고서, 시설 전체 인프라를 다루는
논문.

| 리뷰 | 논문 | 주요 기여 |
|------|------|-----------|
| `review_fullstack_dl_tomo_2023.md` | The Innovation (2023) | 토모그래피 전 단계에 걸친 포괄적 파이프라인 비전 |
| `review_realtime_uct_hpc_2020.md` | McClure et al., SMC (2020) | 실시간 마이크로-CT 분석을 위한 풀 파이프라인 통합 |
| `review_ai_als_workshop_2024.md` | Synchrotron Rad. News (2024) | AI@ALS 워크숍: APS에 적용 가능한 시설 전체 ML 수요 조사 |

---

## 전체 리뷰 목록 (시간순)

| # | 파일 | 제1저자 | 연도 | 모달리티 |
|---|------|---------|------|----------|
| 1 | `review_xrf_gmm_2013.md` | Ward | 2013 | XRF |
| 2 | `review_ptychonet_2019.md` | Guan | 2019 | 타이코그래피 |
| 3 | `review_tomogan_2020.md` | Liu | 2020 | 토모그래피 |
| 4 | `review_realtime_uct_hpc_2020.md` | McClure | 2020 | 마이크로-CT |
| 5 | `review_alphafold_2021.md` | Jumper | 2021 | 결정학 |
| 6 | `review_roi_finder_2022.md` | Chowdhury | 2022 | XRF |
| 7 | `review_aiedge_ptycho_2023.md` | Babu | 2023 | 타이코그래피 |
| 8 | `review_ai_edge_ptychography_2023.md` | Babu | 2023 | 타이코그래피 |
| 9 | `review_fullstack_dl_tomo_2023.md` | Zhang | 2023 | 토모그래피 |
| 10 | `review_fullstack_tomo_2023.md` | Zhang | 2023 | 토모그래피 |
| 11 | `review_deep_residual_xrf_2023.md` | Wu | 2023 | XRF |
| 12 | `review_ai_nerd_2024.md` | Horwath | 2024 | XPCS |
| 13 | `review_ai_als_workshop_2024.md` | Parkinson | 2024 | 다중 모달 |
| 14 | `review_aidriven_xanes_2025.md` | Du | 2025 | 분광학 |

---

## 추천 읽기 순서

방사광 과학에서의 AI/ML에 익숙하지 않은 독자를 위해, 다음 읽기 순서가
논리적인 진행을 제공합니다:

1. **`review_ai_als_workshop_2024.md`** -- 현대 광원에서의 ML 수요 전경을
   이해하기 위해 광범위한 서베이부터 시작합니다.

2. **`review_fullstack_dl_tomo_2023.md`** -- 개별 방법들이 엔드투엔드
   워크플로우에 어떻게 맞는지 이해하기 위해 풀스택 파이프라인 비전을
   읽습니다.

3. **`review_tomogan_2020.md`** 및 **`review_ptychonet_2019.md`** -- 두 가지
   기초적인 딥러닝 접근법(노이즈 제거와 재구성)을 학습합니다.

4. **`review_roi_finder_2022.md`** 및 **`review_xrf_gmm_2013.md`** -- 고전적
   방법에서 현대적 방법까지 XRF를 위한 클러스터링 및 분할 방법을 탐구합니다.

5. **`review_aiedge_ptycho_2023.md`** 및
   **`review_realtime_uct_hpc_2020.md`** -- 실시간 및 엣지 컴퓨팅 접근법을
   살펴봅니다.

6. **`review_deep_residual_xrf_2023.md`** -- 보완적 역량으로서의 해상도 향상을
   다룹니다.

7. **`review_ai_nerd_2024.md`** 및 **`review_aidriven_xanes_2025.md`** --
   자율 및 AI 기반 실험 방법을 다룹니다.

8. **`review_alphafold_2021.md`** -- 구조 생물학 및 단백질 구조 예측을 위한
   AI를 다룹니다.

---

## 상호 참조

- `../template_paper_review.md` -- 리뷰 템플릿
- `../ber_program_publications.md` -- BER 프로그램 출판물
- `../../03_ai_ml_methods/` -- AI/ML 기술 배경
- `../../05_tools_and_code/` -- 리뷰에서 참조된 소프트웨어 도구

---

_최종 업데이트: 2026-Q1_
