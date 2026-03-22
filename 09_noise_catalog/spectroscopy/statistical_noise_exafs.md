# 통계적 노이즈(EXAFS) (Statistical Noise in EXAFS)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 통계적(Statistical) |
| **심각도** | 주요(Major) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 쉬움(Easy) |

## 설명

EXAFS 진동(oscillation)은 chi(k)에서 높은 k 값(>10-12 Å⁻¹)에서 신호 진폭의 감소와 푸아송 계수 통계(Poisson counting statistics)의 결합으로 인해 점점 더 노이즈가 심해집니다. EXAFS 분석에서 사용되는 k² 또는 k³ 가중(weighting)은 고k 영역의 노이즈를 증폭시킵니다.

이는 EXAFS의 근본적인 한계로, X-선 흡수 미세구조(X-ray Absorption Fine Structure) 신호의 진폭이 k가 증가함에 따라 지수적으로 감소하는 반면, 통계적 노이즈는 상대적으로 일정하게 유지되기 때문입니다. k-가중을 적용하면 고k 영역에서 신호 대 잡음비(SNR)가 더욱 악화됩니다.

## 근본 원인

1. **푸아송 계수 통계:** X-선 광자 계수는 본질적으로 √N의 불확실성을 가지며, 광자 수가 적은 고에너지(고k) 영역에서 상대 오차가 증가
2. **EXAFS 신호의 자연 감쇠:** 디바이-왈러 인자(Debye-Waller factor) e^(-2σ²k²)에 의한 지수적 신호 감소
3. **k-가중 증폭:** k² 또는 k³ 가중이 고k 영역의 노이즈를 각각 k⁴ 또는 k⁶으로 증폭
4. **흡수 계수 감소:** 흡수 단(absorption edge) 이후 에너지가 증가하면 흡수 계수(μ)가 감소하여 신호 대비 감소
5. **검출기 비효율:** 고에너지 광자에 대한 검출기의 양자 효율(quantum efficiency) 감소

## 빠른 진단

chi(k) 데이터에서 고k 영역의 노이즈 수준을 빠르게 평가하는 코드:

```python
import numpy as np

# chi(k) 데이터에서 SNR 추정
k = np.linspace(0, 16, 800)  # k 범위
chi_k = exafs_data  # 실험 chi(k) 데이터

# 고k 영역(12-16 Å⁻¹)에서 노이즈 추정
high_k_mask = k > 12
noise_level = np.std(chi_k[high_k_mask])
signal_level = np.max(np.abs(chi_k[(k > 2) & (k < 8)]))
snr_estimate = signal_level / noise_level
print(f"Estimated SNR: {snr_estimate:.1f}")
print(f"High-k noise level: {noise_level:.6f}")
if snr_estimate < 10:
    print("WARNING: Low SNR — consider merging more scans")
```

이 코드는 고k 영역의 표준편차를 노이즈로, 저k 영역의 최대 진폭을 신호로 사용하여 대략적인 SNR을 추정합니다.

## 탐지 방법

### 시각적 지표

- **chi(k) 플롯:** 고k 영역에서 진동 패턴이 무작위 노이즈에 묻힘
- **k²·chi(k) 또는 k³·chi(k) 플롯:** k-가중 적용 시 고k 영역의 노이즈가 과도하게 증폭되어 나타남
- **FT(푸리에 변환) 크기:** R-공간에서 물리적으로 의미 없는 고주파 피크가 나타남

### 자동 탐지

```python
import numpy as np
from scipy.signal import savgol_filter

def assess_exafs_noise(k, chi_k, k_weight=2, window_size=21):
    """
    EXAFS chi(k) 데이터의 노이즈 수준을 평가합니다.

    Parameters
    ----------
    k : np.ndarray
        k 값 배열 (Å⁻¹)
    chi_k : np.ndarray
        chi(k) 배열
    k_weight : int
        k-가중 지수 (기본값: 2)
    window_size : int
        Savitzky-Golay 필터 창 크기 (기본값: 21)

    Returns
    -------
    dict
        노이즈 평가 결과를 담은 딕셔너리
    """
    # k-가중 적용
    chi_kw = chi_k * k ** k_weight

    # Savitzky-Golay 필터로 평활화된 신호 추정
    if len(chi_kw) > window_size:
        smooth = savgol_filter(chi_kw, window_size, polyorder=3)
    else:
        smooth = chi_kw

    # 잔차(노이즈 추정)
    residual = chi_kw - smooth

    # k 범위별 노이즈 평가
    regions = {
        "low_k": (2, 6),
        "mid_k": (6, 10),
        "high_k": (10, 15),
    }

    noise_by_region = {}
    for name, (k_min, k_max) in regions.items():
        mask = (k >= k_min) & (k <= k_max)
        if np.sum(mask) > 5:
            noise_by_region[name] = float(np.std(residual[mask]))
        else:
            noise_by_region[name] = None

    # 전체 노이즈 수준 평가
    overall_noise = float(np.std(residual[k > 2]))

    # k_max 추정: 노이즈가 신호를 초과하는 지점
    usable_k_max = k[-1]
    for ki in np.arange(6, k[-1], 0.5):
        mask = (k >= ki - 1) & (k <= ki + 1)
        if np.sum(mask) > 3:
            local_signal = np.std(smooth[mask])
            local_noise = np.std(residual[mask])
            if local_noise > local_signal and local_signal > 0:
                usable_k_max = ki
                break

    # 심각도 판정
    if noise_by_region.get("high_k") is not None and noise_by_region.get("low_k") is not None:
        noise_ratio = noise_by_region["high_k"] / max(noise_by_region["low_k"], 1e-10)
        if noise_ratio > 20:
            severity = "critical"
        elif noise_ratio > 5:
            severity = "major"
        else:
            severity = "minor"
    else:
        severity = "unknown"

    return {
        "noise_by_region": noise_by_region,
        "overall_noise": overall_noise,
        "usable_k_max": float(usable_k_max),
        "severity": severity,
        "noise_ratio_high_to_low": float(noise_ratio) if severity != "unknown" else None,
    }


def estimate_scans_needed(current_snr, target_snr):
    """
    목표 SNR 달성에 필요한 추가 스캔 수를 추정합니다.
    SNR은 스캔 수의 제곱근에 비례합니다.

    Parameters
    ----------
    current_snr : float
        현재 SNR (단일 스캔 기준)
    target_snr : float
        목표 SNR

    Returns
    -------
    int
        필요한 총 스캔 수
    """
    n_scans = int(np.ceil((target_snr / current_snr) ** 2))
    return n_scans
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 충분한 수의 반복 스캔을 수집합니다 (SNR ∝ √N)
- 계수 시간(counting time)을 최적화합니다 — 특히 고k 영역에서 더 긴 계수 시간 사용
- 이온 챔버(ion chamber) 가스 조성을 에너지 범위에 맞게 최적화합니다
- 형광(fluorescence) 모드의 경우 다중 소자 검출기(multi-element detector)를 사용합니다

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.fft import fft, ifft

def merge_scans(k, chi_list, weights=None):
    """
    다중 EXAFS 스캔을 병합하여 SNR을 향상시킵니다.

    Parameters
    ----------
    k : np.ndarray
        공통 k 그리드
    chi_list : list of np.ndarray
        개별 chi(k) 스캔 리스트
    weights : np.ndarray, optional
        각 스캔의 가중치 (기본값: 균등 가중)

    Returns
    -------
    tuple
        (merged_chi, stderr) 병합된 chi(k)와 표준오차
    """
    chi_array = np.array(chi_list)
    n_scans = chi_array.shape[0]

    if weights is None:
        weights = np.ones(n_scans) / n_scans
    else:
        weights = weights / np.sum(weights)

    # 가중 평균
    merged_chi = np.average(chi_array, axis=0, weights=weights)

    # 표준오차 추정
    if n_scans > 1:
        variance = np.average((chi_array - merged_chi) ** 2, axis=0, weights=weights)
        stderr = np.sqrt(variance / n_scans)
    else:
        stderr = np.zeros_like(merged_chi)

    return merged_chi, stderr


def fourier_filter_noise(k, chi_k, r_min=1.0, r_max=6.0, k_weight=2):
    """
    푸리에 필터링을 통해 R-공간에서 물리적 범위 외의 기여를 제거합니다.

    Parameters
    ----------
    k : np.ndarray
        k 배열
    chi_k : np.ndarray
        chi(k) 배열
    r_min : float
        R-공간 최소 범위 (Å)
    r_max : float
        R-공간 최대 범위 (Å)
    k_weight : int
        k-가중 지수

    Returns
    -------
    np.ndarray
        필터링된 chi(k)
    """
    # k-가중 적용 후 FT
    chi_kw = chi_k * k ** k_weight

    # 균일 간격 k 그리드로 보간
    dk = 0.05
    k_uniform = np.arange(k[0], k[-1], dk)
    chi_interp = np.interp(k_uniform, k, chi_kw)

    # FFT 수행
    n_fft = 2048
    chi_padded = np.zeros(n_fft)
    chi_padded[:len(chi_interp)] = chi_interp

    ft = fft(chi_padded)
    r = np.fft.fftfreq(n_fft, d=dk) * np.pi

    # R-공간 윈도우 적용
    window = np.zeros(n_fft)
    r_abs = np.abs(r)
    window[(r_abs >= r_min) & (r_abs <= r_max)] = 1.0

    # 역 FT
    filtered_ft = ft * window
    chi_filtered = np.real(ifft(filtered_ft))[:len(chi_interp)]

    # k-가중 제거
    k_nonzero = np.where(k_uniform > 0.1, k_uniform, 0.1)
    chi_filtered = chi_filtered / k_nonzero ** k_weight

    return np.interp(k, k_uniform, chi_filtered)
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **딥러닝 디노이징(DL Denoising)** | 지도 학습 | 노이즈가 있는 chi(k)를 고품질 기준 데이터와 쌍으로 학습하여 노이즈 제거 |
| **웨이블릿 임계값 적용(Wavelet Thresholding)** | 비지도 학습 | 웨이블릿 변환 후 노이즈에 해당하는 고주파 계수를 제거 |
| **가우시안 프로세스 회귀(GPR)** | 베이지안 | k 의존적 노이즈 수준을 모델링하여 최적의 평활화 수행 |

```python
import numpy as np

# 웨이블릿 디노이징 예시 (PyWavelets 사용)
import pywt

def wavelet_denoise_exafs(chi_k, wavelet='db4', level=4):
    """
    웨이블릿 임계값 적용을 통한 EXAFS 디노이징.

    Parameters
    ----------
    chi_k : np.ndarray
        노이즈가 있는 chi(k)
    wavelet : str
        웨이블릿 유형
    level : int
        분해 레벨

    Returns
    -------
    np.ndarray
        디노이징된 chi(k)
    """
    coeffs = pywt.wavedec(chi_k, wavelet, level=level)

    # 각 레벨의 상세 계수에 soft thresholding 적용
    for i in range(1, len(coeffs)):
        sigma = np.median(np.abs(coeffs[i])) / 0.6745
        threshold = sigma * np.sqrt(2 * np.log(len(chi_k)))
        coeffs[i] = pywt.threshold(coeffs[i], threshold, mode='soft')

    return pywt.waverec(coeffs, wavelet)[:len(chi_k)]
```

## 미보정 시 영향

- **배위수(Coordination Number) 오류:** 고k 노이즈가 FT 피크 진폭에 영향을 미쳐 배위수 결정에 체계적 오류 발생
- **결합 거리(Bond Distance) 불확실성 증가:** R-공간에서 피크 위치의 불확실성이 증가
- **디바이-왈러 인자 과대 평가:** 노이즈가 구조적 무질서(disorder)로 잘못 해석될 수 있음
- **스퓨리어스 피크(Spurious Peaks):** FT에서 물리적으로 의미 없는 거짓 피크가 나타남
- **피팅 결과 불안정:** 구조 파라미터 피팅 시 수렴이 불안정하거나 비물리적 결과 도출

## 관련 자료

- [에너지 교정 드리프트](energy_calibration_drift.md)
- [이상 스펙트럼](outlier_spectra.md)
- [자기흡수(XAS)](self_absorption_xas.md)
- [방사선 손상](radiation_damage.md)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)
- [Demeter - EXAFS 분석 패키지](https://bruceravel.github.io/demeter/)

## 핵심 요약

> **필요한 스캔 수는 SNR²에 비례합니다 — 품질을 2배로 높이려면 4배의 스캔이 필요합니다.** EXAFS의 통계적 노이즈는 고k 영역에서 본질적으로 증가하므로, 충분한 반복 스캔 병합, 최적의 k-가중 선택, 그리고 적절한 푸리에 필터링을 통해 신뢰할 수 있는 구조 정보를 추출해야 합니다.
