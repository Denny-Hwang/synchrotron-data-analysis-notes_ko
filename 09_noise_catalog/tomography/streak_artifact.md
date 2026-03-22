# 줄무늬 아티팩트(Streak Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

줄무늬 아티팩트의 시각적 예시는 외부 참고 자료를 참조하십시오. 금속 임플란트나 고밀도 물체 주변에서 밝은 줄무늬가 방사상으로 퍼지는 패턴이 전형적입니다.

## 설명

줄무늬 아티팩트(Streak Artifact)는 CT 재구성에서 고밀도 물체(금속, 뼈 등)로부터 방사상으로 퍼지는 밝은 줄무늬 패턴입니다. 이 아티팩트는 빔 경화(beam hardening), 광자 부족(photon starvation), 또는 고감쇠 물질을 통과할 때의 비선형 효과로 인해 발생합니다.

근본적인 원인은 고밀도 물체를 통과하는 X선의 투과율이 0에 가까워지면서, FBP(Filtered Back-Projection) 재구성의 로그 변환 과정에서 노이즈가 극도로 증폭되는 것입니다. 투과값이 0에 가까운 영역에서 $-\ln(I/I_0)$의 값은 급격히 커지고 불안정해져, 재구성 시 고밀도 물체를 잇는 방향으로 밝은 줄무늬가 나타납니다.

의료 CT에서는 "금속 아티팩트(Metal Artifact)"로도 불리며, 방사광 토모그래피에서는 고밀도 광물 입자, 금속 포함물, 또는 시료 홀더의 금속 부분 등에서 흔히 발생합니다.

## 근본 원인

1. **빔 경화(Beam Hardening):** 다색 X선이 물질을 통과하면서 저에너지 성분이 선택적으로 흡수되어 평균 에너지가 증가하는 현상. 단색 빔을 가정하는 재구성 알고리즘에서 줄무늬를 유발
2. **광자 부족(Photon Starvation):** 고감쇠 물체를 통과하면서 검출기에 도달하는 광자 수가 극도로 감소하여 포아송 노이즈가 지배적이 됨
3. **검출기 포화/언더플로우:** 투과율이 검출기의 동적 범위를 초과하여 측정값이 잘리거나(clipping) 0이 됨
4. **비선형 부분 볼륨 효과:** 고밀도 물체의 경계에서 복셀 내 밀도 변화가 급격하여 발생

## 빠른 진단

사이노그램에서 투과율이 0에 가까운 픽셀을 확인합니다:

```python
import numpy as np

def quick_streak_check(sinogram, transmission_threshold=0.01):
    """사이노그램에서 줄무늬 아티팩트 유발 가능성을 빠르게 진단합니다."""
    # 투과율 계산 (정규화된 사이노그램 가정)
    near_zero = np.sum(sinogram < transmission_threshold)
    total = sinogram.size
    fraction = near_zero / total

    print(f"Near-zero transmission pixels: {near_zero} ({fraction * 100:.2f}%)")
    if fraction > 0.01:
        print("WARNING: Significant photon starvation detected - streak artifacts likely")
    elif fraction > 0.001:
        print("CAUTION: Some photon starvation present - minor streaks possible")
    else:
        print("OK: Minimal photon starvation")

    return fraction
```

## 탐지 방법

### 시각적 지표

- **사이노그램:** 매우 어두운 영역(0에 가까운 투과율)이 특정 각도 범위에서 관찰됨
- **재구성 슬라이스:** 고밀도 물체 사이를 연결하는 방향으로 밝거나 어두운 줄무늬가 방사상으로 퍼짐
- **투과율 히스토그램:** 0에 가까운 값에 피크가 존재
- **각도별 프로파일:** 고밀도 물체가 겹치는 각도에서 프로파일 값이 급격히 변동

### 자동 탐지

```python
import numpy as np

def detect_streak_sources(sinogram, transmission_threshold=0.01):
    """
    줄무늬 아티팩트의 원인이 될 수 있는 영역을 사이노그램에서 탐지합니다.

    Parameters
    ----------
    sinogram : np.ndarray
        2D 사이노그램 배열 (angles x detector_columns),
        정규화된 투과율 값 (0~1 범위)
    transmission_threshold : float
        광자 부족으로 판단할 투과율 임계값 (기본값: 0.01)

    Returns
    -------
    dict
        탐지 결과를 담은 딕셔너리
    """
    # 투과율 히스토그램 분석
    near_zero_mask = sinogram < transmission_threshold
    near_zero_fraction = np.sum(near_zero_mask) / sinogram.size

    # 포화 열 탐지 (모든 각도에서 낮은 투과율을 보이는 열)
    col_min = np.min(sinogram, axis=0)
    saturated_cols = np.where(col_min < transmission_threshold)[0]

    # 각도별 영향 분석
    affected_per_angle = np.sum(near_zero_mask, axis=1)
    worst_angles = np.argsort(affected_per_angle)[-10:]

    # 심각도 분류
    if near_zero_fraction > 0.05:
        severity = "critical"
    elif near_zero_fraction > 0.01:
        severity = "major"
    elif near_zero_fraction > 0.001:
        severity = "minor"
    else:
        severity = "negligible"

    return {
        "near_zero_fraction": float(near_zero_fraction),
        "saturated_columns": saturated_cols,
        "worst_angles": worst_angles,
        "affected_pixels_per_angle": affected_per_angle,
        "severity": severity
    }
```

## 해결 및 완화

### 예방 (데이터 수집 전)

- 가능하면 시료에서 금속 부품을 제거합니다
- 높은 에너지의 X선을 사용하여 투과율을 높입니다
- 단색 빔(monochromatic beam)을 사용하여 빔 경화를 최소화합니다
- 노출 시간을 증가시켜 광자 통계를 개선합니다
- 고밀도 물체에 적합한 검출기 동적 범위를 확인합니다

### 보정 — 전통적 방법

```python
import numpy as np
from scipy import ndimage

# 방법 1: MAR(Metal Artifact Reduction) — 사이노그램 인페인팅
def metal_artifact_reduction(sinogram, threshold=0.01):
    """
    금속 아티팩트 저감: 투과율이 매우 낮은 영역을 보간합니다.
    """
    cleaned = sinogram.copy()
    metal_mask = sinogram < threshold

    # 행별로 금속 영역을 인접 값으로 보간
    for i in range(sinogram.shape[0]):
        row = cleaned[i]
        mask = metal_mask[i]
        if np.any(mask):
            good = ~mask
            if np.sum(good) > 2:
                x = np.arange(len(row))
                row[mask] = np.interp(x[mask], x[good], row[good])

    return cleaned

# 방법 2: 반복적 재구성 (SIRT/CGLS)
# FBP 대신 반복적 재구성을 사용하면 줄무늬 아티팩트가 크게 감소합니다
import tomopy

# SIRT (Simultaneous Iterative Reconstruction Technique)
recon_sirt = tomopy.recon(
    sinogram,
    theta,
    center=center,
    algorithm='sirt',
    num_iter=50      # 반복 횟수
)

# 방법 3: 빔 경화 보정 다항식
def beam_hardening_correction(sinogram, coeffs=[1.0, -0.1, 0.05]):
    """
    다항식 기반 빔 경화 보정.
    p = c0 * p_raw + c1 * p_raw^2 + c2 * p_raw^3
    """
    corrected = np.zeros_like(sinogram)
    for i, c in enumerate(coeffs):
        corrected += c * sinogram ** (i + 1)
    return corrected
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **딥러닝 인페인팅(DL Inpainting)** | 지도 학습 | 사이노그램에서 금속 영역을 마스킹한 후 학습된 네트워크로 인페인팅 |
| **LiMAR** | 지도 학습 | 학습 기반 반복적 금속 아티팩트 저감 |
| **조건부 GAN** | 적대적 학습 | 줄무늬가 있는 재구성에서 깨끗한 이미지를 생성하는 조건부 생성 모델 |

딥러닝 기반 인페인팅은 단순 선형 보간보다 금속 영역의 사이노그램 값을 더 정확하게 추정할 수 있으며, 특히 큰 금속 물체가 포함된 경우 효과적입니다.

## 미보정 시 영향

- **고밀도 물체 주변 특성 은폐:** 줄무늬가 관심 영역의 구조를 가려 관찰이 불가능해짐
- **세분화(Segmentation) 오류:** 줄무늬가 물질 경계와 혼동되어 정확한 세분화가 불가능
- **정량적 밀도 분석 왜곡:** 줄무늬 영역에서 재구성된 밀도 값이 실제와 크게 다름
- **3D 볼륨 분석 저해:** 연속 슬라이스에서 줄무늬가 다른 방향으로 나타나 3D 분석이 어려움

## 관련 자료

- [TomoPy를 활용한 탐색적 데이터 분석(EDA)](../../03_eda/tomo_eda.md)
- [TomoPy 역공학 분석](../../07_reverse_engineering/tomopy_recon.md)
- [링 아티팩트](ring_artifact.md)
- [징거](zinger.md)
- [빔 강도 저하](beam_intensity_drop.md)

## 핵심 요약

> **금속 아티팩트는 재구성 전에 사이노그램 수준에서 인페인팅을 통해 해결하십시오.** 고밀도 물체로 인한 광자 부족 영역을 사이노그램에서 탐지하고 보간하는 것이 FBP 재구성 후 줄무늬를 제거하는 것보다 훨씬 효과적이며, 반복적 재구성(SIRT/CGLS) 사용도 줄무늬 저감에 도움이 됩니다.
