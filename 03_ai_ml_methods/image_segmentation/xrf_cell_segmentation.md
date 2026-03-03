# XRF 세포 분할(Cell Segmentation)

## 개요

XRF 현미경에서의 세포 분할은 다원소 형광 맵에서 개별 생물학적 세포를 식별하고 경계를 설정하는 작업입니다. 이는 세포 수준 분석을 가능하게 하는 핵심 전처리 단계로, 세포별 원소 정량화 및 분류를 수행할 수 있게 합니다.

## ROI-Finder 분할 파이프라인

ROI-Finder 도구(Chowdhury et al., 2022)는 XRF 데이터에서 세포 분할을 위한 고전적 이미지 처리 파이프라인을 구현합니다.

### 파이프라인 단계

```
다원소 XRF 맵
    │
    ├─→ 1. 채널 선택 (고대비 원소 선택)
    │
    ├─→ 2. 전처리 (정규화, 평활화)
    │
    ├─→ 3. Otsu 임계값 (이진: 세포 대 배경)
    │
    ├─→ 4. 형태학적 연산 (정리)
    │
    ├─→ 5. 연결 요소 레이블링 (개별 세포 식별)
    │
    └─→ 6. 면적/형태 필터링 (파편 제거, 조각 병합)
```

### 1단계: 채널 선택

세포-배경 대비가 좋은 원소 채널을 선택합니다:

```python
import numpy as np

# 각 원소 채널의 대비를 평가
def channel_contrast(channel):
    """변동 계수를 사용하여 세포-배경 대비를 추정."""
    return np.std(channel) / (np.mean(channel) + 1e-10)

# 최적 채널 선택
contrasts = {elem: channel_contrast(maps[elem]) for elem in elements}
best_channel = max(contrasts, key=contrasts.get)
# 일반적으로 Zn, Fe 또는 P가 생물학적 세포에 대해 최적의 대비를 제공
```

**일반적인 선택**:
- **Zn**: 대부분의 생물학적 세포에서 강함, 좋은 대비
- **Fe**: 특정 세포 유형(예: 적혈구)에서 높음
- **P**: 세포에 편재(핵산), 보통의 대비
- **복합**: Max(정규화된 채널) 또는 PCA 첫 번째 성분

### 2단계: 전처리

```python
from skimage import filters, exposure

# OpenCV 호환을 위해 [0, 255]로 정규화
channel_norm = exposure.rescale_intensity(channel, out_range=(0, 255)).astype(np.uint8)

# 선택 사항: 노이즈 감소를 위한 가우시안 평활화
channel_smooth = filters.gaussian(channel_norm, sigma=1.0)
```

### 3단계: Otsu 임계값 설정

```python
import cv2

# Otsu 방법: 최적 임계값을 자동으로 결정
threshold_value, binary = cv2.threshold(
    channel_uint8, 0, 255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)
# binary: 세포 위치 255, 배경 위치 0
```

**Otsu 작동 원리**:
- 이봉(Bimodal) 강도 히스토그램(세포 + 배경)을 가정
- 클래스 내 분산을 최소화하는 임계값을 찾음
- 클래스 간 분산을 최대화하는 것과 동등
- 완전 자동 (매개변수 조정 불필요)

**한계**: 히스토그램이 이봉이 아닌 경우 실패 (저대비, 다수의 세포 유형)

### 4단계: 형태학적 연산(Morphological Operations)

```python
# 구조 요소 정의
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# 열기(Opening): 작은 노이즈 제거 (침식 → 팽창)
cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

# 닫기(Closing): 작은 구멍 채우기 (팽창 → 침식)
cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

# 선택 사항: 세포 경계를 약간 확장하기 위한 팽창
dilated = cv2.dilate(cleaned, kernel, iterations=1)
```

**형태학적 연산 설명**:
- **침식(Erosion)**: 전경 축소 (얇은 돌출부, 노이즈 제거)
- **팽창(Dilation)**: 전경 확장 (작은 구멍 채우기, 조각 연결)
- **열기(Opening)** (침식 → 팽창): 작은 밝은 노이즈 제거
- **닫기(Closing)** (팽창 → 침식): 작은 어두운 구멍 채우기

### 5단계: 연결 요소 레이블링(Connected Component Labeling)

```python
from skimage import measure

# 연결된 영역 레이블링
labels = measure.label(cleaned)
# labels: 0 = 배경, 1 = cell_1, 2 = cell_2, ...

regions = measure.regionprops(labels)
print(f"{len(regions)}개의 연결 요소 발견")
```

### 6단계: 면적/형태 필터링

```python
# 면적으로 필터링 (파편 및 과대 객체 제거)
min_area = 50     # 픽셀 (예상 세포 크기에 따라 조정)
max_area = 5000   # 픽셀

filtered_labels = np.zeros_like(labels)
cell_id = 1
for region in regions:
    if min_area < region.area < max_area:
        # 선택 사항: 형태로 필터링 (이심률, 밀실도)
        if region.eccentricity < 0.95 and region.solidity > 0.5:
            filtered_labels[labels == region.label] = cell_id
            cell_id += 1

print(f"필터링 후 {cell_id - 1}개 세포 유지")
```

## 전체 파이프라인 코드

```python
import numpy as np
import cv2
from skimage import measure, exposure, filters

def segment_cells_xrf(elemental_maps, channel='Zn',
                       min_area=50, max_area=5000,
                       morph_kernel_size=5, gaussian_sigma=1.0):
    """
    ROI-Finder 스타일 파이프라인을 사용하여 XRF 원소 맵에서 세포 분할.

    매개변수
    ----------
    elemental_maps : dict
        {원소_이름: 2D numpy 배열}
    channel : str
        분할에 사용할 원소
    min_area, max_area : int
        픽셀 단위 세포 면적 범위
    morph_kernel_size : int
        형태학적 구조 요소의 크기
    gaussian_sigma : float
        가우시안 평활화 시그마

    반환값
    -------
    labels : 2D numpy 배열
        레이블된 세포 마스크 (0 = 배경)
    properties : list
        각 세포의 영역 속성
    """
    # 1. 채널 선택 및 전처리
    img = elemental_maps[channel].copy()
    img = filters.gaussian(img, sigma=gaussian_sigma)
    img_uint8 = exposure.rescale_intensity(img, out_range=(0, 255)).astype(np.uint8)

    # 2. Otsu 임계값
    _, binary = cv2.threshold(img_uint8, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. 형태학적 정리
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                       (morph_kernel_size, morph_kernel_size))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    # 4. 레이블링 및 필터링
    all_labels = measure.label(cleaned)
    regions = measure.regionprops(all_labels)

    filtered = np.zeros_like(all_labels)
    cell_id = 1
    kept_regions = []
    for r in regions:
        if min_area < r.area < max_area:
            filtered[all_labels == r.label] = cell_id
            kept_regions.append(r)
            cell_id += 1

    return filtered, kept_regions
```

## 고전적 파이프라인의 한계

### 1. 겹치는/접촉하는 세포
- 연결 요소 레이블링이 접촉하는 세포를 하나의 영역으로 병합
- **완화**: 거리 변환에 대한 워터셰드 분할
```python
from scipy import ndimage

# 접촉하는 세포를 분리하기 위한 거리 변환 → 워터셰드
dist = ndimage.distance_transform_edt(cleaned)
local_max = measure.label(dist > 0.5 * dist.max())
labels = measure.watershed(-dist, local_max, mask=cleaned)
```

### 2. 가변적 세포 밝기
- Otsu는 이봉 분포를 가정 — 여러 세포 유형에서 실패
- **완화**: 적응적 임계값 또는 다중 Otsu
```python
# 적응적 임계값
adaptive = cv2.adaptiveThreshold(img_uint8, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 51, -5)
```

### 3. 낮은 SNR 채널
- 미량 농도의 원소는 신호 대 잡음비가 낮을 수 있음
- 저 SNR 채널에서의 분할은 노이즈가 많은 경계를 생성
- **완화**: 고 SNR 채널로 분할 후 모든 채널에 마스크 적용

### 4. 비세포 시료
- 파이프라인이 평평한 지지대 위의 격리된 세포용으로 설계됨
- 조직 단면, 바이오필름, 토양 입자에 대해 실패
- 비세포 대상에는 다른 접근 방식이 필요

## 고급 대안

| 방법 | 강점 | 한계 |
|--------|-----------|-------------|
| **Cellpose** | 사전 학습됨, 다양한 세포 형태 처리 | XRF 데이터에 대한 미세 조정 필요 |
| **StarDist** | 빠름, 볼록 세포에 정확 | 별 볼록(Star-convex) 형태 가정 |
| **Mask R-CNN** | 인스턴스 분할, 바운딩 박스 | 더 많은 학습 데이터 필요 |
| **SAM** | 제로샷, 프롬프트 기반 | XRF 대비에 최적화되지 않음 |
| **워터셰드(Watershed)** | 접촉하는 세포 분리 | 과분할 위험 |

## 평가 지표

```python
from skimage.metrics import variation_of_information

# 세포별 Jaccard 지수 (IoU)
def cell_iou(pred_mask, gt_mask):
    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()
    return intersection / (union + 1e-10)

# 모든 세포에 대한 평균 IoU
# 탐지율: IoU > 0.5 매칭이 있는 정답 세포의 비율
# 거짓 양성률: 정답 매칭이 없는 예측 세포의 비율
```
