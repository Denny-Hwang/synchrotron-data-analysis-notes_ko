# 데이터 처리 파이프라인

## 개요

처리(processing) 단계는 원시 검출기 프레임을 과학적으로 의미 있는 재구성(reconstruction),
노이즈 제거된 볼륨, 분할된 구조로 변환합니다. 각 단계는 가능한 경우 GPU 가속을 사용하며,
ALCF 리소스(Polaris, Aurora)에서 거의 실시간 처리를 목표로 합니다.

## 파이프라인 단계

```
Raw Frames --> Preprocessing --> Reconstruction --> Denoising --> Segmentation --> Quantification
```

## 1단계: 전처리(Preprocessing)

다크 필드(dark-field) 보정은 전자 노이즈를 차감하고, 플랫 필드(flat-field) 정규화는
빔 프로파일 및 이득 변동을 제거합니다:

```
normalized = (raw - dark) / (flat - dark)
```

추가 전처리 작업:

| 작업 | 목적 | 구현 |
|---|---|---|
| 징거(Zingers) 제거 | 우주선(cosmic ray) 스파이크 제거 | 투영 스택에 대한 중앙값 필터 |
| 링 아티팩트(Ring artifact) 억제 | 줄무늬 아티팩트 보정 | 푸리에-웨이블릿(Fourier-Wavelet) 방법 |
| 위상 복원(Phase retrieval) | 위상 대비(phase contrast) 추출 | Paganin 단일 거리 알고리즘 |
| 회전 중심(Rotation center) 찾기 | 회전축 정렬 | 푸리에 기반 교차상관(cross-correlation) |
| 로그 변환(Log transform) | 투과율을 흡수율로 변환 | `-log(normalized)` |

```python
import tomopy
proj, flat, dark, theta = dxchange.read_aps_32id(filename)
proj = tomopy.normalize(proj, flat, dark)
proj = tomopy.minus_log(proj)
proj = tomopy.remove_stripe_fw(proj, level=7, wname='sym16')
rot_center = tomopy.find_center_vo(proj)
```

## 2단계: 재구성(TomocuPy)

TomocuPy는 토모그래피 알고리즘의 CuPy 기반 GPU 구현을 제공합니다:

| 알고리즘 | 용도 | 속도 (4K x 4K x 2K) |
|---|---|---|
| FBP (Filtered Back-Projection) | 표준 재구성 | ~8 초 (A100) |
| Gridrec | 푸리에 기반 그리딩 | ~12 초 (A100) |
| SIRT (반복법) | 노이즈가 많은 / 제한 각도 데이터 | ~2 분 (20 반복) |
| CGLS (반복법) | 정규화된 재구성 | ~3 분 (30 반복) |

### 다중 GPU 전략

워크로드는 슬라이스 단위로 GPU에 분배됩니다. 각 GPU는 볼륨의 N/4 슬라이스를
병렬로 처리하며, 결과는 최종 출력으로 연결(concatenate)됩니다.

```yaml
reconstruction:
  algorithm: "fourierrec"
  filter: "shepp"
  gpu_devices: [0, 1, 2, 3]
  chunk_size: 64
  dtype: "float32"
  output_format: "zarr"
```

## 3단계: 노이즈 제거(DNN)

심층 신경망(deep neural network) 모델이 재구성된 볼륨에서 잔여 노이즈를 제거합니다:

| 모델 | 아키텍처 | PSNR 향상 |
|---|---|---|
| Noise2Noise | U-Net 변형 | +4-6 dB |
| TomoGAN | 지각 손실(perceptual loss) 적용 GAN | +5-8 dB |
| BM3D-Net | 블록 매칭 + CNN | +3-5 dB |

```python
import torch
model = torch.load("models/tomogan_v3.pt")
model.eval()
for slab in volume.iter_slabs(size=64):
    slab_gpu = torch.from_numpy(slab).cuda().unsqueeze(0)
    with torch.no_grad():
        denoised = model(slab_gpu)
    output.write_slab(denoised.cpu().numpy())
```

2048^3 볼륨에 대한 추론은 4x A100 GPU에서 약 90초가 소요됩니다.

## 4단계: 분할(U-Net)

3D U-Net은 노이즈가 제거된 볼륨을 재료 상(phase)(기공, 매트릭스 등)으로 분할합니다:

| 파라미터 | 값 |
|---|---|
| 아키텍처 | 3D U-Net (4 인코더/디코더 레벨) |
| 입력 패치 크기 | 128 x 128 x 128 복셀(voxel) |
| 오버랩 | 32 복셀 (블렌딩 스티칭) |
| 손실 함수(Loss function) | Dice + 교차 엔트로피(cross-entropy) |
| 추론 시간 | 2048^3 볼륨당 ~3 분 (A100) |

후처리(post-processing)에는 연결 성분 라벨링(connected component labeling),
형태학적 침식/팽창(morphological erosion/dilation), 접촉 객체의
워터셰드(watershed) 분리가 포함됩니다.

## 5단계: 정량화(Quantification)

분할된 볼륨에서 추출되는 지표:

| 지표 | 설명 | 단위 |
|---|---|---|
| 기공률(Porosity) | 기공 상의 부피 분율 | % |
| 기공 크기 분포 | 등가 구(equivalent sphere) 직경 히스토그램 | um |
| 표면적 | 마칭 큐브(marching-cubes) 메시 면적 | um^2 |
| 곡률(Tortuosity) | 경로 길이 / 직선 거리 | 무차원 |
| 연결성(Connectivity) | 기공 네트워크의 오일러 수(Euler number) | 무차원 |

결과는 HDF5 볼륨과 함께 JSON 사이드카 파일로 저장됩니다.

## HPC 작업 제출

```bash
qsub -A eBERlight_allocation \
     -q prod \
     -l select=4:ngpus=4 \
     -l walltime=01:00:00 \
     -l filesystems=eagle \
     -- /path/to/pipeline_runner.sh $SCAN_ID
```

`pipeline_runner.sh` 스크립트는 다섯 단계를 모두 오케스트레이션하며,
중간 출력은 NVMe 스크래치에, 최종 결과는 Eagle에 기록합니다.

## 출력 형식

| 단계 | 형식 | 압축 | 일반적인 크기 |
|---|---|---|---|
| 전처리된 투영 | HDF5 | LZ4 | 20-50 GB |
| 재구성된 볼륨 | Zarr | Blosc-zstd | 30-80 GB |
| 노이즈 제거된 볼륨 | Zarr | Blosc-zstd | 30-80 GB |
| 분할 라벨 | HDF5 | gzip | 5-15 GB |
| 정량화 | JSON | 없음 | < 1 MB |

처리된 데이터는 [analysis.md](analysis.md)에 설명된 분석 단계로 이어집니다.
