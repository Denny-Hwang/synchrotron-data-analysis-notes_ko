# 피크 중첩(Peak Overlap)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

```
에너지 스펙트럼에서의 피크 중첩 예시:

      Fe Kβ (7.058 keV)    Co Kα (6.930 keV)
         ↓                    ↓
    │    ╱╲        ╱╲
    │   ╱  ╲      ╱  ╲
    │  ╱    ╲────╱    ╲      ← 검출기 해상도로 분리 불가
    │ ╱      ╲╱╱       ╲
    │╱                    ╲
    └──────────────────────── 에너지 (keV)
         6.8   6.9   7.0   7.1

    검출기 에너지 분해능: ~130 eV (SDD @ Mn Kα)
```

## 설명

여러 원소의 형광선(fluorescence line)이 유사한 에너지를 가져 측정된 스펙트럼에서 중첩되는 현상입니다. 검출기의 에너지 분해능이 이러한 근접한 피크를 완전히 분리하기에 불충분할 때 발생합니다.

흔한 피크 중첩 사례:
- **Fe K-beta / Co K-alpha** (7.058 keV / 6.930 keV, 차이 128 eV)
- **Ca K-beta / Sc K-alpha** (4.013 keV / 4.091 keV, 차이 78 eV)
- **S K-alpha / Mo L-alpha** (2.308 keV / 2.293 keV, 차이 15 eV)
- **Ti K-beta / V K-alpha** (4.932 keV / 4.952 keV, 차이 20 eV)
- **Pb L-alpha / As K-alpha** (10.551 keV / 10.544 keV, 차이 7 eV)

## 근본 원인

검출기의 에너지 분해능이 근접한 형광선을 완전히 분리하는 데 불충분한 것이 근본 원인입니다.

- **SDD(Silicon Drift Detector)** 의 에너지 분해능은 Mn K-alpha에서 약 **~130 eV** 수준입니다.
- 분해능보다 작은 에너지 차이를 가진 형광선은 단일 브로드 피크(broad peak)로 나타납니다.
- 분해능은 에너지에 따라 변하며, 저에너지에서는 약간 더 좋아집니다.
- 다중 원소가 공존하는 시료에서 특히 문제가 됩니다.

## 빠른 진단

피팅 후 잔차 분석과 카이제곱(chi-squared) 맵을 통해 빠르게 진단할 수 있습니다.

```python
import numpy as np

def quick_overlap_check(spectrum, fitted_spectrum, energy_axis):
    """
    스펙트럼 피팅 잔차를 분석하여 피크 중첩 가능성을 평가합니다.

    Parameters
    ----------
    spectrum : np.ndarray
        Measured spectrum (1D, counts).
    fitted_spectrum : np.ndarray
        Fitted model spectrum (1D).
    energy_axis : np.ndarray
        Energy values for each channel (keV).

    Returns
    -------
    dict with residual statistics and suspicious regions.
    """
    residual = spectrum - fitted_spectrum
    chi_squared = np.sum(residual**2 / np.maximum(fitted_spectrum, 1))
    n_channels = len(spectrum)
    reduced_chi2 = chi_squared / max(n_channels - 1, 1)

    # 잔차에서 체계적 패턴 탐색
    # 연속적으로 양수 또는 음수인 구간 찾기
    sign_changes = np.diff(np.sign(residual))
    runs = np.where(sign_changes != 0)[0]
    max_run_length = np.max(np.diff(runs)) if len(runs) > 1 else n_channels

    print(f"Reduced chi-squared: {reduced_chi2:.2f}")
    print(f"Max residual run length: {max_run_length} channels")
    if reduced_chi2 > 2.0:
        print("WARNING: Poor fit — possible peak overlap or missing elements")
    if max_run_length > 10:
        print("WARNING: Systematic residual pattern detected")

    return {
        "reduced_chi2": reduced_chi2,
        "max_run_length": max_run_length,
        "residual": residual,
    }
```

## 탐지 방법

### 시각적 지표

- 피팅 잔차에서 피크 위치 근처의 **체계적인 양/음 패턴**
- 특정 에너지 영역에서 비대칭적인 피크 형태
- 알려진 중첩 쌍(예: Fe/Co)에서 비정상적인 원소 비율
- 시료에 존재할 가능성이 낮은 원소가 검출되는 경우 (유령 신호)

### 자동 탐지

```python
import numpy as np

# 알려진 피크 중첩 쌍 데이터베이스
KNOWN_OVERLAPS = [
    {"pair": ("Fe Kb", "Co Ka"), "energies": (7.058, 6.930), "delta_eV": 128},
    {"pair": ("Ca Kb", "Sc Ka"), "energies": (4.013, 4.091), "delta_eV": 78},
    {"pair": ("S Ka", "Mo La"), "energies": (2.308, 2.293), "delta_eV": 15},
    {"pair": ("Ti Kb", "V Ka"), "energies": (4.932, 4.952), "delta_eV": 20},
    {"pair": ("Pb La", "As Ka"), "energies": (10.551, 10.544), "delta_eV": 7},
    {"pair": ("Mn Kb", "Fe Ka"), "energies": (6.490, 6.404), "delta_eV": 86},
]


def assess_peak_overlap(fitted_maps, residual_cube, energy_axis,
                         element_list, detector_resolution_eV=130):
    """
    피크 중첩 가능성을 평가하고 문제 영역을 보고합니다.

    Parameters
    ----------
    fitted_maps : dict
        {element_name: 2D fitted map} 딕셔너리.
    residual_cube : np.ndarray
        Shape (ny, nx, n_channels) — 각 픽셀의 피팅 잔차.
    energy_axis : np.ndarray
        Energy axis in keV.
    element_list : list of str
        피팅에 포함된 원소 목록.
    detector_resolution_eV : float
        검출기 에너지 분해능 (eV).

    Returns
    -------
    report : dict
        중첩 평가 보고서.
    """
    warnings = []

    # 1. 알려진 중첩 쌍 확인
    for overlap in KNOWN_OVERLAPS:
        e1_name, e2_name = overlap["pair"]
        # 원소 목록에 두 원소가 모두 있는지 확인
        e1_base = e1_name.split()[0]
        e2_base = e2_name.split()[0]

        if e1_base in element_list and e2_base in element_list:
            if overlap["delta_eV"] < detector_resolution_eV:
                warnings.append(
                    f"OVERLAP: {e1_name} / {e2_name} "
                    f"(delta={overlap['delta_eV']} eV < "
                    f"resolution={detector_resolution_eV} eV)"
                )

    # 2. 픽셀별 reduced chi-squared 계산
    n_pixels = residual_cube.shape[0] * residual_cube.shape[1]
    chi2_map = np.sum(residual_cube**2, axis=2) / max(residual_cube.shape[2] - 1, 1)

    mean_chi2 = np.mean(chi2_map)
    poor_fit_fraction = np.sum(chi2_map > 2.0) / n_pixels

    # 3. 잔차의 체계적 패턴 분석
    mean_residual = np.mean(residual_cube, axis=(0, 1))
    systematic_residual = np.abs(mean_residual) > 3 * np.std(mean_residual)
    suspicious_channels = np.where(systematic_residual)[0]
    suspicious_energies = energy_axis[suspicious_channels] if len(suspicious_channels) > 0 else []

    for w in warnings:
        print(f"  {w}")
    print(f"Mean reduced chi2: {mean_chi2:.2f}")
    print(f"Poor fit pixels (chi2>2): {poor_fit_fraction:.1%}")
    if len(suspicious_energies) > 0:
        print(f"Suspicious energy regions: "
              f"{', '.join(f'{e:.3f} keV' for e in suspicious_energies[:5])}")

    return {
        "warnings": warnings,
        "chi2_map": chi2_map,
        "mean_chi2": mean_chi2,
        "poor_fit_fraction": poor_fit_fraction,
        "suspicious_energies": suspicious_energies,
    }
```

## 해결 및 완화

### 예방 (데이터 수집 전)

1. **높은 분해능 검출기 사용** — 에너지 분해능이 좋은 SDD를 선택합니다.
2. **여기 에너지 최적화** — 중첩 원소 중 하나의 흡수단(absorption edge) 아래 에너지를 사용하여 선택적 여기를 합니다.
3. **시료 사전 분석** — ICP-MS 등으로 원소 조성을 사전에 파악하여 중첩 가능성을 예측합니다.
4. **WDS(파장 분산 분광법) 병용** — 에너지 분해능이 훨씬 높은 WDS를 사용하여 중첩 원소를 확인합니다.

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.optimize import curve_fit

def multi_peak_deconvolution(spectrum, energy_axis, peak_params,
                               detector_fwhm_eV=130):
    """
    다중 가우시안 피크 디컨볼루션으로 중첩된 피크를 분리합니다.

    Parameters
    ----------
    spectrum : np.ndarray
        Measured spectrum (counts).
    energy_axis : np.ndarray
        Energy axis (keV).
    peak_params : list of dict
        각 피크의 초기 파라미터.
        [{"name": "Fe Ka", "energy": 6.404, "intensity": 1000}, ...]
    detector_fwhm_eV : float
        검출기 FWHM in eV.

    Returns
    -------
    result : dict
        디컨볼루션 결과 (각 피크의 피팅된 강도).
    """
    fwhm_keV = detector_fwhm_eV / 1000.0
    sigma_keV = fwhm_keV / 2.3548  # FWHM to sigma

    def multi_gaussian(x, *params):
        """다중 가우시안 모델. params: [amp1, center1, amp2, center2, ...]"""
        y = np.zeros_like(x, dtype=float)
        for i in range(0, len(params), 2):
            amp = params[i]
            center = params[i + 1]
            y += amp * np.exp(-0.5 * ((x - center) / sigma_keV) ** 2)
        return y

    # 초기 파라미터 및 제약 조건 구성
    p0 = []
    bounds_low = []
    bounds_high = []

    for pp in peak_params:
        p0.extend([pp["intensity"], pp["energy"]])
        bounds_low.extend([0, pp["energy"] - 0.01])  # 에너지 위치 제약
        bounds_high.extend([np.inf, pp["energy"] + 0.01])

    try:
        popt, pcov = curve_fit(
            multi_gaussian, energy_axis, spectrum,
            p0=p0, bounds=(bounds_low, bounds_high),
            maxfev=10000
        )
        perr = np.sqrt(np.diag(pcov))

        results = {}
        for i, pp in enumerate(peak_params):
            fitted_amp = popt[2 * i]
            fitted_center = popt[2 * i + 1]
            amp_err = perr[2 * i]

            results[pp["name"]] = {
                "amplitude": fitted_amp,
                "center_keV": fitted_center,
                "amplitude_error": amp_err,
                "relative_error": amp_err / fitted_amp if fitted_amp > 0 else np.inf,
            }
            print(f"{pp['name']}: amp={fitted_amp:.1f} +/- {amp_err:.1f}, "
                  f"center={fitted_center:.4f} keV")

        # 잔차 계산
        fitted_spectrum = multi_gaussian(energy_axis, *popt)
        residual = spectrum - fitted_spectrum

        results["fitted_spectrum"] = fitted_spectrum
        results["residual"] = residual

        return results

    except RuntimeError as e:
        print(f"Fitting failed: {e}")
        return None


def constrained_ka_kb_fit(spectrum, energy_axis, element,
                           ka_energy, kb_energy, kb_ka_ratio=0.13):
    """
    K-alpha/K-beta 비율을 제약 조건으로 사용하는 피팅.

    Parameters
    ----------
    spectrum : np.ndarray
        Measured spectrum.
    energy_axis : np.ndarray
        Energy axis (keV).
    element : str
        Element name.
    ka_energy : float
        K-alpha line energy (keV).
    kb_energy : float
        K-beta line energy (keV).
    kb_ka_ratio : float
        Physical K-beta/K-alpha intensity ratio (typically ~0.13 for 3d metals).

    Returns
    -------
    dict with fitted Ka intensity and quality metrics.
    """
    fwhm_keV = 0.130  # 130 eV
    sigma = fwhm_keV / 2.3548

    def constrained_model(x, amp_ka, background):
        """Ka + Kb (constrained ratio) + linear background."""
        ka = amp_ka * np.exp(-0.5 * ((x - ka_energy) / sigma) ** 2)
        kb = amp_ka * kb_ka_ratio * np.exp(-0.5 * ((x - kb_energy) / sigma) ** 2)
        return ka + kb + background

    try:
        popt, pcov = curve_fit(
            constrained_model, energy_axis, spectrum,
            p0=[np.max(spectrum), np.min(spectrum)],
            bounds=([0, 0], [np.inf, np.inf])
        )

        fitted = constrained_model(energy_axis, *popt)
        residual = spectrum - fitted
        chi2 = np.sum(residual**2 / np.maximum(fitted, 1)) / len(spectrum)

        print(f"{element}: Ka_amp={popt[0]:.1f}, "
              f"Kb_amp={popt[0] * kb_ka_ratio:.1f} (fixed ratio), "
              f"chi2={chi2:.3f}")

        return {
            "ka_amplitude": popt[0],
            "kb_amplitude": popt[0] * kb_ka_ratio,
            "background": popt[1],
            "chi2": chi2,
            "fitted_spectrum": fitted,
        }

    except RuntimeError as e:
        print(f"Fitting failed for {element}: {e}")
        return None
```

### 보정 — AI/ML 방법

피크 중첩 문제는 물리적으로 잘 정의된 문제이므로, 전통적인 다중 피크 디컨볼루션과 제약 조건 피팅이 표준 접근법입니다. AI/ML 방법은 일반적으로 필요하지 않으나, 매우 복잡한 스펙트럼(수십 개 원소 동시 분석)에서 딥러닝 기반 스펙트럼 분해가 연구되고 있습니다.

## 미보정 시 영향

- **잘못된 원소 정량** — 중첩된 원소의 농도가 과대 또는 과소 추정됩니다.
- **유령 원소 신호(Phantom Element)** — 시료에 존재하지 않는 원소가 검출된 것처럼 나타날 수 있습니다.
- **원소 비율 왜곡** — 관련 원소 간의 농도 비율이 부정확해집니다.
- **공간 분포 오해석** — 중첩 원소의 맵이 실제 분포가 아닌 혼합 신호를 보여줍니다.

## 관련 자료

- [PyXRF 문서](https://nsls-ii.github.io/PyXRF/) — NSLS-II의 XRF 스펙트럼 피팅 소프트웨어
- [MAPS 소프트웨어](https://www.aps.anl.gov/Sector-2/2-ID/Software) — APS의 XRF 분석 도구

## 핵심 요약

> **항상 피팅 잔차를 확인하고, K-alpha/K-beta 비율을 물리적 값으로 제약하여 피팅하세요.** 피크 중첩은 다중 피크 디컨볼루션으로 해결 가능하지만, 시료에 어떤 원소가 존재하는지 사전 지식이 중요합니다.

---
