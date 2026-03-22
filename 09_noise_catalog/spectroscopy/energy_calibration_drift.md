# 에너지 교정 드리프트(Energy Calibration Drift)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 가끔(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 설명

빔 운전 중 단색화기(monochromator) 결정의 온도 변화가 에너지 교정의 느린 드리프트를 유발하여, 연속 스캔 사이에서 겉보기 흡수단 위치(E0)가 이동합니다.

단색화기 결정(일반적으로 Si(111) 또는 Si(311))은 브래그 법칙(Bragg's law)에 따라 특정 에너지의 X-선을 선택합니다. 빔 흡수에 의한 열 부하(heat load)가 결정의 격자 상수(lattice constant)를 미세하게 변화시키면, 동일한 각도 설정에서 선택되는 에너지가 달라집니다. 이 드리프트는 일반적으로 0.1-1.0 eV 범위이지만, XANES 분석에서는 이 정도의 이동도 화학 상태 판정에 심각한 오류를 일으킬 수 있습니다.

## 근본 원인

1. **열 부하(Heat Load):** 고강도 방사광 빔이 첫 번째 결정에 흡수되어 국소적 온도 상승을 유발
2. **격자 상수 변화:** 온도 변화에 따른 실리콘 결정의 열팽창으로 격자 상수(d-spacing) 변화
3. **빔 전류 변동:** 저장 링(storage ring) 전류의 감소(탑오프 모드가 아닌 경우)에 따른 열 부하 변화
4. **냉각 시스템 불안정:** 단색화기 냉각수 온도 또는 유량의 변동
5. **기계적 드리프트:** 단색화기 기구부의 열팽창에 의한 미세 각도 변화

## 빠른 진단

기준 포일(reference foil)의 E0 값을 스캔별로 추적하여 드리프트를 빠르게 감지하는 코드:

```python
import numpy as np

def quick_e0_drift_check(energy_list, mu_ref_list):
    """
    기준 포일 스캔에서 E0 드리프트를 빠르게 확인합니다.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_ref_list : list of np.ndarray
        각 스캔의 기준 포일 흡수 스펙트럼

    Returns
    -------
    list of float
        각 스캔의 E0 값
    """
    e0_values = []
    for energy, mu in zip(energy_list, mu_ref_list):
        # 1차 미분의 최대값 위치로 E0 결정
        deriv = np.gradient(mu, energy)
        e0 = energy[np.argmax(deriv)]
        e0_values.append(e0)

    e0_values = np.array(e0_values)
    drift = e0_values[-1] - e0_values[0]
    print(f"E0 range: {np.min(e0_values):.2f} - {np.max(e0_values):.2f} eV")
    print(f"Total drift: {drift:.3f} eV over {len(e0_values)} scans")
    if np.abs(drift) > 0.5:
        print("WARNING: Significant energy drift detected!")
    return e0_values
```

이 코드는 기준 포일의 1차 미분 최대값을 E0로 정의하고, 스캔 간 변동을 추적합니다.

## 탐지 방법

### 시각적 지표

- **기준 포일 흡수단 이동:** 기준 포일의 XANES를 겹쳐 그리면 흡수단의 수평 이동이 관찰됨
- **E0 시계열 플롯:** 스캔 번호에 대한 E0 값의 단조 증가 또는 감소 추세
- **병합 스펙트럼의 흡수단 넓어짐:** 보정 없이 병합하면 흡수단이 인위적으로 넓어짐

### 자동 탐지

```python
import numpy as np
from scipy.interpolate import interp1d

def detect_energy_drift(energy_list, mu_ref_list, threshold_eV=0.3):
    """
    다중 스캔에서 에너지 교정 드리프트를 탐지합니다.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_ref_list : list of np.ndarray
        각 스캔의 기준 포일 흡수 스펙트럼
    threshold_eV : float
        드리프트 경고 임계값 (eV)

    Returns
    -------
    dict
        드리프트 탐지 결과
    """
    e0_values = []
    for energy, mu in zip(energy_list, mu_ref_list):
        # 1차 미분 최대값으로 E0 결정
        deriv = np.gradient(mu, energy)
        e0 = energy[np.argmax(deriv)]
        e0_values.append(e0)

    e0_values = np.array(e0_values)
    scan_numbers = np.arange(len(e0_values))

    # 선형 드리프트 피팅
    coeffs = np.polyfit(scan_numbers, e0_values, 1)
    drift_rate = coeffs[0]  # eV/scan
    total_drift = e0_values[-1] - e0_values[0]

    # 잔차로 무작위 변동과 체계적 드리프트 구분
    fitted = np.polyval(coeffs, scan_numbers)
    residuals = e0_values - fitted
    random_jitter = np.std(residuals)

    # 심각도 판정
    if np.abs(total_drift) > 1.0:
        severity = "critical"
    elif np.abs(total_drift) > threshold_eV:
        severity = "major"
    elif np.abs(total_drift) > 0.1:
        severity = "minor"
    else:
        severity = "none"

    return {
        "e0_values": e0_values,
        "total_drift_eV": float(total_drift),
        "drift_rate_eV_per_scan": float(drift_rate),
        "random_jitter_eV": float(random_jitter),
        "severity": severity,
    }


def align_scans_to_reference(energy_list, mu_list, mu_ref_list, e0_target=None):
    """
    기준 포일 E0를 기반으로 각 스캔의 에너지를 정렬합니다.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_list : list of np.ndarray
        각 스캔의 시료 흡수 스펙트럼
    mu_ref_list : list of np.ndarray
        각 스캔의 기준 포일 흡수 스펙트럼
    e0_target : float, optional
        목표 E0 (기본값: 첫 스캔의 E0)

    Returns
    -------
    list of tuple
        정렬된 (energy, mu) 쌍의 리스트
    """
    # 각 스캔의 E0 결정
    e0_values = []
    for energy, mu_ref in zip(energy_list, mu_ref_list):
        deriv = np.gradient(mu_ref, energy)
        e0 = energy[np.argmax(deriv)]
        e0_values.append(e0)

    if e0_target is None:
        e0_target = e0_values[0]

    aligned = []
    for i, (energy, mu) in enumerate(zip(energy_list, mu_list)):
        shift = e0_target - e0_values[i]
        aligned_energy = energy + shift
        aligned.append((aligned_energy, mu))
        if np.abs(shift) > 0.01:
            print(f"Scan {i}: shifted by {shift:+.3f} eV")

    return aligned
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 기준 포일(reference foil)을 시료와 동시에 항상 측정합니다
- 온도 안정화된 단색화기(liquid nitrogen cooled)를 사용합니다
- 탑오프(top-off) 모드 운전으로 빔 전류를 일정하게 유지합니다
- 실험 시작 전 충분한 열 평형 시간(beam conditioning)을 확보합니다

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.interpolate import interp1d

def correct_energy_drift(energy_list, mu_list, mu_ref_list,
                         e0_standard, merge=True):
    """
    기준 포일 기반 에너지 드리프트 보정 및 선택적 병합.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_list : list of np.ndarray
        각 스캔의 시료 mu 스펙트럼
    mu_ref_list : list of np.ndarray
        각 스캔의 기준 포일 mu 스펙트럼
    e0_standard : float
        기준 원소의 표준 E0 값 (eV)
    merge : bool
        보정 후 병합 여부

    Returns
    -------
    tuple
        (common_energy, corrected_spectra) 또는 병합 시 (common_energy, merged_mu)
    """
    # 1단계: 각 스캔의 기준 포일 E0 결정
    e0_values = []
    for energy, mu_ref in zip(energy_list, mu_ref_list):
        deriv = np.gradient(mu_ref, energy)
        e0 = energy[np.argmax(deriv)]
        e0_values.append(e0)

    # 2단계: 에너지 축 보정
    corrected_spectra = []
    for i, (energy, mu) in enumerate(zip(energy_list, mu_list)):
        shift = e0_standard - e0_values[i]
        corrected_energy = energy + shift
        corrected_spectra.append((corrected_energy, mu))

    # 3단계: 공통 에너지 그리드에 보간
    all_e_min = max(ce[0][0] for ce in corrected_spectra)
    all_e_max = min(ce[0][-1] for ce in corrected_spectra)
    common_energy = np.linspace(all_e_min, all_e_max, len(energy_list[0]))

    interpolated = []
    for corr_e, corr_mu in corrected_spectra:
        f = interp1d(corr_e, corr_mu, kind='cubic', fill_value='extrapolate')
        interpolated.append(f(common_energy))

    if merge:
        merged_mu = np.mean(interpolated, axis=0)
        return common_energy, merged_mu
    else:
        return common_energy, interpolated
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **교차 상관 정렬(Cross-correlation Alignment)** | 신호 처리 | 기준 스펙트럼과의 교차 상관으로 서브픽셀 에너지 이동 결정 |
| **가우시안 프로세스(Gaussian Process)** | 베이지안 | 시간에 따른 E0 드리프트를 GP로 모델링하여 연속적 보정 |
| **딥러닝 스펙트럼 정렬(DL Spectrum Alignment)** | 지도 학습 | 스펙트럼 쌍을 학습하여 에너지 이동을 자동 추정 |

```python
import numpy as np
from scipy.signal import correlate

def cross_correlation_align(energy, mu_reference, mu_target,
                            search_range_eV=2.0):
    """
    교차 상관을 통한 서브픽셀 에너지 정렬.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열
    mu_reference : np.ndarray
        기준 스펙트럼
    mu_target : np.ndarray
        정렬할 스펙트럼
    search_range_eV : float
        탐색 범위 (eV)

    Returns
    -------
    tuple
        (energy_shift, aligned_mu)
    """
    de = energy[1] - energy[0]
    max_shift_pts = int(search_range_eV / de)

    # 1차 미분 사용 (엣지 위치에 민감)
    deriv_ref = np.gradient(mu_reference, energy)
    deriv_target = np.gradient(mu_target, energy)

    # 교차 상관
    cc = correlate(deriv_ref, deriv_target, mode='full')
    mid = len(cc) // 2
    search_slice = slice(mid - max_shift_pts, mid + max_shift_pts + 1)
    cc_region = cc[search_slice]

    # 서브픽셀 정밀도를 위한 포물선 피팅
    peak_idx = np.argmax(cc_region)
    if 1 <= peak_idx < len(cc_region) - 1:
        y0 = cc_region[peak_idx - 1]
        y1 = cc_region[peak_idx]
        y2 = cc_region[peak_idx + 1]
        sub_pixel = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    else:
        sub_pixel = 0.0

    shift_pts = (peak_idx - max_shift_pts) + sub_pixel
    energy_shift = shift_pts * de

    # 보정 적용
    from scipy.interpolate import interp1d
    f = interp1d(energy + energy_shift, mu_target,
                 kind='cubic', fill_value='extrapolate')
    aligned_mu = f(energy)

    return energy_shift, aligned_mu
```

## 미보정 시 영향

- **화학 상태 오판:** E0 이동이 산화 상태(oxidation state) 변화로 잘못 해석될 수 있음 (0.5 eV 이동도 의미 있음)
- **XANES 피크 넓어짐:** 드리프트가 있는 스캔들을 보정 없이 병합하면 흡수단 특성이 인위적으로 넓어짐
- **선형 결합 피팅(LCF) 오류:** 에너지 이동이 성분 비율 결정에 체계적 오차 유발
- **EXAFS 진폭 감쇄:** 에너지 드리프트가 보정 없이 병합된 경우 FT 피크 진폭이 인위적으로 감소

## 관련 자료

- [통계적 노이즈(EXAFS)](statistical_noise_exafs.md)
- [이상 스펙트럼](outlier_spectra.md)
- [고조파 오염](harmonics_contamination.md)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)
- [Athena/Artemis - EXAFS 분석 패키지](https://bruceravel.github.io/demeter/)

## 핵심 요약

> **기준 포일을 항상 동시에 측정하고, 병합 전에 기준 E0에 맞춰 스캔을 정렬하십시오.** 단색화기 결정의 열적 불안정성으로 인한 에너지 드리프트는 XANES 분석에서 화학 상태 오판을 일으킬 수 있으므로, 모든 스캔의 에너지를 기준 포일의 E0에 맞춰 보정한 후 병합해야 합니다.
