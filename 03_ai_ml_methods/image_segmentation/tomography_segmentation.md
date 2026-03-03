# 토모그래피 분할(Tomography Segmentation)

## 개요

재구성된 토모그래피 볼륨의 분할은 3D 데이터 내에서 서로 다른 상(Phase), 특징 또는 구조를 식별합니다. 이는 기공도(Porosity) 측정, 입자 크기 분포, 형태학적 특성화 등 정량적 분석에 필수적입니다.

## 일반적인 분할 대상

| 대상 | 응용 | 과제 |
|--------|-------------|-----------|
| **기공(Pores)** | 토양 기공도, 암석 투과성 | 해상도 한계 부근의 작은 기공 |
| **입자(Grains/Particles)** | 토양 응집체 구조 | 접촉하는 입자 |
| **광물 상(Mineral Phases)** | 지구화학, 암석학 | 유사한 감쇠 계수 |
| **생물 조직** | 뿌리 해부학, 바이오필름 | 저대비, 방사선 손상 |
| **균열/파쇄(Cracks/Fractures)** | 지반역학 | 얇은 특징, 부분 볼륨 효과 |
| **유체/기체** | 다상 유동 | 동적, 저대비 |

## 전통적 방법

### 전역 임계값 설정(Global Thresholding) (Otsu)

```python
from skimage.filters import threshold_otsu

# 간단한 이진 분할
thresh = threshold_otsu(volume)
binary = volume > thresh
# binary: True = 고밀도 상, False = 저밀도/기공
```

적합한 용도: 고대비, 2상 시스템 (예: 기공 대 고체)

### 다중 Otsu (다상)

```python
from skimage.filters import threshold_multiotsu

# 3개 상으로 분할 (예: 기공, 유기물, 광물)
thresholds = threshold_multiotsu(volume, classes=3)
regions = np.digitize(volume, bins=thresholds)
# regions: 각 복셀에 대해 0, 1 또는 2
```

### 워터셰드 분할(Watershed Segmentation)

접촉하는 객체(입자, 파티클) 분리용:

```python
from scipy import ndimage
from skimage import morphology, segmentation

# 1. 이진 임계값
binary = volume > threshold_otsu(volume)

# 2. 거리 변환
distance = ndimage.distance_transform_edt(binary)

# 3. 국소 최대값 찾기 (시드)
local_max = morphology.local_maxima(distance)
markers = measure.label(local_max)

# 4. 워터셰드
labels = segmentation.watershed(-distance, markers, mask=binary)
```

### 랜덤 워커(Random Walker)

그래프 기반 반지도(Semi-supervised) 분할:

```python
from skimage.segmentation import random_walker

# 일부 복셀에 시드 레이블 제공
labels = np.zeros_like(volume, dtype=int)
labels[volume < low_threshold] = 1    # 기공
labels[volume > high_threshold] = 2   # 고체

# 랜덤 워커가 불확실한 영역을 채움
segmented = random_walker(volume, labels, beta=100)
```

### 그래프 컷(Graph Cut) (최대 흐름, Max-Flow)

```python
import maxflow

# 데이터 항 + 평활성 항으로 그래프 정의
# 데이터 항: 복셀이 각 클래스에 속할 우도
# 평활성: 인접 복셀이 다른 레이블을 가질 때의 패널티
# 최대 흐름/최소 컷 알고리즘을 통한 최적 분할
```

## 딥러닝 방법

### 3D U-Net

볼류메트릭(Volumetric) 분할을 위한 표준 아키텍처 ([unet_variants.md](unet_variants.md) 참조).

**패치 기반 전략**:
```
전체 볼륨 (2048³) → 패치 추출 (128³) → 예측 → 스티칭
```

### V-Net

잔차 연결(Residual Connections)과 Dice 손실을 가진 3D U-Net의 변형:
- 볼류메트릭 의료 이미지 분할을 위해 특별히 설계
- 잔차 블록이 심층 네트워크에서 그래디언트 흐름을 개선
- Dice 손실이 클래스 불균형을 더 잘 처리

### DLSIA (과학적 이미지 분석을 위한 딥러닝, Deep Learning for Scientific Image Analysis)

LBNL에서 방사광 데이터를 위해 개발한 프레임워크:

- **혼합 스케일 밀집(Mixed-Scale Dense, MSD) 네트워크**: 풀링 없이 다중 스케일 특징 결합
- **조정 가능한 U-Net(Tunable U-Nets)**: 매개변수화된 아키텍처 탐색
- **과학적 초점**: 의료가 아닌 과학적 데이터 특성을 위해 설계

### 자기 지도 접근법(Self-Supervised Approaches)

레이블 데이터 부족 문제를 해결:

1. **대조 학습(Contrastive Learning)**: 증강된 뷰를 비교하여 특징 학습
2. **마스크 오토인코더(Masked Autoencoder)**: 볼륨의 마스킹된 영역을 예측
3. **유사 레이블링(Pseudo-labeling)**: 전통적 방법으로 초기 레이블 생성 후 반복적으로 정제

## 방사광 토모그래피 특유의 과제

### 1. 링 아티팩트(Ring Artifacts)

전처리 후 잔여 링 아티팩트가 분할 알고리즘을 오도할 수 있음:
- 거짓 원형 경계 생성
- 임계값 기반 방법에 가장 심각한 영향
- 학습 데이터에 존재하면 DL 방법이 링을 무시하도록 학습 가능

### 2. 부분 볼륨 효과(Partial Volume Effects)

물질 계면에서 복셀이 여러 상의 혼합을 포함:
```
실제 경계:     상 A | 상 B
복셀 값:      ... A  [A+B 혼합]  B ...
```
- 경계에서 중간 회색값 생성
- 기공/입자 경계 정확도에 영향
- 완화: 서브복셀 분할, 부분 볼륨 추정

### 3. 빔 경화(Beam Hardening) (다색 광원)

고밀도 물질이 저에너지 X선을 우선적으로 흡수:
- 커핑 아티팩트(Cupping Artifact): 가장자리가 중심보다 밀도가 높게 나타남
- 재구성된 볼륨에 거짓 그래디언트 생성
- 분할 전에 사전 보정이 필요

### 4. 대규모 볼륨 크기

| 볼륨 | 복셀 수 | 크기 (32비트) | GPU 적합? |
|--------|--------|---------------|----------|
| 512³ | 1.34억 | 0.5 GB | 예 |
| 1024³ | 10.7억 | 4 GB | 겨우 |
| 2048³ | 85.9억 | 32 GB | 아니오 |
| 4096³ | 687억 | 256 GB | 아니오 |

**전략**:
- 오버랩 스티칭을 사용한 패치 기반
- 다운샘플링된 조잡한 패스 → 전체 해상도 정제
- 다중 GPU에 걸친 분산 추론
- 2D 슬라이스별 처리 후 3D 일관성 후처리

## 평가 지표

| 지표 | 수식 | 적합한 용도 |
|--------|---------|----------|
| **Dice 계수** | 2|A∩B| / (|A|+|B|) | 전체 오버랩 |
| **IoU (Jaccard)** | |A∩B| / |A∪B| | 클래스별 정확도 |
| **표면 거리(Surface Distance)** | 경계 간 평균 거리 | 경계 정확도 |
| **볼륨 분율(Volume Fraction)** | Volume_phase / Volume_total | 기공도 측정 |
| **오일러 수(Euler Number)** | 위상적 연결성 | 기공 네트워크 토폴로지 |

## 실용 워크플로우

```
재구성된 3D 볼륨
    │
    ├─→ 전처리
    │       ├── 크롭 (재구성 가장자리 제거)
    │       ├── 링 아티팩트 억제
    │       ├── 노이즈 감소 (3D 중간값 또는 NLM 필터)
    │       └── 강도 정규화
    │
    ├─→ 분할
    │       ├── 빠른: 다중 Otsu 임계값
    │       ├── 표준: 개별 입자를 위한 워터셰드
    │       └── 고급: 3D U-Net (학습 데이터가 있는 경우)
    │
    ├─→ 후처리
    │       ├── 형태학적 정리 (열기/닫기)
    │       ├── 연결 요소 필터링 (작은 노이즈 제거)
    │       ├── 구멍 채우기
    │       └── 수동 보정 (필요 시)
    │
    └─→ 정량적 분석
            ├── 기공도 (기공 상의 볼륨 분율)
            ├── 기공 크기 분포 (등가 구 직경)
            ├── 연결성 (오일러 수, 삼투)
            ├── 입자 크기 분포
            └── 표면적 (마칭 큐브, Marching Cubes)
```
