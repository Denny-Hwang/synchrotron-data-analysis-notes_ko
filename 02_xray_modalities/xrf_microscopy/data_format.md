# XRF 현미경 데이터 형식

## 원시 데이터: 전체 스펙트럼 맵

### HDF5 구조 (MAPS 출력)

APS에서의 XRF 데이터는 일반적으로 **MAPS** 소프트웨어를 통해 처리되어 다음 구조의
HDF5 파일을 생성합니다:

```
scan_xrf.h5
├── /MAPS/
│   ├── /Spectra/
│   │   ├── /mca_arr        [shape: (Ndet, Ny, Nx, Nchannels)]
│   │   │                    # 검출기별 픽셀별 원시 MCA 스펙트럼
│   │   │                    # Nchannels 일반적으로 2048
│   │   │                    # Ndet = 검출기 소자 수 (1-4)
│   │   └── /Integrated_Spectra/
│   │       └── /Spectra     [shape: (Nchannels,)]
│   │                        # 전체 맵에 대한 합산 스펙트럼
│   │
│   ├── /XRF_Analyzed/
│   │   ├── /Fitted/
│   │   │   ├── /Counts_Per_Sec  [shape: (Nelements, Ny, Nx)]
│   │   │   │                     # 피팅된 원소 맵
│   │   │   └── /Channel_Names   [shape: (Nelements,)]
│   │   │                         # 원소명: ['P', 'S', 'K', 'Ca', 'Fe', 'Zn', ...]
│   │   ├── /NNLS/               # 비음수 최소제곱 피팅
│   │   │   └── /Counts_Per_Sec  [shape: (Nelements, Ny, Nx)]
│   │   └── /ROI/                # 간단한 관심영역 적분
│   │       └── /Counts_Per_Sec  [shape: (Nelements, Ny, Nx)]
│   │
│   ├── /Scalers/
│   │   ├── /Names              # ['SRcurrent', 'us_ic', 'ds_ic', ...]
│   │   └── /Values             [shape: (Nscalers, Ny, Nx)]
│   │                           # 정규화 신호 (이온챔버, 전류)
│   │
│   └── /Scan/
│       ├── /x_axis             [shape: (Nx,)]  # X 위치 (µm)
│       ├── /y_axis             [shape: (Ny,)]  # Y 위치 (µm)
│       ├── /scan_time_stamp
│       └── /extra_pvs/                         # EPICS 프로세스 변수
│           ├── /Names
│           └── /Values
```

### 원시 검출기 데이터 (Pre-MAPS)

일부 실험은 원시 검출기 데이터도 저장합니다:

```
raw_data.h5
├── /entry/
│   ├── /instrument/
│   │   └── /detector/
│   │       ├── /data          [shape: (Nscanpoints, Nchannels)]
│   │       │                   # 원시 펄스 높이 스펙트럼
│   │       ├── /live_time     [shape: (Nscanpoints,)]
│   │       ├── /real_time     [shape: (Nscanpoints,)]
│   │       └── /dead_time     [shape: (Nscanpoints,)]
│   └── /data/
│       ├── /x_position        [shape: (Nscanpoints,)]
│       └── /y_position        [shape: (Nscanpoints,)]
```

## 메타데이터

### 필수 메타데이터 필드

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `incident_energy` | X선 에너지 (keV) | 10.0 |
| `dwell_time` | 픽셀당 적분 시간 (ms) | 100 |
| `step_size_x/y` | 스캔 스텝 크기 (µm) | 0.5, 0.5 |
| `beam_size` | 집속 빔의 FWHM (nm 또는 µm) | 200 nm |
| `detector_type` | 에너지분산형 검출기 모델 | "Vortex ME-4" |
| `ring_current` | 저장링 전류 (mA) | 100 |
| `us_ic / ds_ic` | 상류/하류 이온챔버 | (정규화) |

## Python 데이터 로딩

```python
import h5py
import numpy as np
import matplotlib.pyplot as plt

# MAPS 처리된 XRF 데이터 로드
with h5py.File('scan_xrf.h5', 'r') as f:
    # 원소명 가져오기
    channel_names = [name.decode() for name in
                     f['/MAPS/XRF_Analyzed/Fitted/Channel_Names'][:]]

    # 피팅된 원소 맵 로드
    elemental_maps = f['/MAPS/XRF_Analyzed/Fitted/Counts_Per_Sec'][:]
    # shape: (Nelements, Ny, Nx)

    # 위치 로드
    x_axis = f['/MAPS/Scan/x_axis'][:]
    y_axis = f['/MAPS/Scan/y_axis'][:]

    # 정규화 로드 (상류 이온챔버)
    scaler_names = [n.decode() for n in f['/MAPS/Scalers/Names'][:]]
    scalers = f['/MAPS/Scalers/Values'][:]
    ic_idx = scaler_names.index('us_ic')
    normalization = scalers[ic_idx]

# 사용 가능한 원소 출력
for i, name in enumerate(channel_names):
    print(f"{name}: min={elemental_maps[i].min():.1f}, "
          f"max={elemental_maps[i].max():.1f}, "
          f"mean={elemental_maps[i].mean():.1f}")

# 이온챔버로 정규화
normalized_maps = elemental_maps / (normalization[np.newaxis, :, :] + 1e-10)

# 선택된 원소 플롯
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
elements_to_plot = ['P', 'S', 'K', 'Ca', 'Fe', 'Zn']
for ax, elem in zip(axes.flat, elements_to_plot):
    if elem in channel_names:
        idx = channel_names.index(elem)
        im = ax.imshow(normalized_maps[idx], cmap='viridis',
                       extent=[x_axis[0], x_axis[-1], y_axis[-1], y_axis[0]])
        ax.set_title(elem)
        plt.colorbar(im, ax=ax)
plt.tight_layout()
```

## 스펙트럼 데이터 구조

각 픽셀은 전체 에너지분산 스펙트럼을 포함합니다:

```
채널 번호 (0-2047)  →  에너지 (keV): E = 채널 × 이득 + 오프셋
                           일반적으로: E = 채널 × 0.01 + 0.0 keV

스펙트럼 특성:
├── 탄성 산란 피크 (레일리) - 입사 에너지
├── 콤프턴 산란 피크 (입사 에너지 이하)
├── 이스케이프 피크 (검출기 아티팩트)
├── 합산 피크 (고계수율에서의 파일업 아티팩트)
└── 형광 피크:
    ├── 각 원소의 Kα, Kβ 라인
    └── 중원소(Z > 40)의 Lα, Lβ 라인
```

## 전처리 단계

### 1. 데드타임 보정
```python
corrected = raw_counts / (1 - dead_time_fraction)
```
고계수율에서의 검출기 포화를 보정합니다.

### 2. 정규화
```python
normalized = counts / (ring_current × dwell_time × ion_chamber)
```
스캔 중 빔 강도 변동을 보정합니다.

### 3. 스펙트럼 피팅
- **ROI 적분**: 예상 피크 위치 주변 채널의 단순 합산
- **가우시안 피팅**: 각 피크를 가우시안 + 선형 배경으로 피팅
- **전체 스펙트럼 피팅**: MAPS/PyXRF가 검출기 응답과 함께 모든 피크를 동시 피팅
- **NNLS**: 참조 스펙트럼을 사용한 비음수 최소제곱 분해

### 4. 정량화
- 형광 강도를 농도(µg/cm² 또는 ppm)로 변환
- 필요: 참조 표준, 기본 파라미터, 또는 보정된 표준
- MAPS는 박막 근사와 함께 기본 파라미터 접근법 사용
