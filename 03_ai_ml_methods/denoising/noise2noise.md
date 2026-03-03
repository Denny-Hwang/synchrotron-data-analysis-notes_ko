# Noise2Noise: 자기 지도 노이즈 제거(Self-Supervised Denoising)

**참고문헌**: Lehtinen et al. (2018), "Noise2Noise: Learning Image Restoration without Clean Data"

## 원리

Noise2Noise는 **노이즈가 있는 관측만으로** 노이즈 제거 네트워크를 학습할 수 있음을 보여줍니다 — 깨끗한 정답(Ground Truth)이 필요 없습니다. 핵심 통찰은 다음과 같습니다:

```
E[noisy₁] = E[noisy₂] = 깨끗한 신호

noisy₁ → noisy₂ (noisy → clean 대신)로 매핑하도록 학습하면,
최적 네트워크 출력은 동일합니다: 깨끗한 신호.
```

### 수학적 정당화

영평균(Zero-mean), 독립적 노이즈의 경우:
- 목표: y = x + η₂ (노이즈 관측 2)
- 입력: x̂ = x + η₁ (노이즈 관측 1)
- MSE 손실: E[||f(x̂) - y||²] = E[||f(x̂) - x||²] + E[||η₂||²]
- 노이즈 항은 상수 → 이 손실을 최소화하는 것은 깨끗한 신호 x에 대한
  재구성 오차를 최소화하는 것과 동등

**요구 사항**: 노이즈는 두 관측 사이에서 영평균이고 독립적이어야 합니다.

## 방사광 데이터에의 적용

### 토모그래피(Tomography)

```
스캔 1 (빠름, 노이즈) → 재구성 1 → 입력
스캔 2 (빠름, 노이즈) → 재구성 2 → 목표

학습: f(Recon₁) → Recon₂
추론: f(noisy_recon) → denoised_recon
```

**실용적 구현**:
- 동일 시료의 두 번의 빠른 연속 스캔을 수집
- 각 스캔은 독립적으로 노이즈가 있지만 동일한 구조를 포착
- 네트워크가 공통(신호) 성분을 추출하는 것을 학습

### XRF 현미경

```
스캔 1 (짧은 체류 시간) → 노이즈 원소 맵 → 입력
스캔 2 (짧은 체류 시간) → 노이즈 원소 맵 → 목표
```

### 분광학(Spectroscopy)

```
스펙트럼 스캔 1 (빠름) → 노이즈 스펙트럼 → 입력
스펙트럼 스캔 2 (빠름) → 노이즈 스펙트럼 → 목표
```

## 구현

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

class NoisyPairDataset(Dataset):
    """쌍을 이루는 노이즈 관측 데이터셋."""

    def __init__(self, noisy_1, noisy_2, patch_size=64):
        self.noisy_1 = noisy_1  # 첫 번째 노이즈 관측
        self.noisy_2 = noisy_2  # 두 번째 노이즈 관측
        self.patch_size = patch_size

    def __len__(self):
        return self.noisy_1.shape[0] * 100  # 무작위 크롭으로 오버샘플링

    def __getitem__(self, idx):
        slice_idx = idx % self.noisy_1.shape[0]
        img1 = self.noisy_1[slice_idx]
        img2 = self.noisy_2[slice_idx]

        # 무작위 크롭
        h, w = img1.shape
        y = torch.randint(0, h - self.patch_size, (1,)).item()
        x = torch.randint(0, w - self.patch_size, (1,)).item()

        patch1 = img1[y:y+self.patch_size, x:x+self.patch_size]
        patch2 = img2[y:y+self.patch_size, x:x+self.patch_size]

        return patch1.unsqueeze(0).float(), patch2.unsqueeze(0).float()

# 학습 루프
model = UNet(in_channels=1, out_channels=1)  # 모든 노이즈 제거 아키텍처
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(100):
    for noisy_input, noisy_target in dataloader:
        pred = model(noisy_input)
        loss = nn.MSELoss()(pred, noisy_target)  # 노이즈 목표도 괜찮음!

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

## 변형

### Noise2Void (N2V)

**단일 노이즈 이미지**만 필요 (쌍 없음):

- 학습 시, 각 수용 영역(Receptive Field)의 중심 픽셀을 마스킹
- 네트워크가 주변 맥락에서 마스킹된 픽셀을 예측
- 공간적 노이즈 독립성을 활용 (인접 픽셀은 독립적 노이즈를 가짐)
- Noise2Noise보다 품질은 낮지만 반복 스캔이 필요 없음

### Noise2Self

이론적 보장이 있는 Noise2Void의 일반화:
- J-불변 네트워크 (픽셀 j의 출력이 픽셀 j의 입력에 의존하지 않음)
- 완만한 노이즈 가정 하에서 증명 가능하게 최적

### Noise2Same

단일 노이즈 이미지와 임의의 노이즈 분포에서 작동하는 추가 확장.

## 방사광 특유의 고려 사항

### 장점
1. **깨끗한 참조 불필요**: 고선량 "깨끗한" 스캔이 비현실적일 때 중요
2. **선량 감소**: 두 번의 절반 선량 스캔 → 학습 → 단일 절반 선량 스캔 노이즈 제거
3. **원위치(In-situ) 연구**: 느리게 변하는 시료에 대해 시간적 이웃을 쌍으로 사용 가능
4. **유연성**: 노이즈 이미지를 생성하는 모든 모달리티에서 작동

### 과제
1. **반복 스캔 필요**: 동일 장면의 두 노이즈 관측을 수집해야 함
2. **정적 시료 가정**: 스캔 사이에 시료가 변하지 않아야 함
3. **노이즈 독립성**: 체계적 아티팩트(링, 줄무늬)가 독립성을 위반
4. **낮은 품질**: 깨끗한 목표를 사용하는 지도 학습 방법보다 일반적으로 1-2 dB PSNR 낮음

### Noise2Noise 대 TomoGAN 사용 시기

| 기준 | Noise2Noise | TomoGAN |
|-----------|-------------|---------|
| 깨끗한 참조 사용 가능? | 아니오 | 예 |
| 반복 스캔 가능? | 예 | 필요 없음 |
| 시료가 방사선에 민감? | 좋음 (각각 절반 선량) | 전체 선량 참조 필요 |
| 이미지 품질 | 좋음 | 최고 |
| 학습 안정성 | 안정적 | GAN 학습의 어려움 |
| 일반화 | 시료별 | 시료 간 일반화 가능 |

## 결과

방사광 토모그래피 데이터에서의 일반적인 성능 비교:

| 방법 | PSNR (dB) | SSIM | 비고 |
|--------|-----------|------|-------|
| 노이즈 입력 | 25.0 | 0.72 | 기준값 |
| BM3D | 30.1 | 0.88 | 고전적, 학습 없음 |
| **Noise2Noise** | **32.5** | **0.92** | 자기 지도 학습 |
| TomoGAN (지도 학습) | 34.5 | 0.95 | 깨끗한 목표 필요 |

*값은 대표적이며, 노이즈 수준과 시료 유형에 따라 달라집니다.*
