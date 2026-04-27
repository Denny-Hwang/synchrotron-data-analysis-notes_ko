# Beam Hardening Artifact

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Medical CT / Synchrotron Tomography |
| **Noise Type** | Systematic |
| **Severity** | Major |
| **Frequency** | Common |
| **Detection Difficulty** | Moderate |
| **Origin Domain** | Medical Imaging (CT) |

## Visual Examples

![Before and after — beam hardening cupping artifact](../images/beam_hardening_before_after.png)

> **Image source:** Synthetic Shepp-Logan phantom with simulated polychromatic cupping. Left: reconstruction showing center-darkening cupping artifact. Right: after polynomial cupping correction. MIT license.

## Description

Beam hardening artifacts appear as cupping (dark center in uniform objects) or dark bands/streaks between dense structures. They arise because polychromatic X-ray beams preferentially lose low-energy photons as they pass through matter, causing the effective beam energy to increase ("harden") with depth. This violates the monochromatic assumption of standard CT reconstruction algorithms.

**Synchrotron relevance:** While synchrotron beams are largely monochromatic, pink-beam or broadband experiments, multilayer monochromator setups, and harmonic contamination can introduce analogous spectral-hardening effects. This is also directly relevant when comparing synchrotron CT data with lab-source micro-CT data.

## Root Cause

- Polychromatic X-ray source with energy-dependent attenuation (Beer-Lambert law breakdown)
- Low-energy photons absorbed preferentially → effective energy increases with path length
- Reconstruction assumes monochromatic beam → systematic underestimation of attenuation in center
- Dense materials (bone, metal) cause severe local hardening

### Physical Model

```
I(d) = ∫ S(E) · exp(-μ(E)·d) dE   (polychromatic)
≠ I₀ · exp(-μ_eff·d)               (monochromatic assumption)
```

## Quick Diagnosis

```python
import numpy as np

def detect_cupping(slice_2d, center=None):
    """Detect beam hardening cupping artifact via radial profile."""
    ny, nx = slice_2d.shape
    if center is None:
        center = (ny // 2, nx // 2)
    Y, X = np.ogrid[:ny, :nx]
    r = np.sqrt((X - center[1])**2 + (Y - center[0])**2).astype(int)
    # Radial mean profile
    r_max = min(center[0], center[1], ny - center[0], nx - center[1])
    radial_mean = np.array([slice_2d[r == ri].mean() for ri in range(r_max)])
    # Cupping: center values significantly lower than periphery
    center_val = np.mean(radial_mean[:r_max // 4])
    edge_val = np.mean(radial_mean[3 * r_max // 4:])
    cupping_ratio = (edge_val - center_val) / edge_val
    print(f"Cupping ratio: {cupping_ratio:.3f} (>0.05 suggests beam hardening)")
    return cupping_ratio
```

## Detection Methods

### Visual Indicators

- **Cupping artifact:** Center of uniform cylindrical object appears darker than edges in reconstructed slice
- **Dark bands:** Dark streaks between two dense objects (e.g., between bones)
- **Non-uniform CT values:** Same material shows different Hounsfield/attenuation values at different positions

### Automated Detection

```python
import numpy as np
from scipy.optimize import curve_fit

def fit_cupping_profile(radial_profile):
    """Fit parabolic cupping to radial profile."""
    r = np.arange(len(radial_profile))
    r_norm = r / r.max()
    # Cupping model: a * r^2 + b
    def cupping_model(x, a, b):
        return a * x**2 + b
    popt, _ = curve_fit(cupping_model, r_norm, radial_profile)
    cupping_coeff = popt[0]
    return cupping_coeff  # positive = cupping present
```

## Correction Methods

### Traditional Approaches

1. **Linearization (water correction):** Pre-correct projection data using known attenuation curve of water
2. **Polynomial correction:** Fit polynomial mapping measured projection values to ideal monochromatic values
3. **Dual-energy CT:** Acquire at two energies to decompose material basis functions
4. **Iterative reconstruction:** Model polychromatic forward projection in iterative loop

```python
def polynomial_beam_hardening_correction(projections, order=3):
    """Simple polynomial beam hardening correction."""
    # Normalize projections
    p = projections.copy()
    p_flat = p.flatten()
    # Fit polynomial: corrected = sum(a_i * measured^i)
    # Coefficients typically determined from phantom calibration
    # Example: cubic correction
    corrected = p + 0.1 * p**2 - 0.01 * p**3  # coefficients from calibration
    return corrected
```

### AI/ML Approaches

- **Deep learning BHC:** CNN trained on paired polychromatic/monochromatic data (Park et al., 2018)
- **SinoNet:** Sinogram-domain correction network
- **Iterative neural network:** Unrolled optimization with learned regularization

## Key References

- **Brooks & Di Chiro (1976)** — "Beam hardening in X-ray reconstructive tomography" — foundational description
- **Herman (1979)** — Correction methods for beam hardening in CT
- **Park et al. (2018)** — "A deep learning approach for beam hardening correction"
- **Kachelrieß et al. (2006)** — "Empirical cupping correction" (ECuP)
- **NIST XCOM database** — Energy-dependent mass attenuation coefficients

## Relevance to Synchrotron Data

| Scenario | Relevance |
|----------|-----------|
| Pink-beam tomography | Direct analog — broadband source |
| Multilayer monochromator | Bandwidth ~1-2% can cause mild cupping |
| Harmonic contamination | Third-harmonic acts as secondary energy component |
| Lab micro-CT comparison | Essential when benchmarking synchrotron vs lab data |
| Phase-contrast imaging | Energy spectrum affects phase retrieval accuracy |

## Real-World Before/After Examples

The following published sources provide real experimental before/after comparisons:

| Source | Type | Figure | Description | License |
|--------|------|--------|-------------|---------|
| [Barrett & Keat 2004](https://doi.org/10.1148/rg.246045065) | Paper | Fig. 7 | Artifacts in CT: Recognition and Avoidance — beam hardening before/after correction | -- |
| [UTCT — Artifacts and Partial-Volume Effects](https://www.ctlab.geo.utexas.edu/about-ct/artifacts-and-partial-volume-effects/) | Facility docs | Multiple | University of Texas CT Lab — real CT artifact examples including beam hardening cupping | Public |
| [Chen et al. 2025](https://doi.org/10.3390/s25072088) | Paper | Figs 3--5 | VGG-based beam hardening correction — before/after comparisons on real CT data | CC BY 4.0 |

**Key references with published before/after comparisons:**
- **Barrett & Keat (2004)**: Fig. 7 shows beam hardening cupping artifact before/after correction in clinical CT. DOI: 10.1148/rg.246045065
- **Chen et al. (2025)**: Figs 3-5 show VGG-based beam hardening correction before/after on real CT data. DOI: 10.3390/s25072088

> **Recommended reference**: [UTCT — Artifacts and Partial-Volume Effects (University of Texas CT Lab)](https://www.ctlab.geo.utexas.edu/about-ct/artifacts-and-partial-volume-effects/)

## Related Resources

- [Harmonics contamination](../spectroscopy/harmonics_contamination.md) — Related spectral contamination issue
- [Streak artifact](../tomography/streak_artifact.md) — Often co-occurs with beam hardening near dense objects
