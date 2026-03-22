# 자기흡수(XAS) (Self-Absorption in XAS)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 분광법(Spectroscopy) |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 설명

형광 모드(fluorescence-mode) XAS에서 농축 시료(concentrated sample)를 측정할 때, 형광 신호가 시료 자체에 의해 감쇠되어 흡수단 특성(특히 백색선(white-line) 피크)이 참 흡수에 비해 평탄화/감소하여 나타나는 현상입니다.

자기흡수(self-absorption, 또는 자기형광(self-fluorescence))는 입사 X-선과 형광 X-선이 모두 시료 내에서 흡수되기 때문에 발생합니다. 흡수가 가장 강한 에너지(백색선 영역)에서 이 효과가 가장 크므로, 스펙트럼의 가장 강한 특성이 가장 많이 감쇠됩니다. 극단적인 경우, 형광 스펙트럼이 거의 평탄해질 수 있습니다.

## 근본 원인

1. **입사 빔의 흡수:** 입사 X-선이 시료 깊이에 따라 지수적으로 감쇠되어 깊은 영역은 더 적은 광자를 받음
2. **형광의 재흡수:** 방출된 형광 X-선이 시료를 빠져나가는 도중 흡수됨
3. **에너지 의존적 침투 깊이:** 흡수단 근처에서 에너지에 따라 침투 깊이(penetration depth)가 급격히 변하여 형광이 발생하는 유효 부피(effective volume)가 달라짐
4. **높은 원소 농도:** 관심 원소의 농도가 높을수록 자기흡수 효과가 커짐
5. **시료 기하학:** 두꺼운 시료 또는 45°/45° 기하학에서 효과가 극대화됨

## 빠른 진단

자기흡수 여부를 빠르게 평가하는 코드:

```python
import numpy as np

def quick_self_absorption_check(energy, mu_fluorescence, mu_transmission=None):
    """
    자기흡수 여부를 빠르게 확인합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu_fluorescence : np.ndarray
        형광 모드 규격화된 스펙트럼
    mu_transmission : np.ndarray, optional
        투과 모드 규격화된 스펙트럼 (있을 경우 비교)
    """
    # 백색선 피크 높이 확인
    edge_region = (energy > energy[len(energy)//3]) & (energy < energy[2*len(energy)//3])
    wl_height_fl = np.max(mu_fluorescence[edge_region])

    print(f"Fluorescence white-line height: {wl_height_fl:.3f}")

    if mu_transmission is not None:
        wl_height_tr = np.max(mu_transmission[edge_region])
        ratio = wl_height_fl / wl_height_tr if wl_height_tr > 0 else 0
        print(f"Transmission white-line height: {wl_height_tr:.3f}")
        print(f"Fl/Tr ratio: {ratio:.3f}")
        if ratio < 0.8:
            print("WARNING: Significant self-absorption detected!")
        elif ratio < 0.95:
            print("CAUTION: Mild self-absorption may be present")
    else:
        if wl_height_fl < 1.0:
            print("CAUTION: Reduced white-line — self-absorption possible")
```

## 탐지 방법

### 시각적 지표

- **형광 vs 투과 모드 비교:** 형광 스펙트럼의 백색선이 투과 스펙트럼보다 낮음
- **규격화 후 스펙트럼 평탄화:** 규격화된 형광 스펙트럼이 기대보다 평탄함
- **농도별 비교:** 농축 시료와 희석 시료의 스펙트럼 형태 차이

### 자동 탐지

```python
import numpy as np

def detect_self_absorption(energy, mu_fl, mu_tr=None,
                           element_info=None):
    """
    자기흡수를 정량적으로 탐지합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu_fl : np.ndarray
        규격화된 형광 모드 스펙트럼
    mu_tr : np.ndarray, optional
        규격화된 투과 모드 스펙트럼
    element_info : dict, optional
        {'concentration': float, 'edge_energy': float}

    Returns
    -------
    dict
        자기흡수 탐지 결과
    """
    results = {}

    if mu_tr is not None:
        # 방법 1: 형광-투과 비교
        # 백색선 영역에서 피크 높이 비교
        wl_fl = np.max(mu_fl)
        wl_tr = np.max(mu_tr)

        damping_ratio = wl_fl / wl_tr if wl_tr > 0 else 0
        results["damping_ratio"] = float(damping_ratio)

        # 전체 스펙트럼 유사도 (흡수가 강한 영역에서 차이가 큼)
        diff = mu_tr - mu_fl
        # 자기흡수는 피크에서 가장 크므로
        peak_region = mu_tr > np.percentile(mu_tr, 80)
        results["peak_diff"] = float(np.mean(diff[peak_region]))

    if element_info is not None:
        # 방법 2: 농도 기반 예측
        conc = element_info.get('concentration', 0)
        if conc > 0.1:  # > 10 wt%
            results["concentration_warning"] = True
            results["expected_severity"] = "major"
        elif conc > 0.01:  # > 1 wt%
            results["concentration_warning"] = True
            results["expected_severity"] = "moderate"
        else:
            results["concentration_warning"] = False
            results["expected_severity"] = "negligible"

    # 심각도 종합 판정
    if "damping_ratio" in results:
        if results["damping_ratio"] < 0.7:
            results["severity"] = "critical"
        elif results["damping_ratio"] < 0.85:
            results["severity"] = "major"
        elif results["damping_ratio"] < 0.95:
            results["severity"] = "minor"
        else:
            results["severity"] = "negligible"
    elif "expected_severity" in results:
        results["severity"] = results["expected_severity"]
    else:
        results["severity"] = "unknown"

    return results


def compare_dilution_series(energy, mu_list, concentrations):
    """
    농도 시리즈에서 자기흡수 효과를 평가합니다.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열
    mu_list : list of np.ndarray
        농도별 규격화된 스펙트럼
    concentrations : list of float
        각 스펙트럼의 원소 농도

    Returns
    -------
    dict
        농도별 자기흡수 분석 결과
    """
    white_line_heights = []
    for mu in mu_list:
        white_line_heights.append(np.max(mu))

    white_line_heights = np.array(white_line_heights)
    concentrations = np.array(concentrations)

    # 이상적 경우 백색선 높이가 농도에 무관해야 함
    # 자기흡수가 있으면 농도 증가에 따라 감소
    corr = np.corrcoef(concentrations, white_line_heights)[0, 1]

    results = {
        "concentrations": concentrations.tolist(),
        "white_line_heights": white_line_heights.tolist(),
        "correlation": float(corr),
        "self_absorption_present": corr < -0.5,
    }

    print(f"Concentration-WL correlation: {corr:.3f}")
    if corr < -0.5:
        print("Self-absorption is significant in concentrated samples")

    return results
```

## 해결 및 완화

### 예방 (데이터 수집 시)

- 시료를 BN(질화붕소) 등의 불활성 매트릭스로 희석합니다
- 가능하면 투과 모드(transmission mode)로 측정합니다
- 사선 입사(glancing angle) 기하학을 사용하여 유효 경로 길이를 줄입니다
- 얇은 시료(thin film)를 준비합니다

### 보정 — 전통적 방법

```python
import numpy as np

def booth_bridges_correction(energy, mu_fl, element,
                              concentration, matrix_composition,
                              theta_in=45, theta_out=45):
    """
    Booth & Bridges 알고리즘을 사용한 자기흡수 보정.

    Parameters
    ----------
    energy : np.ndarray
        에너지 배열 (eV)
    mu_fl : np.ndarray
        형광 모드 흡수 스펙트럼 (규격화됨)
    element : str
        관심 원소 기호
    concentration : float
        관심 원소의 질량 분율
    matrix_composition : dict
        매트릭스 조성 {'Si': 0.3, 'O': 0.6, ...}
    theta_in : float
        입사각 (도)
    theta_out : float
        방출각 (도)

    Returns
    -------
    np.ndarray
        자기흡수 보정된 스펙트럼
    """
    # 간소화된 Booth-Bridges 보정
    # mu_true = mu_fl / (1 - mu_fl * alpha)
    # alpha는 시료 조성과 기하학에 의존

    sin_in = np.sin(np.radians(theta_in))
    sin_out = np.sin(np.radians(theta_out))

    # 각도 인자
    alpha_geom = sin_in / sin_out

    # 매트릭스의 총 흡수 (근사)
    # 실제로는 xraydb 등으로 계산해야 함
    mu_matrix = 1.0  # 임의의 기본값 — 실제로는 계산 필요

    # 자기흡수 보정 인자
    # 간소화된 형태
    mu_corrected = np.zeros_like(mu_fl)
    for i, e in enumerate(energy):
        # 유효 흡수 인자
        chi_fl = mu_fl[i]
        correction_factor = 1.0 / (1.0 + concentration * chi_fl * alpha_geom)
        mu_corrected[i] = chi_fl / correction_factor

    # 재규격화
    pre_edge = np.mean(mu_corrected[:50])
    post_edge = np.mean(mu_corrected[-50:])
    mu_corrected = (mu_corrected - pre_edge) / (post_edge - pre_edge)

    return mu_corrected


def fluo_correction_simple(mu_fl, alpha):
    """
    단순 자기흡수 보정 (Troger et al., 1992).

    Parameters
    ----------
    mu_fl : np.ndarray
        형광 모드 규격화된 스펙트럼
    alpha : float
        자기흡수 보정 파라미터 (0 = 보정 없음, 1 = 최대 보정)

    Returns
    -------
    np.ndarray
        보정된 스펙트럼
    """
    # mu_true = mu_fl / (1 - alpha * mu_fl)
    mu_corrected = mu_fl / (1.0 - alpha * mu_fl)

    # 재규격화
    mu_corrected = mu_corrected / np.mean(mu_corrected[-50:])

    return mu_corrected
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **역 모델링(Inverse Modeling)** | 지도 학습 | 자기흡수된 스펙트럼과 참 스펙트럼 쌍으로 학습하여 보정 |
| **물리 기반 신경망(PINN)** | 하이브리드 | Beer-Lambert 법칙을 손실 함수에 포함하여 물리적 제약 조건 하에서 보정 |
| **전이 학습(Transfer Learning)** | 지도 학습 | FEFF 시뮬레이션 데이터로 사전 학습 후 실험 데이터로 미세 조정 |

```python
import numpy as np

def simulate_self_absorption_training_data(mu_true_list,
                                            alpha_range=(0.0, 0.5),
                                            n_augment=10):
    """
    자기흡수 보정 모델 학습을 위한 합성 데이터를 생성합니다.

    Parameters
    ----------
    mu_true_list : list of np.ndarray
        참 스펙트럼 목록
    alpha_range : tuple
        자기흡수 파라미터 범위
    n_augment : int
        각 참 스펙트럼당 생성할 오염 스펙트럼 수

    Returns
    -------
    tuple
        (inputs, targets) — 학습 데이터 쌍
    """
    inputs = []
    targets = []

    for mu_true in mu_true_list:
        for _ in range(n_augment):
            alpha = np.random.uniform(*alpha_range)
            # 자기흡수 시뮬레이션
            mu_sa = mu_true * (1.0 - alpha * mu_true)

            # 약간의 노이즈 추가
            noise = np.random.normal(0, 0.005, len(mu_true))
            mu_sa_noisy = mu_sa + noise

            inputs.append(mu_sa_noisy)
            targets.append(mu_true)

    return np.array(inputs), np.array(targets)
```

## 미보정 시 영향

- **XANES 피크 높이 과소 평가:** 백색선 강도가 감소하여 화학 상태 지문(fingerprint) 비교가 부정확
- **선형 결합 피팅(LCF) 오류:** 감쇠된 스펙트럼은 기준 스펙트럼과 체계적으로 다르므로 성분 비율 오류 유발
- **배위수 과소 평가:** EXAFS 진폭이 감소하여 배위수(coordination number)가 낮게 결정됨
- **산화 상태 오판:** 백색선 강도 변화가 화학적 변화로 잘못 해석될 수 있음
- **정량 분석 불가:** 자기흡수가 심한 경우 정량적 비교 자체가 무의미해짐

## 관련 자료

- [통계적 노이즈(EXAFS)](statistical_noise_exafs.md)
- [고조파 오염](harmonics_contamination.md)
- [방사선 손상](radiation_damage.md)
- [Larch - XAFS 분석 소프트웨어](https://xraypy.github.io/xraylarch/)
- [Athena self-absorption 보정](https://bruceravel.github.io/demeter/)

## 핵심 요약

> **자기흡수는 형광 XAS 진폭을 항상 감소시킵니다. 정량적 XANES 분석을 위해서는 보정하거나 희석 시료를 사용하십시오.** 농축 시료의 형광 모드 측정에서는 자기흡수가 불가피하므로, Booth & Bridges 알고리즘 등으로 보정하거나, 가능하면 투과 모드 측정 또는 시료 희석으로 문제를 근본적으로 제거해야 합니다.
