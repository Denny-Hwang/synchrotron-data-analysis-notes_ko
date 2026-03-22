# 스캔 줄무늬(Scan Stripe)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 쉬움(Easy) |

## 시각적 예시

```
 줄무늬가 있는 Fe 맵 (원시)            디스트라이핑 보정 후
 ┌────────────────────────────┐      ┌────────────────────────────┐
 │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │ ←dim │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │
 │▒▒▒▒▓▓▓████████▓▓▒▒░░░░░░░ │ ←hot │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │
 │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │ ←dim │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │
 │▒▒▒▒▓▓▓████████▓▓▒▒░░░░░░░ │ ←hot │ ░░░░▒▒▓▓████▓▓▒▒░░░░░░░░░ │
 └────────────────────────────┘      └────────────────────────────┘
 양방향 래스터 스캔에서의               행 정규화 후 균일한 배경
 교대하는 밝/어두운 행
```

## 설명

스캔 줄무늬는 래스터 스캔 방향에 정렬된 XRF 원소 맵의 수평 또는 수직 강도 밴드입니다. 교대하는 밝고 어두운 행으로 나타나 "베네치안 블라인드" 외관을 만들며, 실제 원소 분포와 무관한 체계적 아티팩트로 모든 원소에 동일하게 영향을 미칩니다.

## 근본 원인

여러 메커니즘이 스캔 줄무늬를 생성합니다. 양방향(뱀 형) 래스터 스캔에서 정방향과 역방향 스캔 방향 간의 약간의 오정렬이 교대하는 밝/어두운 행 쌍을 만듭니다. 스캔 중 빔 위치 드리프트로 다른 행이 약간 다른 위치를 샘플링합니다. 픽셀당 드웰 시간보다 빠르지만 전체 스캔 라인보다 느린 I0 변동이 행간 강도 변동을 생성합니다. 스테이지 엔코더 오류나 스틱-슬립 모션이 불균일한 픽셀 간격으로 나타납니다.

## 빠른 진단

```python
import numpy as np

row_means = np.mean(element_map.astype(float), axis=1)
row_variation = np.std(row_means) / np.mean(row_means)
diff = np.diff(row_means)
sign_changes = np.sum(np.diff(np.sign(diff)) != 0)
alternating_fraction = sign_changes / len(diff)
print(f"행 평균 CV: {row_variation:.3f}")
print(f"교대 패턴 점수: {alternating_fraction:.2f} (>0.6 = 줄무늬)")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 양방향 오프셋 아티팩트를 피하기 위해 단방향 래스터 스캔을 사용합니다.
- I0 정규화를 적용합니다(대부분의 플럭스 관련 줄무늬 제거).
- 스테이지 엔코더를 교정하고 스캔 전 균일한 픽셀 간격을 확인합니다.

### 보정 — 전통적 방법

```python
import numpy as np
from scipy import fft


def correct_row_normalization(element_map, scan_direction='horizontal'):
    """각 행(또는 열)이 동일한 평균 강도를 갖도록 정규화하여 스캔 줄무늬를 제거합니다."""
    img = element_map.astype(float).copy()
    if scan_direction == 'horizontal':
        row_means = np.mean(img, axis=1, keepdims=True)
        global_mean = np.mean(img)
        row_means[row_means == 0] = 1.0
        img = img / row_means * global_mean
    else:
        col_means = np.mean(img, axis=0, keepdims=True)
        global_mean = np.mean(img)
        col_means[col_means == 0] = 1.0
        img = img / col_means * global_mean
    return img


def correct_bidirectional_offset(element_map, shift_pixels=1):
    """양방향 래스터 스캔에서 정방향과 역방향 스캔 라인 간의 픽셀 오프셋을 수정합니다."""
    corrected = element_map.astype(float).copy()
    for i in range(1, corrected.shape[0], 2):
        corrected[i, :] = np.roll(corrected[i, :], shift_pixels)
    return corrected


def optimize_bidirectional_shift(element_map, max_shift=5):
    """행간 불연속을 최소화하여 최적의 픽셀 시프트를 자동으로 결정합니다."""
    best_shift = 0
    best_score = np.inf
    for shift in range(-max_shift, max_shift + 1):
        test = element_map.astype(float).copy()
        for i in range(1, test.shape[0], 2):
            test[i, :] = np.roll(test[i, :], shift)
        row_diff = np.sum(np.abs(np.diff(test, axis=0)))
        if row_diff < best_score:
            best_score = row_diff
            best_shift = shift
    return best_shift
```

## 보정하지 않을 경우의 영향

스캔 줄무늬는 미묘한 조성 경계를 가리고 층상 시료 구조로 잘못 해석될 수 있는 인공적 밴딩을 만들어 시각적 해석을 손상시킵니다. 정량적 분석은 다른 행의 픽셀 강도가 동일한 스케일이 아니기 때문에 영향을 받습니다. 세그멘테이션과 클러스터링 같은 후속 처리 단계가 조성이 아닌 줄무늬 위치에 따라 픽셀을 그룹화할 수 있습니다.

## 관련 자료

- 관련 아티팩트: [I0 정규화](i0_normalization.md) — 적절한 I0 보정이 대부분의 플럭스 관련 줄무늬를 제거
- 관련 아티팩트: [광자 계수 노이즈](photon_counting_noise.md) — 노이즈가 많은 맵에서 줄무늬 탐지가 더 어려움
- 관련 아티팩트: [프로브 흐림](probe_blurring.md) — 디스트라이핑이 디컨볼루션에 선행해야 함

## 핵심 요점

스캔 줄무늬는 여러 원인(양방향 오프셋, I0 드리프트, 스테이지 오류)이 있는 흔한 래스터 스캔 아티팩트입니다. 항상 행 및 열 평균에서 체계적 진동을 검사하고, 정량적 분석 전에 행 정규화 또는 푸리에 디스트라이핑을 적용하세요. 단방향 스캔과 적절한 I0 정규화를 사용하면 대부분의 줄무늬 아티팩트를 원천적으로 방지합니다.
