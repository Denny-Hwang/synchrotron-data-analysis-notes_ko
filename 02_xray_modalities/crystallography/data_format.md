# 결정학 데이터 형식

## 원시 데이터 형식

### HDF5 (EIGER 네이티브)

EIGER 검출기 제품군은 다음 구조의 HDF5 형식으로 데이터를 생성합니다:

```
dataset_master.h5
├── /entry/
│   ├── /instrument/
│   │   └── /detector/
│   │       ├── /description = "Eiger 16M"
│   │       ├── /x_pixel_size = 0.000075  # 75 µm
│   │       ├── /y_pixel_size = 0.000075
│   │       ├── /sensor_thickness = 0.00045  # 450 µm Si
│   │       ├── /count_time = 0.01  # 초
│   │       ├── /frame_time = 0.01
│   │       ├── /beam_center_x = 2073.5  # 픽셀
│   │       ├── /beam_center_y = 2167.3
│   │       ├── /detector_distance = 0.250  # 미터
│   │       └── /detectorSpecific/
│   │           ├── /nimages = 3600
│   │           └── /ntrigger = 1
│   └── /data/
│       ├── data_000001 -> (외부 데이터 파일 링크)
│       ├── data_000002 -> ...
│       └── ...
│
dataset_data_000001.h5
├── /entry/data/
│   └── /data [shape: (N_frames, 4362, 4148), dtype: uint32]
│       # bitshuffle-LZ4로 압축
```

### CBF (결정학 바이너리 파일)

일부 검출기(PILATUS, ADSC)에서 여전히 사용되는 레거시 형식:

```
# CBF 헤더 (ASCII)
_array_data.header_convention "PILATUS_1.2"
_diffrn_radiation_wavelength 0.97918
_diffrn_scan_axis omega
_diffrn_scan_frame_axis_offset 0.00
...

# 바이너리 섹션 (압축된 이미지 데이터)
--CIF-BINARY-FORMAT-SECTION--
Content-Type: application/octet-stream
X-Binary-Size: 2073600
...
```

## 메타데이터 구조

### 필수 메타데이터

| 파라미터 | 설명 | 예시 값 |
|----------|------|---------|
| `wavelength` | X선 파장 (Å) | 0.97918 |
| `detector_distance` | 결정-검출기 거리 (mm) | 250.0 |
| `beam_center_x/y` | 검출기 위 빔 위치 (픽셀) | 2073.5, 2167.3 |
| `oscillation_range` | 프레임당 회전 (°) | 0.1 |
| `exposure_time` | 프레임당 적분 시간 (s) | 0.01 |
| `phi/omega` | 고니오미터 각도 (°) | 0.0 – 180.0 |
| `space_group` | 결정 대칭 | P21 |
| `unit_cell` | a, b, c, α, β, γ | 45.2, 67.8, 89.1, 90, 95.3, 90 |

## Python 데이터 로딩

```python
import h5py
import numpy as np

# EIGER HDF5 마스터 파일 로드
with h5py.File('dataset_master.h5', 'r') as f:
    # 검출기 메타데이터 읽기
    det = f['/entry/instrument/detector']
    wavelength = f['/entry/instrument/beam/incident_wavelength'][()]
    distance = det['detector_distance'][()]
    beam_x = det['beam_center_x'][()]
    beam_y = det['beam_center_y'][()]

    # 회절 데이터 읽기 (링크된 데이터 파일에서)
    data = f['/entry/data/data_000001'][:]  # shape: (N, 4362, 4148)
    print(f"Loaded {data.shape[0]} frames, {data.shape[1]}×{data.shape[2]} pixels")

# CBF 파일을 fabio로 로드
import fabio
img = fabio.open('frame_001.cbf')
data = img.data  # numpy 배열
header = img.header  # 메타데이터 사전
```

## 처리된 데이터 형식

### MTZ (병합된 반사 파일)
- 처리된 결정학 데이터의 표준 형식
- 포함: 밀러 지수 (h,k,l), 강도 (I), 표준편차 (σ)
- 사용: CCP4 스위트, PHENIX, SHELX

### PDB/mmCIF (원자 좌표)
- 최종 정밀화된 원자 모델
- PDB: 레거시 고정 열 형식 (단계적 폐지 중)
- mmCIF: 현대적 사전 기반 형식 (현재 표준)
- 단백질 데이터 뱅크(wwPDB)에 등록

## 데이터 처리 파이프라인

```
원시 프레임 (HDF5/CBF)
    │
    ├─→ 인덱싱 (결정 방위 및 단위 셀 결정)
    │       도구: DIALS, XDS, MOSFLM
    │
    ├─→ 적분 (스팟 강도 추출)
    │       도구: DIALS, XDS
    │
    ├─→ 스케일링 & 병합 (대칭 관련 관측 결합)
    │       도구: AIMLESS, XSCALE
    │
    ├─→ 위상 결정
    │       방법: MR (분자 치환), SAD/MAD, 직접 방법
    │       도구: PHASER, SHELXD, AutoSol
    │
    ├─→ 모델 구축 (폴리펩타이드 사슬 추적)
    │       도구: ARP/wARP, Buccaneer, AlphaFold (초기 모델)
    │
    └─→ 정밀화 (데이터에 대한 모델 최적화)
            도구: REFMAC5, phenix.refine
            출력: PDB/mmCIF + MTZ
```

## 전처리 요구사항

1. **불량 픽셀 마스킹**: 검출기의 죽은/과열 픽셀 마스킹
2. **플랫필드 보정**: 픽셀 응답 정규화 (일반적으로 검출기가 적용)
3. **지오메트리 정밀화**: 정확한 검출기 거리, 빔 중심, 회전축
4. **아이스 링 제거**: 아이스 회절로 오염된 해상도 셸 마스킹 (극저온 시)
5. **방사선 손상 평가**: 데이터 수집 중 강도 감쇠 모니터링
