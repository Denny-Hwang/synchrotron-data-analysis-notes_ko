# 이상 스펙트럼(Outlier Spectra)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 통계적(Statistical) |
| **심각도** | 경미(Minor) |
| **빈도** | 가끔(Occasional) |
| **탐지 난이도** | 쉬움(Easy) |

## 설명

빔 덤프(beam dump) 중간 스캔, 단색화기 글리치(monochromator glitch), 시료 이동, 또는 검출기 오작동으로 인해 평균에서 크게 벗어나는 개별 스캔입니다. 이상 스캔을 병합 데이터에 포함하면 데이터 품질이 저하됩니다.

이상 스펙트럼(outlier spectra)은 다양한 원인으로 발생할 수 있으며, 단일 스캔 단위로 나타나는 경우가 많습니다. 문제는 이러한 이상 스캔이 병합(merge) 과정에서 감지되지 않으면 최종 데이터의 SNR을 오히려 악화시키고, 구조 분석에 스퓨리어스(spurious) 특성을 도입할 수 있다는 점입니다.

## 근본 원인

1. **빔 덤프(Beam Dump):** 저장 링의 전자빔 손실로 스캔 중간에 광자 플럭스가 갑자기 사라짐
2. **단색화기 글리치(Monochromator Glitch):** 특정 에너지에서 결정의 다중 회절(multiple diffraction)로 인한 순간적 강도 변동
3. **시료 이동:** 진동이나 열팽창으로 시료가 빔 경로에서 이탈
4. **검출기 포화 또는 오작동:** 검출기의 데드타임(dead time) 초과나 전자적 오류
5. **이온 챔버 문제:** 이온 챔버 가스 기포나 방전으로 인한 순간적 신호 이상
6. **빔 위치 불안정:** 빔 위치의 급격한 변화로 시료 조사 조건이 달라짐

## 빠른 진단

개별 스캔의 이상 여부를 빠르게 확인하는 코드:

```python
import numpy as np

def quick_outlier_check(chi_list, threshold=3.0):
    """
    개별 스캔의 이상 여부를 빠르게 확인합니다.

    Parameters
    ----------
    chi_list : list of np.ndarray
        개별 chi(k) 스캔 리스트
    threshold : float
        이상치 판별 임계값 (MAD 기준 배수)
    """
    chi_array = np.array(chi_list)
    median_chi = np.median(chi_array, axis=0)

    # 각 스캔과 중앙값의 차이
    deviations = np.array([np.sqrt(np.mean((c - median_chi)**2))
                           for c in chi_list])
    mad = np.median(np.abs(deviations - np.median(deviations))) * 1.4826
    scores = (deviations - np.median(deviations)) / max(mad, 1e-10)

    outliers = np.where(scores > threshold)[0]
    print(f"Outlier scans: {outliers.tolist()}")
    print(f"Scores: {scores.round(2).tolist()}")
    return outliers
```

## 탐지 방법

### 시각적 지표

- **개별 스캔 오버레이:** 모든 스캔을 겹쳐 그리면 이상 스캔이 명확히 구분됨
- **차이 플롯:** 각 스캔과 평균 사이의 차이(잔차)를 그리면 이상 스캔의 잔차가 비정상적으로 큼
- **chi(k) 위상 불일치:** 이상 스캔의 EXAFS 진동이 다른 스캔과 위상이 맞지 않음

### 자동 탐지

```python
import numpy as np
from scipy.stats import chi2

def detect_outlier_spectra(energy_common, mu_list,
                           method='mad', threshold=3.0):
    """
    다중 스캔에서 이상 스펙트럼을 탐지합니다.

    Parameters
    ----------
    energy_common : np.ndarray
        공통 에너지 그리드
    mu_list : list of np.ndarray
        개별 스캔의 mu 배열 리스트
    method : str
        탐지 방법 ('mad', 'pca', 'chi2')
    threshold : float
        이상치 판별 임계값

    Returns
    -------
    dict
        이상 스캔 탐지 결과
    """
    mu_array = np.array(mu_list)
    n_scans, n_points = mu_array.shape

    if method == 'mad':
        # MAD(Median Absolute Deviation) 기반 탐지
        median_spectrum = np.median(mu_array, axis=0)

        # 각 스캔의 RMS 편차
        rms_deviations = np.sqrt(np.mean((mu_array - median_spectrum)**2,
                                          axis=1))

        # 강건한 통계로 이상치 판별
        med_dev = np.median(rms_deviations)
        mad_dev = np.median(np.abs(rms_deviations - med_dev)) * 1.4826

        if mad_dev > 0:
            scores = (rms_deviations - med_dev) / mad_dev
        else:
            scores = np.zeros(n_scans)

        outlier_mask = scores > threshold

    elif method == 'pca':
        # PCA 기반 탐지 — 주성분 공간에서의 이상치
        from sklearn.decomposition import PCA

        pca = PCA(n_components=min(5, n_scans - 1))
        scores_pca = pca.fit_transform(mu_array)

        # Mahalanobis 거리 기반 이상치 탐지
        cov = np.cov(scores_pca.T)
        try:
            cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            cov_inv = np.linalg.pinv(cov)

        mean_scores = np.mean(scores_pca, axis=0)
        mahal_dist = np.array([
            np.sqrt((s - mean_scores) @ cov_inv @ (s - mean_scores))
            for s in scores_pca
        ])

        # chi2 분포 기반 임계값
        p_threshold = 0.01
        chi2_threshold = np.sqrt(chi2.ppf(1 - p_threshold,
                                           pca.n_components_))

        scores = mahal_dist
        outlier_mask = mahal_dist > chi2_threshold

    elif method == 'chi2':
        # chi-squared 기반 탐지
        mean_spectrum = np.mean(mu_array, axis=0)
        std_spectrum = np.std(mu_array, axis=0)
        std_spectrum = np.where(std_spectrum > 1e-10, std_spectrum, 1e-10)

        chi2_values = np.sum(
            ((mu_array - mean_spectrum) / std_spectrum)**2, axis=1
        )

        # 기대 chi2 값과 비교
        expected_chi2 = n_points
        scores = chi2_values / expected_chi2
        outlier_mask = scores > threshold

    else:
        raise ValueError(f"Unknown method: {method}")

    outlier_indices = np.where(outlier_mask)[0]

    # 이상 유형 분류
    outlier_types = {}
    for idx in outlier_indices:
        scan = mu_array[idx]
        median_spec = np.median(mu_array, axis=0)
        diff = scan - median_spec

        if np.any(np.abs(diff) > 10 * np.std(mu_array, axis=0)):
            outlier_types[int(idx)] = "spike_or_dropout"
        elif np.mean(np.abs(diff[:n_points//4])) > np.mean(np.abs(diff)):
            outlier_types[int(idx)] = "pre_edge_anomaly"
        else:
            outlier_types[int(idx)] = "general_deviation"

    return {
        "outlier_indices": outlier_indices.tolist(),
        "scores": scores.tolist(),
        "n_outliers": int(np.sum(outlier_mask)),
        "outlier_types": outlier_types,
        "method": method,
    }


def iterative_outlier_removal(mu_list, max_iterations=5,
                               threshold=3.0):
    """
    반복적 이상치 제거 후 병합합니다.

    Parameters
    ----------
    mu_list : list of np.ndarray
        개별 스캔 리스트
    max_iterations : int
        최대 반복 횟수
    threshold : float
        이상치 제거 임계값

    Returns
    -------
    tuple
        (merged_mu, kept_indices, removed_indices)
    """
    remaining = list(range(len(mu_list)))
    removed = []

    for iteration in range(max_iterations):
        if len(remaining) < 3:
            break

        current_array = np.array([mu_list[i] for i in remaining])
        median_spec = np.median(current_array, axis=0)

        rms_devs = np.sqrt(np.mean(
            (current_array - median_spec)**2, axis=1
        ))

        med = np.median(rms_devs)
        mad = np.median(np.abs(rms_devs - med)) * 1.4826

        if mad < 1e-10:
            break

        scores = (rms_devs - med) / mad
        worst = np.argmax(scores)

        if scores[worst] > threshold:
            removed_idx = remaining.pop(worst)
            removed.append(removed_idx)
            print(f"Iteration {iteration + 1}: removed scan {removed_idx} "
                  f"(score={scores[worst]:.2f})")
        else:
            break

    # 최종 병합
    kept_array = np.array([mu_list[i] for i in remaining])
    merged = np.mean(kept_array, axis=0)

    print(f"\nKept {len(remaining)}/{len(mu_list)} scans, "
          f"removed {len(removed)}")

    return merged, remaining, removed
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 빔라인 상태(빔 전류, 검출기 상태)를 모니터링합니다
- 빔 안정성이 확보된 후 데이터를 수집합니다
- 자동 빔 위치 보정(feedback) 시스템을 가동합니다
- 충분한 수의 반복 스캔을 수집하여 이상 스캔 제거 여유를 확보합니다

### 보정 — 전통적 방법

```python
import numpy as np

def robust_merge(mu_list, weights=None, sigma_clip=3.0):
    """
    시그마 클리핑을 적용한 강건한 스캔 병합.

    Parameters
    ----------
    mu_list : list of np.ndarray
        개별 스캔 리스트
    weights : np.ndarray, optional
        스캔별 가중치
    sigma_clip : float
        클리핑 임계값

    Returns
    -------
    tuple
        (merged_mu, stderr)
    """
    mu_array = np.array(mu_list)
    n_scans, n_points = mu_array.shape

    merged = np.zeros(n_points)
    stderr = np.zeros(n_points)

    for j in range(n_points):
        values = mu_array[:, j]

        # 반복적 시그마 클리핑
        mask = np.ones(n_scans, dtype=bool)
        for _ in range(3):
            med = np.median(values[mask])
            mad = np.median(np.abs(values[mask] - med)) * 1.4826
            if mad > 0:
                new_mask = np.abs(values - med) < sigma_clip * mad
                mask = mask & new_mask

        if np.sum(mask) > 0:
            merged[j] = np.mean(values[mask])
            if np.sum(mask) > 1:
                stderr[j] = np.std(values[mask]) / np.sqrt(np.sum(mask))
        else:
            merged[j] = np.median(values)

    return merged, stderr


def weighted_merge_by_quality(mu_list, quality_scores):
    """
    품질 점수 기반 가중 병합.

    Parameters
    ----------
    mu_list : list of np.ndarray
        개별 스캔 리스트
    quality_scores : np.ndarray
        각 스캔의 품질 점수 (높을수록 좋음)

    Returns
    -------
    np.ndarray
        가중 병합된 스펙트럼
    """
    quality_scores = np.array(quality_scores)
    weights = quality_scores / np.sum(quality_scores)

    mu_array = np.array(mu_list)
    merged = np.average(mu_array, axis=0, weights=weights)

    print("Weights per scan:")
    for i, w in enumerate(weights):
        print(f"  Scan {i}: weight = {w:.3f}")

    return merged
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **Isolation Forest** | 비지도 학습 | 다차원 특성 공간에서 이상 스캔을 자동 격리 |
| **오토인코더(Autoencoder)** | 비지도 학습 | 재구성 오차가 큰 스캔을 이상치로 판별 |
| **DBSCAN 클러스터링** | 비지도 학습 | 밀도 기반 클러스터링으로 소수 클러스터를 이상치로 분류 |

```python
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def isolation_forest_outlier_detection(mu_list, contamination=0.1):
    """
    Isolation Forest를 사용한 이상 스캔 탐지.

    Parameters
    ----------
    mu_list : list of np.ndarray
        개별 스캔 리스트
    contamination : float
        예상 이상치 비율

    Returns
    -------
    dict
        탐지 결과
    """
    mu_array = np.array(mu_list)

    # 특성 추출 (차원 축소)
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(10, len(mu_list) - 1))
    features = pca.fit_transform(mu_array)

    # 스케일링
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Isolation Forest
    clf = IsolationForest(contamination=contamination,
                          random_state=42)
    predictions = clf.fit_predict(features_scaled)
    scores = clf.score_samples(features_scaled)

    outlier_indices = np.where(predictions == -1)[0]

    print(f"Detected {len(outlier_indices)} outlier scans: "
          f"{outlier_indices.tolist()}")

    return {
        "outlier_indices": outlier_indices.tolist(),
        "anomaly_scores": scores.tolist(),
        "predictions": predictions.tolist(),
    }
```

## 미보정 시 영향

- **병합 데이터 품질 저하:** 이상 스캔이 평균을 왜곡하여 SNR이 오히려 감소
- **스퓨리어스 특성 도입:** 글리치나 스파이크가 병합 스펙트럼에 잔존
- **구조 파라미터 불확실성 증가:** EXAFS 피팅에서 오차 범위가 불필요하게 넓어짐
- **재현성 문제:** 이상 스캔 포함 여부에 따라 결과가 달라질 수 있음

## 관련 자료

- [통계적 노이즈(EXAFS)](statistical_noise_exafs.md)
- [에너지 교정 드리프트](energy_calibration_drift.md)
- [방사선 손상](radiation_damage.md)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)

## 핵심 요약

> **병합 전에 항상 모든 개별 스캔을 플롯하고, 통계적 기준을 사용하여 이상치를 제거하십시오.** 이상 스캔은 빔 덤프, 검출기 오류 등 다양한 원인으로 발생하며, 포함 시 병합 데이터의 SNR을 오히려 악화시킵니다. MAD 기반 강건한 통계 또는 PCA 기반 탐지를 병합 전 표준 절차로 적용하십시오.
