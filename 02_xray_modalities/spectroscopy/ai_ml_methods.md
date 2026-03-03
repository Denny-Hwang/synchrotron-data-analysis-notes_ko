# X선 흡수 분광법을 위한 AI/ML 방법

## 개요

XAS를 위한 AI/ML 방법은 스펙트럼 분류를 자동화하고, 신속한 화학적 종분화(speciation)를 가능하게 하며, 복잡한 다성분 혼합물의 분석을 개선합니다. 이러한 접근법은 수천 개 스펙트럼의 수동 분석이 비현실적인 대규모 µ-XANES 이미징 데이터셋에 특히 유용합니다.

## ML 문제 분류

| 문제 | 유형 | 입력 | 출력 |
|---------|------|-------|--------|
| 화학종 식별 | 분류(classification) | XANES 스펙트럼 | 화학종 레이블 |
| 선형 결합 피팅 | 회귀(regression) | 스펙트럼 + 참조 시료 | 성분 분율 |
| 모서리 에너지 결정 | 회귀 | XANES 스펙트럼 | 모서리 에너지 (eV) |
| 산화 상태 매핑 | 분류 | µ-XANES 이미지 스택 | 산화 상태 맵 |
| 스펙트럼 잡음 제거 | 회귀 | 잡음이 있는 스펙트럼 | 깨끗한 스펙트럼 |
| 구조 예측 | 회귀 | EXAFS 스펙트럼 | 결합 거리, 배위수 |

## 스펙트럼 분류

### 지도 학습 분류(Supervised Classification)

참조 XANES 스펙트럼 라이브러리를 사용하여 분류기를 훈련합니다:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# X: (Nsamples, Nenergy_points) - normalized XANES spectra
# y: labels (e.g., 'Fe2O3', 'FeO', 'FePO4', ...)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Classify unknown spectrum
prediction = clf.predict(unknown_spectrum.reshape(1, -1))
probabilities = clf.predict_proba(unknown_spectrum.reshape(1, -1))
```

**접근법**:
- **Random Forest**: 견고하고 해석 가능한 특징 중요도(feature importance)
- **SVM**: 고차원 스펙트럼 데이터에 효과적
- **신경망(Neural Networks)**: 복잡한 스펙트럼 패턴을 위한 MLP 또는 1D CNN
- **전이 학습(transfer learning)**: 시뮬레이션 스펙트럼(FEFF/FDMNES)으로 사전 훈련(pre-train) 후, 실험 데이터로 미세 조정(fine-tune)

### 데이터베이스 기반 분류

참조 스펙트럼 데이터베이스의 등장으로 ML 훈련이 가능해지고 있습니다:
- **XASdb**: 실험 XANES 스펙트럼 데이터베이스
- **Materials Project**: 결정 구조로부터 계산된 XANES (FEFF 계산)
- **XANESNET**: 계산된 Fe K-edge 스펙트럼으로 훈련된 신경망

## PCA 기반 분석

### 성분 식별

```python
from sklearn.decomposition import PCA

# For µ-XANES imaging: reshape to (Npixels, Nenergies)
spectra_2d = xanes_stack.reshape(-1, n_energies)

# Remove pixels with no signal
mask = spectra_2d.mean(axis=1) > threshold
spectra_filtered = spectra_2d[mask]

pca = PCA(n_components=10)
scores = pca.fit_transform(spectra_filtered)
components = pca.components_

# Determine number of independent components
# (number of significant eigenvalues)
explained_var = pca.explained_variance_ratio_
n_components = np.argmax(np.cumsum(explained_var) > 0.99) + 1
print(f"Number of independent spectral components: {n_components}")
```

### 타겟 변환(Target Transformation)

PCA와 타겟 테스트를 결합하여 끝점 스펙트럼(end-member spectra)을 식별합니다:
1. PCA로 독립 성분 수를 결정
2. 참조 스펙트럼을 잠재적 끝점(end-member)으로 테스트
3. SPOIL/IND 값으로 적합도 평가
4. µ-XANES 분석에 가장 일반적으로 사용되는 접근법

## 자동 선형 결합 피팅(Automated Linear Combination Fitting)

### 전통적 LCF
```python
from scipy.optimize import nnls

# reference_matrix: (Nenergies, Nreferences)
# unknown: (Nenergies,) - the unknown spectrum

fractions, residual = nnls(reference_matrix, unknown)
fractions = fractions / fractions.sum()  # normalize to 100%
```

### ML 강화 LCF

**전통적 LCF의 문제점**:
- 참조 화합물의 사전 선택이 필요
- 가능한 참조 시료가 많은 경우 조합 폭발(combinatorial explosion)
- 알려지지 않은 상(phase)을 처리할 수 없음

**ML 해결책**:
- **신경망 피팅(neural network fitting)**: 스펙트럼에서 직접 분율을 예측하도록 NN 훈련
- **변분 추론(variational inference)**: 분율에 대한 불확실성을 제공하는 베이지안(Bayesian) 접근법
- **클러스터링 + LCF**: 먼저 유사도별로 픽셀을 클러스터링한 후, 대표 스펙트럼을 피팅

## XANES를 위한 딥러닝(Deep Learning)

### 1D 합성곱 신경망(1D Convolutional Neural Networks)

```python
import torch.nn as nn

class XANESClassifier(nn.Module):
    def __init__(self, n_energies, n_classes):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        self.fc = nn.Linear(128, n_classes)

    def forward(self, x):
        # x: (batch, 1, n_energies)
        features = self.conv(x).squeeze(-1)
        return self.fc(features)
```

### 응용
- **산화 상태 예측**: 모서리 형상으로부터 Fe²⁺/Fe³⁺ 분류
- **배위 환경(coordination environment)**: pre-edge 특징으로부터 사면체/팔면체 예측
- **종분화 매핑**: 훈련된 모델을 µ-XANES 스택의 각 픽셀에 적용

## 스펙트럼 잡음 제거(Spectral Denoising)

### 웨이블릿 잡음 제거(Wavelet Denoising)
- 웨이블릿 변환 적용, 고주파 계수 임계값 처리, 역변환 수행
- 평활화(smoothing)보다 스펙트럼 특징을 더 잘 보존

### 오토인코더 잡음 제거(Autoencoder Denoising)
- 깨끗한 참조 스펙트럼으로 오토인코더(autoencoder)를 훈련
- 잡음이 있는 스펙트럼 입력 → 인코딩 → 디코딩 → 깨끗한 스펙트럼
- 장점: 물리적으로 의미 있는 스펙트럼 특징을 학습

## 신흥 방법론(Emerging Methods)

### 시뮬레이션 기반 전이 학습(Transfer Learning from Simulations)
1. 결정 구조로부터 FEFF/FDMNES 계산을 사용하여 대규모 훈련 세트 생성
2. 시뮬레이션 스펙트럼으로 신경망 사전 훈련
3. 소규모 실험 데이터셋으로 미세 조정
4. 제한된 실험 훈련 데이터 문제를 해결

### 자기 지도 학습(Self-Supervised Learning)
- 훈련 중 스펙트럼의 일부를 마스킹 (마스킹된 스펙트럼 모델링)
- 레이블 없이 스펙트럼 표현(representation)을 학습
- 특정 분류/회귀 작업을 위해 미세 조정

### 불확실성 정량화(Uncertainty Quantification)
- **몬테카를로 드롭아웃(Monte Carlo dropout)**: 드롭아웃을 적용한 상태에서 추론을 여러 번 수행하여 불확실성 추정
- **앙상블 방법(ensemble methods)**: 여러 모델을 훈련하고 분산(variance)을 불확실성으로 활용
- **베이지안 신경망(Bayesian neural networks)**: 사후 분포(posterior distribution)로부터 직접 불확실성 도출
- 신뢰도가 중요한 과학적 응용에서 핵심적

## 현재 한계

1. **참조 데이터베이스 완전성**: 많은 환경 화학종에 대한 참조 스펙트럼이 부족
2. **스펙트럼 유사성**: 일부 화학종은 XANES만으로는 거의 구별 불가
3. **비선형 혼합(non-linear mixing)**: 실제 스펙트럼이 단순한 선형 조합이 아닐 수 있음
4. **자기 흡수(self-absorption)**: 두꺼운/농축된 시료가 스펙트럼 형상을 왜곡
5. **방사선 손상(radiation damage)**: 빔 손상이 측정 중 종분화를 변화시킴

## 개선 기회

1. **포괄적 스펙트럼 데이터베이스**: 레이블이 지정된 데이터베이스 구축을 위한 커뮤니티 차원의 노력
2. **다중 모서리 분석(multi-edge analysis)**: 여러 원소 모서리의 정보를 결합
3. **XAS + XRF 결합 분석**: XRF의 공간 맥락을 활용하여 스펙트럼 피팅 제약
4. **능동 학습(active learning)**: ML이 최대 정보를 위해 어떤 스펙트럼을 측정할지 안내
5. **실시간 종분화**: 측정 중 XAS 데이터를 ML 모델로 스트리밍
