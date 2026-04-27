# Noise2Void: 단일 노이즈 이미지로부터의 자기지도 노이즈 제거

**참고문헌**: Krull et al., CVPR (2019), DOI: [10.1109/CVPR.2019.00223](https://doi.org/10.1109/CVPR.2019.00223)

## 개념

**Noise2Void (N2V)** 는 학습에 **단일 노이즈 이미지**만 필요로 하는 자기지도 노이즈 제거 방법으로, 클린 타겟이나 노이즈 쌍, 반복 측정이 필요하지 않습니다. 학습 중 중심 픽셀을 마스킹하는 블라인드 스팟 네트워크를 사용하여 주변 컨텍스트로부터 각 픽셀을 예측하는 방법을 학습합니다.

```
Traditional supervised:   Noisy image + Clean target → Train CNN
Noise2Noise:              Noisy image + Noisy pair   → Train CNN
Noise2Void:               Single noisy image ONLY    → Train CNN
```

## 아키텍처

### 블라인드 스팟 네트워크

```
Noisy input image (1ch, H×W)
    │
    ├─→ Random pixel sampling (per batch)
    │       Select N random pixel locations (i, j)
    │       For each: mask center pixel from receptive field
    │
    ├─→ U-Net encoder-decoder
    │       Conv→BN→ReLU (64)  ─────────────────────┐
    │       Conv→BN→ReLU (128) ──────────────┐       │
    │       Conv→BN→ReLU (256) ───────┐       │       │
    │       Conv→BN→ReLU (512)  ──┐   │       │       │
    │       │ [Bottleneck]        │   │       │       │
    │       TransConv + skip ─────┘   │       │       │
    │       TransConv + skip ─────────┘       │       │
    │       TransConv + skip ─────────────────┘       │
    │       TransConv + skip ─────────────────────────┘
    │
    └─→ Output: Predicted pixel values at masked locations

Key: The network NEVER sees the target pixel value during prediction.
     It must infer the clean value from surrounding context only.
```

### 블라인드 스팟 마스킹 전략

```
Receptive field (5×5 example):

  Standard CNN:          Blind-spot CNN:
  ┌─┬─┬─┬─┬─┐          ┌─┬─┬─┬─┬─┐
  │x│x│x│x│x│          │x│x│x│x│x│
  ├─┼─┼─┼─┼─┤          ├─┼─┼─┼─┼─┤
  │x│x│x│x│x│          │x│x│x│x│x│
  ├─┼─┼─┼─┼─┤          ├─┼─┼─┼─┼─┤
  │x│x│■│x│x│          │x│x│ │x│x│  ← center pixel EXCLUDED
  ├─┼─┼─┼─┼─┤          ├─┼─┼─┼─┼─┤
  │x│x│x│x│x│          │x│x│x│x│x│
  ├─┼─┼─┼─┼─┤          ├─┼─┼─┼─┼─┤
  │x│x│x│x│x│          │x│x│x│x│x│
  └─┴─┴─┴─┴─┘          └─┴─┴─┴─┴─┘

The center pixel is replaced with a random neighbor value during training.
This prevents the trivial identity mapping solution.
```

## 손실 함수

```
L = (1/N) Σ_i ||f_θ(x_masked)_i - x_i||²

where:
  f_θ       = blind-spot network
  x_masked  = input image with center pixel replaced by neighbor
  x_i       = original (noisy) pixel value at sampled location i
  N         = number of sampled pixels per image

Key insight: If noise is zero-mean and pixel-independent, minimizing this
loss is equivalent to minimizing MSE against the clean image.
```

### 작동 원리 (통계적 논증)

```
Assumption: noise n_i is zero-mean, independent per pixel
  x_i = s_i + n_i   (noisy = clean + noise)

The network sees neighbors x_j = s_j + n_j for j ≠ i
Predicts: f_θ(context) ≈ E[s_i | {x_j, j ≠ i}]
Trains against: x_i = s_i + n_i

E[L] = E[||f_θ - s_i||²] + E[||n_i||²]
                ↑                    ↑
        minimized by training   constant (noise variance)

→ Network learns to predict the clean signal!
```

## 변형 모델

### Noise2Self (Batson & Royer, 2019)

```
Generalizes blind-spot idea to arbitrary partitions:
- Partition pixels into J subsets (e.g., checkerboard)
- Train network on subset J_k to predict pixels not in J_k
- Mathematical framework unifying self-supervised denoising
```

### Neighbor2Neighbor (Huang et al., 2021)

```
Creates training pairs from a single noisy image:
- Subsample image into two complementary views
  (e.g., even/odd pixels in checkerboard pattern)
- Train a standard denoiser using the two views as input/target
- Avoids blind-spot architecture constraints
- Often better quality than N2V
```

### Noise2Void 2 / PN2V (확률론적 모델)

```
- Extends N2V with a noise model (e.g., Gaussian mixture)
- Outputs a distribution, not a point estimate
- Provides pixel-wise uncertainty maps
- Better handling of signal-dependent noise (Poisson, mixed)
```

## 학습 전략

### 데이터 준비

```
Single noisy synchrotron image (or volume)
    │
    ├─→ No clean reference needed
    ├─→ No repeated measurements needed
    ├─→ Can train on the SAME image being denoised
    │
    └─→ Optional: train on multiple noisy images of similar type
         for a more general model
```

### 학습 세부사항

- **패치 크기**: 64×64 (입력 이미지에서 무작위로 자름)
- **패치당 마스킹 픽셀**: 픽셀의 0.5-2% (예: 64×64 패치당 20-80개)
- **배치 크기**: 64-128 패치
- **옵티마이저**: Adam (lr=4×10⁻⁴)
- **에폭 수**: 100-300 (단일 이미지로 학습 가능)
- **데이터 증강**: 무작위 뒤집기, 회전 (90도 단위)
- **학습 시간**: 단일 GPU에서 10-30분 (이미지당)

## 정량적 성능

| 지표 | Noisy input | BM3D | Noise2Noise | **Noise2Void** | Supervised CNN |
|--------|------------|------|-------------|----------------|---------------|
| **PSNR (dB)** | 22.1 | 29.8 | 32.1 | **30.5** | 33.2 |
| **SSIM** | 0.61 | 0.87 | 0.92 | **0.89** | 0.94 |
| **NRMSE** | 0.152 | 0.062 | 0.041 | **0.053** | 0.035 |

*값은 synchrotron CT 데이터에 대한 대표적인 수치이며, 실제 성능은 노이즈 레벨과 데이터셋에 따라 달라집니다. N2V는 클린 데이터나 페어 데이터가 필요 없다는 큰 장점을 위해 약 1-2 dB의 PSNR을 절충합니다.*

## 싱크로트론 데이터에 대한 응용

### Synchrotron CT

```
Problem:  Low-dose CT scans produce noisy reconstructions.
          No clean reference available (cannot re-scan at higher dose).
N2V use:  Train on the noisy reconstruction volume itself.
          Each 2D slice or 3D patch treated as training sample.
          Denoise entire volume without any additional data.
```

### Cryo-EM

```
Problem:  Extremely low SNR micrographs (SNR < 0.1).
          Biological samples cannot tolerate repeated exposure.
N2V use:  Train on collection of micrographs from same session.
          Leverages structural redundancy across particles.
          Improves particle picking and initial model quality.
```

### SAXS / WAXS

```
Problem:  Low-exposure scattering patterns have high Poisson noise.
          Time-resolved experiments cannot repeat measurements.
N2V use:  Train on series of SAXS frames.
          Reduces noise while preserving peak positions and shapes.
          Enables analysis of weaker scattering features.
```

## 강점

1. **클린 데이터 불필요**: 노이즈 이미지 자체만 필요함
2. **반복 측정 불필요**: Noise2Noise와 달리 노이즈 쌍이 필요 없음
3. **모든 모달리티에 적용 가능**: CT, cryo-EM, SAXS, XRF, ptychography
4. **빠른 적응**: 타겟 이미지에서 직접 수 분 내에 학습 가능
5. **이론적 근거**: 픽셀 독립 노이즈 하에서 증명 가능한 최적성
6. **오픈 소스**: 잘 유지되는 구현체와 광범위한 커뮤니티 지원

## 한계점

1. **지도 학습 대비 낮은 품질**: 데이터 유연성을 위해 1-3 dB의 PSNR 절충
2. **노이즈 독립성 가정**: 노이즈가 공간적으로 상관되어 있으면 성능 저하
3. **블라인드 스팟 아티팩트**: 미세한 체커보드 패턴이 발생할 수 있음
4. **구조화된 노이즈 처리 불가**: 링 아티팩트나 시스템적 오류 처리 불가
5. **하이퍼파라미터 민감성**: 마스킹 비율과 패치 크기가 품질에 영향을 줌
6. **신호 의존적 노이즈**: 표준 N2V는 가산 노이즈를 가정함; Poisson 노이즈는
   확률론적 확장(PN2V)이 필요함

## 코드 예제

```python
import torch
import torch.nn as nn
import numpy as np

class Noise2VoidUNet(nn.Module):
    """Simplified U-Net for Noise2Void self-supervised denoising."""

    def __init__(self, in_ch=1, out_ch=1, base_filters=64):
        super().__init__()
        # Encoder
        self.enc1 = self._block(in_ch, base_filters)
        self.enc2 = self._block(base_filters, base_filters * 2)
        self.enc3 = self._block(base_filters * 2, base_filters * 4)

        # Bottleneck
        self.bottleneck = self._block(base_filters * 4, base_filters * 8)

        # Decoder
        self.up3 = nn.ConvTranspose2d(base_filters * 8, base_filters * 4, 4, 2, 1)
        self.dec3 = self._block(base_filters * 8, base_filters * 4)
        self.up2 = nn.ConvTranspose2d(base_filters * 4, base_filters * 2, 4, 2, 1)
        self.dec2 = self._block(base_filters * 4, base_filters * 2)
        self.up1 = nn.ConvTranspose2d(base_filters * 2, base_filters, 4, 2, 1)
        self.dec1 = self._block(base_filters * 2, base_filters)

        self.final = nn.Conv2d(base_filters, out_ch, 1)
        self.pool = nn.MaxPool2d(2)

    def _block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        e1 = self.enc1(x);    p1 = self.pool(e1)
        e2 = self.enc2(p1);   p2 = self.pool(e2)
        e3 = self.enc3(p2);   p3 = self.pool(e3)

        b = self.bottleneck(p3)

        d3 = self.dec3(torch.cat([self.up3(b), e3], 1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], 1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], 1))

        return self.final(d1)


def n2v_mask_batch(patches, mask_ratio=0.01):
    """Apply Noise2Void blind-spot masking to a batch of patches.

    For each patch, randomly select pixels, replace with neighbor value,
    and return the masked input, original values, and mask coordinates.
    """
    b, c, h, w = patches.shape
    n_masked = int(h * w * mask_ratio)

    masked_patches = patches.clone()
    target_values = torch.zeros(b, n_masked)
    mask_coords = torch.zeros(b, n_masked, 2, dtype=torch.long)

    for i in range(b):
        # Random pixel locations
        y_coords = torch.randint(0, h, (n_masked,))
        x_coords = torch.randint(0, w, (n_masked,))

        # Store original values as targets
        target_values[i] = patches[i, 0, y_coords, x_coords]
        mask_coords[i, :, 0] = y_coords
        mask_coords[i, :, 1] = x_coords

        # Replace with random neighbor
        for j in range(n_masked):
            dy, dx = np.random.choice([-1, 0, 1], size=2)
            ny = np.clip(y_coords[j].item() + dy, 0, h - 1)
            nx = np.clip(x_coords[j].item() + dx, 0, w - 1)
            masked_patches[i, 0, y_coords[j], x_coords[j]] = patches[i, 0, ny, nx]

    return masked_patches, target_values, mask_coords


def train_n2v(model, noisy_image, n_epochs=200, patch_size=64,
              batch_size=64, lr=4e-4, mask_ratio=0.01):
    """Train Noise2Void on a single noisy image."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    h, w = noisy_image.shape[-2:]

    for epoch in range(n_epochs):
        # Extract random patches
        patches = []
        for _ in range(batch_size):
            y = np.random.randint(0, h - patch_size)
            x = np.random.randint(0, w - patch_size)
            patches.append(noisy_image[:, :, y:y+patch_size, x:x+patch_size])
        patches = torch.cat(patches, dim=0)

        # Apply blind-spot masking
        masked_input, targets, coords = n2v_mask_batch(patches, mask_ratio)

        # Forward pass
        output = model(masked_input)

        # Compute loss ONLY at masked pixel locations
        loss = 0
        for i in range(batch_size):
            pred_vals = output[i, 0, coords[i, :, 0], coords[i, :, 1]]
            loss += torch.mean((pred_vals - targets[i]) ** 2)
        loss /= batch_size

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}/{n_epochs}, Loss: {loss.item():.6f}")

    return model
```

### CAREamics/N2V 라이브러리 사용

```python
# Installation: pip install careamics
from careamics import CAREamist
from careamics.config import create_n2v_configuration

# Create N2V configuration for 2D synchrotron data
config = create_n2v_configuration(
    experiment_name="synchrotron_ct_n2v",
    data_type="array",
    axes="YX",
    patch_size=[64, 64],
    batch_size=64,
    num_epochs=200,
)

# Train on noisy image stack
careamist = CAREamist(source=config)
careamist.train(train_source=noisy_slices)  # numpy array (N, H, W)

# Denoise
denoised = careamist.predict(source=noisy_slices)
```

## APS BER 프로그램과의 관련성

### 주요 응용

- **In-situ 실험**: 반복이 불가능한 단일 측정값의 노이즈 제거
- **선량 민감 시료**: 생물학적 및 환경 시료(토양, 뿌리, 바이오필름)
- **시간 분해 연구**: 각 시간 프레임이 고유함; 노이즈 페어 수집 불가
- **고처리량 스크리닝**: 사전 데이터 수집 없이 각 시료에 대해 빠르게 학습

### 빔라인 통합

- **2-BM**: 생물학적 시료의 저선량 토모그래피 — N2V를 통해 추가 참조 스캔 없이
  노이즈 제거 가능
- **26-ID**: 시료 드리프트로 반복 획득이 불가능한 nanoprobe 측정
- **9-ID**: In-situ 반응 모니터링을 위한 SAXS/WAXS 시계열 노이즈 제거
- 기존 TomoPy/ALCF 처리 파이프라인과 호환

### TomoGAN과의 비교

```
TomoGAN:     Needs paired low-dose/full-dose training data → Higher quality
Noise2Void:  Needs only the noisy data itself → More flexible, lower quality

Recommendation: Use TomoGAN when training data is available.
                Use N2V when only single noisy acquisitions exist.
```

## 참고문헌

1. Krull, A., Buchholz, T.O., Jost, F. "Noise2Void — Learning Denoising from Single
   Noisy Images." CVPR 2019. DOI: [10.1109/CVPR.2019.00223](https://doi.org/10.1109/CVPR.2019.00223)
2. Batson, J., Royer, L. "Noise2Self: Blind Denoising by Self-Supervision."
   ICML 2019. arXiv: 1901.11365
3. Huang, T., et al. "Neighbor2Neighbor: Self-Supervised Denoising from Single
   Noisy Images." CVPR 2021. DOI: [10.1109/CVPR46437.2021.01454](https://doi.org/10.1109/CVPR46437.2021.01454)
4. Prakash, M., et al. "Fully Unsupervised Probabilistic Noise2Void."
   IEEE ISBI 2020. arXiv: 1911.12420

**GitHub**: [https://github.com/juglab/n2v](https://github.com/juglab/n2v) (BSD-3 License)
