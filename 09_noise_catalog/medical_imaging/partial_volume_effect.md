# Partial Volume Effect

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Medical CT / Synchrotron Tomography / Microscopy |
| **Noise Type** | Systematic |
| **Severity** | Major |
| **Frequency** | Always |
| **Detection Difficulty** | Moderate |
| **Origin Domain** | Medical Imaging (CT/PET) |

## Description

Partial volume effect (PVE) occurs when a single voxel contains a mixture of two or more materials, resulting in an averaged attenuation value that represents none of the actual materials. This causes blurring of boundaries, incorrect quantification, and artificial intermediate-density regions. It is fundamental to any discretized imaging modality and becomes critical when feature sizes approach the voxel resolution.

## Root Cause

- Finite voxel size → each voxel integrates signal from all materials within its volume
- Voxel straddles material boundary → CT value is weighted average of constituent materials
- Worse for: thick slices, coarse detector pitch, small features relative to voxel size
- In PET/SPECT: "spill-in" and "spill-out" of radiotracer signal across boundaries

## Quick Diagnosis

```python
import numpy as np

def detect_partial_volume(slice_2d, expected_values, tolerance=0.1):
    """Detect partial volume by finding voxels with intermediate values."""
    mask_intermediate = np.ones_like(slice_2d, dtype=bool)
    for val in expected_values:
        mask_intermediate &= np.abs(slice_2d - val) > tolerance * val
    pve_fraction = mask_intermediate.sum() / slice_2d.size
    print(f"Partial volume voxels: {pve_fraction:.1%}")
    return mask_intermediate
```

## Detection Methods

### Visual Indicators

- Blurred boundaries between distinct materials
- Intermediate gray values at edges (not matching any known material)
- Apparent "halo" around small dense features
- Small objects appear larger and less dense than reality

### Automated Detection

```python
import numpy as np
from scipy import ndimage

def edge_pve_analysis(slice_2d, sigma=1.0):
    """Quantify PVE at material boundaries using gradient analysis."""
    grad_mag = ndimage.gaussian_gradient_magnitude(slice_2d, sigma)
    # Identify boundary region
    threshold = np.percentile(grad_mag, 90)
    boundary_mask = grad_mag > threshold
    # Measure transition width
    return boundary_mask, grad_mag
```

## Correction Methods

### Traditional Approaches

1. **Higher resolution:** Smaller voxel size (obvious but costly in dose/time)
2. **Sub-voxel segmentation:** Model each voxel as mixture of known materials
3. **Deconvolution-based PVC:** Apply geometric transfer matrix (GTM) correction
4. **Multi-resolution fusion:** Combine low-res volumetric with high-res surface data

### AI/ML Approaches

- **Super-resolution CNNs:** Learn sub-voxel material distribution
- **Segmentation-aware reconstruction:** Joint segmentation-reconstruction frameworks
- **PVC-Net:** Partial volume correction networks for PET/SPECT

## Key References

- **Kessler et al. (1984)** — Analysis of partial volume effects in emission CT
- **Soret et al. (2007)** — "Partial-volume effect in PET tumor imaging" (review)
- **Van Eijnatten et al. (2018)** — PVE in CT-based 3D printing
- **Erlandsson et al. (2012)** — "A review of partial volume correction techniques for PET"

## Relevance to Synchrotron Data

| Scenario | Relevance |
|----------|-----------|
| Nano-tomography | Critical for features near resolution limit |
| XRF microscopy | Sub-pixel elemental mixing at boundaries |
| Multi-phase materials | Voxels at grain boundaries show averaged density |
| Porosity quantification | Small pores underestimated; porosity analysis biased |

## Related Resources

- [Probe blurring](../xrf_microscopy/probe_blurring.md) — Analogous spatial averaging in XRF
- [Low-dose noise](../tomography/low_dose_noise.md) — Noise compounds PVE measurement
