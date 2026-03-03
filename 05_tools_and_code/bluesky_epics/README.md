# Bluesky / EPICS -- 실험 오케스트레이션 개요

## Bluesky란?

Bluesky는 원래 NSLS-II (Brookhaven National Laboratory)에서 개발되었으며 현재 APS를 포함한 여러 방사광 시설에서 채택된 Python 기반 실험 오케스트레이션 프레임워크입니다. 실험 절차를 정의, 실행 및 기록하기 위한 하드웨어 추상화된 이벤트 기반 시스템을 제공합니다.

## EPICS란?

EPICS (Experimental Physics and Industrial Control System)는 APS와 전 세계 대부분의 방사광 시설에서 사용되는 분산 제어 시스템입니다. Channel Access (CA) 및 pvAccess (PVA) 네트워크 프로토콜을 통해 하드웨어 장치 (모터, 검출기, 셔터) 간의 실시간 통신을 제공합니다.

## 함께 작동하는 방식

```
Bluesky RunEngine  (experiment logic, Python)
       |
       v
     ophyd          (hardware abstraction layer)
       |
       v
  EPICS IOCs        (input/output controllers, C)
       |
       v
  Hardware          (motors, detectors, shutters)
```

Bluesky는 EPICS Process Variable (PV)에 매핑되는 `ophyd` 장치 객체를 사용합니다. RunEngine이 스캔 플랜을 실행하면 ophyd가 고수준 명령 (예: "모터를 45도로 이동")을 EPICS `caput` / `caget` 호출로 변환합니다.

## 주요 컴포넌트

| 컴포넌트 | 역할 |
|-----------|------|
| **RunEngine** | 스캔 플랜 실행, 문서 스트림 발행 |
| **ophyd** | EPICS PV에 대한 Python 장치 추상화 |
| **Databroker** | 실험 문서 저장 및 검색 |
| **Bluesky Queue Server** | 무인 운영을 위한 원격 작업 대기열 |
| **Tiled** | 데이터 접근 서비스 (REST API + Python 클라이언트) |

## APS BER 프로그램과의 관련성

- APS-U 빔라인은 Bluesky/EPICS를 표준 제어 스택으로 채택하고 있습니다.
- 자동화된 XRF 스캐닝 및 토모그래피 데이터 수집을 Bluesky 플랜으로 정의할 수 있습니다.
- ROI Finder는 추천된 ROI를 Bluesky에 피드백하여 적응형 폐루프 실험을 수행할 수 있습니다.

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [architecture.md](architecture.md) | 상세 아키텍처 및 문서 모델 |
