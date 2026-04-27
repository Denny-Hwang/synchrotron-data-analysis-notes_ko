# Bias Field (Intensity Inhomogeneity)

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Medical MRI / Synchrotron Imaging |
| **Noise Type** | Instrumental |
| **Severity** | Major |
| **Frequency** | Common |
| **Detection Difficulty** | Moderate |
| **Origin Domain** | Medical Imaging (MRI) |

## Description

Bias field (also called intensity inhomogeneity, shading, or RF inhomogeneity in MRI) is a smooth, low-frequency spatial variation in image intensity that is unrelated to the actual tissue/material properties. In MRI it comes from non-uniform RF coil sensitivity; in synchrotron imaging, analogous effects arise from non-uniform beam profile, detector response non-uniformity, and illumination gradients.

## Root Cause

- **MRI origin:** Non-uniform B1 (RF) transmit/receive field → spatially varying flip angle and signal intensity
- **Synchrotron analog:** Non-uniform beam profile (Gaussian/top-hat imperfections), scintillator non-uniformity, lens vignetting
- Low-frequency multiplicative modulation: `I_observed(x) = I_true(x) × B(x) + noise`
- Compounds segmentation errors and quantitative measurements

## Quick Diagnosis

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

## Detection Methods

### Visual Indicators

- Smooth brightness gradient across the image
- Same material appears darker in one region than another
- Segmentation thresholds fail globally but work locally

### Automated Detection

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

## Correction Methods

### Traditional Approaches

1. **N4ITK (ANTs):** Industry-standard iterative bias field correction (Tustison et al., 2010)
2. **Homomorphic filtering:** Log transform → high-pass filter → exponential (removes multiplicative bias)
3. **Surface fitting:** Fit low-order polynomial to background/reference regions
4. **Flat-field normalization:** Divide by separately acquired uniform-illumination image

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

### AI/ML Approaches

- **DeepN4:** Learning-based bias field estimation (faster than iterative N4)
- **Joint segmentation-correction networks:** Simultaneously segment and correct bias

## Key References

- **Tustison et al. (2010)** — "N4ITK: Improved N3 Bias Correction" — gold standard tool
- **Sled et al. (1998)** — "N3: Nonparametric Noncuniformity Normalization" — original N3 algorithm
- **Vovk et al. (2007)** — "A review of methods for correction of intensity inhomogeneity in MRI"
- **SimpleITK** — N4BiasFieldCorrectionImageFilter implementation

## Relevance to Synchrotron Data

| Scenario | Relevance |
|----------|-----------|
| Flat-field correction residuals | Imperfect flat-field leaves multiplicative bias |
| Beam profile non-uniformity | Gaussian or structured beam → center-to-edge gradient |
| XRF scan normalization | Beam intensity variation across scan area |
| Full-field microscopy | Lens vignetting, scintillator non-uniformity |
| Multi-tile stitching | Illumination mismatch between tiles |

## Related Resources

- [Flat-field issues](../tomography/flatfield_issues.md) — Primary synchrotron correction for illumination non-uniformity
- [I0 normalization](../xrf_microscopy/i0_normalization.md) — Beam intensity correction in XRF
- [Scan stripe](../xrf_microscopy/scan_stripe.md) — Row-by-row variant of intensity inhomogeneity
