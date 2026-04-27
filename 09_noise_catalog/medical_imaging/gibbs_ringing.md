# 깁스 링잉(Gibbs Ringing, 절단 링잉)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 의료 MRI / 방사광 코히어런트 영상 |
| **노이즈 유형** | 계산적(Computational) |
| **심각도** | 보통(Moderate) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |
| **기원 도메인** | 의료 영상(MRI) |

## 시각적 예시

![보정 전후 — 깁스 링잉](../images/gibbs_ringing_before_after.png)

> **이미지 출처:** 푸리에 절단을 적용한 합성 날카로운 가장자리 팬텀. 왼쪽: 유한 주파수 샘플링으로 인한 계단 경계의 진동. 오른쪽: Hamming 어포다이제이션 후. MIT 라이선스.

## 설명

깁스 링잉(절단 링잉 또는 스펙트럼 누출이라고도 함)은 날카로운 가장자리에 평행하게 진동하는 밝은/어두운 띠로 나타납니다. 이는 주파수 공간(MRI의 k-공간, 회절의 역격자 공간)의 유한 샘플링에서 비롯되며, 이는 이상적인 무한 스펙트럼에 직사각형 창 함수를 곱하는 것과 동등합니다. 결과로 생기는 sinc 함수 컨볼루션은 불연속점에서 특징적인 오버슈트(overshoot)와 링잉을 만듭니다.

**방사광 관련성:** 코히어런트 회절 영상(CDI), 유한한 검출기 범위를 갖는 프티코그래피(ptychography), 그리고 제한된 주파수 샘플링을 갖는 모든 푸리에 기반 재구성에 직접 적용됩니다.

## 근본 원인

- 주파수/역격자 공간의 유한 샘플링 → 푸리에 급수의 절단
- 실공간의 날카로운 가장자리는 정확한 표현을 위해 무한 주파수 성분이 필요
- 유한 주파수에서 절단 → sinc 함수와의 컨볼루션 → 링잉 진동
- 다음의 경우 더 심함: 작은 행렬 크기, 날카로운 물질 경계, 고대비 인터페이스

### 수학적 기원

```
f(x) = Σ_{n=-N}^{N} c_n · exp(2πinx)   (truncated at ±N)
     → Gibbs overshoot ≈ 9% of discontinuity height (regardless of N)
```

## 빠른 진단

```python
import numpy as np
from scipy.signal import find_peaks

def detect_gibbs_ringing(line_profile):
    """Detect Gibbs ringing from oscillations near edges."""
    # Compute gradient to find edges
    gradient = np.gradient(line_profile)
    edge_positions = np.where(np.abs(gradient) > np.std(gradient) * 3)[0]
    if len(edge_positions) == 0:
        print("No sharp edges found")
        return False
    # Check for oscillations near edges
    for edge in edge_positions:
        region = line_profile[max(0, edge-20):min(len(line_profile), edge+20)]
        peaks, _ = find_peaks(region)
        valleys, _ = find_peaks(-region)
        if len(peaks) >= 2 and len(valleys) >= 2:
            print(f"Gibbs ringing detected near position {edge}")
            return True
    return False
```

## 탐지 방법

### 시각적 지표

- 날카로운 가장자리에 평행하게 교차하는 밝은/어두운 띠
- 고대비 경계에 바로 인접한 오버슈트(밝은 선)
- 링잉 진폭이 가장자리 대비의 약 9%이며, 거리에 따라 감쇠
- 고대비 인터페이스(뼈/연조직, 공기/물질)에서 가장 잘 보임

### 자동 탐지

```python
import numpy as np

def gibbs_overshoot_measurement(line_profile, edge_idx, side='right'):
    """Measure Gibbs overshoot percentage at a known edge."""
    if side == 'right':
        region = line_profile[edge_idx:edge_idx + 30]
    else:
        region = line_profile[max(0, edge_idx - 30):edge_idx]
    overshoot = np.max(region) - np.mean(region[10:])
    step_height = abs(line_profile[edge_idx + 5] - line_profile[edge_idx - 5])
    overshoot_pct = overshoot / step_height * 100
    return overshoot_pct  # Theoretical max ~8.95%
```

## 보정 방법

### 전통적 접근법

1. **어포다이제이션(Apodization) / 윈도윙:** 역 FFT 전에 k-공간 데이터에 Hamming, Hanning, 또는 Tukey 창 적용
2. **제로 패딩 보간:** 행렬 크기 증가 (외형적 개선만, 새로운 정보는 없음)
3. **Gegenbauer 재구성:** 깁스 오버슈트를 회피하는 다항식 기반 방법
4. **Total Variation 필터링:** 재구성 후 TV 디노이징을 통해 진동 억제

```python
import numpy as np

def apply_hamming_apodization(kspace_data):
    """Apply Hamming window to suppress Gibbs ringing."""
    ny, nx = kspace_data.shape
    wy = np.hamming(ny)
    wx = np.hamming(nx)
    window = np.outer(wy, wx)
    return kspace_data * window
```

### AI/ML 접근법

- **HDNR (2018):** MRI를 위한 CNN 기반 깁스 링잉 제거 (Muckley et al.)
- **서브복셀 정확도 네트워크:** 디링잉을 초해상도(super-resolution) 과제로 학습

## 주요 참고문헌

- **Gibbs (1899)** — 현상에 대한 원조 수학적 기술
- **Archibald & Gelb (2002)** — "Reducing the Gibbs phenomenon" — 종합적 방법 리뷰
- **Kellner et al. (2016)** — "Gibbs-ringing artifact removal based on local subvoxel-shifts" — 널리 쓰이는 MRI 방법
- **Block et al. (2008)** — 압축 센싱 MRI (희소성을 통해 깁스를 암묵적으로 처리)

## 방사광 데이터와의 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 코히어런트 회절 영상(CDI) | 유한 검출기 → 푸리에 절단 → 링잉 |
| 프티코그래피 재구성 | 높은 q에서 제한된 역격자 공간 샘플링 |
| 위상 복원(Paganin) | 날카로운 위상 경계가 재구성에서 링잉 생성 |
| EXAFS 푸리에 변환 | 유한 k-범위가 R-공간에 잔물결 유발 |
| 결정학(푸리에 맵) | 원자 주변의 급수 종결 잔물결 |

## 관련 자료

- [Partial coherence](../ptychography/partial_coherence.md) — 관련된 푸리에 공간 한계
- [Sparse-angle artifact](../tomography/sparse_angle_artifact.md) — 각도 영역의 불완전 샘플링
- [Statistical noise (EXAFS)](../spectroscopy/statistical_noise_exafs.md) — 분광학에서의 k-공간 절단
