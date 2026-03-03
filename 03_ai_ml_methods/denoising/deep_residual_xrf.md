# XRF 해상도 향상을 위한 심층 잔차 네트워크(Deep Residual Networks)

**참고문헌**: npj Computational Materials (2023), DOI: 10.1038/s41524-023-00995-9

## 개념

단순한 노이즈 제거가 아닌, 이 접근 방식은 심층 잔차 네트워크(Deep Residual Networks)를 사용하여 X선 빔 프로브 크기에 의해 설정된 물리적 한계를 넘어 XRF 현미경 맵의 **유효 공간 해상도를 향상**시킵니다.

### 문제 정의

```
실제 원소 분포: f(x, y)     (무한 해상도)
측정된 XRF 맵: g(x, y) = f(x,y) * h(x,y) + n(x,y)

여기서:
  h(x,y) = 프로브/빔 프로파일 (점 확산 함수, Point Spread Function)
  n(x,y) = 측정 노이즈
  * = 합성곱(Convolution)

목표: g(x,y)에서 f(x,y)를 복원 — 역합성곱(Deconvolution) / 초해상도(Super-resolution)
```

### 왜 딥러닝인가?

전통적인 역합성곱(위너 필터, Richardson-Lucy)은 노이즈를 증폭합니다.
딥러닝은 노이즈를 억제하면서 동시에 역합성곱을 학습합니다.

## 방법

### 아키텍처: 심층 잔차 네트워크

```
입력: 저해상도 XRF 맵 (Ny, Nx)
    │
    ├─→ Conv3×3 → ReLU (64 필터)
    │
    ├─→ 잔차 블록(Residual Block) × N (일반적으로 16-20 블록)
    │       ┌──────────────────────┐
    │       │ Conv3×3 → BN → ReLU │
    │       │ Conv3×3 → BN        │
    │       │ + 스킵 연결          │
    │       └──────────────────────┘
    │
    ├─→ Conv3×3 (64 필터)
    │   + 전역 스킵 연결 (입력으로부터)
    │
    └─→ Conv3×3 (1 필터) → 향상된 해상도 맵
```

### 잔차 학습(Residual Learning)

네트워크는 저해상도와 고해상도 간의 **차이**를 학습합니다:
```
output = input + network(input)

네트워크는 전체 매핑이 아닌 잔차(고주파 세부 정보)만 학습하면 되므로
학습이 더 쉬워짐.
```

### 학습 데이터 생성

```
접근법 1: 쌍을 이루는 스캔
  - 고해상도 스캔 (50 nm 스텝) → 고해상도 정답(Ground Truth)
  - 저해상도 스캔 (200 nm 스텝) → 저해상도 입력
  - 쌍을 이루는 스캔의 패치로 네트워크 학습

접근법 2: 시뮬레이션된 열화
  - 사용 가능한 최고 해상도 스캔에서 시작
  - 추정된 프로브 프로파일로 합성곱 → 시뮬레이션된 저해상도
  - 현실적인 노이즈 모델 추가
  - (시뮬레이션 저해상도, 원본 고해상도) 쌍으로 학습
```

## 결과

### 해상도 향상

| 지표 | 처리 전 | 향상 후 | 개선 정도 |
|--------|--------|-------------------|-------------|
| **유효 해상도** | 200 nm | 80 nm | 2.5배 |
| **PSNR** | 기준값 | +6-8 dB | 상당한 개선 |
| **특징 가시성** | 흐린 세포소기관 | 구분된 세포하 구조 | 정성적 개선 |

### 주요 발견
- XRF 원소 맵에서 2-4배 유효 해상도 향상 실증
- 여러 원소에서 동시에 작동
- 원소 농도의 정량적 정확도 유지
- 프로브 크기 이하의 특징 식별 가능

## 강점

1. **물리적 한계를 초월**: 빔 크기보다 더 나은 해상도 달성
2. **다원소**: 단일 네트워크가 모든 원소 채널을 향상
3. **정량적**: 농도 정확도 유지
4. **빠른 추론**: 학습 후 실시간 처리 가능
5. **잔차 학습**: 안정적인 학습, 저주파 콘텐츠 보존

## 한계

1. **학습 데이터**: 학습을 위해 쌍을 이루는 저해상도/고해상도 스캔이 필요
2. **시료 특이성**: 매우 다른 시료 유형에 대해 재학습이 필요할 수 있음
3. **이론적 한계**: 노이즈 플로어(Noise Floor) 이하의 정보를 진정으로 복원할 수 없음
4. **프로브 모델**: 성능이 프로브 특성화의 정확도에 의존
5. **검증**: 독립적 측정 없이 해상도 주장을 검증하기 어려움

## APS BER 프로그램에의 적용

### 잠재적 영향
- **2-ID-D 나노프로브**: 100-200 nm 맵을 100 nm 이하 유효 해상도로 향상
- **2-ID-E 마이크로프로브**: 1 µm 맵을 서브마이크론(sub-µm) 해상도로 향상
- **8-BM-B**: 처리량을 유지하면서 대면적 맵 향상

### 워크플로우 통합
```
저해상도 XRF 스캔 (빠름, 넓은 영역)
    │
    ├─→ DL 해상도 향상
    │       입력: 저해상도 맵 (1-5 µm 스텝)
    │       출력: 향상된 맵 (~0.5 µm 유효)
    │
    ├─→ ROI-Finder (향상된 맵에서)
    │       더 나은 분할 및 클러스터링
    │
    └─→ 표적화된 고해상도 스캔 (선택된 ROI에서만)
            전체 해상도, 작은 영역
```

이 워크플로우는 데이터 품질을 유지하면서 빔 타임을 크게 줄일 수 있습니다.

## 코드 스케치

```python
import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.BatchNorm2d(channels),
        )

    def forward(self, x):
        return x + self.block(x)

class XRFResolutionEnhancer(nn.Module):
    def __init__(self, in_channels=1, n_blocks=16, n_filters=64):
        super().__init__()
        self.input_conv = nn.Sequential(
            nn.Conv2d(in_channels, n_filters, 3, padding=1),
            nn.ReLU(inplace=True)
        )
        self.res_blocks = nn.Sequential(
            *[ResidualBlock(n_filters) for _ in range(n_blocks)]
        )
        self.mid_conv = nn.Conv2d(n_filters, n_filters, 3, padding=1)
        self.output_conv = nn.Conv2d(n_filters, in_channels, 3, padding=1)

    def forward(self, x):
        initial = self.input_conv(x)
        residual = self.mid_conv(self.res_blocks(initial))
        enhanced = self.output_conv(initial + residual)
        return x + enhanced  # 전역 잔차 연결
```
