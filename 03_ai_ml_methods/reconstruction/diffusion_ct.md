# CT 재구성을 위한 Diffusion 모델

**참고문헌**: Song et al. (2021), DOI: [10.48550/arXiv.2011.13456](https://doi.org/10.48550/arXiv.2011.13456); DM4CT Benchmark (OpenReview, 2024)

## 개념

**Score 기반 diffusion 모델**은 데이터 분포의 그래디언트("score")를 학습하고
반복적인 디노이징을 통해 노이즈로부터 고품질 이미지를 생성한다. CT 재구성에
적용하면, 물리 기반 데이터 일관성과 결합되어 심하게 언더샘플링된 측정값으로부터
재구성을 수행할 수 있는 강력한 학습된 prior로 작용한다.

```
Traditional:   Sparse projections → FBP → Artifact-heavy image
Learned:       Sparse projections → Trained CNN → Single-pass reconstruction
Diffusion:     Sparse projections → Iterative denoise + physics → Clean reconstruction
                                     (100-1000 refinement steps)
```

## 아키텍처

### Score 네트워크 (Noise-Conditional)

```
Input: Noisy image x_t + noise level t
    │
    ├─→ Time embedding
    │       t → sinusoidal encoding → MLP → time features
    │
    ├─→ U-Net with attention
    │       Conv→GN→SiLU (64)  + time ─────────────────────┐
    │       Conv→GN→SiLU (128) + time ──────────────┐       │
    │       Conv→GN→SiLU (256) + time + attn ────┐  │       │
    │       Conv→GN→SiLU (512) + time + attn ─┐  │  │       │
    │       │ [Bottleneck + self-attention]     │  │  │       │
    │       TransConv + skip ──────────────────┘  │  │       │
    │       TransConv + skip + attn ──────────────┘  │       │
    │       TransConv + skip ────────────────────────┘       │
    │       TransConv + skip ────────────────────────────────┘
    │
    └─→ Output: Score estimate ∇_x log p_t(x_t)

GN = Group Normalization
SiLU = Sigmoid Linear Unit (x · sigmoid(x))
```

### Score 기반 생성 모델링

```
Forward process (adding noise):
  x_0 → x_1 → x_2 → ... → x_T ≈ N(0, I)
  x_t = √(α_t) × x_0 + √(1 - α_t) × ε,   ε ~ N(0, I)

Reverse process (denoising):
  x_T → x_{T-1} → ... → x_1 → x_0
  x_{t-1} = (1/√α_t)(x_t - (1-α_t)/√(1-ᾱ_t) × s_θ(x_t, t)) + σ_t × z

where s_θ(x_t, t) is the learned score network
```

## CT 재구성에의 응용

### 문제 설정

```
Sparse-view CT:      Few projection angles (e.g., 60 instead of 720)
Limited-angle CT:    Restricted angular range (e.g., 0°-120° instead of 0°-180°)
Low-dose CT:         Few photons per projection

All cases: Standard FBP produces severe artifacts (streaks, distortions)
```

### Diffusion + 데이터 일관성

핵심 혁신은 diffusion prior를 물리 기반 투영 제약 조건과 결합하는 것이다.

```
For each reverse diffusion step t = T, T-1, ..., 1:
    1. Denoise step: x̂_{t-1} = denoise(x_t, s_θ)    [learned prior]
    2. Data consistency: x_{t-1} = DC(x̂_{t-1}, y)    [physics constraint]

Data Consistency (DC):
    x_{t-1} = x̂_{t-1} + λ × A^T(y - A × x̂_{t-1})

where:
    A    = forward projection operator (Radon transform)
    A^T  = backprojection operator
    y    = measured sinogram
    λ    = step size for data consistency
```

### 장점: 다른 패턴에 대해 재학습 불필요

```
GAN/CNN approach:   Train for 60 views → retrain for 30 views → retrain for limited-angle
Diffusion approach: Train score model ONCE on CT images
                    → Apply with ANY undersampling pattern at inference time
                    → Data consistency adapts to the measurement geometry

This is because the score model learns the image prior p(x),
NOT the inverse mapping A^{-1}. The measurement model A is
applied separately during inference.
```

## DM4CT 벤치마크 (2024)

DM4CT 벤치마크는 CT 재구성 작업을 위한 diffusion 모델의 표준화된 평가를
제공한다.

```
Tasks:
  ├── Sparse-view CT (60, 120, 180 views)
  ├── Limited-angle CT (90°, 120°, 150° range)
  ├── Low-dose CT (Poisson noise levels)
  └── Region-of-interest CT (truncated projections)

Key findings:
  - Diffusion models outperform FBP+postprocessing by 3-6 dB PSNR
  - Competitive with or superior to GAN methods
  - More robust to out-of-distribution samples
  - Slower inference (minutes vs. milliseconds for CNNs)
```

## GAN 기반 방법과의 비교

| 측면 | GAN (예: TomoGAN) | Diffusion 모델 |
|--------|-------------------|-----------------|
| **학습 안정성** | Mode collapse 위험 | 안정적 (디노이징 목적함수) |
| **환각(Hallucination)** | 비물리적 특징 생성 가능 | 환각 적음 (반복적 정제) |
| **다양성** | 단일 출력 | 여러 샘플 생성 가능 |
| **불확실성** | 기본 불확실성 없음 | 샘플 분산 = 불확실성 |
| **속도** | 빠름 (단일 forward pass) | 느림 (100-1000 steps) |
| **유연성** | 새로운 셋업마다 재학습 | 동일 모델, 다른 물리 |
| **품질 (sparse-view)** | ★★★★ | ★★★★★ |
| **품질 (limited-angle)** | ★★★ | ★★★★ |

## 정량적 성능

| 방법 | Sparse-view (60) PSNR | Sparse-view (60) SSIM | Limited-angle (120°) PSNR |
|--------|----------------------|----------------------|--------------------------|
| **FBP** | 22.4 | 0.62 | 18.1 |
| **SIRT (200 iter)** | 26.8 | 0.78 | 22.5 |
| **FBPConvNet** | 31.2 | 0.91 | 27.8 |
| **TomoGAN** | 32.5 | 0.93 | 28.3 |
| **Diffusion + DC** | **34.1** | **0.95** | **30.7** |

*DM4CT 벤치마크의 대표적 수치이며, 실제 성능은 데이터셋 및 구현 세부사항에
따라 달라진다.*

## 학습 전략

### Score 네트워크 학습

```
Training data: Collection of high-quality CT reconstructions
               (these serve as samples from p(x))

Training procedure:
    1. Sample clean image x_0 from training set
    2. Sample random noise level t ~ Uniform(1, T)
    3. Add noise: x_t = √(ᾱ_t) × x_0 + √(1-ᾱ_t) × ε
    4. Train score network: L = ||s_θ(x_t, t) - ε||²
       (predict the added noise)

No projection/sinogram data needed during training!
The physics model is applied only at inference time.
```

### 학습 세부사항

- **아키텍처**: 16×16 및 32×32 해상도에서 self-attention을 갖는 U-Net
- **이미지 크기**: 256×256 또는 512×512 CT 슬라이스
- **학습 셋**: 5,000-50,000 CT 슬라이스
- **배치 크기**: 8-32
- **옵티마이저**: Adam (lr=2×10⁻⁴)
- **Diffusion steps T**: 1000 (학습), 50-200 (DDIM 추론)
- **학습 시간**: 4 GPUs에서 1-3일
- **추론 시간**: 슬라이스당 30초 - 5분 (단계 수에 따라)

## 강점

1. **유연한 측정 모델**: 동일한 학습된 모델이 어떤 투영 기하학과도 작동
2. **Mode collapse 없음**: 안정적인 학습 (GAN과 달리)
3. **불확실성 정량화**: 여러 번 실행 → 샘플 분산을 불확실성으로 활용
4. **최첨단 품질**: Sparse-view 및 limited-angle CT에서 최고 성능
5. **물리 기반 가이드**: 데이터 일관성이 측정 충실도 보장
6. **분포 변화에 강건**: 학습된 prior가 샘플 유형 전반에 걸쳐 일반화

## 한계점

1. **느린 추론**: 100-1000 디노이징 단계 (CNN의 밀리초 대비 슬라이스당 분 단위)
2. **메모리 집약적**: Score 네트워크 + 중간 상태가 상당한 GPU 메모리 요구
3. **학습 데이터 요구량 큼**: Prior 학습을 위해 수천 개의 고품질 CT 이미지 필요
4. **하이퍼파라미터 튜닝**: 데이터 일관성 가중치 λ, 단계 수, 노이즈 스케줄
5. **수렴 보장 없음**: 반복 과정이 모든 입력에 대해 수렴하지 않을 수 있음
6. **2D 슬라이스로 제한**: 전체 3D 볼륨으로의 확장은 계산적으로 어려움

## 가속화된 추론

```
Standard DDPM:    1000 steps → ~10 minutes per slice
DDIM sampling:    50-100 steps → ~1 minute per slice
DPM-Solver:       20-50 steps → ~20 seconds per slice
Consistency model: 1-4 steps → ~1-5 seconds per slice (quality trade-off)
```

## 코드 예시

```python
import torch
import torch.nn as nn
import numpy as np

class ScoreUNet(nn.Module):
    """Simplified score network for CT diffusion model."""

    def __init__(self, channels=64, time_emb_dim=128):
        super().__init__()
        # Time embedding
        self.time_mlp = nn.Sequential(
            nn.Linear(1, time_emb_dim),
            nn.SiLU(),
            nn.Linear(time_emb_dim, time_emb_dim),
        )

        # U-Net encoder
        self.enc1 = self._block(1, channels, time_emb_dim)
        self.enc2 = self._block(channels, channels * 2, time_emb_dim)
        self.enc3 = self._block(channels * 2, channels * 4, time_emb_dim)

        # Bottleneck
        self.bottleneck = self._block(channels * 4, channels * 8, time_emb_dim)

        # Decoder
        self.up3 = nn.ConvTranspose2d(channels * 8, channels * 4, 4, 2, 1)
        self.dec3 = self._block(channels * 8, channels * 4, time_emb_dim)
        self.up2 = nn.ConvTranspose2d(channels * 4, channels * 2, 4, 2, 1)
        self.dec2 = self._block(channels * 4, channels * 2, time_emb_dim)
        self.up1 = nn.ConvTranspose2d(channels * 2, channels, 4, 2, 1)
        self.dec1 = self._block(channels * 2, channels, time_emb_dim)

        self.final = nn.Conv2d(channels, 1, 1)
        self.pool = nn.MaxPool2d(2)

    def _block(self, in_ch, out_ch, time_dim):
        return nn.ModuleDict({
            'conv': nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 3, padding=1),
                nn.GroupNorm(8, out_ch),
                nn.SiLU(),
                nn.Conv2d(out_ch, out_ch, 3, padding=1),
                nn.GroupNorm(8, out_ch),
                nn.SiLU(),
            ),
            'time_proj': nn.Linear(time_dim, out_ch),
        })

    def _apply_block(self, block, x, t_emb):
        h = block['conv'](x)
        t = block['time_proj'](t_emb)[:, :, None, None]
        return h + t

    def forward(self, x, t):
        t_emb = self.time_mlp(t.unsqueeze(-1).float())

        e1 = self._apply_block(self.enc1, x, t_emb)
        e2 = self._apply_block(self.enc2, self.pool(e1), t_emb)
        e3 = self._apply_block(self.enc3, self.pool(e2), t_emb)

        b = self._apply_block(self.bottleneck, self.pool(e3), t_emb)

        d3 = self._apply_block(self.dec3, torch.cat([self.up3(b), e3], 1), t_emb)
        d2 = self._apply_block(self.dec2, torch.cat([self.up2(d3), e2], 1), t_emb)
        d1 = self._apply_block(self.dec1, torch.cat([self.up1(d2), e1], 1), t_emb)

        return self.final(d1)


def diffusion_ct_reconstruct(score_model, sinogram, angles, n_steps=200,
                              image_size=256, lam=1.0):
    """Reconstruct CT image using diffusion model with data consistency.

    Args:
        score_model: Trained score network
        sinogram: Measured projections (n_angles, n_detectors)
        angles: Projection angles in radians
        n_steps: Number of reverse diffusion steps
        image_size: Output image size
        lam: Data consistency weight
    """
    from skimage.transform import radon, iradon

    device = next(score_model.parameters()).device

    # Initialize from noise
    x = torch.randn(1, 1, image_size, image_size, device=device)

    # Noise schedule (linear)
    betas = torch.linspace(1e-4, 0.02, 1000, device=device)
    alphas = 1 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)

    # DDIM-style sampling with fewer steps
    step_indices = torch.linspace(999, 0, n_steps, dtype=torch.long, device=device)

    for i in range(len(step_indices)):
        t = step_indices[i]

        # 1. Score prediction (denoise step)
        with torch.no_grad():
            noise_pred = score_model(x, t.unsqueeze(0))

        # Predict x_0
        alpha_bar_t = alpha_bars[t]
        x0_pred = (x - torch.sqrt(1 - alpha_bar_t) * noise_pred) / torch.sqrt(alpha_bar_t)

        # 2. Data consistency step
        x0_np = x0_pred.squeeze().cpu().numpy()
        sino_pred = radon(x0_np, theta=np.degrees(angles))
        sino_residual = sinogram - sino_pred
        correction = iradon(sino_residual, theta=np.degrees(angles),
                           filter_name=None, output_size=image_size)
        correction_tensor = torch.tensor(correction, device=device,
                                         dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        x0_corrected = x0_pred + lam * correction_tensor

        # 3. Add noise for next step (if not last step)
        if i < len(step_indices) - 1:
            t_next = step_indices[i + 1]
            alpha_bar_next = alpha_bars[t_next]
            x = (torch.sqrt(alpha_bar_next) * x0_corrected +
                 torch.sqrt(1 - alpha_bar_next) * torch.randn_like(x))
        else:
            x = x0_corrected

    return x
```

## APS BER 프로그램과의 관련성

### 주요 응용

- **Sparse-view in-situ CT**: 시간 분해 스캔을 더 빠르게 수행하기 위한 투영 수 감소
- **Limited-angle 단층 촬영**: 제한된 각도 범위로부터 재구성 (예: HEDM)
- **선량 감소**: 더 적은 투영 = 방사선에 민감한 샘플의 총 선량 감소
- **불확실성 정량화**: 여러 diffusion 샘플이 재구성 불확실성을 제공

### 빔라인 통합

- **2-BM**: Sparse-view 고속 단층 촬영 — diffusion 모델로 5-10배 적은 투영 가능
- **1-ID**: 제한된 각도 범위의 고에너지 회절 현미경
- **32-ID**: 각 투영이 고유한 초고속 이미징 (반복 각도 없음)
- GPU 집약적 추론을 위한 ALCF의 계산 지원

### 향후 방향 (2025-2026)

- **3D diffusion 모델**: 3D 볼륨에서 직접 작동 (슬라이스별 처리 대비)
- **Conditional diffusion**: 샘플 유형, 실험 파라미터에 조건화
- **실시간 추론**: 단일 단계 재구성을 위한 consistency distillation
- **다중 모달**: 흡수 + 위상 대비 CT에 대한 결합 diffusion prior

## 참고문헌

1. Song, Y., et al. "Score-Based Generative Modeling through Stochastic Differential
   Equations." ICLR 2021. DOI: [10.48550/arXiv.2011.13456](https://doi.org/10.48550/arXiv.2011.13456)
2. Chung, H., et al. "Diffusion Posterior Sampling for General Noisy Inverse Problems."
   ICLR 2023. arXiv: 2209.14687
3. DM4CT: "A Benchmark for Diffusion Models in CT Reconstruction."
   OpenReview, 2024.
4. Song, J., Meng, C., Ermon, S. "Denoising Diffusion Implicit Models."
   ICLR 2021. arXiv: 2010.02502
