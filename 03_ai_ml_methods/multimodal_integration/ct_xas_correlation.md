# CT + XAS 상관 분석: 구조 및 화학적 화학종 분석

## 개요

X선 컴퓨터 단층촬영(CT)과 X선 흡수 분광법(XAS)의 상관 분석은 3D 구조 정보와
화학적 화학종 분석(chemical speciation)을 결합하여, 시료가 3D에서 어떻게 보이는지뿐만
아니라 시료 내 특정 원소의 화학적 상태까지 밝혀냅니다.

## 접근법

### 1. 순차적 측정(Sequential Measurement)

```
단계 1: µCT 스캔 → 3D 볼륨 (형태, 밀도)
단계 2: µ-XANES → 2D 화학종 맵 (선택된 슬라이스 또는 ROI)
단계 3: CT와 XANES 데이터 정합(registration)
단계 4: 구조와 화학 정보의 상관 분석
```

**빔라인**: 2-BM-A에서 µCT → 20-BM에서 XANES (동일 시료, 다른 장비)

### 2. 분광 토모그래피(Spectroscopic Tomography, XANES-CT)

흡수단(absorption edge)에 걸쳐 여러 에너지에서 토모그래피 스캔을 수집:

```
각 에너지 E_i에 대해 (흡수단에 걸쳐, 예: Fe K-edge 7100-7200 eV):
    전체 토모그래피 스캔 수집 (900+ 프로젝션)
    에너지 E_i에서 3D 볼륨 재구성

스택: µ(x,y,z,E) → 4D 데이터셋 (공간 + 분광)
각 복셀에서 XANES 스펙트럼 추출 → 3D 화학종 맵
```

**과제**: N_에너지 × 전체 토모그래피 스캔이 필요 (매우 시간 집약적)

### 3. 이중 에너지 CT(Dual-Energy CT)

2-3개 에너지만 사용하는 간소화된 버전:

```
E_흡수단_아래에서 스캔 → µ₁(x,y,z)
E_흡수단_위에서 스캔 → µ₂(x,y,z)

비율 맵: R(x,y,z) = µ₂/µ₁
→ 대상 원소를 포함하는 영역을 강조
→ 비율 값이 산화 상태를 나타냄 (잘 분리된 흡수단 에너지의 경우)
```

## 통합 워크플로

```python
import numpy as np
from skimage import measure

# CT 볼륨과 XANES 화학종 맵 로드
ct_volume = load_ct('ct_scan.h5')           # shape: (Nz, Ny, Nx)
xanes_map = load_xanes('xanes_scan.h5')     # shape: (Ny_xanes, Nx_xanes, N_energies)

# XANES를 CT 좌표계로 정합
from skimage.transform import AffineTransform, warp
# 알려진 변환 적용 (기준 마커 또는 수동 정렬에서)

# CT를 구조적 상으로 분할
labels = segment_ct(ct_volume)  # 예: pore=0, mineral=1, organic=2

# 각 상에 대해 XANES 스펙트럼 추출
for phase_id in [1, 2]:
    mask = labels == phase_id
    # 이 구조적 상 내의 XANES 스펙트럼 추출
    phase_spectra = extract_spectra_in_region(xanes_map, mask)
    # 평균 후 화학종 결정을 위한 피팅
    avg_spectrum = phase_spectra.mean(axis=0)
    fractions = linear_combination_fit(avg_spectrum, references)
    print(f"Phase {phase_id}: {fractions}")
```

## 과학적 응용

### 토양 과학 사례
```
µCT가 드러내는 것:
  - 광물 입자의 위치와 크기
  - 기공 네트워크 구조
  - 유기물 응집체

Fe K-edge에서의 XANES가 드러내는 것:
  - Fe(II) 대 Fe(III) 분포
  - Fe-유기 착물 대 결정성 Fe 광물
  - 응집체 내의 산화환원 기울기

상관 분석:
  - Fe(II)가 기공-광물 계면에 우선적으로 존재
  - Fe(III)가 잘 연결된 기공 영역(산화됨)에 존재
  - Fe-유기 착물이 유기물이 풍부한 응집체에 존재
```

## ML 기회

1. **자동 정합(registration)**: CT와 XANES 간 CNN 기반 이미지 정렬
2. **초해상도 화학종 분석**: 저해상도 XANES + 고해상도 CT에서 세밀한 화학종 분석 예측
3. **전이 학습(Transfer learning)**: CT 형태에서 가능한 화학적 상태 예측
4. **희소 XANES-CT**: ML을 사용하여 더 적은 에너지에서 전체 분광 토모그래피 재구성
5. **결합 분할(Joint segmentation)**: 다중 채널 네트워크를 사용하여 CT와 XANES를 동시에 분할

## 과제

1. **정합 정확도**: 모달리티 간 서브픽셀 정렬 필요
2. **시간**: 전체 XANES-CT에 수 시간에서 수 일 소요
3. **선량(Dose)**: 다수의 스캔이 누적 방사선 선량을 증가
4. **해상도 불일치**: CT가 보통 XANES보다 높은 해상도
5. **자기흡수(Self-absorption)**: XANES 형광 신호가 시료 밀도/두께에 의해 영향받음
