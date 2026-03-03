# MLExchange

## 개요

MLExchange는 Lawrence Berkeley National Laboratory (LBNL)에서 Advanced Light Source (ALS)를 위해 개발한 웹 기반 머신러닝 플랫폼입니다. 빔라인 과학자들이 코드를 작성하지 않고도 실험 데이터에 대해 ML 모델을 학습, 배포 및 실행할 수 있는 낮은 진입 장벽의 인터페이스를 제공합니다.

이 플랫폼은 시설에 구애받지 않도록 설계되었으며, BER 프로그램 이니셔티브의 일환으로 Advanced Photon Source (APS)에서의 도입이 평가되고 있습니다.

## 주요 기능

- **웹 GUI** -- 데이터 업로드, 모델 선택, 학습 구성 및 결과 시각화를 위한 브라우저 기반 인터페이스.
- **모델 저장소** -- 이미지 세그멘테이션, 노이즈 제거, 이상 탐지 및 분류와 같은 일반적인 작업을 위한 사전 구축된 모델.
- **DLSIA 통합** -- 유연한 U-Net 및 인코더-디코더 아키텍처를 위해 Deep Learning for Scientific Image Analysis (DLSIA) 라이브러리를 사용합니다.
- **컴퓨팅 추상화** -- 사용자 측 구성 변경 없이 로컬 GPU, NERSC 또는 Kubernetes 클러스터에서 작업을 실행할 수 있습니다.
- **REST API** -- 모든 GUI 동작은 REST API로 지원되어 프로그래밍 방식의 접근과 파이프라인 통합이 가능합니다.

## APS / BER 프로그램과의 관련성

- XRF 맵 세그멘테이션 및 노이즈 제거는 MLExchange의 자연스러운 활용 사례입니다.
- 마이크로서비스 아키텍처를 Bluesky/EPICS와 함께 APS 컴퓨팅 인프라에 배포할 수 있습니다.
- ALS 데이터로 학습된 모델은 유사한 검출기 기하학을 고려할 때 최소한의 재학습으로 APS 데이터에 전이할 수 있습니다.

## 저장소

- GitHub: <https://github.com/mlexchange>
- 문서: <https://mlexchange.readthedocs.io>
- 주요 팀: CAMERA 그룹, LBNL

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [architecture.md](architecture.md) | 마이크로서비스 아키텍처 세부 사항 |
| [pros_cons.md](pros_cons.md) | 확장성 및 사용성 평가 |
