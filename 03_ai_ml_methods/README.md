# 방사광 과학을 위한 AI/ML 방법론

## 개요

이 섹션은 방사광 X선 데이터 분석에 적용되는 AI/ML 방법론의 포괄적인 분류 체계를 작업 범주별로 정리하여 제공합니다. 각 범주는 전통적 접근 방식, 딥러닝(Deep Learning) 방법, 그리고 방사광 데이터에 특화된 적용 사례를 다룹니다.

## 방법론 분류 체계

```
방사광 과학을 위한 AI/ML
├── 이미지 분할(Image Segmentation)
│   ├── 의미론적 분할(Semantic) (픽셀 분류)
│   ├── 인스턴스 분할(Instance) (개별 객체 탐지)
│   └── 파놉틱 분할(Panoptic) (의미론적 + 인스턴스)
│
├── 노이즈 제거(Denoising)
│   ├── 지도 학습(Supervised) (쌍을 이루는 학습 데이터)
│   ├── 자기 지도 학습(Self-supervised) (깨끗한 목표 없음)
│   └── GAN 기반 (적대적 학습)
│
├── 재구성(Reconstruction)
│   ├── GPU 가속 고전적 방법 (TomocuPy)
│   ├── CNN 후처리 (FBPConvNet)
│   ├── 학습 기반 반복법 (언롤링 최적화)
│   └── 암시적 신경 표현(Implicit Neural Representations, INR)
│
├── 자율 실험(Autonomous Experiment)
│   ├── ROI 선택 (ROI-Finder)
│   ├── 베이지안 최적화(Bayesian Optimization)
│   └── 비지도 핑거프린팅(AI-NERD)
│
└── 다중 모달리티 통합(Multimodal Integration)
    ├── 교차 모달리티 정합(Cross-modal Registration)
    ├── 결합 분석(Joint Analysis)
    └── 융합 네트워크(Fusion Networks)
```

## 모달리티별 방법론 비교

| 방법론 범주 | 결정학(Crystallography) | 토모그래피(Tomography) | XRF | 분광학(Spectroscopy) | 타이코그래피(Ptychography) | 산란(Scattering) |
|----------------|----------------|------------|-----|-------------|-------------|-----------|
| **분할** | 결정 탐지 | 상(Phase) 식별, 기공/입자 | 세포 분할 | — | 특징 추출 | — |
| **노이즈 제거** | — | TomoGAN, N2N | 해상도 향상 | 스펙트럼 평활화 | — | — |
| **재구성** | 위상 복원 | TomocuPy, DL 재구성 | — | — | PtychoNet, AI@Edge | — |
| **자율 실험** | 결정 센터링 | 스마트 스캐닝 | ROI-Finder | 능동적 에너지 선택 | 적응적 스캐닝 | AI-NERD |
| **다중 모달리티** | AlphaFold + MR | CT + XAS | XRF + ptycho | XAS + XRF 매핑 | Ptycho + XRF | SAXS + WAXS |

## 분야 공통 주제

### 1. 학습 데이터 문제

- 레이블이 지정된 방사광 데이터가 부족함 (전문가 주석 작업의 비용이 높음)
- 자기 지도 학습 및 비지도 학습 방법이 선호됨
- 시뮬레이션 기반 사전 학습(Pre-training)이 점점 보편화
- 능동 학습(Active Learning)으로 주석 작업 요구량을 최소화

### 2. 규모 문제

- 방사광 데이터 볼륨이 매우 대규모 (실험당 TB 단위)
- 모델이 2K³에서 4K³ 복셀 볼륨을 처리할 수 있어야 함
- 패치 기반 접근 방식에서 스티칭 아티팩트 발생
- HPC 시스템에서의 분산/병렬 추론

### 3. 실시간 요구 사항

- APS-U 업그레이드 이후, 데이터 속도가 실시간 분석을 요구
- 데이터 수집 중 스트리밍 추론
- 엣지 컴퓨팅 배포 (FPGA, 임베디드 GPU)
- 실험 조종 결정을 위한 지연 시간 예산: 밀리초 단위

### 4. 물리적 정확성

- ML 출력이 물리적으로 의미 있어야 함
- 물리 정보 기반 손실 함수(Physics-informed Loss Functions) 및 아키텍처
- 과학적 신뢰도를 위한 불확실성 정량화(Uncertainty Quantification)
- 하이브리드 접근법: ML + 물리 기반 검증

## 디렉토리 내용

| 하위 디렉토리 | 범주 | 주요 방법론 |
|-------------|----------|-------------|
| [image_segmentation/](image_segmentation/) | 분할 | U-Net 변형, 세포 분할, 토모그래피 상(Phase) 식별 |
| [denoising/](denoising/) | 노이즈 제거 | TomoGAN, Noise2Noise, 심층 잔차 네트워크 |
| [reconstruction/](reconstruction/) | 재구성 | TomocuPy, PtychoNet, 동적 영상을 위한 INR |
| [autonomous_experiment/](autonomous_experiment/) | 자율 실험 | ROI-Finder, 베이지안 최적화, AI-NERD |
| [multimodal_integration/](multimodal_integration/) | 통합 | XRF+ptycho, CT+XAS, 광학+X선 정합 |
