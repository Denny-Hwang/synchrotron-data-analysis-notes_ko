# 자기흡수(Self-Absorption)

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
자기흡수 효과 개념도:

    입사 X선 빔
        ↓  ↓  ↓
    ┌───────────────────┐ ─── 표면
    │  ○ 약한 흡수      │       ← 고에너지 형광 (Fe Kα, 6.4 keV)
    │  ● ──→ 검출기     │          → 대부분 탈출
    │                   │
    │  ○ 강한 흡수      │       ← 저에너지 형광 (Na Kα, 1.04 keV)
    │  ● ──✕            │          → 시료 내에서 흡수
    │                   │
    └───────────────────┘ ─── 기판

    깊이가 깊을수록, 에너지가 낮을수록 자기흡수 효과가 심함
    I = I₀ · exp(-μρt)
```

## 설명

시료 내부 깊은 곳에서 방출된 형광 X선이 검출기에 도달하기 전에 시료 매트릭스에 의해 부분적으로 흡수되어, 두꺼운/고밀도 시료에서 원소 농도가 체계적으로 과소 추정되는 현상입니다.

이 효과는 **에너지 의존적**입니다 — 저에너지 형광(경원소)이 고에너지 형광(중원소)보다 더 강하게 흡수됩니다. 따라서:
- **Na, Mg, Al, Si** 등 경원소의 형광은 시료 내에서 크게 감쇠됩니다.
- **Fe, Cu, Zn** 등 중원소의 형광은 상대적으로 적게 감쇠됩니다.
- 동일 원소라도 시료의 두께나 밀도에 따라 감쇠 정도가 달라집니다.

## 근본 원인

시료 매트릭스가 입사 빔과 방출된 형광 양쪽을 모두 감쇠시킵니다. 감쇠는 **비어-람베르트 법칙(Beer-Lambert law)** 을 따릅니다:

**I = I₀ · exp(-μρt)**

여기서:
- **μ** = 질량 감쇠 계수 (cm²/g), 에너지에 의존
- **ρ** = 시료 밀도 (g/cm³)
- **t** = 경로 길이 (cm)

자기흡수의 물리적 과정:
1. 입사 빔이 시료에 침투하면서 감쇠 (입사빔 감쇠)
2. 형광 X선이 시료 내부에서 검출기 방향으로 탈출하면서 감쇠 (형광 감쇠)
3. 총 자기흡수 = 입사빔 감쇠 + 형광 감쇠

## 빠른 진단

얇은 영역과 두꺼운 영역 비교, 또는 흡수단 점프 비율(edge-jump ratio)을 통해 진단할 수 있습니다.

```python
import numpy as np

def quick_self_absorption_check(thin_region, thick_region, element_names):
    """
    얇은 영역과 두꺼운 영역의 원소 비율을 비교하여 자기흡수를 진단합니다.

    Parameters
    ----------
    thin_region : dict
        {element: mean_counts} for thin sample region.
    thick_region : dict
        {element: mean_counts} for thick sample region.
    element_names : list of str
        분석할 원소 이름 목록.

    Returns
    -------
    dict with element-wise thick/thin ratios.
    """
    print("Element    Thin     Thick    Ratio    Status")
    print("-" * 55)

    results = {}
    for elem in element_names:
        thin_val = thin_region.get(elem, 0)
        thick_val = thick_region.get(elem, 0)

        if thin_val > 0:
            ratio = thick_val / thin_val
        else:
            ratio = np.inf

        # 자기흡수가 없으면 ratio ≈ thickness_ratio
        # 자기흡수가 있으면 ratio < thickness_ratio (특히 저에너지)
        status = "OK" if 0.8 < ratio < 1.5 else "ABSORPTION"
        results[elem] = ratio

        print(f"{elem:10s} {thin_val:8.1f} {thick_val:8.1f} "
              f"{ratio:8.3f}  {status}")

    return results
```

## 탐지 방법

### 시각적 지표

- **경원소 맵에서 두꺼운 영역의 신호 감소** — 시료가 두꺼운 곳에서 Na, Mg, Si 등의 신호가 약해짐
- **원소 비율의 공간적 변동** — 두께에 따라 원소 간 비율이 변하는 패턴
- **컴프턴/레일리 산란 맵과의 상관관계** — 산란 신호가 강한 곳(두꺼운 곳)에서 경원소 형광이 약해짐
- **시료 가장자리에서 비정상적으로 높은 경원소 농도** — 가장자리가 얇아 자기흡수가 적기 때문

### 자동 탐지

```python
import numpy as np

def estimate_self_absorption(element_maps, element_energies,
                               compton_map, matrix_composition,
                               geometry_angle_deg=45):
    """
    기본 파라미터(fundamental parameters)를 사용하여 자기흡수 효과를 추정합니다.

    Parameters
    ----------
    element_maps : dict
        {element: 2D map (counts)} — 원소별 맵.
    element_energies : dict
        {element: fluorescence_energy_keV} — 각 원소의 형광 에너지.
    compton_map : np.ndarray
        2D Compton scatter map (두께/밀도의 프록시).
    matrix_composition : dict
        {element: weight_fraction} — 시료 매트릭스의 근사 조성.
    geometry_angle_deg : float
        검출기 takeoff angle (degrees).

    Returns
    -------
    report : dict
        각 원소별 자기흡수 심각도 평가.
    """
    # 간단한 질량 감쇠 계수 근사 (에너지 의존)
    # 실제 응용에서는 xraylib 또는 NIST 데이터베이스 사용
    def approx_mu(energy_keV):
        """간단한 질량 감쇠 계수 근사 (SiO2 매트릭스 가정)."""
        # 대략적 power-law 근사
        return 20.0 * energy_keV ** (-2.7)  # cm^2/g, rough

    angle_rad = np.radians(geometry_angle_deg)
    sin_angle = np.sin(angle_rad)

    report = {}
    for elem, elem_map in element_maps.items():
        energy = element_energies.get(elem, 5.0)
        mu = approx_mu(energy)

        # Compton 맵을 두께 프록시로 사용
        # 높은 Compton 산란 = 더 두꺼운/밀도 높은 시료
        thickness_proxy = compton_map / np.median(compton_map)

        # 예상 감쇠 계수
        # 감쇠 ≈ exp(-μ·ρ·t / sin(θ))
        rho_t_proxy = thickness_proxy * 0.01  # 임의 스케일링
        expected_attenuation = np.exp(-mu * rho_t_proxy / sin_angle)

        mean_attenuation = np.mean(expected_attenuation)

        # 상관관계 분석: 원소 맵과 두께 프록시의 반상관
        flat_elem = elem_map.flatten()
        flat_thick = thickness_proxy.flatten()
        mask = (flat_elem > 0) & np.isfinite(flat_thick)

        if np.sum(mask) > 10:
            correlation = np.corrcoef(flat_elem[mask], flat_thick[mask])[0, 1]
        else:
            correlation = 0.0

        # 심각도 평가
        if energy < 2.0:
            severity = "critical"  # 저에너지 형광
        elif energy < 5.0:
            severity = "major"
        else:
            severity = "minor"

        report[elem] = {
            "energy_keV": energy,
            "mu_approx": mu,
            "mean_attenuation": mean_attenuation,
            "correlation_with_thickness": correlation,
            "severity": severity,
        }

        print(f"{elem} ({energy:.2f} keV): "
              f"mu={mu:.1f} cm2/g, "
              f"mean_atten={mean_attenuation:.3f}, "
              f"correlation={correlation:.3f}, "
              f"severity={severity}")

    return report
```

## 해결 및 완화

### 예방 (데이터 수집 전)

1. **얇은 시료 준비** — 마이크로톰(microtome)을 사용하여 수 μm 이하의 얇은 절편을 준비합니다.
2. **시료 희석** — 분말 시료의 경우 비흡수성 매트릭스(예: 셀룰로스)로 희석합니다.
3. **높은 에너지 여기 사용** — 입사 빔 에너지를 높여 침투 깊이를 증가시킵니다.
4. **적절한 검출기 기하학** — 검출기 takeoff 각도를 최적화합니다.

### 보정 — 전통적 방법

```python
import numpy as np

def fundamental_parameters_correction(raw_counts, incident_energy_keV,
                                        fluorescence_energy_keV,
                                        matrix_mu_in, matrix_mu_out,
                                        density, thickness_cm,
                                        angle_in_deg=90, angle_out_deg=45):
    """
    기본 파라미터(Fundamental Parameters) 방법으로 자기흡수를 보정합니다.

    Parameters
    ----------
    raw_counts : np.ndarray
        보정 전 원소 맵 (counts).
    incident_energy_keV : float
        입사 빔 에너지 (keV).
    fluorescence_energy_keV : float
        형광 에너지 (keV).
    matrix_mu_in : float
        입사 에너지에서의 질량 감쇠 계수 (cm^2/g).
    matrix_mu_out : float
        형광 에너지에서의 질량 감쇠 계수 (cm^2/g).
    density : float
        시료 밀도 (g/cm^3).
    thickness_cm : float
        시료 두께 (cm).
    angle_in_deg : float
        입사 빔 각도 (표면 법선 기준, degrees).
    angle_out_deg : float
        검출기 takeoff 각도 (degrees).

    Returns
    -------
    corrected : np.ndarray
        자기흡수 보정된 맵.
    correction_factor : float
        적용된 보정 계수.
    """
    sin_in = np.sin(np.radians(angle_in_deg))
    sin_out = np.sin(np.radians(angle_out_deg))

    # 총 감쇠 계수
    chi = (matrix_mu_in / sin_in) + (matrix_mu_out / sin_out)

    # 보정 계수 (얇은 시료 근사)
    rho_t = density * thickness_cm
    absorption_term = chi * rho_t

    if absorption_term < 0.01:
        # 매우 얇은 시료 — 보정 불필요
        correction_factor = 1.0
    elif absorption_term > 10:
        # 매우 두꺼운 시료 (무한 두께 근사)
        correction_factor = chi * rho_t  # 선형 근사
    else:
        # 일반적인 경우
        correction_factor = absorption_term / (1 - np.exp(-absorption_term))

    corrected = raw_counts * correction_factor

    print(f"Self-absorption correction:")
    print(f"  Incident energy: {incident_energy_keV:.2f} keV")
    print(f"  Fluorescence energy: {fluorescence_energy_keV:.2f} keV")
    print(f"  chi*rho*t = {absorption_term:.3f}")
    print(f"  Correction factor: {correction_factor:.3f}")

    return corrected, correction_factor


def thin_sample_approximation_check(density, thickness_cm,
                                      mu_in, mu_out,
                                      angle_in_deg=90, angle_out_deg=45,
                                      threshold=0.1):
    """
    얇은 시료 근사(thin-sample approximation)의 유효성을 확인합니다.

    Parameters
    ----------
    density : float
        시료 밀도 (g/cm³).
    thickness_cm : float
        시료 두께 (cm).
    mu_in : float
        입사 에너지에서의 질량 감쇠 계수.
    mu_out : float
        형광 에너지에서의 질량 감쇠 계수.
    angle_in_deg, angle_out_deg : float
        입사/출사 각도 (degrees).
    threshold : float
        유효성 판단 임계값 (기본값 0.1 = 10% 오차).

    Returns
    -------
    dict with validity assessment.
    """
    sin_in = np.sin(np.radians(angle_in_deg))
    sin_out = np.sin(np.radians(angle_out_deg))

    chi = (mu_in / sin_in) + (mu_out / sin_out)
    rho_t = density * thickness_cm
    absorption_term = chi * rho_t

    # 얇은 시료 근사의 오차
    if absorption_term < 0.001:
        approx_error = 0.0
    else:
        exact = absorption_term / (1 - np.exp(-absorption_term))
        thin_approx = 1.0
        approx_error = abs(exact - thin_approx) / exact

    is_valid = approx_error < threshold

    print(f"Thin-sample approximation check:")
    print(f"  chi*rho*t = {absorption_term:.4f}")
    print(f"  Approximation error: {approx_error:.1%}")
    print(f"  Valid (< {threshold:.0%} error): {is_valid}")

    return {
        "absorption_term": absorption_term,
        "approximation_error": approx_error,
        "is_valid": is_valid,
    }
```

### 보정 — AI/ML 방법

자기흡수 보정은 물리적 원리(비어-람베르트 법칙, 기본 파라미터 방법)가 잘 확립되어 있으므로 일반적으로 AI/ML 방법이 필요하지 않습니다. 시료의 매트릭스 조성과 두께 정보가 정확하다면 해석적 보정으로 충분합니다.

## 미보정 시 영향

- **농도 과소 추정** — 특히 경원소의 실제 농도보다 낮게 측정됩니다.
- **깊이 의존적 편향** — 시료의 두꺼운 영역에서 체계적으로 농도가 낮게 나타납니다.
- **원소 비율 왜곡** — 에너지에 따른 차등 흡수로 인해 경원소/중원소 비율이 왜곡됩니다.
- **정량 분석 무효화** — 보정 없이는 절대 농도 정량이 불가능합니다.

## 관련 자료

- [xraylib 라이브러리](https://github.com/tschoonj/xraylib) — X선 물리 데이터베이스 (질량 감쇠 계수 등)
- [NIST XCOM 데이터베이스](https://www.nist.gov/pml/xcom-photon-cross-sections-database) — 광자 단면적 데이터

## 핵심 요약

> **자기흡수는 모든 XRF 측정에 항상 존재하며, 심각도는 시료 두께, 매트릭스 조성, 형광 에너지에 따라 결정됩니다.** 정량 분석을 위해서는 기본 파라미터 보정을 적용하거나 얇은 시료를 준비해야 합니다. 경원소(저에너지 형광)일수록 보정이 더 중요합니다.

---
