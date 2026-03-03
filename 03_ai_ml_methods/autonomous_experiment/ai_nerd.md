# AI-NERD: XPCS 동역학을 위한 비지도 핑거프린팅(Unsupervised Fingerprinting)

**참고문헌**: Horwath et al., Nature Communications (2024)

## 개요

**AI-NERD** (AI for Nonequilibrium Relaxation Dynamics)는 물리적 모델 가정 없이 X선 광자 상관 분광법(X-ray Photon Correlation Spectroscopy, XPCS) 데이터로부터 물질 동역학을 "핑거프린팅"하는 비지도 기계 학습 프레임워크입니다.

## 동기

전통적인 XPCS 분석은 상관 함수를 가정된 모델(지수 함수, 확장 지수 함수 등)에 피팅하는 것을 포함합니다. 이 접근 방식은:
- 올바른 모델을 사전에 선택해야 함
- 예상치 못한 동역학적 거동을 놓칠 수 있음
- 대규모 데이터셋에서 동역학적 상태를 쉽게 분류할 수 없음
- 대규모 매개변수 연구에 노동 집약적임

AI-NERD는 모델 프리(Model-free), 비지도 접근 방식으로 이러한 한계를 해결합니다.

## 방법

### 파이프라인(Pipeline)

```mermaid
graph TD
    A[XPCS 시계열<br>스페클 패턴] --> B[상관 함수<br>다중 q에서 g₂(q,τ)]
    B --> C[특징 공학<br>g₂ 곡선 평탄화 또는 인코딩]
    C --> D[차원 축소<br>UMAP 임베딩]
    D --> E[클러스터링<br>HDBSCAN]
    E --> F[동역학적 핑거프린트 맵<br>각 클러스터 = 고유 상태]
```

### 1단계: 상관 함수 계산

```python
# 표준 다중 타우(multi-tau) 상관 알고리즘
# 각 q 빈에 대해 g₂(τ) 계산:
# g₂(q, τ) = <I(q,t) × I(q,t+τ)> / <I(q,t)>²
```

### 2단계: 특징 표현

**접근법 A: 직접 연결(Direct concatenation)**
```python
# 모든 q 값에서의 g₂ 곡선을 단일 특징 벡터로 연결
# feature = [g₂(q₁,τ₁), g₂(q₁,τ₂), ..., g₂(qN,τM)]
# 차원: N_q × N_tau
features = g2_array.reshape(n_measurements, -1)
```

**접근법 B: 오토인코더(Autoencoder) 인코딩**
```python
# 오토인코더를 학습하여 g₂ 곡선을 압축
# feature = encoder(g₂_curves)  → 컴팩트한 잠재 표현
```

### 3단계: UMAP 차원 축소(Dimensionality Reduction)

```python
import umap

reducer = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    metric='euclidean'
)
embedding = reducer.fit_transform(features)
```

UMAP은 지역 및 전역 구조를 모두 보존하여 유사한 동역학의 클러스터를 드러냅니다.

### 4단계: HDBSCAN 클러스터링

```python
import hdbscan

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,
    min_samples=5,
    cluster_selection_method='eom'
)
labels = clusterer.fit_predict(embedding)

# labels: -1 = 노이즈, 0,1,2,... = 클러스터 ID
# 각 클러스터는 고유한 동역학적 상태를 나타냄
```

### 5단계: 해석

```python
# 각 클러스터에 대해 대표 g₂ 곡선 계산
for cluster_id in range(max(labels) + 1):
    mask = labels == cluster_id
    mean_g2 = features[mask].mean(axis=0).reshape(n_q, n_tau)

    # 시각화: 이 동역학적 상태가 어떤 모습인가?
    # 알려진 동역학 모델과 비교
    # 상태 간 전이 식별 (시간적 진화)
```

## 핵심 혁신

### 모델 프리 분석(Model-Free Analysis)
- 이완 모델(지수 함수, 거듭제곱 법칙 등)에 대한 가정 없음
- 데이터 구조에서 직접 동역학적 상태를 발견
- 예상치 못한 또는 새로운 동역학적 거동을 식별 가능
- 모델이 존재하지 않는 비평형 시스템에 특히 유용

### 포괄적 q-의존성
- 전체 q-의존 g₂ 정보를 사용 (단일 q 피팅이 아닌)
- 단일 q 분석으로는 놓칠 수 있는 q-의존 동역학을 포착
- 핑거프린트가 완전한 동역학 정보를 인코딩

### 시간적 진화 추적
```
시간 → 클러스터 시퀀스: [A, A, A, B, B, B, C, C, B, B, A, A]

클러스터 간 전이는 동역학적 상(Phase) 변화를 나타냄
```

## 적용 예시

### 콜로이드 겔 노화(Colloidal Gel Aging)
- **관찰**: UMAP이 겔 노화 과정에서 3개의 뚜렷한 클러스터를 드러냄
- **해석**: 액체 → 겔 전이 → 노화 겔
- **통찰**: 모델 피팅 없이 전이 시간을 정확하게 식별

### 온도 의존 동역학
- 다양한 온도에서의 XPCS 측정을 매핑
- 클러스터가 동역학적 상(결정질, 액체, 유리)에 해당
- 비지도 분석에서 상 다이어그램(Phase Diagram)이 도출됨

### 방사선 손상 모니터링(Radiation Damage Monitoring)
- 동역학적 핑거프린트의 변화로 빔 손상 시작을 감지
- 자동 탐지: 핑거프린트가 크게 변할 때 플래그
- 적응적 선량 관리 가능

## 강점

1. **모델 프리**: 물리적 모델 가정이 필요 없음
2. **비지도**: 레이블이 지정된 학습 데이터가 필요 없음
3. **포괄적**: 전체 q-의존 동역학 정보를 사용
4. **민감성**: 표준 분석에서 놓치는 미세한 전이를 감지
5. **확장성**: 대규모 매개변수 연구를 자동으로 처리
6. **해석 가능성**: 클러스터 중심이 대표적인 동역학을 제공

## 한계

1. **사후 분석(Post-hoc)**: 현재 데이터 수집 후에 적용 (실시간이 아님)
2. **하이퍼파라미터**: UMAP과 HDBSCAN에 조정 가능한 매개변수가 있음
3. **특징 공학(Feature Engineering)**: 표현 방식의 선택이 결과에 영향
4. **물리적 해석**: 클러스터에 전문가의 해석이 필요
5. **검증**: 정답 레이블(Ground Truth) 없이 검증이 어려움

## APS BER 프로그램과의 관련성

### APS-U XPCS (12-ID-E)
- 업그레이드 후 XPCS가 대규모 데이터셋(수백만 프레임)을 생성
- 전통적 분석으로는 데이터 속도를 따라갈 수 없음
- AI-NERD가 동역학적 상태의 자동 분류를 가능하게 함
- 실시간 구현 시 자율 실험 조종이 가능

### 다른 모달리티로의 확장
- XPCS 이외에도 원리를 적용 가능:
  - 시간 분해 SAXS → 구조적 진화 핑거프린팅
  - 순차적 XANES 스펙트럼 → 화학적 변화 핑거프린팅
  - 시계열 XRF 맵 → 원소 재분배 핑거프린팅
