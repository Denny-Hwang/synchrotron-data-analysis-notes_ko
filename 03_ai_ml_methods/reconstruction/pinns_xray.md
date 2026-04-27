# X선 재구성을 위한 물리 정보 기반 신경망(PINNs)

**참고문헌**: Li et al. (2021) FNO, DOI: [10.48550/arXiv.2010.08895](https://doi.org/10.48550/arXiv.2010.08895); Raissi et al. (2019) PINNs, DOI: [10.1016/j.jcp.2018.10.045](https://doi.org/10.1016/j.jcp.2018.10.045)

## 개념

**물리 정보 기반 신경망(Physics-Informed Neural Networks, PINNs)**은 물리적 순방향 모델을 신경망 학습 과정의 제약조건으로 직접 임베딩합니다. 순수하게 데이터 기반 매핑을 학습하는 대신, 신경망은 측정 데이터에 적합하면서 동시에 지배 물리 방정식(파동 전파, X-ray 수송, 회절)을 만족해야 합니다.

```
Data-driven CNN:     Input measurement → CNN → Output image
                     (learned entirely from training pairs)

PINN:                Input measurement → Neural network → Output image
                     + Physical model as loss constraint
                     (network output must satisfy physics)
```

## 아키텍처

### 위상 복원을 위한 표준 PINN

```
Input: Diffraction intensity I(q) or inline hologram
    │
    ├─→ Neural network f_θ (MLP or CNN)
    │       Predicts: complex field ψ(r) = A(r) × exp(iφ(r))
    │       where A = amplitude, φ = phase
    │
    ├─→ Physics loss: Apply forward model
    │       ψ(r) → Propagate(ψ) → I_predicted(q)
    │       L_physics = ||I_predicted - I_measured||²
    │
    ├─→ Data loss (if available):
    │       L_data = ||f_θ(input) - ground_truth||²
    │
    ├─→ Regularization:
    │       L_reg = ||∇φ||₁ + ||A - 1||²
    │       (smoothness of phase, weak absorption)
    │
    └─→ Total loss: L = L_physics + λ₁ L_data + λ₂ L_reg

Key: L_physics enforces that the solution is PHYSICALLY CONSISTENT
     with the measured data through the known forward model.
```

### 단층촬영 재구성을 위한 PINN

```
Input: (x, y, z) coordinates
    │
    ├─→ Coordinate network f_θ(x, y, z) → µ(x, y, z)
    │       (similar to INR, but physics-constrained)
    │
    ├─→ Physics loss: Radon transform consistency
    │       For each measured projection p_i at angle θ_i:
    │       p_predicted(θ_i) = ∫ f_θ(ray(θ_i, s)) ds
    │       L_physics = Σ_i ||p_predicted(θ_i) - p_measured(θ_i)||²
    │
    ├─→ PDE constraint (optional):
    │       Material conservation: ∇·(D∇µ) = source
    │       Positivity: µ(x,y,z) ≥ 0
    │       Known material properties
    │
    └─→ Reconstructed 3D volume: query f_θ at any (x,y,z)
```

## PDE 기반 재구성을 위한 신경 연산자

### 푸리에 신경 연산자 (FNO)

FNO(Li et al. 2021)는 함수 공간 간의 매핑을 학습하므로 PDE 기반 재구성 문제에 이상적입니다.

```
Input function: u(x) (e.g., sinogram, diffraction pattern)
    │
    ├─→ Lifting: P(u) → v₀ (project to higher-dimensional feature space)
    │
    ├─→ Fourier layers (×4):
    │       v_l → FFT → Filter in Fourier space → IFFT → + bias → σ(·) → v_{l+1}
    │
    │       In detail:
    │       v_{l+1}(x) = σ( W_l × v_l(x) + F⁻¹(R_l × F(v_l))(x) )
    │
    │       R_l = learnable filter in Fourier space (truncated modes)
    │       W_l = local linear transform (like 1×1 conv)
    │       σ  = GeLU activation
    │
    ├─→ Projection: Q(v_L) → output function
    │
    └─→ Output function: f(x) (e.g., reconstructed image)

Key advantage: Resolution-invariant — train on 64×64, infer on 256×256
Complexity: O(N log N) per layer (FFT), vs. O(N²) for attention
```

### DeepONet (Deep Operator Network)

```
Branch network: Encodes input function (measurement)
    u(x₁), u(x₂), ..., u(x_m) → MLP → [b₁, b₂, ..., b_p]

Trunk network: Encodes output coordinates
    (x, y) → MLP → [t₁, t₂, ..., t_p]

Output: G(u)(x, y) = Σ_k b_k × t_k + bias

Advantage: Evaluates output at ANY coordinate (continuous)
```

## 응용

### 위상 복원

```
Problem:  Recover complex wavefield from intensity-only measurements
          (phase problem in coherent diffraction imaging, ptychography)

PINN approach:
  - Network predicts amplitude A(r) and phase φ(r)
  - Forward model: Fresnel/Fraunhofer propagation
  - Loss: ||propagate(A×exp(iφ)) - I_measured||²
  - Constraint: positivity, support, known object features

Advantage over iterative methods (ER, HIO):
  - Implicit regularization from network architecture
  - Continuous representation (no pixelation artifacts)
  - Can incorporate multiple physics constraints simultaneously
```

### 물질 사전 정보를 활용한 단층촬영 재구성

```
Standard CT:  Reconstruct µ(x,y,z) from projections only
PINN-CT:      Reconstruct µ(x,y,z) from projections + physics

Additional physics constraints:
  - Known material attenuation coefficients (e.g., water, calcium, air)
  - Segmentation priors (discrete material types)
  - Mass conservation during in-situ experiments
  - Beer-Lambert law for polychromatic beams

Result: More accurate reconstruction from fewer projections
```

### X-ray 형광(XRF) 단층촬영

```
Problem:  Reconstruct 3D elemental distributions from XRF projections
          Self-absorption complicates the forward model

PINN approach:
  - Network predicts element concentrations c_k(x,y,z)
  - Forward model includes:
    × Excitation beam attenuation (Beer-Lambert)
    × Fluorescence emission
    × Fluorescence self-absorption (path to detector)
  - All physics in the loss function
  - Jointly reconstructs all elements with correct self-absorption
```

## 학습 전략

### 자기 지도 학습 (정답 데이터 불필요)

```
PINNs can be trained WITHOUT ground truth reconstructions:
  1. Randomly sample coordinate points (x, y, z)
  2. Evaluate network: µ = f_θ(x, y, z)
  3. Compute line integrals through network (differentiable)
  4. Compare with measured projections
  5. Backpropagate through both network AND forward model

This is self-supervised: the physics model provides the supervision signal.
```

### 학습 세부사항

- **신경망**: 작업에 따라 MLP(4-8 레이어, 256-512 뉴런) 또는 CNN
- **옵티마이저**: Adam (lr=1×10⁻³, 코사인 어닐링 적용)
- **물리 손실 가중치**: 학습 중 점진적으로 증가 (커리큘럼 방식)
- **좌표 샘플링**: 배치당 4096-16384개의 무작위 점
- **학습 시간**: 재구성당 10분 - 2시간 (GPU)
- **사전 학습 불필요**: 인스턴스별로 최적화 (INR과 유사)

## 정량적 성능

| 방법 | 희소 뷰 CT (90 views) | 위상 복원 (CDI) | XRF 단층촬영 |
|--------|--------------------------|----------------------|----------------|
| **FBP / ER** | 26.2 dB | 0.82 (correlation) | N/A (ignores self-abs) |
| **SIRT / HIO** | 29.1 dB | 0.91 | 0.85 (correlation) |
| **CNN (supervised)** | 32.4 dB | 0.95 | 0.92 |
| **PINN** | **31.8 dB** | **0.96** | **0.95** |
| **FNO** | **33.1 dB** | **0.97** | **0.94** |

*PINNs는 순방향 모델 통합이 가장 큰 이점을 제공하는 물리 중심 문제(위상 복원, 자기 흡수가 있는 XRF)에서 뛰어난 성능을 보입니다. FNO는 유사한 문제의 데이터셋으로 학습한 후 높은 처리량을 달성합니다.*

## 강점

1. **데이터 효율적**: 단일 측정만으로 재구성 가능 (학습 데이터셋 불필요)
2. **물리적 일관성**: 솔루션이 구조적으로 지배 방정식을 만족
3. **유연한 순방향 모델**: 미분 가능한 어떤 물리 모델도 통합 가능
4. **학습 쌍 불필요**: 물리 손실을 통한 자기 지도 학습
5. **연속 표현**: 임의 해상도 출력 (좌표 신경망의 경우)
6. **복잡한 물리 처리**: 자기 흡수, 다중 산란, 다색 효과 처리

## 한계점

1. **느린 최적화**: 인스턴스별 학습이 분에서 시간 단위 소요
2. **순방향 모델 필요**: 미분 가능한 물리 구현이 있어야 함
3. **하이퍼파라미터 민감성**: 물리/데이터 손실 균형이 매우 중요
4. **알려진 물리에 한정**: 알려지지 않은 시스템적 오류는 보정 불가
5. **스펙트럴 편향**: MLP는 저주파를 먼저 학습 (세밀한 디테일을 놓칠 수 있음)
6. **확장성**: 큰 3D 볼륨은 상당한 GPU 메모리를 요구

## 코드 예시

```python
import torch
import torch.nn as nn
import numpy as np

class PhysicsInformedReconstructor(nn.Module):
    """PINN for tomographic reconstruction with physics constraints."""

    def __init__(self, hidden_dim=256, n_layers=6, n_frequencies=10):
        super().__init__()
        # Positional encoding
        self.n_freq = n_frequencies
        input_dim = 2 * (2 * n_frequencies + 1)  # 2D: (x, y) encoded

        layers = [nn.Linear(input_dim, hidden_dim), nn.SiLU()]
        for _ in range(n_layers - 2):
            layers += [nn.Linear(hidden_dim, hidden_dim), nn.SiLU()]
        layers += [nn.Linear(hidden_dim, 1), nn.Softplus()]  # positive attenuation

        self.network = nn.Sequential(*layers)

    def positional_encoding(self, coords):
        """Fourier feature encoding for coordinates."""
        encodings = [coords]
        freq_bands = 2.0 ** torch.arange(self.n_freq, device=coords.device)
        for freq in freq_bands:
            encodings.append(torch.sin(freq * np.pi * coords))
            encodings.append(torch.cos(freq * np.pi * coords))
        return torch.cat(encodings, dim=-1)

    def forward(self, coords):
        """Predict attenuation at (x, y) coordinates."""
        encoded = self.positional_encoding(coords)
        return self.network(encoded)


def compute_line_integral(model, angle, n_rays=256, n_samples=256, device='cuda'):
    """Compute projection at given angle through the PINN volume.

    Differentiable line integral for backpropagation through the physics model.
    """
    # Ray geometry
    t = torch.linspace(-1, 1, n_samples, device=device)
    s = torch.linspace(-1, 1, n_rays, device=device)

    cos_a, sin_a = torch.cos(angle), torch.sin(angle)

    projections = []
    for si in s:
        # Points along ray at offset si, angle `angle`
        x = si * cos_a - t * sin_a
        y = si * sin_a + t * cos_a
        coords = torch.stack([x, y], dim=-1)  # (n_samples, 2)

        # Query attenuation values (differentiable)
        mu = model(coords).squeeze(-1)  # (n_samples,)

        # Numerical integration (trapezoidal rule)
        dt = 2.0 / n_samples
        line_integral = torch.sum(mu) * dt
        projections.append(line_integral)

    return torch.stack(projections)


def train_pinn_ct(model, sinogram, angles, n_iterations=2000, lr=1e-3):
    """Train PINN for CT reconstruction using physics-based loss.

    Args:
        model: PhysicsInformedReconstructor
        sinogram: Measured projections (n_angles, n_rays)
        angles: Projection angles in radians
        n_iterations: Training iterations
        lr: Learning rate
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, n_iterations)
    device = next(model.parameters()).device

    sinogram_tensor = torch.tensor(sinogram, device=device, dtype=torch.float32)

    for iteration in range(n_iterations):
        optimizer.zero_grad()

        # Physics loss: projection consistency
        physics_loss = 0
        for i, angle in enumerate(angles):
            angle_tensor = torch.tensor(angle, device=device, dtype=torch.float32)
            pred_proj = compute_line_integral(model, angle_tensor,
                                              n_rays=sinogram.shape[1],
                                              device=device)
            physics_loss += torch.mean((pred_proj - sinogram_tensor[i]) ** 2)
        physics_loss /= len(angles)

        # Regularization: total variation on reconstruction
        coords = torch.rand(4096, 2, device=device) * 2 - 1
        coords.requires_grad_(True)
        mu = model(coords)
        grad_mu = torch.autograd.grad(mu.sum(), coords, create_graph=True)[0]
        tv_loss = torch.mean(torch.abs(grad_mu))

        # Total loss
        loss = physics_loss + 1e-4 * tv_loss
        loss.backward()
        optimizer.step()
        scheduler.step()

        if (iteration + 1) % 200 == 0:
            print(f"Iter {iteration+1}/{n_iterations}, "
                  f"Physics: {physics_loss.item():.6f}, TV: {tv_loss.item():.6f}")

    return model
```

### 학습 기반 CT 재구성을 위한 FNO

```python
import torch
import torch.nn as nn
import torch.fft

class FourierLayer(nn.Module):
    """Single Fourier Neural Operator layer."""

    def __init__(self, channels, modes):
        super().__init__()
        self.modes = modes
        self.channels = channels

        # Learnable Fourier coefficients (complex)
        self.weights = nn.Parameter(
            torch.randn(channels, channels, modes, modes, 2) * 0.02
        )
        # Local linear transform
        self.linear = nn.Conv2d(channels, channels, 1)

    def forward(self, x):
        # x: (batch, channels, H, W)
        batch_size = x.shape[0]

        # FFT
        x_ft = torch.fft.rfft2(x)

        # Multiply in Fourier space (truncated modes)
        weights_complex = torch.view_as_complex(self.weights)
        out_ft = torch.zeros_like(x_ft)
        out_ft[:, :, :self.modes, :self.modes] = torch.einsum(
            "bixy,ioxy->boxy",
            x_ft[:, :, :self.modes, :self.modes],
            weights_complex,
        )

        # IFFT
        x_fourier = torch.fft.irfft2(out_ft, s=(x.shape[-2], x.shape[-1]))

        # Add local transform
        x_local = self.linear(x)

        return nn.functional.gelu(x_fourier + x_local)


class FNOReconstructor(nn.Module):
    """Fourier Neural Operator for sinogram-to-image reconstruction."""

    def __init__(self, modes=16, width=64, n_layers=4):
        super().__init__()
        self.lift = nn.Conv2d(1, width, 1)
        self.layers = nn.ModuleList([
            FourierLayer(width, modes) for _ in range(n_layers)
        ])
        self.project = nn.Sequential(
            nn.Conv2d(width, width, 1),
            nn.GELU(),
            nn.Conv2d(width, 1, 1),
        )

    def forward(self, sinogram):
        """Map sinogram → reconstructed image."""
        x = self.lift(sinogram)
        for layer in self.layers:
            x = layer(x)
        return self.project(x)
```

## APS BER 프로그램과의 관련성

### 핵심 응용

- **위상 복원**: 26-ID에서 물리 제약 기반 역산을 통한 결맞음 회절 이미징
- **XRF 단층촬영**: 2-ID에서 미분 가능한 물리 모델을 사용한 자기 흡수 보정
- **In-situ CT**: 2-BM에서 반응 모니터링을 위한 물질 보존 제약
- **다중 모달 재구성**: 흡수 + 위상 CT 결합을 위한 통합 물리 모델

### 빔라인 통합

- **26-ID**: PINN 기반 연속 표현을 사용한 타이코그래피 위상 복원
- **2-ID**: 신경망에 자기 흡수 물리가 임베딩된 XRF 단층촬영
- **2-BM**: 사전 학습된 FNO 모델을 사용한 빠른 단층촬영 재구성
- **1-ID**: 결정학적 물리 제약을 갖는 HEDM 재구성
- GPU 집약적인 인스턴스별 최적화를 위한 ALCF의 컴퓨팅 지원

### APS-U를 위한 이점

```
APS-U produces:
  - Higher coherence → more phase-sensitive measurements → PINNs excel
  - Smaller beams → faster scanning → need fast FNO inference
  - Multi-modal data → PINNs naturally combine multiple physics models

PINNs + Neural Operators bridge the gap between:
  classical physics-based methods (accurate but slow)
  and pure ML methods (fast but may violate physics)
```

## 참고문헌

1. Li, Z., et al. "Fourier Neural Operator for Parametric Partial Differential
   Equations." ICLR 2021. DOI: [10.48550/arXiv.2010.08895](https://doi.org/10.48550/arXiv.2010.08895)
2. Raissi, M., Perdikaris, P., Karniadakis, G.E. "Physics-informed neural networks:
   A deep learning framework for solving forward and inverse problems involving
   nonlinear partial differential equations." J. Comp. Physics 2019.
   DOI: [10.1016/j.jcp.2018.10.045](https://doi.org/10.1016/j.jcp.2018.10.045)
3. Lu, L., et al. "DeepONet: Learning nonlinear operators for identifying differential
   equations based on the universal approximation theorem of operators."
   Nature Machine Intelligence 2021. DOI: [10.1038/s42256-021-00302-5](https://doi.org/10.1038/s42256-021-00302-5)
4. Sun, Y., et al. "Physics-informed deep learning for computational imaging."
   Optica 2022.
