# TomocuPy: GPU 가속 토모그래피 재구성

## 개요

**TomocuPy**는 APS(아르곤 국립연구소, Argonne National Laboratory)에서 개발된 GPU 가속 토모그래피 재구성 패키지입니다. **CuPy**(GPU 가속 NumPy)를 사용하여 핵심 TomoPy 알고리즘을 재구현하여 CPU 기반 TomoPy 대비 20-30배 속도 향상을 달성합니다.

**리포지토리**: [https://github.com/nikitinvv/tomocupy](https://github.com/nikitinvv/tomocupy)

## 아키텍처

### 설계 철학
```
TomoPy (CPU)                    TomocuPy (GPU)
─────────────                   ──────────────
NumPy 배열           →          CuPy 배열
CPU 계산             →          CUDA 커널
순차적 슬라이스      →          병렬 슬라이스
디스크 I/O 병목      →          스트리밍 파이프라인
```

### 핵심 구성 요소

1. **CuPy 커널**: 핵심 수학 연산(FFT, 역투영)을 GPU에서 수행
2. **스트리밍 파이프라인**: 데이터 전송과 계산을 오버랩
3. **청크 처리(Chunk Processing)**: GPU 메모리보다 큰 볼륨 처리
4. **래퍼 함수**: TomoPy 호환 API

### 스트리밍 파이프라인 아키텍처

```
CPU 메모리                  GPU 메모리               CPU 메모리
[청크 1] ──전송──→ [처리] ──전송──→ [결과 1]
[청크 2] ──전송──→ [처리] ──전송──→ [결과 2]
           ↑              ↑                        ↑
           └──────────────┘────────────────────────┘
           오버랩됨 (전송 + 계산 동시 수행)
```

## 지원 알고리즘

| 알고리즘 | 유형 | 사용 사례 |
|-----------|------|----------|
| **FBP** | 해석적 | 표준 재구성, 가장 빠름 |
| **Gridrec** | 해석적 (FFT) | FBP와 동등, 약간 다른 구현 |
| **SIRT** | 반복적 | 노이즈/희소 데이터에서 더 나은 품질 |
| **Log-polar FBP** | 해석적 | 대안적 좌표계 |

### GPU에서의 FBP

```python
# 간소화된 GPU FBP 파이프라인 (CuPy)
import cupy as cp
from cupyx.scipy.fft import fft, ifft, fftfreq

def fbp_gpu(sinogram, theta, center):
    """단일 슬라이스에 대한 GPU 가속 필터링 역투영."""
    n_angles, n_det = sinogram.shape

    # 1. GPU로 이동
    sino_gpu = cp.asarray(sinogram)

    # 2. 푸리에 영역에서 램프 필터 적용
    freq = fftfreq(n_det)
    ramp_filter = cp.abs(freq)
    sino_filtered = cp.real(ifft(fft(sino_gpu, axis=1) * ramp_filter[None, :], axis=1))

    # 3. 역투영
    recon = cp.zeros((n_det, n_det), dtype=cp.float32)
    for i, angle in enumerate(theta):
        # 회전 및 누적 (실제 구현은 커스텀 CUDA 커널 사용)
        recon += back_project_line(sino_filtered[i], angle, center)

    return cp.asnumpy(recon)
```

## 벤치마크

### 속도 비교 (2048×2048 사이노그램, 1500 투영)

| 방법 | 플랫폼 | 슬라이스당 시간 | 속도 향상 |
|--------|----------|---------------|---------|
| TomoPy gridrec | CPU (32 코어) | 0.5 s | 1× |
| TomoPy FBP | CPU (32 코어) | 2.0 s | 0.25× |
| **TomocuPy FBP** | **NVIDIA A100** | **0.02 s** | **25×** |
| **TomocuPy gridrec** | **NVIDIA A100** | **0.015 s** | **33×** |

### 전체 볼륨 재구성

| 볼륨 크기 | TomoPy (CPU) | TomocuPy (GPU) | 속도 향상 |
|------------|-------------|----------------|---------|
| 1024³ | 8분 | 15초 | 32× |
| 2048³ | 65분 | 2분 | 32× |
| 4096³ | 520분 | 20분 | 26× |

*참고: 4096³은 GPU 메모리 한계로 인해 청크 기반 처리가 필요.*

### GPU 메모리 사용량

| 볼륨 | FBP 메모리 | 반복적 (SIRT) |
|--------|-----------|------------------|
| 1024³ | ~4 GB | ~8 GB |
| 2048³ | ~16 GB | ~32 GB |
| 4096³ | 청크 처리 | 청크 처리 |

## 사용 예제

```python
import tomocupy as tc
import h5py

# 데이터 로드
with h5py.File('scan.h5', 'r') as f:
    proj = f['/exchange/data'][:]
    flat = f['/exchange/data_white'][:]
    dark = f['/exchange/data_dark'][:]
    theta = f['/exchange/theta'][:] * np.pi / 180  # 라디안으로 변환

# 전처리 (GPU에서)
proj_norm = tc.normalize(proj, flat, dark)
proj_log = tc.minus_log(proj_norm)

# 회전 중심 찾기
center = tc.find_center(proj_log, theta)

# 재구성
recon = tc.recon(proj_log, theta, center=center, algorithm='fbp')
# recon shape: (Nslices, Ny, Nx)
```

## 한계

1. **NVIDIA GPU 필수**: CuPy가 CUDA 지원 NVIDIA GPU를 요구
2. **GPU 메모리**: 청크당 GPU 메모리로 제한 (카드에 따라 16-80 GB)
3. **지오메트리**: 주로 평행빔 지오메트리 (팬/콘 빔은 제한적)
4. **알고리즘 선택**: TomoPy보다 적은 알고리즘 (가장 많이 사용되는 것에 집중)
5. **의존성**: CUDA 툴킷, CuPy 설치가 복잡할 수 있음

## TomoPy와의 비교

| 기능 | TomoPy | TomocuPy |
|---------|--------|----------|
| **속도** | 기준 (CPU) | 20-30배 빠름 (GPU) |
| **알고리즘** | 다수 (FBP, gridrec, SIRT, MLEM, CGLS, ...) | 핵심 하위 집합 (FBP, gridrec, SIRT) |
| **하드웨어** | CPU만 | NVIDIA GPU 필수 |
| **메모리 한계** | 시스템 RAM (~수백 GB) | GPU RAM (16-80 GB) |
| **대용량 볼륨** | 직접 처리 | 청크 기반 스트리밍 |
| **설치** | 쉬움 (pip) | CUDA 설정 필요 |
| **실시간 가능** | 아니오 | 예 (스캔당 초 단위) |
| **품질** | 참조 구현 | 동일한 결과 |

*상세 비교: [05_tools_and_code/tomopy/pros_cons.md](../../05_tools_and_code/tomopy/pros_cons.md)*
