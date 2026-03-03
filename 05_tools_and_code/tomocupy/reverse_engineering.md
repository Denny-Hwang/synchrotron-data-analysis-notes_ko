# TomocuPy -- 아키텍처 및 역공학 노트

## 모듈 레이아웃

```
tomocupy/
  cli/            # Command-line entry points
  conf.py         # Configuration and parameter defaults
  proc.py         # Top-level processing orchestrator
  rec.py          # Reconstruction loop (chunk scheduler)
  retrieve.py     # Phase retrieval (Paganin)
  remove.py       # Ring / stripe removal
  utils.py        # Padding, centering, logging helpers
  kernels/        # Raw CUDA / CuPy RawKernel sources (.cu)
  tests/
```

## CuPy 커널 전략

TomocuPy는 가능한 경우 `cupyx.scipy`를 피하고 대신 `cupy.RawKernel` 객체로 로드되는 수작업 CUDA 커널을 제공합니다. 주요 커널:

| 커널 파일 | 용도 |
|-------------|---------|
| `fbp.cu` | 램프 필터 역투영 (팬/평행 빔) |
| `log_polar.cu` | 중심 보정을 위한 로그 극좌표 보간 |
| `ring.cu` | 푸리에 공간 링 아티팩트 억제 |

각 커널은 임포트 시 한 번 컴파일되며 CuPy의 JIT 캐시에 캐싱됩니다.

## 스트리밍 파이프라인

재구성은 세 단계 파이프라인으로 구성됩니다:

1. **H2D** -- HDF5에서 사이노그램 청크를 핀드 호스트 메모리로 읽은 다음 GPU 스테이징 버퍼로 비동기 복사합니다.
2. **Compute** -- GPU에서 전처리 (플랫/다크 보정, 위상 복원, 링 제거) 및 FBP를 적용합니다.
3. **D2H** -- 재구성된 슬라이스 청크를 호스트 메모리로 복사하고 출력 HDF5 파일에 기록합니다.

단계들은 두 개의 CUDA 스트림을 통해 중첩되어 다음 청크의 H2D 전송이 현재 청크의 연산과 동시에 실행됩니다.

### 청크 크기

청크 크기는 사용 가능한 GPU 메모리의 약 60%를 채우도록 자동 조정됩니다. 나머지 40%는 중간 FFT 버퍼와 램프 필터를 위해 예약됩니다.

## 메모리 관리

- 모든 GPU 배열은 `proc.init()` 중에 한 번 사전 할당됩니다.
- 재구성 배치 간에 `cupy.get_default_memory_pool().free_all_blocks()`를 호출하여 단편화를 방지합니다.
- 비동기 DMA 전송을 가능하게 하기 위해 모든 HDF5 읽기 버퍼에 핀드 호스트 메모리 (`cupy.cuda.alloc_pinned_memory`)를 사용합니다.

## 벤치마크 참조 데이터

| 데이터셋 크기 | GPU | 처리 시간 | 참고 사항 |
|-------------|-----|-----------|-------|
| 2048 x 2048 x 1500 | A100 40 GB | 25 s | FBP gridrec |
| 2048 x 2048 x 1500 | V100 32 GB | 42 s | FBP gridrec |
| 4096 x 4096 x 3000 | A100 40 GB | 210 s | FBP gridrec, 청크 처리 |

모든 시간 측정은 I/O를 포함합니다. `tomocupy bench` CLI로 측정되었습니다.

## 주요 설계 결정

1. **단일 GPU 전용** -- 다중 GPU 또는 분산 재구성은 범위 밖이며, 철학은 "빔라인 워크스테이션당 하나의 GPU"입니다.
2. **최소 의존성** -- CuPy, NumPy, h5py 및 scipy만 필요합니다.
3. **반복적 솔버 없음** -- TomocuPy는 해석적 (FBP) 방법에 집중합니다. 반복적 재구성을 위해서는 ASTRA Toolbox 또는 GPU 가속이 있는 TomoPy를 사용하도록 안내합니다.
