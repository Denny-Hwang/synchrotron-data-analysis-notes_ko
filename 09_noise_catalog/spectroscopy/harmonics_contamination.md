# 고조파 오염(Harmonics Contamination)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 가끔(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 설명

단색화기 결정의 고차 브래그 반사(higher-order Bragg reflections, 2차, 3차 고조파)가 공칭 에너지(nominal energy)의 2배, 3배 에너지의 광자를 통과시킵니다. 이로 인해 잘못된 에너지의 광자가 측정을 오염시키며, XANES 특성(feature)이 감쇠되고 흡수단 형태가 왜곡됩니다.

고조파 오염은 특히 저에너지 측정(< 10 keV)에서 심각한 문제가 됩니다. 예를 들어 Si(111) 결정으로 5 keV를 선택하면 15 keV의 3차 고조파가 함께 통과할 수 있습니다. (Si(111)의 경우 2차 고조파는 구조 인자에 의해 소멸되어 3차가 주요 문제입니다.) 고조파 광자는 시료에서 다른 흡수 계수를 가지므로, 측정된 스펙트럼이 참 스펙트럼의 왜곡된 선형 결합이 됩니다.

## 근본 원인

1. **브래그 법칙의 고차 해:** nλ = 2d sinθ에서 n = 2, 3, ... 에 해당하는 반사가 동일한 각도에서 회절
2. **결정 구조 인자:** Si(111)에서 2차 반사(222)는 금지되지만, 3차(333)는 허용됨; Si(311)에서는 2차(622)도 허용
3. **광원의 넓은 스펙트럼:** 언듈레이터/벤딩 마그넷(bending magnet)은 넓은 에너지 범위의 X-선을 방출
4. **이온 챔버 응답:** 고에너지 고조파 광자에 대한 이온 챔버의 다른 감도
5. **검출기 에너지 분해능 부족:** 에너지 분해가 불가능한 투과 모드 검출기에서 고조파 구분 불가

## 빠른 진단

고조파 오염을 빠르게 확인하는 코드:

```python
import numpy as np

def quick_harmonics_check(energy, mu, edge_energy):
    """
    흡수단 전(pre-edge) 영역에서 고조파 오염의 징후를 확인합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu : np.ndarray
        흡수 계수 배열
    edge_energy : float
        흡수단 에너지 (eV)

    Returns
    -------
    dict
        고조파 진단 결과
    """
    # pre-edge 영역 선택 (흡수단 50-150 eV 아래)
    pre_mask = (energy > edge_energy - 150) & (energy < edge_energy - 20)
    pre_mu = mu[pre_mask]
    pre_e = energy[pre_mask]

    # pre-edge 기울기 확인 (고조파가 있으면 기울기가 비정상적)
    coeffs = np.polyfit(pre_e, pre_mu, 1)
    slope = coeffs[0]

    # 흡수단 점프 크기
    post_mask = (energy > edge_energy + 30) & (energy < edge_energy + 100)
    edge_jump = np.mean(mu[post_mask]) - np.mean(pre_mu)

    print(f"Pre-edge slope: {slope:.6f} /eV")
    print(f"Edge jump: {edge_jump:.4f}")
    if edge_jump < 0.1:
        print("WARNING: Very small edge jump — possible harmonic contamination")

    return {"slope": slope, "edge_jump": edge_jump}
```

## 탐지 방법

### 시각적 지표

- **흡수단 점프(edge jump) 감소:** 정상보다 작은 흡수단 크기
- **XANES 특성 감쇠:** 백색선(white-line) 피크의 높이가 비정상적으로 낮음
- **비정상적 pre-edge 기울기:** pre-edge 영역의 기울기가 기대와 다름
- **규격화 후 post-edge 곡률:** 규격화된 스펙트럼의 post-edge 곡률이 비정상적

### 자동 탐지

```python
import numpy as np

def detect_harmonic_contamination(energy, mu, edge_energy,
                                   expected_edge_jump=None):
    """
    고조파 오염을 정량적으로 탐지합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu : np.ndarray
        투과 모드 흡수 계수
    edge_energy : float
        흡수단 에너지 (eV)
    expected_edge_jump : float, optional
        기대 흡수단 점프 크기

    Returns
    -------
    dict
        탐지 결과
    """
    # pre-edge 및 post-edge 영역 정의
    pre_mask = (energy > edge_energy - 150) & (energy < edge_energy - 20)
    post_mask = (energy > edge_energy + 50) & (energy < edge_energy + 200)

    pre_mu = np.mean(mu[pre_mask])
    post_mu = np.mean(mu[post_mask])
    edge_jump = post_mu - pre_mu

    # Victoreen 함수 피팅 (pre-edge 기울기 분석)
    pre_e = energy[pre_mask]
    pre_vals = mu[pre_mask]
    coeffs = np.polyfit(pre_e, pre_vals, 2)
    pre_curvature = coeffs[0]

    # log(I0/I)의 음수 영역 확인 (고조파의 직접 징후)
    negative_fraction = np.sum(mu < 0) / len(mu) if len(mu) > 0 else 0

    # 고조파 분율 추정 (Stern의 방법)
    # 고조파가 있으면 실제 edge jump는 줄어듦
    harmonics_fraction = 0.0
    if expected_edge_jump is not None and edge_jump > 0:
        harmonics_fraction = max(0, 1 - edge_jump / expected_edge_jump)

    # 심각도 판정
    if harmonics_fraction > 0.1 or negative_fraction > 0.01:
        severity = "critical"
    elif harmonics_fraction > 0.03:
        severity = "major"
    elif harmonics_fraction > 0.01:
        severity = "minor"
    else:
        severity = "none"

    return {
        "edge_jump": float(edge_jump),
        "pre_curvature": float(pre_curvature),
        "negative_fraction": float(negative_fraction),
        "estimated_harmonics_fraction": float(harmonics_fraction),
        "severity": severity,
    }


def estimate_harmonic_fraction_glancing(energy, mu_flat, mu_glancing):
    """
    평면 대 사선 입사(glancing angle) 측정을 비교하여 고조파 분율을 추정합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열
    mu_flat : np.ndarray
        일반 입사각 스펙트럼
    mu_glancing : np.ndarray
        사선 입사각 스펙트럼 (두꺼운 유효 경로)

    Returns
    -------
    float
        추정 고조파 분율
    """
    # 두꺼운 시료에서는 고조파 효과가 더 두드러짐
    ratio = mu_glancing / np.where(mu_flat > 0.01, mu_flat, 0.01)

    # pre-edge 영역에서 비율 변동 분석
    harmonics_indicator = np.std(ratio) / np.mean(ratio)

    return float(harmonics_indicator)
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 단색화기를 디튠(detune)하여 고조파를 제거합니다 (2번째 결정을 30-50% 디튜닝)
- 고조파 제거 미러(harmonic rejection mirror)를 사용합니다
- 에너지에 적합한 결정 쌍을 선택합니다 (예: Si(111) vs Si(311))
- 이온 챔버 가스 조성을 최적화하여 고조파 광자에 대한 감도를 줄입니다

### 보정 — 전통적 방법

```python
import numpy as np

def correct_harmonic_contamination(energy, mu_measured,
                                    harmonic_fraction,
                                    mu_harmonic=None):
    """
    알려진 고조파 분율을 사용하여 스펙트럼을 보정합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열
    mu_measured : np.ndarray
        측정된 (오염된) 흡수 스펙트럼
    harmonic_fraction : float
        고조파 광자의 분율 (0-1)
    mu_harmonic : np.ndarray, optional
        고조파 에너지에서의 흡수 스펙트럼 (모르면 0으로 가정)

    Returns
    -------
    np.ndarray
        보정된 흡수 스펙트럼
    """
    f = harmonic_fraction

    if mu_harmonic is None:
        # 고조파 에너지에서 흡수가 매우 낮다고 가정
        mu_harmonic = np.zeros_like(mu_measured) + np.min(mu_measured) * 0.1

    # Beer-Lambert 법칙 기반 보정
    # I_measured = (1-f) * I0 * exp(-mu_true * t) + f * I0 * exp(-mu_harm * t)
    # 투과 모드: mu_measured = -ln(I/I0)

    I_ratio_measured = np.exp(-mu_measured)
    I_ratio_harmonic = np.exp(-mu_harmonic)

    # 반복적 보정
    mu_corrected = mu_measured.copy()
    for iteration in range(20):
        I_ratio_true = np.exp(-mu_corrected)
        I_ratio_model = (1 - f) * I_ratio_true + f * I_ratio_harmonic
        mu_model = -np.log(np.clip(I_ratio_model, 1e-10, None))

        # 보정 갱신
        correction = mu_measured - mu_model
        mu_corrected = mu_corrected + correction

        if np.max(np.abs(correction)) < 1e-8:
            print(f"Converged in {iteration + 1} iterations")
            break

    return mu_corrected


def detune_optimization(energies, detuning_fractions, edge_jumps):
    """
    최적의 디튜닝 비율을 결정하기 위한 스캔 결과를 분석합니다.

    Parameters
    ----------
    energies : list
        테스트한 에너지 목록
    detuning_fractions : list of float
        테스트한 디튜닝 비율 (0-1)
    edge_jumps : list of float
        각 조건에서 측정된 흡수단 점프

    Returns
    -------
    float
        최적 디튜닝 비율
    """
    edge_jumps = np.array(edge_jumps)
    detuning_fractions = np.array(detuning_fractions)

    # 흡수단 점프가 최대가 되는 디튜닝 비율
    # 디튜닝이 너무 크면 플럭스 손실이 커짐
    max_idx = np.argmax(edge_jumps)
    optimal_detune = detuning_fractions[max_idx]

    print(f"Optimal detuning: {optimal_detune:.0%}")
    print(f"Maximum edge jump: {edge_jumps[max_idx]:.4f}")

    return float(optimal_detune)
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **스펙트럼 분해(Spectral Decomposition)** | 비지도 학습 | NMF/PCA를 사용하여 기본파와 고조파 성분을 분리 |
| **시뮬레이션 기반 보정(Simulation-based)** | 지도 학습 | FEFF 등으로 생성한 시뮬레이션 데이터로 고조파 효과를 학습하여 제거 |

```python
import numpy as np
from sklearn.decomposition import NMF

def nmf_harmonic_separation(spectra_matrix, n_components=2):
    """
    NMF를 사용하여 기본파와 고조파 성분을 분리합니다.

    Parameters
    ----------
    spectra_matrix : np.ndarray
        Shape (n_samples, n_energy_points) — 여러 조건에서 측정된 스펙트럼
    n_components : int
        분리할 성분 수 (기본값: 2, 기본파 + 고조파)

    Returns
    -------
    tuple
        (components, weights) — 추출된 성분과 가중치
    """
    # NMF는 음수가 아닌 행렬 분해
    # 흡수 스펙트럼이 양수이므로 적합
    model = NMF(n_components=n_components, max_iter=500, random_state=42)
    weights = model.fit_transform(spectra_matrix)
    components = model.components_

    print(f"Explained variance per component:")
    for i in range(n_components):
        contrib = np.sum(weights[:, i]) / np.sum(weights)
        print(f"  Component {i}: {contrib:.1%}")

    return components, weights
```

## 미보정 시 영향

- **XANES 특성 왜곡:** 백색선(white-line) 피크가 감쇠되어 화학 상태 분석이 부정확해짐
- **흡수단 형태 변형:** 흡수단의 날카로운 특성이 뭉개져 표준 스펙트럼과의 비교가 어려워짐
- **선형 결합 피팅(LCF) 오류:** 감쇠된 스펙트럼으로 인해 각 성분의 비율이 잘못 결정됨
- **EXAFS 진폭 감소:** 배위수(coordination number) 결정에 체계적 과소 평가 유발
- **배경(background) 제거 오류:** 비정상적 pre-edge 기울기로 인한 규격화 오류

## 관련 자료

- [에너지 교정 드리프트](energy_calibration_drift.md)
- [통계적 노이즈(EXAFS)](statistical_noise_exafs.md)
- [자기흡수(XAS)](self_absorption_xas.md)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)

## 핵심 요약

> **단색화기를 30-50% 디튠하여 고조파를 제거하고, 고에너지 실험에서는 고조파 제거 미러를 사용하십시오.** 고조파 오염은 XANES 특성을 감쇠시키고 흡수단 형태를 왜곡하여 화학 상태 분석의 신뢰성을 심각하게 훼손합니다. 디튜닝은 단순하면서도 가장 효과적인 예방 조치입니다.
