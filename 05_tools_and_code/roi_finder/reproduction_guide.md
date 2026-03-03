# ROI-Finder: 재현 가이드

## 사전 요구 사항

- Python 3.8+ (호환성을 위해 3.8 권장)
- Conda 또는 pip 패키지 관리자
- ~2 GB 디스크 공간 (코드 + 샘플 데이터)
- GPU 불필요

## 1단계: 환경 설정

```bash
# Option A: Conda (recommended)
conda create -n roifinder python=3.8
conda activate roifinder

# Option B: venv
python -m venv roifinder-env
source roifinder-env/bin/activate  # Linux/Mac
```

## 2단계: 클론 및 설치

```bash
# Clone the repository
git clone https://github.com/arshadzahangirchowdhury/ROI-Finder.git
cd ROI-Finder

# Install dependencies
pip install -r requirements.txt

# Or install as package (if setup.py available)
pip install -e .
```

## 3단계: 샘플 데이터 확보

저장소에서 샘플 데이터를 확인합니다:

```bash
# Sample data may be in the repository
ls data/

# Or download from linked sources (check README)
# Typical sample: MAPS-processed HDF5 file with multi-element XRF maps
```

샘플 데이터가 포함되어 있지 않은 경우, 빔라인 실험의 MAPS 형식 HDF5 파일을 사용하거나 논문 저자에게 샘플 데이터를 요청할 수 있습니다.

## 4단계: 파이프라인 실행

### 자동화된 파이프라인

```bash
# Check for example scripts
python examples/run_pipeline.py --input data/sample_xrf.h5
```

### 수동 단계별 실행

```python
# In Python or Jupyter notebook:

# 1. Load data
from roifinder.data_loader import load_xrf_data

data = load_xrf_data('data/sample_xrf.h5')
print(f"Elements: {list(data.keys())}")
print(f"Map shape: {list(data.values())[0].shape}")

# 2. Segment cells
from roifinder.segmenter import segment_cells

labels, props = segment_cells(data['Zn'], min_area=50, max_area=5000)
print(f"Found {labels.max()} cells")

# 3. Extract features and cluster
from roifinder.recommender import extract_features, cluster_cells

features, cell_ids = extract_features(data, labels, elements=['P','S','K','Ca','Fe','Zn'])
cluster_labels, membership, pca_scores, centers = cluster_cells(features, n_clusters=5)

# 4. Get recommendations
from roifinder.recommender import recommend_rois

recommended = recommend_rois(membership, cluster_labels, n_per_cluster=3)
print(f"Recommended {len(recommended)} cells for detailed scanning")

# 5. Visualize
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].imshow(data['Zn'], cmap='viridis')
axes[0].set_title('Zn Map')
axes[1].imshow(labels, cmap='nipy_spectral')
axes[1].set_title('Segmented Cells')
scatter = axes[2].scatter(pca_scores[:, 0], pca_scores[:, 1], c=cluster_labels, cmap='tab10')
axes[2].set_title('PCA + Clusters')
plt.colorbar(scatter, ax=axes[2])
plt.tight_layout()
plt.savefig('roi_finder_results.png', dpi=150)
```

## 5단계: 대화형 GUI 실행

```bash
# If GUI module is available
python -m roifinder.annotator --input data/sample_xrf.h5
```

## 예상 결과

### 세그멘테이션
- 높은 대비 원소 채널 (Zn, Fe, P)에서 명확한 세포 경계
- 맵당 일반적으로 50-500개 세포 (시료 및 스캔 영역에 따라 다름)
- 일부 과잉/부족 세그멘테이션 예상 (파라미터 조정 필요)

### 클러스터링
- 생물학적 시료에서 일반적으로 3-7개 클러스터가 의미 있음
- FPC (퍼지 분할 계수) > 0.5이면 합리적인 클러스터링을 나타냄
- PCA는 일반적으로 상위 3개 구성 요소에서 >80% 분산을 포착

### 추천
- 클러스터 전반에 걸친 다양한 선택
- 이상치 세포 (비정상적 조성)가 높은 순위
- 결과가 도메인 전문가의 직관과 일치해야 함

## 문제 해결

| 문제 | 해결 방법 |
|-------|----------|
| HDF5 경로 오류 | MAPS 출력 형식 확인; MAPS 버전에 따라 경로가 다를 수 있음 |
| 세포가 발견되지 않음 | min_area, max_area 조정 또는 다른 채널 시도 |
| 클러스터가 너무 많음 | n_clusters 줄이기; 최적 k를 위해 FPC 확인 |
| GUI가 실행되지 않음 | tkinter 설치 확인: `sudo apt install python3-tk` |
| 메모리 오류 | 큰 맵을 서브샘플링하거나 영역별로 처리 |

## 논문 결과 재현

Chowdhury 등 (2022)의 특정 결과를 재현하려면:

1. 논문에서 참조된 정확한 데이터셋을 사용합니다 (필요한 경우 저자에게 요청)
2. 파라미터 일치: 채널 선택, 형태학적 커널 크기, PCA 구성 요소, k 값
3. 세그멘테이션 세포 수 및 클러스터 분포를 비교합니다
4. PCA 설명 분산 비율이 보고된 값과 일치하는지 확인합니다
5. 추천된 ROI가 논문의 그림과 일치하는지 확인합니다
