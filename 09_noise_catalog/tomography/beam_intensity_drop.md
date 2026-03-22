# 빔 강도 저하(Beam Intensity Drop)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

```
  사이노그램 뷰                        I0 모니터 추적 (합성)
  ┌────────────────────────┐      ┌────────────────────────┐
  │████████████████████████│      │────────────────────────│
  │████████████████████████│      │────────────────────────│
  │████████████████████████│      │────────────────────────│
  │░░░░░░░░░░░░░░░░░░░░░░░│ ←    │         ╲              │ ← 빔 저하
  │░░░░░░░░░░░░░░░░░░░░░░░│      │          ╲_____        │
  │████████████████████████│      │                ╱───────│ ← 회복
  │████████████████████████│      │────────────────────────│
  │████████████████████████│      │────────────────────────│
  └────────────────────────┘      └────────────────────────┘

  빔 저하 이벤트에서의 수평            갑작스러운 I0 저하 후
  밝은/어두운 밴드                     회복 (빔 덤프/탑업)
```

## 설명

빔 강도 저하는 사이노그램에서 비정상적인 빔 조건 동안 획득된 투영 그룹에 해당하는 수평 밝거나 어두운 밴드로 나타납니다. 재구성에서는 특정 반경의 링형 아티팩트나 인접 슬라이스 간의 갑작스러운 강도 변화로 나타나며, 영향받은 투영은 강도 감소, 대비 변화 또는 완전한 신호 손실을 보입니다.

## 근본 원인

여러 운영 이벤트가 갑작스러운 빔 전류 손실을 유발할 수 있습니다: 빔 덤프(저장된 빔의 완전한 손실), 탑업 주입 실패(예정된 주입으로 빔 전류가 완전히 복원되지 않음), 셔터 오작동(데이터 수집 중 빔이 차단되거나 부분적으로 차단됨), 빔 위치 피드백 진동, 또는 삽입 장치(언듈레이터/위글러) 변경 등이 있습니다. 저장 링 불안정성, 진공 이벤트, RF 시스템 장애도 원인이 됩니다. 표준 플랫필드 보정만으로는 이러한 과도 이벤트를 완전히 처리할 수 없습니다.

## 빠른 진단

```python
import numpy as np

# 투영당 총 강도를 I0 대리 변수로 모니터링
proj_intensity = np.mean(projections, axis=(1, 2))
median_intensity = np.median(proj_intensity)
# 유의미한 강도 편차가 있는 투영 표시
drop_mask = proj_intensity < 0.9 * median_intensity
print(f"10% 이상 강도 저하 투영 수: {np.sum(drop_mask)}")
print(f"저하 인덱스: {np.where(drop_mask)[0]}")
```

## 탐지 방법

### 시각적 지표

- 사이노그램 전체 폭에 걸친 수평 밴드(밝거나 어두운)
- 투영을 순차적으로 검토할 때 보이는 갑작스러운 강도 변화
- I0 모니터 데이터가 있는 경우 빔 전류 추적에서 명확한 하락 또는 급등
- 재구성된 볼륨에서 링형 밴드 또는 강도 불연속

### 자동 탐지

```python
import numpy as np


def detect_beam_intensity_drops(projections, i0_monitor=None,
                                 drop_threshold=0.9, spike_threshold=1.1):
    """
    투영 데이터 또는 I0 모니터에서 빔 강도 저하 이벤트를 탐지합니다.

    Parameters
    ----------
    projections : np.ndarray
        3D 투영 스택 (num_proj, height, width).
    i0_monitor : np.ndarray or None
        투영당 I0 모니터 판독값의 1D 배열.
    drop_threshold : float
        저하로 표시할 중앙값 대비 비율.
    spike_threshold : float
        급등으로 표시할 중앙값 대비 비율.

    Returns
    -------
    dict with keys:
        'intensity_curve' : np.ndarray — 투영당 강도
        'drop_indices' : list of int — 저하가 있는 투영
        'spike_indices' : list of int — 급등이 있는 투영
        'has_beam_issues' : bool
        'affected_fraction' : float
    """
    if i0_monitor is not None:
        intensity = i0_monitor.astype(np.float64)
    else:
        intensity = np.mean(projections.astype(np.float64), axis=(1, 2))

    median_i = np.median(intensity)

    drop_indices = np.where(intensity < drop_threshold * median_i)[0].tolist()
    spike_indices = np.where(intensity > spike_threshold * median_i)[0].tolist()

    affected = len(drop_indices) + len(spike_indices)
    total = len(intensity)

    return {
        "intensity_curve": intensity,
        "drop_indices": drop_indices,
        "spike_indices": spike_indices,
        "has_beam_issues": affected > 0,
        "affected_fraction": affected / total,
    }
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 탑업이 연속적이지 않은 경우 주입 시간대를 피하고 안정적인 빔 기간에 스캔을 예약합니다.
- 투영과 동기화하여 기록되는 빔 전류 모니터(I0 이온 챔버)를 사용합니다.
- 빔 덤프 중 수집을 일시 중지하고 복구 후 재개하도록 스캔 제어 시스템을 구성합니다.
- 거의 일정한 빔 전류를 유지하기 위해 탑업 저장 링 모드를 사용합니다.
- 스캔 중단을 트리거하는 자동 빔 전류 임계값을 설정합니다.

### 보정 — 전통적 방법

투영별 I0 정규화로 강도 변동을 제거합니다. 심하게 영향받은 투영은 제거하고 누락된 각도를 보간 또는 반복 재구성으로 처리할 수 있습니다.

```python
import numpy as np


def correct_beam_intensity(projections, i0_monitor=None, remove_bad=True,
                            drop_threshold=0.8):
    """
    I0 모니터 데이터 또는 추정된 투영별 강도를 사용하여
    빔 강도 변동을 보정합니다.
    """
    if i0_monitor is not None:
        i0 = i0_monitor.astype(np.float64)
    else:
        margin = 20
        left_margin = np.mean(projections[:, :, :margin].astype(np.float64),
                              axis=(1, 2))
        right_margin = np.mean(projections[:, :, -margin:].astype(np.float64),
                               axis=(1, 2))
        i0 = 0.5 * (left_margin + right_margin)

    median_i0 = np.median(i0)

    corrected = np.zeros_like(projections, dtype=np.float64)
    for i in range(projections.shape[0]):
        if i0[i] > 0:
            corrected[i] = projections[i].astype(np.float64) * (median_i0 / i0[i])
        else:
            corrected[i] = projections[i].astype(np.float64)

    valid_mask = i0 > drop_threshold * median_i0

    if remove_bad and not np.all(valid_mask):
        bad_indices = np.where(~valid_mask)[0]
        print(f"심하게 영향받은 {len(bad_indices)}개 투영 제거")

        for idx in bad_indices:
            left = idx - 1
            right = idx + 1
            while left >= 0 and not valid_mask[left]:
                left -= 1
            while right < len(valid_mask) and not valid_mask[right]:
                right += 1

            if left >= 0 and right < len(valid_mask):
                weight = (idx - left) / (right - left)
                corrected[idx] = ((1 - weight) * corrected[left] +
                                  weight * corrected[right])
                valid_mask[idx] = True
            elif left >= 0:
                corrected[idx] = corrected[left]
                valid_mask[idx] = True
            elif right < len(valid_mask):
                corrected[idx] = corrected[right]
                valid_mask[idx] = True

    return corrected, valid_mask
```

### 보정 — AI/ML 방법

빔 강도 저하 보정에 특화된 확립된 AI/ML 방법은 없습니다. 이 아티팩트는 I0 정규화와 투영 보간으로 잘 처리됩니다. 다른 아티팩트(예: 금속 아티팩트 저감)를 위해 개발된 딥러닝 사이노그램 인페인팅 방법이 이론적으로 손상된 사이노그램 행을 채우는 데 적용될 수 있지만, 전통적인 I0 보정의 효과가 충분하므로 거의 필요하지 않습니다.

## 보정하지 않을 경우의 영향

보정되지 않은 빔 강도 저하는 재구성에 잘못된 밀도 변동을 도입합니다. 빔 저하 중 획득된 투영은 SNR이 감소하고 대비가 변경되어 재구성된 볼륨에서 링형 밴드나 강도 점프를 생성합니다. 정량적 감쇠값이 신뢰할 수 없게 되어 물질 식별이 어려워집니다. 완전한 빔 손실은 누락 데이터를 생성하고 제한 각도 토모그래피와 유사한 스트릭 아티팩트를 만듭니다.

## 관련 자료

- [토모그래피 EDA 노트북](../../06_data_structures/eda/tomo_eda.md) — 빔 강도 모니터링 및 투영 품질 검사
- 관련 아티팩트: [플랫필드 문제](flatfield_issues.md) — 플랫필드가 부분적으로 처리하는 빔 드리프트
- 관련 아티팩트: [링 아티팩트](ring_artifact.md) — 강도 밴드가 사이노그램에서 링 소스로 위장할 수 있음

## 핵심 요점

항상 I0 빔 모니터를 투영과 동기화하여 기록하고, 투영별 강도 정규화를 표준 전처리 단계로 적용하세요. 재구성 전에 I0 추적을 검사하여 빔 덤프나 주입 실패 중 획득된 투영을 표시하고, 보정하거나 제거하여 재구성 아티팩트를 방지해야 합니다.
