# 실시간 데이터 스트리밍

## 개요

프레임이 검출기를 떠나 Area Detector 프레임워크를 통과한 후, 최소한의 지연으로
처리 노드에 전송되어야 합니다. BER 프로그램 파이프라인은 서로 다른 지연 시간과
대역폭 요구에 적합한 세 가지 상호 보완적인 스트리밍 기술을 사용합니다 --
ZeroMQ (ZMQ), PV Access, Globus.

## 스트리밍 아키텍처

일반적인 스트리밍 패턴은 **생산자-브로커-소비자** 모델을 따릅니다:

```
Producer(s)              Broker / Router           Consumer(s)
+-----------+          +-----------------+       +-------------+
| Area Det  |--ZMQ---->| Stream Router   |------>| Preprocessor|
| IOC       |--PVA---->| (edge node)     |------>| Live Viewer |
+-----------+          +-----------------+       +-------------+
                              |
                        Globus Transfer
                              v
                       +--------------+
                       | ALCF Compute |
                       +--------------+
```

### 설계 원칙

1. **팬아웃** -- 단일 데이터 소스가 여러 소비자에게 동시에 공급합니다.
2. **배압 처리** -- 느린 소비자가 검출기를 차단하지 않습니다; 브로커가
   구성된 정책에 따라 프레임을 삭제하거나 대기열에 넣습니다.
3. **제로 카피** -- ZMQ와 공유 메모리 전송은 불필요한 복사를 방지합니다.

## ZeroMQ (ZMQ) 스트리밍

ZMQ는 빔라인 네트워크 내에서 프레임 수준 스트리밍을 위한 주요 저지연
경로를 제공합니다.

| 구성요소 | ZMQ 패턴 | 포트 | 용도 |
|----------|---------|------|------|
| Area Detector 플러그인 | PUB | 5555 | 원시 프레임 발행 |
| Stream Router | XSUB / XPUB | 5556 / 5557 | 소비자에게 팬아웃 |
| 전처리기 | SUB | -- | 프레임 토픽 구독 |
| 실시간 뷰어 | SUB | -- | 디스플레이용 구독 |

### 메시지 형식

각 ZMQ 메시지는 다중 파트 엔벨로프입니다:

```
Part 0:  Topic string     ("detector.eiger.frame")
Part 1:  Header (JSON)    {"frame_id": 42, "shape": [2070,2167], "dtype": "uint16"}
Part 2:  Data blob         (raw pixel bytes, optionally LZ4-compressed)
Part 3:  Metadata (JSON)   {"energy_keV": 12.0, "angle_deg": 45.3}
```

### 성능

- **지연 시간**: 랙 내 전송 시 < 1 ms (56 Gbps InfiniBand)
- **처리량**: ZMQ PUB 소켓당 지속 8 GB/s (10 x 100 GbE 본딩)
- **신뢰성**: 최대 1회 전달(at-most-once); 부하 상태에서 프레임 손실률 < 0.01%

## PV Access 스트리밍

PV Access (pvAccess)는 EPICS v7 네트워크 프로토콜로, 내재적 유형 안전성과
모니터링 의미론을 갖춘 구조화된 데이터 전송을 제공합니다.

- **NTNDArray**: EPICS 네이티브 소비자(CSS 디스플레이, 아카이버 어플라이언스)를 위해
  검출기 프레임을 Normative Type ND 배열로 전송합니다.
- **NTScalar / NTTable**: 이미지와 함께 스칼라 및 표 형태 메타데이터를 스트리밍합니다.

```yaml
pva_gateway:
  listen_interface: "10.0.0.0/16"
  server_addresses:
    - "ioc-det-eiger:5075"
    - "ioc-det-jungfrau:5075"
  max_array_bytes: 50000000
```

PV Access는 대량 전송보다 제어 시스템 의미론에 최적화되어 있습니다.
지속적인 다중 GB/s 처리량에는 ZMQ가 선호됩니다.

## Globus 데이터 전송

### APS에서 ALCF로의 연결

APS와 ALCF 간 대량 데이터 전송은 100 Gbps ESnet 링크로 연결된
전용 DTN 노드를 통해 Globus를 사용합니다.

| 매개변수 | 값 |
|----------|-----|
| 프로토콜 | GridFTP (Globus Connect Server v5.4) |
| 병렬성 | 전송당 8개 동시 TCP 스트림 |
| 동시성 | 4개 동시 파일 전송 |
| 암호화 | 제어 채널용 TLS 1.3; 데이터는 선택사항 |
| 체크섬 | 전송 후 SHA-256 검증 |
| 자동화 | EPICS 스캔 완료 PV로 트리거되는 Globus Flows |

### 자동화된 트리거 흐름

1. 스캔 완료 -- EPICS IOC가 `$(P):ScanComplete` PV를 1로 설정합니다.
2. Bluesky RunEngine `post_scan_hook`이 REST API를 통해 Globus Flow를 실행합니다.
3. Globus Flow 단계: 데이터 전송, 체크섬 확인, ALCF 작업 트리거.
4. ALCF 배치 스케줄러 (PBS Pro)가 전처리 컨테이너를 시작합니다.

### 처리량

- **측정값**: APS와 ALCF DTN 간 지속 40-60 Gbps
- **지연 시간**: Globus Flows를 통한 전송 개시 < 5초
- **일반적인 스캔**: 50 GB 단층촬영 데이터셋이 약 8초에 전송됨

## 모니터링 및 관측 가능성

모든 스트리밍 구성요소는 중앙화된 Grafana 스택에 메트릭을 전송합니다:

| 메트릭 | 소스 | 대시보드 |
|--------|------|---------|
| 프레임 레이트 (fps) | ZMQ 퍼블리셔 | 검출기 처리량 |
| 전송 속도 (Gbps) | Globus 활동 로그 | 데이터 무버 |
| 소비자 지연 (프레임) | ZMQ 브로커 | 스트림 상태 |
| PV 업데이트 속도 (Hz) | pvAccess 게이트웨이 | EPICS 메트릭 |

소비자 지연이 100 프레임을 초과하거나 전송 속도가 10 Gbps 미만으로 떨어지면
알림이 발생하며, 이는 실시간 처리에 영향을 미칠 수 있는 병목을 나타냅니다.

## 다음 단계

스트리밍된 데이터는 처리 노드에 도착하여 [processing.md](processing.md)에
설명된 재구성 파이프라인에 진입합니다.
