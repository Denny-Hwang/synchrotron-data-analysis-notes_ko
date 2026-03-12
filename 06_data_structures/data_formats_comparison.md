# ANL의 데이터 형식: HDF5, Zarr 및 그 이상

## 개요

APS 생태계는 데이터 파이프라인의 각 단계에서 다양한 데이터 형식을 사용합니다.
이 문서는 형식들의 상세한 비교를 제공하고, ANL에서 각 형식이 언제 그리고 왜 사용되는지 설명하며,
areaDetector, Databroker, Tiled와 같은 프레임워크가 데이터 흐름 관리에서 수행하는
핵심 역할을 다룹니다.

## 형식 비교 매트릭스

| 기능 | HDF5 | Zarr | TIFF 스택 | CXI (HDF5) | NeXus (HDF5) | CBF |
|------|------|------|-----------|-------------|--------------|-----|
| **자기 기술적** | Yes | Yes | No | Yes | Yes | Partial |
| **N차원** | Yes | Yes | 2D only | Yes | Yes | 2D |
| **압축** | Pluggable | Pluggable | LZW/None | Same as HDF5 | Same as HDF5 | CBF packed |
| **청킹** | Yes | Yes (mandatory) | Per-file | Yes | Yes | No |
| **병렬 쓰기** | MPI-IO | Native (files) | Files | MPI-IO | MPI-IO | No |
| **클라우드 네이티브** | Poor | Excellent | Poor | Poor | Poor | No |
| **스트리밍 (SWMR)** | Yes | No | N/A | Yes | Yes | No |
| **메타데이터** | Attributes | JSON sidecar | None/header | Attributes | Standardized | Mini-header |
| **최대 파일 크기** | Exabytes | Unlimited (chunks=files) | 4 GB (classic) | Exabytes | Exabytes | 4 GB |
| **생태계 지원** | Universal | Growing | Universal | Ptychography | Synchrotron std | Crystallography |

## ANL에서의 HDF5

### 역할

HDF5는 APS에서 원시 데이터와 처리된 결과 모두를 위한 **주요 저장 형식**입니다.
수집부터 아카이브까지 모든 단계에서 사용됩니다.

### HDF5가 사용되는 곳

| 단계 | 형식 변형 | 예시 |
|------|----------|------|
| 검출기 출력 | EIGER master + data files | `scan_001_master.h5` + `data_000001.h5` |
| areaDetector NDArray | NeXus 유사 레이아웃의 HDF5 | `det_image_0001.h5` |
| 처리된 볼륨 | Data Exchange 규약 | `/exchange/data [float32]` |
| 아카이브 | NeXus/HDF5 | 전체 실험 메타데이터 + 데이터 |
| 출판 | DOI가 포함된 NeXus/HDF5 | 자기 완결적 재현 가능 데이터셋 |

### APS 규모에서의 강점

- **SWMR**을 통해 수집 중 실시간 모니터링 가능
- **Direct chunk write**로 검출기 데이터 속도 유지 (8+ GB/s)
- **VDS**를 통해 다중 파일 EIGER 출력을 단일 논리적 데이터셋으로 통합
- ALCF에서 분산 재구성을 위한 **Parallel HDF5**
- **범용 도구 지원** (h5py, TomoPy, MAPS, pyFAI 등)

### 약점

- **POSIX 의존적**: 클라우드 오브젝트 스토어에서 성능 저하
- **단일 파일 병목**: 모든 메타데이터와 데이터가 하나의 파일에 집중
- **병렬 압축 쓰기 불가**: 병렬 I/O를 위해 비압축 상태로 쓰기 필요
- **재청킹 비용**: 접근 패턴 변경 시 전체 재작성 필요

## Zarr

### Zarr란 무엇인가?

Zarr는 클라우드 및 분산 컴퓨팅을 위해 설계된 청크 기반, 압축, N차원 배열 형식입니다.
각 청크는 별도의 파일(또는 오브젝트 스토어 키)로 저장되며,
메타데이터는 JSON 사이드카 파일에 기록됩니다.

### 디렉토리 구조

```
volume.zarr/
├── .zarray          # {"shape": [1800,2048,2048], "chunks": [1,2048,2048], ...}
├── .zattrs          # {"units": "counts", "pixel_size": 6.5e-6}
├── 0.0.0            # chunk (0,0,0) -- binary data
├── 0.0.1            # chunk (0,0,1)
├── 1.0.0            # chunk (1,0,0)
└── ...
```

### ANL에서 Zarr가 사용되는 곳

| 사용 사례 | Zarr를 사용하는 이유 |
|----------|---------------------|
| **TomocuPy 출력** | GPU 재구성이 빠른 사이노그램 접근을 위해 Zarr로 출력 |
| **중간 처리** | 투영에서 사이노그램 레이아웃으로의 재청킹 |
| **Dask 워크플로** | 병렬 컴퓨팅을 위한 네이티브 Dask 배열 통합 |
| **클라우드 스테이징** | ML 학습을 위해 클라우드로 데이터를 이동할 때 |

### Zarr 대 HDF5 성능 비교

#### 순차 읽기 (단일 프로세스)

| 작업 | HDF5 (gzip) | HDF5 (LZ4) | Zarr (Blosc-Zstd) | Zarr (LZ4) |
|------|------------|------------|-------------------|------------|
| 전체 볼륨 읽기 (100 GB) | 45 s | 28 s | 35 s | 25 s |
| 단일 슬라이스 읽기 | 15 ms | 8 ms | 12 ms | 7 ms |
| 임의 청크 접근 | 5 ms | 3 ms | 8 ms | 5 ms |

#### 병렬 읽기 (32 프로세스)

| 작업 | HDF5 (MPI-IO) | Zarr (filesystem) |
|------|--------------|-------------------|
| 전체 볼륨 읽기 | 4 s | 2.5 s |
| 확장 효율 | 70% | 95% |
| 잠금 경합 | Moderate | None |

Zarr의 청크별 파일 설계는 잠금 경합을 완전히 제거하여
병렬 파일시스템에서 거의 선형적인 확장성을 제공합니다.

#### 클라우드 접근 (S3 호환)

| 작업 | HDF5 (ros3) | Zarr (s3fs) |
|------|------------|-------------|
| 데이터셋 열기 | 2--5 s | 50 ms |
| 단일 청크 읽기 | 200 ms | 80 ms |
| 임의 접근 패턴 | Very slow | Fast |
| 부분 읽기 | Requires full chunk | Native |

### Zarr의 한계

| 한계 | APS에서의 영향 |
|------|---------------|
| SWMR에 해당하는 기능 없음 | 수집 중 실시간 데이터 스트리밍 불가 |
| 가상 데이터셋 없음 | 다중 파일 검출기 출력을 네이티브로 통합 불가 |
| 별도 JSON에 메타데이터 저장 | 메타데이터/데이터 분리 위험 |
| Zarr용 NeXus 표준 없음 | 방사광 Zarr 파일을 위한 커뮤니티 스키마 부재 |
| 미성숙한 생태계 | Zarr를 네이티브로 지원하는 분석 도구가 적음 |
| 다수의 소형 파일 | 수백만 개의 청크가 파일시스템 메타데이터에 부하 |

### Zarr v3 (신규)

Zarr v3에서 도입되는 기능:
- **Sharding**: 하나의 파일에 여러 청크를 저장 (소형 파일 문제 감소)
- **Codecs 파이프라인**: 조합 가능한 압축 체인
- **확장 포인트**: 사용자 정의 데이터 타입 및 스토어
- **통합 메타데이터**: 전체 계층 구조에 대한 단일 메타데이터 읽기

## TIFF 스택

### 레거시 역할

TIFF 스택은 APS에서 단층촬영 투영을 위한 원래 형식이었습니다.
각 투영은 번호가 매겨진 시퀀스의 별도 `.tif` 파일입니다.

```
scan_001/
├── proj_0001.tif
├── proj_0002.tif
├── ...
├── proj_1800.tif
├── flat_001.tif
├── dark_001.tif
└── scan_log.txt   # separate metadata file
```

### TIFF가 대체되는 이유

| 문제 | 영향 |
|------|------|
| 파일 내 메타데이터 없음 | 파라미터 파일이 분리되거나 유실됨 |
| 파일시스템 부하 | 스캔당 10,000개 이상의 파일이 메타데이터 작업에 과부하 |
| 압축 옵션 부족 | LZW/ZIP (느림) 또는 비압축만 가능 |
| 청킹 없음 | 전체 이미지를 로드해야 함 |
| 4 GB 제한 (Classic TIFF) | 단일 EIGER 프레임 세트가 초과 |

### TIFF가 여전히 사용되는 곳

- TIFF만 읽을 수 있는 레거시 분석 코드
- 빠른 시각적 검사 (모든 이미지 뷰어에서 TIFF 열기 가능)
- 외부 협력자와의 데이터 교환 형식
- 출판 그림용 타이코그래피 재구성 위상 이미지

## APS의 벤더별 형식

### Dectris 검출기 (EIGER, Pilatus, Mythen)

| 검출기 | 네이티브 형식 | APS 출력 | 비고 |
|--------|-------------|---------|------|
| EIGER2 X 9M | HDF5 (master + data) | HDF5 via areaDetector | bitshuffle+LZ4 in firmware |
| Pilatus 100K/300K | CBF (crystallography) | HDF5 or TIFF via areaDetector | 32-bit count images |
| Mythen2 1K | Raw binary | HDF5 via EPICS | 1D strip detector |

**EIGER 데이터 흐름**:
```
EIGER firmware
  ├─ FileWriter → HDF5 master + data files (detector disk)
  ├─ Stream → ZMQ multipart messages (bitshuffle+LZ4)
  └─ Monitor → TIFF images (low-rate preview)
        │
        ▼
areaDetector (ADEiger driver)
  ├─ Decodes ZMQ stream or reads FileWriter output
  ├─ Produces NDArray objects in EPICS pipeline
  └─ Writes HDF5 via NDFileHDF5 plugin
```

### 기타 검출기

| 검출기 | 유형 | 네이티브 형식 | APS 변환 |
|--------|------|-------------|---------|
| PCO.edge 5.5 | CMOS camera | TIFF/Raw | HDF5 via areaDetector |
| Oryx 10GigE | CMOS camera | Raw frames | HDF5 via areaDetector |
| Vortex ME4 | XRF SDD | MCA spectra | HDF5 via MAPS |
| Lambda 2M | GaAs hybrid pixel | Raw binary | HDF5 via areaDetector |

## areaDetector 프레임워크

### 아키텍처

areaDetector는 수십 가지 검출기 유형에 대한 통합 인터페이스를 제공하는
EPICS 기반 프레임워크입니다. 플러그인 체인을 통해 수집, 처리, 파일 쓰기를 처리합니다.

```
Detector Driver (e.g., ADEiger)
    │
    ├─ NDPluginStats     → live statistics (mean, sigma, centroid)
    ├─ NDPluginROI       → region-of-interest extraction
    ├─ NDPluginProcess   → background subtraction, flat-field
    ├─ NDPluginCodec     → compression (Blosc, JPEG, LZ4)
    ├─ NDFileHDF5        → write HDF5 files
    ├─ NDFileTIFF        → write TIFF files (legacy)
    └─ NDPluginPva       → publish via PV Access (streaming)
```

### NDFileHDF5 플러그인

HDF5 파일 기록 플러그인은 APS에서 주요 출력 경로입니다. 주요 기능:

| 기능 | 설명 |
|------|------|
| SWMR 지원 | 수집 중 실시간 읽기 가능 |
| Direct chunk write | 사전 압축된 데이터에 대해 필터 파이프라인 우회 |
| NeXus 레이아웃 | NeXus 호환 출력을 위한 설정 가능한 XML 템플릿 |
| 속성 캡처 | EPICS PV 값을 프레임별 HDF5 속성으로 기록 |
| 압축 | hdf5plugin 필터를 통한 LZ4, Blosc, bitshuffle |
| 다중 데이터셋 | 하나의 파일에 여러 검출기/채널 저장 |

### NeXus XML 템플릿

areaDetector는 XML 템플릿을 사용하여 HDF5 그룹/데이터셋 계층 구조를 정의합니다:

```xml
<group name="entry">
  <attribute name="NX_class" source="constant" value="NXentry" type="string"/>
  <group name="instrument">
    <attribute name="NX_class" source="constant" value="NXinstrument" type="string"/>
    <group name="detector">
      <attribute name="NX_class" source="constant" value="NXdetector" type="string"/>
      <dataset name="data" source="detector" det_default="true">
        <attribute name="units" source="constant" value="counts" type="string"/>
      </dataset>
      <dataset name="x_pixel_size" source="constant" value="75e-6" type="float"/>
    </group>
  </group>
</group>
```

## Databroker와 Tiled

### Databroker (레거시)

Databroker는 Bluesky 프로젝트의 Python 라이브러리로,
실험 데이터를 카탈로그화하고 검색합니다. 기반 파일 형식에 관계없이
통합된 API를 제공합니다.

```python
from databroker import catalog

cat = catalog["aps_8id"]  # Beamline catalog
run = cat[-1]              # Most recent run
data = run.primary.read()  # Returns xarray Dataset
```

**주요 기능**:
- 메타데이터(계획 이름, 시료, 날짜 등)별 실행 카탈로그화
- 지연 로딩: 접근 시에만 데이터 읽기
- 형식 무관: HDF5, TIFF, MongoDB 등 읽기 가능
- 검색: `cat.search({"plan_name": "fly_scan", "sample": "NMC*"})`

### Tiled (현재)

Tiled는 Databroker의 후속으로, 라이브러리가 아닌 **데이터 접근 서비스**로
설계되었습니다. HTTP를 통해 배열 및 테이블 데이터를 제공합니다.

| 측면 | Databroker | Tiled |
|------|-----------|-------|
| 아키텍처 | Python 라이브러리 | 클라이언트-서버 (HTTP API) |
| 접근 방식 | 로컬 프로세스 | 모든 클라이언트 (Python, 웹, curl) |
| 형식 | 파일 직접 읽기 | 타일/청크 온디맨드 제공 |
| 확장성 | 단일 머신 | 수평 확장 가능 |
| 인증 | 파일 수준 | OAuth2, API keys |
| 카탈로그 | MongoDB | 플러거블 (PostgreSQL 등) |

```python
from tiled.client import from_uri

client = from_uri("https://tiled.aps.anl.gov")
run = client["8id"]["scan_0042"]
# Fetch only the region you need
roi = run["primary"]["data"]["detector_image"][100:200, 500:1500, 500:1500]
```

**APS-U에서 Tiled가 중요한 이유**: 하루 100+ TB의 데이터 생성 환경에서
사용자는 전체 데이터셋을 다운로드할 수 없습니다. Tiled는 서버 측 슬라이싱을 가능하게 하여
-- 데이터가 어디에 저장되어 있든 사용자가 필요한 배열 청크만 가져올 수 있게 합니다.

## APS 사용자를 위한 형식 선택 가이드

| 시나리오 | 권장 형식 | 근거 |
|----------|----------|------|
| 검출기 수집 | HDF5 (areaDetector) | SWMR, direct chunk write, 생태계 |
| GPU 재구성 | Zarr 출력 | 병렬 쓰기, Dask 통합 |
| 장기 아카이브 | NeXus/HDF5 | 자기 기술적, 표준화, 검증됨 |
| 클라우드/원격 분석 | Zarr (또는 Tiled 제공 HDF5) | 클라우드 네이티브 접근 |
| ML 학습 데이터 | Zarr 또는 HDF5 | 프레임워크에 따라 다름 (PyTorch DataLoader 둘 다 지원) |
| 출판 | NeXus/HDF5 | DataCite 호환성, DOI 등록 |
| 빠른 시각화 | TIFF (내보내기) | 범용 뷰어 지원 |
| 결정학 | CBF 또는 HDF5 | DIALS/CCP4 호환성 |

## 신규 기술: kerchunk과 VirtualiZarr

**kerchunk**은 기존 HDF5 파일 위에 Zarr 호환 인덱스를 생성하여
데이터 변환 없이 Zarr 스타일 접근을 가능하게 합니다:

```python
import kerchunk.hdf
import fsspec

# Create virtual Zarr reference for existing HDF5
refs = kerchunk.hdf.SingleHdf5ToZarr("scan_001.h5").translate()

# Access via Zarr API (no data copy)
import zarr
store = fsspec.filesystem("reference", fo=refs).get_mapper("")
z = zarr.open(store, mode="r")
slice_data = z["entry/data/data"][500]
```

이는 APS의 HDF5 투자와 클라우드 네이티브 워크플로 사이의 격차를
형식 변환 없이 해소합니다.

## 관련 문서

- [HDF5 심층 분석](hdf5_deep_dive.md) -- 내부 아키텍처, SWMR, 병렬 I/O
- [HDF5 구조 개요](hdf5_structure/README.md) -- 기본 HDF5 개념
- [APS-U 데이터 과제](data_challenges_apsu.md) -- 인프라 과제
- [데이터 규모 분석](data_scale_analysis.md) -- 볼륨 예측
