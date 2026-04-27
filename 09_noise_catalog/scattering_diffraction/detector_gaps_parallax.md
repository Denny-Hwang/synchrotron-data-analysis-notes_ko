# 검출기 간격 및 시차(Detector Gaps & Parallax)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 산란 / 회절 / 토모그래피 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 큼(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |
| **기원 도메인** | 방사광(다중 시설: ESRF, Diamond, DESY, APS) |

## 설명

다중 모듈 영역 검출기(Pilatus, Eiger, Jungfrau, Medipix)에는 광자가 검출되지 않는 센서 타일 간 물리적 간격이 존재합니다. 이러한 간격은 회절 패턴, SAXS 이미지 및 토모그래피 투영 영상에서 데이터가 누락된 줄무늬를 만듭니다. 두꺼운 센서의 시차(parallax, 상호작용 깊이) 효과는 위치에 따라 점확산(point spread)이 달라지게 하며, 비스듬한 각도로 입사한 광자가 잘못된 측면 위치에 기록되도록 합니다.

## 근본 원인

### 검출기 간격
- ASIC/센서 모듈은 데드 보더(wire-bond pads, guard rings)를 가짐
- 타일형 검출기: 예를 들어, Pilatus 6M = 60개 모듈, 칩 사이에 ~7 픽셀 간격
- 데이터 손실 → Bragg 반사 누락, SAXS에서 방위각 커버리지 불완전

### 시차(Parallax)
- 두꺼운 센서(450-1000 μm Si, 750 μm CdTe)는 유한한 광자 흡수 깊이를 가짐
- 비스듬한 각도로 입사한 광자는 흡수되기 전 측면으로 이동
- 측면 변위 = 흡수 깊이 × tan(입사각)
- 비대칭 PSF가 발생하며, 위치에 따라 달라지고 검출기 가장자리로 갈수록 악화

## 빠른 진단

```python
import numpy as np

def find_detector_gaps(image_2d, threshold=0):
    """Identify detector gap regions (zero-count columns/rows)."""
    # Gaps: contiguous zero-value columns or rows
    col_sums = image_2d.sum(axis=0)
    row_sums = image_2d.sum(axis=1)
    gap_cols = np.where(col_sums <= threshold)[0]
    gap_rows = np.where(row_sums <= threshold)[0]
    # Group contiguous gaps
    def group_contiguous(arr):
        if len(arr) == 0:
            return []
        groups = [[arr[0]]]
        for v in arr[1:]:
            if v == groups[-1][-1] + 1:
                groups[-1].append(v)
            else:
                groups.append([v])
        return [(g[0], g[-1]) for g in groups]
    col_gaps = group_contiguous(gap_cols)
    row_gaps = group_contiguous(gap_rows)
    print(f"Column gaps: {col_gaps}")
    print(f"Row gaps: {row_gaps}")
    return col_gaps, row_gaps
```

## 탐지 방법

### 시각적 지표

- **간격:** 검출기 이미지에서 데이터가 누락된 라인의 규칙적 격자
- **시차:** 검출기 가장자리 쪽으로 향하는 날카로운 특징(Bragg 피크, 빔 중심)의 방사형 줄무늬
- 점확산함수(PSF)가 큰 각도에서 비대칭적이고 길쭉해짐

### 자동 탐지

```python
import numpy as np

def measure_parallax_psf(image, peak_positions, box_size=20):
    """Measure PSF anisotropy at different detector positions."""
    results = []
    for y, x in peak_positions:
        box = image[y-box_size//2:y+box_size//2, x-box_size//2:x+box_size//2]
        if box.shape != (box_size, box_size):
            continue
        # Second moments → PSF shape
        yy, xx = np.mgrid[:box_size, :box_size]
        total = box.sum()
        if total <= 0:
            continue
        cy = (yy * box).sum() / total
        cx = (xx * box).sum() / total
        sigma_y = np.sqrt(((yy - cy)**2 * box).sum() / total)
        sigma_x = np.sqrt(((xx - cx)**2 * box).sum() / total)
        anisotropy = max(sigma_y, sigma_x) / (min(sigma_y, sigma_x) + 1e-10)
        results.append({'pos': (y, x), 'anisotropy': anisotropy})
    return results
```

## 보정 방법

### 간격 보정

1. **다중 검출기 위치:** 2개 이상의 오프셋 위치에서 데이터를 수집하여 병합으로 간격을 채움
2. **방위각 보간:** SAXS에서 방위각 대칭성을 이용하여 간격을 가로질러 보간
3. **마스킹과 재구성:** 간격을 누락 데이터로 표시하고 반복 알고리즘 사용
4. **가상 검출기 병합:** 다중 패널 검출기를 위한 소프트웨어 스티칭

### 시차 보정

1. **기하학적 보정:** 알려진 기하 정보를 바탕으로 위치 의존적 시프트 적용
2. **상호작용 깊이 모델링:** 센서 내 광자 흡수 프로파일 모델링
3. **PSF 디컨볼루션:** 위치 의존적 디컨볼루션

```python
def correct_parallax_shift(x_det, y_det, detector_distance, sensor_thickness,
                           mean_absorption_depth):
    """Correct pixel positions for parallax in thick sensor."""
    r_det = np.sqrt(x_det**2 + y_det**2)
    two_theta = np.arctan2(r_det, detector_distance)
    # Lateral shift due to parallax
    lateral_shift = mean_absorption_depth * np.tan(two_theta)
    # Correction: shift toward beam center
    correction_x = -lateral_shift * x_det / (r_det + 1e-10)
    correction_y = -lateral_shift * y_det / (r_det + 1e-10)
    return x_det + correction_x, y_det + correction_y
```

### 소프트웨어 도구

- **pyFAI** (ESRF) — 검출기 간격 처리, 기하학적 보정, 시차 인식 적분
- **DIALS** — 다중 패널 검출기 기하 정제
- **FIT2D** — 마스킹 기능을 갖춘 고전적 2D 적분
- **NeXus/HDF5 detector geometry** — 표준 검출기 기술 형식

## 주요 참고문헌

- **Kraft et al. (2009)** — "Characterization and calibration of Pilatus detectors"
- **Henrich et al. (2009)** — "PILATUS: a single photon counting pixel detector"
- **Ashiotis et al. (2015)** — "pyFAI: a Python library for high performance azimuthal integration"
- **Hülsen et al. (2006)** — "Distortion calibration of the PILATUS detector"

## 시설별 벤치마크

| 시설 | 검출기 | 간격 처리 |
|------|--------|----------|
| ESRF | Eiger2 CdTe | 시차 보정 포함 pyFAI |
| Diamond | Pilatus 6M / Eiger2 | DIALS 다중 패널 정제 |
| DESY | Lambda/Eiger | DAWN/pyFAI 적분 |
| SPring-8 | Pilatus3 / custom | 빔라인 특화 보정 |
| SLS | Eiger 16M | 처리 파이프라인 내 네이티브 간격 보간 |

## 실제 보정 전후 예시

다음 출판된 자료들은 실제 실험적 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림 | 설명 | 라이선스 |
|------|------|------|------|---------|
| [pyFAI documentation](https://pyfai.readthedocs.io/) | 소프트웨어 문서 | 다수 | 실제 검출기 데이터를 활용한 간격 채움, 검출기 기하 보정 및 방위각 적분 예시 | MIT |

> **권장 참고자료**: [pyFAI — Python Fast Azimuthal Integration (ESRF)](https://pyfai.readthedocs.io/)

## 관련 자료

- [검출기 일반 문제](../cross_cutting/detector_common_issues.md) — 일반적 검출기 결함
- [불량/과열 픽셀](../xrf_microscopy/dead_hot_pixel.md) — 개별 픽셀 결함 vs 모듈 간격
- [스티칭 아티팩트](../ptychography/stitching_artifact.md) — 관련된 경계/접합 아티팩트
