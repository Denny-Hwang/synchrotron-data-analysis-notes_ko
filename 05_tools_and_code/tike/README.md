# Tike

## 개요

Tike는 Advanced Photon Source (APS), Argonne National Laboratory에서 개발한 GPU 가속 ptychography 재구성 툴킷입니다. 여러 ptychography 재구성 알고리즘의 고성능 구현을 제공하며, 최신 싱크로트론 빔라인에서 스트리밍 ptychography를 위한 거의 실시간 기능을 갖추고 있습니다.

## 주요 기능

- **GPU 가속 재구성** -- 모든 핵심 알고리즘이 CuPy/CUDA를 통해 NVIDIA GPU에서 실행되어 거의 실시간 ptychography 재구성을 가능하게 합니다.
- **다중 재구성 알고리즘** -- ePIE (extended Ptychographic Iterative Engine), DM (Difference Map), LSQ-ML (Least-Squares Maximum Likelihood) 솔버를 지원합니다.
- **스트리밍 기능** -- ptychography 데이터가 수집되는 동안 거의 실시간 재구성을 위해 설계되어 APS-U 데이터 속도를 지원합니다.
- **모듈식 설계** -- 확장성과 테스트를 위한 순방향 모델, 솔버, I/O 간의 명확한 분리.
- **다중 GPU 지원** -- 대용량 데이터셋을 위해 여러 GPU에 걸쳐 재구성을 분산합니다.

## 지원 알고리즘

| 알고리즘 | 설명 |
|-----------|-------------|
| ePIE | Extended Ptychographic Iterative Engine |
| DM | Difference Map 솔버 |
| LSQ-ML | Least-Squares Maximum Likelihood |
| Position correction | 프로브 위치 및 객체의 공동 정제 |
| Probe recovery | 프로브와 객체의 동시 재구성 |

## 일반적인 성능

NVIDIA A100 하드웨어의 GPU 가속 솔버는 표준 데이터셋 크기의 거의 실시간 ptychography 재구성을 가능하게 하며, 처리량은 APS-U 스트리밍 데이터 속도와 호환됩니다.

## 저장소

- GitHub: <https://github.com/AdvancedPhotonSource/tike>
- 라이선스: BSD-3-Clause
- 언어: Python/CUDA
- 주요 유지 관리자: Advanced Photon Source, Argonne National Laboratory

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| Ptychography 노트 | 싱크로트론 기법 문서 참조 |
