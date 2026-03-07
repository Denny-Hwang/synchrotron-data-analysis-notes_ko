# 분광학을 위한 지식 주입 베이지안 최적화

**참고문헌**: Du et al., npj Computational Materials (2025)

## 개요

지식 주입 베이지안 최적화(Knowledge-Injected Bayesian Optimization, KI-BO)는 표준 BO를 확장하여
스펙트럼 구조에 대한 도메인 특이적 지식을 획득 함수에 통합합니다. XANES 분광학의 경우,
이 알고리즘은 흡수 에지와 프리에지 특징이 발생할 가능성이 높은 위치를 이해하여,
스펙트럼 정확도를 유지하면서 5배 빠른 데이터 수집을 가능하게 합니다.

## 표준 BO가 XANES에 부적합한 이유

표준 BO 획득 함수는 XANES 물리학에 무관합니다:

- **분산 기반**: 모든 곳에서 불확실성을 균등하게 줄이기 위해 균일하게 샘플링 —
  평탄한 프리에지/포스트에지 영역에서 예산을 낭비
- **UCB (Upper Confidence Bound)**: 스펙트럼 재구성이 아닌 최대화를 위해 설계됨 —
  고흡수 영역으로 편향
- **EI (Expected Improvement)**: 현재 최적값을 개선하려 함 — 모든 점이 중요한
  스펙트럼 매핑에는 부적절

## 지식 주입 획득 함수

```
α(E) = w₁ · |∂μ(E)/∂E| + w₂ · σ(E) + w₃ · P_edge(E)

구성 요소:
  |∂μ(E)/∂E|  = GP 사후 평균의 기울기 크기
                 → 흡수 에지 근처에서 높고, 평탄 영역에서 낮음
  σ(E)        = GP 사후 불확실성
                 → 데이터가 희소한 곳에서 높음
  P_edge(E)   = 에지 영역에 있을 사전 확률
                 → 원소별 에지 에너지에 대한 도메인 지식 인코딩

일반적인 가중치: w₁ = 0.5, w₂ = 0.3, w₃ = 0.2
```

### 기울기 인식 샘플링

```
프리에지 영역:      |∂μ/∂E| ≈ 0    → 소수의 샘플 필요
흡수 에지:          |∂μ/∂E| >> 0   → 많은 샘플 할당
화이트 라인 피크:    |∂μ/∂E| 가변   → 보통 수준의 샘플
포스트에지 (EXAFS):  |∂μ/∂E| ≈ 0   → 소수의 샘플 필요
```

이는 가장 중요한 곳에 측정 예산을 자연스럽게 집중시킵니다.

## 알고리즘

```
1. 시드: 5-10개의 넓게 간격을 둔 에너지 포인트 측정
2. 관측값에 GP 서로게이트 피팅: f(E) ~ GP(μ, K)
3. 에너지 범위에 대해 지식 주입 획득 함수 계산: α(E)
4. E* = argmax α(E) 선택
5. 모노크로메이터를 E*로 이동, I₀ 및 I_t 수집
6. μ(E*) = -ln(I_t / I₀) 계산
7. 새로운 (E*, μ(E*)) 관측값으로 GP 업데이트
8. 수렴 기준 충족 시 → 중단
   아닐 경우 → 2단계로 이동
9. 출력: GP 사후 평균을 재구성된 XANES 스펙트럼으로 출력
```

### 수렴 기준

```python
# 최대 획득 값이 임계값 이하로 떨어지거나
# N_max 측정 횟수에 도달하면 중단
if max(acquisition_values) < epsilon or n_measurements >= N_max:
    stop_and_interpolate()
```

## Bluesky와의 통합

```python
from bluesky import RunEngine
from bluesky.plans import scan
from ophyd import EpicsMotor, EpicsSignalRO

# 모노크로메이터 및 검출기
mono = EpicsMotor("XF:25IDC-OP:1{Mono}", name="mono_energy")
I0 = EpicsSignalRO("XF:25IDC-BI:1{IC:I0}", name="I0")
It = EpicsSignalRO("XF:25IDC-BI:1{IC:It}", name="It")

# 적응형 계획
def adaptive_xanes(element_edge, E_range, n_seed=8, n_max=50):
    """Bluesky용 지식 주입 BO XANES 계획."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    import numpy as np

    # 시드 측정
    E_seed = np.linspace(E_range[0], E_range[1], n_seed)
    observations = []

    for E in E_seed:
        yield from bps.mv(mono, E)
        ret = yield from bps.trigger_and_read([I0, It])
        mu = -np.log(ret[It.name]["value"] / ret[I0.name]["value"])
        observations.append((E, mu))

    # 적응형 루프
    for step in range(n_max - n_seed):
        X = np.array([o[0] for o in observations]).reshape(-1, 1)
        y = np.array([o[1] for o in observations])

        gp = GaussianProcessRegressor()
        gp.fit(X, y)

        # 지식 주입 획득 함수
        E_candidates = np.linspace(E_range[0], E_range[1], 500).reshape(-1, 1)
        mu_pred, sigma = gp.predict(E_candidates, return_std=True)
        gradient = np.abs(np.gradient(mu_pred.flatten()))
        acq = 0.5 * gradient + 0.3 * sigma + 0.2 * edge_prior(E_candidates, element_edge)

        E_next = E_candidates[np.argmax(acq)][0]
        yield from bps.mv(mono, E_next)
        ret = yield from bps.trigger_and_read([I0, It])
        mu = -np.log(ret[It.name]["value"] / ret[I0.name]["value"])
        observations.append((E_next, mu))

    return observations
```

## 성능

| 지표 | 표준 그리드 | 표준 BO | KI-BO |
|--------|--------------|-------------|-------|
| **필요 포인트 수** | 200-500 | 60-100 | 30-50 |
| **에지 오차 (eV)** | < 0.01 | 0.2-0.5 | < 0.1 |
| **화이트 라인 오차** | < 0.01 | 0.1-0.3 | < 0.03 |
| **RMSE** | 기준 | 0.02 | < 0.005 |
| **시간 절감** | — | 2-3배 | **5배** |

## 강점

1. **5배 속도 향상**: 5배 더 세밀한 시간 분해능으로 시간 분해 XANES를 가능하게 함
2. **물리학 기반**: 도메인 지식이 중요한 특징 근처의 샘플링 오류를 방지
3. **Bluesky 네이티브**: 기존 빔라인 인프라에 바로 적용 가능
4. **원소 무관 프레임워크**: 에지 사전 확률을 모든 원소에 대해 구성 가능
5. **정량적 정확도**: 에지 위치에 대해 0.1 eV 미만의 정확도 유지

## 한계

1. **단일 에지 집중**: 현재 구현은 한 번에 하나의 흡수 에지만 대상으로 함
2. **GP 스케일링**: GP 피팅에 O(N³), 단 N은 작음 (30-50 포인트)
3. **원소별 사전 확률**: 에지 사전 확률은 원소/에지 유형별로 구성이 필요
4. **EXAFS 미지원**: EXAFS 영역에는 k-공간 샘플링 전략이 필요
5. **빔 안정성 가정**: 적응형 시퀀스 동안 안정적인 빔 필요

## 다른 자율 방법과의 비교

| 방법 | 도메인 | 공간/스펙트럼 | 결정 유형 |
|--------|--------|-----------------|---------------|
| **KI-BO XANES** | 분광학 | 스펙트럼 (에너지) | 다음 에너지 포인트 |
| **AI-NERD** | XPCS | 시간적 | 다음 측정 시간 |
| **ROI-Finder** | XRF | 공간 (x, y) | 다음 스캔 영역 |
| **표준 BO** | 일반 | 모든 | 다음 매개변수 세트 |
