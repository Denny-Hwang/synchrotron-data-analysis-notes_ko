# 부분 부피 효과(Partial Volume Effect)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 의료 CT / 방사광 토모그래피 / 현미경 |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 의료 영상(CT/PET) |

## 설명

부분 부피 효과(Partial Volume Effect, PVE)는 단일 복셀이 둘 이상의 물질의 혼합을 포함할 때 발생하며, 그 결과 어떤 실제 물질도 대표하지 않는 평균화된 감쇠 값이 산출됩니다. 이는 경계의 흐림, 부정확한 정량화, 인위적인 중간 밀도 영역을 야기합니다. 이는 모든 이산화 영상 모달리티에 본질적이며, 특징 크기가 복셀 해상도에 가까워질수록 매우 중요해집니다.

## 근본 원인

- 유한한 복셀 크기 → 각 복셀이 자신의 부피 내 모든 물질의 신호를 적분
- 복셀이 물질 경계에 걸쳐짐 → CT 값이 구성 물질의 가중 평균이 됨
- 다음의 경우 더 심함: 두꺼운 슬라이스, 거친 검출기 피치, 복셀 크기 대비 작은 특징
- PET/SPECT에서: 경계를 가로지르는 방사성 추적자 신호의 "유입(spill-in)"과 "유출(spill-out)"

## 빠른 진단

```python
import numpy as np

def detect_partial_volume(slice_2d, expected_values, tolerance=0.1):
    """Detect partial volume by finding voxels with intermediate values."""
    mask_intermediate = np.ones_like(slice_2d, dtype=bool)
    for val in expected_values:
        mask_intermediate &= np.abs(slice_2d - val) > tolerance * val
    pve_fraction = mask_intermediate.sum() / slice_2d.size
    print(f"Partial volume voxels: {pve_fraction:.1%}")
    return mask_intermediate
```

## 탐지 방법

### 시각적 지표

- 서로 다른 물질 간 흐려진 경계
- 가장자리에 있는 중간 회색값(어떤 알려진 물질과도 일치하지 않음)
- 작고 고밀도인 특징 주변의 명백한 "헤일로(halo)"
- 작은 물체가 실제보다 더 크고 덜 조밀하게 보임

### 자동 탐지

```python
import numpy as np
from scipy import ndimage

def edge_pve_analysis(slice_2d, sigma=1.0):
    """Quantify PVE at material boundaries using gradient analysis."""
    grad_mag = ndimage.gaussian_gradient_magnitude(slice_2d, sigma)
    # Identify boundary region
    threshold = np.percentile(grad_mag, 90)
    boundary_mask = grad_mag > threshold
    # Measure transition width
    return boundary_mask, grad_mag
```

## 보정 방법

### 전통적 접근법

1. **고해상도화:** 더 작은 복셀 크기 (명백하지만 선량/시간 측면에서 비용 큼)
2. **서브복셀 세분화:** 각 복셀을 알려진 물질들의 혼합으로 모델링
3. **디컨볼루션 기반 PVC:** 기하학적 전달 행렬(GTM) 보정 적용
4. **다중 해상도 융합:** 저해상도 볼륨 데이터와 고해상도 표면 데이터를 결합

### AI/ML 접근법

- **초해상도 CNN:** 서브복셀 물질 분포를 학습
- **세분화 인지 재구성:** 공동 세분화-재구성 프레임워크
- **PVC-Net:** PET/SPECT를 위한 부분 부피 보정 네트워크

## 주요 참고문헌

- **Kessler et al. (1984)** — 방사형 CT에서 부분 부피 효과 분석
- **Soret et al. (2007)** — "Partial-volume effect in PET tumor imaging" (리뷰)
- **Van Eijnatten et al. (2018)** — CT 기반 3D 프린팅에서의 PVE
- **Erlandsson et al. (2012)** — "A review of partial volume correction techniques for PET"

## 방사광 데이터와의 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 나노 토모그래피 | 해상도 한계 부근 특징에 매우 중요 |
| XRF 현미경 | 경계의 서브픽셀 원소 혼합 |
| 다상 물질 | 결정립 경계의 복셀이 평균 밀도를 보임 |
| 기공률 정량화 | 작은 기공이 과소 추정되어 기공률 분석이 편향됨 |

## 관련 자료

- [Probe blurring](../xrf_microscopy/probe_blurring.md) — XRF의 유사 공간 평균
- [Low-dose noise](../tomography/low_dose_noise.md) — 노이즈가 PVE 측정을 가중시킴
