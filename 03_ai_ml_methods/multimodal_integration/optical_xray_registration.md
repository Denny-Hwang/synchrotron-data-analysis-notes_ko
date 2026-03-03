# 광학-X선 이미지 정합(Registration)

## 개요

광학 현미경 이미지와 X선 데이터 간의 정합(registration)은 다음을 가능하게 합니다:
1. 광학 이미지를 사용하여 X선 측정 전에 관심 영역(ROI)을 사전 선택
2. 가시광 특징과 원소/구조 X선 데이터를 상관
3. 빔 타임 중 광학적으로 식별된 특정 특징으로 이동

이는 광학 현미경과 XRF 스캐닝의 통합을 계획하고 있는 ROI-Finder의 로드맵과
특히 관련이 있습니다.

## 정합 문제

```
광학 현미경 이미지                 X선 맵 (XRF, ptychography 등)
┌─────────────────────┐           ┌──────────────────────┐
│  높은 해상도          │           │  낮은 해상도           │
│  컬러 (RGB)          │   정합    │  다중 채널             │
│  넓은 시야각(FOV)    │ ═══════════│  좁은 시야각(FOV)     │
│  표면 형태           │           │  벌크 조성             │
│  빔 타임 불필요      │           │  빔 타임 필요          │
└─────────────────────┘           └──────────────────────┘
```

### 과제

| 과제 | 설명 |
|-----------|------------|
| **다른 대비** | 광학: 반사율/흡수. X선: 형광/위상 |
| **해상도 불일치** | 광학: 0.3-1 µm. XRF: 0.05-20 µm |
| **시야각(FOV) 불일치** | 광학: mm-cm. X선: µm-mm |
| **왜곡** | 서로 다른 광학 경로, 시료 장착 변화 |
| **특징 대응** | 동일한 특징이 매우 다르게 보일 수 있음 |

## 정합 방법

### 1. 기준 마커 기반(Fiducial Marker-Based)

```
시료에 알려진 마커(예: 금 격자선) 배치
    │
    ├─→ 광학 이미지에서 마커 식별 → (x₁,y₁), (x₂,y₂), ...
    │
    ├─→ X선 맵에서 마커 식별 → (x₁',y₁'), (x₂',y₂'), ...
    │
    └─→ 아핀 변환 계산:
         [x']   [a b tx] [x]
         [y'] = [c d ty] [y]
         [1 ]   [0 0 1 ] [1]

         풀이: T = argmin Σᵢ ||(x'ᵢ,y'ᵢ) - T(xᵢ,yᵢ)||²
```

**장점**: 신뢰성 높음, 잘 정의된 대응점
**단점**: 마커 필요, 시료 영역을 가릴 수 있음

### 2. 특징 기반 정합(Feature-Based Registration)

```python
import cv2
import numpy as np

# 두 이미지에서 특징 검출
sift = cv2.SIFT_create()
kp1, desc1 = sift.detectAndCompute(optical_image, None)
kp2, desc2 = sift.detectAndCompute(xray_image, None)

# 특징 매칭
bf = cv2.BFMatcher()
matches = bf.knnMatch(desc1, desc2, k=2)

# Lowe의 비율 테스트
good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

# 변환 계산
src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# 변환 적용
registered = cv2.warpPerspective(optical_image, M, xray_image.shape[::-1])
```

**장점**: 마커 불필요, 자동
**단점**: 두 모달리티 모두에서 보이는 공통 특징이 필요 (종종 어려움)

### 3. 상호 정보량 기반(Mutual Information-Based)

서로 다른 대비 메커니즘을 가진 이미지의 경우:

```python
from skimage.registration import phase_cross_correlation
from scipy.optimize import minimize

def mutual_information(image1, image2):
    """두 이미지 간의 상호 정보량을 계산합니다."""
    hist_2d, _, _ = np.histogram2d(
        image1.ravel(), image2.ravel(), bins=50
    )
    # 정규화
    pxy = hist_2d / hist_2d.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)

    # MI = H(X) + H(Y) - H(X,Y)
    hx = -np.sum(px[px > 0] * np.log(px[px > 0]))
    hy = -np.sum(py[py > 0] * np.log(py[py > 0]))
    hxy = -np.sum(pxy[pxy > 0] * np.log(pxy[pxy > 0]))

    return hx + hy - hxy

# 상호 정보량을 최대화하도록 변환 최적화
# (서로 다른 대비 메커니즘을 처리)
```

### 4. 딥러닝 정합(Deep Learning Registration)

```
광학 이미지 ──→ CNN 특징 추출기 ──→ 특징 A ──┐
                                              ├─→ 공간 변환기(Spatial Transformer)
X선 이미지 ───→ CNN 특징 추출기 ──→ 특징 B ──┘     → 변환 파라미터
```

- **VoxelMorph**: 원래 의료 영상 정합용
- **DeepReg**: 범용 딥러닝 정합 프레임워크
- **자기지도(Self-supervised)**: 증강된 단일 모달리티 데이터로 훈련, 교차 모달리티에 적용

## ROI-Finder 통합 로드맵

### 현재 상태
- ROI-Finder는 XRF 데이터에서만 작동
- 광학 이미지는 내비게이션에 수동으로 사용

### 계획된 개선
```
1. 빔 타임 전: 시료의 광학 현미경 촬영
   → 광학적으로 후보 세포/영역 식별
   → 기준 마커 기준의 좌표 저장

2. 빔라인에서: 빠른 개략 XRF 스캔
   → 광학 이미지와 정합
   → 광학 ROI 선택을 XRF 좌표계로 전환

3. 빔 타임 중:
   → 사전 선택된 ROI를 고해상도로 스캔
   → 선택적으로 XRF에서 ROI-Finder 실행하여 선택 정밀화
```

### 이점
- 광학으로 사전 스크리닝하여 빔 타임 절약 (무료이고 빠름)
- 형태학적(광학) 및 원소(XRF) 정보를 결합한 더 나은 ROI 선택
- 여러 실험에 걸쳐 동일 세포 추적 (광학 식별)

## 과제 및 향후 방향

1. **교차 모달 학습(Cross-modal learning)**: 광학과 X선 특징 간의 대응을 이해하는 모델 훈련
2. **다중 스케일 정합**: 큰 해상도 차이(100배 이상) 처리
3. **변형 가능 정합(Deformable registration)**: 광학과 X선 촬영 사이의 시료 변화 보상
4. **실시간**: 빔 타임 중 즉각적인 ROI 전환을 위한 정합
5. **3D**: 광학 표면 이미지와 3D X선 토모그래피 데이터의 정합
