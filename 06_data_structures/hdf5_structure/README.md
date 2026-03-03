# 방사광 과학을 위한 HDF5 데이터 구조

## HDF5란?

**Hierarchical Data Format version 5 (HDF5)**는 대용량 과학 데이터의 저장 및 구성을
위해 설계된 오픈소스 파일 형식 및 라이브러리입니다. The HDF Group에서 개발한 이 형식은
APS, NSLS-II, ESRF, Diamond Light Source, SPring-8을 포함한 전 세계 방사광 시설에서
데이터 저장의 보편적 표준이 되었습니다.

HDF5 파일은 다음을 결합하는 자체 포함 컨테이너입니다:
- 임의 크기와 데이터 유형의 **N차원 배열**
- 파일시스템 유사 트리를 사용한 **계층적 구성**
- 계층의 모든 수준에 첨부되는 **풍부한 메타데이터**
- 플러거블 코덱을 지원하는 **효율적인 압축**

## 핵심 개념

### 그룹

그룹은 HDF5에서 디렉토리에 해당합니다. 데이터를 논리적으로 구성하는 트리 구조를 형성합니다.
모든 HDF5 파일에는 루트 그룹 `/`이 있습니다.

```
/                           # 루트 그룹
/entry/                     # 실험 항목
/entry/instrument/          # 장비 구성
/entry/data/                # 측정 데이터
/entry/sample/              # 시료 메타데이터
```

### 데이터셋

데이터셋은 실제 수치 배열을 보관합니다. 주요 속성은 다음과 같습니다:

| 속성 | 설명 |
|------|------|
| Shape | N차원 배열 치수 (예: `(1800, 2048, 2048)`) |
| Dtype | 데이터 유형 (`float32`, `uint16`, `complex64` 등) |
| Chunks | 효율적인 부분 I/O를 위한 세분화 (예: `(1, 2048, 2048)`) |
| Compression | 코덱 및 수준 (예: `gzip level 4`, `lz4`) |
| Fill value | 기록되지 않은 요소의 기본값 |

### 속성

속성은 그룹이나 데이터셋에 첨부되는 소규모 메타데이터 항목입니다. 다음을 저장합니다:
- 실험 매개변수 (에너지, 노출 시간, 픽셀 크기)
- 출처 정보 (소프트웨어 버전, 처리 이력)
- 단위 및 교정 인자
- 타임스탬프 및 사용자 주석

```python
# Example: reading attributes
import h5py
with h5py.File("scan.h5", "r") as f:
    energy = f["/entry/instrument/monochromator"].attrs["energy"]  # keV
    pixel_size = f["/entry/instrument/detector"].attrs["x_pixel_size"]  # meters
```

## 압축 옵션

HDF5는 각각 장단점이 있는 여러 압축 필터를 지원합니다:

| 필터 | 비율 | 속도 | 최적 용도 |
|------|------|------|----------|
| gzip (level 4) | 3--5배 | 보통 | 범용, 보관 |
| LZ4 | 2--3배 | 매우 빠름 | 실시간 스트리밍 |
| Blosc | 3--6배 | 빠름 | 인메모리 계산 |
| bitshuffle + LZ4 | 4--8배 | 빠름 | 낮은 비트 패턴의 검출기 데이터 |
| SZ / ZFP | 10--50배 | 빠름 | 손실, 부동소수점 배열 |

APS에서 기본 파이프라인은 원시 검출기 데이터에 **bitshuffle + LZ4**를,
처리된 결과에 **gzip level 4**를 사용합니다.

## 방사광이 HDF5를 사용하는 이유

1. **규모** -- APS-U에서의 단일 단층촬영 스캔은 50+ GB의 원시 데이터를 생성할 수 있습니다.
   HDF5는 청크 I/O와 압축으로 이를 기본적으로 처리합니다.
2. **자기 기술적** -- 모든 메타데이터가 데이터와 함께 이동하므로,
   분리되거나 분실될 수 있는 별도의 매개변수 파일이 필요하지 않습니다.
3. **병렬 I/O** -- HDF5는 MPI 병렬 읽기/쓰기를 지원하며, 이는
   ALCF (Argonne Leadership Computing Facility) 슈퍼컴퓨터에서의 처리에 핵심적입니다.
4. **스트리밍** -- 청크 데이터셋은 수집 중에 추가할 수 있어
   Bluesky와 databroker 같은 도구를 통한 실시간 모니터링이 가능합니다.
5. **생태계** -- 거의 모든 방사광 분석 패키지(TomoPy, MAPS, pyFAI,
   Mantid, Dials)가 HDF5를 읽고 씁니다.

## NeXus 규약

**NeXus**는 HDF5 위에 명명 규칙과 조직 규칙을 정의하는 국제 표준입니다.
다음을 지정합니다:

- **NXentry** -- 최상위 실험 컨테이너
- **NXinstrument** -- 광원, 단색화기, 검출기 설명
- **NXsample** -- 시료 이름, 조성, 환경
- **NXdata** -- 축이 포함된 기본 플롯 가능 신호
- **NXprocess** -- 처리 출처 체인

```
/entry:NXentry
  /instrument:NXinstrument
    /source:NXsource
      @name = "APS"
      @energy = 6.0   # GeV
    /detector:NXdetector
      data [2048, 2048] uint16
      @x_pixel_size = 6.5e-6  # meters
  /sample:NXsample
    @name = "soil_core_27B"
  /data:NXdata
    @signal = "data"
    @axes = ["y", "x"]
```

NeXus 파일은 `.nxs` 또는 `.nx5` 확장자를 사용하며 모든 HDF5 도구로 읽을 수 있는
완전히 유효한 HDF5 파일입니다.

## 모달리티별 스키마

각 방사광 기법은 HDF5 내에서 데이터를 구성하기 위한 확립된 규약을 가지고 있습니다:

| 모달리티 | 규약 | 스키마 파일 |
|----------|------|------------|
| X선 형광 (XRF) | MAPS 출력 | [xrf_hdf5_schema.md](xrf_hdf5_schema.md) |
| 단층촬영 | Data Exchange | [tomo_hdf5_schema.md](tomo_hdf5_schema.md) |
| 타이코그래피 | CXI 형식 | [ptychography_hdf5_schema.md](ptychography_hdf5_schema.md) |

## HDF5용 Python 도구

| 패키지 | 용도 |
|--------|------|
| **h5py** | HDF5에 대한 저수준 Python 인터페이스 |
| **h5pyd** | HSDS(클라우드 HDF5)용 h5py 호환 인터페이스 |
| **nexusformat** | NeXus 인식 읽기 및 쓰기 |
| **silx** | GUI 트리 브라우저가 있는 HDF5 뷰어 |
| **dxchange** | Data Exchange 단층촬영 파일 읽기/쓰기 |
| **hdf5plugin** | 추가 압축 필터 (Blosc, bitshuffle, SZ) |

## 실습 노트북

| 노트북 | 설명 |
|--------|------|
| [01_hdf5_exploration.ipynb](notebooks/01_hdf5_exploration.ipynb) | h5py로 HDF5 파일 탐색 |
| [02_data_visualization.ipynb](notebooks/02_data_visualization.ipynb) | 다채널 방사광 데이터 시각화 |

## 모범 사례

1. **접근 패턴에 맞춘 청킹 사용** -- 단층촬영의 경우, 재구성을 위해 투영별
   `(1, nrow, ncol)` 또는 시노그램 접근을 위해 `(nproj, 1, ncol)`로 청킹합니다.
2. **단위를 속성으로 저장** -- 데이터셋에 항상 `units` 속성을 첨부합니다.
3. **처리 출처 포함** -- 소프트웨어 버전, 매개변수, 타임스탬프를 기록합니다.
4. **상대 링크 사용** -- HDF5 소프트 링크는 복제 없이 관련 데이터셋을 연결할 수 있습니다.
5. **NeXus 검증** -- `cnxvalidate` 또는 `punx`를 사용하여 NeXus 준수 여부를 확인합니다.
