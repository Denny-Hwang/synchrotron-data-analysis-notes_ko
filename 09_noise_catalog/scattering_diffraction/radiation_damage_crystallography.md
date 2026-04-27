# 결정학에서의 방사선 손상(Radiation Damage in Crystallography)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 거대분자 결정학(MX) / 분말 회절 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 방사광 결정학(모든 MX 빔라인) |

## 설명

결정학에서의 방사선 손상은 X선 유도 구조 변화로 인한 회절 데이터 품질의 점진적 저하입니다. 1차 손상(광전자 흡수)은 자유 라디칼을 생성하여 2차 화학적 손상을 유발합니다 — 이황화 결합 절단, 산성 잔기의 탈탄산화, 그리고 결국 결정 질서의 손실. 이는 이미 카탈로그된 분광학적 방사선 손상과 구별되며, 여기서는 결정학적 특징과 구조 결정에 미치는 영향에 초점을 맞춥니다.

## 근본 원인

- **1차 손상:** 광전자 흡수가 빠른 전자를 생성 → 이온화 캐스케이드
- **2차 손상:** 자유 라디칼(OH·, e⁻_aq)이 확산하여 특정 화학 그룹을 공격
- **전역 손상:** B-factor 증가, 고해상도 회절 손실, 단위 셀 확장
- **특이적 손상:** 이황화 결합, 카르복실산염, 메티오닌에서의 우선적 파괴
- Henderson 한계: 100K cryo 냉각 단백질 결정의 경우 ~2×10⁷ Gy (20 MGy)
- 비율은 다음에 의존: 선량률, 온도, 시료 조성, 용매 함량

## 빠른 진단

```python
import numpy as np

def track_radiation_damage(frame_intensities, resolution_shells):
    """Track intensity decay per resolution shell across frames."""
    n_frames = len(frame_intensities)
    for shell_idx, shell_name in enumerate(resolution_shells):
        intensities = [f[shell_idx] for f in frame_intensities]
        decay = intensities[-1] / intensities[0]
        print(f"Shell {shell_name}: I_last/I_first = {decay:.3f}")
        if decay < 0.7:
            print(f"  ⚠ Significant radiation damage in {shell_name} shell")
    # Check unit cell expansion
    # unit_cells = [get_unit_cell(frame) for frame in frames]
    # expansion = (unit_cells[-1] - unit_cells[0]) / unit_cells[0]
```

## 탐지 방법

### 시각적 지표

- 데이터 수집 중 회절 점이 점진적으로 희미해짐(특히 고해상도)
- Wilson plot에서 누적 선량에 따라 B-factor 증가
- 단위 셀 차원 증가(전체 데이터셋에서 0.1-1%)
- 후반 프레임의 R_merge 증가
- 차이 Fourier 맵이 이황화 결합에서 음의 밀도, 카르복실산염에서 양의 밀도를 표시

### 자동 탐지

```python
import numpy as np

def dose_dependent_bfactor(frame_number, mean_b_per_frame):
    """Fit linear dose-dependent B-factor increase."""
    slope, intercept = np.polyfit(frame_number, mean_b_per_frame, 1)
    print(f"B-factor increase rate: {slope:.2f} Å²/frame")
    print(f"Suggests {'severe' if slope > 1.0 else 'moderate' if slope > 0.3 else 'mild'} damage")
    return slope
```

## 보정 방법

### 예방

1. **Cryo 냉각 (100K):** 라디칼 확산을 상온 대비 ~100배 늦춤
2. **Helical 데이터 수집:** 회전 중 결정을 이동시켜 선량을 분산
3. **다중 결정 전략:** 여러 결정의 부분 데이터셋을 병합
4. **빔 감쇠:** 플럭스 밀도 감소(노출 시간과의 트레이드오프)
5. **라디칼 제거제:** Cryoprotectant 내 ascorbate, sodium nitrate

### 데이터 처리 보정

1. **제로 선량 외삽:** 감쇠 곡선을 사용하여 강도를 제로 선량으로 외삽
2. **프레임 거부:** Henderson 선량 한계를 넘는 프레임 폐기
3. **선량 가중 스케일링:** 누적 선량의 역수로 프레임 가중
4. **RIDL (Radiation-Induced Density Loss):** 원자별 손상 측정 분석

```python
def zero_dose_extrapolation(intensities_per_frame, doses):
    """Extrapolate reflection intensities to zero dose."""
    corrected = np.zeros(intensities_per_frame.shape[1])
    for i in range(intensities_per_frame.shape[1]):
        I_vs_dose = intensities_per_frame[:, i]
        valid = I_vs_dose > 0
        if valid.sum() >= 2:
            # Linear fit: I(d) = I(0) + slope * d
            slope, I0 = np.polyfit(doses[valid], I_vs_dose[valid], 1)
            corrected[i] = I0  # Zero-dose intensity
        else:
            corrected[i] = I_vs_dose[valid].mean() if valid.any() else 0
    return corrected
```

### 소프트웨어 도구

- **RADDOSE-3D** — MX 실험을 위한 선량 추정
- **BEST** — 선량을 고려한 최적 데이터 수집 전략
- **RIDL** — Radiation-Induced Density Loss 분석
- **AIMLESS / XSCALE** — 선량 의존적 스케일링

## 주요 참고문헌

- **Garman & Weik (2023)** — "Radiation damage in macromolecular crystallography" — 종합 리뷰
- **Henderson (1990)** — "Cryo-protection of protein crystals against radiation damage"
- **Zeldin et al. (2013)** — "RADDOSE-3D: time- and space-resolved modelling of dose in MX"
- **Bury et al. (2018)** — "RIDL: radiation-induced density loss analysis"
- **de la Mora et al. (2020)** — "Radiation damage and dose limits in serial synchrotron crystallography"

## 시설별 벤치마크

| 시설 | 접근법 |
|------|--------|
| ESRF (MASSIF) | 완전 자동화된 손상 인식 데이터 수집 |
| Diamond I04 | ISPyB 선량 추적 + BEST 전략 |
| SPring-8 ZOO | 다중 결정 직렬 접근법 |
| APS GM/CA | 래스터/벡터 데이터 수집 |
| SLS PXI/PXII | adp에서의 선량 계층화 처리 |
| NSLS-II FMX | Eiger 검출기 — 빠른 읽기로 프레임당 선량 최소화 |

## 관련 자료

- [방사선 손상 (분광학)](../spectroscopy/radiation_damage.md) — 분광학적 방사선 손상(XANES/EXAFS)
- [빔 강도 강하](../tomography/beam_intensity_drop.md) — 관련된 시간 의존적 신호 변화
