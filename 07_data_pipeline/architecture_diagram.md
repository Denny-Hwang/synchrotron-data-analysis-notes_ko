# 시스템 아키텍처 다이어그램

## 개요

APS BER 데이터 파이프라인의 컴포넌트 상호작용, 데이터 형식 변환, 시스템 인터페이스를
보여주는 Mermaid 기반 종합 다이어그램입니다.

## 전체 시스템 아키텍처

```mermaid
flowchart TB
    subgraph BL["Beamline (APS)"]
        DET[Detector] -->|"raw frames"| IOC[EPICS IOC]
        IOC -->|"HDF5/SWMR"| GPFS[(Beamline GPFS)]
    end
    subgraph EDGE["Edge Computing"]
        IOC -->|"NDArray"| ZMQ_PUB[ZMQ Publisher]
        IOC -->|"NTNDArray"| PVA[PV Access GW]
    end
    subgraph ALCF["ALCF (Polaris / Aurora)"]
        EAGLE[(Eagle FS)]
        PRE[Preprocessing] -->|"HDF5"| REC[TomocuPy]
        REC -->|"Zarr"| DEN[Denoising]
        DEN -->|"Zarr"| SEG[U-Net Segmentation]
        SEG -->|"HDF5"| QNT[Quantification]
        GPFS -->|"Globus 100Gbps"| EAGLE --> PRE
        ZMQ_PUB -->|"ZMQ TCP"| PRE
    end
    subgraph ANALYSIS["Analysis"]
        QNT --> TRT[Triton Inference]
        EAGLE --> JH[JupyterHub]
    end
    subgraph STORE["Storage"]
        EAGLE -->|"Globus Flow"| PET[(Petrel)]
        EAGLE -->|"Globus Flow"| TAPE[(HPSS Tape)]
        PET --> DOI[DataCite DOI]
    end
```

## 데이터 형식 변환 지점

```mermaid
flowchart LR
    A["Vendor Binary"] -->|"IOC decode"| B["HDF5/SWMR"]
    B -->|"NDPluginCodec"| C["ZMQ Multipart"]
    C -->|"consumer"| D["HDF5 float32"]
    B -->|"Globus copy"| D
    D -->|"TomocuPy"| E["Zarr float32"]
    E -->|"DNN"| F["Zarr float32"]
    F -->|"U-Net"| G["HDF5 uint8"]
    G -->|"measure"| H["JSON metrics"]
    D & E & F & G & H -->|"NeXus writer"| I["NeXus/HDF5 archive"]
```

## 인터페이스 프로토콜 맵

```mermaid
flowchart TB
    QS["Queue Server"] -->|"HTTP/JSON"| BS["Bluesky RE"]
    BS -->|"Channel Access"| EP["EPICS IOC"]
    EP -->|"plugin chain"| AD["areaDetector"]
    BS -->|"msgpack"| DB["Databroker"]
    AD -->|"ZMQ PUB"| ZM["ZMQ Broker"]
    BS -->|"REST API"| GF["Globus Flows"]
    GF -->|"GridFTP"| PT["Petrel"]
    GF -->|"PBS qsub"| TC["TomocuPy"]
    TC -->|"Zarr"| PY["PyTorch"]
    PY -->|"HTTP"| ML["MLflow"]
    PT -->|"REST"| DC["DataCite"]
```

## 스캔 생애주기 시퀀스

```mermaid
sequenceDiagram
    participant User
    participant QS as Queue Server
    participant BS as Bluesky RE
    participant IOC as EPICS IOC
    participant Det as Detector
    participant GF as Globus Flows
    participant HPC as ALCF Compute
    participant Pet as Petrel

    User->>QS: Submit scan plan
    QS->>BS: Execute plan
    BS->>IOC: Configure detector
    IOC->>Det: Start acquisition
    loop Each projection
        Det->>IOC: Frame (trigger)
        IOC->>IOC: Write HDF5 + stream ZMQ
    end
    IOC->>BS: Scan done
    BS->>GF: Trigger transfer
    GF->>HPC: Transfer + process
    GF->>Pet: Archive results
    GF->>User: Notification
```

## 네트워크 토폴로지

```mermaid
flowchart LR
    subgraph APS["APS Network"]
        SW1[Beamline Switch] --- DTN1[APS DTN]
    end
    subgraph ES["ESnet Backbone"]
        RTR[Router 400GbE]
    end
    subgraph ALCF["ALCF Network"]
        DTN2[ALCF DTN] --- SW2[Core Switch]
        SW2 --- GPU[Compute Nodes]
        SW2 --- EGL[Eagle Storage]
    end
    DTN1 ---|"100 Gbps"| RTR ---|"100 Gbps"| DTN2
```

## 범례

| 기호 | 의미 |
|---|---|
| 직사각형 | 컴퓨팅 서비스 또는 애플리케이션 |
| 원통형 | 저장 시스템 (파일시스템, 데이터베이스, 아카이브) |
| 화살표 라벨 | 인터페이스의 프로토콜 또는 데이터 형식 |
| 서브그래프 | 네트워크 또는 논리적 경계 |

## 관련 문서

- [README.md](README.md) -- 파이프라인 개요
- [acquisition.md](acquisition.md) -- 검출기 및 IOC 상세
- [streaming.md](streaming.md) -- 전송 프로토콜
- [processing.md](processing.md) -- 재구성 및 ML 파이프라인
- [analysis.md](analysis.md) -- 추론 및 시각화
- [storage.md](storage.md) -- 아카이브 및 DOI 워크플로
