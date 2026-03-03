# 04 출판물 -- 방사광 데이터 분석 노트

## 목적

이 디렉토리에는 BER 프로그램의 방사광 과학 AI/ML 전략에 기여하는 엄선된
논문 리뷰, 출판물 추적, 참고 자료가 수록되어 있습니다. 모든 리뷰는 표준화된
템플릿을 따르므로 통찰을 빠르게 상호 참조하고 Advanced Photon Source (APS)의
빔라인 개발에 적용할 수 있습니다.

---

## 읽기 안내

| 단계 | 읽을 내용 | 이유 |
|------|-----------|------|
| 1 | `template_paper_review.md` | 본격적으로 읽기 전에 리뷰 형식 이해 |
| 2 | `ber_program_publications.md` | BER 프로그램의 기존 출판 현황 파악 |
| 3 | `ai_ml_synchrotron/README.md` | AI/ML 논문의 전체 구성 파악 |
| 4 | 개별 리뷰 (아래 목록) | 특정 방법론과 결과에 대한 심층 분석 |

---

## 이 디렉토리의 파일

| 파일 | 설명 |
|------|------|
| `README.md` | 이 색인 (현재 위치) |
| `template_paper_review.md` | 모든 논문 리뷰를 위한 표준화된 템플릿 |
| `ber_program_publications.md` | BER 프로그램 귀속 출판물 추적기 (2023-2025) |
| `ai_ml_synchrotron/` | 엄선된 리뷰 모음 -- 방사광 과학에 적용된 AI/ML |

---

## 논문 리뷰 (총 10편)

모든 리뷰는 `ai_ml_synchrotron/`에 있으며 템플릿을 따릅니다. 빠른 탐색을 위해
주요 주제별로 정리되어 있습니다.

### 클러스터링 및 분할

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 1 | `ai_ml_synchrotron/review_roi_finder_2022.md` | ROI-Finder: 비지도 XRF 세포 분할 | 2022 |
| 2 | `ai_ml_synchrotron/review_xrf_gmm_2013.md` | 세포 하위 구조 XRF를 위한 GMM 소프트 클러스터링 | 2013 |

### 노이즈 제거

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 3 | `ai_ml_synchrotron/review_tomogan_2020.md` | TomoGAN: GAN 기반 토모그래피 노이즈 제거 | 2020 |

### 자율/비지도 분석

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 4 | `ai_ml_synchrotron/review_ai_nerd_2024.md` | AI-NERD: 비지도 XPCS 핑거프린팅 | 2024 |

### 타이코그래피

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 5 | `ai_ml_synchrotron/review_ai_edge_ptychography_2023.md` | 실시간 엣지 타이코그래피 이미징 | 2023 |
| 6 | `ai_ml_synchrotron/review_ptychonet_2019.md` | PtychoNet: CNN 위상 복원 | 2019 |

### 해상도 향상

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 7 | `ai_ml_synchrotron/review_deep_residual_xrf_2023.md` | XRF 해상도를 위한 심층 잔차 네트워크 | 2023 |

### 전체 파이프라인 / 인프라

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 8 | `ai_ml_synchrotron/review_fullstack_dl_tomo_2023.md` | 토모그래피를 위한 풀스택 DL 파이프라인 | 2023 |
| 9 | `ai_ml_synchrotron/review_realtime_uct_hpc_2020.md` | 마이크로-CT를 위한 실시간 AI+HPC | 2020 |

### 워크숍 보고서 및 서베이

| # | 파일 | 약칭 | 연도 |
|---|------|------|------|
| 10 | `ai_ml_synchrotron/review_ai_als_workshop_2024.md` | AI@ALS 워크숍 보고서 | 2024 |

---

## 템플릿

리뷰 템플릿(`template_paper_review.md`)은 다음을 표준화합니다:

- **서지 메타데이터** -- 제목, 저자, 학술지, DOI, 빔라인/시설
- **요약(TL;DR)** -- 한 문단 핵심 요약
- **배경 및 동기** -- 해당 연구의 중요성
- **방법** -- 기술적 접근법, 모델 아키텍처, 데이터 파이프라인
- **주요 결과** -- 정량적 성과 및 성능 지표
- **데이터 및 코드 가용성** -- 링크, 재현성 점수 (1-5)
- **강점** -- 논문의 우수한 점
- **한계 및 공백** -- 부족한 점 또는 누락된 사항
- **APS BER 프로그램과의 관련성** -- 프로그램에 대한 직접적 적용 가능성
- **실행 가능한 시사점** -- 팀을 위한 구체적 다음 단계

---

## 기여 방법

새 리뷰를 추가하려면:

1. `template_paper_review.md`를 적절한 하위 디렉토리에 복사합니다.
2. `review_<간략_설명>_<연도>.md`로 이름을 변경합니다.
3. 모든 섹션을 작성합니다. 섹션을 비워두지 마세요 -- 해당되지 않는 경우 "N/A"로
   작성합니다.
4. 이 README와 하위 디렉토리 README를 새 항목으로 업데이트합니다.
5. `docs(pubs): add review of <저자> <연도>` 형식의 메시지로 커밋합니다.

---

## 관리자

- APS BER 프로그램 AI/ML 팀, Argonne National Laboratory
- 최종 업데이트: 2025-Q4
