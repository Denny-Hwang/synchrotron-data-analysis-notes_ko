# 교차 도메인 노이즈 추정 및 특성 분석 방법(Cross-Domain Noise Estimation & Characterization Methods)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 교차 도메인 (모든 모달리티) |
| **노이즈 유형** | 방법론 참조 |
| **심각도** | N/A (참조 문서) |
| **빈도** | N/A |
| **탐지 난이도** | N/A |
| **기원 도메인** | 의료 영상, 천문학, 전자현미경 |

## 설명

이 문서는 방사광 데이터에 적용 가능한 여러 이미징 도메인의 노이즈 추정 및 특성 분석 방법론을 카탈로그화합니다. 이러한 교차 도메인 방법은 노이즈 정량화, 데이터 품질 비교, 잡음 제거 알고리즘 검증을 위한 표준화된 프레임워크를 제공합니다.

## 노이즈 특성 분석 방법

### 1. 노이즈 파워 스펙트럼(NPS) / 위너 스펙트럼(Wiener Spectrum)

**기원:** 의료 영상 (CT 품질 보증) 및 천문학
**목적:** 주파수 의존적 노이즈 특성 분석

```python
import numpy as np

def compute_nps(image, roi_size=128, n_rois=20):
    """균일 영역 ROI로부터 노이즈 파워 스펙트럼을 계산합니다."""
    ny, nx = image.shape
    nps_sum = np.zeros((roi_size, roi_size))
    for _ in range(n_rois):
        y0 = np.random.randint(0, ny - roi_size)
        x0 = np.random.randint(0, nx - roi_size)
        roi = image[y0:y0+roi_size, x0:x0+roi_size]
        # 평균(DC 성분) 제거
        roi = roi - roi.mean()
        # 2D DFT
        F = np.fft.fftshift(np.fft.fft2(roi))
        nps_sum += np.abs(F)**2
    nps = nps_sum / n_rois * (1.0 / roi_size**2)
    return nps

def radial_nps(nps_2d, pixel_size=1.0):
    """2D NPS로부터 1D 방사형 NPS를 계산합니다."""
    ny, nx = nps_2d.shape
    cy, cx = ny // 2, nx // 2
    Y, X = np.ogrid[-cy:ny-cy, -cx:nx-cx]
    r = np.sqrt(X**2 + Y**2).astype(int)
    r_max = min(cy, cx)
    radial = np.array([nps_2d[r == ri].mean() for ri in range(1, r_max)])
    freq = np.arange(1, r_max) / (2 * r_max * pixel_size)
    return freq, radial
```

**방사광 응용:**
- CT 이미지 품질 평가
- 검출기 특성 분석
- 재구성 알고리즘 비교
- 잡음 제거 검증

### 2. 검출 양자 효율(DQE)

**기원:** 의료 영상 및 검출기 물리
**목적:** 주파수 대비 검출기의 신호 전달 효율 정량화

```python
import numpy as np

def compute_dqe(mtf, nps, mean_signal, incident_quanta):
    """MTF와 NPS로부터 DQE를 계산합니다."""
    # DQE(f) = MTF(f)² × mean_signal² / (NPS(f) × incident_quanta)
    dqe = mtf**2 * mean_signal**2 / (nps * incident_quanta + 1e-10)
    return np.clip(dqe, 0, 1)
```

**핵심 지표:** DQE(0) = 출력 SNR² / 입력 SNR² — 전체 효율

### 3. 평균-분산 분석 (Poisson-Gaussian 노이즈 모델)

**기원:** 천문학 (CCD 특성 분석) 및 형광 현미경
**목적:** Poisson(신호 의존) 노이즈와 Gaussian(읽기) 노이즈 성분 분리

```python
import numpy as np

def mean_variance_analysis(image_pairs):
    """평균-분산 관계로부터 게인과 읽기 노이즈를 추정합니다.

    Args:
        image_pairs: 다른 노출 수준에서의 (flat1, flat2) 이미지 쌍 리스트
    """
    means, variances = [], []
    for flat1, flat2 in image_pairs:
        mean_val = (flat1.mean() + flat2.mean()) / 2
        # 차이의 분산 / 2 = 시간적 노이즈 분산
        diff = flat1.astype(float) - flat2.astype(float)
        var_val = diff.var() / 2
        means.append(mean_val)
        variances.append(var_val)
    means, variances = np.array(means), np.array(variances)
    # 선형 피팅: Var = (1/gain) * Mean + readnoise²
    slope, intercept = np.polyfit(means, variances, 1)
    gain = 1.0 / slope  # e⁻/ADU
    readnoise = np.sqrt(abs(intercept))  # ADU
    print(f"Gain: {gain:.2f} e⁻/ADU")
    print(f"Read noise: {readnoise:.2f} ADU ({readnoise*gain:.2f} e⁻)")
    return gain, readnoise
```

### 4. MAD 추정기 (단일 이미지로부터의 강건한 노이즈 추정)

**기원:** 신호 처리 / 웨이블릿 분석
**목적:** 깨끗한 참조 없이 노이즈 표준편차를 추정

```python
import numpy as np

def mad_noise_estimate(image):
    """웨이블릿 계수의 중앙값 절대편차(MAD)를 사용해 노이즈 시그마를 추정합니다."""
    from scipy.ndimage import convolve
    # 수평 디테일 계수 (Haar 웨이블릿 근사)
    kernel = np.array([[1, -1]])
    detail = convolve(image.astype(float), kernel)
    # MAD 추정기 (신호 내용에 강건)
    mad = np.median(np.abs(detail - np.median(detail)))
    sigma = mad / 0.6745  # Gaussian 가정에서 MAD를 sigma로 변환
    print(f"Estimated noise sigma: {sigma:.3f}")
    return sigma
```

### 5. Noise2Void / Noise2Self 프레임워크

**기원:** 컴퓨터 비전 / 딥러닝
**목적:** 깨끗한 참조 없이 자기지도 노이즈 추정

```python
# 개념적 프레임워크 — 실제 구현은 딥러닝 라이브러리가 필요
def noise2void_concept(noisy_image):
    """
    Noise2Void (Krull et al., 2019):
    - 주변 컨텍스트로부터 중심 픽셀을 예측하도록 CNN 학습
    - 블라인드 스팟 네트워크: 수용 영역에서 중심 픽셀 제외
    - 네트워크는 신호(상관성 있음)를 학습하지만 노이즈(독립적)는 학습할 수 없음
    - 적용 조건: 노이즈가 픽셀별 독립적이고, 깨끗한 데이터가 없을 때

    방사광에 적용 가능:
    - 저선량 토모그래피 잡음 제거
    - XRF 맵 잡음 제거
    - 픽셀별 독립 노이즈를 갖는 모든 검출기
    """
    pass
```

## 표준 벤치마크 및 데이터셋

### 자연 이미지 잡음 제거

| 데이터셋 | 설명 | 용도 |
|----------|------|------|
| BSD68 | Berkeley Segmentation Dataset의 68개 이미지 | 표준 PSNR/SSIM 벤치마크 |
| Set12 | 12개의 고전 테스트 이미지 | 빠른 평가 |
| CBSD68 | BSD68의 컬러 버전 | 컬러 잡음 제거 |
| McMaster | 18개의 고품질 이미지 | 컬러 잡음 제거 |

### 도메인 특화

| 데이터셋 | 도메인 | 설명 |
|----------|--------|------|
| LDCT Grand Challenge (AAPM) | 의료 CT | 정상/저선량 CT 페어 |
| FMD | 형광 현미경 | 공초점, 이광자, 광시야 |
| Planaria / Tribolium | 형광 현미경 | 노이즈/클린 페어 생물 이미지 |
| EMPIAR | Cryo-EM | 단일 입자 벤치마크 데이터 |
| TomoBank | 방사광 | APS 토모그래피 데이터셋 |
| SciCat | 방사광 | ESS/PSI 데이터 카탈로그 |

### 노이즈 수준 관례

| 도메인 | 노이즈 매개변수화 |
|--------|-------------------|
| 자연 이미지 잡음 제거 | 가산 Gaussian σ = 15, 25, 50 |
| 의료 CT | 선량 수준 (mAs), 노이즈 인덱스 |
| 천문학 | 게인 (e⁻/ADU) + 읽기 노이즈 (e⁻) |
| 전자현미경 | 선량 (e⁻/Å²) |
| 방사광 XRF | 체류 시간 (ms), 총 카운트 |
| 방사광 CT | 노출 시간, I₀ 카운트 |

## 품질 지표

```python
import numpy as np

def compute_psnr(clean, denoised, data_range=None):
    """피크 신호 대 잡음비(Peak Signal-to-Noise Ratio)."""
    mse = np.mean((clean - denoised)**2)
    if data_range is None:
        data_range = clean.max() - clean.min()
    return 10 * np.log10(data_range**2 / mse)

def compute_ssim(clean, denoised, win_size=7):
    """구조적 유사성 지수(Structural Similarity Index, 단순화 버전)."""
    from scipy.ndimage import uniform_filter
    C1 = (0.01 * (clean.max() - clean.min()))**2
    C2 = (0.03 * (clean.max() - clean.min()))**2
    mu1 = uniform_filter(clean, win_size)
    mu2 = uniform_filter(denoised, win_size)
    sigma1_sq = uniform_filter(clean**2, win_size) - mu1**2
    sigma2_sq = uniform_filter(denoised**2, win_size) - mu2**2
    sigma12 = uniform_filter(clean * denoised, win_size) - mu1 * mu2
    ssim_map = ((2*mu1*mu2 + C1) * (2*sigma12 + C2)) / \
               ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()

def compute_cnr(image, roi_signal, roi_background):
    """대비 대 잡음비(Contrast-to-Noise Ratio) — 의료 영상의 표준."""
    signal_mean = image[roi_signal].mean()
    bg_mean = image[roi_background].mean()
    bg_std = image[roi_background].std()
    cnr = abs(signal_mean - bg_mean) / (bg_std + 1e-10)
    return cnr
```

## 핵심 참고문헌

- **van Dokkum (2001)** — L.A.Cosmic (우주선 / 이상치 탐지)
- **Krull et al. (2019)** — "Noise2Void: Learning Denoising from Single Noisy Images"
- **Batson & Royer (2019)** — "Noise2Self: Blind Denoising by Self-Supervision"
- **Zhang et al. (2017)** — "Beyond a Gaussian Denoiser: Residual Learning of Deep CNN (DnCNN)"
- **Lehtinen et al. (2018)** — "Noise2Noise: Learning Image Restoration without Clean Data"
- **Siewerdsen et al. (2002)** — "Framework for NPS of multi-dimensional imaging systems"
- **Cunningham & Shaw (1999)** — "Signal-to-noise optimization of medical imaging systems" (DQE 프레임워크)
- **Foi et al. (2008)** — "Practical Poissonian-Gaussian noise modeling for photography and microscopy"

## 관련 자료

- [저선량 노이즈](../tomography/low_dose_noise.md) — NPS 및 DQE 개념 적용
- [광자 계수 노이즈](../xrf_microscopy/photon_counting_noise.md) — Poisson-Gaussian 모델
- [DL 환각](dl_hallucination.md) — ML 방법으로 인한 잡음 제거 아티팩트
- [검출기 일반 문제](detector_common_issues.md) — 검출기 특성 분석
