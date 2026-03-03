# TomocuPy -- 설정 및 벤치마크 재현 가이드

## 사전 요구 사항

| 요구 사항 | 최소 | 권장 |
|-------------|---------|-------------|
| NVIDIA GPU | Pascal (sm_60) | Ampere A100 |
| CUDA Toolkit | 11.2 | 12.x |
| GPU RAM | 16 GB | 40 GB |
| Python | 3.9 | 3.10+ |
| OS | Linux (x86_64) | Rocky Linux 8+ |

## 설치

### 1. Conda 환경 생성

```bash
conda create -n tomocupy python=3.10 -y
conda activate tomocupy
```

### 2. CuPy 설치 (CUDA 버전에 맞게)

```bash
# For CUDA 12.x
pip install cupy-cuda12x

# For CUDA 11.x
pip install cupy-cuda11x
```

### 3. TomocuPy 설치

```bash
git clone https://github.com/tomography/tomocupy.git
cd tomocupy
pip install -e .
```

### 4. 설치 확인

```bash
python -c "import tomocupy; print(tomocupy.__version__)"
```

## 테스트 데이터 다운로드

APS는 HDF5 `exchange` 형식의 참조 데이터셋을 제공합니다.

```bash
# Small test phantom (256 x 256 x 128)
wget https://tomobank.readthedocs.io/en/latest/_downloads/phantom_00001.h5

# Medium dataset (2048 x 2048 x 1500) -- ~4 GB
wget https://tomobank.readthedocs.io/en/latest/_downloads/tomo_00001.h5
```

또는 Shepp-Logan 팬텀을 생성할 수 있습니다:

```python
import tomopy
obj = tomopy.shepp3d(size=512)
ang = tomopy.angles(720)
proj = tomopy.project(obj, ang)
tomopy.write_hdf5(proj, fname="shepp_512.h5")
```

## 재구성 실행

```bash
tomocupy recon \
    --file-name tomo_00001.h5 \
    --rotation-axis 1024 \
    --reconstruction-type full \
    --nsino-per-chunk 4 \
    --output-dir ./recon_output
```

주요 플래그:

| 플래그 | 용도 |
|------|---------|
| `--rotation-axis` | 픽셀 단위의 회전 중심 |
| `--nsino-per-chunk` | GPU 배치당 처리되는 사이노그램 수 |
| `--retrieve-phase` | Paganin 위상 복원 활성화 |
| `--remove-stripe` | 링/줄무늬 제거 활성화 |

## 벤치마크 재현

TomocuPy에는 내장 벤치마킹 명령이 포함되어 있습니다.

```bash
tomocupy bench \
    --file-name tomo_00001.h5 \
    --rotation-axis 1024 \
    --nruns 5
```

이 명령은 다음을 수행합니다:

1. 시간을 측정하지 않는 한 번의 실행으로 GPU를 워밍업합니다.
2. `--nruns`회의 시간 측정 재구성을 실행합니다.
3. 처리 시간의 평균 및 표준 편차를 출력합니다.

### 예상 결과 (A100 40 GB)

| 데이터셋 | 평균 시간 | 표준 편차 |
|---------|-----------|-----|
| 2048 x 2048 x 1500 | 25.3 s | 0.4 s |
| 4096 x 4096 x 3000 | 212 s | 3.1 s |

## 문제 해결

| 문제 | 해결 방법 |
|---------|----------|
| `CUDADriverError` | `nvidia-smi`가 작동하는지 확인하고 CUDA 툴킷 버전이 CuPy와 일치하는지 확인 |
| GPU 메모리 부족 | `--nsino-per-chunk` 줄이기 |
| 느린 I/O | HDF5 저장에 SSD 또는 NVMe 사용; `--use-pinned-memory` 활성화 |
| 부정확한 재구성 | `--rotation-axis` 값 재확인 |
