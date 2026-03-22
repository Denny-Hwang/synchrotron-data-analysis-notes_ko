# 데드타임 포화(Dead-Time Saturation)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

```
데드타임 포화 특성 곡선:

    출력 계수율(OCR)
    │
    │           ╭──── 이상적 (데드타임 = 0)
    │          ╱
    │    ╭────╱──── 비마비형(Non-paralyzable)
    │   ╱   ╱
    │  ╱  ╱╲──── 마비형(Paralyzable)
    │ ╱ ╱    ╲
    │╱╱        ╲
    └───────────────── 입력 계수율(ICR)

    ICR/OCR = 1.0  → 데드타임 없음 (이상적)
    ICR/OCR > 1.0  → 데드타임 손실 발생
    ICR/OCR > 1.4  → 심각한 손실 (>30%)
```

## 설명

높은 계수율에서 검출기 전자 회로가 각 이벤트를 처리하는 데 유한한 시간(데드타임)이 필요합니다. 데드타임 동안 도착하는 광자는 손실되어, 입사 플럭스가 증가해도 계수율이 정체하거나 오히려 감소합니다. ICR(Input Count Rate)/OCR(Output Count Rate) 비율이 1.0에서 벗어납니다.

두 가지 데드타임 모델:
- **비마비형(Non-paralyzable)**: 데드타임 중 새 이벤트가 도착해도 데드타임이 연장되지 않음 → 출력이 포화 수준에서 정체
- **마비형(Paralyzable)**: 데드타임 중 새 이벤트가 데드타임을 재시작시킴 → 매우 높은 계수율에서 출력이 오히려 감소

## 근본 원인

1. **펄스 처리 시간** — 각 검출 이벤트의 펄스를 성형(shaping)하고 디지털화하는 데 최소한의 시간이 필요합니다.
2. **펄스 파일업(Pulse Pileup)** — 두 개의 펄스가 너무 가까이 도착하면 하나의 높은 에너지 이벤트로 잘못 기록됩니다.
3. **전자 회로 한계** — ADC 변환 속도, 디지털 펄스 처리기(DPP)의 처리 용량 제한
4. **고농도 주원소** — 시료에 고농도로 존재하는 원소(예: Fe이 풍부한 광물)가 검출기를 압도합니다.

## 빠른 진단

ICR/OCR 비율을 확인하여 빠르게 진단할 수 있습니다.

```python
import numpy as np

def quick_dead_time_check(icr_map, ocr_map):
    """
    ICR/OCR 비율을 통해 데드타임 상태를 빠르게 진단합니다.

    Parameters
    ----------
    icr_map : np.ndarray
        2D Input Count Rate map (counts/sec).
    ocr_map : np.ndarray
        2D Output Count Rate map (counts/sec).

    Returns
    -------
    dict with dead-time statistics.
    """
    # ICR/OCR 비율 계산
    ratio_map = np.where(ocr_map > 0, icr_map / ocr_map, 1.0)

    mean_ratio = np.mean(ratio_map)
    max_ratio = np.max(ratio_map)
    fraction_above_1_3 = np.sum(ratio_map > 1.3) / ratio_map.size
    fraction_above_1_5 = np.sum(ratio_map > 1.5) / ratio_map.size

    print(f"ICR/OCR ratio statistics:")
    print(f"  Mean:  {mean_ratio:.3f}")
    print(f"  Max:   {max_ratio:.3f}")
    print(f"  >1.3 (>23% loss): {fraction_above_1_3:.1%} of pixels")
    print(f"  >1.5 (>33% loss): {fraction_above_1_5:.1%} of pixels")

    if max_ratio > 1.5:
        print("WARNING: Severe dead-time saturation detected!")
    elif max_ratio > 1.3:
        print("CAUTION: Moderate dead-time effects present")
    else:
        print("OK: Dead-time effects minimal")

    return {
        "ratio_map": ratio_map,
        "mean_ratio": mean_ratio,
        "max_ratio": max_ratio,
        "fraction_above_1_3": fraction_above_1_3,
    }
```

## 탐지 방법

### 시각적 지표

- ICR/OCR 비율 맵에서 **고농도 영역의 비율 상승** (> 1.0)
- 고농도 영역에서 원소 농도가 예상보다 **낮게** 나타남 (언더카운팅)
- 스펙트럼에서 파일업 피크(sum peak)의 출현 — 예: Fe Kα의 2배 에너지(12.8 keV)에 인위적 피크
- 빔 세기 증가에 비례하지 않는 카운트 증가 패턴

### 자동 탐지

```python
import numpy as np

def assess_dead_time(icr_map, ocr_map, dwell_time_sec,
                      warning_threshold=1.3, critical_threshold=1.5):
    """
    데드타임 포화 수준을 평가하고 보정 필요성을 판단합니다.

    Parameters
    ----------
    icr_map : np.ndarray
        2D Input Count Rate map (counts/sec or total input counts).
    ocr_map : np.ndarray
        2D Output Count Rate map (counts/sec or total output counts).
    dwell_time_sec : float
        Per-pixel dwell time in seconds.
    warning_threshold : float
        ICR/OCR ratio for warning.
    critical_threshold : float
        ICR/OCR ratio for critical warning.

    Returns
    -------
    report : dict
        데드타임 평가 보고서.
    """
    # ICR/OCR 비율 맵
    valid = ocr_map > 0
    ratio_map = np.ones_like(icr_map, dtype=float)
    ratio_map[valid] = icr_map[valid] / ocr_map[valid]

    # 데드타임 프랙션: (ICR - OCR) / ICR
    dead_fraction_map = np.zeros_like(icr_map, dtype=float)
    icr_valid = icr_map > 0
    dead_fraction_map[icr_valid] = (
        (icr_map[icr_valid] - ocr_map[icr_valid]) / icr_map[icr_valid]
    )
    dead_fraction_map = np.clip(dead_fraction_map, 0, 1)

    # 통계
    n_pixels = ratio_map.size
    n_warning = int(np.sum(ratio_map > warning_threshold))
    n_critical = int(np.sum(ratio_map > critical_threshold))
    mean_dead_fraction = np.mean(dead_fraction_map)
    max_dead_fraction = np.max(dead_fraction_map)

    # 심각도 분류
    if n_critical > 0.01 * n_pixels:
        severity = "critical"
    elif n_warning > 0.05 * n_pixels:
        severity = "major"
    elif n_warning > 0:
        severity = "minor"
    else:
        severity = "none"

    # 파일업 추정 (높은 ICR에서)
    max_icr = np.max(icr_map)
    estimated_pileup_rate = max_icr * mean_dead_fraction  # 대략적 추정

    print(f"Dead-time assessment:")
    print(f"  Warning pixels (ratio>{warning_threshold}):  "
          f"{n_warning} ({n_warning / n_pixels:.1%})")
    print(f"  Critical pixels (ratio>{critical_threshold}): "
          f"{n_critical} ({n_critical / n_pixels:.1%})")
    print(f"  Mean dead fraction: {mean_dead_fraction:.1%}")
    print(f"  Max dead fraction:  {max_dead_fraction:.1%}")
    print(f"  Severity: {severity}")

    return {
        "ratio_map": ratio_map,
        "dead_fraction_map": dead_fraction_map,
        "severity": severity,
        "n_warning": n_warning,
        "n_critical": n_critical,
        "mean_dead_fraction": mean_dead_fraction,
        "max_dead_fraction": max_dead_fraction,
    }
```

## 해결 및 완화

### 예방 (데이터 수집 전)

1. **입사 플럭스 감소** — 감쇠기(attenuator)를 사용하여 검출기에 도달하는 플럭스를 줄입니다.
2. **빠른 검출기 사용** — 짧은 피킹 타임(peaking time)의 고속 DPP를 사용합니다.
3. **다중 검출기 배치** — 여러 검출기의 카운트를 합산하여 개별 검출기의 부하를 분산합니다.
4. **ICR 모니터링** — 실시간으로 ICR/OCR 비율을 모니터링하며 데이터를 수집합니다.

### 보정 — 전통적 방법

```python
import numpy as np

def correct_dead_time_nonparalyzable(measured_counts, icr, ocr, dwell_time):
    """
    비마비형(non-paralyzable) 모델을 사용한 데드타임 보정.

    모델: OCR = ICR / (1 + ICR * tau)
    보정: true_counts = measured_counts * (ICR / OCR)

    Parameters
    ----------
    measured_counts : np.ndarray
        측정된 카운트 맵.
    icr : np.ndarray
        Input Count Rate (counts/sec).
    ocr : np.ndarray
        Output Count Rate (counts/sec).
    dwell_time : float
        체류 시간 (seconds).

    Returns
    -------
    corrected : np.ndarray
        데드타임 보정된 카운트 맵.
    """
    correction_factor = np.ones_like(measured_counts, dtype=float)
    valid = ocr > 0
    correction_factor[valid] = icr[valid] / ocr[valid]

    corrected = measured_counts * correction_factor

    max_correction = np.max(correction_factor)
    mean_correction = np.mean(correction_factor[valid])

    print(f"Non-paralyzable dead-time correction:")
    print(f"  Mean correction factor: {mean_correction:.3f}")
    print(f"  Max correction factor:  {max_correction:.3f}")

    if max_correction > 2.0:
        print("  WARNING: Very large correction (>2x) — data may be unreliable")

    return corrected


def correct_dead_time_paralyzable(measured_rate, tau_sec):
    """
    마비형(paralyzable) 모델을 사용한 데드타임 보정.

    모델: m = n * exp(-n * tau)
    여기서 m = 측정된 계수율, n = 실제 계수율, tau = 데드타임.
    Newton-Raphson 방법으로 n을 구합니다.

    Parameters
    ----------
    measured_rate : np.ndarray
        측정된 계수율 (counts/sec).
    tau_sec : float
        검출기 데드타임 (seconds), 예: 1e-6 for 1 μs.

    Returns
    -------
    true_rate : np.ndarray
        보정된 실제 계수율.
    """
    true_rate = measured_rate.copy().astype(float)

    # Newton-Raphson 반복
    for iteration in range(50):
        f = true_rate * np.exp(-true_rate * tau_sec) - measured_rate
        f_prime = np.exp(-true_rate * tau_sec) * (1 - true_rate * tau_sec)

        # 발산 방지
        valid = np.abs(f_prime) > 1e-20
        update = np.zeros_like(true_rate)
        update[valid] = f[valid] / f_prime[valid]
        true_rate -= update

        # 음수 방지
        true_rate = np.maximum(true_rate, measured_rate)

        if np.max(np.abs(update[valid])) < 1.0:
            break

    correction = np.where(measured_rate > 0,
                          true_rate / measured_rate, 1.0)

    print(f"Paralyzable dead-time correction (tau={tau_sec*1e6:.1f} us):")
    print(f"  Iterations: {iteration + 1}")
    print(f"  Max correction factor: {np.max(correction):.3f}")

    return true_rate


def estimate_dead_time_tau(icr_series, ocr_series):
    """
    ICR-OCR 관계로부터 검출기 데드타임(tau)을 추정합니다.

    Parameters
    ----------
    icr_series : np.ndarray
        다양한 플럭스 조건에서 측정한 ICR 값들.
    ocr_series : np.ndarray
        대응하는 OCR 값들.

    Returns
    -------
    tau_sec : float
        추정된 데드타임 (seconds).
    """
    # 비마비형 모델: OCR = ICR / (1 + ICR * tau)
    # 재배열: 1/OCR = 1/ICR + tau
    # 선형 회귀로 tau 추정

    valid = (icr_series > 0) & (ocr_series > 0)
    x = 1.0 / icr_series[valid]  # 1/ICR
    y = 1.0 / ocr_series[valid]  # 1/OCR

    # 선형 회귀: y = x + tau
    # y - x = tau
    tau_estimates = y - x
    tau_sec = np.median(tau_estimates)

    print(f"Estimated dead time: {tau_sec * 1e6:.2f} microseconds")

    return tau_sec
```

### 보정 — AI/ML 방법

데드타임 보정은 물리적 모델(마비형/비마비형)이 잘 확립되어 있으므로 일반적으로 AI/ML 방법이 필요하지 않습니다. ICR/OCR 데이터가 기록되어 있다면 해석적 보정으로 충분합니다.

## 미보정 시 영향

- **고농도 영역의 농도 과소 추정** — 가장 관심 있는 핫스팟에서 정량이 부정확합니다.
- **비선형 응답** — 검출기 응답이 비선형이 되어 농도와 카운트의 비례 관계가 깨집니다.
- **파일업 아티팩트** — 스펙트럼에서 합산 피크(sum peak)가 출현하여 유령 원소를 생성합니다.
- **공간 정보 왜곡** — 농도 분포의 역치가 잘리는 효과가 발생합니다.

## 관련 자료

- [MAPS 워크플로우 분석](../../07_reverse_engineering/workflow_analysis.md) — MAPS 소프트웨어의 데드타임 보정 구현

## 핵심 요약

> **ICR/OCR 비율을 항상 모니터링하고, 정량 분석 전에 데드타임 보정을 적용하세요.** 비율이 1.4 이상(데드 프랙션 > 30%)이면 감쇠기를 사용하여 플럭스를 줄이는 것을 권장합니다. 보정 계수가 2배를 초과하면 데이터의 신뢰성이 크게 저하됩니다.

---
