# TomoGAN: 방사광 토모그래피를 위한 GAN 기반 노이즈 제거

**참고문헌**: Liu et al., J. Opt. Soc. Am. A (2020)

## 아키텍처

TomoGAN은 U-Net 생성기(Generator)와 PatchGAN 판별기(Discriminator)를 갖춘 조건부 GAN(Conditional GAN) 아키텍처를 사용합니다.

### 생성기(Generator) (U-Net)

```
노이즈 입력 슬라이스 (1ch, 256×256)
    │
    ▼ [인코더]
    Conv→IN→LeakyReLU (64)  ───────────────────────────┐
    Conv→IN→LeakyReLU (128) ────────────────────┐       │
    Conv→IN→LeakyReLU (256) ─────────────┐       │       │
    Conv→IN→LeakyReLU (512) ──────┐       │       │       │
    │                              │       │       │       │
    ▼ [병목층(Bottleneck)]          │       │       │       │
    Conv→IN→LeakyReLU (512)       │       │       │       │
    │                              │       │       │       │
    ▼ [디코더]                      │       │       │       │
    TransConv→IN→ReLU + skip ─────┘       │       │       │
    TransConv→IN→ReLU + skip ─────────────┘       │       │
    TransConv→IN→ReLU + skip ─────────────────────┘       │
    TransConv→IN→ReLU + skip ─────────────────────────────┘
    │
    ▼
    Conv→Tanh → 노이즈 제거된 출력 (1ch, 256×256)

IN = 인스턴스 정규화(Instance Normalization)
```

### 판별기(Discriminator) (PatchGAN)

```
입력: [실제/가짜 이미지, 노이즈 입력] 연결 (2ch)
    │
    Conv→LeakyReLU (64)
    Conv→IN→LeakyReLU (128)
    Conv→IN→LeakyReLU (256)
    Conv→IN→LeakyReLU (512)
    │
    Conv→Sigmoid → 패치별 실제/가짜 확률 (16×16)
```

PatchGAN은 각 16×16 패치를 실제 또는 가짜로 분류하여 지역적 텍스처 사실감을 촉진합니다.

## 손실 함수(Loss Function)

총 생성기 손실은 세 가지 구성 요소를 결합합니다:

```
L_total = λ₁ × L_L1 + λ₂ × L_adversarial + λ₃ × L_perceptual

여기서:
  L_L1 = ||G(noisy) - clean||₁               (픽셀 단위 재구성)
  L_adv = -log(D(G(noisy), noisy))            (판별기를 속임)
  L_perc = ||VGG(G(noisy)) - VGG(clean)||₂   (특징 매칭)

일반적인 가중치: λ₁ = 100, λ₂ = 1, λ₃ = 10
```

### 각 손실의 역할
- **L1**: 픽셀 단위 정확도를 보장하고 색상 변이를 방지
- **적대적(Adversarial)**: 선명하고 사실적인 텍스처를 생성 (흐려짐 방지)
- **지각적(Perceptual)**: 구조적 특징과 상위 수준의 유사성을 보존

## 학습 전략

### 데이터 준비
```
전체 선량 스캔 → 재구성 (고품질) → 깨끗한 목표
저선량 스캔  → 재구성 (노이즈) → 노이즈 입력

또는: 전체 선량 투영을 서브샘플링하여 저선량을 시뮬레이션
```

### 학습 세부 사항
- **패치 크기**: 256×256 (전체 슬라이스에서 무작위 크롭)
- **배치 크기**: 4-16
- **옵티마이저**: Adam (lr=2×10⁻⁴, β₁=0.5, β₂=0.999)
- **에포크 수**: 100-200
- **증강**: 무작위 뒤집기, 회전, 강도 지터링(Jittering)
- **학습 시간**: 단일 GPU에서 약 12-24시간

### 대안: 인접 슬라이스 사용
```
입력: [slice_{n-1}, slice_n, slice_{n+1}]  (3 채널)
출력: 노이즈 제거된 slice_n (1 채널)
```
인접 슬라이스의 공간적 맥락을 사용하여 노이즈 제거를 보조합니다.

## 정량적 성능

| 지표 | 저선량 (노이즈) | 가우시안 필터 | NLM | TomoGAN |
|--------|-----------------|----------------|-----|---------|
| **PSNR (dB)** | 25.3 | 28.1 | 30.2 | **34.5** |
| **SSIM** | 0.72 | 0.81 | 0.88 | **0.95** |
| **NRMSE** | 0.118 | 0.078 | 0.051 | **0.029** |

*값은 대표적이며, 실제 성능은 데이터셋에 따라 달라집니다.*

## 강점

1. **지각적 품질**: GAN이 선명하고 사실적인 이미지를 생성 (흐려지지 않음)
2. **미세 디테일 보존**: 적대적 손실이 작은 특징의 평활화를 방지
3. **유연성**: 다양한 노이즈 수준 및 모달리티에서 작동
4. **선량 감소**: 이미지 품질을 유지하면서 4-10배 선량 감소 가능

## 한계

1. **모드 붕괴(Mode Collapse)**: GAN 학습 불안정성으로 반복적 아티팩트 생성 가능
2. **환각(Hallucination) 위험**: 생성기가 그럴듯하지만 비물리적인 특징을 생성할 수 있음
3. **학습 데이터 의존성**: 대응하는 저선량/전체 선량 쌍이 필요
4. **시료 특이성**: 한 시료 유형으로 학습된 모델이 일반화되지 않을 수 있음
5. **불확실성 없음**: 신뢰도 측정 없는 단일 출력

## 환각 완화(Hallucination Mitigation)

```python
# 전략 1: 잔차 학습
# 깨끗한 이미지가 아닌 노이즈를 예측하도록 학습
denoised = noisy_input - generator(noisy_input)

# 전략 2: 일관성 검사
# 노이즈 제거된 이미지를 순방향 모델(투영)을 통해 실행
# 측정된 투영과 비교
# 큰 불일치가 있는 영역을 플래그

# 전략 3: 앙상블 불확실성
# 여러 GAN을 학습하고 분산을 불확실성 맵으로 사용
```

## 코드 예제

```python
import torch
import torch.nn as nn

class TomoGANGenerator(nn.Module):
    """간소화된 TomoGAN 생성기 (U-Net 아키텍처)."""

    def __init__(self, in_ch=1, out_ch=1, base_filters=64):
        super().__init__()
        # 인코더
        self.enc1 = self._block(in_ch, base_filters)
        self.enc2 = self._block(base_filters, base_filters * 2)
        self.enc3 = self._block(base_filters * 2, base_filters * 4)
        self.enc4 = self._block(base_filters * 4, base_filters * 8)

        # 병목층
        self.bottleneck = self._block(base_filters * 8, base_filters * 8)

        # 디코더
        self.up4 = nn.ConvTranspose2d(base_filters * 8, base_filters * 8, 4, 2, 1)
        self.dec4 = self._block(base_filters * 16, base_filters * 4)
        self.up3 = nn.ConvTranspose2d(base_filters * 4, base_filters * 4, 4, 2, 1)
        self.dec3 = self._block(base_filters * 8, base_filters * 2)
        self.up2 = nn.ConvTranspose2d(base_filters * 2, base_filters * 2, 4, 2, 1)
        self.dec2 = self._block(base_filters * 4, base_filters)
        self.up1 = nn.ConvTranspose2d(base_filters, base_filters, 4, 2, 1)
        self.dec1 = self._block(base_filters * 2, base_filters)

        self.final = nn.Sequential(nn.Conv2d(base_filters, out_ch, 1), nn.Tanh())
        self.pool = nn.MaxPool2d(2)

    def _block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.InstanceNorm2d(out_ch),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.InstanceNorm2d(out_ch),
            nn.LeakyReLU(0.2, inplace=True),
        )

    def forward(self, x):
        e1 = self.enc1(x);     p1 = self.pool(e1)
        e2 = self.enc2(p1);    p2 = self.pool(e2)
        e3 = self.enc3(p2);    p3 = self.pool(e3)
        e4 = self.enc4(p3);    p4 = self.pool(e4)

        b = self.bottleneck(p4)

        d4 = self.dec4(torch.cat([self.up4(b), e4], 1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], 1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], 1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], 1))

        return self.final(d1)
```
