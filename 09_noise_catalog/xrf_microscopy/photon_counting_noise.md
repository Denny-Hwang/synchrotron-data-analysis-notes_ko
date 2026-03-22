# 광자 계수 노이즈(Photon Counting Noise)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 통계적(Statistical) |
| **심각도** | 주요(Major) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 쉬움(Easy) |

## 설명

XRF 검출기에서 이산적 광자 계수(discrete photon counting)로 인해 발생하는 근본적인 포아송 노이즈(Poisson noise)입니다. 저농도 원소는 형광 광자 수가 적어 상대적 노이즈가 높아집니다. 신호 대 잡음비(SNR)는 총 계수 N에 대해 **SNR = √N**으로 스케일링됩니다.

이 노이즈는 모든 XRF 측정에 본질적으로 존재하며, 특히 미량 원소(trace element) 분석에서 정량적 신뢰성에 직접적인 영향을 미칩니다. 예를 들어 100 카운트의 경우 SNR = 10 (10% 상대 오차), 10,000 카운트의 경우 SNR = 100 (1% 상대 오차)입니다.

## 근본 원인

X선 형광의 양자적 특성에서 비롯됩니다. 검출된 각 광자는 **포아송 통계(Poisson statistics)**를 따르는 이산적 확률 사건입니다.

- **SNR = √N**: 총 카운트 수의 제곱근에 비례하므로, 소수의 카운트만 갖는 미량 원소는 통계적 정밀도가 낮습니다.
- 체류 시간(dwell time)이 짧을수록, 빔 세기가 낮을수록, 원소 농도가 낮을수록 노이즈가 더 심해집니다.
- 이 노이즈는 제거할 수 없으며, 오직 더 많은 광자를 모아서 줄일 수만 있습니다.

## 빠른 진단

픽셀별 총 카운트 통계와 SNR 맵을 통해 빠르게 진단할 수 있습니다.

```python
import numpy as np

def quick_poisson_check(xrf_map):
    """
    XRF 맵의 포아송 노이즈 수준을 빠르게 진단합니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D XRF elemental map (counts).

    Returns
    -------
    dict with mean counts, expected SNR, and relative noise.
    """
    mean_counts = np.mean(xrf_map)
    expected_snr = np.sqrt(mean_counts)
    relative_noise = 1.0 / expected_snr if expected_snr > 0 else np.inf

    print(f"Mean counts per pixel: {mean_counts:.1f}")
    print(f"Expected SNR (√N):     {expected_snr:.1f}")
    print(f"Relative noise:        {relative_noise:.1%}")

    return {
        "mean_counts": mean_counts,
        "expected_snr": expected_snr,
        "relative_noise": relative_noise,
    }
```

## 탐지 방법

### 시각적 지표

- 저농도 원소 맵에서 "소금과 후추(salt-and-pepper)" 형태의 노이즈 패턴
- 주요 원소(Ca, Fe 등) 맵은 깨끗하지만, 미량 원소(As, Se 등) 맵은 노이즈가 심함
- 동일 영역의 반복 측정 시 픽셀 값의 확률적 변동

### 자동 탐지

```python
import numpy as np
from scipy import stats

def assess_xrf_counting_statistics(xrf_cube, element_names=None):
    """
    XRF 데이터 큐브에 대한 광자 계수 통계를 평가합니다.

    Parameters
    ----------
    xrf_cube : np.ndarray
        Shape (n_elements, ny, nx) — 원소별 맵 배열.
    element_names : list of str, optional
        각 채널에 해당하는 원소 이름.

    Returns
    -------
    report : list of dict
        각 원소별 통계 보고서.
    """
    n_elements = xrf_cube.shape[0]
    if element_names is None:
        element_names = [f"Ch{i}" for i in range(n_elements)]

    report = []
    for i in range(n_elements):
        elem_map = xrf_cube[i]
        total_counts = np.sum(elem_map)
        mean_counts = np.mean(elem_map)
        var_counts = np.var(elem_map)

        # Poisson 통계에서 분산 ≈ 평균이어야 함
        variance_ratio = var_counts / mean_counts if mean_counts > 0 else np.inf

        # 포아송 적합도 검정 (대표 픽셀 샘플링)
        flat = elem_map.flatten()
        sample = flat[np.random.choice(len(flat), min(1000, len(flat)), replace=False)]
        sample_int = sample.astype(int)

        expected_snr = np.sqrt(mean_counts)

        # SNR 맵 생성
        snr_map = np.where(elem_map > 0, np.sqrt(elem_map), 0)

        info = {
            "element": element_names[i],
            "mean_counts": mean_counts,
            "variance": var_counts,
            "variance_ratio": variance_ratio,
            "expected_snr": expected_snr,
            "min_snr": np.min(snr_map[snr_map > 0]) if np.any(snr_map > 0) else 0,
            "snr_map": snr_map,
        }
        report.append(info)

        status = "OK" if expected_snr > 10 else "LOW" if expected_snr > 3 else "POOR"
        print(f"[{status}] {element_names[i]}: "
              f"mean={mean_counts:.1f}, SNR={expected_snr:.1f}, "
              f"var/mean={variance_ratio:.2f}")

    return report
```

## 해결 및 완화

### 예방 (데이터 수집 전)

1. **체류 시간 증가** — SNR은 √(dwell_time)로 증가하므로, 체류 시간을 4배로 늘리면 SNR이 2배 향상됩니다.
2. **반복 스캔** — 동일 영역을 K번 반복 측정 후 평균을 취하면 SNR이 √K배 향상됩니다.
3. **빔 세기 최적화** — 언듈레이터 갭, 슬릿 크기를 조정하여 플럭스를 최대화합니다 (데드타임 포화 주의).
4. **검출기 기하학 최적화** — 검출기를 시료에 더 가까이 배치하거나 대면적 검출기를 사용합니다.

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.ndimage import uniform_filter, gaussian_filter

def spatial_binning(xrf_map, bin_factor=2):
    """
    공간적 비닝으로 카운트를 합산하여 SNR을 향상시킵니다.
    해상도가 bin_factor만큼 감소하지만, SNR은 bin_factor만큼 향상됩니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D elemental map.
    bin_factor : int
        Binning factor (2 = 2x2 binning).

    Returns
    -------
    binned_map : np.ndarray
        Binned map with improved statistics.
    """
    ny, nx = xrf_map.shape
    ny_new = ny // bin_factor
    nx_new = nx // bin_factor

    # Trim to divisible size
    trimmed = xrf_map[:ny_new * bin_factor, :nx_new * bin_factor]

    # Reshape and sum
    binned = trimmed.reshape(ny_new, bin_factor, nx_new, bin_factor).sum(axis=(1, 3))

    print(f"Binning {bin_factor}x{bin_factor}: "
          f"SNR improvement ≈ {bin_factor:.1f}x, "
          f"resolution {ny}x{nx} → {ny_new}x{nx_new}")

    return binned


def repeat_scan_average(scan_list):
    """
    반복 스캔의 평균을 구합니다.

    Parameters
    ----------
    scan_list : list of np.ndarray
        동일 영역의 반복 측정 맵 목록.

    Returns
    -------
    averaged : np.ndarray
        평균화된 맵.
    """
    stacked = np.stack(scan_list, axis=0)
    averaged = np.mean(stacked, axis=0)
    n_scans = len(scan_list)
    print(f"Averaged {n_scans} scans: SNR improvement ≈ {np.sqrt(n_scans):.2f}x")
    return averaged


def gaussian_denoise(xrf_map, sigma=1.0):
    """
    가우시안 필터를 이용한 간단한 디노이징.
    공간 해상도와 노이즈 사이의 트레이드오프가 있습니다.

    Parameters
    ----------
    xrf_map : np.ndarray
        2D elemental map.
    sigma : float
        Gaussian kernel standard deviation in pixels.

    Returns
    -------
    smoothed : np.ndarray
    """
    smoothed = gaussian_filter(xrf_map.astype(float), sigma=sigma)
    return smoothed
```

### 보정 — AI/ML 방법

**딥 잔차 네트워크(Deep Residual Network)**를 사용한 XRF 디노이징이 최근 연구에서 우수한 성능을 보여주고 있습니다.

- **Noise2Noise 접근법**: 깨끗한 참조 데이터 없이 노이즈 데이터 쌍만으로 학습 가능
- **딥 잔차 XRF 네트워크**: 잔차 학습(residual learning)을 통해 노이즈만 학습하여 제거
- 전통적 가우시안/메디안 필터 대비 공간 해상도 보존이 우수함

자세한 내용은 [딥 잔차 XRF 리뷰](../../04_publications/ai_ml_synchrotron/review_deep_residual_xrf_2023.md)를 참조하세요.

## 미보정 시 영향

- **미량 원소 정량의 신뢰성 저하** — 낮은 카운트의 원소는 농도 추정에 큰 불확실성이 동반됩니다.
- **노이즈가 심한 원소 맵** — 공간 분포 해석이 어렵습니다.
- **후속 분석 오류 전파** — 클러스터링, 분류 등 다운스트림 분석에 노이즈가 전파됩니다.
- **거짓 상관관계** — 노이즈가 심한 채널 간 허위 상관/반상관이 발생할 수 있습니다.

## 관련 자료

- [XRF EDA 노트북](../../06_data_structures/eda/xrf_eda.md) — XRF 데이터 탐색적 분석 및 노이즈 진단
- [딥 잔차 XRF 리뷰](../../04_publications/ai_ml_synchrotron/review_deep_residual_xrf_2023.md) — AI/ML 기반 XRF 디노이징 논문 리뷰

## 핵심 요약

> **SNR은 √(dwell_time)으로 향상됩니다** — 체류 시간을 2배로 늘려도 SNR은 약 41%만 향상됩니다. 미량 원소의 적절한 통계를 확보하려면 체류 시간, 반복 스캔, 또는 공간 비닝 전략을 신중히 계획해야 합니다. 수집 전에 필요한 최소 카운트 수를 계산하세요.

---
