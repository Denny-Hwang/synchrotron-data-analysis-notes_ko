# MAPS -- 데이터 흐름 및 피팅 방법

## 데이터 흐름

```
Beamline scan
  |
  v
Raw data (MDA / HDF5)
  |
  v
MAPS Import
  |- Energy calibration (keV per channel)
  |- Detector dead-time correction
  |
  v
Standards Fitting
  |- Fit reference standard spectra
  |- Derive detector sensitivity vs energy
  |
  v
Per-Pixel Fitting
  |- Gaussian peak model for each element line
  |- Compton + elastic scatter background
  |- Matrix absorption correction (optional)
  |
  v
Quantification
  |- Convert fitted peak areas to ug/cm2
  |- Apply sensitivity calibration
  |
  v
HDF5 Output
  |- /MAPS/XRF_fits     (n_elements x rows x cols)
  |- /MAPS/channel_names (element labels)
  |- /MAPS/scalers       (I0, live time, dwell, etc.)
```

## 피팅 방법

### 1. ROI 적분 (빠른 방법)

각 원소에 대해 미리 정의된 에너지 윈도우가 주요 방출선을 포함합니다. 윈도우 내의 총 카운트가 픽셀별로 합산됩니다. 이 방법은 빠르지만 겹치는 선 (예: Fe-Kbeta와 Co-Kalpha)을 분리할 수 없습니다.

### 2. 픽셀별 가우시안 피팅 (표준 방법)

각 픽셀 스펙트럼을 다음 모델에 피팅합니다:

```
S(E) = sum_i  A_i * G(E; E_i, sigma_i) + B(E)
```

여기서:
- `A_i`는 원소 선 `i`의 피팅된 면적
- `G`는 알려진 방출 에너지 `E_i`에 중심을 둔 가우시안
- `sigma_i`는 해당 에너지에서의 검출기 분해능
- `B(E)`는 다항식 또는 계단 함수 배경

MAPS는 속도를 위해 비음수 최소 제곱법 (NNLS)을 사용합니다. 복잡한 스펙트럼의 경우 Levenberg-Marquardt 솔버를 사용할 수 있습니다.

### 3. NNLS 매트릭스 피팅

순수 원소 스펙트럼 (측정 또는 시뮬레이션)의 참조 매트릭스를 구성합니다. 각 픽셀 스펙트럼은 참조 스펙트럼의 비음수 선형 조합으로 표현됩니다. 이는 명시적인 피크 형상 모델링을 피하고 겹치는 선을 잘 처리합니다.

## 출력 HDF5 스키마

| HDF5 경로 | 형상 | 설명 |
|-----------|-------|-------------|
| `/MAPS/XRF_fits` | (N_elem, rows, cols) | 피팅된 농도 맵 |
| `/MAPS/XRF_fits_quant` | (N_elem, rows, cols) | 정량화된 맵 (ug/cm2) |
| `/MAPS/channel_names` | (N_elem,) | 원소/선 레이블 (예: "Fe", "Zn_K") |
| `/MAPS/scalers` | (N_scaler, rows, cols) | I0, 라이브 타임, 드웰 타임 |
| `/MAPS/scan_metadata` | -- | 스캔 매개변수, 모터 위치 |

## 교정 참고 사항

- 검출기 에너지 교정: 표준 시료의 알려진 방출선을 사용하여 채널 번호를 keV로 선형 피팅.
- 감도 곡선: 표준 피팅에서 도출; 검출기 효율, 필터 흡수 및 입체각을 보정합니다.
- 데드타임 보정: 검출기 전자장치의 입력 카운트 레이트 (ICR)와 출력 카운트 레이트 (OCR)를 사용하여 픽셀별로 적용됩니다.

## 한계

- MAPS는 비공개 소스이며 컴파일된 바이너리로만 제공됩니다.
- GUI 기반 워크플로우는 대규모 배치 처리를 위한 스크립팅이 어려울 수 있습니다.
- Python 바인딩이 제한적이며, 대부분의 자동화는 HDF5 출력과 외부 스크립트에 의존합니다.
