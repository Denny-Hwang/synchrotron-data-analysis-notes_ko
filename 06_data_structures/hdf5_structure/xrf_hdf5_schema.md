# XRF HDF5 스키마 (MAPS 출력 형식)

## 개요

APS에서의 X선 형광 (XRF) 현미경 데이터는 주로 잘 정의된 HDF5 구조로 결과를 출력하는
**MAPS** (Microscopy Analysis and Processing Software)에 의해 처리됩니다. 각 HDF5
파일에는 단일 래스터 스캔에 대한 피팅된 원소 맵, 원시 스펙트럼, 교정 데이터, 스캔
메타데이터가 포함됩니다.

APS BER 빔라인 (2-ID-D, 2-ID-E)에서의 일반적인 XRF 데이터셋은 다음으로 구성됩니다:
- 시료 표면에 대한 2D 래스터 스캔
- 각 픽셀에서의 전체 에너지 분산 스펙트럼
- 피팅된 원소 농도 맵
- 정량화 표준 및 교정 곡선

## MAPS HDF5 그룹 계층 구조

```
/MAPS/
  Spectra/                      # 원시 및 적분 스펙트럼
    mca_arr         [nrow, ncol, nchan]   float32   # 픽셀당 원시 MCA 스펙트럼
    integrated_spectra [nchan]  float32              # 합산 스펙트럼
    energy           [nchan]    float32              # 에너지 축 (keV)
    energy_calib     [3]        float32              # 이차 교정 계수

  XRF_Analyzed/                 # 피팅된 원소 맵
    Fitted/
      Counts_Per_Sec  [nelem, nrow, ncol]  float32  # 원소별 피팅 카운트/초
    Channel_Names     [nelem]   bytes                # 원소 기호 ("Fe", "Cu", ...)
    Channel_Units     [nelem]   bytes                # "ug/cm2" 또는 "counts"

  XRF_ROI/                      # 관심 영역 적분 맵
    Counts_Per_Sec    [nroi, nrow, ncol]   float32
    ROI_Names         [nroi]    bytes
    ROI_Limits        [nroi, 2] float32              # 에너지 창 [low, high] keV

  Scalers/                      # 검출기 및 I0 스케일러
    Names             [nscaler] bytes                # "I0", "I1", "SRcurrent", ...
    Values            [nscaler, nrow, ncol] float32

  Scan/                         # 스캔 매개변수
    x_axis            [ncol]    float32              # X 위치 (마이크론)
    y_axis            [nrow]    float32              # Y 위치 (마이크론)
    scan_time_stamp   scalar    bytes                # ISO 8601 타임스탬프
    dwell_time        scalar    float32              # 픽셀당 체류 시간 (초)
    beamline          scalar    bytes                # "2-ID-D"
    incident_energy   scalar    float32              # keV
    detector_distance scalar    float32              # mm

  Quantification/               # 표준 및 교정
    Calibration_Curve [nelem, 2] float32             # 원소별 기울기 및 절편
    Standard_Name     scalar    bytes                # 예: "AXO_RF_7"
    Standard_Filenames [nstd]   bytes                # 참조 표준 파일
```

## 일반적인 치수

| 매개변수 | Microprobe (2-ID-D) | Bionanoprobe (9-ID) |
|----------|---------------------|---------------------|
| 행 (nrow) | 100--500 | 200--2000 |
| 열 (ncol) | 100--500 | 200--2000 |
| 채널 (nchan) | 2048 또는 4096 | 4096 |
| 원소 (nelem) | 10--25 | 10--30 |
| 픽셀 크기 | 0.5--5 um | 20--200 nm |
| 파일 크기 | 0.2--2 GB | 1--20 GB |

## Python 로딩 예제

### 구조 열기 및 검사

```python
import h5py
import numpy as np

filepath = "sample_xrf_scan.h5"

with h5py.File(filepath, "r") as f:
    # Print full tree structure
    def print_tree(name, obj):
        print(name)
    f.visititems(print_tree)

    # Check top-level groups
    print("Groups:", list(f["MAPS"].keys()))
```

### 원소 맵 로딩

```python
with h5py.File(filepath, "r") as f:
    maps = f["MAPS/XRF_Analyzed/Fitted/Counts_Per_Sec"][:]     # [nelem, nrow, ncol]
    element_names = [n.decode() for n in f["MAPS/XRF_Analyzed/Channel_Names"][:]]

    # Extract a single element map
    fe_idx = element_names.index("Fe")
    fe_map = maps[fe_idx]    # [nrow, ncol]

    print(f"Iron map shape: {fe_map.shape}")
    print(f"Fe range: {fe_map.min():.2f} -- {fe_map.max():.2f} ug/cm2")
```

### 원시 스펙트럼 로딩

```python
with h5py.File(filepath, "r") as f:
    spectra = f["MAPS/Spectra/mca_arr"]         # [nrow, ncol, nchan] -- lazy
    energy = f["MAPS/Spectra/energy"][:]         # [nchan]
    summed = f["MAPS/Spectra/integrated_spectra"][:]  # [nchan]

    # Extract spectrum from a single pixel
    pixel_spectrum = spectra[50, 75, :]          # Row 50, Col 75

    # Load a subregion only (memory efficient)
    roi_spectra = spectra[40:60, 70:90, :]       # 20x20 pixel ROI
```

### 스캔 좌표 및 스케일러 로딩

```python
with h5py.File(filepath, "r") as f:
    x = f["MAPS/Scan/x_axis"][:]                 # microns
    y = f["MAPS/Scan/y_axis"][:]
    dwell = f["MAPS/Scan/dwell_time"][()]         # scalar

    scaler_names = [n.decode() for n in f["MAPS/Scalers/Names"][:]]
    scaler_vals = f["MAPS/Scalers/Values"][:]     # [nscaler, nrow, ncol]

    i0_idx = scaler_names.index("I0")
    i0_map = scaler_vals[i0_idx]                  # Incident flux map
```

### 빠른 시각화

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

elements_to_plot = ["Fe", "Cu", "Zn"]
for ax, elem in zip(axes, elements_to_plot):
    idx = element_names.index(elem)
    im = ax.imshow(maps[idx], cmap="inferno", origin="lower",
                   extent=[x[0], x[-1], y[0], y[-1]])
    ax.set_title(elem)
    ax.set_xlabel("X (um)")
    ax.set_ylabel("Y (um)")
    plt.colorbar(im, ax=ax, label="ug/cm2")

plt.tight_layout()
plt.savefig("xrf_elemental_maps.png", dpi=150)
```

## 다중 검출기 처리

최신 XRF 빔라인은 4소자 또는 7소자 Vortex ME4/ME7 검출기를 사용합니다. MAPS 출력에서:

- 개별 검출기 스펙트럼은 `/MAPS/Spectra/mca_arr_detN` (N = 0, 1, 2, ...)에 저장됩니다
- 합산 배열 `/MAPS/Spectra/mca_arr`은 불감시간 보정 후 모든 검출기를 결합합니다
- 불감시간 보정 인자는 `/MAPS/Scalers/`에 검출기별 스케일러 채널로 포함됩니다

## 일괄 처리 패턴

데이터셋 디렉토리에서 여러 HDF5 파일을 스캔하는 경우:

```python
from pathlib import Path

data_dir = Path("/data/eBERlight/2024-3/xrf_scans/")
h5_files = sorted(data_dir.glob("*.h5"))

all_fe_maps = []
for fpath in h5_files:
    with h5py.File(fpath, "r") as f:
        names = [n.decode() for n in f["MAPS/XRF_Analyzed/Channel_Names"][:]]
        fe_idx = names.index("Fe")
        fe_map = f["MAPS/XRF_Analyzed/Fitted/Counts_Per_Sec"][fe_idx]
        all_fe_maps.append(fe_map)

print(f"Loaded {len(all_fe_maps)} Fe maps")
```

## 관련 자료

- [MAPS 소프트웨어 문서](https://www.aps.anl.gov/Microscopy/Software)
- [XRF EDA 가이드](../eda/xrf_eda.md)
- [XRF 모달리티 개요](../../02_xray_modalities/)
