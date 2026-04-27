# 기생 산란(Parasitic Scattering, SAXS/WAXS)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | SAXS / WAXS |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 심각(Critical) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 방사광 산란(ESRF, DESY, Diamond, SPring-8) |

## 시각적 예시

![보정 전후 — 기생 산란](../images/parasitic_scattering_before_after.png)

> **이미지 출처:** 저-q 영역에 시뮬레이션된 기생 산란을 가진 합성 SAXS I(q) 곡선. 왼쪽: 슬릿/윈도우 산란으로 인한 가파른 상승. 오른쪽: 버퍼 차감 후 진정한 Guinier 영역이 드러남. MIT 라이선스.

## 설명

기생 산란(Parasitic scattering)은 시료가 아닌 광학 부품(슬릿, 윈도우, 공기 갭, 빔스톱)과의 X선 상호작용에서 발생하는 원치 않는 배경 신호입니다. SAXS에서는 저-q 영역의 지배적인 노이즈 원천이며, 관심 있는 과학적 신호(대규모 구조)가 빔 정의 슬릿과 윈도우의 산란과 겹칩니다. 신뢰할 수 있는 구조 분석을 위해서는 기생 산란의 적절한 차감이 필수적입니다.

## 근본 원인

- **슬릿 산란:** 슬릿 가장자리에 부딪힌 X선이 저각도에서 발산 산란을 생성
- **윈도우 산란:** Kapton, mica 또는 diamond 윈도우가 광범위한 배경 기여
- **공기 산란:** 모든 공기 경로 길이가 확산 배경을 더함(N₂, O₂ 산란)
- **빔스톱 산란:** 빔스톱과 그 지지선이 저-q에서 산란
- **비행 튜브 결함:** 진공 경로 내 잔류 가스, 윈도우 흐림

## 빠른 진단

```python
import numpy as np

def check_parasitic_scatter(q, I_sample, I_buffer, I_empty):
    """Assess parasitic scattering contribution."""
    # Parasitic scatter: remains after buffer subtraction
    I_corrected = I_sample - I_buffer
    I_parasitic = I_buffer - I_empty
    # Check ratio at low q
    low_q_mask = q < q[len(q)//10]
    ratio = I_parasitic[low_q_mask].mean() / I_sample[low_q_mask].mean()
    print(f"Parasitic/sample ratio at low-q: {ratio:.2%}")
    if ratio > 0.5:
        print("⚠ High parasitic scattering — check slits and windows")
    return ratio
```

## 탐지 방법

### 시각적 지표

- 매우 낮은 q에서 I(q)의 가파른 상승(시료의 진정한 Guinier 영역 아래)
- 배경 모양이 시료가 아닌 슬릿 설정에 따라 변화
- 비대칭 2D 패턴(기생 산란이 슬릿 기하를 따름)
- 빔 내 시료가 없어도 신호가 지속됨

### 자동 탐지

```python
import numpy as np

def parasitic_slope_test(q, I_q, q_min=0.005, q_max=0.02):
    """Check for parasitic scatter by power-law slope at low q."""
    mask = (q >= q_min) & (q <= q_max)
    log_q, log_I = np.log10(q[mask]), np.log10(I_q[mask])
    slope = np.polyfit(log_q, log_I, 1)[0]
    # Parasitic: slope ~ -4 (Porod from slits); Real Guinier: slope ~ -q²Rg²/3
    print(f"Low-q slope: {slope:.1f} (< -3 suggests parasitic scattering)")
    return slope
```

## 보정 방법

### 전통적 접근

1. **빈 빔 / 버퍼 차감:** 빈 셀 + 버퍼를 측정하여 시료에서 차감
2. **가드 슬릿:** 1차 슬릿의 기생 산란을 차단하는 2차 슬릿 세트
3. **무산란 슬릿(Scatterless slits):** 기생 산란을 발생시키지 않는 단결정(Ge/Si) 슬릿
4. **진공 비행 튜브:** 비워진 경로로 공기 산란 제거
5. **방위각 마스킹:** 2D 패턴에서 비등방성 기생 특징 마스킹

```python
def saxs_background_subtraction(I_sample, I_buffer, I_empty,
                                  transmission_sample, transmission_buffer):
    """Standard SAXS background subtraction with transmission correction."""
    I_corrected = (I_sample / transmission_sample -
                   I_buffer / transmission_buffer)
    return I_corrected
```

### 소프트웨어 도구

- **SASView / sasmodels** — 배경 처리를 포함한 종합 SAXS/SANS 분석
- **ATSAS (EMBL)** — 자동 배경 추정 기능을 갖춘 PRIMUS, GNOM
- **pyFAI** — 마스킹을 지원하는 빠른 방위각 적분(ESRF)
- **Dawn Science** — Diamond Light Source 처리 파이프라인

## 주요 참고문헌

- **Glatter & Kratky (1982)** — "Small Angle X-ray Scattering" — 기초 교과서
- **Pauw (2013)** — "Everything SAXS: small-angle scattering pattern collection and correction"
- **Li et al. (2008)** — "Scatterless hybrid metal–single-crystal slit for SAXS"
- **ESRF ID02 beamline documentation** — 기생 산란 완화 전략

## 시설별 벤치마크

| 시설 | 빔라인 | 접근법 |
|------|--------|--------|
| ESRF | ID02 | 무산란 슬릿 + 34m 진공 경로 |
| DESY PETRA III | P12 (EMBL) | 자동화된 버퍼 차감 파이프라인 |
| Diamond | I22 | 가드 슬릿 + 진공 카메라 |
| SPring-8 | BL40B2 | 정밀 슬릿 시스템 + He 경로 |
| APS | 12-ID-B | 핀홀 콜리메이션 + 진공 |

## 실제 보정 전후 예시

다음 출판된 자료들은 실제 실험적 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림/위치 | 설명 | 라이선스 |
|------|------|----------|------|---------|
| [Ashiotis et al. 2015 — pyFAI](https://doi.org/10.1107/S1600576715004306) | 논문 | 다수 | pyFAI: 고성능 방위각 적분을 위한 Python 라이브러리 — 기생 산란 제거를 위한 마스킹 적분 예시 | MIT |
| [pyFAI documentation](https://pyfai.readthedocs.io/) | 소프트웨어 문서 | 튜토리얼 | 기생 산란 및 빔스톱 그림자 마스킹을 보여주는 pyFAI 방위각 적분 튜토리얼 | MIT |

**출판된 보정 전후 비교를 포함한 주요 참고문헌:**
- **Ashiotis et al. (2015)**: 기생 산란 제거를 보여주는 pyFAI 방위각 적분 마스킹 예시. DOI: 10.1107/S1600576715004306

## 관련 자료

- [산란 아티팩트](../medical_imaging/scatter_artifact.md) — CT 기하에서의 산란
- [빔 강도 강하](../tomography/beam_intensity_drop.md) — 정규화에 관련된 I0 모니터링
