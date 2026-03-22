# 리청킹 데이터 무결성(Rechunking Data Integrity)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 교차 분야(Cross-cutting) |
| **노이즈 유형** | 계산(Computational) |
| **심각도** | 주요(Major) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

```
원본 HDF5 데이터 (올바름)              리청킹 실패 후

슬라이스 0: ##################     슬라이스 0: ##################
슬라이스 1: ##################     슬라이스 1: ##################
슬라이스 2: ##################     슬라이스 2: ..................  <- 0값 (손실)
슬라이스 3: ##################     슬라이스 3: ..................  <- 0값 (손실)
슬라이스 4: ##################     슬라이스 4: ##################
...                                슬라이스 5: @@@@....####......  <- 손상됨

차원 확인:                         차원 불일치:
  (1800, 2048, 2048) OK              (1795, 2048, 2048) X  <- 5 슬라이스 누락!
```

## 설명

리청킹 및 데이터 무결성 문제는 포맷 변환, HDF5 데이터셋 리청킹 또는 데이터 전송 작업 중에 발생하는 데이터 손상 문제의 한 유형입니다. 누락된 슬라이스, 0으로 채워진 영역, 손상된 값, 차원 불일치 또는 조용히 잘린 데이터셋으로 나타납니다. 기기 관련 아티팩트와 달리, 이것은 원본 데이터가 보존되지 않으면 정보를 비가역적으로 파괴하는 순수 계산 실패입니다.

## 근본 원인

가장 흔한 원인은 HDF5 리청킹 중 중단된 쓰기 작업입니다 — 프로세스가 쓰기 도중 종료되면(OOM, 벽시간 초과, 파일시스템 쿼터) 출력 파일에는 유효한 청크와 초기화되지 않은 청크가 혼재합니다. Dask 기반 리청킹은 태스크 그래프가 사용 가능한 메모리를 초과할 때 실패할 수 있으며, 워커 충돌 후 부분적 출력을 남깁니다. 네트워크 파일시스템(NFS, GPFS) 문제가 병렬 쓰기 중 데이터를 손상시킬 수 있습니다. 포맷 변환 중 바이트 순서(엔디안) 불일치가 뒤섞인 값을 생성합니다. 압축 코덱 불일치가 가비지 데이터를 조용히 생성합니다. 또한 dtype 변환 중 정수 오버플로(예: 클리핑 없이 float64에서 uint16으로)가 래핑 손상을 유발합니다.

## 빠른 진단

```python
import numpy as np
import h5py

with h5py.File("reconstructed_volume.h5", "r") as f:
    dset = f["/exchange/data"]
    print(f"형태: {dset.shape}, Dtype: {dset.dtype}, 청크: {dset.chunks}")
    for i in range(0, dset.shape[0], dset.shape[0] // 20):
        slice_data = dset[i]
        if np.all(slice_data == 0) or np.any(np.isnan(slice_data)):
            print(f"경고: 슬라이스 {i}이 0값이거나 NaN을 포함합니다!")
```

## 탐지 방법

### 시각적 지표

- 볼륨을 스크롤할 때 유효한 데이터 사이에 산재한 검은(0값) 슬라이스
- 청크 경계(예: 64 또는 128 슬라이스마다)에서의 갑작스러운 강도 점프 또는 불연속
- 데이터셋 차원과 dtype에 대해 예상보다 상당히 작은 파일 크기
- 검출기 물리학과 불일치하는 뒤섞인 또는 소금-후추 노이즈 패턴

### 자동 탐지

```python
import numpy as np
import h5py
from pathlib import Path


def verify_hdf5_integrity(filepath, dataset_path="/exchange/data",
                           expected_shape=None, sample_fraction=0.1,
                           checksum_file=None):
    """HDF5 데이터셋의 포괄적 무결성 검사."""
    issues = []
    slice_report = {}

    if not Path(filepath).exists():
        return {"is_valid": False, "issues": ["파일이 존재하지 않습니다"]}

    try:
        f = h5py.File(filepath, "r")
    except Exception as e:
        return {"is_valid": False, "issues": [f"HDF5 파일을 열 수 없습니다: {e}"]}

    try:
        if dataset_path not in f:
            issues.append(f"데이터셋 '{dataset_path}'을 파일에서 찾을 수 없습니다")
            return {"is_valid": False, "issues": issues}

        dset = f[dataset_path]

        if expected_shape is not None and dset.shape != expected_shape:
            issues.append(f"형태 불일치: 예상 {expected_shape}, 실제 {dset.shape}")

        num_slices = dset.shape[0]
        num_samples = max(1, int(num_slices * sample_fraction))
        sample_indices = np.linspace(0, num_slices - 1, num_samples, dtype=int)

        ref_checksums = None
        if checksum_file is not None and Path(checksum_file).exists():
            ref_checksums = np.load(checksum_file)

        zero_slices = []
        nan_slices = []

        for idx in sample_indices:
            idx = int(idx)
            try:
                slice_data = dset[idx]
            except Exception as e:
                issues.append(f"슬라이스 {idx} 읽기 불가: {e}")
                continue

            if np.all(slice_data == 0):
                zero_slices.append(idx)

            if np.issubdtype(slice_data.dtype, np.floating):
                if np.any(np.isnan(slice_data)):
                    nan_slices.append(idx)

            if ref_checksums is not None and idx < len(ref_checksums):
                current_checksum = np.sum(slice_data.astype(np.float64))
                if not np.isclose(current_checksum, ref_checksums[idx], rtol=1e-6):
                    issues.append(f"슬라이스 {idx} 체크섬 불일치")

        if zero_slices:
            issues.append(f"0값 슬라이스 탐지: {zero_slices}")
        if nan_slices:
            issues.append(f"NaN 값 슬라이스: {nan_slices}")

    finally:
        f.close()

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "slice_report": slice_report,
    }
```

## 해결 방법 및 완화

### 예방

- 처리된 출력이 완전히 검증될 때까지 항상 원본 데이터를 보존합니다.
- 원자적 쓰기 패턴을 사용합니다: 임시 파일에 쓰고, 검증한 후 최종 경로로 이름을 변경합니다.
- Dask 워커에 보수적인 메모리 제한을 설정합니다(사용 가능 RAM의 50-70%).
- 변환 후 검증을 위해 소스 데이터에서 슬라이스별 체크섬을 계산합니다.

### 보정 — 전통적 방법

```python
import numpy as np
import h5py
from pathlib import Path


def safe_rechunk_hdf5(source_path, dest_path, dataset_path="/exchange/data",
                       new_chunks=None, compression="gzip"):
    """무결성 검증이 포함된 안전한 HDF5 데이터셋 리청킹."""
    tmp_path = dest_path + ".tmp"

    with h5py.File(source_path, "r") as src:
        dset_src = src[dataset_path]
        shape = dset_src.shape
        dtype = dset_src.dtype

        if new_chunks is None:
            new_chunks = (1, shape[1], shape[2])

        print("소스 체크섬 계산 중...")
        src_checksums = np.zeros(shape[0], dtype=np.float64)
        for i in range(shape[0]):
            src_checksums[i] = np.sum(dset_src[i].astype(np.float64))

        print(f"{shape} 리청킹 중 (chunks={new_chunks})...")
        with h5py.File(tmp_path, "w") as dst:
            dset_dst = dst.create_dataset(
                dataset_path, shape=shape, dtype=dtype,
                chunks=new_chunks, compression=compression,
            )
            for i in range(shape[0]):
                dset_dst[i] = dset_src[i]
                if i % 100 == 0:
                    print(f"  슬라이스 {i}/{shape[0]} 기록됨")

    print("리청킹된 데이터 검증 중...")
    errors = []
    with h5py.File(tmp_path, "r") as dst:
        dset_dst = dst[dataset_path]
        if dset_dst.shape != shape:
            raise RuntimeError(f"형태 불일치: 소스 {shape} vs 대상 {dset_dst.shape}")
        for i in range(shape[0]):
            dst_checksum = np.sum(dset_dst[i].astype(np.float64))
            if not np.isclose(dst_checksum, src_checksums[i], rtol=1e-6):
                errors.append(i)

    if errors:
        Path(tmp_path).unlink()
        raise RuntimeError(f"{len(errors)}개 슬라이스 검증 실패: {errors[:20]}...")

    Path(tmp_path).rename(dest_path)
    print(f"리청킹 완료 및 검증됨: {dest_path}")
```

## 보정하지 않을 경우의 영향

손상된 데이터는 명백하게 잘못되지 않을 수 있는 과학적으로 무의미한 결과를 생성합니다. 토모그래피 볼륨의 0값 슬라이스는 3D 렌더링에서 실제 특징으로 잘못 해석되는 평면 공극을 만듭니다. 누락된 슬라이스는 모든 후속 데이터의 z좌표를 이동시켜 다른 모달리티와의 공간 정합을 손상시킵니다. 다중 사용자 시설에서 데이터가 수집 후 수개월 뒤에 처리되면, 원본 데이터가 빠른 저장소에서 이미 삭제되어 손상이 비가역적일 수 있습니다.

## 관련 자료

- [토모그래피 EDA 노트북](../../06_data_structures/eda/tomo_eda.md) — 데이터 검사 및 품질 검사
- [HDF5 심화](../../06_data_structures/hdf5_deep_dive.md) — 청킹 및 압축 전략
- [데이터 파이프라인 — 처리](../../07_data_pipeline/processing.md) — 안전한 리청킹 패턴

## 핵심 요점

리청킹 및 포맷 변환 중 데이터 무결성 문제는 조용한 킬러입니다 — 데이터 변환 전후에 항상 체크섬을 계산하고 검증하며, 검증이 완료될 때까지 원본 데이터를 보존하고, 부분 쓰기 손상을 방지하기 위해 원자적 쓰기 작업을 사용하세요.
