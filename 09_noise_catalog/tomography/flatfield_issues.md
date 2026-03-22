# 플랫필드 문제(Flat-Field Issues)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

![플랫필드 비균일성 시뮬레이션 전후 비교 — Shepp-Logan 팬텀](../images/flatfield_before_after.png)

> **이미지 출처:** 합성 — 빔 비균일성이 시뮬레이션된 Shepp-Logan 팬텀, 플랫필드 + 다크필드 정규화로 보정.

## 설명

플랫필드 문제는 재구성된 슬라이스 전체에 걸쳐 부드러운 강도 음영, 밝거나 어두운 패치, 또는 국부적인 강도 불균일성으로 나타납니다. 링 아티팩트(동심원 패턴)와 달리, 플랫필드 문제는 넓고 느리게 변하는 강도 기울기 또는 패치 형태의 영역을 생성하여 겉보기 감쇠값을 왜곡합니다. 심한 경우 시야각 가장자리 근처에 밝거나 어두운 헤일로가 나타나거나 잘못된 강도의 뚜렷한 얼룩 모양 영역이 나타날 수 있습니다.

## 근본 원인

플랫필드 보정은 "플랫" 이미지(시료 없는 빔)로 나누고 "다크" 이미지(빔 없음)를 빼서 원시 투영을 정규화합니다. 플랫필드 이미지가 시료 수집 중 빔 조건을 정확히 반영하지 못할 때 문제가 발생합니다. 일반적인 원인: 신틸레이터 결함(균열, 박리, 두께 변동), 신틸레이터나 광학 요소의 먼지, 입사 빔의 공간적 비균일성, 플랫필드 수집과 시료 측정 사이의 빔 강도/프로파일의 시간적 드리프트, 신틸레이터 잔광이나 방사선 손상으로 인한 응답 변화, 플랫필드 프레임의 불충분한 평균화(정규화에 통계적 노이즈 잔존).

## 빠른 진단

```python
import numpy as np

flat = flat_field_image.astype(float)
flat_norm = flat / np.max(flat)
cv = np.std(flat_norm) / np.mean(flat_norm)
print(f"플랫필드 변동 계수: {cv:.4f}")
print(f"플랫필드 비균일성 문제 가능성: {cv > 0.05}")
```

## 탐지 방법

### 시각적 지표

- 시료 구조와 무관한 재구성 슬라이스 전체의 부드러운 강도 기울기
- 여러 슬라이스에서 동일한 공간 위치에 지속되는 밝거나 어두운 패치
- 재구성의 엣지 밝아짐(vignetting) 효과
- 광학 요소의 먼지로 인한 얼룩 형태 아티팩트
- 초기와 후기 투영 비교 시 다른 배경 강도 패턴

### 자동 탐지

```python
import numpy as np
from scipy import ndimage


def detect_flatfield_issues(flat_images, dark_image=None, threshold_cv=0.05):
    """
    플랫필드 이미지의 비균일성과 결함을 분석합니다.
    """
    if flat_images.ndim == 2:
        flat_images = flat_images[np.newaxis, ...]

    flat_avg = np.mean(flat_images, axis=0).astype(np.float64)

    if dark_image is not None:
        flat_avg = flat_avg - dark_image.astype(np.float64)
        flat_avg = np.clip(flat_avg, 1.0, None)

    flat_norm = flat_avg / np.median(flat_avg)
    cv = np.std(flat_norm) / np.mean(flat_norm)

    issues = []

    median_val = np.median(flat_norm)
    mad = np.median(np.abs(flat_norm - median_val))
    defect_mask = np.abs(flat_norm - median_val) > 5 * 1.4826 * mad
    num_defects = np.sum(defect_mask)

    if num_defects > 0.001 * flat_norm.size:
        issues.append(f"과도한 결함 픽셀: {num_defects}")

    smoothed = ndimage.gaussian_filter(flat_norm, sigma=50)
    gradient_range = np.max(smoothed) - np.min(smoothed)
    if gradient_range > 0.1:
        issues.append(f"대규모 강도 기울기: {gradient_range:.3f}")

    if flat_images.shape[0] > 1:
        flat_std = np.std(flat_images.astype(np.float64), axis=0)
        temporal_cv = np.mean(flat_std) / np.mean(flat_avg)
        if temporal_cv > 0.02:
            issues.append(f"높은 시간적 플랫필드 변동: {temporal_cv:.4f}")

    if cv > threshold_cv:
        issues.append(f"높은 전체 비균일성 (CV={cv:.4f})")

    return {
        "coefficient_of_variation": float(cv),
        "has_issues": len(issues) > 0,
        "defect_mask": defect_mask,
        "issues_found": issues,
    }
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 시료 스캔 직전과 직후에 플랫필드 이미지를 수집합니다(몇 시간 전이 아님).
- 많은 플랫필드 프레임(20-100장)을 수집하고 평균하여 통계적 노이즈를 억제합니다.
- 실험 전 신틸레이터의 먼지, 긁힘, 박리를 검사합니다.
- 스캔 시작 전 빔 안정성을 확인하고 주입 후 빔 평형을 기다립니다.

### 보정 — 전통적 방법

동적 플랫필드 보정은 스캔 전후에 수집된 플랫필드 이미지를 선형 보간하여 시간적 드리프트를 보상합니다.

```python
import numpy as np
from scipy import ndimage


def dynamic_flatfield_correction(projections, flats_before, flats_after,
                                  dark_image):
    """
    스캔 전후의 플랫필드 간 선형 보간으로 동적 플랫필드 보정을 적용합니다.
    """
    flat_pre = np.mean(flats_before, axis=0).astype(np.float64)
    flat_post = np.mean(flats_after, axis=0).astype(np.float64)
    dark = dark_image.astype(np.float64)

    num_proj = projections.shape[0]
    corrected = np.zeros_like(projections, dtype=np.float64)

    for i in range(num_proj):
        weight = i / max(num_proj - 1, 1)
        flat_interp = (1 - weight) * flat_pre + weight * flat_post
        flat_interp = flat_interp - dark
        flat_interp = np.clip(flat_interp, 1.0, None)

        proj = projections[i].astype(np.float64) - dark
        corrected[i] = proj / flat_interp

    return corrected
```

### 보정 — AI/ML 방법

플랫필드 보정 아티팩트에 특화된 확립된 AI/ML 방법은 없습니다. 플랫필드 오류의 느리게 변하는 특성은 전통적인 저주파 필터링 접근법에 적합합니다.

## 보정하지 않을 경우의 영향

플랫필드 문제는 재구성된 감쇠값에 공간적으로 변하는 편향을 도입하여 정량적 밀도 측정을 신뢰할 수 없게 만듭니다. 잘못된 정규화 영역은 거짓 밀도 변동으로 나타나 세그멘테이션 오류를 유발합니다. 기공률 측정, 물질 식별, 치수 계측 등 후속 분석이 모두 영향을 받습니다.

## 관련 자료

- [토모그래피 EDA 노트북](../../06_data_structures/eda/tomo_eda.md) — 플랫필드 품질 검사
- 관련 아티팩트: [링 아티팩트](ring_artifact.md) — 종종 플랫필드 픽셀 결함에 의해 발생하거나 증폭됨
- 관련 아티팩트: [빔 강도 저하](beam_intensity_drop.md) — 플랫필드가 보정할 수 없는 시간적 빔 변화

## 핵심 요점

플랫필드 보정은 정량적 토모그래피의 기초입니다 — 고품질의 동시대 플랫 및 다크 이미지 수집에 시간을 투자하세요. 스캔 중 빔 조건이 드리프트할 때, 스캔 전후의 보간된 플랫 이미지를 사용한 동적 플랫필드 보정이 정규화 품질을 크게 향상시킵니다.
