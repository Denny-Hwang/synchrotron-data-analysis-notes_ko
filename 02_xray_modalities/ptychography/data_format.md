# 타이코그래피 데이터 형식

## 원시 데이터: 회절 패턴

### CXI 형식 (Coherent X-ray Imaging)

**CXI 형식** (HDF5 기반)은 결맞음 이미징 데이터를 위한 새로운 표준입니다:

```
scan_ptycho.cxi
├── /entry_1/
│   ├── /data_1/
│   │   └── /data            [shape: (Npositions, Ny_det, Nx_det), dtype: uint16/float32]
│   │                         # 회절 패턴 (스캔 위치당 하나)
│   │                         # 일반적: (2000, 256, 256) 또는 (5000, 512, 512)
│   │
│   ├── /sample_1/
│   │   └── /geometry_1/
│   │       └── /translation  [shape: (Npositions, 3), dtype: float64]
│   │                         # 스캔 위치 (미터 단위) (x, y, z)
│   │
│   ├── /instrument_1/
│   │   ├── /detector_1/
│   │   │   ├── /distance     # 시료-검출기 거리 (m), 예: 2.0
│   │   │   ├── /x_pixel_size # 검출기 픽셀 크기 (m), 예: 75e-6
│   │   │   ├── /y_pixel_size
│   │   │   ├── /corner_position  [shape: (3,)]
│   │   │   │                     # 검출기 모서리 위치 (미터)
│   │   │   └── /mask         [shape: (Ny_det, Nx_det), dtype: uint8]
│   │   │                     # 불량 픽셀 마스크 (1 = 유효, 0 = 마스킹)
│   │   │
│   │   ├── /source_1/
│   │   │   ├── /energy       # 광자 에너지 (eV), 예: 8000
│   │   │   └── /wavelength   # 파장 (m)
│   │   │
│   │   └── /illumination_1/
│   │       └── /probe        [shape: (Ny_probe, Nx_probe), dtype: complex64]
│   │                         # 초기 probe 추정값 (선택 사항)
│   │
│   └── /image_1/
│       ├── /data_real        [shape: (Ny_obj, Nx_obj), dtype: float32]
│       │                     # 복원된 object (실수 부분)
│       ├── /data_imag        [shape: (Ny_obj, Nx_obj), dtype: float32]
│       │                     # 복원된 object (허수 부분)
│       ├── /data_phase       [shape: (Ny_obj, Nx_obj), dtype: float32]
│       │                     # 위상 이미지 (라디안)
│       └── /data_amplitude   [shape: (Ny_obj, Nx_obj), dtype: float32]
│                             # 진폭 이미지
```

### APS HDF5 형식

APS 빔라인은 간소화된 HDF5 형식을 사용할 수 있습니다:

```
scan.h5
├── /exchange/
│   ├── /data              [shape: (Npositions, Ny_det, Nx_det)]
│   │                       # 회절 패턴
│   ├── /positions_x       [shape: (Npositions,)]
│   │                       # X 스캔 위치 (µm)
│   ├── /positions_y       [shape: (Npositions,)]
│   │                       # Y 스캔 위치 (µm)
│   └── /theta             [shape: (Nangles,)]  # 타이코-토모용
│
├── /instrument/
│   ├── /detector/
│   │   ├── /distance      # meters
│   │   └── /pixel_size    # meters
│   └── /source/
│       └── /energy        # keV
```

## 메타데이터

### 필수 파라미터

| 파라미터 | 설명 | 일반적 값 |
|-----------|-------------|---------------|
| `energy` | 광자 에너지 | 8–12 keV |
| `wavelength` | X선 파장 | 0.1–0.2 nm |
| `detector_distance` | 시료-검출기 거리 | 1–5 m |
| `pixel_size` | 검출기 픽셀 크기 | 55–75 µm |
| `scan_positions` | 프레임당 (x, y) 좌표 | µm 정밀도 |
| `step_size` | 위치 간 공칭 간격 | 50–500 nm |
| `exposure_time` | 위치당 적분 시간 | 0.5–100 ms |

### 유도 파라미터

```
# 복원 이미지의 픽셀 크기:
dx_recon = wavelength × detector_distance / (N_pixels × pixel_size_detector)

# 예시: λ=0.155 nm, z=2 m, N=256, pixel=75 µm
# dx_recon = 0.155e-9 × 2 / (256 × 75e-6) = 16.1 nm
```

## Python 데이터 로딩

```python
import h5py
import numpy as np

# CXI 형식 로드
with h5py.File('scan_ptycho.cxi', 'r') as f:
    # Diffraction patterns
    patterns = f['/entry_1/data_1/data'][:]
    print(f"Patterns: {patterns.shape}")  # (Npos, Ny, Nx)

    # Scan positions (meters → micrometers)
    positions = f['/entry_1/sample_1/geometry_1/translation'][:] * 1e6
    pos_x = positions[:, 0]
    pos_y = positions[:, 1]

    # Detector parameters
    distance = f['/entry_1/instrument_1/detector_1/distance'][()]
    pixel_size = f['/entry_1/instrument_1/detector_1/x_pixel_size'][()]
    energy_eV = f['/entry_1/instrument_1/source_1/energy'][()]

    # Wavelength
    wavelength = 12398.4 / energy_eV * 1e-10  # eV → meters

    # Pixel size in reconstruction
    N = patterns.shape[-1]
    dx_recon = wavelength * distance / (N * pixel_size)
    print(f"Reconstruction pixel size: {dx_recon*1e9:.1f} nm")

# 복원된 이미지 로드
with h5py.File('reconstruction.cxi', 'r') as f:
    phase = f['/entry_1/image_1/data_phase'][:]
    amplitude = f['/entry_1/image_1/data_amplitude'][:]

    # Complex object
    obj = amplitude * np.exp(1j * phase)
```

## 복원된 데이터

### 출력 형식

```
reconstruction.h5
├── /object/
│   ├── /complex           [shape: (Ny, Nx), dtype: complex64]
│   ├── /phase             [shape: (Ny, Nx), dtype: float32]
│   ├── /amplitude         [shape: (Ny, Nx), dtype: float32]
│   └── /pixel_size        # meters
│
├── /probe/
│   ├── /complex           [shape: (Ny_probe, Nx_probe), dtype: complex64]
│   └── /modes             [shape: (Nmodes, Ny_probe, Nx_probe), dtype: complex64]
│                          # 혼합 상태(mixed-state) / 부분 결맞음(partial coherence)용
│
└── /metrics/
    ├── /error_per_iteration  [shape: (Niterations,)]
    ├── /algorithm             # "ePIE", "DM", "LSQ-ML"
    └── /n_iterations          # 총 반복 횟수
```

### 타이코-토모그래피 3D

타이코그래피 토모그래피의 경우, 각 각도에서 2D 위상 이미지를 복원한 후 토모그래피 복원을 적용합니다:

```
ptycho_tomo/
├── angle_000/
│   ├── phase.tif          # 0°에서의 위상 이미지
│   └── amplitude.tif
├── angle_001/
│   ├── phase.tif          # 1°에서의 위상 이미지
│   └── amplitude.tif
├── ...
└── reconstructed_3d.h5
    └── /volume [shape: (Nz, Ny, Nx), dtype: float32]
        # 3D 전자 밀도 맵
```

## 전처리 요구 사항

1. **암전류 차감(dark subtraction)**: 검출기 암전류 제거
2. **핫 픽셀 마스킹(hot pixel masking)**: 결함 픽셀 식별 및 마스킹
3. **질량 중심 정렬(center of mass alignment)**: 회절 패턴을 공통 중심에 정렬
4. **배경 차감(background subtraction)**: 공기 산란 및 기생 산란(parasitic scattering) 제거
5. **포화 처리(saturation handling)**: 빔 스톱(beam stop) 근처의 포화 픽셀을 마스킹 또는 스케일링
6. **위치 보정(position refinement)**: 스캔 위치 보정 (간섭계 또는 이미지 기반)
