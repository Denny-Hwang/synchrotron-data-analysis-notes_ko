# TomoPy

## 개요

TomoPy는 Advanced Photon Source (APS), Argonne National Laboratory에서 개발 및 유지 관리하는 토모그래피 데이터 처리 및 이미지 재구성을 위한 표준 오픈소스 Python 라이브러리입니다. 원시 투영 데이터에서 재구성된 3D 볼륨까지의 전체 파이프라인을 포괄하는 종합 툴킷을 제공합니다.

## 주요 기능

- **다중 알고리즘 지원** -- 해석적 (gridrec, FBP) 및 반복적 (ART, SIRT, MLEM, OSEM, TV 정규화) 재구성 방법.
- **전처리 모음** -- 플랫/다크 보정, 위상 복원 (Paganin, Bronnikov), 링 제거, 줄무늬 보정, 징거 제거.
- **플러그인 백엔드** -- 하드웨어 가속을 위한 ASTRA Toolbox (GPU) 및 UFO와의 선택적 통합.
- **HDF5 Data Exchange I/O** -- APS Data Exchange 형식에 대한 네이티브 지원 (`/exchange/data`, `/exchange/data_white`, `/exchange/data_dark`).
- **병렬 실행** -- CPU 병렬 처리를 위한 OpenMP를 통한 멀티스레드 C 확장.

## 일반적인 사용 사례

```python
import tomopy

# Read data
proj, flat, dark, theta = tomopy.read_aps_32id("data.h5")

# Preprocessing
proj = tomopy.normalize(proj, flat, dark)
proj = tomopy.minus_log(proj)
rot_center = tomopy.find_center(proj, theta)

# Reconstruction
recon = tomopy.recon(proj, theta, center=rot_center, algorithm="gridrec")

# Write output
tomopy.write_tiff_stack(recon, fname="recon/slice")
```

## 저장소

- GitHub: <https://github.com/tomography/tomopy>
- 문서: <https://tomopy.readthedocs.io>
- 라이선스: BSD-3-Clause

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [reverse_engineering.md](reverse_engineering.md) | 모듈 구조 및 알고리즘 참고 사항 |
| [pros_cons.md](pros_cons.md) | TomocuPy와의 비교 |
