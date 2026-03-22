# 데드/핫 픽셀(Dead/Hot Pixel)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |

## 시각적 예시

![데드/핫 픽셀 보정 전후 비교](../images/dead_hot_pixel_before_after.png)

*합성 데이터(Synthetic). 왼쪽: 데드 픽셀(어두운 점)과 핫 픽셀(밝은 점)이 포함된 원소 맵. 오른쪽: 메디안 필터 보정 후.*

## 설명

검출기 픽셀 중 영구적으로 응답하지 않는 픽셀(데드 = 0)이나 포화 상태인 픽셀(핫 = 최대값)을 말합니다. 모든 원소 맵에서 고정된 위치에 고립된 어두운 점 또는 밝은 점으로 나타납니다.

데드 픽셀은 항상 0 또는 매우 낮은 카운트를 출력하며, 핫 픽셀은 입사 신호에 관계없이 비정상적으로 높은 카운트를 출력합니다. 이러한 픽셀은 모든 원소 채널에서 동일한 위치에 나타나므로 시료의 실제 특징과 구별할 수 있습니다.

## 근본 원인

1. **제조 결함** — 검출기 제작 과정에서 발생하는 픽셀 수준의 결함
2. **방사선 손상** — 장기간 X선 노출에 의한 검출기 소자의 누적 손상
3. **판독 채널 고장** — 특정 픽셀에 연결된 전자 회로의 물리적 손상 또는 접촉 불량
4. **열화(Aging)** — 검출기 소자의 시간에 따른 성능 저하

## 빠른 진단

Z-점수(Z-score) 이상치 맵과 이웃 픽셀 비교를 통해 빠르게 진단할 수 있습니다.

```python
import numpy as np

def quick_dead_hot_check(xrf_map, z_threshold=5.0):
    """
    XRF 맵에서 데드/핫 픽셀을 빠르게 탐지합니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D XRF elemental map (counts).
    z_threshold : float
        Z-score threshold for outlier detection.

    Returns
    -------
    dict with dead pixel count, hot pixel count, and outlier positions.
    """
    mean_val = np.mean(xrf_map)
    std_val = np.std(xrf_map)

    if std_val == 0:
        print("Warning: zero variance in map")
        return {"dead": 0, "hot": 0}

    z_scores = (xrf_map - mean_val) / std_val

    dead_mask = xrf_map == 0
    hot_mask = z_scores > z_threshold

    n_dead = np.sum(dead_mask)
    n_hot = np.sum(hot_mask)

    print(f"Dead pixels (value=0): {n_dead}")
    print(f"Hot pixels (z>{z_threshold}): {n_hot}")
    print(f"Total outliers: {n_dead + n_hot} / {xrf_map.size} "
          f"({(n_dead + n_hot) / xrf_map.size:.4%})")

    return {
        "dead_count": n_dead,
        "hot_count": n_hot,
        "dead_mask": dead_mask,
        "hot_mask": hot_mask,
    }
```

## 탐지 방법

### 시각적 지표

- 모든 원소 맵에서 **동일한 위치**에 나타나는 고립된 밝은 점 또는 어두운 점
- 주변 픽셀과 극단적으로 다른 값을 가지는 단일 픽셀
- 플랫필드(flat-field) 이미지에서 동일 위치에 재현되는 이상 픽셀
- 시간에 따라 변하지 않는 고정 패턴 노이즈(fixed-pattern noise)

### 자동 탐지

```python
import numpy as np
from scipy.ndimage import median_filter

def detect_dead_hot_pixels(xrf_map, z_threshold=5.0, neighbor_threshold=3.0):
    """
    Z-score 및 이웃 비교를 사용하여 데드/핫 픽셀을 탐지합니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D XRF elemental map (counts).
    z_threshold : float
        Global z-score threshold for outlier detection.
    neighbor_threshold : float
        Local neighbor comparison threshold (multiplier of local MAD).

    Returns
    -------
    dict
        탐지 결과를 담은 딕셔너리.
    """
    # --- 방법 1: 전역 Z-score ---
    mean_val = np.mean(xrf_map)
    std_val = np.std(xrf_map)

    if std_val > 0:
        z_scores = np.abs((xrf_map - mean_val) / std_val)
    else:
        z_scores = np.zeros_like(xrf_map, dtype=float)

    global_outliers = z_scores > z_threshold

    # --- 방법 2: 이웃 픽셀 비교 ---
    # 메디안 필터로 지역 중앙값 계산
    local_median = median_filter(xrf_map.astype(float), size=3)
    residual = np.abs(xrf_map.astype(float) - local_median)

    # MAD(Median Absolute Deviation) 기반 임계값
    mad = np.median(residual)
    mad_scaled = mad * 1.4826  # 정규분포 일관성 상수

    if mad_scaled > 0:
        local_outliers = residual / mad_scaled > neighbor_threshold
    else:
        local_outliers = residual > 0

    # --- 결합 ---
    # 데드 픽셀: 값이 0인 픽셀
    dead_mask = xrf_map == 0

    # 핫 픽셀: 전역 또는 지역 기준에서 이상치
    hot_mask = (global_outliers | local_outliers) & ~dead_mask

    # 결합된 불량 픽셀 마스크
    bad_pixel_mask = dead_mask | hot_mask

    n_dead = int(np.sum(dead_mask))
    n_hot = int(np.sum(hot_mask))
    n_total = xrf_map.size

    # 심각도 분류
    bad_fraction = (n_dead + n_hot) / n_total
    if bad_fraction > 0.01:
        severity = "critical"
    elif bad_fraction > 0.001:
        severity = "major"
    elif bad_fraction > 0:
        severity = "minor"
    else:
        severity = "none"

    print(f"Dead pixels: {n_dead} ({n_dead / n_total:.4%})")
    print(f"Hot pixels:  {n_hot} ({n_hot / n_total:.4%})")
    print(f"Severity:    {severity}")

    return {
        "dead_mask": dead_mask,
        "hot_mask": hot_mask,
        "bad_pixel_mask": bad_pixel_mask,
        "n_dead": n_dead,
        "n_hot": n_hot,
        "severity": severity,
    }
```

## 해결 및 완화

### 예방 (데이터 수집 전)

1. **플랫필드 촬영** — 실험 전 플랫필드 이미지를 촬영하여 불량 픽셀 맵을 생성합니다.
2. **정기적 검출기 점검** — 검출기 불량 픽셀의 변화를 주기적으로 모니터링합니다.
3. **검출기 냉각** — 적절한 냉각으로 열 노이즈에 의한 핫 픽셀을 최소화합니다.
4. **방사선 차폐** — 불필요한 방사선 노출로부터 검출기를 보호합니다.

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.ndimage import median_filter

def replace_bad_pixels(xrf_map, bad_pixel_mask, method="median"):
    """
    불량 픽셀을 이웃 값으로 대체합니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D XRF elemental map.
    bad_pixel_mask : np.ndarray (bool)
        True where pixel is bad.
    method : str
        'median' for median filter replacement,
        'interpolate' for bilinear interpolation.

    Returns
    -------
    corrected : np.ndarray
        Corrected map.
    """
    corrected = xrf_map.copy().astype(float)

    if method == "median":
        # 메디안 필터로 대체값 생성
        filtered = median_filter(corrected, size=3)
        corrected[bad_pixel_mask] = filtered[bad_pixel_mask]

    elif method == "interpolate":
        from scipy.interpolate import griddata

        ny, nx = xrf_map.shape
        yy, xx = np.mgrid[0:ny, 0:nx]

        # 정상 픽셀 좌표 및 값
        good_mask = ~bad_pixel_mask
        good_points = np.column_stack((yy[good_mask], xx[good_mask]))
        good_values = corrected[good_mask]

        # 불량 픽셀 좌표
        bad_points = np.column_stack((yy[bad_pixel_mask], xx[bad_pixel_mask]))

        # 보간
        if len(bad_points) > 0:
            interpolated = griddata(
                good_points, good_values, bad_points,
                method='linear', fill_value=np.nanmedian(good_values)
            )
            corrected[bad_pixel_mask] = interpolated

    n_replaced = np.sum(bad_pixel_mask)
    print(f"Replaced {n_replaced} bad pixels using {method} method")

    return corrected


def build_bad_pixel_mask(flat_field_images):
    """
    복수의 플랫필드 이미지로부터 불량 픽셀 마스크를 생성합니다.

    Parameters
    ----------
    flat_field_images : list of np.ndarray
        동일 조건에서 촬영한 플랫필드 이미지 목록.

    Returns
    -------
    bad_mask : np.ndarray (bool)
        불량 픽셀 마스크.
    """
    stacked = np.stack(flat_field_images, axis=0)
    mean_flat = np.mean(stacked, axis=0)
    std_flat = np.std(stacked, axis=0)

    # 데드 픽셀: 모든 이미지에서 0
    dead = np.all(stacked == 0, axis=0)

    # 핫 픽셀: 평균에서 크게 벗어남
    global_mean = np.mean(mean_flat)
    global_std = np.std(mean_flat)
    hot = mean_flat > global_mean + 5 * global_std

    # 불안정 픽셀: 분산이 비정상적으로 큼
    median_std = np.median(std_flat)
    unstable = std_flat > 5 * median_std

    bad_mask = dead | hot | unstable

    print(f"Bad pixel mask: {np.sum(dead)} dead, "
          f"{np.sum(hot)} hot, {np.sum(unstable)} unstable, "
          f"total {np.sum(bad_mask)}")

    return bad_mask
```

### 보정 — AI/ML 방법

데드/핫 픽셀 보정은 전통적인 방법(메디안 필터, 보간)으로 충분히 효과적이므로, 일반적으로 AI/ML 방법이 필요하지 않습니다. 불량 픽셀 위치가 명확하고 보간이 간단하기 때문에 전통적 접근이 표준입니다.

## 미보정 시 영향

- **거짓 농도 값** — 데드 픽셀은 0 농도로, 핫 픽셀은 비현실적으로 높은 농도로 나타납니다.
- **오해의 소지가 있는 공간 특징** — 단일 픽셀의 이상값이 실제 시료 특징으로 오인될 수 있습니다.
- **통계 분석 왜곡** — 평균, 분산 등 통계량이 이상치에 의해 편향됩니다.
- **다운스트림 분석 오류** — 클러스터링, 주성분 분석(PCA) 등 후속 분석에 오류가 전파됩니다.

## 관련 자료

- [XRF EDA 노트북](../../06_data_structures/eda/xrf_eda.md) — XRF 데이터 탐색적 분석
- [링 아티팩트](../tomography/ring_artifact.md) — 토모그래피에서의 유사한 검출기 결함 문제

## 핵심 요약

> **플랫필드 데이터로 불량 픽셀 마스크를 생성하고, 정량 분석 전에 반드시 적용하세요.** 데드/핫 픽셀은 모든 원소 맵에서 동일한 위치에 나타나므로, 단일 마스크로 모든 채널을 보정할 수 있습니다.

---
