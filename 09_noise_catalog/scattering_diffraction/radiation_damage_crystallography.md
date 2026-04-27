# Radiation Damage in Crystallography

## Classification

| Attribute | Value |
|-----------|-------|
| **Modality** | Macromolecular Crystallography (MX) / Powder Diffraction |
| **Noise Type** | Systematic |
| **Severity** | Critical |
| **Frequency** | Common |
| **Detection Difficulty** | Moderate |
| **Origin Domain** | Synchrotron Crystallography (All MX beamlines) |

## Description

Radiation damage in crystallography is the progressive deterioration of diffraction data quality due to X-ray-induced structural changes in the crystal. Primary damage (photoelectric absorption) creates free radicals that cause secondary chemical damage — disulfide bond breakage, decarboxylation of acidic residues, and eventual loss of crystalline order. This is distinct from the spectroscopic radiation damage already cataloged; here the focus is on crystallographic signatures and their impact on structure determination.

## Root Cause

- **Primary damage:** Photoelectric absorption creates fast electrons → ionization cascade
- **Secondary damage:** Free radicals (OH·, e⁻_aq) diffuse and attack specific chemical groups
- **Global damage:** Increasing B-factors, loss of high-resolution diffraction, unit cell expansion
- **Specific damage:** Preferential destruction at disulfide bonds, carboxylates, methionines
- Henderson limit: ~2×10⁷ Gy (20 MGy) for cryo-cooled protein crystals at 100K
- Rate depends on: dose rate, temperature, sample composition, solvent content

## Quick Diagnosis

```python
import numpy as np

def track_radiation_damage(frame_intensities, resolution_shells):
    """Track intensity decay per resolution shell across frames."""
    n_frames = len(frame_intensities)
    for shell_idx, shell_name in enumerate(resolution_shells):
        intensities = [f[shell_idx] for f in frame_intensities]
        decay = intensities[-1] / intensities[0]
        print(f"Shell {shell_name}: I_last/I_first = {decay:.3f}")
        if decay < 0.7:
            print(f"  ⚠ Significant radiation damage in {shell_name} shell")
    # Check unit cell expansion
    # unit_cells = [get_unit_cell(frame) for frame in frames]
    # expansion = (unit_cells[-1] - unit_cells[0]) / unit_cells[0]
```

## Detection Methods

### Visual Indicators

- Diffraction spots fade progressively during data collection (especially high-resolution)
- Wilson plot shows increasing B-factor with accumulated dose
- Unit cell dimensions increase (0.1-1% over full dataset)
- R_merge increases for later frames
- Difference Fourier maps show negative density at disulfides, positive at carboxylates

### Automated Detection

```python
import numpy as np

def dose_dependent_bfactor(frame_number, mean_b_per_frame):
    """Fit linear dose-dependent B-factor increase."""
    slope, intercept = np.polyfit(frame_number, mean_b_per_frame, 1)
    print(f"B-factor increase rate: {slope:.2f} Å²/frame")
    print(f"Suggests {'severe' if slope > 1.0 else 'moderate' if slope > 0.3 else 'mild'} damage")
    return slope
```

## Correction Methods

### Prevention

1. **Cryo-cooling (100K):** Slows radical diffusion ~100× vs room temperature
2. **Helical data collection:** Translate crystal during rotation to spread dose
3. **Multi-crystal strategy:** Merge partial datasets from multiple crystals
4. **Beam attenuation:** Reduce flux density (trade-off with exposure time)
5. **Radical scavengers:** Ascorbate, sodium nitrate in cryoprotectant

### Data Processing Corrections

1. **Zero-dose extrapolation:** Extrapolate intensities to zero dose using decay curves
2. **Frame rejection:** Discard frames beyond Henderson dose limit
3. **Dose-weighted scaling:** Weight frames inversely by accumulated dose
4. **RIDL (Radiation-Induced Density Loss):** Per-atom damage metric analysis

```python
def zero_dose_extrapolation(intensities_per_frame, doses):
    """Extrapolate reflection intensities to zero dose."""
    corrected = np.zeros(intensities_per_frame.shape[1])
    for i in range(intensities_per_frame.shape[1]):
        I_vs_dose = intensities_per_frame[:, i]
        valid = I_vs_dose > 0
        if valid.sum() >= 2:
            # Linear fit: I(d) = I(0) + slope * d
            slope, I0 = np.polyfit(doses[valid], I_vs_dose[valid], 1)
            corrected[i] = I0  # Zero-dose intensity
        else:
            corrected[i] = I_vs_dose[valid].mean() if valid.any() else 0
    return corrected
```

### Software Tools

- **RADDOSE-3D** — Dose estimation for MX experiments
- **BEST** — Optimal data collection strategy considering dose
- **RIDL** — Radiation-Induced Density Loss analysis
- **AIMLESS / XSCALE** — Dose-dependent scaling

## Key References

- **Garman & Weik (2023)** — "Radiation damage in macromolecular crystallography" — comprehensive review
- **Henderson (1990)** — "Cryo-protection of protein crystals against radiation damage"
- **Zeldin et al. (2013)** — "RADDOSE-3D: time- and space-resolved modelling of dose in MX"
- **Bury et al. (2018)** — "RIDL: radiation-induced density loss analysis"
- **de la Mora et al. (2020)** — "Radiation damage and dose limits in serial synchrotron crystallography"

## Facility Benchmarks

| Facility | Approach |
|----------|----------|
| ESRF (MASSIF) | Fully automated damage-aware data collection |
| Diamond I04 | ISPyB dose tracking + BEST strategy |
| SPring-8 ZOO | Multi-crystal serial approach |
| APS GM/CA | Rastered/vector data collection |
| SLS PXI/PXII | Dose-stratified processing in adp |
| NSLS-II FMX | Eiger detector — fast readout minimizes per-frame dose |

## Related Resources

- [Radiation damage (spectroscopy)](../spectroscopy/radiation_damage.md) — Spectroscopic radiation damage (XANES/EXAFS)
- [Beam intensity drop](../tomography/beam_intensity_drop.md) — Related time-dependent signal change
