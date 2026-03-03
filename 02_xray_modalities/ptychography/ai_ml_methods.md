# 타이코그래피를 위한 AI/ML 방법

## 개요

타이코그래피를 위한 AI/ML 방법은 위상 복원 가속화, 실시간 복원 구현, 희소 데이터 처리 및 이미지 품질 향상에 중점을 둡니다. 잘 정의된 순방향 모델(forward model)과 대용량 데이터의 조합은 타이코그래피를 딥러닝(deep learning) 접근법의 이상적인 후보로 만듭니다.

## ML 문제 분류

| 문제 | 유형 | 입력 | 출력 |
|---------|------|-------|--------|
| 위상 복원(phase retrieval) | 역문제(inverse problem) | 회절 패턴 | 복소 이미지 |
| 실시간 복원 | 추론(inference) | 스트리밍 패턴 | 실시간 이미지 업데이트 |
| 희소 복원(sparse reconstruction) | 역문제 | 과소 샘플링 데이터 | 전체 이미지 |
| 분해능 향상 | 이미지-이미지 변환 | 저분해능 | 고분해능 |
| 위치 보정 | 회귀(regression) | 패턴 + 위치 | 보정된 위치 |
| Probe 추정 | 회귀 | 패턴 | Probe 함수 |

## PtychoNet: CNN 기반 위상 복원

**참조**: Guan et al. (2019)

### 아키텍처
```
Input: Single diffraction pattern (256×256)
    │
    ├─→ Encoder (ResNet-style blocks)
    │       Conv → BN → ReLU → Conv → BN → ReLU + skip
    │       Progressively reduces spatial dimensions
    │
    ├─→ Bottleneck (dense features)
    │
    ├─→ Decoder (transpose convolutions)
    │       Progressively increases spatial dimensions
    │
    └─→ Output: Phase + Amplitude images (256×256 each)
```

### 주요 결과
- **속도**: 반복적 ePIE보다 90% 빠름 (100회 이상 반복 대비 단일 순전파)
- **품질**: 훈련된 시료 유형에서 반복법과 비견할 만한 수준
- **한계**: 미지의 시료 유형에 대한 일반화에는 재훈련 필요

### 훈련 전략
- (회절 패턴, 반복법에 의한 정답 복원) 쌍으로 훈련
- 데이터 증강(data augmentation): 회전, 이동, 잡음 추가
- 손실 함수(loss): 위상 + 진폭에 대한 MSE, 위상 랩핑(phase wrapping) 처리 포함

## AI@Edge: 실시간 타이코그래피

**참조**: Babu et al., Nature Communications (2023)

### 혁신
ML 추론을 빔라인 엣지 컴퓨팅(edge computing) 하드웨어에 직접 배포하여
**2 kHz 프레임 속도의 실시간 타이코그래피 이미징** 구현.

### 아키텍처
- 엣지 배포에 최적화된 경량 CNN (FPGA 또는 GPU)
- 스트리밍 추론: 각 회절 패턴이 도착하는 대로 처리
- 점진적 업데이트: 더 많은 위치가 측정됨에 따라 복원을 정밀화

### 파이프라인
```
Detector (2 kHz) → Edge GPU/FPGA → CNN Inference → Live Reconstruction
    │                                                      │
    └── 0.5 ms/frame ──────────────────────────── Display update
```

### APS BER 프로그램에 대한 의의
- 실험 중 피드백 가능 (사후 분석이 아닌)
- 실험자가 실시간으로 복원 품질 확인 가능
- 스캔 파라미터를 즉시 중단하거나 조정 가능
- APS-U 데이터 전송률에 필수적

## 암시적 신경 표현(Implicit Neural Representations, INR)

### 개념
타이코그래피 객체를 신경망으로 매개변수화된 연속 함수로 표현합니다:

```
f_θ(x, y) → (amplitude, phase)    for 2D
f_θ(x, y, z) → (amplitude, phase)  for 3D ptycho-tomo
f_θ(x, y, z, t) → (amplitude, phase)  for dynamic 4D
```

### 아키텍처
- **SIREN**: 부드러운 고주파 표현을 위한 정현파 활성화 함수(sinusoidal activation functions)
- **위치 인코딩(positional encoding)**: 더 나은 고주파 학습을 위한 푸리에 특징 매핑(Fourier feature mapping)

### 장점
- **연속적**: 이산 격자(discrete grid)에 의해 분해능이 제한되지 않음
- **컴팩트**: 전체 볼륨이 아닌 모델 파라미터를 저장
- **동적**: 시변(time-varying) 시료로의 자연스러운 확장
- **물리 기반(physics-informed)**: 순방향 모델을 물리적 제약으로 포함 가능

### 과제
- 훈련 시간: 복원당 수 분에서 수 시간
- 현재 중간 수준의 분해능(~512×512)으로 제한
- 하이퍼파라미터 민감성

## 희소 타이코그래피(Sparse Ptychography)

### 문제
복원 품질을 유지하면서 데이터 수집 속도를 높이기 위해 스캔 위치 수를 줄이는 것.

### ML 접근법

1. **압축 센싱(compressed sensing) + DL**:
   - 중첩 위치를 줄여 수집 (60-80% 대신 30-50%)
   - 훈련된 CNN으로 누락된 정보를 보완
   - 데이터 수집 2-3배 속도 향상

2. **적응형 스캔(adaptive scanning)**:
   - 조대한 격자로 시작 → 복원 → 특징 식별 → 국소적으로 스캔 정밀화
   - ML이 추가 측정이 가장 유익한 위치를 예측
   - 시료 구조에 맞춤화된 비균일 스캔 패턴

3. **전이 학습(transfer learning)**:
   - 유사한 시료 유형으로 사전 훈련
   - 같은 종류의 새 시료에 대해 더 적은 측정으로 충분

## 위치 보정(Position Correction)

### 문제
타이코그래피는 스캔 위치 오차에 매우 민감합니다 (nm 정밀도 필요).

### ML 해결책
- 회절 패턴 특징으로부터 위치 보정값을 예측하도록 CNN 훈련
- 입력: 측정된 패턴 + 공칭 위치
- 출력: 보정된 위치 오프셋 (Δx, Δy)
- 전처리 단계로 복원 파이프라인에 통합

## Probe 복원

### 전통적 방법
ePIE 및 유사 알고리즘이 probe와 object를 동시에 복원합니다.

### ML 강화 방법
- CNN이 처음 몇 개의 회절 패턴으로부터 probe 함수를 예측
- 더 나은 초기화를 제공 → 반복법의 빠른 수렴
- 다중 모드 분해(multi-mode decomposition)를 통해 부분 결맞음(partial coherence) 모델링 가능

## 소프트웨어 도구

| 도구 | 언어 | GPU | 방법 |
|------|----------|-----|--------|
| **PtychoShelves** | MATLAB/GPU | Yes | ePIE, DM, LSQ-ML |
| **PyNX** | Python/GPU | Yes | 다양한 반복 알고리즘 |
| **Tike** | Python/CuPy | Yes | APS 개발, 타이코 + 토모 |
| **PtyPy** | Python | Yes | 유연한 혼합 상태 지원 |
| **PtychoNN** | Python/PyTorch | Yes | CNN 기반 (AI@Edge) |

## 현재 한계

1. **일반화**: 훈련된 모델은 시료 유형에 특화됨
2. **훈련 데이터**: 정답(ground truth)으로 반복법 복원이 필요
3. **3D 확장**: 타이코-토모그래피를 위한 DL은 아직 초기 단계
4. **부분 결맞음(partial coherence)**: 혼합 상태(mixed-state) 조명의 ML 처리에 개선 필요
5. **정량적 정확도**: DL 복원이 정량적 위상 값을 보존하지 못할 수 있음

## 개선 기회

1. **자기 지도 훈련(self-supervised training)**: 물리 기반 손실 함수 사용 (측정 데이터와의 일관성)
2. **파운데이션 모델(foundation models)**: 여러 시설의 대규모 타이코그래피 데이터셋으로 사전 훈련
3. **하이브리드 접근법**: DL 초기화 + 소수의 반복 정밀화 단계
4. **다중 모달(multi-modal)**: 타이코그래피 + XRF 결합 복원
5. **4D 타이코-토모**: DL 가속 동적 3D 이미징
6. **불확실성 맵(uncertainty maps)**: 픽셀별 복원 신뢰도 제공
