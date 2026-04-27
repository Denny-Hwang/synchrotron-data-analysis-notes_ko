# Shot Noise in Low-Dose Imaging

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | SEM / TEM / Cryo-EM |
| **Noise Type** | Statistical |
| **Severity** | Critical |
| **Frequency** | Always |
| **Detection Difficulty** | Easy |
| **Origin Domain** | Electron Microscopy |

## Visual Examples

![Before and after — shot noise in low-dose imaging](../images/shot_noise_low_dose_before_after.png)

> **Image source:** Synthetic particle image with Poisson noise at ~5 e⁻/pixel. Left: single low-dose exposure (SNR < 0.1). Right: class average of 100 aligned particles. MIT license.

## Description

Shot noise (Poisson noise) is the fundamental statistical noise in electron microscopy arising from the discrete nature of electron detection. Each pixel's electron count follows a Poisson distribution, where the variance equals the mean count. In low-dose imaging — essential for radiation-sensitive biological samples in cryo-EM — SNR can be extremely low (SNR < 0.1 per particle image), making individual particles virtually invisible without averaging.

**Synchrotron relevance:** Directly analogous to photon counting noise in low-flux synchrotron measurements (XRF, low-dose CT). The Poisson noise model, SNR considerations, and averaging strategies are identical.

## Root Cause

- Electron detection is a discrete counting process → Poisson statistics
- Low-dose required for: biological cryo-EM, beam-sensitive materials, in-situ experiments
- SNR = √N for N detected electrons per pixel
- Typical cryo-EM: ~20-40 e⁻/Å² total dose → SNR per particle image < 0.1
- Compounded by detector DQE (Detective Quantum Efficiency) < 1

## Quick Diagnosis

```python
import numpy as np

def assess_poisson_noise(image, gain=1.0):
    """Verify Poisson noise characteristics via mean-variance analysis."""
    # Divide image into blocks
    block_size = 32
    means, variances = [], []
    ny, nx = image.shape
    for y in range(0, ny - block_size, block_size):
        for x in range(0, nx - block_size, block_size):
            block = image[y:y+block_size, x:x+block_size] / gain
            means.append(block.mean())
            variances.append(block.var())
    means, variances = np.array(means), np.array(variances)
    # For Poisson noise: variance ∝ mean (slope ≈ 1/gain)
    from numpy.polynomial.polynomial import polyfit
    slope = polyfit(means, variances, 1)[1]
    print(f"Variance/Mean slope: {slope:.3f} (expect ~{1/gain:.3f} for Poisson)")
    return slope
```

## Detection Methods

### Visual Indicators

- Grainy, "speckled" appearance uniform across image
- SNR degrades with lower dose — features barely distinguishable from noise
- Individual particle images in cryo-EM appear as noisy blobs
- Noise amplitude proportional to √(signal intensity)

### Automated Detection

```python
import numpy as np

def estimate_snr_per_particle(micrograph, particle_coords, box_size=256):
    """Estimate SNR of individual particles in cryo-EM micrograph."""
    snrs = []
    for y, x in particle_coords:
        particle = micrograph[y-box_size//2:y+box_size//2,
                             x-box_size//2:x+box_size//2]
        if particle.shape == (box_size, box_size):
            # Spectral SNR estimation
            F = np.fft.fft2(particle)
            power = np.abs(F)**2
            # Signal: low frequency, Noise: high frequency
            signal_power = power[:box_size//8, :box_size//8].mean()
            noise_power = power[box_size//4:, box_size//4:].mean()
            snrs.append(np.sqrt(signal_power / noise_power))
    print(f"Mean particle SNR: {np.mean(snrs):.3f}")
    return snrs
```

## Correction Methods

### Traditional Approaches

1. **Class averaging:** Align and average thousands of similar particle images (cryo-EM gold standard)
2. **Dose weighting:** Weight movie frames by radiation-damage-aware filter (higher dose = more damage = lower weight at high frequencies)
3. **Wiener filtering:** Optimal linear filter given known CTF and noise model
4. **Electron counting:** Direct detection with counting mode (DQE → 1)

```python
def dose_weighting(movie_frames, dose_per_frame, voltage=300):
    """Apply dose-dependent frequency weighting to movie frames."""
    n_frames, ny, nx = movie_frames.shape
    freqs = np.fft.fftfreq(ny).reshape(-1, 1)**2 + np.fft.fftfreq(nx).reshape(1, -1)**2
    freqs = np.sqrt(freqs)
    weighted_sum = np.zeros((ny, nx), dtype=complex)
    weight_sum = np.zeros((ny, nx))
    for i, frame in enumerate(movie_frames):
        cumulative_dose = (i + 0.5) * dose_per_frame
        # Optimal exposure filter (Grant & Grigorieff, 2015)
        critical_dose = 0.245 * (freqs * ny + 1e-10)**(-1.665) + 2.81
        weight = np.exp(-cumulative_dose / (2 * critical_dose))
        F_frame = np.fft.fft2(frame)
        weighted_sum += F_frame * weight
        weight_sum += weight
    return np.real(np.fft.ifft2(weighted_sum / (weight_sum + 1e-10)))
```

### AI/ML Approaches

- **Topaz-Denoise:** Self-supervised denoising for cryo-EM (Bepler et al., 2020)
- **CryoDRGN:** Deep generative model for heterogeneous reconstruction
- **Noise2Noise / Noise2Void:** Self-supervised approaches applicable to EM data
- **Warp:** Real-time processing with ML-based denoising

## Key References

- **Bepler et al. (2020)** — "Topaz-Denoise: general deep denoising models for cryoEM" — Nature Communications
- **Grant & Grigorieff (2015)** — "Measuring the optimal exposure for single particle cryo-EM" — dose weighting
- **Zheng et al. (2017)** — "MotionCor2: anisotropic correction of beam-induced motion" — frame alignment
- **McMullan et al. (2014)** — "Detective quantum efficiency of electron area detectors" — DQE analysis
- **EMPIAR** — Electron Microscopy Public Image Archive (benchmark datasets)

## Key Datasets & Benchmarks

| Dataset | Description |
|---------|-------------|
| EMPIAR-10025 | T20S proteasome — standard cryo-EM benchmark |
| EMPIAR-10028 | β-galactosidase — high-resolution test case |
| EMPIAR-10061 | TRPV1 channel — membrane protein benchmark |
| Topaz-Denoise training set | Paired even/odd frame averages for self-supervised training |

## Real-World Before/After Examples

The following published sources provide real experimental before/after comparisons:

| Source | Type | Figure | Description | License |
|--------|------|--------|-------------|---------|
| [Bepler et al. 2020 — Topaz-Denoise](https://doi.org/10.1038/s41467-020-18952-1) | Paper | Fig 2 | General deep denoising models for cryo-EM — real micrograph before/after denoising | CC BY 4.0 |
| [EMPIAR database](https://www.ebi.ac.uk/empiar/) | Data repository | Multiple datasets | Electron Microscopy Public Image Archive — real cryo-EM datasets for benchmarking | Open access |

> **Recommended reference**: [Bepler et al. 2020 — Topaz-Denoise (Nature Communications)](https://doi.org/10.1038/s41467-020-18952-1)

## Related Resources

- [Photon counting noise](../xrf_microscopy/photon_counting_noise.md) — Same Poisson statistics in X-ray detection
- [Low-dose noise](../tomography/low_dose_noise.md) — Analogous problem in synchrotron tomography
- [Radiation damage](../spectroscopy/radiation_damage.md) — Why low dose is necessary
