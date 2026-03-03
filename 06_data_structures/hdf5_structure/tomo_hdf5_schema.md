# 단층촬영 HDF5 스키마 (Data Exchange 형식)

## 개요

APS의 단층촬영 데이터셋은 Argonne에서 방사광 단층촬영을 위해 개발된 HDF5 기반 규약인
**Data Exchange** (DXchange) 형식을 따릅니다. 이 형식은 투영 이미지, 플랫필드 및
다크필드 참조, 회전 각도, 실험 메타데이터를 **TomoPy** 및 **TomocuPy**와 같은
재구성 도구에서 직접 사용할 수 있는 표준화된 계층으로 저장합니다.

APS BER 빔라인 (예: 2-BM, 7-BM, 32-ID)에서 단일 단층촬영 스캔은 시료가 180도 또는
360도로 회전하는 동안 수백에서 수천 개의 투영을 캡처합니다.

## Data Exchange HDF5 계층 구조

```
/exchange/
  data              [nproj, nrow, ncol]   uint16 / float32   # 투영 이미지
  data_white        [nflat, nrow, ncol]   uint16 / float32   # 플랫필드 (개방 빔)
  data_dark         [ndark, nrow, ncol]   uint16 / float32   # 다크필드 (빔 차단)
  theta             [nproj]               float32             # 회전 각도 (라디안)

/measurement/
  instrument/
    source/
      @name          = "APS"
      @energy        = 6.0                 # GeV 링 에너지
      @current       = 100.0               # mA 링 전류
    monochromator/
      @energy        = 20.0                # keV 빔 에너지
      @energy_mode   = "white" | "mono"
    detector/
      @manufacturer  = "Teledyne FLIR"
      @model         = "Oryx 10GigE"
      @pixel_size_x  = 6.5e-6             # 미터
      @pixel_size_y  = 6.5e-6
      @exposure_time = 0.01                # 초
      @binning       = 1
      roi_x          [2]  int32            # [시작, 크기] 픽셀
      roi_y          [2]  int32
    scintillator/
      @material      = "LuAG:Ce"
      @thickness     = 50e-6               # 미터 (50 um)
    objective/
      @magnification = 5.0

  sample/
    @name            = "rhizosphere_core_12"
    @description     = "Soil rhizosphere section, sieved < 2mm"
    experimenter/
      @name          = "J. Smith"
      @institution   = "ANL"
    environment/
      @temperature   = 22.0                # 섭씨
      @humidity      = 45.0                # 퍼센트

/process/
  acquisition/
    @start_date      = "2025-03-15T08:30:00"
    @end_date        = "2025-03-15T09:15:00"
    rotation/
      @range         = 180.0               # 도
      @num_angles    = 1800
      @speed         = 1.0                 # deg/sec (플라이 스캔용)
    flat_field/
      @num_images    = 20
      @frequency     = "every 200 projections"
```

## 일반적인 치수

| 매개변수 | 표준 (2-BM) | 고해상도 (32-ID) | Micro-CT (7-BM) |
|----------|-------------|-----------------|-----------------|
| 투영 수 (nproj) | 900--1800 | 1500--3600 | 1200--2400 |
| 행 (nrow) | 2048 | 2048--4096 | 2048 |
| 열 (ncol) | 2448 | 2048--4096 | 2448 |
| 플랫필드 수 (nflat) | 10--40 | 20--50 | 10--20 |
| 다크필드 수 (ndark) | 10--20 | 10--20 | 10--20 |
| 픽셀 크기 | 0.65--6.5 um | 0.03--1.0 um | 1.3--6.5 um |
| 파일 크기 | 8--20 GB | 20--100 GB | 5--15 GB |

## dxchange를 사용한 Python 로딩

```python
import dxchange

# Load all arrays in one call
proj, flat, dark, theta = dxchange.read_aps_32id(
    "tomo_scan_001.h5", sino=(500, 600)    # Load sinogram range [500:600]
)
print(f"Projections: {proj.shape}")         # (nproj, 100, ncol)
print(f"Flat fields: {flat.shape}")         # (nflat, 100, ncol)
print(f"Dark fields: {dark.shape}")         # (ndark, 100, ncol)
print(f"Theta:       {theta.shape}")        # (nproj,)
```

### 직접 h5py 접근

```python
import h5py
import numpy as np

with h5py.File("tomo_scan_001.h5", "r") as f:
    # Lazy access -- no data loaded yet
    proj_dset = f["/exchange/data"]
    print(f"Shape: {proj_dset.shape}, dtype: {proj_dset.dtype}")

    # Load a single projection
    proj_0 = proj_dset[0, :, :]

    # Load a sinogram slice
    sino = proj_dset[:, 1024, :]             # All angles, row 1024

    # Load theta
    theta = f["/exchange/theta"][:]

    # Read metadata
    energy = f["/measurement/instrument/monochromator"].attrs["energy"]
    px_size = f["/measurement/instrument/detector"].attrs["pixel_size_x"]
```

## 전처리 단계

재구성 전에 단층촬영 데이터는 여러 전처리 단계를 필요로 합니다. 각 단계는
일반적으로 다음 순서로 적용됩니다:

### 1. 다크필드 제거

평균 다크필드 이미지를 빼서 검출기 열 잡음을 제거합니다:

```python
import tomopy

dark_mean = np.mean(dark, axis=0)
proj_corrected = proj - dark_mean
flat_corrected = flat - dark_mean
```

### 2. 플랫필드 정규화

빔 비균일성과 이득 변동을 보정하기 위해 플랫필드로 투영을 정규화합니다:

```python
proj_norm = tomopy.normalize(proj, flat, dark)
```

### 3. 음의 로그

투과율을 흡수로 변환합니다 (Beer-Lambert 법칙):

```python
proj_norm = tomopy.minus_log(proj_norm)
```

### 4. 링 아티팩트 제거

불량 검출기 픽셀로 인한 링 아티팩트를 억제합니다:

```python
proj_clean = tomopy.remove_stripe_fw(proj_norm, level=7, wname="db5")
```

### 5. 위상 복원 (선택사항)

전파 기반 위상 대비 데이터의 경우:

```python
proj_phase = tomopy.retrieve_phase(
    proj_clean, pixel_size=px_size, dist=50.0,
    energy=energy, alpha=1e-3, pad=True
)
```

### 6. 회전 중심 찾기

회전 중심을 결정합니다 (재구성 품질에 핵심적):

```python
rot_center = tomopy.find_center_vo(proj_clean)
print(f"Rotation center: {rot_center:.2f} pixels")
```

### 7. 재구성

```python
recon = tomopy.recon(proj_clean, theta, center=rot_center, algorithm="gridrec")
recon = tomopy.circ_mask(recon, axis=0, ratio=0.95)
```

## 시계열 단층촬영

4D (3D + 시간) 실험의 경우, 여러 스캔이 시퀀스로 저장됩니다:

```
experiment_dir/
  tomo_t000.h5      # t = 0 min
  tomo_t010.h5      # t = 10 min
  tomo_t020.h5      # t = 20 min
  ...
```

각 파일은 동일한 Data Exchange 스키마를 따릅니다. 마스터 인덱스 파일은 다음을 제공할 수 있습니다:

```
/time_series/
  timestamps    [ntime]   float64        # 시작부터의 초
  filenames     [ntime]   bytes          # 상대 파일 경로
  conditions    [ntime]   bytes          # 시점별 실험 메모
```

## 관련 자료

- [Data Exchange 사양](https://dxchange.readthedocs.io/)
- [TomoPy 문서](https://tomopy.readthedocs.io/)
- [단층촬영 EDA 가이드](../eda/tomo_eda.md)
- [단층촬영 모달리티 개요](../../02_xray_modalities/)
