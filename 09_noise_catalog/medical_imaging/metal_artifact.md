# Metal Artifact

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Medical CT / Synchrotron Tomography |
| **Noise Type** | Systematic |
| **Severity** | Critical |
| **Frequency** | Occasional |
| **Detection Difficulty** | Easy |
| **Origin Domain** | Medical Imaging (CT) |

## Visual Examples

![Before and after — metal artifact](../images/metal_artifact_before_after.png)

> **Image source:** Synthetic phantom with dense metallic insert. Left: starburst streaks radiating from metal object. Right: after MAR sinogram inpainting. MIT license.

## Description

Metal artifacts are severe image distortions caused by highly attenuating metallic objects (implants, dental fillings, surgical hardware). They manifest as bright/dark streaks, "starburst" patterns, and signal voids radiating from the metal. This is a compound artifact caused by the simultaneous occurrence of beam hardening, photon starvation, scatter, and partial volume effects near the metal object.

**Synchrotron relevance:** Directly relevant when imaging samples containing metallic inclusions, electrodes, catalysts with heavy metal nanoparticles, or composite materials with high-Z components.

## Root Cause

- **Photon starvation:** Metal absorbs nearly all photons → near-zero transmission → very noisy projections
- **Beam hardening:** Extreme spectral shift through thick metal
- **Nonlinear partial volume:** Metal-tissue voxels have extreme attenuation mismatch
- **Scatter:** Metal produces significant scatter signal
- Combined effect → corrupted sinogram bands → streaks in reconstruction

## Quick Diagnosis

```python
import numpy as np

def detect_metal_projections(sinogram, threshold_percentile=99.5):
    """Identify projections severely affected by metal."""
    # Metal causes very high attenuation → near-zero transmission
    log_sino = -np.log(sinogram + 1e-10)
    high_atten = log_sino > np.percentile(log_sino, threshold_percentile)
    metal_angles = np.where(high_atten.any(axis=1))[0]
    print(f"Metal-affected projections: {len(metal_angles)} / {sinogram.shape[0]}")
    return metal_angles, high_atten
```

## Detection Methods

### Visual Indicators

- Bright/dark streaks radiating from dense object ("starburst")
- Signal void or saturation region at metal location
- Loss of all detail in region surrounding metal
- Streaks connect pairs of metal objects (e.g., bilateral hip implants)

### Automated Detection

```python
import numpy as np
from scipy.ndimage import label

def segment_metal_regions(recon_slice, threshold=None):
    """Segment metal regions by extreme attenuation values."""
    if threshold is None:
        threshold = np.percentile(recon_slice, 99.5)
    metal_mask = recon_slice > threshold
    labeled, n_objects = label(metal_mask)
    print(f"Metal objects detected: {n_objects}")
    return metal_mask, labeled
```

## Correction Methods

### Traditional Approaches

1. **MAR (Metal Artifact Reduction):** Segment metal in recon → forward project → replace sinogram metal-trace → re-reconstruct
2. **NMAR (Normalized MAR):** Improved MAR with prior-image normalization (Meyer et al., 2010)
3. **Frequency split:** Separate low/high frequency and correct independently
4. **Iterative reconstruction:** Model metal physics in forward projector

```python
def simple_mar_sinogram_inpainting(sinogram, metal_trace_mask):
    """Replace metal-affected sinogram regions with interpolation."""
    import scipy.interpolate as interp
    corrected = sinogram.copy()
    for i in range(sinogram.shape[0]):
        row = sinogram[i, :]
        mask = metal_trace_mask[i, :]
        if mask.any():
            good_idx = np.where(~mask)[0]
            bad_idx = np.where(mask)[0]
            if len(good_idx) > 2:
                f = interp.interp1d(good_idx, row[good_idx], kind='linear',
                                     fill_value='extrapolate')
                corrected[i, bad_idx] = f(bad_idx)
    return corrected
```

### AI/ML Approaches

- **ADN (Artifact Disentanglement Network):** Liao et al., 2019 — learns to separate artifact from image
- **DuDoNet:** Lin et al., 2019 — dual-domain (sinogram + image) correction network
- **cGAN-MAR:** Conditional GAN for metal artifact reduction

## Key References

- **Meyer et al. (2010)** — "Normalized metal artifact reduction (NMAR)"
- **Gjesteby et al. (2016)** — "Metal artifact reduction in CT: a comprehensive review"
- **Liao et al. (2019)** — "ADN: Artifact Disentanglement Network for metal artifact reduction"
- **Lin et al. (2019)** — "DuDoNet: Dual Domain Network for CT Metal Artifact Reduction"

## Relevance to Synchrotron Data

| Scenario | Relevance |
|----------|-----------|
| Metal-containing composites | Direct — metal inclusions in materials science samples |
| Battery / fuel cell imaging | Electrodes with heavy metals (Pt, Ni, etc.) |
| Geological samples | Dense mineral grains create similar artifacts |
| In-situ experiments | Metal sample holders, thermocouples, pressure cells |
| Cultural heritage imaging | Metal fasteners, gilding in historical artifacts |

## Real-World Before/After Examples

The following published sources provide real experimental before/after comparisons:

| Source | Type | Figure | Description | License |
|--------|------|--------|-------------|---------|
| [Boas & Fleischmann 2012](https://doi.org/10.4329/wjr.v4.i4.156) | Paper | Figs 1--4 | CT artifacts: Causes and reduction techniques — comprehensive clinical metal artifact before/after examples | -- |
| [Katsura et al. 2018](https://doi.org/10.1148/rg.2018170102) | Paper | Multiple | Current and novel techniques for metal artifact reduction at CT — MAR techniques with before/after comparisons | -- |
| [Liao et al. 2019 — ADN](https://doi.org/10.1016/j.media.2019.101554) | Paper | Multiple | Artifact Disentanglement Network for Metal Artifact Reduction — real clinical CT before/after MAR | -- |

**Key references with published before/after comparisons:**
- **Boas & Fleischmann (2012)**: Figs 1-4 show comprehensive metal artifact before/after correction examples. DOI: 10.4329/wjr.v4.i4.156
- **Katsura et al. (2018)**: RadioGraphics review of current and novel MAR techniques with clinical before/after examples. DOI: 10.1148/rg.2018170102

> **Recommended reference**: [Boas & Fleischmann 2012 — CT artifacts: Causes and reduction techniques (World J. Radiol.)](https://doi.org/10.4329/wjr.v4.i4.156)

## Related Resources

- [Streak artifact](../tomography/streak_artifact.md) — Overlap with metal-induced streaks
- [Beam hardening](beam_hardening.md) — Contributing mechanism to metal artifacts
