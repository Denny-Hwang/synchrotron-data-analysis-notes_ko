# 타이코그래피 HDF5 / CXI 스키마

## 개요

APS BER 빔라인 (예: 2-ID-D, 26-ID)에서의 타이코그래피 데이터셋은 코히어런트 회절 실험을
위해 CXIDB 커뮤니티에서 개발한 HDF5 기반 규약인 **CXI (Coherent X-ray Imaging)** 형식을
사용하여 저장됩니다. 이 형식은 회절 패턴, 스캔 위치, 프로브 정보, 검출기 기하학을
**PtychoNN**, **Tike**, **PyNX**와 같은 재구성 코드와 호환되는 표준화된 계층으로 저장합니다.

타이코그래피는 시료의 투과 함수의 진폭과 위상 모두를 복원하는 주사형 코히어런트 회절 기법으로,
집속 광학계의 한계를 훨씬 넘어 정기적으로 10 nm 미만의 공간 분해능을 달성합니다.

## CXI HDF5 계층 구조

```
/entry_1/
  @NX_class = "NXentry"

  instrument_1/
    @NX_class = "NXinstrument"

    source_1/
      energy          scalar     float64       # 광자 에너지 (eV)
      @units = "eV"

    detector_1/
      @NX_class = "NXdetector"
      data            [npos, ny_det, nx_det]  float32  # 회절 패턴
      distance        scalar     float64       # 시료-검출기 거리 (m)
      x_pixel_size    scalar     float64       # 검출기 픽셀 크기 (m)
      y_pixel_size    scalar     float64       # 검출기 픽셀 크기 (m)
      corner_position [3]        float64       # 실험실 프레임에서의 검출기 모서리 (m)
      mask            [ny_det, nx_det]  uint8  # 불량 픽셀 마스크 (0=양호, 1=불량)
      saturation_value scalar    float64       # 검출기 포화 임계값

    detector_1/detectorSpecific/
      countrate_correction_applied  scalar  int32
      flatfield_applied             scalar  int32
      pixel_mask                    [ny_det, nx_det]  uint32

  sample_1/
    @NX_class = "NXsample"
    @name = "biofilm_section_A"
    geometry_1/
      translation     [npos, 3]   float64     # 스캔 위치 (m), 열 = [x, y, z]
      @units = "m"

  data_1/
    @NX_class = "NXdata"
    data            -> /entry_1/instrument_1/detector_1/data   # 소프트 링크
    translation     -> /entry_1/sample_1/geometry_1/translation

  image_1/                                     # 재구성 결과 (선택사항)
    data            [ny_obj, nx_obj]  complex64 # 복소 객체 투과율
    @is_fft_shifted = 1
    mask            [ny_obj, nx_obj]  float32   # 지지 마스크
    process_1/
      @algorithm     = "ePIE"
      @iterations    = 500
      @error_metric  [500]  float32            # 수렴 이력
```

## 스캔 위치 규약

타이코그래피는 겹치는 조명 스팟을 필요로 합니다. 스캔 위치는 각 측정 지점에서의
프로브 중심을 정의합니다:

| 스캔 패턴 | 설명 | 일반적인 매개변수 |
|-----------|------|-------------------|
| 래스터 | 규칙적인 격자 | step = 100--400 nm, 중첩 60--75% |
| 페르마 나선 | 비주기적 나선 | npos = 200--5000, max_radius |
| 동심원 | 링 기반 | nrings, points_per_ring |
| 무작위 지터 | 격자 + 무작위 오프셋 | step + jitter_amplitude |

APS에서는 재구성에서 주기적 아티팩트를 방지하고 최소한의 위치로 거의 균일한 커버리지를
제공하는 페르마 나선이 선호됩니다.

```python
# Fermat spiral scan positions
import numpy as np

def fermat_spiral(n_points, step_size=100e-9):
    """Generate Fermat spiral scan positions."""
    golden_angle = np.pi * (3 - np.sqrt(5))
    indices = np.arange(n_points)
    radii = step_size * np.sqrt(indices)
    angles = golden_angle * indices
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack([x, y, np.zeros(n_points)])  # [npos, 3]
```

## 일반적인 치수

| 매개변수 | 연 X선 (2-ID-D) | 경 X선 (26-ID) |
|----------|-----------------|----------------|
| 위치 수 (npos) | 500--5000 | 200--2000 |
| 검출기 (ny, nx) | 256x256 | 512x512 또는 256x256 |
| 광자 에너지 | 500--2000 eV | 6000--12000 eV |
| 검출기 거리 | 1--3 m | 2--5 m |
| 픽셀 크기 (검출기) | 50--75 um | 50--75 um |
| 달성 분해능 | 5--20 nm | 8--50 nm |
| 파일 크기 | 0.5--5 GB | 1--10 GB |

## Python 로딩 예제

### CXI 파일 열기 및 검사

```python
import h5py
import numpy as np

filepath = "ptycho_scan_001.cxi"

with h5py.File(filepath, "r") as f:
    # Print structure
    def visitor(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f"  {name}: shape={obj.shape}, dtype={obj.dtype}")
        else:
            print(f"  {name}/")
    f.visititems(visitor)
```

### 회절 패턴 및 위치 로딩

```python
with h5py.File(filepath, "r") as f:
    # Diffraction patterns
    diff_dset = f["/entry_1/instrument_1/detector_1/data"]
    print(f"Diffraction patterns: {diff_dset.shape}")   # (npos, ny, nx)

    # Load a single pattern
    pattern_0 = diff_dset[0, :, :]

    # Scan positions in meters
    positions = f["/entry_1/sample_1/geometry_1/translation"][:]  # (npos, 3)
    pos_x = positions[:, 0] * 1e6   # Convert to microns
    pos_y = positions[:, 1] * 1e6

    # Detector parameters
    det = f["/entry_1/instrument_1/detector_1"]
    distance = det["distance"][()]           # meters
    px_size = det["x_pixel_size"][()]        # meters
    energy_eV = f["/entry_1/instrument_1/source_1/energy"][()]

    # Wavelength calculation
    h_c = 1.23984198e-6   # eV * m
    wavelength = h_c / energy_eV
    print(f"Wavelength: {wavelength*1e10:.4f} Angstrom")
```

### 검출기 마스크 로딩 및 적용

```python
with h5py.File(filepath, "r") as f:
    patterns = f["/entry_1/instrument_1/detector_1/data"][:]
    mask = f["/entry_1/instrument_1/detector_1/mask"][:]

    # Apply mask: set bad pixels to zero
    patterns_masked = patterns * (1 - mask)[np.newaxis, :, :]
```

### 스캔 커버리지 시각화

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Scan positions
axes[0].scatter(pos_x, pos_y, s=2, c=np.arange(len(pos_x)), cmap="viridis")
axes[0].set_xlabel("X (um)")
axes[0].set_ylabel("Y (um)")
axes[0].set_title("Scan Positions (Fermat Spiral)")
axes[0].set_aspect("equal")

# Log-scaled diffraction pattern
axes[1].imshow(np.log1p(patterns[len(patterns)//2]),
               cmap="gray", origin="lower")
axes[1].set_title("Central Diffraction Pattern (log scale)")

plt.tight_layout()
```

## 전처리 요구사항

재구성 전에 타이코그래피 데이터는 다음이 필요합니다:

1. **배경 제거** -- 검출기 다크 전류 제거
2. **핫/불량 픽셀 보정** -- 검출기 마스크를 사용한 보간
3. **크롭/비닝** -- 검출기 프레임을 코히어런트 스페클 영역으로 축소
4. **위치 보정** -- 교차상관 또는 재구성 중 결합 최적화를 통한 스캔 위치 정밀화
5. **프로브 초기화** -- 알려진 존 플레이트 또는 KB 미러 개구부의 프레넬 전파를 통한 초기 프로브 추정

## 재구성 출력

재구성은 복소 값 객체 배열을 생성하며, 여기서:
- **진폭** = 흡수 대비 (굴절률의 허수 부분인 beta와 관련)
- **위상** = 위상 이동 (굴절률의 실수 부분인 delta와 관련)

```python
# After reconstruction
obj = recon_object   # complex64 array [ny_obj, nx_obj]

amplitude = np.abs(obj)
phase = np.angle(obj)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].imshow(amplitude, cmap="gray")
axes[0].set_title("Amplitude")
axes[1].imshow(phase, cmap="twilight")
axes[1].set_title("Phase")
```

## 관련 자료

- [CXI 형식 사양 (CXIDB)](https://www.cxidb.org/cxi.html)
- [Tike 재구성 라이브러리](https://tike.readthedocs.io/)
- [PtychoNN -- 신경망 타이코그래피](https://github.com/mcherukara/PtychoNN)
- [타이코그래피 모달리티 개요](../../02_xray_modalities/)
