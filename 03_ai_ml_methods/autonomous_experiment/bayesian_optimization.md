# 방사광 실험을 위한 베이지안 최적화(Bayesian Optimization)

## 개요

베이지안 최적화(Bayesian Optimization, BO)는 각 평가가 비용이 많이 드는 (예: 빔 타임이 필요한) 실험 매개변수에 대한 표본 효율적(Sample-efficient) 최적화 전략입니다. 목적 함수의 확률적 대리 모델(Surrogate Model)을 구축하고 획득 함수(Acquisition Function)를 사용하여 다음에 어디를 샘플링할지 결정합니다.

## 왜 베이지안 최적화인가?

방사광 실험은 최적화 문제에 직면합니다:
- **비용이 높은 평가**: 각 측정에 수분에서 수시간 소요
- **제한된 예산**: 빔 타임이 부족함 (일반적으로 3-5일)
- **고차원**: 여러 매개변수가 상호작용 (에너지, 노출, 위치, 온도)
- **노이즈 존재**: 측정에 내재적 통계적 노이즈가 있음

BO는 최적 매개변수를 찾는 데 필요한 평가 횟수를 최소화하므로 이상적입니다.

## 방법

### 핵심 알고리즘

```
초기화: 몇 가지 무작위 매개변수 구성을 샘플링
예산 소진까지 반복:
    1. 모든 관측값에 대리 모델(GP)을 피팅
    2. 매개변수 공간에서 획득 함수 계산
    3. 다음 매개변수 선택 x* = argmax(acquisition)
    4. 목적 함수 f(x*) 평가 — 실험 수행
    5. (x*, f(x*))를 관측 집합에 추가
```

### 가우시안 프로세스 대리 모델(Gaussian Process Surrogate)

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern

# GP는 목적 함수를 확률적 함수로 모델링
# 평균: 임의의 지점에서 목적 함수의 기대값
# 분산: 불확실성 (관측이 적은 곳에서 높음)

kernel = Matern(nu=2.5, length_scale_bounds=(0.01, 10.0))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
gp.fit(X_observed, y_observed)

# 불확실성과 함께 새로운 지점에서 예측
mu, sigma = gp.predict(X_new, return_std=True)
```

### 획득 함수(Acquisition Functions)

| 함수 | 수식 | 전략 |
|----------|---------|----------|
| **기대 향상(Expected Improvement, EI)** | E[max(f(x) - f_best, 0)] | 탐색/활용 균형 |
| **상한 신뢰 구간(Upper Confidence Bound, UCB)** | µ(x) + κ·σ(x) | 조정 가능한 탐색 매개변수 |
| **향상 확률(Probability of Improvement, PI)** | P(f(x) > f_best + ξ) | 보수적 |
| **톰슨 샘플링(Thompson Sampling)** | GP 사후 분포에서 샘플링 | 무작위 탐색 |

## 방사광 과학에서의 응용

### 1. 노출 최적화

```
목적: SNR / 측정 시간 극대화
매개변수: [exposure_time, detector_distance, energy]
제약: Dose < max_allowed_dose

BO가 신호 품질과 속도 간의 최적 절충점을 찾음
```

### 2. 스캔 전략 최적화

```
목적: 재구성 품질 극대화 (SSIM 또는 PSNR)
매개변수: [n_projections, angular_range, resolution]
제약: 총 스캔 시간 < T_max

BO가 허용 가능한 품질에 필요한 최소 투영 수를 결정
```

### 3. 시료 환경 매개변수

```
목적: 특징 대비 또는 과학적 신호 극대화
매개변수: [temperature, humidity, flow_rate, pH]
제약: 시료 무결성

BO가 목표 현상을 드러내는 조건을 찾기 위해 매개변수 공간을 탐색
```

### 4. XANES를 위한 에너지 선택

```
목적: 종(Species) 구별 극대화
매개변수: [energy_1, energy_2, energy_3]
제약: 3개 에너지 포인트만 사용 (빠른 비율 매핑을 위해)

BO가 다중 에너지 화학종 분포 매핑(Speciation Mapping)을 위한 최적 에너지를 선택
```

## 구현 예제

```python
from botorch import fit_gpytorch_mll
from botorch.models import SingleTaskGP
from botorch.acquisition import ExpectedImprovement
from botorch.optim import optimize_acqf
import torch

# 매개변수 범위 정의
bounds = torch.tensor([
    [0.001, 0.1, 8.0],   # 하한: [exposure_s, step_um, energy_keV]
    [1.0, 10.0, 20.0]    # 상한
])

# 초기 무작위 샘플
X_init = torch.rand(5, 3) * (bounds[1] - bounds[0]) + bounds[0]
Y_init = torch.tensor([run_experiment(x) for x in X_init]).unsqueeze(-1)

# BO 루프
for iteration in range(20):
    # GP 피팅
    gp = SingleTaskGP(X_init, Y_init)
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(gp.likelihood, gp)
    fit_gpytorch_mll(mll)

    # 획득 함수
    EI = ExpectedImprovement(gp, best_f=Y_init.max())

    # 획득 함수 최적화
    candidate, acq_value = optimize_acqf(
        EI, bounds=bounds, q=1, num_restarts=10, raw_samples=512
    )

    # 선택된 매개변수로 실험 수행
    new_y = run_experiment(candidate.squeeze())

    # 데이터셋 업데이트
    X_init = torch.cat([X_init, candidate])
    Y_init = torch.cat([Y_init, new_y.unsqueeze(0).unsqueeze(-1)])

    print(f"반복 {iteration}: 최고값 = {Y_init.max():.4f}")
```

## 다목적 베이지안 최적화(Multi-Objective Bayesian Optimization)

종종 여러 경쟁 목표가 존재합니다:

```
목적 1: 이미지 품질 극대화 (해상도, SNR)
목적 2: 선량 최소화 (시료 보호)
목적 3: 시간 최소화 (처리량 극대화)

→ 파레토 최적(Pareto-optimal) 절충면
```

```python
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement

# 다목적 최적화를 위한 EHVI 획득 함수
# 파레토 프론트를 효율적으로 찾음
```

## 강점

1. **표본 효율적**: 10-50회 평가로 최적값을 찾음 (그리드 서치의 수백 회 대비)
2. **노이즈 처리**: GP가 측정 불확실성을 자연스럽게 모델링
3. **범용 목적 함수**: 블랙박스 최적화 — 그래디언트 불필요
4. **불확실성 인식**: 탐색-활용 균형
5. **다목적**: 경쟁하는 목표를 동시에 최적화 가능

## 한계

1. **확장성**: 표준 GP는 O(N³)으로 스케일링 — 약 1000개 관측으로 제한
2. **차원수**: 저차원에서 가장 잘 동작 (매개변수 20개 미만)
3. **이산 매개변수**: 이산 선택에 대한 확장이 필요
4. **GP 가정**: 정상성(Stationarity), 평활성이 항상 성립하지 않을 수 있음
5. **구현 복잡성**: 올바르게 설정하려면 ML 전문 지식이 필요
