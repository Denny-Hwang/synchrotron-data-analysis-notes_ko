# X선 산란을 위한 AI/ML 방법

## 개요

산란을 위한 AI/ML 방법은 자동 상(phase) 식별, 패턴 분류, 실시간 데이터 분석, 상관 데이터로부터의 동역학 추출에 중점을 둡니다. 산란 실험의 높은 처리량과 다성분 피팅의 복잡성은 ML 접근법을 특히 유용하게 만듭니다.

## ML 문제 분류

| 문제 | 유형 | 입력 | 출력 |
|---------|------|-------|--------|
| 상 식별 | 분류(classification) | 1D I(q) 또는 2D 패턴 | 상/혼합물 레이블 |
| 재료 지문 분석(fingerprinting) | 비지도 학습(unsupervised) | I(q) 프로파일 또는 g₂(τ) | 클러스터 할당 |
| 파라미터 추출 | 회귀(regression) | I(q) 프로파일 | 크기, 형상 파라미터 |
| 모델 피팅 | 회귀 | I(q) 프로파일 | 최적 모델 + 파라미터 |
| 이상 탐지(anomaly detection) | 분류 | 시분해 I(q) | 전이 사건 |
| 동역학 분류 | 분류 | g₂(q,τ) | 동역학 유형 |

## AI-NERD: XPCS를 위한 비지도 지문 분석

**참조**: Horwath et al., Nature Communications (2024)

### 개념
**AI-NERD** (AI for Nonequilibrium Relaxation Dynamics)는 물리적 모델 피팅 없이 XPCS 상관 함수로부터 재료 동역학을 "지문 분석"하는 비지도 ML 방법입니다.

### 방법
```
XPCS correlation functions g₂(q, τ)
    │
    ├─→ Feature extraction
    │       Encode g₂ at multiple q values into fixed-length feature vector
    │       Options: direct sampling, wavelet coefficients, autoencoder
    │
    ├─→ Dimensionality reduction
    │       UMAP or t-SNE → 2D embedding
    │
    ├─→ Clustering
    │       HDBSCAN or k-means on embedded space
    │
    └─→ Fingerprint map
            Each cluster = distinct dynamical state
            Changes in cluster = dynamical transitions
```

### 핵심 혁신
- **모델 프리(model-free)**: 완화(relaxation)의 함수 형태에 대한 가정 불필요
- **비지도(unsupervised)**: 레이블 없이 동적 상태를 발견
- **포괄적**: 동역학의 전체 q-의존성을 포착
- **고감도**: 수동 피팅이 놓칠 수 있는 미묘한 전이를 감지

### 응용
- 콜로이드 겔 에이징 → 서로 다른 동적 상(dynamical phases) 식별
- 연성 물질(soft matter)에서의 온도 구동 상전이
- 측정 중 방사선 손상 추적
- 감지된 전이에 기반한 실시간 실험 조향(steering)

*상세 리뷰 참조: [04_publications/ai_ml_synchrotron/review_ai_nerd_2024.md](../../04_publications/ai_ml_synchrotron/review_ai_nerd_2024.md)*

## 산란으로부터의 상 식별

### 전통적 접근법
- 측정된 I(q)를 알려진 패턴 데이터베이스와 비교
- 결정질 상의 Rietveld 정밀화 (WAXS)
- SAXS 모델의 수동 선택 및 피팅

### ML 접근법

#### 1. 2D 패턴에 대한 CNN
```python
# Input: 2D scattering pattern (256×256 pixels)
# Output: Phase classification (N classes)

class ScatteringClassifier(nn.Module):
    def __init__(self, n_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(4)
        )
        self.classifier = nn.Linear(128 * 16, n_classes)

    def forward(self, x):
        return self.classifier(self.features(x).flatten(1))
```

#### 2. 1D 프로파일 매칭
- 알려진 구조에 대한 시뮬레이션 I(q) 프로파일 라이브러리로 훈련
- 비닝된 I(q) 값에 대해 Random Forest, SVM 또는 MLP 분류기 사용
- 다중 레이블 분류(multi-label classification)로 혼합물 처리

#### 3. 변분 오토인코더(Variational Autoencoders, VAE)
- 산란 패턴의 잠재 표현(latent representation)을 학습
- 잠재 공간(latent space) 구조가 재료 범주를 드러냄
- 데이터 증강을 위한 합성 패턴 생성

## SAXS 모델 피팅

### 전통적 방법
분석적 모델(구, 원통, 코어-셸 등)을 I(q)에 피팅:

```python
# SASView-style model fitting
from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment

model = load_model('sphere')
# Parameters: radius, sld, sld_solvent, scale, background
# Minimize chi² between model and data
```

### 신경망 피팅

I(q)로부터 직접 모델 파라미터를 예측하도록 NN을 훈련:

```
I(q) profile → CNN/MLP → [radius, polydispersity, concentration, ...]
```

**장점**:
- 즉각적인 추론 (최소자승 피팅의 수 분 대비 ~ms)
- 확률 분포 예측을 통해 퇴화 해(degenerate solutions) 처리 가능
- 고속 처리량 측정 중 실시간 분석 가능

**훈련 데이터**: 다양한 파라미터의 알려진 모델로부터 대규모 라이브러리 생성

## 시분해 분석(Time-Resolved Analysis)

### 반응 속도론 SAXS(Kinetic SAXS)
반응, 자기 조립(self-assembly), 또는 상전이 중 구조적 변화를 모니터링:

```
Time series of I(q,t) profiles
    │
    ├─→ SVD / PCA decomposition → identify number of independent components
    │
    ├─→ MCR-ALS (Multivariate Curve Resolution) → extract pure component spectra
    │
    └─→ ML classification → detect transition points, classify phases
```

### 자동 이벤트 감지
- 시분해 SAXS에서 전이 이벤트를 식별하도록 CNN 훈련
- 유의미한 구조적 변화가 발생하는 프레임을 표시
- 자율적 실험 결정 가능 (예: 온도 램프 속도 조정)

## XPCS 동역학 분석

### 전통적 피팅
```python
from scipy.optimize import curve_fit

def kww(tau, beta, tau_r, gamma):
    """Kohlrausch-Williams-Watts stretched exponential."""
    return 1 + beta * np.exp(-2 * (tau / tau_r)**gamma)

# Fit each q independently
for q_idx in range(n_q):
    popt, pcov = curve_fit(kww, tau, g2[q_idx],
                           p0=[0.1, 1.0, 1.0],
                           bounds=([0, 0, 0], [1, np.inf, 2]))
```

### ML 강화 XPCS 분석

1. **완화 시간 추출**: CNN이 g₂ 곡선으로부터 직접 τ(q) 예측
2. **동역학 분류**: 동역학 유형 범주화 (확산, 탄도, 압축, 늘어진)
3. **q-의존성 분석**: 전체 g₂(q,τ) 데이터셋으로부터 분산 관계(dispersion relation) D(q) 예측
4. **이시간 분석(two-time analysis)**: CNN이 이시간 상관 맵으로부터 에이징 체제(aging regimes) 식별

## 벤치마크 데이터셋

| 데이터셋 | 유형 | 설명 | 접근 |
|---------|------|-------------|--------|
| SAXS-benchmark | SAXS | 합성 + 실험 프로파일 | 커뮤니티 |
| NIST SRM 표준 | SAXS/WAXS | 참조 재료 (glassy carbon, silver behenate) | NIST |
| XPCS 콜로이드 겔 | XPCS | 시분해 동역학 데이터셋 | APS |

## 현재 한계

1. **훈련 데이터**: 레이블이 지정된 산란 데이터셋이 제한적; 시뮬레이션에 대한 의존도가 높음
2. **모델 일반화**: 특정 재료 시스템에서 훈련된 네트워크는 전이(transfer)가 어려울 수 있음
3. **다성분 혼합물**: 복잡한 혼합물에서의 산란 역합성(deconvolution)은 여전히 어려운 과제
4. **절대 스케일링**: ML 방법은 종종 절대 강도 정보를 무시
5. **q-분해능 효과**: 기기 스미어링(instrumental smearing)을 고려해야 함

## 개선 기회

1. **자기 지도 사전 훈련(self-supervised pre-training)**: 레이블 없는 데이터로부터 산란 표현 학습
2. **물리 기반 네트워크(physics-informed networks)**: 산란 이론 제약을 아키텍처에 통합
3. **생성 모델(generative models)**: 구조-산란 관계 탐구를 위한 VAE/확산 모델(diffusion models)
4. **다중 모달(multi-modal)**: SAXS + WAXS + XRF 결합 분석
5. **스트리밍 분석**: 고속 처리량 측정 중 실시간 상 식별
6. **파운데이션 모델(foundation models)**: 다양한 재료 분류에 걸쳐 산란 데이터를 위한 대규모 사전 훈련 모델
