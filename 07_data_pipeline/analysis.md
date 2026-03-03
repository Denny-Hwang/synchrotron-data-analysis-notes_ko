# 분석

## 개요

분석(analysis) 단계에서는 처리된 데이터에 학습된 머신러닝(machine learning) 모델을 적용하고,
사람의 해석을 위한 대화형 시각화(visualization)를 제공하며,
결과가 아카이브에 커밋되기 전에 품질 게이트(quality gate)를 적용합니다.

## ML 추론 파이프라인

추론(inference) 파이프라인은 처리된 볼륨을 받아 예측값 또는 파생 수량을 반환하는
컨테이너화된 서비스로 배포됩니다.

```
Processed Volume (Zarr / HDF5)
    |
    v
Model Registry (MLflow)  -->  Inference Service (Triton)
                                    |
                                    v
                              Predictions (JSON / HDF5)
```

### 모델 레지스트리

모든 프로덕션 모델은 MLflow에서 추적됩니다:

| 항목 | 예시 |
|---|---|
| 모델 이름 | `tomoseg-unet3d-v4` |
| 프레임워크 | PyTorch 2.2 |
| 학습 데이터셋 | `2024Q3-battery-cathode` |
| 검증 지표 | Dice = 0.94, IoU = 0.89 |
| 입력 사양 | float32, 128^3 패치 |

모델은 단계별로 승격됩니다: `Staging` -> `Production` -> `Archived`.
자동화된 파이프라인 실행에는 `Production` 모델만 사용됩니다.

### 추론 모드

| 모드 | 트리거 | 지연 시간 | 용도 |
|---|---|---|---|
| 실시간 | ZMQ 프레임 도착 | < 500 ms | 스캔 중 실시간 분류 |
| 배치 | Globus 전송 완료 | 수 분 | 전체 볼륨 분할(segmentation) |
| 온디맨드 | API를 통한 사용자 요청 | 수 초 | 새 모델로 재분석 |

### 지원되는 모델 유형

- **분할(Segmentation)**: 다상 라벨링을 위한 3D U-Net, nnU-Net
- **분류(Classification)**: 스캔 품질 / 시료 유형을 위한 ResNet-50
- **이상 탐지(Anomaly detection)**: 이상치 프레임 검출을 위한 오토인코더(Autoencoder)
- **초해상도(Super-resolution)**: 저선량 수집 향상을 위한 ESRGAN

## 시각화 도구

### Jupyter Notebooks

JupyterHub은 Eagle 파일시스템에 직접 접근할 수 있는 ALCF Polaris 노드에 배포되어 있습니다.
일반적인 워크플로를 위한 표준 노트북이 제공됩니다:

| 노트북 | 용도 |
|---|---|
| `01_quick_look.ipynb` | 재구성 로드, 직교 슬라이스 플롯 |
| `02_histogram_analysis.ipynb` | 강도 히스토그램, 임계값 선택 |
| `03_3d_rendering.ipynb` | ipyvolume / itkwidgets를 사용한 볼륨 렌더링 |
| `04_comparison.ipynb` | 처리 전후 나란히 비교 |

### Streamlit 대시보드

안내형 분석 워크플로를 위한 대화형 웹 대시보드:

- **스캔 브라우저(Scan Browser)** -- 최근 스캔 탐색, 썸네일 보기, 분석 실행
- **품질 대시보드(Quality Dashboard)** -- 캠페인 내 모든 스캔에 대한 QA 지표 표시
- **파라미터 탐색기(Parameter Explorer)** -- 재구성 / 분할 파라미터 조정
- **보고서 생성기(Report Generator)** -- 각 데이터셋에 대한 PDF 요약 보고서 생성

### Napari

Napari는 Dask 기반 지연 로딩(lazy loading)을 통한 아웃오브코어(out-of-core) 볼륨,
레이어 기반 오버레이, 분할 라벨 수정을 위한 수동 주석 도구와 함께
GPU 가속 다차원 이미지 뷰어를 제공합니다.

```python
import napari
import dask.array as da

volume = da.from_zarr("/eagle/eBERlight/recon/scan_0042.zarr")
labels = da.from_zarr("/eagle/eBERlight/seg/scan_0042_labels.zarr")

viewer = napari.Viewer()
viewer.add_image(volume, name="reconstruction", contrast_limits=[0, 0.005])
viewer.add_labels(labels, name="segmentation", opacity=0.4)
napari.run()
```

## 결과 검증 프로세스

### 자동화된 품질 게이트

처리된 모든 데이터셋은 자동화된 품질 검사를 거칩니다:

| 검사 항목 | 기준 | 실패 시 조치 |
|---|---|---|
| 재구성 완전성 | 모든 슬라이스 존재, NaN 없음 | 거부, 재대기열 |
| SNR 임계값 | ROI 내 SNR > 15 dB | 검토 대상 표시 |
| 분할 커버리지 | 볼륨의 95% 이상 분류됨 | 검토 대상 표시 |
| 링 아티팩트(ring artifact) 점수 | FFT 링 지표 < 0.02 | 더 강한 필터로 재실행 |
| 모델 신뢰도 | 평균 소프트맥스 > 0.85 | 저신뢰도 영역 표시 |

### 사람에 의한 검토 워크플로

자동화된 검사에서 표시된 데이터셋은 사람의 검토 대기열에 들어갑니다:

1. **검토자**가 검토 링크를 통해 Napari 또는 Jupyter에서 데이터셋을 엽니다.
2. **주석(annotation)**으로 영역을 수락, 수정, 또는 거부로 표시합니다.
3. **결정**이 기록됩니다: `accept`, `reprocess`, 또는 `discard`.
4. 수락된 데이터셋은 아카이브를 위해 [storage.md](storage.md)로 진행됩니다.
5. 수정된 라벨은 모델 개선을 위해 학습 파이프라인에 피드백됩니다.

### 출처 추적(Provenance Tracking)

모든 분석 작업은 NeXus 메타데이터에 내장된 출처 기록(provenance record)에 로그됩니다:

```json
{
  "scan_id": "scan_0042",
  "pipeline_version": "2.4.1",
  "model": "tomoseg-unet3d-v4",
  "model_hash": "sha256:a3f8c1...",
  "qa_checks": {"snr_db": 22.4, "seg_coverage": 0.987, "ring_score": 0.008},
  "reviewer": "jsmith",
  "decision": "accept",
  "timestamp": "2025-11-03T14:22:00Z"
}
```

## 통합 지점

- **업스트림**: [processing.md](processing.md)에서 처리된 볼륨을 수신
- **다운스트림**: 검증된 결과가 [storage.md](storage.md)로 진행
- **피드백 루프**: 수정된 라벨이 모델 재학습을 위해 `06_ml_ai/`로 반환
