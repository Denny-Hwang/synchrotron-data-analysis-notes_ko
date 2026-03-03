# 산란 데이터 형식

## 원시 데이터: 2D 산란 패턴

### HDF5 형식 (EIGER/PILATUS 검출기)

```
saxs_data.h5
├── /entry/
│   ├── /instrument/
│   │   ├── /detector/
│   │   │   ├── /data              [shape: (Nframes, Ny, Nx), dtype: uint32]
│   │   │   │                       # 2D 산란 패턴
│   │   │   ├── /x_pixel_size      # 172 µm (PILATUS) 또는 75 µm (EIGER)
│   │   │   ├── /y_pixel_size
│   │   │   ├── /distance          # 시료-검출기 거리 (m)
│   │   │   ├── /beam_center_x     # pixels
│   │   │   ├── /beam_center_y
│   │   │   └── /mask              [shape: (Ny, Nx), dtype: uint8]
│   │   │                           # 불량 픽셀 / 빔 스톱 마스크
│   │   ├── /source/
│   │   │   ├── /energy            # keV
│   │   │   └── /wavelength        # Å
│   │   └── /sample/
│   │       ├── /name
│   │       ├── /temperature       # K 또는 °C
│   │       └── /concentration     # mg/mL (단백질 SAXS용)
│   │
│   └── /data/
│       └── /data -> /entry/instrument/detector/data
```

### XPCS 시계열

```
xpcs_timeseries.h5
├── /exchange/
│   ├── /data                  [shape: (Nframes, Ny, Nx), dtype: uint16]
│   │                           # 스페클 패턴 시계열
│   ├── /timestamps            [shape: (Nframes,), dtype: float64]
│   │                           # 프레임 타임스탬프 (초)
│   └── /frame_rate            # Hz
│
├── /instrument/
│   ├── /detector/
│   │   ├── /distance
│   │   ├── /pixel_size
│   │   └── /mask              [shape: (Ny, Nx)]
│   └── /source/
│       └── /energy
│
└── /metadata/
    ├── /temperature
    ├── /sample_name
    └── /q_range               # [q_min, q_max] (Å⁻¹)
```

## 처리된 데이터: 1D 프로파일

### 방위각 적분된 I(q)

주요 축약 데이터 산출물은 2D 패턴의 방위각 적분(azimuthal integration)으로 얻어지는 1D 산란 프로파일입니다:

```
# ASCII format (common exchange format)
# Sample: Protein_solution_1mgml
# Beamline: 12-ID-B, APS
# Energy: 12.0 keV
# Distance: 3.5 m
# q (Å⁻¹)    I(q) (cm⁻¹)    σ(I)
0.00500      125.678         2.345
0.00520      124.891         2.301
0.00540      123.567         2.278
...
0.50000      0.00123         0.00056
```

### HDF5 처리 형식

```
saxs_processed.h5
├── /data/
│   ├── /q                    [shape: (Nq,), dtype: float64]
│   │                          # 산란 벡터 (Å⁻¹)
│   ├── /I                    [shape: (Nsamples, Nq), dtype: float64]
│   │                          # 강도 프로파일
│   ├── /sigma                [shape: (Nsamples, Nq), dtype: float64]
│   │                          # 표준 편차
│   └── /sample_names         [shape: (Nsamples,)]
│
├── /guinier/
│   ├── /Rg                   # 회전 반경(Radius of gyration) (Å)
│   ├── /I0                   # 전방 산란 강도(forward scattering intensity)
│   ├── /qRg_range            # [qmin×Rg, qmax×Rg] (피팅 범위)
│   └── /guinier_plot         [shape: (Nq_guinier, 2)]
│                              # ln(I) vs q²
│
└── /processing/
    ├── /background_file
    ├── /normalization         # 예: "concentration"
    └── /software              # 예: "ATSAS", "pyFAI"
```

## XPCS 처리 데이터: 상관 함수

```
xpcs_processed.h5
├── /exchange/
│   ├── /norm-0-stderr        [shape: (Nq, Ntau)]
│   │                          # g₂ 표준 오차
│   ├── /norm-0-g2            [shape: (Nq, Ntau)]
│   │                          # g₂(q, τ) 상관 함수
│   ├── /tau                  [shape: (Ntau,), dtype: float64]
│   │                          # 지연 시간(delay times) (초)
│   ├── /qphi_bin_centers     [shape: (Nq,)]
│   │                          # 각 상관에 대한 q 값
│   └── /twotime/
│       └── /C_all            [shape: (Nq, Nframes, Nframes)]
│                              # 이시간 상관 행렬(two-time correlation matrices)
│
├── /fits/
│   ├── /tau_relaxation       [shape: (Nq,)]
│   │                          # 피팅된 완화 시간(relaxation times)
│   ├── /stretching_exponent  [shape: (Nq,)]
│   │                          # β 지수 (KWW 피팅)
│   └── /contrast             [shape: (Nq,)]
│                              # 스페클 대비(speckle contrast)
│
└── /metadata/
    ├── /temperature
    ├── /frame_rate
    └── /acquisition_time
```

## Python 데이터 로딩 및 처리

```python
import numpy as np
import h5py

# === SAXS: 로드 및 방위각 적분 ===
import pyFAI

# Setup integrator
ai = pyFAI.AzimuthalIntegrator(
    dist=3.5,              # sample-detector distance (m)
    poni1=0.085,           # beam center Y (m)
    poni2=0.085,           # beam center X (m)
    pixel1=172e-6,         # pixel size Y (m)
    pixel2=172e-6,         # pixel size X (m)
    wavelength=1.033e-10   # wavelength (m) for 12 keV
)

# Load 2D pattern
with h5py.File('saxs_data.h5', 'r') as f:
    pattern_2d = f['/entry/instrument/detector/data'][0]
    mask = f['/entry/instrument/detector/mask'][:]

# Azimuthal integration
q, I, sigma = ai.integrate1d(
    pattern_2d, 1000,       # number of bins
    mask=mask,
    unit='q_A^-1',          # q in Å⁻¹
    error_model='poisson'
)

# === XPCS: 로드 및 g2 계산 ===
with h5py.File('xpcs_processed.h5', 'r') as f:
    g2 = f['/exchange/norm-0-g2'][:]    # (Nq, Ntau)
    tau = f['/exchange/tau'][:]          # delay times
    q_values = f['/exchange/qphi_bin_centers'][:]

# 특정 q에서의 상관 함수 플롯
import matplotlib.pyplot as plt

q_idx = 5  # select q bin
plt.semilogx(tau, g2[q_idx], 'o-')
plt.xlabel('τ (s)')
plt.ylabel('g₂(q, τ)')
plt.title(f'q = {q_values[q_idx]:.4f} Å⁻¹')
```

## 전처리 단계

### SAXS/WAXS

1. **암전류 차감(dark subtraction)**: 검출기 암전류 제거
2. **평탄면 보정(flat-field correction)**: 픽셀 응답 정규화 (보통 검출기 펌웨어에서 적용)
3. **입체각 보정(solid angle correction)**: 검출기 전면에 걸친 입체각 변화 보정
4. **편광 보정(polarization correction)**: X선 빔 편광 보정
5. **마스킹(masking)**: 빔 스톱, 불량 픽셀, 모듈 간 간격 마스킹
6. **방위각 적분(azimuthal integration)**: 2D → 1D 프로파일 I(q)
7. **배경 차감(background subtraction)**: 용매/빈 캐필러리 산란 차감
8. **정규화(normalization)**: 농도, 투과율, 노출 시간별
9. **절대 스케일링(absolute scaling)**: glassy carbon 표준을 사용하여 cm⁻¹로 변환

### XPCS

1. **픽셀 마스킹**: 불량 픽셀 및 빔 스톱 그림자 제거
2. **q-비닝(q-binning)**: 다중 q 분석을 위해 픽셀을 q 빈에 할당
3. **다중 타우 상관(multi-tau correlation)**: 다중 타우 알고리즘을 사용하여 g₂(q,τ) 계산
4. **이시간 상관(two-time correlation)**: 비정상(non-stationary) 동역학을 위한 C(q, t₁, t₂) 계산
5. **피팅(fitting)**: 지수 함수 또는 늘어진 지수 함수(KWW) 모델로 g₂(τ) 피팅:
   ```
   g₂(τ) = 1 + β × exp(-2(τ/τ_r)^γ)
   where τ_r = relaxation time, γ = stretching exponent
   ```

## 주요 소프트웨어

| 소프트웨어 | 용도 | 언어 |
|----------|---------|---------|
| **pyFAI** | 방위각 적분 (SAXS/WAXS) | Python |
| **ATSAS** | BioSAXS 분석 스위트 | C/Fortran |
| **SASView** | SAXS/SANS 모델링 및 피팅 | Python |
| **XPCS-Eigen** | XPCS 상관 분석 | C++/Python |
| **Xana** | XPCS 데이터 분석 | Python |
| **scikit-beam** | 범용 산란 분석 | Python |
