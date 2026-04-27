# 위상 래핑 아티팩트(Phase Wrapping Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 위상 대비 이미징 / CDI / 간섭계 |
| **노이즈 유형** | 계산적(Computational) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 방사광 위상 대비 이미징(ESRF, Diamond, SLS) |

## 시각적 예시

![보정 전후 — 위상 래핑](../images/phase_wrapping_before_after.png)

> **이미지 출처:** 범위가 [-π, π]를 초과하는 합성 위상 맵. 왼쪽: 2π 불연속을 포함한 래핑된 위상. 오른쪽: 품질 기반 위상 언래핑 후 진정한 연속 위상이 복원됨. MIT 라이선스.

## 설명

위상 래핑(Phase wrapping)은 복원된 위상이 주값 범위 [-π, π]를 초과할 때 발생하며, 위상 맵에서 갑작스러운 2π 불연속을 야기합니다. 이러한 인위적인 "점프"는 거짓 경계를 만들고, 정량적 위상 측정을 손상시키며, 분할(segmentation) 알고리즘을 오도할 수 있습니다. 이는 신호 처리에서의 에일리어싱 문제와 유사하게, 모든 위상 복원 방법에 내재된 근본적 모호성입니다.

**다중 시설 관련성:** 위상 대비 이미징(ESRF ID19, Diamond I13, SLS TOMCAT), 격자 간섭계, ptychography, 홀로그래픽 방법을 수행하는 모든 방사광 시설에서 발생합니다.

## 근본 원인

- 위상은 본질적으로 주기적: φ와 φ + 2πn은 동일한 측정값을 산출
- 위상 복원 알고리즘은 [-π, π] 범위로 래핑된 위상을 반환
- 두꺼운 또는 밀도가 높은 시료의 진정한 위상은 π를 초과 가능 → 래핑 발생
- 큰 위상 기울기(날카로운 밀도 경계) → 위상 언더샘플링 → 래핑
- 간섭계: 프린지 분석은 본질적으로 래핑된 위상 산출

### 수학적 기술

```
φ_wrapped(x) = φ_true(x) mod 2π - π
When φ_true > π: discontinuous jump of -2π appears
```

## 빠른 진단

```python
import numpy as np

def detect_phase_wraps(phase_map, threshold=5.0):
    """Detect phase wrapping by finding large phase jumps."""
    dy = np.diff(phase_map, axis=0)
    dx = np.diff(phase_map, axis=1)
    # Phase wraps cause jumps near ±2π
    wrap_y = np.abs(dy) > threshold
    wrap_x = np.abs(dx) > threshold
    n_wraps = wrap_y.sum() + wrap_x.sum()
    print(f"Phase wraps detected: {n_wraps}")
    print(f"Wrap fraction: {n_wraps / phase_map.size:.2%}")
    # Create wrap location map
    wrap_map = np.zeros_like(phase_map, dtype=bool)
    wrap_map[:-1, :] |= wrap_y
    wrap_map[:, :-1] |= wrap_x
    return wrap_map
```

## 탐지 방법

### 시각적 지표

- 부드러운 위상 맵 내 날카롭고 불연속적인 "절벽(cliff)" 라인
- 위상 값이 +π에서 -π(또는 그 반대)로 갑자기 점프
- 밀도가 높거나 두꺼운 경계에서의 비정상 위상의 "줄무늬"
- 위상 값 히스토그램이 ±π 경계에 쌓임

### 자동 탐지

```python
import numpy as np

def phase_gradient_reliability(phase_map):
    """Compute reliability map for phase unwrapping (Herraez et al.)."""
    dy = np.diff(phase_map, axis=0, prepend=phase_map[:1, :])
    dx = np.diff(phase_map, axis=1, prepend=phase_map[:, :1])
    # Wrap gradients to [-π, π]
    dy = np.angle(np.exp(1j * dy))
    dx = np.angle(np.exp(1j * dx))
    # Second differences → reliability (lower = more reliable)
    dyy = np.diff(dy, axis=0, prepend=dy[:1, :])
    dxx = np.diff(dx, axis=1, prepend=dx[:, :1])
    dxy = np.diff(dy, axis=1, prepend=dy[:, :1])
    reliability = np.sqrt(dyy**2 + dxx**2 + dxy**2)
    return reliability
```

## 보정 방법

### 전통적 접근

1. **경로 추종 언래핑:** Goldstein(branch-cut), Flynn(minimum discontinuity)
2. **품질 기반 언래핑:** 가장 신뢰할 수 있는 픽셀부터 언래핑(Herráez et al., 2002)
3. **최소 자승 언래핑:** ∇²(φ_unwrapped - φ_wrapped)를 최소화 — 전역 방법
4. **다중 거리 위상 복원:** 여러 시료-검출기 거리로 모호성 감소
5. **이중 에너지 위상 복원:** 두 에너지를 사용하여 래핑 해결

```python
def quality_guided_unwrap_2d(wrapped_phase):
    """Simple quality-guided 2D phase unwrapping."""
    from skimage.restoration import unwrap_phase
    # scikit-image implements quality-guided unwrapping
    unwrapped = unwrap_phase(wrapped_phase)
    return unwrapped
```

### AI/ML 접근

- **PhaseNet (2019):** 딥러닝 위상 언래핑 (Wang et al.)
- **DeepPhaseUnwrap:** 래핑된 입력으로부터 언래핑된 위상을 예측하는 U-Net
- **물리 기반 언래핑:** 위상 일관성 손실을 사용하는 신경망

### 소프트웨어 도구

- **scikit-image** — `skimage.restoration.unwrap_phase` (품질 기반)
- **SNAPHU** — 통계 비용 기반 위상 언래핑(원래 InSAR용)
- **PyPhase** — X선 이미징용 위상 복원 및 언래핑

## 주요 참고문헌

- **Goldstein et al. (1988)** — "Satellite radar interferometry: two-dimensional phase unwrapping"
- **Herráez et al. (2002)** — "Fast two-dimensional phase-unwrapping algorithm based on sorting by reliability"
- **Ghiglia & Pritt (1998)** — "Two-Dimensional Phase Unwrapping: Theory, Algorithms, and Software" — 정통 교과서
- **Paganin et al. (2002)** — "Simultaneous phase and amplitude extraction from a single defocused image"

## 시설별 벤치마크

| 시설 | 빔라인 | 위상 방법 |
|------|--------|----------|
| ESRF | ID19 | 전파 기반 위상 대비 + Paganin 복원 |
| Diamond | I13 | 인라인 위상 대비 + 다중 거리 복원 |
| SLS TOMCAT | X02DA | 단일 거리 Paganin + 격자 간섭계 |
| SPring-8 | BL20B2 | Talbot-Lau 격자 간섭계 |
| APS | 32-ID | 전파 위상 대비, Zernike 위상 대비 |

## 실제 보정 전후 예시

다음 출판된 자료들은 실제 실험적 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림 | 설명 | 라이선스 |
|------|------|------|------|---------|
| [scikit-image unwrap_phase](https://scikit-image.org/docs/stable/api/skimage.restoration.html) | 소프트웨어 문서 | API 예제 | 래핑된 위상 맵 vs 언래핑된 위상 맵의 예시를 보여주는 위상 언래핑 함수 | BSD-3 |

> **권장 참고자료**: [scikit-image — unwrap_phase (skimage.restoration)](https://scikit-image.org/docs/stable/api/skimage.restoration.html)

## 관련 자료

- [위치 오류](../ptychography/position_error.md) — Ptychography 재구성에서의 위상 오류
- [Gibbs ringing](../medical_imaging/gibbs_ringing.md) — Fourier 관련 재구성 아티팩트
- [부분 결맞음](../ptychography/partial_coherence.md) — 결맞음이 위상 복원 품질에 영향
