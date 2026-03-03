# ROI-Finder

## 개요

**ROI-Finder**는 방사광 빔라인에서의 X선 형광 (XRF) 현미경 실험에서 ML 기반 관심 영역 (ROI) 선택을 위한 오픈소스 Python 도구입니다.

| | |
|---|---|
| **저장소** | [https://github.com/arshadzahangirchowdhury/ROI-Finder](https://github.com/arshadzahangirchowdhury/ROI-Finder) |
| **저자** | Arshad Zahangir Chowdhury 등 |
| **논문** | J. Synchrotron Rad. 29 (2022), DOI: 10.1107/S1600577522008876 |
| **언어** | Python 3.x |
| **라이선스** | 명시적으로 기재되지 않음 (저장소 확인 필요) |
| **최근 활동** | 최신 커밋은 GitHub 참조 |

## 목적

ROI-Finder는 XRF 현미경의 핵심 과제를 해결합니다: 빔 타임이 제한된 상황에서 상세한 고해상도 스캐닝을 위해 과학적으로 가장 흥미로운 세포 또는 영역을 효율적으로 선택하는 방법입니다.

### 대상 사용자
- 방사광 XRF 빔라인 과학자
- XRF 현미경을 사용하는 환경 및 생물학 연구자
- 다중 원소 공간 데이터에서 영역 우선순위를 정해야 하는 모든 사람

## 핵심 기능

1. **세포 세그멘테이션**: XRF 원소 맵에서 개별 세포를 자동으로 식별
2. **특징 추출**: PCA를 사용하여 다중 원소 데이터를 유익한 특징 공간으로 축소
3. **클러스터링**: 퍼지 k-평균을 사용하여 원소 조성별로 세포 그룹화
4. **추천**: 상세 스캐닝을 위한 세포 순위 지정 및 추천
5. **주석**: 세포를 보기, 선택 및 주석 달기를 위한 대화형 GUI

## 설치

```bash
# Clone repository
git clone https://github.com/arshadzahangirchowdhury/ROI-Finder.git
cd ROI-Finder

# Create conda environment (recommended)
conda create -n roifinder python=3.8
conda activate roifinder

# Install dependencies
pip install -r requirements.txt
```

## 의존성

| 패키지 | 용도 | 버전 |
|---------|---------|---------|
| numpy | 배열 연산 | ≥1.20 |
| scipy | 과학 컴퓨팅 | ≥1.6 |
| scikit-learn | PCA, 전처리 | ≥0.24 |
| scikit-fuzzy | 퍼지 k-평균 클러스터링 | ≥0.4 |
| scikit-image | 이미지 처리, 형태학 | ≥0.18 |
| opencv-python | 임계값 처리, 형태학적 연산 | ≥4.5 |
| h5py | HDF5 데이터 로딩 | ≥3.0 |
| matplotlib | 시각화 | ≥3.3 |
| tkinter | GUI (표준 라이브러리) | — |

## 관련 파일

| 파일 | 내용 |
|------|---------|
| [reverse_engineering.md](reverse_engineering.md) | 코드 구조 분석, 알고리즘 흐름 |
| [pros_cons.md](pros_cons.md) | 강점, 한계, 개선 기회 |
| [reproduction_guide.md](reproduction_guide.md) | 결과 재현을 위한 단계별 가이드 |
| [notebooks/](notebooks/) | 실습 탐구를 위한 Jupyter 노트북 |
