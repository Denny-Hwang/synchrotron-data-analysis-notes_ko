# Bluesky / EPICS -- 아키텍처 세부 사항

## RunEngine

RunEngine은 Bluesky의 핵심 실행 엔진입니다. **플랜** (Python 제너레이터로 **메시지**를 yield하는 것)을 소비하고 각 메시지를 하드웨어 동작 및 문서 발행으로 변환합니다.

### 메시지 유형

| 메시지 | 설명 |
|---------|-------------|
| `open_run` | 새로운 실행 시작; RunStart 문서 발행 |
| `set` | 장치에 특정 값으로 이동 명령 |
| `trigger` | 검출기에 데이터 취득 트리거 |
| `read` | 장치에서 현재 값 읽기 |
| `save` | 현재 판독값을 Event 문서로 번들링 |
| `close_run` | 실행 종료; RunStop 문서 발행 |

### 실행 흐름

```python
from bluesky import RunEngine
from bluesky.plans import scan
from ophyd import EpicsMotor, EpicsSignalRO

motor = EpicsMotor("IOC:m1", name="motor")
det = EpicsSignalRO("IOC:det:total", name="detector")

RE = RunEngine({})
RE(scan([det], motor, 0, 180, 100))
```

`scan` 플랜은 다음과 같은 메시지 시퀀스를 yield합니다:
`open_run -> (set, trigger, read, save) x N -> close_run`

## ophyd 장치 모델

ophyd는 장치 클래스의 계층 구조를 제공합니다.

| 클래스 | 용도 |
|-------|-----|
| `Signal` | 단일 PV (읽기 전용 또는 읽기-쓰기) |
| `EpicsSignal` | EPICS PV로 지원되는 Signal |
| `EpicsMotor` | 위치, 속도 및 상태 PV를 가진 모터 |
| `Device` | Signal들의 복합 그룹 |
| `AreaDetector` | 플러그인 체인을 가진 다중 PV 검출기 |

### 장치 구성 대 읽기

각 장치는 다음을 구분합니다:

- **read()** -- 주요 데이터 (예: 모터 위치, 검출기 카운트).
- **read_configuration()** -- 느리게 변하는 메타데이터 (예: 게인, 노출 시간).

두 가지 모두 문서 스트림에 캡처됩니다.

## 문서 모델

Bluesky는 모든 실행 중에 JSON 직렬화 가능한 문서 스트림을 발행합니다.

| 문서 | 발행 시점 | 내용 |
|----------|-------------|----------|
| **RunStart** | `open_run` | UID, 플랜 이름, 메타데이터, 타임스탬프 |
| **Descriptor** | 첫 `save` | 데이터 키, 형상, dtype, 소스 PV |
| **Event** | 각 `save` | 타임스탬프가 포함된 데이터 판독값 |
| **EventPage** | 대량 `save` | Event의 컬럼형 배치 (성능용) |
| **Resource** | 외부 파일 | 파일 경로, 사양 (HDF5, TIFF) |
| **Datum** | 외부 데이터 | Resource 내 포인터 |
| **RunStop** | `close_run` | 종료 상태, 종료 타임스탬프 |

### 문서 흐름

```
RunEngine
   |
   +---> Callback 1: LiveTable (print to terminal)
   +---> Callback 2: LivePlot (matplotlib)
   +---> Callback 3: Databroker insert (MongoDB / msgpack)
   +---> Callback 4: Custom analysis callback
```

## Databroker

Databroker는 문서 스트림에 대한 사후 접근을 제공합니다.

```python
from databroker import catalog

cat = catalog["my_beamline"]
run = cat[-1]           # most recent run
ds = run.primary.read() # xarray Dataset
```

스토리지 백엔드: MongoDB + GridFS (레거시), msgpack 파일 (Databroker v2) 또는 Tiled 서버.

## Bluesky Queue Server

무인 또는 원격 운영을 위해 Queue Server는 RunEngine을 ZMQ 기반 서비스로 래핑합니다.

- 플랜은 JSON 설명으로 대기열에 제출됩니다.
- 서버는 플랜을 순차적으로 (또는 구성 가능한 동시성으로) 실행합니다.
- 상태와 결과는 REST API 또는 `bluesky-widgets` GUI를 통해 접근할 수 있습니다.

## APS 통합 패턴

1. **데이터 수집** -- Bluesky 플랜이 EPICS 모터와 areaDetector를 통해 XRF 래스터 스캔을 실행합니다.
2. **데이터 저장** -- areaDetector 파일 플러그인이 HDF5 파일을 기록합니다.
3. **분석 트리거** -- Bluesky 콜백이 RunStop을 감지하고 ROI Finder 파이프라인을 시작합니다.
4. **적응형 피드백** -- ROI Finder 결과가 EPICS PV에 기록되거나, 추천된 ROI에 대한 고해상도 재스캔을 위한 새로운 Bluesky 플랜으로 제출됩니다.
