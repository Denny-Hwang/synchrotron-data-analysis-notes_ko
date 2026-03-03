# 방사광 데이터를 위한 U-Net 변형(Variants)

## 원본 U-Net 아키텍처

**참고문헌**: Ronneberger et al. (2015), "U-Net: Convolutional Networks for Biomedical Image Segmentation"

### 아키텍처

```
입력 (1ch, 572×572)
    │
    ▼ [인코더 경로]
    Conv3×3→ReLU→Conv3×3→ReLU ─────────────────────────────┐ (스킵 연결)
    │ MaxPool 2×2                                            │
    Conv3×3→ReLU→Conv3×3→ReLU ──────────────────────┐       │
    │ MaxPool 2×2                                    │       │
    Conv3×3→ReLU→Conv3×3→ReLU ─────────────┐       │       │
    │ MaxPool 2×2                            │       │       │
    Conv3×3→ReLU→Conv3×3→ReLU ──────┐       │       │       │
    │ MaxPool 2×2                    │       │       │       │
    │                                │       │       │       │
    ▼ [병목층(Bottleneck)]            │       │       │       │
    Conv3×3→ReLU→Conv3×3→ReLU       │       │       │       │
    │                                │       │       │       │
    ▼ [디코더 경로]                    │       │       │       │
    UpConv 2×2 ──── 연결(Concatenate) ┘       │       │       │
    Conv3×3→ReLU→Conv3×3→ReLU               │       │       │
    UpConv 2×2 ──── 연결(Concatenate) ───────┘       │       │
    Conv3×3→ReLU→Conv3×3→ReLU                       │       │
    UpConv 2×2 ──── 연결(Concatenate) ───────────────┘       │
    Conv3×3→ReLU→Conv3×3→ReLU                               │
    UpConv 2×2 ──── 연결(Concatenate) ───────────────────────┘
    Conv3×3→ReLU→Conv3×3→ReLU
    │
    ▼
    Conv1×1 → 출력 (Nclass 채널)
```

### 핵심 설계 원리
- **인코더**: 다중 스케일에서 특징을 점진적으로 추출
- **디코더**: 원래 해상도로 점진적으로 업샘플링
- **스킵 연결(Skip Connections)**: 인코더의 미세한 공간적 세부 정보를 보존
- **대칭 구조**: 인코더와 디코더의 깊이가 동일

### PyTorch 구현 (최소 버전)

```python
import torch
import torch.nn as nn

class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.conv(x)

class UNet(nn.Module):
    def __init__(self, in_channels=1, out_channels=2, features=[64, 128, 256, 512]):
        super().__init__()
        self.encoder = nn.ModuleList()
        self.decoder = nn.ModuleList()
        self.pool = nn.MaxPool2d(2, 2)

        # 인코더
        for f in features:
            self.encoder.append(DoubleConv(in_channels, f))
            in_channels = f

        # 병목층
        self.bottleneck = DoubleConv(features[-1], features[-1] * 2)

        # 디코더
        for f in reversed(features):
            self.decoder.append(nn.ConvTranspose2d(f * 2, f, 2, stride=2))
            self.decoder.append(DoubleConv(f * 2, f))

        self.final = nn.Conv2d(features[0], out_channels, 1)

    def forward(self, x):
        skips = []
        for enc in self.encoder:
            x = enc(x)
            skips.append(x)
            x = self.pool(x)

        x = self.bottleneck(x)

        skips = skips[::-1]
        for i in range(0, len(self.decoder), 2):
            x = self.decoder[i](x)      # 업샘플링
            x = torch.cat([x, skips[i // 2]], dim=1)  # 스킵 연결
            x = self.decoder[i + 1](x)  # 이중 합성곱

        return self.final(x)
```

## 어텐션 U-Net(Attention U-Net)

**개선 사항**: 관련 영역에 집중하기 위해 스킵 연결에 어텐션 게이트(Attention Gates)를 추가합니다.

```
스킵 연결 → 어텐션 게이트 → 필터링된 특징 → 연결
                  ↑
         디코더 특징 (쿼리)
```

### 어텐션 게이트
```
g (디코더 특징) ──→ Conv1×1 ──┐
                               ├──→ ReLU → Conv1×1 → Sigmoid → α
x (스킵 특징) ────→ Conv1×1 ──┘
                                    ↓
                         x_filtered = x × α
```

### 방사광 데이터에 대한 이점
- 관련 없는 영역(배경, 아티팩트)을 억제
- 관심 구조(세포, 기공)에 집중
- 대용량 볼륨에서 특징이 희소한 경우 특히 유용

## nnU-Net (자기 구성 U-Net, Self-Configuring U-Net)

**참고문헌**: Isensee et al. (2021), Nature Methods

### 핵심 혁신
데이터셋 속성에 기반하여 모든 U-Net 하이퍼파라미터를 자동 구성합니다:

| 매개변수 | nnU-Net 결정 논리 |
|-----------|----------------------|
| 2D 대 3D | 복셀 간격 이방성(Anisotropy)에 기반 |
| 패치 크기 | GPU 메모리에 맞으며 가장 큰 구조를 포함 |
| 배치 크기 | GPU 활용도 극대화 |
| 정규화 | 인스턴스 정규화(대부분의 경우) 또는 배치 정규화 |
| 손실 함수 | Dice + 교차 엔트로피(기본값) |
| 데이터 증강 | 회전, 스케일링, 탄성 변형, 감마 |
| 후처리 | 연결 요소 분석, 크기 필터링 |

### 파이프라인
```
원시 데이터셋 (이미지 + 레이블)
    │
    ├─→ 데이터셋 핑거프린팅 (간격, 크기, 클래스 분포)
    │
    ├─→ 구성 선택 (2D, 3D-fullres, 3D-lowres, 캐스케이드)
    │
    ├─→ 학습 (5겹 교차 검증)
    │
    ├─→ 후처리 최적화
    │
    └─→ 앙상블 선택 (최적 개별 또는 앙상블)
```

### 방사광에 대한 관련성
- 이방성 복셀 크기 처리 (토모그래피에서 일반적)
- 대용량 볼륨을 위한 캐스케이드 접근법: 저해상도 3D → 고해상도 3D
- 다양한 분할 작업에서 일관되게 최고 수준의 성능
- 아키텍처 탐색 전문 지식의 필요성 감소

## 3D U-Net

### 2D 대 3D 절충

| 측면 | 2D U-Net | 3D U-Net |
|--------|----------|----------|
| **메모리** | 낮음 (~1 GB) | 높음 (패치당 4-16 GB) |
| **맥락** | 단일 슬라이스 | 3D 볼류메트릭 맥락 |
| **일관성** | 슬라이스 간 아티팩트 가능 | z 방향으로 자연스럽게 일관 |
| **학습 데이터** | 적은 볼륨에서 더 많은 슬라이스 | 더 많은 3D 레이블 볼륨 필요 |
| **속도** | 빠름 | 5-10배 느림 |

### 대용량 볼륨(2048³)을 위한 전략

1. **패치 기반 추론**: 오버래핑 3D 패치 처리 (64³에서 128³)
2. **슬라이딩 윈도우**: 경계 아티팩트를 방지하기 위해 패치 오버랩
3. **캐스케이드**: 저해상도 3D → ROI 크롭 → 고해상도 3D
4. **2.5D**: 3-5개 인접 슬라이스를 다채널 2D 입력으로 사용

### 메모리 관리

```python
# 대용량 볼륨을 위한 패치 기반 추론
def segment_volume(model, volume, patch_size=128, overlap=32):
    """오버래핑 패치를 사용하여 대용량 볼륨을 분할."""
    result = np.zeros_like(volume, dtype=np.float32)
    count = np.zeros_like(volume, dtype=np.float32)
    step = patch_size - overlap

    for z in range(0, volume.shape[0] - patch_size + 1, step):
        for y in range(0, volume.shape[1] - patch_size + 1, step):
            for x in range(0, volume.shape[2] - patch_size + 1, step):
                patch = volume[z:z+patch_size, y:y+patch_size, x:x+patch_size]
                pred = model.predict(patch[np.newaxis, np.newaxis])[0, 0]
                result[z:z+patch_size, y:y+patch_size, x:x+patch_size] += pred
                count[z:z+patch_size, y:y+patch_size, x:x+patch_size] += 1

    return result / np.maximum(count, 1)
```

## 방사광 특화 적응

### 1. 다채널 입력
- XRF: 여러 원소 채널을 입력으로 사용 (자연 이미지의 RGB와 유사)
- 토모그래피: 위상 + 흡수를 이중 채널 입력으로
- 분광학: 여러 에너지 이미지를 채널로

### 2. 불균형 데이터를 위한 손실 함수
```python
# Dice 손실 (작은 구조에 더 적합)
def dice_loss(pred, target, smooth=1e-5):
    pred_flat = pred.flatten()
    target_flat = target.flatten()
    intersection = (pred_flat * target_flat).sum()
    return 1 - (2 * intersection + smooth) / (pred_flat.sum() + target_flat.sum() + smooth)

# 초점 손실(Focal Loss) (쉬운 예시의 가중치를 줄임)
def focal_loss(pred, target, alpha=0.25, gamma=2.0):
    ce = F.binary_cross_entropy(pred, target, reduction='none')
    pt = torch.where(target == 1, pred, 1 - pred)
    return (alpha * (1 - pt)**gamma * ce).mean()
```

### 3. 사전 학습 전략
- 시뮬레이션된 방사광 데이터로 사전 학습 (알려진 정답)
- 의료 영상 모델에서 전이 (유사한 데이터 특성)
- 레이블이 없는 방사광 볼륨에 대한 자기 지도 사전 학습

## 강점 및 한계

### 강점
- 비교적 적은 레이블 예시로 높은 정확도 (2D에서 50-200개)
- 스킵 연결을 통해 미세한 공간적 세부 정보 보존
- 유연한 아키텍처: 2D, 3D, 다채널에 적응 가능
- 잘 확립된 생태계 (nnU-Net이 구성을 자동화)

### 한계
- 레이블이 지정된 학습 데이터가 필요 (소량이라도)
- 대용량 3D 볼륨은 신중한 메모리 관리가 필요
- 클래스 불균형이 학습을 지배할 수 있음 (Dice/초점 손실 필요)
- 도메인 시프트: 한 빔라인에서 학습된 모델이 다른 빔라인에서 실패할 수 있음
- 내장된 불확실성 정량화 없음 (앙상블 또는 MC 드롭아웃 필요)
