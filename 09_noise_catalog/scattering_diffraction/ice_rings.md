# 얼음 링(Ice Rings, 결정학)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 거대분자 결정학(MX) |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 큼(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |
| **기원 도메인** | 방사광 결정학(Diamond, ESRF, APS, SPring-8) |

## 시각적 예시

![보정 전후 — 회절에서의 얼음 링](../images/ice_rings_before_after.png)

> **이미지 출처:** 알려진 d-spacings에 시뮬레이션된 얼음 분말 링이 포함된 합성 2D 회절 패턴. 왼쪽: Bragg 반사와 겹치는 얼음 링. 오른쪽: 얼음 링 마스킹 및 보간 후. MIT 라이선스.

## 설명

얼음 링(Ice rings)은 결정학 회절 이미지에서 결정성 얼음(육방정 Ih 또는 입방정 Ic)에 해당하는 특정 d-spacings에서 나타나는 날카롭고 동심원 형태의 분말 회절 링입니다. 이는 시료, 루프 또는 cryo-stream에 형성된 얼음에서 발생하며, Bragg 반사를 가리고 강도 측정을 손상시키며 구조 결정에 체계적 오차를 도입할 수 있습니다.

## 근본 원인

- **저온 냉각 아티팩트:** 결정을 100K로 급속 냉각할 때 cryoprotection이 부적절하면 결정성 얼음이 형성될 수 있음
- **Cryo-stream 결빙:** 차가운 스트림이나 시료 마운트에 수분 응결
- **불완전한 유리화:** Cryoprotectant 농도가 너무 낮음 → 모액(mother liquor)에 얼음 결정 형성
- **시간에 따른 얼음 축적:** 긴 데이터 수집 동안 습한 공기로부터 얼음이 축적

### 특징적인 d-spacings (육방정 얼음 Ih)

```
d = 3.90 Å  (strongest)
d = 3.67 Å
d = 3.44 Å  (strong)
d = 2.67 Å
d = 2.25 Å
d = 1.92 Å
d = 1.72 Å
```

## 빠른 진단

```python
import numpy as np

# Known ice ring d-spacings (Angstroms) for hexagonal ice
ICE_D_SPACINGS = [3.90, 3.67, 3.44, 2.67, 2.25, 1.92, 1.72]

def check_ice_rings(resolution_bins, mean_intensity_per_bin, wavelength=1.0):
    """Check for ice rings by looking for intensity spikes at known d-spacings."""
    ice_resolutions = [d for d in ICE_D_SPACINGS]
    baseline = np.median(mean_intensity_per_bin)
    threshold = baseline + 3 * np.std(mean_intensity_per_bin)
    ice_detected = []
    for d_ice in ice_resolutions:
        # Find nearest resolution bin
        idx = np.argmin(np.abs(resolution_bins - d_ice))
        if mean_intensity_per_bin[idx] > threshold:
            ice_detected.append(d_ice)
            print(f"⚠ Ice ring detected at d = {d_ice:.2f} Å")
    if not ice_detected:
        print("No ice rings detected")
    return ice_detected
```

## 탐지 방법

### 시각적 지표

- 회절 이미지의 밝은 동심원 링(분말 패턴 링)
- 얼음의 특정 알려진 d-spacings에서의 링
- 링이 배경 산란보다 날카롭지만 Bragg 점보다는 넓음
- 강도 vs 해상도 플롯에서 얼음 d-spacings에 강도 스파이크 확인

### 자동 탐지

```python
import numpy as np

def azimuthal_intensity_at_d(image_2d, center, d_spacing, wavelength,
                              detector_distance, pixel_size):
    """Compute azimuthal intensity profile at a specific d-spacing."""
    theta = np.arcsin(wavelength / (2 * d_spacing))
    r_pixels = detector_distance * np.tan(2 * theta) / pixel_size
    ny, nx = image_2d.shape
    Y, X = np.ogrid[:ny, :nx]
    R = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
    ring_mask = np.abs(R - r_pixels) < 2  # 2-pixel width
    ring_intensity = image_2d[ring_mask].mean() if ring_mask.any() else 0
    return ring_intensity
```

## 보정 방법

### 예방

1. **적절한 Cryoprotection:** Cryoprotectant(glycerol, PEG, ethylene glycol) 농도 최적화
2. **건조한 Cryo-stream:** 질소 스트림이 수분이 없도록 보장
3. **어닐링(Annealing):** 결정을 잠시 데웠다가 재냉각하여 유리화 향상
4. **습도 제어:** 회절계 주변에 제습기 사용

### 데이터 처리

1. **해상도 셸 제외:** 영향을 받는 해상도 빈을 스케일링/정제에서 제외
2. **얼음 링 플래그:** 얼음 d-spacings 근처의 반사를 신뢰할 수 없는 것으로 표시
3. **배경 모델링:** 얼음 링을 추가 배경 성분으로 모델링

```python
def flag_ice_ring_reflections(hkl_data, d_spacings_ice=None, tolerance=0.02):
    """Flag reflections that fall within ice ring d-spacings."""
    if d_spacings_ice is None:
        d_spacings_ice = [3.90, 3.67, 3.44, 2.67, 2.25, 1.92, 1.72]
    flags = np.zeros(len(hkl_data['d']), dtype=bool)
    for d_ice in d_spacings_ice:
        flags |= np.abs(hkl_data['d'] - d_ice) < tolerance
    n_flagged = flags.sum()
    print(f"Flagged {n_flagged} reflections ({n_flagged/len(flags):.1%}) near ice rings")
    return flags
```

### 소프트웨어 도구

- **DIALS** — 자동 얼음 링 탐지 및 제외(Diamond Light Source)
- **XDS** — EXCLUDE_RESOLUTION_RANGE 키워드
- **autoPROC** — 자동화된 얼음 링 처리(Global Phasing)
- **CCP4 / AIMLESS** — 해상도 셸 거부

## 주요 참고문헌

- **Parkhurst et al. (2017)** — Ice ring detection in DIALS
- **Thorn et al. (2017)** — "Subatomic resolution crystal structures: ice ring artifacts and modelling"
- **Garman & Weik (2023)** — "Radiation damage in macromolecular crystallography" (review)

## 시설별 벤치마크

| 시설 | 접근법 |
|------|--------|
| Diamond I03/I04 | DIALS 자동 얼음 링 탐지 파이프라인 |
| ESRF ID23/ID30 | 얼음 탐지를 포함한 MXCuBE 자동 데이터 수집 |
| SPring-8 BL32XU | 얼음 모니터링이 포함된 ZOO 자동 시스템 |
| APS GM/CA | 얼음 링 경고가 포함된 JBluIce |
| NSLS-II FMX/AMX | 자동 품질 측정 지표 포함 LSDC |

## 실제 보정 전후 예시

다음 출판된 자료들은 실제 실험적 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림 | 설명 | 라이선스 |
|------|------|------|------|---------|
| [Parkhurst et al. 2017](https://doi.org/10.1107/S2059798317010348) | 논문 | Fig. 1 | 얼음 링이 존재하는 상황에서의 배경 모델링 — 실제 MX 데이터에서 얼음 링 마스킹 전후 | BSD-3 |
| [DIALS documentation](https://dials.github.io/) | 소프트웨어 문서 | 다수 | 얼음 링 탐지 및 마스킹 도구를 갖춘 DIALS 회절 적분 소프트웨어 | BSD-3 |

**출판된 보정 전후 비교를 포함한 주요 참고문헌:**
- **Parkhurst et al. (2017)**: Fig. 1은 실제 결정학 데이터에서 얼음 링 마스킹 전후를 보여줍니다. DOI: 10.1107/S2059798317010348

> **권장 참고자료**: [Parkhurst et al. 2017 — DIALS integration package (Acta Cryst D)](https://doi.org/10.1107/S2059798317010348)

## 관련 자료

- [방사선 손상](../spectroscopy/radiation_damage.md) — 둘 다 cryo 관련 실험적 문제
- [링 아티팩트](../tomography/ring_artifact.md) — 다른 기원이지만 유사한 링 형태
