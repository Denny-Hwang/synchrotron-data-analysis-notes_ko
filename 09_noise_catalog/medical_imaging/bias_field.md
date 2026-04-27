# 바이어스 필드(Bias Field, 강도 불균일성)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 의료 MRI / 방사광 영상 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 의료 영상(MRI) |

## 설명

바이어스 필드(강도 불균일성, 셰이딩, 또는 MRI에서의 RF 불균일성으로도 불림)는 실제 조직/물질 특성과 무관한 매끄럽고 저주파의 공간적 강도 변화입니다. MRI에서는 RF 코일 감도의 비균일성에서 비롯되며, 방사광 영상에서는 비균일한 빔 프로파일, 검출기 응답 불균일성, 조명 그래디언트로부터 유사한 효과가 발생합니다.

## 근본 원인

- **MRI 기원:** 비균일한 B1(RF) 송신/수신 장 → 공간적으로 변하는 플립 각도와 신호 강도
- **방사광 유사 사례:** 비균일한 빔 프로파일(Gaussian/top-hat 불완전성), 섬광체(scintillator) 불균일, 렌즈 비네팅(vignetting)
- 저주파 곱셈 변조: `I_observed(x) = I_true(x) × B(x) + noise`
- 세분화 오류 및 정량 측정 오차를 가중시킴

## 빠른 진단

```python
import numpy as np
from scipy.ndimage import uniform_filter

def detect_bias_field(image_2d, object_mask, block_size=64):
    """Detect bias field by checking intensity variation of uniform regions."""
    # Divide into blocks, compute mean of each
    ny, nx = image_2d.shape
    means = []
    positions = []
    for y in range(0, ny - block_size, block_size):
        for x in range(0, nx - block_size, block_size):
            block = image_2d[y:y+block_size, x:x+block_size]
            mask_block = object_mask[y:y+block_size, x:x+block_size]
            if mask_block.sum() > block_size**2 * 0.5:
                means.append(block[mask_block].mean())
                positions.append((y + block_size//2, x + block_size//2))
    cv = np.std(means) / np.mean(means)
    print(f"Block intensity CV: {cv:.3f} (>0.05 suggests bias field)")
    return cv
```

## 탐지 방법

### 시각적 지표

- 이미지 전반에 걸친 매끄러운 밝기 그래디언트
- 동일 물질이 영역에 따라 더 어둡게 나타남
- 세분화 임계값이 전역적으로는 실패하지만 국소적으로는 동작함

### 자동 탐지

```python
import numpy as np
from scipy.ndimage import gaussian_filter

def estimate_bias_field(image_2d, sigma=50):
    """Estimate low-frequency bias field via Gaussian smoothing."""
    # Log-domain estimation (multiplicative bias becomes additive)
    log_img = np.log(image_2d + 1)
    bias_log = gaussian_filter(log_img, sigma=sigma)
    bias_field = np.exp(bias_log)
    return bias_field
```

## 보정 방법

### 전통적 접근법

1. **N4ITK (ANTs):** 산업 표준 반복 바이어스 필드 보정 (Tustison et al., 2010)
2. **호모모픽(Homomorphic) 필터링:** 로그 변환 → 고주파 통과 필터 → 지수화 (곱셈 바이어스 제거)
3. **표면 적합:** 배경/참조 영역에 저차 다항식 적합
4. **플랫필드 정규화:** 별도로 획득한 균일 조명 이미지로 나누기

```python
def homomorphic_bias_correction(image_2d, cutoff=0.05):
    """Homomorphic filtering for bias field removal."""
    log_img = np.log1p(image_2d.astype(float))
    # High-pass filter in Fourier domain
    F = np.fft.fft2(log_img)
    ny, nx = log_img.shape
    Y, X = np.meshgrid(np.fft.fftfreq(ny), np.fft.fftfreq(nx), indexing='ij')
    high_pass = 1 - np.exp(-(X**2 + Y**2) / (2 * cutoff**2))
    corrected_log = np.real(np.fft.ifft2(F * high_pass))
    corrected = np.expm1(corrected_log)
    return corrected
```

### AI/ML 접근법

- **DeepN4:** 학습 기반 바이어스 필드 추정 (반복적 N4보다 빠름)
- **공동 세분화-보정 네트워크:** 세분화와 바이어스 보정을 동시에 수행

## 주요 참고문헌

- **Tustison et al. (2010)** — "N4ITK: Improved N3 Bias Correction" — 표준 도구
- **Sled et al. (1998)** — "N3: Nonparametric Noncuniformity Normalization" — 원조 N3 알고리즘
- **Vovk et al. (2007)** — "A review of methods for correction of intensity inhomogeneity in MRI"
- **SimpleITK** — N4BiasFieldCorrectionImageFilter 구현

## 방사광 데이터와의 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 플랫필드 보정 잔차 | 불완전한 플랫필드는 곱셈 바이어스를 남김 |
| 빔 프로파일 불균일 | Gaussian 또는 구조화된 빔 → 중심-가장자리 그래디언트 |
| XRF 스캔 정규화 | 스캔 영역에 걸친 빔 강도 변화 |
| 전체 시야 현미경 | 렌즈 비네팅, 섬광체 불균일 |
| 다중 타일 스티칭 | 타일 간 조명 불일치 |

## 관련 자료

- [Flat-field issues](../tomography/flatfield_issues.md) — 조명 불균일에 대한 주요 방사광 보정
- [I0 normalization](../xrf_microscopy/i0_normalization.md) — XRF에서의 빔 강도 보정
- [Scan stripe](../xrf_microscopy/scan_stripe.md) — 행 단위 강도 불균일 변형
