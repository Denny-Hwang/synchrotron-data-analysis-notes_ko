# 회전 중심 오류(Rotation Center Error)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

![회전 중심 오프셋이 있는 Shepp-Logan 팬텀 전후 비교](../images/rotation_center_error_before_after.png)

> **이미지 출처:** 합성 — +5 픽셀 회전 중심 오프셋으로 재구성한 Shepp-Logan 팬텀 vs. 올바른 중심 정렬.

## 설명

회전 중심 오류는 재구성된 CT 슬라이스에서 시야 전체에 걸친 컵핑(cupping) 또는 돔형(doming) 강도 프로파일, 날카로운 엣지의 소리굽쇠(tuning-fork) 형태 이중화, 중심에서 벗어난 동심원 링 또는 호 패턴 등 특징적인 아티팩트를 생성합니다. 작은 오류(서브픽셀)는 미묘한 흐림과 해상도 손실을 유발하고, 큰 오류(수 픽셀)는 특징 주위에 명확한 이중 이미지 또는 초승달 모양 아티팩트를 만듭니다.

## 근본 원인

필터 역투영법과 대부분의 반복 재구성 알고리즘은 검출기에 대한 회전축 위치의 정밀한 정보를 필요로 합니다. 오류 원인: 회전 스테이지의 기계적 오정렬, 위치 시스템의 엔코더 드리프트 또는 백래시, 스캔 중 열팽창으로 인한 회전축 이동, 잘못된 메타데이터 또는 수동 입력, 비대칭 시료 장착 등. 고해상도 데이터셋에서는 서브픽셀 오류도 재구성 품질을 저하시킵니다.

## 빠른 진단

```python
import numpy as np

proj_0 = projections[0].astype(float)
proj_180 = projections[num_proj // 2].astype(float)
proj_180_flipped = np.fliplr(proj_180)
from scipy.ndimage import shift as ndi_shift
correlation = np.correlate(np.mean(proj_0, axis=0), np.mean(proj_180_flipped, axis=0), mode='full')
offset = np.argmax(correlation) - (proj_0.shape[1] - 1)
print(f"추정 중심 오프셋: {offset / 2:.1f} 픽셀")
```

## 탐지 방법

### 시각적 지표

- 재구성에서 균일 영역의 그릇 모양 프로파일(컵핑/돔형 아티팩트)
- 소리굽쇠 이중화 — 날카로운 엣지가 두 개의 근접한 평행선으로 나타남
- 중심에서 벗어난 반원형 호 또는 부분 링(중심에 있는 진정한 링 아티팩트와 구별)
- 이미지 한쪽에서는 개선되고 다른 쪽에서는 악화되는 흐림

### 자동 탐지

```python
import numpy as np
from scipy.signal import correlate


def detect_rotation_center_error(projections, expected_center=None):
    """0°와 180° 투영을 비교하여 회전 중심 오류를 탐지합니다."""
    num_proj = projections.shape[0]
    num_cols = projections.shape[2]

    if expected_center is None:
        expected_center = num_cols / 2.0

    proj_0 = np.mean(projections[0].astype(np.float64), axis=0)
    proj_180 = np.mean(projections[num_proj // 2].astype(np.float64), axis=0)
    proj_180_flip = proj_180[::-1]

    corr = correlate(proj_0, proj_180_flip, mode='full')
    peak_idx = np.argmax(corr)
    if 1 <= peak_idx <= len(corr) - 2:
        y0, y1, y2 = corr[peak_idx - 1], corr[peak_idx], corr[peak_idx + 1]
        delta = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-10)
        refined_peak = peak_idx + delta
    else:
        refined_peak = float(peak_idx)

    estimated_center = (refined_peak - num_cols + 1) / 2.0 + num_cols / 2.0
    center_offset = estimated_center - expected_center

    abs_offset = abs(center_offset)
    if abs_offset < 0.5:
        severity = "none"
    elif abs_offset < 2.0:
        severity = "mild"
    elif abs_offset < 5.0:
        severity = "moderate"
    else:
        severity = "severe"

    return {
        "estimated_center": float(estimated_center),
        "center_offset": float(center_offset),
        "has_error": abs_offset > 0.5,
        "severity": severity,
    }
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 실험 전 정렬 도구를 사용하여 회전축을 신중하게 정렬합니다.
- 전체 스캔 전에 180° 투영 쌍을 수집하고 실시간으로 정렬을 확인합니다.
- 기준 마커(예: 작은 구)를 사용하여 회전 중심을 교정합니다.

### 보정 — 전통적 방법

TomoPy는 재구성 전에 적용할 수 있는 여러 자동 회전 중심 찾기 알고리즘을 제공합니다.

```python
import tomopy
import numpy as np


def find_and_apply_rotation_center(projections, theta):
    """올바른 회전 중심을 찾고 이를 적용하여 재구성합니다."""
    center_vo = tomopy.find_center_vo(projections)
    print(f"Vo 방법 중심: {center_vo:.2f}")

    center_pc = tomopy.find_center_pc(
        projections[0], projections[projections.shape[0] // 2]
    )
    print(f"위상 상관 중심: {center_pc:.2f}")

    center = center_vo

    recon = tomopy.recon(
        projections, theta, center=center, algorithm='gridrec'
    )
    recon = tomopy.circ_mask(recon, axis=0, ratio=0.95)

    return recon, center
```

### 보정 — AI/ML 방법

회전 중심 찾기에 특화된 확립된 AI/ML 방법은 없습니다. 이 문제는 전통적인 교차 상관과 최적화 방법으로 잘 해결됩니다. 그러나 재구성과 기하학적 매개변수를 동시에 최적화하는 학습된 재구성 네트워크가 훈련의 일부로 작은 중심 오프셋을 암묵적으로 처리할 수 있습니다.

## 보정하지 않을 경우의 영향

회전 중심 오류는 재구성 전체에 걸쳐 공간 해상도를 균일하게 저하시키고 잘못된 강도 변동을 도입합니다. 엣지 기반 측정(벽 두께, 입자 크기)은 이중화 효과로 편향됩니다. 고해상도 마이크로 CT 데이터셋에서는 1픽셀 오류도 해상도를 눈에 띄게 줄일 수 있습니다.

## 관련 자료

- [토모그래피 EDA 노트북](../../06_data_structures/eda/tomo_eda.md) — 회전 중심 확인
- 관련 아티팩트: [링 아티팩트](ring_artifact.md) — 중심에서 벗어난 링이 회전 중심 오류를 나타낼 수 있음
- 관련 아티팩트: [모션 아티팩트](motion_artifact.md) — 스캔 중 회전축 드리프트가 중심 오류와 유사

## 핵심 요점

회전 중심은 토모그래피 재구성 품질에 가장 중요한 단일 매개변수입니다. 전체 재구성을 실행하기 전에 항상 `find_center_vo()`와 같은 자동 방법으로 중심을 확인하고, 결과가 의심스러울 때 테스트 슬라이스에서 중심 스윕을 수행하세요 — 서브픽셀 보정으로 이미지 품질이 극적으로 향상될 수 있습니다.
