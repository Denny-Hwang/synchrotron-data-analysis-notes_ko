# Detector Gaps & Parallax

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Scattering / Diffraction / Tomography |
| **Noise Type** | Instrumental |
| **Severity** | Major |
| **Frequency** | Common |
| **Detection Difficulty** | Easy |
| **Origin Domain** | Synchrotron (Multi-facility: ESRF, Diamond, DESY, APS) |

## Description

Multi-module area detectors (Pilatus, Eiger, Jungfrau, Medipix) have physical gaps between sensor tiles where no photons are detected. These gaps create missing-data stripes in diffraction patterns, SAXS images, and tomographic projections. Parallax (depth-of-interaction) effects in thick sensors cause position-dependent point spread, where photons entering at oblique angles register at incorrect lateral positions.

## Root Cause

### Detector Gaps
- ASIC/sensor modules have dead borders (wire-bond pads, guard rings)
- Tiled detector: e.g., Pilatus 6M = 60 modules with ~7 pixel gaps between chips
- Lost data → missing Bragg reflections, incomplete azimuthal coverage in SAXS

### Parallax
- Thick sensors (450-1000 μm Si, 750 μm CdTe) have finite photon absorption depth
- Photons entering at oblique angle travel laterally before absorption
- Lateral displacement = absorption depth × tan(angle of incidence)
- Results in asymmetric PSF, position-dependent, worsening toward detector edges

## Quick Diagnosis

```python
import numpy as np

def find_detector_gaps(image_2d, threshold=0):
    """Identify detector gap regions (zero-count columns/rows)."""
    # Gaps: contiguous zero-value columns or rows
    col_sums = image_2d.sum(axis=0)
    row_sums = image_2d.sum(axis=1)
    gap_cols = np.where(col_sums <= threshold)[0]
    gap_rows = np.where(row_sums <= threshold)[0]
    # Group contiguous gaps
    def group_contiguous(arr):
        if len(arr) == 0:
            return []
        groups = [[arr[0]]]
        for v in arr[1:]:
            if v == groups[-1][-1] + 1:
                groups[-1].append(v)
            else:
                groups.append([v])
        return [(g[0], g[-1]) for g in groups]
    col_gaps = group_contiguous(gap_cols)
    row_gaps = group_contiguous(gap_rows)
    print(f"Column gaps: {col_gaps}")
    print(f"Row gaps: {row_gaps}")
    return col_gaps, row_gaps
```

## Detection Methods

### Visual Indicators

- **Gaps:** Regular grid of missing-data lines in detector image
- **Parallax:** Radial streaking of sharp features (Bragg peaks, beam center) toward detector edges
- Point spread function (PSF) becomes asymmetric and elongated at high angles

### Automated Detection

```python
import numpy as np

def measure_parallax_psf(image, peak_positions, box_size=20):
    """Measure PSF anisotropy at different detector positions."""
    results = []
    for y, x in peak_positions:
        box = image[y-box_size//2:y+box_size//2, x-box_size//2:x+box_size//2]
        if box.shape != (box_size, box_size):
            continue
        # Second moments → PSF shape
        yy, xx = np.mgrid[:box_size, :box_size]
        total = box.sum()
        if total <= 0:
            continue
        cy = (yy * box).sum() / total
        cx = (xx * box).sum() / total
        sigma_y = np.sqrt(((yy - cy)**2 * box).sum() / total)
        sigma_x = np.sqrt(((xx - cx)**2 * box).sum() / total)
        anisotropy = max(sigma_y, sigma_x) / (min(sigma_y, sigma_x) + 1e-10)
        results.append({'pos': (y, x), 'anisotropy': anisotropy})
    return results
```

## Correction Methods

### Gap Correction

1. **Multiple detector positions:** Collect data at 2+ offset positions, merge to fill gaps
2. **Azimuthal interpolation:** In SAXS, interpolate across gaps using azimuthal symmetry
3. **Mask and reconstruct:** Flag gaps as missing data, use iterative algorithms
4. **Virtual detector merging:** Software stitching for multi-panel detectors

### Parallax Correction

1. **Geometric correction:** Apply position-dependent shift based on known geometry
2. **Depth-of-interaction modeling:** Model photon absorption profile in sensor
3. **PSF deconvolution:** Position-dependent deconvolution

```python
def correct_parallax_shift(x_det, y_det, detector_distance, sensor_thickness,
                           mean_absorption_depth):
    """Correct pixel positions for parallax in thick sensor."""
    r_det = np.sqrt(x_det**2 + y_det**2)
    two_theta = np.arctan2(r_det, detector_distance)
    # Lateral shift due to parallax
    lateral_shift = mean_absorption_depth * np.tan(two_theta)
    # Correction: shift toward beam center
    correction_x = -lateral_shift * x_det / (r_det + 1e-10)
    correction_y = -lateral_shift * y_det / (r_det + 1e-10)
    return x_det + correction_x, y_det + correction_y
```

### Software Tools

- **pyFAI** (ESRF) — Detector gap handling, geometry correction, parallax-aware integration
- **DIALS** — Multi-panel detector geometry refinement
- **FIT2D** — Classic 2D integration with masking
- **NeXus/HDF5 detector geometry** — Standard detector description format

## Key References

- **Kraft et al. (2009)** — "Characterization and calibration of Pilatus detectors"
- **Henrich et al. (2009)** — "PILATUS: a single photon counting pixel detector"
- **Ashiotis et al. (2015)** — "pyFAI: a Python library for high performance azimuthal integration"
- **Hülsen et al. (2006)** — "Distortion calibration of the PILATUS detector"

## Facility Benchmarks

| Facility | Detector | Gap Handling |
|----------|----------|-------------|
| ESRF | Eiger2 CdTe | pyFAI with parallax correction |
| Diamond | Pilatus 6M / Eiger2 | DIALS multi-panel refinement |
| DESY | Lambda/Eiger | DAWN/pyFAI integration |
| SPring-8 | Pilatus3 / custom | BL-specific calibration |
| SLS | Eiger 16M | Native gap interpolation in processing pipeline |

## Real-World Before/After Examples

The following published sources provide real experimental before/after comparisons:

| Source | Type | Figure | Description | License |
|--------|------|--------|-------------|---------|
| [pyFAI documentation](https://pyfai.readthedocs.io/) | Software docs | Multiple | Gap filling, detector geometry correction, and azimuthal integration examples with real detector data | MIT |

> **Recommended reference**: [pyFAI — Python Fast Azimuthal Integration (ESRF)](https://pyfai.readthedocs.io/)

## Related Resources

- [Detector common issues](../cross_cutting/detector_common_issues.md) — General detector defects
- [Dead/hot pixel](../xrf_microscopy/dead_hot_pixel.md) — Individual pixel defects vs module gaps
- [Stitching artifact](../ptychography/stitching_artifact.md) — Related boundary/joining artifacts
