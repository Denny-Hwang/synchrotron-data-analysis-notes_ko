# 토모그래피 데이터 형식

## 원시 데이터: 투영

### HDF5 (Data Exchange 형식)

**Data Exchange** 형식은 APS 싱크로트론 토모그래피의 표준 HDF5 스키마입니다:

```
scan.h5
├── /exchange/
│   ├── /data              [shape: (Nangles, Ny, Nx), dtype: uint16/float32]
│   │                      # 투영 이미지
│   ├── /data_white        [shape: (Nflat, Ny, Nx), dtype: uint16/float32]
│   │                      # 플랫필드 (개방빔) 이미지
│   ├── /data_dark         [shape: (Ndark, Ny, Nx), dtype: uint16/float32]
│   │                      # 다크필드 (빔 없음) 이미지
│   └── /theta             [shape: (Nangles,), dtype: float32]
│                          # 회전 각도 (도)
│
├── /measurement/
│   ├── /instrument/
│   │   ├── /monochromator/
│   │   │   └── /energy    # X선 에너지 (keV)
│   │   ├── /detector/
│   │   │   ├── /manufacturer
│   │   │   ├── /model
│   │   │   ├── /pixel_size   # µm
│   │   │   └── /exposure_time # 초
│   │   └── /source/
│   │       ├── /beamline
│   │       └── /current   # 링 전류 (mA)
│   └── /sample/
│       ├── /name
│       ├── /description
│       └── /experimenter
│
└── /process/
    └── /acquisition/
        ├── /rotation/
        │   ├── /range     # 총 회전 (°)
        │   └── /num_angles
        └── /magnification
```

### TIFF 스택 (레거시)

일부 빔라인은 여전히 개별 TIFF 파일을 출력합니다:

```
scan_001/
├── proj_0000.tif    # 0° 각도의 투영
├── proj_0001.tif    # Δθ 각도의 투영
├── ...
├── proj_1799.tif    # 179.9° 각도의 투영
├── flat_0000.tif    # 플랫필드 이미지 1
├── flat_0001.tif    # 플랫필드 이미지 2
├── dark_0000.tif    # 다크필드 이미지 1
└── dark_0001.tif    # 다크필드 이미지 2
```

## 중간 데이터: 사이노그램

정규화 후 데이터를 **사이노그램**으로 재배열할 수 있습니다 — 시료의 각 수평 슬라이스당
하나의 사이노그램:

```
사이노그램 형태: (Nangles, Nx)
    - 각 행 = 하나의 투영 각도
    - 각 열 = 하나의 검출기 열 (공간 위치)
    - 검출기 행(슬라이스)당 하나의 사이노그램
```

사이노그램은 재구성 알고리즘의 자연스러운 입력입니다.

## 재구성된 데이터: 3D 볼륨

### 재구성된 볼륨 구조

```
reconstructed.h5
├── /exchange/
│   └── /data     [shape: (Nz, Ny, Nx), dtype: float32]
│                  # 3D 감쇠 계수 맵
└── /metadata/
    ├── /pixel_size   # µm
    ├── /algorithm     # "FBP", "SIRT", "gridrec"
    └── /center        # 회전 중심 (픽셀)
```

### TIFF 스택 출력

```
recon_slices/
├── recon_0000.tif    # 슬라이스 z=0
├── recon_0001.tif    # 슬라이스 z=1
├── ...
└── recon_2047.tif    # 슬라이스 z=2047
```

### 일반적 볼륨 크기

| 검출기 | 볼륨 차원 | 크기 (16비트) | 크기 (32비트) |
|--------|----------|-------------|-------------|
| 2048×2048 | 2048×2048×2048 | 16 GB | 32 GB |
| 4096×4096 | 4096×4096×4096 | 128 GB | 256 GB |

## Python 데이터 로딩

```python
import h5py
import numpy as np

# Data Exchange HDF5 로드
with h5py.File('scan.h5', 'r') as f:
    projections = f['/exchange/data'][:]        # (Nangles, Ny, Nx)
    flat_fields = f['/exchange/data_white'][:]  # (Nflat, Ny, Nx)
    dark_fields = f['/exchange/data_dark'][:]   # (Ndark, Ny, Nx)
    theta = f['/exchange/theta'][:]             # (Nangles,)

    print(f"Projections: {projections.shape}")
    print(f"Angles: {theta[0]:.1f}° to {theta[-1]:.1f}°")

# 투영 정규화
dark = np.mean(dark_fields, axis=0)
flat = np.mean(flat_fields, axis=0)
normalized = (projections - dark) / (flat - dark + 1e-6)

# 음의 로그 변환 (Beer-Lambert)
sinograms = -np.log(np.clip(normalized, 1e-6, None))

# TIFF 스택 로드
import tifffile
projections = tifffile.imread('scan_001/proj_*.tif')  # shape: (Nangles, Ny, Nx)
```

## 전처리 단계

### 1. 다크/플랫 필드 보정
```
corrected = (projection - dark_mean) / (flat_mean - dark_mean)
```
검출기 배경을 제거하고 불균일한 빔 강도를 정규화합니다.

### 2. 음의 로그 변환
```
sinogram = -log(corrected)
```
투과율을 감쇠 계수의 선적분으로 변환합니다.

### 3. 링 아티팩트 제거
- **푸리에 필터링**: 사이노그램 도메인에서의 고역 통과 필터
- **TomoPy `remove_stripe_*`**: 다중 알고리즘 (Vo, Münch 등)
- 결함/오보정된 검출기 픽셀에 의한 아티팩트를 제거

### 4. 회전 중심 결정
- 재구성 품질에 결정적
- 방법: Vo 알고리즘, 위상 상관, 수동 최적화
- 1 픽셀의 오차만으로도 가시적 아티팩트 발생

### 5. 위상 복원 (선택사항)
- 위상대비 데이터의 경우: Paganin 단일거리 위상 복원
- 엣지 향상 대비를 면적 대비로 변환
- 저대비 물질(생물학적 시료)의 분할 개선
