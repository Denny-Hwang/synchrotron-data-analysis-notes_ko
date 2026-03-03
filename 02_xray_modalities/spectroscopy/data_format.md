# 분광법 데이터 형식

## 원시 데이터: 에너지-흡수 스펙트럼

### 표준 XAS 데이터 (ASCII)

대부분의 XAS 데이터는 단순한 열 형식의 ASCII 파일로 교환됩니다:

```
# Fe K-edge XANES
# Sample: Soil sample A
# Beamline: 20-BM, APS
# Date: 2025-01-15
# Columns: Energy(eV)  I0  I1  IF  mu_transmission  mu_fluorescence
7100.0   234567   223456   1234   0.0487   0.00526
7100.5   234789   223567   1256   0.0489   0.00535
7101.0   234890   223678   1278   0.0490   0.00544
...
7200.0   235678   198765   8765   0.1721   0.03722
...
```

### 열 정의

| 열 | 설명 | 단위 |
|--------|-------------|-------|
| `Energy` | 입사 X선 에너지 | eV |
| `I0` | 입사 빔 강도 (이온 챔버) | counts |
| `I1` | 투과 빔 강도 | counts |
| `IF` | 형광 강도 | counts |
| `mu_trans` | 흡수 계수 (투과) | -ln(I1/I0) |
| `mu_fluor` | 흡수 계수 (형광) | IF/I0 |

### HDF5 형식 (µ-XANES 이미징용)

```
xanes_imaging.h5
├── /exchange/
│   ├── /data          [shape: (Nenergies, Ny, Nx), dtype: float32]
│   │                   # 각 에너지에서의 흡수 맵
│   ├── /energy        [shape: (Nenergies,), dtype: float64]
│   │                   # 에너지 값 (eV)
│   └── /positions/
│       ├── /x         [shape: (Nx,)]
│       └── /y         [shape: (Ny,)]
│
├── /metadata/
│   ├── /element       # "Fe"
│   ├── /edge          # "K"
│   ├── /edge_energy   # 7112.0 eV
│   └── /beamline      # "20-BM"
│
└── /references/
    ├── /standard_1/
    │   ├── /name      # "Fe2O3 (hematite)"
    │   ├── /spectrum   [shape: (Nenergies,)]
    │   └── /oxidation_state  # "Fe(III)"
    └── /standard_2/
        ├── /name      # "FeO (wüstite)"
        └── ...
```

### Athena 프로젝트 파일 (.prj)

Athena (Demeter/Larch 스위트의 일부)는 자체 프로젝트 형식을 사용합니다:
- 처리 파라미터와 함께 여러 스펙트럼을 저장
- 정규화(normalization), 배경 차감(background subtraction) 설정 포함
- 표준 ASCII, JSON으로 내보내기 가능

## Python 데이터 로딩

```python
import numpy as np

# ASCII XAS 데이터 로드
def load_xas_ascii(filename):
    """Load standard XAS ASCII data file."""
    data = np.loadtxt(filename, comments='#')
    energy = data[:, 0]      # eV
    i0 = data[:, 1]
    i1 = data[:, 2]          # transmission
    i_fluor = data[:, 3]     # fluorescence

    # Calculate absorption coefficient
    mu_trans = -np.log(i1 / i0)
    mu_fluor = i_fluor / i0

    return energy, mu_trans, mu_fluor

# larch를 사용한 로드 (종합 XAS 라이브러리)
import larch
from larch.io import read_ascii
from larch.xafs import pre_edge, autobk

group = read_ascii('fe_spectrum.dat')
pre_edge(group)         # normalize: sets group.norm, group.edge_step
autobk(group)           # background subtraction: sets group.chi, group.k

# Access processed data
energy = group.energy   # eV
norm = group.norm       # normalized µ(E)
k = group.k             # wavenumber (Å⁻¹)
chi_k = group.chi       # χ(k) EXAFS oscillations

# µ-XANES 이미징 로드
import h5py

with h5py.File('xanes_imaging.h5', 'r') as f:
    energy_stack = f['/exchange/data'][:]    # (Nenergies, Ny, Nx)
    energies = f['/exchange/energy'][:]       # (Nenergies,)
```

## 처리 단계

### 1. 에너지 교정(Energy Calibration)
- 알려진 표준 시료의 값에 맞춰 모서리 에너지를 정렬
- 스캔 간 단색화기(monochromator) 드리프트 보정
- 정확한 종분화(speciation)를 위해 필수적

### 2. 정규화 (Pre-edge / Post-edge)
```python
# XAS 스펙트럼 정규화:
# 1. Fit pre-edge region (linear/polynomial) → extrapolate as baseline
# 2. Fit post-edge region (linear/polynomial) → extrapolate as post-edge line
# 3. Normalized µ(E) = [µ(E) - pre_edge(E)] / [post_edge(E₀) - pre_edge(E₀)]
```

### 3. 배경 차감 (EXAFS용)
```python
# AUTOBK algorithm (Newville et al.):
# - Fit smooth spline to post-edge µ(E) as µ₀(E)
# - χ(E) = [µ(E) - µ₀(E)] / Δµ₀
# - Convert E → k: k = √(2m(E-E₀)/ℏ²)
# - Weight: χ(k) × k^n (n = 1, 2, or 3)
```

### 4. 푸리에 변환 (EXAFS → 실공간)
```python
# FT of k-weighted χ(k) gives radial distribution function:
# χ̃(R) = FT[k^n × χ(k) × W(k)]
# Peaks correspond to coordination shells (shifted from true distance)
```

### 5. 선형 결합 피팅(Linear Combination Fitting, LCF)
```python
# Fit unknown spectrum as weighted sum of reference standards:
# µ_sample(E) = Σᵢ fᵢ × µ_ref_i(E) + residual
# subject to: Σ fᵢ = 1, fᵢ ≥ 0
#
# Provides: fraction of each chemical species in the sample
```

## 주요 소프트웨어

| 소프트웨어 | 설명 | 언어 |
|----------|-------------|---------|
| **Larch** | 종합 XAS 분석 (IFEFFIT 후속) | Python |
| **Athena** | XANES 처리용 GUI (Demeter 패키지) | Perl/GUI |
| **Artemis** | EXAFS 피팅용 GUI | Perl/GUI |
| **FEFF** | 제일원리(ab initio) XAFS 계산 | Fortran |
| **FDMNES** | 결정 구조로부터의 XANES 시뮬레이션 | Fortran |
