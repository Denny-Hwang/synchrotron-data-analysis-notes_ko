# TomoPy -- 모듈 구조 및 알고리즘 참고 사항

## 최상위 패키지 레이아웃

```
tomopy/
  io/           # Data I/O (HDF5, TIFF, SXM, etc.)
  prep/         # Preprocessing (normalize, phase, stripe, alignment)
  recon/        # Reconstruction algorithms
  misc/         # Utilities (morph, corr, phantom generation)
  sim/          # Forward projection / simulation
  util/         # Internal helpers, dtype handling, multiprocessing
```

## 모듈 세부 사항

### `tomopy.io`

- `exchange.py` -- APS Data Exchange HDF5 스키마를 읽고 씁니다.
- `reader.py` -- 지연 로딩을 지원하는 범용 HDF5 / TIFF 스택 리더.
- `writer.py` -- 선택적 압축이 포함된 TIFF 스택 및 HDF5 라이터.

빔라인 특정 리더 (예: `read_aps_32id`, `read_aps_2bm`)는 빔라인 HDF5 경로를 표준 exchange 레이아웃에 매핑하는 얇은 래퍼입니다.

### `tomopy.prep`

| 하위 모듈 | 주요 함수 |
|-----------|---------------|
| `normalize.py` | `normalize()`, `normalize_bg()` -- 플랫/다크 필드 보정 |
| `phase.py` | `retrieve_phase()` -- Paganin 단일 거리 위상 복원 |
| `stripe.py` | `remove_stripe_fw()`, `remove_stripe_ti()` -- 푸리에 / Titarenko |
| `alignment.py` | `align_seq()`, `find_center()`, `find_center_vo()` |

### `tomopy.recon`

`recon()` 디스패처는 `algorithm` 매개변수에 따라 백엔드를 선택합니다.

| 알고리즘 키 | 방법 | 백엔드 |
|---------------|--------|----------|
| `gridrec` | 푸리에 그리딩 FBP | C 확장 |
| `fbp` | 직접 필터 역투영 | C 확장 |
| `art` | 대수적 재구성 기법 | C 확장 |
| `sirt` | 동시 반복법 | C 확장 |
| `mlem` / `osem` | 최대 우도 EM | C 확장 |
| `tv` | 총 변동 정규화 | C 확장 |
| `astra` | 모든 ASTRA 알고리즘 | 플러그인 (GPU) |

재구성은 C 레이어에서 OpenMP 스레드를 통해 사이노그램 행에 대해 병렬화됩니다. Python 측에서는 매우 큰 데이터셋에 대해 청크 수준 병렬 처리에 `multiprocessing`이 사용됩니다.

### `tomopy.misc`

- `phantom.py` -- Shepp-Logan 및 커스텀 팬텀 생성기.
- `corr.py` -- 중앙값 필터링, 가우시안 스무딩.
- `morph.py` -- 재구성된 볼륨에 대한 이진 형태학적 연산.

## C 확장

성능이 중요한 루프는 C로 구현되며 `ctypes`를 통해 노출됩니다. 소스 파일은 `src/` 아래에 위치하며 `setup.py` / `meson.build`로 설치 시 컴파일됩니다.

주요 C 소스 파일:

| 파일 | 용도 |
|------|---------|
| `gridrec.c` | 푸리에 공간 그리딩 재구성 |
| `project.c` | 순방향 / 역투영 (광선 구동) |
| `art.c` | ART 반복 커널 |
| `sirt.c` | SIRT 반복 커널 |
| `utils.c` | 패딩, 배열 전치 헬퍼 |

## 데이터 흐름 요약

```
Raw HDF5  -->  io.reader  -->  prep.normalize  -->  prep.phase (optional)
  -->  prep.stripe  -->  recon.recon()  -->  io.writer  -->  TIFF / HDF5
```

## 확장 지점

- 커스텀 알고리즘은 `tomopy.recon.algorithm.register()`를 통해 등록할 수 있습니다.
- ASTRA 통합은 `astra.create_sino3d_gpu()`에 데이터를 전달하고 가능한 경우 불필요한 복사를 피하면서 재구성된 슬라이스를 가져옵니다.
