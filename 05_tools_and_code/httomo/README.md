# HTTomo

## 개요

HTTomo (High Throughput Tomography)는 Diamond Light Source에서 개발한 GPU 가속 모듈식 토모그래피 처리 파이프라인입니다. YAML 기반 워크플로 구성 시스템을 제공하여 플러그인 아키텍처를 통해 전처리, 재구성, 후처리 단계를 연결하며, TB 규모 싱크로트론 토모그래피 데이터셋의 거의 실시간 처리를 가능하게 합니다.

## 주요 기능

- **YAML 기반 워크플로 구성** -- 사람이 읽기 쉽고, 버전 관리가 가능하며, 본질적으로 재현 가능한 선언적 파이프라인 정의.
- **모듈식 플러그인 아키텍처** -- 표준화된 인터페이스를 갖춘 전처리, 재구성, 후처리용 자체 완비 플러그인. 핵심 프레임워크 수정 없이 새로운 알고리즘을 추가할 수 있습니다.
- **GPU 가속 백엔드** -- CuPy 및 커스텀 CUDA 커널을 활용하여 최신 검출기 데이터 속도와 호환되는 고처리량 처리를 지원합니다.
- **청크 기반 처리** -- 대용량 데이터셋을 메모리 효율적인 청크로 분할하여, 메모리 부족 오류 없이 임의의 큰 볼륨도 처리할 수 있습니다.
- **MPI 병렬 처리** -- 클러스터 배포를 위해 여러 GPU 및 노드에 걸친 분산 처리.
- **HDF5/NeXus I/O** -- 표준 싱크로트론 데이터 형식을 읽고 씁니다.
- **TomoPy 및 CuPy 백엔드와의 통합** -- 핵심 알고리즘의 백엔드로 검증된 재구성 라이브러리를 활용합니다.

## 지원 알고리즘

| 알고리즘 | 설명 |
|-----------|-------------|
| Normalization | 이상치 처리를 포함한 플랫/다크 필드 보정 |
| Ring removal | 다양한 링 아티팩트 억제 방법 |
| Phase retrieval | Paganin 및 transport-of-intensity 방법 |
| Center finding | 자동 회전 중심 검출 (Vo 방법) |
| FBP (CPU/GPU) | TomoPy/CuPy 백엔드를 통한 필터링된 역투영 |
| Iterative recon | 백엔드 라이브러리를 통한 SIRT, CGLS |
| Segmentation | 재구성 후 분할 플러그인 |

## 예제 구성

```yaml
- method: normalize
  module_path: httomo.methods.preprocessing
  parameters:
    cutoff: 10

- method: find_center_vo
  module_path: httomo.methods.misc

- method: recon
  module_path: httomo.methods.reconstruction
  parameters:
    algorithm: FBP_CUDA
    center: auto
```

## 일반적인 성능

GPU 가속 처리는 표준 싱크로트론 토모그래피 데이터셋에서 거의 실시간 처리량을 가능하게 합니다. 청크 기반 메모리 관리를 통해 GPU 메모리가 제한된 하드웨어에서도 TB 규모 데이터셋을 처리할 수 있습니다.

## 저장소

- GitHub: <https://github.com/DiamondLightSource/httomo>
- 라이선스: Apache-2.0
- 언어: Python/CUDA
- 주요 유지 관리자: Diamond Light Source

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [review_httomo_2024.md](../../04_publications/ai_ml_synchrotron/review_httomo_2024.md) | 출판물 리뷰 |
