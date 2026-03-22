# 딥러닝 환각(DL Hallucination)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 교차 분야(Cross-cutting) |
| **노이즈 유형** | 계산(Computational) |
| **심각도** | 심각(Critical) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 어려움(Hard) |

## 시각적 예시

```
원본(Ground Truth)        DL 노이즈 제거 출력           차이 (환각)

+---------------+    +---------------+          +---------------+
|               |    |     *         |          |     *         |
|   노이즈가    |    |   깨끗 +      |          |  거짓 특징     |
|   있지만      | -> |   환각된      |    =     |  데이터에      |
|   특징 없음   |    |   입자        |          |  존재하지 않음 |
|               |    |               |          |               |
+---------------+    +---------------+          +---------------+
```

> **중요 경고:** 딥러닝 재구성 및 노이즈 제거 출력은 독립적 검증 없이 정량적 과학 분석의 근거(ground truth)로 절대 신뢰해서는 안 됩니다. 네트워크는 특히 저SNR 영역이나 훈련 분포 외 데이터를 처리할 때 그럴듯하지만 완전히 허구인 특징을 생성할 수 있습니다.

> **외부 참고자료:**
> - [Gottschling et al. — DL 이미징의 환각 문제](https://doi.org/10.1137/20M1387237)
> - [Antun et al. — 이미지 재구성에서의 DL 불안정성](https://doi.org/10.1073/pnas.1907377117)

## 설명

딥러닝 환각은 신경망 처리 이미지에 나타나지만 시료의 실제 구조에 해당하지 않는 특징입니다. 신경망은 훈련 데이터로부터 통계적 사전 지식을 학습하는 생성 모델이므로, 모호하거나 노이즈가 많은 입력이 주어지면 실제 물리적 현실이 아닌 학습된 분포와 일치하는 그럴듯한 세부 사항을 채워 넣습니다. 환각은 자연스럽고 자체 일관성이 있어 독립적 검증 없이는 실제 특징과 거의 구별할 수 없기 때문에 특히 위험합니다.

## 근본 원인

신경망은 훈련 데이터에 대해 손실 함수를 최소화하면서 진정한 신호 구조와 훈련 세트에 존재하는 통계적 편향 모두를 학습합니다. 네트워크가 훈련 분포와 다른 입력(분포 외 데이터, 특이한 시료 형태, 다른 노이즈 수준 또는 다른 수집 매개변수)을 만나면, 측정된 신호 대신 학습된 사전 지식을 사용하여 외삽합니다. 노이즈 제거 네트워크는 특징 없는 영역에서 텍스처와 입자를 환각할 수 있고, 초해상도 네트워크는 서브해상도 구조를 발명할 수 있으며, 재구성 네트워크는 과소 샘플링 영역에서 코히어런트하지만 거짓인 특징을 만들 수 있습니다.

## 빠른 진단

```python
import numpy as np

# DL 출력을 전통적 재구성과 비교
residual = dl_recon - conv_recon
residual_snr = np.std(residual) / np.mean(np.abs(conv_recon) + 1e-10)
print(f"잔차 상대 크기: {residual_snr:.4f}")
print(f"잔차에 구조적 특징이 포함되어 있으면(단순 노이즈가 아니면), 환각 가능성 있음")
```

## 탐지 방법

### 시각적 지표

- 동일 데이터의 전통적 재구성에는 없는 DL 출력의 특징
- 매우 노이즈가 많거나 과소 샘플링된 입력 데이터에서 의심스럽게 깨끗하거나 아티팩트 없는 결과
- 훈련 데이터 모티프와 유사한 반복적이거나 템플릿 같은 구조
- 입력의 작은 교란에 따라 상당히 변하는 특징(적대적 불안정성)

### 자동 탐지

```python
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.stats import pearsonr


def detect_dl_hallucination(dl_output, conventional_output,
                             structure_threshold=0.15):
    """DL 출력을 전통적 재구성과 비교하여 잠재적 환각을 탐지합니다."""
    dl_norm = (dl_output - np.mean(dl_output)) / (np.std(dl_output) + 1e-10)
    conv_norm = (conventional_output - np.mean(conventional_output)) / (
        np.std(conventional_output) + 1e-10
    )
    residual = dl_norm - conv_norm

    residual_centered = residual - np.mean(residual)
    local_var = gaussian_filter(residual_centered**2, sigma=10)
    global_var = np.var(residual_centered)

    structure_score = float(np.max(local_var) / (global_var + 1e-10))
    structure_score = min(structure_score / 5.0, 1.0)

    residual_smooth = gaussian_filter(np.abs(residual_centered), sigma=5)
    noise_threshold = 3.0 * np.std(residual_centered)
    suspicious = residual_smooth > noise_threshold

    has_risk = (
        structure_score > structure_threshold
        or np.sum(suspicious) > 0.01 * suspicious.size
    )

    return {
        "residual_structure_score": structure_score,
        "suspicious_regions": suspicious,
        "has_hallucination_risk": has_risk,
    }
```

## 해결 방법 및 완화

### 예방

- DL 노이즈 제거 또는 재구성에 대한 극단적 의존을 피하기 위해 충분한 데이터 품질을 확보합니다.
- DL 모델 훈련 시 예상 시료 변동성을 포괄하는 다양한 훈련 데이터를 사용합니다.
- 엣지 케이스와 분포 외 샘플을 포함하는 홀드아웃 테스트 데이터로 DL 모델을 검증합니다.

### 보정 — 전통적 방법

주요 안전장치는 항상 DL 처리 출력을 전통적 재구성과 비교하고 잔차에서 구조를 검사하는 것입니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


def hallucination_audit(dl_image, conventional_image, output_path=None):
    """DL 출력과 전통적 재구성을 비교하는 시각적 환각 감사를 생성합니다."""
    dl_norm = (dl_image - dl_image.mean()) / (dl_image.std() + 1e-10)
    conv_norm = (conventional_image - conventional_image.mean()) / (
        conventional_image.std() + 1e-10
    )
    residual = dl_norm - conv_norm
    noise_floor = np.std(gaussian_filter(conv_norm, sigma=1) - conv_norm)
    suspicious_mask = np.abs(gaussian_filter(residual, sigma=3)) > 3 * noise_floor

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes[0, 0].imshow(conv_norm, cmap="gray")
    axes[0, 0].set_title("전통적 재구성")
    axes[0, 1].imshow(dl_norm, cmap="gray")
    axes[0, 1].set_title("DL 출력")
    im_res = axes[1, 0].imshow(residual, cmap="RdBu_r", vmin=-3*noise_floor, vmax=3*noise_floor)
    axes[1, 0].set_title("잔차 (DL - 전통적)")
    plt.colorbar(im_res, ax=axes[1, 0])
    axes[1, 1].imshow(dl_norm, cmap="gray")
    axes[1, 1].contour(suspicious_mask, colors="red", linewidths=0.5)
    axes[1, 1].set_title("의심 영역 (빨간 윤곽)")

    pct_suspicious = 100 * np.sum(suspicious_mask) / suspicious_mask.size
    fig.suptitle(f"DL 환각 감사 — {pct_suspicious:.1f}% 픽셀 플래그됨", fontsize=14, fontweight="bold")
    plt.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)
```

### 보정 — AI/ML 방법 (불확실성 정량화)

- **앙상블 방법:** 다른 초기화로 여러 네트워크를 훈련하고 픽셀별 분산을 계산합니다. 높은 분산은 신뢰할 수 없는 영역을 나타냅니다.
- **몬테카를로 드롭아웃:** 드롭아웃을 활성화한 상태로 여러 번 추론을 실행합니다. 실행 간 분산이 인식론적 불확실성을 추정합니다.
- **학습된 불확실성:** 예측과 불확실성 맵 모두를 출력하도록 네트워크를 훈련합니다(이분산 손실).

## 보정하지 않을 경우의 영향

환각된 특징은 완전히 잘못된 과학적 결론으로 이어질 수 있습니다. 재료과학에서 환각된 입자나 기공은 측정된 기공률, 결정립 크기 분포 또는 결함 밀도를 변경할 수 있습니다. 생물학적 이미징에서 거짓 구조가 세포소기관이나 병리학적 특징으로 오식별될 수 있습니다. DL 환각은 자연스럽고 자체 일관성이 있어 시각적으로 명확한 전통적 아티팩트(링, 스트릭)보다 훨씬 더 위험합니다.

## 관련 자료

- [TomoGAN 노이즈 제거](../../03_ai_ml_methods/denoising/tomogan.md) — 환각 위험이 특히 높은 GAN 기반 노이즈 제거
- [저선량 노이즈](../tomography/low_dose_noise.md) — DL 노이즈 제거(및 환각 위험)를 촉진하는 주요 사용 사례
- [희소 각도 아티팩트](../tomography/sparse_angle_artifact.md) — DL 기반 희소 뷰 재구성은 특히 환각에 취약

## 핵심 요점

딥러닝 환각은 현대 싱크로트론 데이터 분석에서 과학적으로 가장 위험한 아티팩트입니다. 정량적 결론을 위해 DL 처리 결과만 의존하지 마세요 — 항상 전통적 재구성에 대한 잔차 분석을 수행하고, 불확실성 정량화를 사용하며, DL 출력을 검증될 가설로 취급하세요.
