# XRF + Ptychography: 동시적 구조 및 원소 매핑

## 개요

빔라인 **2-ID-E** (및 향후 33-ID-C)에서는 XRF와 ptychography 데이터가
동시에 수집됩니다: 동일한 집속 X선 빔이 각 스캔 위치에서 형광 신호와
결맞음 회절 패턴을 모두 생성합니다.

## 실험 설정

```
집속된 결맞음 X선 빔
    │
    ▼
스캐닝 스테이지 위의 시료
    │
    ├──→ 형광 검출기 (90°)  → 원소 맵 (XRF)
    │         Vortex SDD
    │
    └──→ 픽셀화된 면적 검출기    → 위상 + 진폭 (ptychography)
              (원거리장)
              Eiger 500K
```

동일한 스캔 위치에서 두 신호 수집 → **자연적으로 공동 정합(co-registered)**.

## 데이터 구조

```
combined_scan.h5
├── /xrf/
│   ├── /spectra       [shape: (Npos, Nchannels)]   # 원시 XRF 스펙트럼
│   ├── /elemental_maps/
│   │   ├── /Fe        [shape: (Ny, Nx)]
│   │   ├── /Zn        [shape: (Ny, Nx)]
│   │   └── ...
│   └── /positions     [shape: (Npos, 2)]
│
├── /ptychography/
│   ├── /diffraction   [shape: (Npos, Ndet_y, Ndet_x)]  # 회절 패턴
│   └── /positions     [shape: (Npos, 2)]  # XRF 위치와 동일
│
└── /reconstructed/
    ├── /phase          [shape: (Ny_recon, Nx_recon)]
    ├── /amplitude      [shape: (Ny_recon, Nx_recon)]
    └── /pixel_size     # nm
```

## 통합 접근법

### 1. 오버레이 시각화(Overlay Visualization)

가장 간단한 접근법: XRF 원소 맵을 ptychography 위상 이미지 위에 중첩.

```python
import matplotlib.pyplot as plt
import numpy as np

# Ptychography가 구조적 맥락을 제공
# XRF가 원소 정체성을 제공

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(phase_image, cmap='gray', alpha=1.0)
ax.imshow(fe_map_resampled, cmap='hot', alpha=0.5)
ax.set_title('Phase (structure) + Fe distribution (XRF)')
```

### 2. 상관 분석(Correlated Analysis)

```python
# 각 XRF 픽셀에서 구조적 특징 추출
# 원소 농도와 구조적 속성의 상관 분석

for cell_region in segmented_cells:
    # Ptychography에서: 위상 대비 값, 텍스처 특징
    phase_mean = phase_image[cell_region].mean()
    phase_std = phase_image[cell_region].std()

    # XRF에서: 원소 농도
    fe_conc = fe_map[cell_region].mean()
    zn_conc = zn_map[cell_region].mean()

    # 상관: Fe가 풍부한 영역이 다른 밀도를 가지는가?
```

### 3. 결합 재구성(Joint Reconstruction, 고급)

객체 모델을 공유하면서 XRF와 ptychography 이미지를 동시에 재구성:

```
공유 객체 모델:
  - 두께 t(x,y) ← 두 모달리티를 모두 제약
  - 조성 c_i(x,y) ← XRF에서의 원소 농도
  - 위상 φ(x,y) = Σ_i c_i(x,y) × δ_i × t(x,y)  ← 위상과 조성을 연결하는 물리

결합 최적화:
  min ||I_ptycho - |F{P·O}|²||² + ||I_xrf - σ_xrf(c_i, t)||²
```

## 이점

1. **자연적 공동 정합**: 동일 스캔 → 정렬 불필요
2. **상호 보완적 정보**: 구조(ptychography) + 조성(XRF)
3. **해상도 연결**: Ptychography 10 nm, XRF 50-100 nm
4. **정량적**: 두 가지 모두 정량적 측정을 제공
5. **자기 일관적**: 결합 재구성이 두 모달리티를 모두 제약

## 과제

1. **해상도 불일치**: Ptychography가 XRF보다 더 세밀한 해상도를 가짐
2. **다른 SNR**: XRF가 미량 원소에 대해 낮은 계수를 가질 수 있음
3. **계산 비용**: 결합 재구성의 계산량이 많음
4. **자기흡수(Self-absorption)**: XRF 신호가 시료 두께와 조성에 영향받음
5. **제한된 알고리즘**: 진정한 결합 분석을 지원하는 도구가 적음

## 향후 방향

- 결합 XRF + ptychography 분석을 위한 딥러닝
- Ptychography의 구조적 특징을 전이하여 XRF 분할 개선
- 쌍을 이루는 데이터셋으로 훈련된 다중 모달 기반 모델(foundation model)
- 스캐닝 중 실시간 결합 분석
