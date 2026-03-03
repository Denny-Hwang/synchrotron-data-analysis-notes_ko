# XRF 현미경을 위한 AI/ML 방법

## 개요

XRF 현미경은 머신러닝 분석에 적합한 풍부한 다중 원소 공간 데이터셋을 생성합니다.
주요 ML 응용에는 자동 ROI 선택, 세포/입자 분할, 원소 연관의 비지도 클러스터링,
해상도 향상이 포함됩니다.

## ML 문제 분류

| 문제 | 유형 | 입력 | 출력 |
|------|------|------|------|
| ROI 선택 | 추천 | 다중 원소 맵 | 우선순위 ROI 목록 |
| 세포 분할 | 인스턴스 분할 | 원소 맵 | 세포 경계 + 레이블 |
| 클러스터링 | 비지도 | 다중 원소 픽셀 벡터 | 클러스터 할당 |
| 스펙트럼 피팅 | 회귀 | 원시 스펙트럼 | 원소 농도 |
| 해상도 향상 | 이미지-이미지 | 저해상도 맵 | 고해상도 맵 |
| 이상 검출 | 분류 | 픽셀 스펙트럼 | 정상/비정상 |

## ROI-Finder

**ROI-Finder**는 빔타임 동안 자율 실험 조향을 위해 APS에서 개발된 XRF 현미경의
주력 ML 도구입니다.

### 워크플로우
```
저해상도 XRF 서베이 스캔 (넓은 영역)
    │
    ├─→ 세포 분할
    │       오쓰 임계값 → 형태학적 연산 → 연결 성분
    │
    ├─→ 특징 추출 (세포별)
    │       다중 원소 벡터에 대한 PCA → 축소된 특징 공간
    │
    ├─→ 클러스터링
    │       퍼지 k-means → 연성 멤버십 할당
    │
    └─→ ROI 추천
            다양성/흥미도에 따라 세포 순위화 → 상세 스캐닝 제안
```

### 핵심 혁신
- 비지도: 레이블 학습 데이터 불필요
- 빔타임 중 작동: 실험자를 가장 흥미로운 영역으로 안내
- 대화형: 주석 및 파라미터 조정을 위한 GUI

**참고문헌**: Chowdhury et al., J. Synchrotron Rad. 29 (2022), DOI: 10.1107/S1600577522008876

*상세 분석 참조: [05_tools_and_code/roi_finder/](../../05_tools_and_code/roi_finder/)*

## 세포 분할 방법

### 이진 임계값 파이프라인 (ROI-Finder)

```python
import cv2
import numpy as np
from skimage import morphology, measure

# 1. 고대비 원소 채널 선택 (예: Zn)
channel = elemental_maps['Zn']

# 2. 오쓰 임계값
threshold = cv2.threshold(channel_uint8, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# 3. 형태학적 연산
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
cleaned = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)   # 노이즈 제거
cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)     # 구멍 채움

# 4. 연결 성분 레이블링
labels = measure.label(cleaned)

# 5. 면적/형태로 필터링
regions = measure.regionprops(labels)
filtered = [r for r in regions if min_area < r.area < max_area]
```

### 한계
- 겹치는/접촉하는 세포에서 실패 (워터셰드 또는 인스턴스 분할 필요)
- 채널 선택과 SNR에 민감
- 가변적 세포 밝기를 처리할 수 없음

### 고급 대안
- **Cellpose**: 세포용 사전 학습된 인스턴스 분할 (범용 모델)
- **Mask R-CNN**: 바운딩 박스가 있는 인스턴스 분할
- **StarDist**: 볼록 세포를 위한 별모양 볼록 다각형 검출
- **U-Net**: 의미적 분할 (세포 대 배경)

## 비지도 클러스터링

### GMM (가우시안 혼합 모델)

Ward et al. (2013)은 말라리아 감염 적혈구의 XRF 데이터에 GMM을 적용했습니다:

```python
from sklearn.mixture import GaussianMixture

# 픽셀별 다중 원소 특징 벡터 준비
# shape: (Npixels, Nelements)
X = np.column_stack([maps[e].flatten() for e in selected_elements])

# GMM 피팅
gmm = GaussianMixture(n_components=k, covariance_type='full')
gmm.fit(X)

# 연성 클러스터 할당
probabilities = gmm.predict_proba(X)  # shape: (Npixels, k)
labels = gmm.predict(X)               # shape: (Npixels,)
```

**장점**:
- 연성 클러스터링 (확률적 멤버십)
- 타원형 클러스터 모델링 (원소 상관관계 포착)
- 최적 k 선택을 위한 BIC/AIC

### 퍼지 K-Means (ROI-Finder)

```python
import skfuzzy as fuzz

# 퍼지 c-means 클러스터링
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
    X.T, c=k, m=2, error=0.005, maxiter=1000
)
# u: 멤버십 행렬, shape: (k, Npixels)
# cntr: 클러스터 중심, shape: (k, Nelements)
```

**장점**:
- 연성 멤버십 (각 픽셀이 여러 클러스터에 부분적으로 속함)
- 세포 유형 간 전이 영역을 더 잘 처리
- 품질 평가를 위한 퍼지 분할 계수 (FPC)

### 기타 클러스터링 접근법
- **HDBSCAN**: 밀도 기반, 임의 형태의 클러스터 찾기, 노이즈 처리
- **스펙트럼 클러스터링**: 그래프 기반, 비선형 관계 포착
- **자기조직화맵 (SOM)**: 위상적 차원 축소 + 클러스터링

## 특징 추출

### PCA 기반 (ROI-Finder 접근법)
```
다중 원소 맵 (Ny, Nx, Nelements)
    → (Npixels, Nelements)로 재형성
    → 표준화
    → PCA → 상위 k 성분
    → 세포별 평균 특징 (분할된 영역 내 집계)
```

### 딥러닝 대안
- **오토인코더**: 다중 원소 스펙트럼의 압축 표현 학습
- **대조 학습**: 증강된 스펙트럼 데이터로부터의 자기지도 특징
- **VAE**: 스펙트럼 분포의 생성적 모델링을 위한 변분 오토인코더

## 해상도 향상

### XRF용 딥 잔차 네트워크

**참고문헌**: npj Computational Materials (2023), DOI: 10.1038/s41524-023-00995-9

빔 프로브 크기를 넘어서는 XRF 공간 해상도 향상:

```
저해상도 XRF 맵 → 딥 잔차 네트워크 → 향상된 해상도 맵
```

**방법**:
- 쌍을 이룬 저해상도(큰 스텝)/고해상도(미세 스텝) 스캔으로 학습
- 잔차 학습: 네트워크가 차이(고해상도 - 업샘플된 저해상도)를 예측
- 프로브 프로파일을 효과적으로 디컨볼루션

**결과**: 2-4배 유효 해상도 향상 입증

## 현재 한계

1. **분할**: 표준 방법은 겹치는 세포와 가변 대비에 어려움
2. **특징 공학**: PCA는 비선형 원소 연관을 놓칠 수 있음
3. **학습 데이터**: 지도 ML을 위한 레이블된 XRF 데이터셋이 거의 없음
4. **3D XRF**: ML 방법이 대부분 2D에 제한; 3D 토모그래피 XRF 개발 필요
5. **정량화 불확실성**: ML 기반 스펙트럼 피팅은 엄격한 불확실성 추정이 부족

## 개선 기회

1. **인스턴스 분할**: XRF 원소 맵에 적응된 Cellpose/StarDist
2. **자기지도 사전학습**: 레이블 없는 XRF 데이터에서 특징 학습
3. **다중모달 융합**: XRF + 타이코그래피 공동 분석
4. **능동 학습**: ML이 최대 모델 개선을 위해 어떤 세포에 레이블을 달지 제안
5. **실시간 스트리밍**: 초 이하 의사결정의 ML 안내 스캐닝
6. **물리 정보 ML**: XRF 물리(자기흡수, 매트릭스 효과)를 네트워크에 통합
