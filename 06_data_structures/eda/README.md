# 방사광 데이터를 위한 탐색적 데이터 분석 (EDA)

## 목적

탐색적 데이터 분석은 데이터 수집 후, 고급 처리나 머신러닝 전의 필수적인
첫 번째 단계입니다. 방사광 실험에서 EDA는 다음을 수행합니다:

1. **데이터 무결성 확인** -- 파일이 완전하고, 손상되지 않았으며, 예상되는 수의 프레임,
   채널 또는 에너지 포인트를 포함하는지 확인합니다.
2. **데이터 품질 평가** -- 불량 픽셀, 핫 픽셀, 포화 영역,
   검출기 아티팩트 및 잡음 수준을 식별합니다.
3. **분포 이해** -- 강도 히스토그램, 동적 범위 활용도 및
   통계적 요약을 검토하여 정규화 전략에 정보를 제공합니다.
4. **구조 발견** -- 공간 패턴, 채널 간 상관관계 및
   분석을 안내할 수 있는 예상치 못한 특징을 찾습니다.
5. **전처리 정보 제공** -- 어떤 보정(배경 제거, 링 제거, 위상 복원)이
   필요한지 결정하고 매개변수를 설정합니다.
6. **기준선 문서화** -- 처리된 결과와 비교할 수 있는 정량적 벤치마크(SNR, 분해능 지표)를
   수립합니다.

## 범용 EDA 체크리스트

모달리티에 관계없이 모든 방사광 데이터셋에 이 체크리스트를 적용하세요:

### 파일 수준 점검

- [ ] 파일이 오류 없이 열림 (손상되거나 잘린 파일이 아님)
- [ ] HDF5 계층에 예상되는 그룹/데이터셋이 존재
- [ ] 데이터셋 형태가 예상 차원과 일치 (행, 열, 채널, 각도)
- [ ] 데이터 유형이 올바름 (uint16, float32 등)
- [ ] 메타데이터 속성이 채워져 있음 (에너지, 픽셀 크기, 타임스탬프)
- [ ] 파일 크기가 예상과 일치 (비정상적으로 작지 않음)

### 배열 수준 통계

- [ ] 각 주요 데이터셋에 대해 min, max, mean, median, std 계산
- [ ] 예상치 못한 NaN, Inf 또는 음수 값 확인
- [ ] 동적 범위 활용 확인 (0에서 잘리거나 포화되지 않음)
- [ ] 프레임/슬라이스 간 통계 비교하여 일관성 확인
- [ ] 비정상적 통계를 가진 이상 프레임 식별

### 공간 품질

- [ ] 대표적인 프레임/슬라이스 시각화
- [ ] 불량 픽셀 클러스터 또는 검출기 간격 확인
- [ ] 체계적 패턴 (줄무늬, 링, 무아레) 확인
- [ ] 공간 범위가 예상 시료 치수와 일치하는지 확인
- [ ] 참조 프레임과 데이터 간 정렬 확인

### 메타데이터 검증

- [ ] 빔 에너지가 예상 값과 일치
- [ ] 픽셀 크기가 구성된 배율에 맞는지 확인
- [ ] 스캔 위치가 예상 범위를 포괄
- [ ] 타임스탬프가 순차적이고 합리적임
- [ ] 모터 위치가 예상 범위 내에 있음

## 모달리티별 EDA 가이드

각 방사광 기법은 고유한 데이터 특성과 품질 지표를 가지고 있습니다:

| 모달리티 | 가이드 | 주요 관심사항 |
|----------|--------|-------------|
| X선 형광 | [xrf_eda.md](xrf_eda.md) | 채널 혼선, 불량 픽셀, I0 정규화 |
| 단층촬영 | [tomo_eda.md](tomo_eda.md) | 링 아티팩트, 회전 중심, 플랫/다크 품질 |
| 분광학 | [spectroscopy_eda.md](spectroscopy_eda.md) | 에지 정렬, 자기흡수, 잡음 |

## 일반 EDA 도구

| 도구 | 용도 | 설치 |
|------|------|------|
| **h5py** | HDF5 읽기 및 검사 | `pip install h5py` |
| **matplotlib** | 2D 시각화 | `pip install matplotlib` |
| **numpy** | 배열 통계 | `pip install numpy` |
| **scipy** | 신호 처리, 통계 | `pip install scipy` |
| **silx** | HDF5 GUI 브라우저 + 플로팅 | `pip install silx` |
| **pandas** | 표 형태 메타데이터 분석 | `pip install pandas` |
| **scikit-image** | 이미지 품질 지표 | `pip install scikit-image` |
| **seaborn** | 통계적 시각화 | `pip install seaborn` |

## 표준 EDA 코드 패턴

### 빠른 통계 요약

```python
import h5py
import numpy as np

def dataset_summary(filepath, dataset_path):
    """Print summary statistics for an HDF5 dataset."""
    with h5py.File(filepath, "r") as f:
        dset = f[dataset_path]
        print(f"Path:   {dataset_path}")
        print(f"Shape:  {dset.shape}")
        print(f"Dtype:  {dset.dtype}")
        print(f"Chunks: {dset.chunks}")
        print(f"Compression: {dset.compression}")

        # Load data (or a subset for large datasets)
        if dset.nbytes > 1e9:
            data = dset[0]   # First frame only
            print("(Statistics for first frame only)")
        else:
            data = dset[:]

        print(f"Min:    {np.nanmin(data):.4g}")
        print(f"Max:    {np.nanmax(data):.4g}")
        print(f"Mean:   {np.nanmean(data):.4g}")
        print(f"Median: {np.nanmedian(data):.4g}")
        print(f"Std:    {np.nanstd(data):.4g}")
        print(f"NaNs:   {np.isnan(data).sum()}")
        print(f"Zeros:  {(data == 0).sum()} ({100*(data==0).mean():.1f}%)")
```

### 프레임별 일관성 확인

```python
def check_frame_consistency(filepath, dataset_path, axis=0):
    """Check mean/std across frames to find anomalous ones."""
    with h5py.File(filepath, "r") as f:
        dset = f[dataset_path]
        nframes = dset.shape[axis]
        means = np.zeros(nframes)
        stds = np.zeros(nframes)
        for i in range(nframes):
            frame = np.take(dset, i, axis=axis)
            means[i] = np.mean(frame)
            stds[i] = np.std(frame)

    # Flag outlier frames
    mean_of_means = np.mean(means)
    std_of_means = np.std(means)
    outliers = np.where(np.abs(means - mean_of_means) > 3 * std_of_means)[0]
    if len(outliers) > 0:
        print(f"WARNING: {len(outliers)} outlier frames detected: {outliers}")
    return means, stds
```

## 실습 노트북

| 노트북 | 설명 |
|--------|------|
| [01_xrf_eda.ipynb](notebooks/01_xrf_eda.ipynb) | XRF 원소 맵 탐색 |
| [02_tomo_eda.ipynb](notebooks/02_tomo_eda.ipynb) | 단층촬영 투영 및 시노그램 분석 |
| [03_spectral_eda.ipynb](notebooks/03_spectral_eda.ipynb) | 분광학 에지 및 잡음 분석 |

## EDA 워크플로우 요약

```
1. 파일 열기, 구조 확인
        |
2. 전역 통계 계산
        |
3. 대표 프레임 시각화
        |
4. 아티팩트 및 이상치 확인
        |
5. 메타데이터 일관성 검사
        |
6. 결과 문서화
        |
7. 전처리 진행
```

## 관련 자료

- [HDF5 구조 가이드](../hdf5_structure/)
- [데이터 규모 분석](../data_scale_analysis.md)
- [처리 파이프라인](../../07_data_pipeline/)
