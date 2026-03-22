# 프로브 흐림(Probe Blurring)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | XRF 현미경 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 경미(Minor) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 어려움(Hard) |

## 시각적 예시

```
 실제 시료 구조                 측정된 XRF 맵                  디컨볼루션 맵
 (서브빔 해상도)                (프로브와 컨볼루션)             (Richardson-Lucy)
 ┌────────────────────┐        ┌────────────────────┐        ┌────────────────────┐
 │    ██              │        │   ░▒▓▓▒░           │        │    ▓█▓             │
 │    ██              │        │   ▒▓██▓▒           │        │    ▓██             │
 │          ████████  │        │       ░▒▓████▓▒░   │        │         ▒▓█████▓   │
 │          ████████  │        │       ░▒▓████▓▒░   │        │         ▒▓█████▓   │
 │ ██████████████████ │        │ ░▒▓████████████▓▒░ │        │ ▒▓██████████████▓  │
 └────────────────────┘        └────────────────────┘        └────────────────────┘
  날카로운 경계                   흐릿한 엣지, 특징이            부분적으로 복원된
  2 nm 특징                      ~200 nm 더 넓게 보임           선명도
```

## 설명

프로브 흐림은 집속된 X선 빔의 유한한 크기에 의해 부과되는 공간 해상도 한계입니다. XRF 맵의 모든 픽셀은 수학적 점이 아닌 빔 풋프린트에 의해 정의된 영역의 형광을 기록합니다. 측정된 맵은 빔의 점확산함수(PSF)와 진짜 원소 분포의 컨볼루션이므로, 빔보다 작은 특징은 확대되어 보이고, 날카로운 경계는 점진적 기울기가 되며, 근접한 특징은 합쳐집니다.

## 근본 원인

싱크로트론 마이크로프로브의 X선 빔은 광학 요소(KB 미러, 존 플레이트 또는 복합 굴절 렌즈)에 의해 유한한 크기의 점으로 집속됩니다. 일반적으로 빔라인과 광학에 따라 50 nm ~ 10 μm FWHM입니다. 수학적으로, 측정된 맵 M(x,y) = PSF(x,y) * C(x,y)이며, 여기서 *는 2D 컨볼루션을 나타내고 C(x,y)는 실제 농도입니다.

## 빠른 진단

```python
import numpy as np
from scipy import ndimage

gradient = np.hypot(*np.gradient(element_map.astype(float)))
edge_profile = element_map[np.unravel_index(np.argmax(gradient), gradient.shape)[0], :]
fwhm_pixels = np.sum(edge_profile > 0.5 * np.max(edge_profile))
print(f"가장 날카로운 엣지 FWHM: ~{fwhm_pixels} 픽셀")
print(f"스텝 크기 = 0.5 μm이면 → 빔 FWHM ≈ {fwhm_pixels * 0.5:.1f} μm")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 가능한 가장 작은 빔 크기를 사용합니다(나노프로브 빔라인은 30-50 nm 해상도 제공).
- 스캔 전 집속 광학의 올바른 정렬과 수차 부재를 확인합니다.
- 스캔 스텝 크기를 빔 크기에 맞춥니다(2-3배 오버샘플링이 디컨볼루션을 가능하게 함).

### 보정 — 전통적 방법

```python
import numpy as np
from scipy.signal import fftconvolve


def richardson_lucy_deconvolution(image, psf, n_iterations=50,
                                    clip_negative=True):
    """Richardson-Lucy 디컨볼루션으로 XRF 원소 맵을 선명화합니다."""
    psf = psf / np.sum(psf)
    psf_mirror = psf[::-1, ::-1]
    estimate = image.astype(float).copy()
    estimate[estimate <= 0] = 1e-10

    for i in range(n_iterations):
        blurred_estimate = fftconvolve(estimate, psf, mode='same')
        blurred_estimate[blurred_estimate <= 0] = 1e-10
        ratio = image.astype(float) / blurred_estimate
        correction = fftconvolve(ratio, psf_mirror, mode='same')
        estimate *= correction
        if clip_negative:
            estimate = np.maximum(estimate, 0)

    return estimate


def make_gaussian_psf(fwhm_pixels, size=None):
    """디컨볼루션용 2D 가우시안 PSF 커널을 생성합니다."""
    sigma = fwhm_pixels / 2.3548
    if size is None:
        size = int(4 * fwhm_pixels) + 1
        if size % 2 == 0:
            size += 1
    center = size // 2
    y, x = np.mgrid[:size, :size]
    psf = np.exp(-((x - center)**2 + (y - center)**2) / (2 * sigma**2))
    psf /= np.sum(psf)
    return psf
```

### 보정 — AI/ML 방법

쌍을 이룬 저해상도/고해상도 XRF 데이터에서 훈련된 딥러닝 초해상도 방법은 Richardson-Lucy 디컨볼루션이 할 수 없는 서브빔 특징을 복원할 수 있습니다. 딥 잔차 아키텍처와 같은 네트워크는 흐리고 노이즈가 있는 XRF 맵에서 선명하고 노이즈가 제거된 버전으로의 매핑을 학습하며, 고전적 디컨볼루션에 내재된 노이즈 증폭을 동시에 방지합니다.

## 보정하지 않을 경우의 영향

프로브 흐림은 스캔 스텝 크기와 관계없이 XRF 맵의 유효 공간 해상도를 빔 크기로 제한합니다. 서브빔 특징은 뭉개져 분해할 수 없으며, 작은 특징의 정량적 분석은 빔이 특징과 주변을 평균화하기 때문에 희석된 농도를 산출합니다.

## 관련 자료

- [딥 잔차 XRF 노이즈 제거](../../03_ai_ml_methods/denoising/deep_residual_xrf.md) — 동시 노이즈 제거 및 디블러링에 대한 신경망 접근법
- 관련 아티팩트: [광자 계수 노이즈](photon_counting_noise.md) — 디컨볼루션은 노이즈를 증폭; 먼저 노이즈 제거
- 관련 아티팩트: [스캔 줄무늬](scan_stripe.md) — 디스트라이핑이 디컨볼루션에 선행해야 함

## 핵심 요점

프로브 흐림은 유한한 빔 크기의 불가피한 결과이며 XRF 현미경의 진정한 공간 해상도를 설정합니다. 작은 특징의 정량적 분석을 위해서는 더 작은 프로브가 있는 빔라인을 사용하거나 측정된 PSF로 Richardson-Lucy 디컨볼루션을 적용하세요 — 단, 디컨볼루션이 노이즈를 증폭하므로 신중한 정규화가 필요합니다.
