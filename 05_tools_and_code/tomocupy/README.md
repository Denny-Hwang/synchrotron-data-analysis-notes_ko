# TomocuPy

## 개요

TomocuPy는 Advanced Photon Source (APS), Argonne National Laboratory에서 개발한 GPU 가속 토모그래피 재구성 패키지입니다. CuPy를 사용하여 TomoPy의 핵심 알고리즘을 재구현하여 단일 NVIDIA GPU에서 방사광 마이크로 CT 데이터의 거의 실시간 재구성을 가능하게 합니다.

## 주요 기능

- **CuPy 기반 커널** -- 모든 필터링, 역투영 및 링 제거 연산이 CuPy를 통해 전적으로 GPU에서 실행되어 반복적인 호스트-장치 전송을 방지합니다.
- **스트리밍 청크 파이프라인** -- 사이노그램이 겹치는 청크로 처리되어 GPU 연산과 호스트-장치 I/O가 중첩되므로 GPU가 지속적으로 활용됩니다.
- **직접 대체 CLI** -- APS 섹터 2-BM 및 32-ID 빔라인의 데이터 관리 시스템과 호환되는 명령줄 인터페이스.
- **HDF5 I/O** -- TomoPy 및 APS Data Exchange 사양에서 사용하는 동일한 `exchange` HDF5 형식을 읽고 씁니다.

## 지원 알고리즘

| 알고리즘 | 설명 |
|-----------|-------------|
| FBP (gridrec) | 푸리에 기반 필터 역투영 |
| Log-polar FBP | 회전 중심 허용 변형 |
| Phase retrieval | Paganin 단일 거리 방법 |
| Ring removal | 결합된 푸리에 + Titarenko 접근법 |
| Stripe removal | 웨이블릿 기반 수직 줄무늬 보정 |

## 일반적인 성능

NVIDIA A100 (40 GB)에서 TomocuPy는 2048 x 2048 x 1500 데이터셋을 약 25초에 재구성하며, 이는 64코어 CPU 노드에서 동일한 TomoPy gridrec 실행의 수분과 비교됩니다.

## 저장소

- GitHub: <https://github.com/tomography/tomocupy>
- 라이선스: BSD-3-Clause
- 주요 유지 관리자: Viktor Nikitin (APS)

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [reverse_engineering.md](reverse_engineering.md) | 아키텍처 심층 분석 |
| [pros_cons.md](pros_cons.md) | TomoPy와의 비교 |
| [reproduction_guide.md](reproduction_guide.md) | 설정 및 벤치마킹 |
