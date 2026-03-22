# 방사선 손상(Radiation Damage)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 가끔(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 설명

강한 X-선 빔이 측정 중 시료에 화학적 변화(결합 파괴, 산화 상태 변화, 질량 손실)를 일으킵니다. 이는 연속 스캔에서 흡수단 이동(edge shift), 특성 변화, 또는 진폭 감소로 나타납니다.

방사선 손상(radiation damage)은 X-선 광자가 시료 내 원자와 상호작용하면서 라디칼(radical)을 생성하고, 이것이 화학 반응을 유발하는 과정에서 발생합니다. 유기 시료, 수화 시료, 산화-환원 민감 시료에서 특히 심각하며, 3세대 이상의 고휘도 방사광에서 초점 크기가 작아질수록 선량 밀도(dose density)가 높아져 문제가 악화됩니다.

## 근본 원인

1. **광전자 캐스케이드(Photoelectron Cascade):** X-선 흡수로 생성된 광전자가 주변 원자와 추가 반응을 일으킴
2. **라디칼 생성(Radical Generation):** 물 분자의 분해(radiolysis)로 OH·, H·, e⁻(aq) 등의 반응성 종 생성
3. **결합 파괴(Bond Breaking):** C-S, C-N, S-S 결합 등이 직접 X-선에 의해 파괴됨
4. **산화-환원 변화:** 금속 이온의 산화 상태 변화 (예: Fe³⁺ → Fe²⁺, Mn⁴⁺ → Mn²⁺)
5. **국소적 가열:** 강한 빔에 의한 국소적 온도 상승이 열분해를 유발
6. **질량 손실(Mass Loss):** 유기 시료에서 분해 산물의 증발에 의한 시료 손실

## 빠른 진단

첫 번째와 마지막 스캔을 비교하여 방사선 손상을 빠르게 확인하는 코드:

```python
import numpy as np

def quick_radiation_damage_check(energy, mu_first, mu_last):
    """
    첫 번째와 마지막 스캔을 비교하여 방사선 손상을 확인합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu_first : np.ndarray
        첫 번째 스캔의 mu
    mu_last : np.ndarray
        마지막 스캔의 mu
    """
    # E0 비교
    deriv_first = np.gradient(mu_first, energy)
    deriv_last = np.gradient(mu_last, energy)
    e0_first = energy[np.argmax(deriv_first)]
    e0_last = energy[np.argmax(deriv_last)]
    e0_shift = e0_last - e0_first

    # 백색선 높이 비교
    wl_first = np.max(mu_first)
    wl_last = np.max(mu_last)
    wl_change = (wl_last - wl_first) / wl_first * 100

    print(f"E0 shift: {e0_shift:+.2f} eV")
    print(f"White-line change: {wl_change:+.1f}%")
    if abs(e0_shift) > 0.3 or abs(wl_change) > 5:
        print("WARNING: Radiation damage detected!")
```

## 탐지 방법

### 시각적 지표

- **스캔 간 점진적 변화:** 연속 스캔들을 겹쳐 그리면 흡수단의 체계적 이동이 관찰됨
- **백색선 피크 감소:** 스캔 진행에 따라 백색선 높이가 점진적으로 감소
- **흡수단 이동(Edge Shift):** 산화-환원 변화에 따른 E0의 저에너지 또는 고에너지 방향 이동
- **EXAFS 진폭 변화:** 스캔에 따라 진동 진폭이 감소하는 경향

### 자동 탐지

```python
import numpy as np
from scipy.interpolate import interp1d

def detect_radiation_damage(energy_list, mu_list,
                             sensitivity=0.3):
    """
    다중 스캔에서 방사선 손상을 체계적으로 탐지합니다.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_list : list of np.ndarray
        각 스캔의 mu 배열
    sensitivity : float
        E0 변화 감도 (eV)

    Returns
    -------
    dict
        방사선 손상 탐지 결과
    """
    n_scans = len(mu_list)

    # 각 스캔의 특성 추출
    e0_values = []
    wl_heights = []
    edge_jumps = []

    for energy, mu in zip(energy_list, mu_list):
        # E0 (1차 미분 최대값)
        deriv = np.gradient(mu, energy)
        e0 = energy[np.argmax(deriv)]
        e0_values.append(e0)

        # 백색선 높이
        wl_heights.append(np.max(mu))

        # 흡수단 점프
        pre = np.mean(mu[:30])
        post = np.mean(mu[-30:])
        edge_jumps.append(post - pre)

    e0_values = np.array(e0_values)
    wl_heights = np.array(wl_heights)
    edge_jumps = np.array(edge_jumps)
    scan_numbers = np.arange(n_scans)

    # 선형 추세 분석
    e0_trend = np.polyfit(scan_numbers, e0_values, 1)[0]
    wl_trend = np.polyfit(scan_numbers, wl_heights, 1)[0]
    edge_trend = np.polyfit(scan_numbers, edge_jumps, 1)[0]

    # 총 변화량
    total_e0_shift = e0_values[-1] - e0_values[0]
    total_wl_change = (wl_heights[-1] - wl_heights[0]) / wl_heights[0] * 100

    # 심각도 판정
    if abs(total_e0_shift) > 1.0 or abs(total_wl_change) > 15:
        severity = "critical"
    elif abs(total_e0_shift) > sensitivity or abs(total_wl_change) > 5:
        severity = "major"
    elif abs(total_e0_shift) > 0.1 or abs(total_wl_change) > 2:
        severity = "minor"
    else:
        severity = "none"

    # 손상이 시작되는 스캔 번호 추정
    damage_onset_scan = n_scans  # 기본값: 손상 없음
    for i in range(1, n_scans):
        if abs(e0_values[i] - e0_values[0]) > sensitivity:
            damage_onset_scan = i
            break

    return {
        "e0_values": e0_values.tolist(),
        "wl_heights": wl_heights.tolist(),
        "total_e0_shift_eV": float(total_e0_shift),
        "total_wl_change_pct": float(total_wl_change),
        "e0_trend_eV_per_scan": float(e0_trend),
        "damage_onset_scan": int(damage_onset_scan),
        "severity": severity,
        "usable_scans": int(damage_onset_scan),
    }


def calculate_dose(flux, time_s, beam_area_um2, energy_eV):
    """
    시료에 전달된 흡수 선량을 계산합니다.

    Parameters
    ----------
    flux : float
        빔 플럭스 (photons/s)
    time_s : float
        노출 시간 (s)
    beam_area_um2 : float
        빔 면적 (μm²)
    energy_eV : float
        광자 에너지 (eV)

    Returns
    -------
    float
        선량 (Gray, J/kg) — 물 기준 근사
    """
    eV_to_J = 1.602e-19
    energy_J = energy_eV * eV_to_J
    total_photons = flux * time_s
    total_energy_J = total_photons * energy_J

    # 빔 면적을 m²로 변환
    beam_area_m2 = beam_area_um2 * 1e-12

    # 물 기준 질량 흡수 계수 근사 (간단화)
    # 실제로는 에너지 의존적 계산 필요
    fluence = total_photons / beam_area_m2  # photons/m²
    dose_Gy = total_energy_J / (beam_area_m2 * 1e-3)  # 근사적

    print(f"Estimated dose: {dose_Gy:.1e} Gy")
    print(f"Total photons: {total_photons:.2e}")

    return dose_Gy
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 감쇠기(attenuator)를 사용하여 선량률(dose rate)을 줄입니다
- 빔을 디포커스(defocus)하여 선량 밀도를 분산시킵니다
- 빠른 스캔(quick-EXAFS, QEXAFS)으로 노출 시간을 최소화합니다
- 극저온 냉각(cryogenic cooling, ~100K)으로 라디칼 확산을 억제합니다
- 스캔 사이에 시료를 새로운 위치로 이동시킵니다
- 비활성 분위기(N₂ 또는 He)를 사용합니다

### 보정 — 전통적 방법

```python
import numpy as np

def select_undamaged_scans(energy_list, mu_list,
                            e0_tolerance=0.3, max_wl_change=5.0):
    """
    방사선 손상이 없는 스캔만 선택하여 병합합니다.

    Parameters
    ----------
    energy_list : list of np.ndarray
        각 스캔의 에너지 배열
    mu_list : list of np.ndarray
        각 스캔의 mu 배열
    e0_tolerance : float
        허용 E0 변화 (eV)
    max_wl_change : float
        허용 백색선 변화 (%)

    Returns
    -------
    tuple
        (selected_energies, selected_mus, selected_indices)
    """
    # 첫 번째 스캔을 기준으로 사용
    energy_ref = energy_list[0]
    mu_ref = mu_list[0]
    deriv_ref = np.gradient(mu_ref, energy_ref)
    e0_ref = energy_ref[np.argmax(deriv_ref)]
    wl_ref = np.max(mu_ref)

    selected_energies = []
    selected_mus = []
    selected_indices = []

    for i, (energy, mu) in enumerate(zip(energy_list, mu_list)):
        deriv = np.gradient(mu, energy)
        e0 = energy[np.argmax(deriv)]
        wl = np.max(mu)

        e0_shift = abs(e0 - e0_ref)
        wl_change = abs(wl - wl_ref) / wl_ref * 100

        if e0_shift <= e0_tolerance and wl_change <= max_wl_change:
            selected_energies.append(energy)
            selected_mus.append(mu)
            selected_indices.append(i)
        else:
            print(f"Scan {i} rejected: E0 shift={e0_shift:.2f} eV, "
                  f"WL change={wl_change:.1f}%")

    print(f"\nSelected {len(selected_indices)}/{len(mu_list)} scans")
    return selected_energies, selected_mus, selected_indices


def extrapolate_to_zero_dose(scan_numbers, mu_values_at_feature,
                              method='linear'):
    """
    선량-응답 곡선의 0선량 외삽으로 참 스펙트럼 특성을 추정합니다.

    Parameters
    ----------
    scan_numbers : np.ndarray
        스캔 번호 (선량에 비례)
    mu_values_at_feature : np.ndarray
        특정 에너지에서의 mu 값 시계열
    method : str
        외삽 방법 ('linear' 또는 'exponential')

    Returns
    -------
    float
        0선량 외삽 값
    """
    if method == 'linear':
        coeffs = np.polyfit(scan_numbers, mu_values_at_feature, 1)
        zero_dose_value = coeffs[1]  # y-절편
    elif method == 'exponential':
        # log 변환 후 선형 피팅
        log_vals = np.log(np.abs(mu_values_at_feature) + 1e-10)
        coeffs = np.polyfit(scan_numbers, log_vals, 1)
        zero_dose_value = np.exp(coeffs[1])
    else:
        raise ValueError(f"Unknown method: {method}")

    print(f"Zero-dose extrapolated value: {zero_dose_value:.4f}")
    return float(zero_dose_value)
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **시계열 이상 탐지(Time-series Anomaly Detection)** | 비지도 학습 | 스캔 시계열에서 방사선 손상 시작점을 자동 탐지 |
| **스펙트럼 복원 네트워크(Spectral Restoration)** | 지도 학습 | 손상된 스펙트럼과 참 스펙트럼 쌍으로 학습하여 복원 |
| **가우시안 프로세스 외삽(GP Extrapolation)** | 베이지안 | 선량-응답 곡선의 불확실성을 포함한 0선량 외삽 |

```python
import numpy as np

def auto_detect_damage_onset(feature_series, method='cusum'):
    """
    스캔 특성 시계열에서 방사선 손상 시작점을 자동 탐지합니다.

    Parameters
    ----------
    feature_series : np.ndarray
        스캔별 특성 값 (E0, 백색선 높이 등)
    method : str
        탐지 방법 ('cusum' 또는 'changepoint')

    Returns
    -------
    int
        손상 시작 스캔 인덱스
    """
    if method == 'cusum':
        # 누적합(CUSUM) 변화점 탐지
        mean_val = np.mean(feature_series[:3])  # 초기 3 스캔 기준
        std_val = np.std(feature_series[:3]) if np.std(feature_series[:3]) > 0 else 1e-6

        cusum_pos = np.zeros(len(feature_series))
        cusum_neg = np.zeros(len(feature_series))
        threshold = 4.0 * std_val

        for i in range(1, len(feature_series)):
            deviation = feature_series[i] - mean_val
            cusum_pos[i] = max(0, cusum_pos[i-1] + deviation - 0.5 * std_val)
            cusum_neg[i] = max(0, cusum_neg[i-1] - deviation - 0.5 * std_val)

            if cusum_pos[i] > threshold or cusum_neg[i] > threshold:
                return i

    return len(feature_series)  # 손상 미탐지
```

## 미보정 시 영향

- **화학 상태 오판:** 산화 상태 변화가 시료 본래의 상태가 아닌 빔에 의한 환원/산화를 반영
- **구조 파라미터 오류:** EXAFS 진폭 감소로 배위수 과소 평가
- **재현 불가능한 결과:** 다른 빔라인이나 조건에서 측정하면 다른 결과가 나옴
- **시계열 분석 왜곡:** in-situ/operando 실험에서 시료 변화와 빔 손상을 구분할 수 없게 됨
- **거짓 반응 속도론:** 빔 손상 속도가 실제 화학 반응 속도로 오해될 수 있음

## 관련 자료

- [통계적 노이즈(EXAFS)](statistical_noise_exafs.md)
- [에너지 교정 드리프트](energy_calibration_drift.md)
- [이상 스펙트럼](outlier_spectra.md)
- [Henderson (1990) "Cryo-protection of protein crystals"](https://doi.org/10.1098/rspb.1990.0057)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)

## 핵심 요약

> **첫 번째와 마지막 스캔을 비교하십시오 — 흡수단이 이동하거나 특성이 변하면 방사선 손상이 진행 중이므로 즉시 선량을 줄이십시오.** 방사선 손상은 비가역적 화학 변화이므로, 예방이 가장 효과적입니다. 감쇠기 사용, 빔 디포커스, 극저온 냉각, 스캔 간 시료 이동 등을 통해 선량을 관리하고, 손상 여부를 실시간으로 모니터링해야 합니다.
