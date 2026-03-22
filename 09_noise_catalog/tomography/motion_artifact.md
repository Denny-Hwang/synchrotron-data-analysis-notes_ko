# 모션 아티팩트(Motion Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

```
  깨끗한 재구성                   모션 아티팩트 있음
  ┌─────────────────┐        ┌─────────────────┐
  │                 │        │                 │
  │    ┌───────┐   │        │    ┌───────┐   │
  │    │       │   │        │   ┌┤  ___  ├┐  │
  │    │  ○  ○ │   │        │   │○ ○ ○  ○│   │
  │    │       │   │        │    │  __   │   │
  │    │  ───  │   │        │    │ ─── ──│   │
  │    │       │   │        │    │    __ │   │
  │    └───────┘   │        │    └──────┘│   │
  │                 │        │         ───┘   │
  └─────────────────┘        └─────────────────┘

  흐림, 고스팅, 이중 엣지가 시료 이동을 나타냅니다.
```

## 설명

모션 아티팩트는 토모그래피 스캔 중 시료가 움직여서 발생하는 재구성 CT 슬라이스의 흐림, 고스팅 또는 이중 엣지로 나타납니다. 아티팩트의 심각도는 움직임의 크기와 성격에 따라 달라집니다 — 병진 드리프트는 방향성 흐림을, 갑작스러운 점프는 고스트 복사본을, 연속적인 변형은 불일치하는 경계를 만듭니다.

## 근본 원인

토모그래피 재구성은 시료가 스캔 전체에 걸쳐 완벽하게 정지해 있다고 가정합니다. 이 가정으로부터의 모든 이탈 — 열팽창/수축, 회전 스테이지의 기계적 진동, 연질 시료의 중력 처짐, 환경 부하(가열, 압축) 하의 시료 변형, 회전축 드리프트 등 — 은 다른 시간에 촬영된 투영 간의 불일치를 유발합니다. 각 투영은 약간 다른 물체 구성을 기록하며, 정적 물체를 가정하는 재구성 알고리즘은 다른 상태들의 흐릿하거나 고스팅된 절충안을 생성합니다.

## 빠른 진단

```python
import numpy as np

# 첫 번째와 마지막 (0°와 360°) 투영을 비교하여 시료 이동 감지
proj_first = projections[0].astype(float)
proj_last = projections[-1].astype(float)
nrmse = np.sqrt(np.mean((proj_first - proj_last)**2)) / (np.max(proj_first) - np.min(proj_first))
print(f"0°와 360° 투영 간 NRMSE: {nrmse:.4f}")
print(f"모션 가능성: {nrmse > 0.02}")
```

## 탐지 방법

### 자동 탐지

```python
import numpy as np
from scipy import ndimage


def detect_motion_artifacts(projections, angular_step_deg=None):
    """
    투영 간 일관성을 분석하여 토모그래피 스캔 중 시료 이동을 탐지합니다.
    """
    num_proj = projections.shape[0]
    com_x = np.zeros(num_proj)
    com_y = np.zeros(num_proj)

    for i in range(num_proj):
        proj = projections[i].astype(np.float64)
        total = np.sum(proj)
        if total > 0:
            yy, xx = np.mgrid[:proj.shape[0], :proj.shape[1]]
            com_x[i] = np.sum(xx * proj) / total
            com_y[i] = np.sum(yy * proj) / total

    from numpy.polynomial import polynomial as P
    t = np.arange(num_proj)
    coeff_x = P.polyfit(t, com_x, deg=2)
    coeff_y = P.polyfit(t, com_y, deg=2)
    trend_x = P.polyval(t, coeff_x)
    trend_y = P.polyval(t, coeff_y)
    residual_x = com_x - trend_x
    residual_y = com_y - trend_y

    drift = np.sqrt(residual_x**2 + residual_y**2)
    max_drift = np.max(drift)

    diff_drift = np.diff(drift)
    if max_drift < 0.5:
        motion_type = "none"
    elif np.max(np.abs(diff_drift)) > 3 * np.std(diff_drift):
        motion_type = "sudden_jump"
    elif np.std(diff_drift) > 0.3 * np.mean(np.abs(diff_drift)):
        motion_type = "vibration"
    else:
        motion_type = "gradual_drift"

    return {
        "drift_curve": drift,
        "max_drift_pixels": float(max_drift),
        "has_motion": max_drift > 0.5,
        "motion_type": motion_type,
    }
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 드리프트 시간을 최소화하기 위해 빠른 스캔 프로토콜(플라이 스캔, 연속 회전)을 사용합니다.
- 적절한 접착제나 클램핑으로 안정적인 시료 장착을 보장합니다.
- 스캔 전 열적 평형을 허용합니다.
- 진동 격리된 회전 스테이지를 사용합니다.
- 실시간 드리프트 모니터링을 위해 기준 투영(예: 0°를 주기적으로 반복)을 수집합니다.

### 보정 — 전통적 방법

수집 후 모션 보정은 재구성 전에 투영을 공통 기준 프레임에 재정합하는 것을 포함합니다.

```python
import numpy as np
from scipy.ndimage import shift
from skimage.registration import phase_cross_correlation


def correct_motion_projections(projections, reference_idx=0):
    """위상 교차 상관을 사용하여 모든 투영을 기준에 정렬하여 병진 이동을 보정합니다."""
    corrected = projections.copy().astype(np.float64)
    reference = projections[reference_idx].astype(np.float64)
    shifts_detected = np.zeros((projections.shape[0], 2))

    for i in range(projections.shape[0]):
        if i == reference_idx:
            continue
        current = projections[i].astype(np.float64)
        detected_shift, error, _ = phase_cross_correlation(
            reference, current, upsample_factor=10
        )
        shifts_detected[i] = detected_shift
        corrected[i] = shift(current, -detected_shift, order=3)

    return corrected, shifts_detected
```

### 보정 — AI/ML 방법

암시적 신경 표현(INR)이 모션 보상 토모그래피 재구성을 위한 강력한 도구로 부상했습니다. 재구성 볼륨을 신경망(좌표 기반 MLP 또는 해시 그리드 인코딩)으로 매개변수화된 연속 함수로 표현함으로써, INR은 볼륨과 투영별 모션 매개변수를 동시에 최적화할 수 있습니다. 이 접근법은 강체 및 비강체 모션 모두를 처리하며, 명시적인 모션 측정이나 기준 마커가 필요하지 않습니다.

## 보정하지 않을 경우의 영향

모션 아티팩트는 모션 진폭에 비례하는 공간 해상도 손실을 유발합니다. 이중 엣지는 잘못된 치수 측정을 만들고, 세그멘테이션 알고리즘은 부정확한 경계를 생성하며, 정량적 밀도 측정은 다른 물체 구성의 평균화로 인해 손상됩니다.

## 관련 자료

- [INR 동적 재구성](../../03_ai_ml_methods/reconstruction/inr_dynamic.md) — 모션 보상 CT를 위한 암시적 신경 표현
- 관련 아티팩트: [회전 중심 오류](rotation_center_error.md) — 모션 아티팩트와 유사하거나 복합될 수 있음
- 관련 아티팩트: [희소 각도 아티팩트](sparse_angle_artifact.md) — 모션 줄이기 위한 빠른 스캔이 각도를 과소 샘플링할 수 있음

## 핵심 요점

모션 아티팩트는 시료가 수집 중 이동하여 표준 재구성의 정적 물체 가정을 위반할 때 발생합니다. 빠른 스캔과 안정적인 장착을 통한 예방이 최선이며, 모션이 불가피한 경우 투영 재정합 또는 INR 기반 공동 재구성-정렬로 이미지 품질을 복원할 수 있습니다.
