# 동적 토모그래피를 위한 암시적 신경 표현(Implicit Neural Representations)

## 개념

**암시적 신경 표현(Implicit Neural Representations, INR)**은 신경망의 가중치를 사용하여 연속 함수(예: 3D 볼륨 또는 4D 시공간 필드)를 표현합니다. 이산 복셀 값을 저장하는 대신, 네트워크가 좌표를 값으로 매핑합니다:

```
표준 표현: Volume V[i, j, k]  (이산 3D 배열)
INR 표현:  f_θ(x, y, z) → value  (연속 함수)
```

## 아키텍처

### 좌표 네트워크(Coordinate Network) (MLP)

```
입력: (x, y, z) 좌표
    │
    ├─→ 위치 인코딩(Positional Encoding)
    │       γ(x) = [sin(2⁰πx), cos(2⁰πx), sin(2¹πx), cos(2¹πx), ...,
    │               sin(2^(L-1)πx), cos(2^(L-1)πx)]
    │       저차원 입력을 고차원 특징 공간으로 매핑
    │       고주파 콘텐츠 학습을 가능하게 함
    │
    ├─→ MLP (6-8 층, 각 256-512 뉴런)
    │       FC → ReLU → FC → ReLU → ... → FC
    │       (또는 SIREN: FC → sin → FC → sin → ...)
    │
    └─→ 출력: 감쇠값 µ(x, y, z)
```

### SIREN (정현파 표현 네트워크, Sinusoidal Representation Networks)

ReLU 대신 정현파 활성화 함수를 사용:
```
φ(x) = sin(ω₀ × Wx + b)

여기서 ω₀는 주파수 매개변수 (일반적으로 30)
```

**장점**: 고주파 디테일을 가진 연속적이고 매끄러운 함수의 자연스러운 표현.

## 동적 토모그래피(4D)에의 적용

### 문제

동적(4D) 토모그래피에서 시료는 스캔 중 변합니다:
- 전통적: 모든 각도 수집 → 단일 시간 재구성 (정적 가정)
- 현실: 시료가 진화 → 재구성에 동작 아티팩트(Motion Artifacts) 발생

### INR 해결 방법

좌표 네트워크를 시간을 포함하도록 확장:

```
f_θ(x, y, z, t) → µ(x, y, z, t)

네트워크가 4D 시공간 볼륨을 연속 함수로 표현.
```

### 학습 (물리 정보 기반, Physics-Informed)

정답(Ground Truth)을 사용한 지도 학습 대신, 측정된 투영과 일치하도록 네트워크를 최적화:

```python
# 순방향 모델:
# 각도 θ_i, 시간 t_i에서 측정된 투영:
# p_measured(θ_i, t_i) = ∫ f_θ(ray(θ_i, s), t_i) ds
#                         (INR 볼륨을 통한 선적분)

# 손실: 측정된 투영과의 일관성
loss = Σ_i ||p_measured(θ_i, t_i) - ∫ f_θ(ray(θ_i, s), t_i) ds||²

# + 정규화 항:
# - 시간적 평활성: ||∂f_θ/∂t||² (급격한 변화에 패널티)
# - 공간적 평활성: ||∇f_θ||² (전체 변이, Total Variation)
# - 희소성: ||f_θ||₁ (해당되는 경우)
```

### 학습 파이프라인

```
서로 다른 (각도, 시간) 쌍에서의 투영
    │
    ├─→ 투영의 무작위 배치를 샘플링
    │
    ├─→ 각 투영에 대해:
    │       ├── INR 볼륨을 통과하는 광선(Ray)을 따라 포인트 샘플링
    │       ├── 샘플링된 포인트에서 f_θ(x, y, z, t) 쿼리
    │       ├── 수치 적분 (선적분)
    │       └── 측정된 투영 값과 비교
    │
    ├─→ 손실 계산 (데이터 충실도 + 정규화)
    │
    └─→ 역전파 및 네트워크 가중치 θ 업데이트
```

## 이산 방법 대비 장점

| 측면 | 이산 (복셀 격자) | INR (신경망) |
|--------|----------------------|---------------------|
| **해상도** | 격자에 의해 고정 | 연속 (임의) |
| **메모리** | 3D 볼륨에 대해 O(N³) | O(매개변수) ≈ 수 MB |
| **시간 모델링** | 시간당 별도 볼륨 | 매끄러운 시간 보간 |
| **누락 각도** | 아티팩트 | 암시적 정규화 |
| **보간** | 삼선형(Trilinear) (블록형) | 매끄럽고, 학습된 |
| **초해상도** | 불가능 | 임의 해상도에서 자연스러운 쿼리 |

## 과제

### 1. 학습 시간
- 볼륨별로 최적화 필요 (수분에서 수시간)
- 사전 학습된 모델이 아님 — 학습이 곧 재구성
- GPU 집약적 (다수의 CUDA 코어 필요)

### 2. 제한된 해상도
- 현재 MLP 기반 INR은 약 512³ 유효 해상도로 제한
- 더 높은 해상도는 더 큰 네트워크 또는 해시 기반 표현이 필요
- Instant-NGP (해시 격자)가 이를 부분적으로 해결

### 3. 스펙트럼 편향(Spectral Bias)
- MLP는 자연스럽게 저주파 콘텐츠를 먼저 학습
- 위치 인코딩과 SIREN이 도움이 되지만 완전히 해결하지는 못함
- 점진적 학습: 저주파에서 시작하여 시간에 따라 고주파 추가

### 4. 하이퍼파라미터 민감성
- 네트워크 아키텍처 (깊이, 너비, 활성화 함수)
- 위치 인코딩 주파수 범위
- 정규화 가중치
- 학습률 스케줄

## 토모그래피를 위한 Instant-NGP

**NVIDIA Instant-NGP**는 위치 인코딩 대신 다중 해상도 해시 테이블을 사용합니다:

```
입력: (x, y, z)
    │
    ├─→ 다중 해상도 해시 인코딩
    │       각 해상도 레벨에 대해:
    │       └── 복셀 코너 해싱 → 학습된 특징 조회 → 보간
    │
    ├─→ 소형 MLP (2 층)
    │
    └─→ 출력: 값

학습 시간: 초에서 분 (표준 INR의 수시간 대비)
```

## 예시: 4D 토양 습윤 실험

```
실험: 토양 기둥으로의 물 침투
    - 스캔: 연속 회전, 180° 회전당 0.5초
    - 지속 시간: 30분
    - 과제: 각 회전 중 수분 전선이 이동

전통적 접근법:
    - 3600개의 개별 재구성 (회전당 하나)
    - 각각 물 이동으로 인한 동작 아티팩트를 가짐

INR 접근법:
    - 단일 연속 4D 표현 f_θ(x, y, z, t)
    - 각 투영이 정확한 타임스탬프를 사용
    - 물 분포의 매끄러운 시간적 진화
    - 시각화를 위해 임의의 시점에서 쿼리
```

## 구현 스케치

```python
import torch
import torch.nn as nn
import numpy as np

class PositionalEncoding(nn.Module):
    def __init__(self, in_dim, n_frequencies=10):
        super().__init__()
        self.n_freq = n_frequencies
        # 주파수 대역: 2^0, 2^1, ..., 2^(L-1)
        self.freq_bands = 2.0 ** torch.arange(n_frequencies)

    def forward(self, x):
        # x: (batch, in_dim)
        encodings = [x]
        for freq in self.freq_bands:
            encodings.append(torch.sin(freq * np.pi * x))
            encodings.append(torch.cos(freq * np.pi * x))
        return torch.cat(encodings, dim=-1)
        # 출력: (batch, in_dim * (2*n_freq + 1))

class DynamicINR(nn.Module):
    """동적 토모그래피를 위한 4D INR: (x,y,z,t) -> 감쇠값."""

    def __init__(self, n_frequencies=10, hidden_dim=256, n_layers=6):
        super().__init__()
        in_dim = 4  # x, y, z, t
        encoded_dim = in_dim * (2 * n_frequencies + 1)

        self.pe = PositionalEncoding(in_dim, n_frequencies)

        layers = [nn.Linear(encoded_dim, hidden_dim), nn.ReLU()]
        for _ in range(n_layers - 2):
            layers += [nn.Linear(hidden_dim, hidden_dim), nn.ReLU()]
        layers += [nn.Linear(hidden_dim, 1), nn.Softplus()]  # 양수 출력

        self.mlp = nn.Sequential(*layers)

    def forward(self, coords):
        # coords: (batch, 4) — (x, y, z, t) [-1, 1]로 정규화
        encoded = self.pe(coords)
        return self.mlp(encoded)  # (batch, 1) 감쇠값
```

## APS BER 프로그램과의 관련성

### 주요 응용
- **원위치(In-situ) 토모그래피**: 습윤/건조, 반응 전선, 뿌리 성장 추적
- **선량 감소**: INR 정규화를 사용하여 더 적은 투영에서 재구성
- **임의 시간 쿼리**: 임의 시점에서 구조적 변화를 시각화
- **다중 스케일**: 동일 INR을 서로 다른 공간 해상도에서 쿼리

### 빔라인 통합
- **2-BM-A**: 빠른 원위치 토모그래피 → 시간 동역학을 위한 4D INR
- **7-BM-B**: 시간 분해 연구 → 연속적 시간 표현
- 대규모 INR 모델 학습을 위한 ALCF의 계산 지원
