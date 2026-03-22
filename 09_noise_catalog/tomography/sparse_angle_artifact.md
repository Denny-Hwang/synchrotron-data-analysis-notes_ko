# 희소 각도 아티팩트(Sparse-Angle Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 계산(Computational) |
| **심각도** | 주요(Major) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 보통(Moderate) |

## 시각적 예시

![희소 각도 vs 전체 각도 FBP 재구성 비교](../images/sparse_angle_before_after.png)

> **이미지 출처:** Sarepy 중성자 CT 데이터 — 희소 투영의 FBP 재구성(스트릭 아티팩트 표시) vs. 링 제거가 적용된 전체 360° 수집.

## 설명

희소 각도 아티팩트는 재구성 이미지 위에 중첩된 스트릭 및 별 모양 패턴으로 나타나며, 스트릭은 누락된 투영 각도에 해당하는 방향을 따릅니다. 재구성 이미지는 특정 방향에서는 선명하지만 다른 방향에서는 흐릿해져 특징적인 각도 앨리어싱 패턴을 만듭니다.

## 근본 원인

표준 필터 역투영법은 나이퀴스트 샘플링 조건을 만족하는 충분한 수의 균등 간격 투영 각도를 필요로 합니다. 필요한 최소 투영 수는 검출기 픽셀 수에 따라 비례합니다(N 픽셀 검출기에 대해 약 π/2 × N). 스캔 시간 제약, 선량 제한, 빠른 동적 프로세스, 또는 제한된 각도 범위로 인해 투영이 부족하면 각도 샘플링이 불충분해집니다. 누락된 각도 정보는 푸리에 영역에서 널 공간을 생성하고, 재구성 알고리즘이 이 간극을 앨리어싱 아티팩트로 채웁니다.

## 빠른 진단

```python
import numpy as np

num_angles = sinogram.shape[0]
num_columns = sinogram.shape[1]
nyquist_angles = int(np.ceil(np.pi / 2 * num_columns))
ratio = num_angles / nyquist_angles
print(f"투영 수: {num_angles}, 나이퀴스트 요구: {nyquist_angles}")
print(f"샘플링 비율: {ratio:.2f}")
print(f"희소 각도 영역: {ratio < 0.5}")
```

## 탐지 방법

### 자동 탐지

```python
import numpy as np


def detect_sparse_angle_artifacts(reconstruction, num_projections, num_detector_pixels):
    """각도 샘플링과 이미지 품질 지표에 기반하여 희소 각도 아티팩트를 평가합니다."""
    nyquist_required = int(np.ceil(np.pi / 2 * num_detector_pixels))
    nyquist_ratio = num_projections / nyquist_required

    fft_2d = np.fft.fftshift(np.fft.fft2(reconstruction))
    magnitude = np.abs(fft_2d)
    log_mag = np.log1p(magnitude)

    cy, cx = np.array(log_mag.shape) // 2
    y, x = np.mgrid[:log_mag.shape[0], :log_mag.shape[1]]
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    theta = np.arctan2(y - cy, x - cx)

    num_angle_bins = 180
    angle_bins = np.linspace(-np.pi, np.pi, num_angle_bins + 1)
    radial_power = np.zeros(num_angle_bins)

    for k in range(num_angle_bins):
        mask = (theta >= angle_bins[k]) & (theta < angle_bins[k + 1]) & (r > 5)
        if np.sum(mask) > 0:
            radial_power[k] = np.mean(log_mag[mask])

    streak_score = np.std(radial_power) / (np.mean(radial_power) + 1e-10)

    if nyquist_ratio < 0.2:
        severity = "severe"
    elif nyquist_ratio < 0.5:
        severity = "moderate"
    elif nyquist_ratio < 0.8:
        severity = "mild"
    else:
        severity = "none"

    return {
        "nyquist_ratio": float(nyquist_ratio),
        "is_undersampled": nyquist_ratio < 0.8,
        "streak_score": float(streak_score),
        "severity": severity,
    }
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- N 픽셀 너비 검출기에 대해 최소 π/2 × N 투영을 수집합니다.
- 스캔 시간이 제한되면 검출기 해상도를 줄여(비닝) 필요한 투영 수를 낮춥니다.
- 균일 간격 대신 황금비 각도 간격을 사용하여 누락 정보를 더 균등하게 분배합니다.

### 보정 — 전통적 방법

정규화가 있는 반복 재구성 알고리즘은 이미지에 대한 사전 지식(예: 희소성, 부드러움)을 적용하여 누락된 각도 정보를 부분적으로 복원할 수 있습니다.

```python
import tomopy
import numpy as np


def reconstruct_sparse_angle(sinogram, theta, center, num_iter=50):
    """TV 정규화가 있는 반복 방법으로 희소 각도 데이터를 재구성합니다."""
    recon_sirt = tomopy.recon(
        sinogram, theta, center=center, algorithm='sirt', num_iter=num_iter,
    )

    from skimage.restoration import denoise_tv_chambolle
    recon_tv = np.zeros_like(recon_sirt)
    for i in range(recon_sirt.shape[0]):
        recon_tv[i] = denoise_tv_chambolle(recon_sirt[i], weight=0.05)

    return recon_tv
```

### 보정 — AI/ML 방법

희소 각도 토모그래피를 위한 딥러닝 접근법에는 획득된 투영에서 누락 투영을 예측하는 뷰 합성 네트워크, 학습된 정규화기로 최적화 알고리즘을 언롤하는 학습된 반복 재구성 네트워크 등이 있습니다. FBPConvNet, 학습된 프라이멀-듀얼 네트워크, NeRF에서 영감을 받은 암시적 신경 표현이 매우 적은 뷰에서 재구성할 수 있습니다. 이러한 접근법은 유리한 경우 10-50배 더 적은 투영에서 거의 전체 샘플링 품질을 달성할 수 있습니다.

## 보정하지 않을 경우의 영향

희소 각도 아티팩트는 구조적 세부 사항으로 잘못 해석될 수 있는 거짓 특징을 만듭니다. 스트릭 패턴은 특히 스트릭 방향에 정렬된 특징에 대해 세그멘테이션과 정량적 분석을 방해합니다. 해상도가 비등방적이 되어 치수 측정이 신뢰할 수 없게 됩니다.

## 관련 자료

- [토모그래피 AI/ML 방법](../../02_xray_modalities/tomography/ai_ml_methods.md) — DL 뷰 합성 및 학습된 재구성
- 관련 아티팩트: [저선량 포아송 노이즈](low_dose_noise.md) — 희소 각도와 저선량 영역이 종종 함께 발생
- 관련 아티팩트: [모션 아티팩트](motion_artifact.md) — 모션 방지를 위한 빠른 스캔이 희소 각도 샘플링을 요구할 수 있음

## 핵심 요점

희소 각도 아티팩트는 각도 샘플링이 나이퀴스트 임계값 아래로 떨어질 때 발생하여 방향성 스트릭과 앨리어싱을 생성합니다. TV 정규화가 있는 반복 재구성을 1차 보정으로 사용하고, 전통적 방법이 부족한 심하게 과소 샘플링된 데이터셋에는 딥러닝 접근법을 고려하세요.
