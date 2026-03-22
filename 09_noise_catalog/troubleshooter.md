# 증상 기반 트러블슈터

데이터에서 **무언가 잘못 보이지만** 원인이 확실하지 않을 때 이 가이드를 사용하세요. 관찰하는 증상을 선택하면 결정 트리가 가능한 원인으로 안내합니다.

> **사용 방법:** 아래에서 가장 잘 맞는 증상 카테고리를 선택하세요. 각 트리는 예/아니오 질문이나 다중 선택으로 원인을 좁혀갑니다. 코드 스니펫은 빠른 진단 검사를 제공합니다.

---

## 증상 카테고리

| # | 증상 | 관련 노이즈 유형 |
|---|------|-----------------|
| 1 | [원형/링 패턴](#1-원형링-패턴) | 링 아티팩트, 플랫필드 문제, 회전 중심 오류 |
| 2 | [고립된 밝은/어두운 점](#2-고립된-밝은어두운-점) | 징거, 데드/핫 픽셀, 검출기 문제 |
| 3 | [스트릭/줄무늬 패턴](#3-스트릭줄무늬-패턴) | 스트릭 아티팩트, 희소 각도, 빔 강도 저하, 링 아티팩트, 스캔 줄무늬 |
| 4 | [전체적인 입자감/노이즈](#4-전체적인-입자감노이즈) | 저선량 노이즈, 광자 계수 노이즈, EXAFS 통계 노이즈 |
| 5 | [흐림/디테일 손실](#5-흐림디테일-손실) | 모션 아티팩트, 회전 중심 오류, 프로브 흐림, 부분 코히어런스 |
| 6 | [강도/값 이상](#6-강도값-이상) | 빔 강도 저하, 데드타임 포화, 자기 흡수, I0 정규화 |
| 7 | [스펙트럼 이상](#7-스펙트럼-이상) | 방사선 손상, 에너지 교정 드리프트, 고조파 오염, 자기 흡수(XAS) |
| 8 | [경계/스티칭 아티팩트](#8-경계스티칭-아티팩트) | 스티칭 아티팩트, 위치 오류, 리청킹 데이터 무결성 |
| 9 | [의심스럽게 "너무 좋은" 특징](#9-의심스럽게-너무-좋은-특징) | DL 환각 |

---

## 1. 원형/링 패턴

**링이 회전축에 중심을 두고 있습니까?**

- **예 → 선명하고 잘 정의된 링?**
  - → **[링 아티팩트](tomography/ring_artifact.md)** (심각) — 사이노그램에서 스트라이프 제거 적용
  - → 넓거나 흐린 부분 호: **[플랫필드 문제](tomography/flatfield_issues.md)** (주요)
- **아니오 →**
  - 물체 엣지가 이중으로 보임: **[회전 중심 오류](tomography/rotation_center_error.md)** (심각)
  - 조밀한 포함물 주위의 링: **[스트릭 아티팩트](tomography/streak_artifact.md)** (심각)

```python
import numpy as np
sinogram = data[data.shape[0]//2]
col_std = np.std(sinogram, axis=0)
suspect_cols = np.where(col_std < np.median(col_std) * 0.1)[0]
print(f"데드 컬럼 (링 소스): {suspect_cols}")
```

---

## 2. 고립된 밝은/어두운 점

**어디에서 점이 보입니까?**

- 원시 투영 (단일 프레임만): **[징거](tomography/zinger.md)** (주요)
- 원시 투영 (모든 프레임에서 동일 픽셀): **[검출기 공통 문제](cross_cutting/detector_common_issues.md)** (주요)
- XRF 맵 (비정상적으로 밝거나 어두운): **[데드/핫 픽셀](xrf_microscopy/dead_hot_pixel.md)** (주요)
- 재구성된 CT (징거에서 유래): **[징거](tomography/zinger.md)** (주요)

```python
import numpy as np
diff = np.abs(np.diff(projections, axis=0))
threshold = np.median(diff) + 10 * np.std(diff)
zingers = np.where(diff > threshold)
print(f"잠재적 징거 발견: {len(zingers[0])}")
```

---

## 3. 스트릭/줄무늬 패턴

**방향과 맥락은?**

- 조밀한 물체에서의 밝은 스트릭 (CT): **[스트릭 아티팩트](tomography/streak_artifact.md)** (심각)
- 재구성 전체의 별 모양 스트릭: **[희소 각도 아티팩트](tomography/sparse_angle_artifact.md)** (주요)
- 사이노그램의 수평 줄무늬 (I0 저하와 함께): **[빔 강도 저하](tomography/beam_intensity_drop.md)** (주요)
- 사이노그램의 수직 줄무늬: **[링 아티팩트](tomography/ring_artifact.md)** (심각)
- XRF 맵의 줄무늬 (스캔 방향): **[스캔 줄무늬](xrf_microscopy/scan_stripe.md)** (주요)
- XRF 맵의 줄무늬 (I0 상관): **[I0 정규화](xrf_microscopy/i0_normalization.md)** (주요)
- 타일 경계의 줄무늬 (타이코그래피): **[스티칭 아티팩트](ptychography/stitching_artifact.md)** (경미)

```python
import numpy as np
n_projections = projections.shape[0]
detector_width = projections.shape[-1]
nyquist = int(np.pi/2 * detector_width)
print(f"투영 수: {n_projections}, 나이퀴스트 최소: {nyquist}")
print(f"{'과소 샘플링' if n_projections < nyquist else '정상'}")
```

---

## 4. 전체적인 입자감/노이즈

**어떤 유형의 데이터입니까?**

- CT 재구성 (균일 노이즈): **[저선량 노이즈](tomography/low_dose_noise.md)** (주요)
- CT 재구성 (조밀 영역에서 더 심함): **[스트릭 아티팩트](tomography/streak_artifact.md)** (주요)
- CT 재구성 (엣지에서 더 심함): **[플랫필드 문제](tomography/flatfield_issues.md)** (주요)
- XRF 맵 (저농도 원소가 더 노이즈): **[광자 계수 노이즈](xrf_microscopy/photon_counting_noise.md)** (주요)
- XRF 맵 (모든 원소가 노이즈): **[데드타임 포화](xrf_microscopy/dead_time_saturation.md)** (주요)
- EXAFS (높은 k에서 노이즈): **[EXAFS 통계 노이즈](spectroscopy/statistical_noise_exafs.md)** (주요)

```python
import numpy as np
roi_signal = recon[100:150, 100:150]
roi_bg = recon[10:30, 10:30]
snr = np.mean(roi_signal) / np.std(roi_bg)
print(f"SNR 추정: {snr:.1f} (< 5 매우 노이즈, > 20 양호)")
```

---

## 5. 흐림/디테일 손실

**어떤 유형의 데이터입니까?**

- CT — 방향성 흐림: **[모션 아티팩트](tomography/motion_artifact.md)** (심각)
- CT — 균일한 부드러움 (적은 투영?): **[희소 각도 아티팩트](tomography/sparse_angle_artifact.md)** (주요)
- CT — 이중 엣지: **[회전 중심 오류](tomography/rotation_center_error.md)** (심각)
- XRF — 특징이 예상보다 큼: **[프로브 흐림](xrf_microscopy/probe_blurring.md)** (경미)
- XRF — 일부 원소는 선명, 다른 것은 흐림: **[피크 겹침](xrf_microscopy/peak_overlap.md)** (주요)
- 타이코그래피 — 균일한 대비 손실: **[부분 코히어런스](ptychography/partial_coherence.md)** (주요)
- 타이코그래피 — FOV에 따라 변함: **[위치 오류](ptychography/position_error.md)** (심각)

---

## 6. 강도/값 이상

**무엇을 관찰합니까?**

- 사이노그램의 갑작스러운 강도 점프: **[빔 강도 저하](tomography/beam_intensity_drop.md)** (주요)
- XRF 농도 평탄화 (ICR/OCR 비정상): **[데드타임 포화](xrf_microscopy/dead_time_saturation.md)** (심각)
- XRF 농도 평탄화 (ICR/OCR 정상): **[자기 흡수](xrf_microscopy/self_absorption.md)** (주요)
- XRF 스캔의 체계적 기울기: **[I0 정규화](xrf_microscopy/i0_normalization.md)** (주요)
- 감쇠된 형광 (농축 시료): **[자기 흡수(XAS)](spectroscopy/self_absorption_xas.md)** (주요)
- 감쇠된 형광 (희석 시료): **[고조파 오염](spectroscopy/harmonics_contamination.md)** (주요)

---

## 7. 스펙트럼 이상

**스펙트럼의 무엇이 문제입니까?**

- 스캔 간 엣지가 단조 이동: **[방사선 손상](spectroscopy/radiation_damage.md)** (심각)
- 스캔 간 엣지가 무작위 이동: **[에너지 교정 드리프트](spectroscopy/energy_calibration_drift.md)** (심각)
- 화이트라인 평탄화 (형광, 농축): **[자기 흡수(XAS)](spectroscopy/self_absorption_xas.md)** (주요)
- XANES 특징 감쇠/왜곡: **[고조파 오염](spectroscopy/harmonics_contamination.md)** (주요)
- 개별 스캔이 평균과 다름: **[이상치 스펙트럼](spectroscopy/outlier_spectra.md)** (경미)
- EXAFS 진폭이 스캔과 함께 감소: **[방사선 손상](spectroscopy/radiation_damage.md)** (심각)

```python
import numpy as np
e0_values = []
for scan in scans:
    deriv = np.gradient(scan['mu'], scan['energy'])
    e0_values.append(scan['energy'][np.argmax(deriv)])
drift = max(e0_values) - min(e0_values)
print(f"엣지 드리프트: {drift:.2f} eV ({len(scans)}회 스캔) (> 0.5 eV 문제)")
```

---

## 8. 경계/스티칭 아티팩트

**불연속이 어디에 있습니까?**

- 타이코그래피 타일 경계 (위상 점프): **[스티칭 아티팩트](ptychography/stitching_artifact.md)** (경미)
- 타이코그래피에서 이동된 특징: **[위치 오류](ptychography/position_error.md)** (심각)
- HDF5 리청킹 후 누락/손상 데이터: **[리청킹 데이터 무결성](cross_cutting/rechunking_data_integrity.md)** (주요)
- 포맷 변환 후 누락/손상 데이터: **[리청킹 데이터 무결성](cross_cutting/rechunking_data_integrity.md)** (주요)

---

## 9. 의심스럽게 "너무 좋은" 특징

**신경망을 적용했습니까?**

- 예 — 저SNR 영역에서 고주파 디테일: **[DL 환각](cross_cutting/dl_hallucination.md)** (심각)
- 예 — 주기적/반복적 패턴 출현: **[DL 환각](cross_cutting/dl_hallucination.md)** (심각)
- 예 — 결과가 입력과 동일: 네트워크가 이 데이터 분포에 대해 훈련되지 않았을 수 있음
- 아니오 — 신경망 미사용: 다른 증상 카테고리를 재검토하세요

```python
import numpy as np
residual = dl_output - conventional_recon
residual_std = np.std(residual)
signal_std = np.std(conventional_recon)
print(f"잔차/신호 비율: {residual_std/signal_std:.3f}")
print(f"> 0.1이면 DL이 상당한 콘텐츠를 추가하고 있음 — 신중히 검증")
```

---

## 교차 참조 표

| 노이즈/아티팩트 | 증상 카테고리 |
|----------------|-------------|
| 링 아티팩트 | 원형 패턴, 스트릭/줄무늬 |
| 징거 | 고립 점, 스트릭 |
| 스트릭 아티팩트 | 스트릭/줄무늬, 입자감 |
| 저선량 노이즈 | 입자감 |
| 희소 각도 아티팩트 | 스트릭/줄무늬, 흐림 |
| 모션 아티팩트 | 흐림 |
| 플랫필드 문제 | 원형 패턴, 입자감 |
| 회전 중심 오류 | 원형 패턴, 흐림 |
| 빔 강도 저하 | 스트릭/줄무늬, 강도 이상 |
| 광자 계수 노이즈 | 입자감 |
| 데드/핫 픽셀 | 고립 점 |
| 피크 겹침 | 흐림 |
| 자기 흡수 (XRF) | 강도 이상 |
| 데드타임 포화 | 강도 이상, 입자감 |
| I0 정규화 | 스트릭/줄무늬, 강도 이상 |
| 프로브 흐림 | 흐림 |
| 스캔 줄무늬 | 스트릭/줄무늬 |
| EXAFS 통계 노이즈 | 입자감 |
| 에너지 교정 드리프트 | 스펙트럼 이상 |
| 고조파 오염 | 스펙트럼 이상, 강도 이상 |
| 자기 흡수 (XAS) | 스펙트럼 이상, 강도 이상 |
| 방사선 손상 | 스펙트럼 이상 |
| 이상치 스펙트럼 | 스펙트럼 이상 |
| 위치 오류 | 흐림, 경계 |
| 부분 코히어런스 | 흐림 |
| 스티칭 아티팩트 | 경계, 스트릭 |
| DL 환각 | 너무 좋은 특징 |
| 리청킹 무결성 | 경계 |
| 검출기 공통 문제 | 고립 점 |
