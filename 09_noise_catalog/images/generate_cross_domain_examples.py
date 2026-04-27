#!/usr/bin/env python3
"""
generate_cross_domain_examples.py

Generates synthetic before/after PNG pairs for the 13 new cross-domain
noise catalog entries. Self-contained: requires only numpy, scipy, matplotlib.

Output: 13 PNG files saved to the same directory as this script.

License: MIT (synthetic data only, no external datasets)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import (
    median_filter, uniform_filter, gaussian_filter, rotate
)
from scipy.interpolate import interp1d

FIGSIZE = (10, 4.5)
DPI = 300
CMAP = "gray"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _savefig(fig, filename):
    path = os.path.join(SCRIPT_DIR, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> saved {filename}")


def shepp_logan_phantom(n=256):
    """Generate a Shepp-Logan phantom on an n×n grid."""
    ellipses = [
        (+1.0, 0.6900, 0.9200, 0.0000, 0.0000, 0),
        (-0.8, 0.6624, 0.8740, 0.0000, -0.0184, 0),
        (-0.2, 0.1100, 0.3100, 0.2200, 0.0000, -18),
        (-0.2, 0.1600, 0.4100, -0.2200, 0.0000, 18),
        (+0.1, 0.2100, 0.2500, 0.0000, 0.3500, 0),
        (+0.1, 0.0460, 0.0460, 0.0000, 0.1000, 0),
        (+0.1, 0.0460, 0.0460, 0.0000, -0.1000, 0),
        (+0.1, 0.0460, 0.0230, -0.0800, -0.6050, 0),
        (+0.1, 0.0230, 0.0230, 0.0000, -0.6050, 0),
        (+0.1, 0.0230, 0.0460, 0.0600, -0.6050, 0),
    ]
    img = np.zeros((n, n), dtype=np.float64)
    coords = np.linspace(-1, 1, n)
    xg, yg = np.meshgrid(coords, coords)
    for A, a, b, x0, y0, phi_deg in ellipses:
        phi = np.deg2rad(phi_deg)
        cos_p, sin_p = np.cos(phi), np.sin(phi)
        xr = cos_p * (xg - x0) + sin_p * (yg - y0)
        yr = -sin_p * (xg - x0) + cos_p * (yg - y0)
        mask = (xr / a) ** 2 + (yr / b) ** 2 <= 1.0
        img[mask] += A
    return img


# ===================================================================
# 1. Beam Hardening — cupping artifact
# ===================================================================
def generate_beam_hardening():
    print(" 1/13 Beam hardening ...")
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Simulate cupping: multiply by radial darkening profile
    Y, X = np.ogrid[:n, :n]
    cy, cx = n // 2, n // 2
    r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / (n / 2)
    cupping_factor = 1.0 - 0.25 * r ** 2  # parabolic cupping
    hardened = clean * cupping_factor

    # Correction: polynomial
    corrected = hardened / (cupping_factor + 1e-6)
    corrected = np.clip(corrected, 0, 1)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(hardened, cmap=CMAP, vmin=0, vmax=1)
    axes[0].set_title("Before: Beam Hardening\n(cupping artifact — center darkened)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=1)
    axes[1].set_title("After: Polynomial Cupping\nCorrection", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Beam Hardening — Medical CT / Synchrotron Pink-Beam", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "beam_hardening_before_after.png")


# ===================================================================
# 2. Truncation Artifact — bright edge from FOV clipping
# ===================================================================
def generate_truncation_artifact():
    print(" 2/13 Truncation artifact ...")
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Simulate truncation: zero out edges of sinogram-like data
    # Show as image with bright halo at FOV boundary
    mask = np.ones((n, n))
    Y, X = np.ogrid[:n, :n]
    r = np.sqrt((X - n // 2) ** 2 + (Y - n // 2) ** 2)
    fov_radius = n * 0.38
    mask[r > fov_radius] = 0
    # Create bright edge artifact
    edge_ring = np.exp(-((r - fov_radius) ** 2) / (2 * 5 ** 2)) * 0.6
    truncated = clean * mask + edge_ring * mask
    truncated = np.clip(truncated, 0, 1)

    # Corrected: smooth edge transition
    smooth_mask = 1.0 / (1.0 + np.exp((r - fov_radius) / 3))
    corrected = clean * smooth_mask
    corrected = corrected / (corrected.max() + 1e-10)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(truncated, cmap=CMAP, vmin=0, vmax=0.8)
    axes[0].set_title("Before: Truncation Artifact\n(bright halo at FOV boundary)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=0.8)
    axes[1].set_title("After: Sinogram Extrapolation\nCorrection", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Truncation Artifact — Local/Interior Tomography", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "truncation_artifact_before_after.png")


# ===================================================================
# 3. Scatter Artifact — reduced contrast + cupping
# ===================================================================
def generate_scatter_artifact():
    print(" 3/13 Scatter artifact ...")
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Simulate scatter: add broad low-freq background + reduce contrast
    scatter_bg = gaussian_filter(clean, sigma=40) * 0.4
    scattered = clean * 0.6 + scatter_bg + 0.05
    scattered = np.clip(scattered, 0, 1)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(scattered, cmap=CMAP, vmin=0, vmax=1)
    axes[0].set_title("Before: Scatter Artifact\n(reduced contrast + haze)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(clean, cmap=CMAP, vmin=0, vmax=1)
    axes[1].set_title("After: Scatter Kernel\nSubtraction", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Scatter Artifact — Cone-Beam CT / SAXS", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "scatter_artifact_before_after.png")


# ===================================================================
# 4. Gibbs Ringing — oscillations near sharp edges
# ===================================================================
def generate_gibbs_ringing():
    print(" 4/13 Gibbs ringing ...")
    n = 256
    # Sharp-edge phantom: circle with step function
    Y, X = np.ogrid[:n, :n]
    r = np.sqrt((X - n // 2) ** 2 + (Y - n // 2) ** 2)
    sharp = np.zeros((n, n))
    sharp[r < 60] = 1.0
    sharp[(r >= 60) & (r < 90)] = 0.5

    # Simulate Gibbs by truncating Fourier spectrum
    F = np.fft.fftshift(np.fft.fft2(sharp))
    mask = np.zeros((n, n))
    mask_r = 50
    Y2, X2 = np.ogrid[:n, :n]
    mask[np.sqrt((X2 - n // 2) ** 2 + (Y2 - n // 2) ** 2) <= mask_r] = 1.0
    F_truncated = F * mask
    gibbs_image = np.real(np.fft.ifft2(np.fft.ifftshift(F_truncated)))

    # Correction: Hamming apodization
    hamming_mask = np.zeros((n, n))
    for yi in range(n):
        for xi in range(n):
            rr = np.sqrt((xi - n // 2) ** 2 + (yi - n // 2) ** 2)
            if rr <= mask_r:
                hamming_mask[yi, xi] = 0.54 + 0.46 * np.cos(np.pi * rr / mask_r)
    F_apodized = F * hamming_mask
    corrected = np.real(np.fft.ifft2(np.fft.ifftshift(F_apodized)))

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmin, vmax = -0.1, 1.1
    axes[0].imshow(gibbs_image, cmap=CMAP, vmin=vmin, vmax=vmax)
    axes[0].set_title("Before: Gibbs Ringing\n(oscillations at sharp edges)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=vmin, vmax=vmax)
    axes[1].set_title("After: Hamming Apodization\n(ringing suppressed)", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Gibbs Ringing — MRI / Coherent Imaging / EXAFS FT", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "gibbs_ringing_before_after.png")


# ===================================================================
# 5. Metal Artifact — starburst streaks from dense object
# ===================================================================
def generate_metal_artifact():
    print(" 5/13 Metal artifact ...")
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Add metal insert (very high attenuation)
    Y, X = np.ogrid[:n, :n]
    metal = np.sqrt((X - 170) ** 2 + (Y - 140) ** 2) < 12
    clean_with_metal = clean.copy()
    clean_with_metal[metal] = 3.0

    # Simulate metal artifact: radial streaks from metal location
    rng = np.random.default_rng(42)
    angles = np.linspace(0, 2 * np.pi, 60)
    streak_img = np.zeros((n, n))
    for angle in angles:
        length = rng.integers(40, 120)
        for t in range(length):
            yi = int(140 + t * np.sin(angle))
            xi = int(170 + t * np.cos(angle))
            if 0 <= yi < n and 0 <= xi < n:
                streak_img[yi, xi] += rng.uniform(-0.3, 0.3) * (1 - t / length)
    streak_img = gaussian_filter(streak_img, sigma=1.5)
    artifacted = clean_with_metal + streak_img
    artifacted = np.clip(artifacted, 0, 2)

    # Corrected: inpaint metal region, remove streaks
    corrected = clean.copy()  # idealized correction

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(artifacted, cmap=CMAP, vmin=0, vmax=1.2)
    axes[0].set_title("Before: Metal Artifact\n(starburst streaks from implant)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=1.2)
    axes[1].set_title("After: MAR Sinogram\nInpainting", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Metal Artifact — CT with Dense Inclusions", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "metal_artifact_before_after.png")


# ===================================================================
# 6. Shot Noise (Low-Dose EM/Cryo-EM)
# ===================================================================
def generate_shot_noise():
    print(" 6/13 Shot noise (low-dose) ...")
    n = 256
    rng = np.random.default_rng(55)

    # Simulate a "particle" image: circular object with internal structure
    Y, X = np.ogrid[:n, :n]
    particle = np.zeros((n, n))
    # Main body
    r = np.sqrt((X - n // 2) ** 2 + (Y - n // 2) ** 2)
    particle[r < 80] = 0.5
    particle[r < 40] = 0.8
    # Internal features
    for cx, cy, rad, val in [(90, 100, 15, 0.7), (160, 140, 20, 0.6),
                              (128, 170, 12, 0.9), (140, 90, 10, 0.75)]:
        feat_r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        particle[feat_r < rad] = val
    particle = gaussian_filter(particle, sigma=2)

    # Very low dose: ~5 e-/pixel
    dose = 5
    noisy = rng.poisson(particle * dose).astype(float) / dose

    # Averaged (simulate 100 particles averaged)
    averaged = particle + rng.normal(0, 0.02, (n, n))

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(noisy, cmap=CMAP, vmin=0, vmax=1.2)
    axes[0].set_title("Before: Single Low-Dose Image\n(~5 e⁻/pixel — SNR < 0.1)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(averaged, cmap=CMAP, vmin=0, vmax=1.2)
    axes[1].set_title("After: Class Average\n(100 particles aligned & averaged)", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Shot Noise — Cryo-EM / Low-Dose Synchrotron", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "shot_noise_low_dose_before_after.png")


# ===================================================================
# 7. CTF Artifact — contrast reversals and Thon rings
# ===================================================================
def generate_ctf_artifact():
    print(" 7/13 CTF artifact ...")
    n = 256
    # Simple object
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Simulate CTF modulation in Fourier space
    Y, X = np.ogrid[:n, :n]
    qy = (Y - n // 2) / n
    qx = (X - n // 2) / n
    q2 = qx ** 2 + qy ** 2

    # CTF = sin(π λ Δf q² - π/2 Cs λ³ q⁴)
    defocus = 2.0  # arbitrary units
    ctf = np.sin(np.pi * defocus * q2 * 1e4 - 0.5 * np.pi * q2 ** 2 * 1e6)

    F = np.fft.fftshift(np.fft.fft2(clean))
    F_ctf = F * ctf
    ctf_image = np.real(np.fft.ifft2(np.fft.ifftshift(F_ctf)))

    # Wiener correction
    snr = 5.0
    wiener = np.conj(ctf) / (ctf ** 2 + 1.0 / snr)
    F_corrected = F_ctf * wiener
    corrected = np.real(np.fft.ifft2(np.fft.ifftshift(F_corrected)))

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    v = np.percentile(np.abs(ctf_image), 99)
    axes[0].imshow(ctf_image, cmap=CMAP, vmin=-v, vmax=v)
    axes[0].set_title("Before: CTF Modulation\n(contrast reversals)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=-v * 0.5, vmax=v * 0.5)
    axes[1].set_title("After: Wiener CTF\nCorrection", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("CTF Artifact — TEM / Zernike Phase-Contrast X-ray", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "ctf_artifact_before_after.png")


# ===================================================================
# 8. Drift & Vibration — directional blur and scan distortion
# ===================================================================
def generate_drift_vibration():
    print(" 8/13 Drift & vibration ...")
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)

    # Simulate drift: progressive shift per scan line
    drifted = np.zeros_like(clean)
    for row in range(n):
        shift = int(row * 0.08)  # ~20 pixels total drift
        drifted[row, :] = np.roll(clean[row, :], shift)

    # Corrected: realign each line
    corrected = np.zeros_like(clean)
    for row in range(n):
        shift = int(row * 0.08)
        corrected[row, :] = np.roll(drifted[row, :], -shift)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(drifted, cmap=CMAP, vmin=0, vmax=1)
    axes[0].set_title("Before: Specimen Drift\n(progressive horizontal shift)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=1)
    axes[1].set_title("After: Cross-Correlation\nDrift Correction", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Drift & Vibration — SEM/TEM / Nanoprobe Synchrotron", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "drift_vibration_before_after.png")


# ===================================================================
# 9. Parasitic Scattering (SAXS) — low-q upturn
# ===================================================================
def generate_parasitic_scattering():
    print(" 9/13 Parasitic scattering ...")
    rng = np.random.default_rng(33)
    q = np.logspace(-2, 0, 500)

    # True SAXS signal: Guinier + Porod
    Rg = 5.0
    I_true = 100 * np.exp(-q ** 2 * Rg ** 2 / 3) + 0.1 * q ** (-4) + 0.01

    # Parasitic scattering: steep power law at low q
    I_parasitic = 500 * q ** (-4) * np.exp(-q * 10)
    I_measured = I_true + I_parasitic + rng.normal(0, 0.5, len(q))
    I_measured = np.clip(I_measured, 0.001, None)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].loglog(q, I_measured, 'b-', alpha=0.8, lw=1.2)
    axes[0].loglog(q, I_parasitic, 'r--', alpha=0.5, lw=1, label='Parasitic')
    axes[0].set_xlabel("q (Å⁻¹)")
    axes[0].set_ylabel("I(q)")
    axes[0].set_title("Before: With Parasitic Scattering\n(steep low-q upturn)", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(q, I_true, 'b-', lw=1.2)
    axes[1].set_xlabel("q (Å⁻¹)")
    axes[1].set_ylabel("I(q)")
    axes[1].set_title("After: Buffer Subtracted\n(true Guinier region visible)", fontsize=10)
    fig.suptitle("Parasitic Scattering — SAXS/WAXS", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "parasitic_scattering_before_after.png")


# ===================================================================
# 10. Ice Rings — powder rings in diffraction pattern
# ===================================================================
def generate_ice_rings():
    print("10/13 Ice rings ...")
    rng = np.random.default_rng(77)
    n = 512

    # Simulate 2D diffraction pattern with Bragg spots
    Y, X = np.ogrid[:n, :n]
    r = np.sqrt((X - n // 2) ** 2 + (Y - n // 2) ** 2)

    # Background: smooth radial falloff
    pattern = 100 / (r + 10) ** 1.5
    # Add Bragg-like spots
    for _ in range(200):
        sx, sy = rng.integers(100, n - 100, 2)
        sr = np.sqrt((X - sx) ** 2 + (Y - sy) ** 2)
        pattern += rng.uniform(50, 300) * np.exp(-(sr ** 2) / 4)
    pattern += rng.poisson(5, (n, n))

    # Add ice rings at specific radii (simulating d-spacings)
    ice_radii = [80, 95, 110, 160, 200]  # pixels
    ice_pattern = pattern.copy()
    for ir in ice_radii:
        ring = np.exp(-((r - ir) ** 2) / (2 * 2 ** 2))
        ice_pattern += ring * rng.uniform(80, 200)

    # Corrected: mask out ice ring regions
    corrected = ice_pattern.copy()
    for ir in ice_radii:
        mask = np.abs(r - ir) < 4
        # Interpolate from neighbors
        inner = (np.abs(r - (ir - 6)) < 2) & (r > 0)
        outer = (np.abs(r - (ir + 6)) < 2)
        avg_val = (ice_pattern[inner].mean() + ice_pattern[outer].mean()) / 2
        corrected[mask] = avg_val + rng.normal(0, 3, mask.sum())

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmax = np.percentile(ice_pattern, 98)
    axes[0].imshow(np.log1p(ice_pattern), cmap="viridis", vmin=0, vmax=np.log1p(vmax))
    axes[0].set_title("Before: Ice Rings\n(powder rings at known d-spacings)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(np.log1p(corrected), cmap="viridis", vmin=0, vmax=np.log1p(vmax))
    axes[1].set_title("After: Ice Ring Masking\n& Interpolation", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Ice Rings — Macromolecular Crystallography", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "ice_rings_before_after.png")


# ===================================================================
# 11. Phase Wrapping — 2π discontinuities in phase map
# ===================================================================
def generate_phase_wrapping():
    print("11/13 Phase wrapping ...")
    n = 256
    Y, X = np.ogrid[:n, :n]

    # True phase: smooth ramp + sphere-like object (range > 2π)
    true_phase = (0.02 * (X - n // 2) + 0.01 * (Y - n // 2)
                  + 4.0 * np.exp(-((X - 130) ** 2 + (Y - 128) ** 2) / (2 * 40 ** 2))
                  - 2.0 * np.exp(-((X - 180) ** 2 + (Y - 100) ** 2) / (2 * 25 ** 2)))

    # Wrapped phase
    wrapped = np.angle(np.exp(1j * true_phase))

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(wrapped, cmap="twilight", vmin=-np.pi, vmax=np.pi)
    axes[0].set_title("Before: Wrapped Phase\n(2π discontinuities)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(true_phase, cmap="twilight", vmin=true_phase.min(), vmax=true_phase.max())
    axes[1].set_title("After: Unwrapped Phase\n(quality-guided unwrapping)", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Phase Wrapping — Phase-Contrast Imaging / CDI", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "phase_wrapping_before_after.png")


# ===================================================================
# 12. Cosmic Ray / Outlier — L.A.Cosmic-style detection
# ===================================================================
def generate_cosmic_ray():
    print("12/13 Cosmic ray / outlier ...")
    rng = np.random.default_rng(42)
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / (clean.max() + 1e-10)
    clean += rng.normal(0, 0.02, (n, n))

    # Inject cosmic rays: bright points and short tracks
    cr_image = clean.copy()
    # Point CRs
    for _ in range(100):
        x, y = rng.integers(5, n - 5, 2)
        cr_image[y, x] = rng.uniform(2, 8)
    # Track CRs (short lines)
    for _ in range(15):
        x0, y0 = rng.integers(10, n - 10, 2)
        angle = rng.uniform(0, 2 * np.pi)
        length = rng.integers(3, 12)
        for t in range(length):
            xi = int(x0 + t * np.cos(angle))
            yi = int(y0 + t * np.sin(angle))
            if 0 <= xi < n and 0 <= yi < n:
                cr_image[yi, xi] = rng.uniform(3, 7)

    # Correction: median replacement
    corrected = cr_image.copy()
    med = median_filter(cr_image, size=5)
    diff = cr_image - med
    threshold = 5 * np.std(diff)
    cr_mask = diff > threshold
    corrected[cr_mask] = med[cr_mask]

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(cr_image, cmap=CMAP, vmin=0, vmax=1.2)
    axes[0].set_title("Before: Cosmic Rays\n(bright points & tracks)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=1.2)
    axes[1].set_title("After: L.A.Cosmic Detection\n& Median Replacement", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Cosmic Ray / Outlier — Astronomy → Synchrotron", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "cosmic_ray_before_after.png")


# ===================================================================
# 13. Afterglow / Persistence — ghost from previous exposure
# ===================================================================
def generate_afterglow():
    print("13/13 Afterglow / persistence ...")
    n = 256
    rng = np.random.default_rng(88)

    # "Previous" bright exposure: a star/source
    Y, X = np.ogrid[:n, :n]
    prev_exposure = 2.0 * np.exp(-((X - 100) ** 2 + (Y - 120) ** 2) / (2 * 20 ** 2))

    # Current dim exposure: different field
    current = shepp_logan_phantom(n)
    current = current - current.min()
    current = current / (current.max() + 1e-10) * 0.5

    # Afterglow: fraction of previous exposure persists
    afterglow_fraction = 0.15
    with_ghost = current + afterglow_fraction * prev_exposure
    with_ghost += rng.normal(0, 0.02, (n, n))
    with_ghost = np.clip(with_ghost, 0, None)

    # Corrected: subtract estimated afterglow
    corrected = with_ghost - afterglow_fraction * prev_exposure
    corrected = np.clip(corrected, 0, None)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmax = np.percentile(with_ghost, 99.5)
    axes[0].imshow(with_ghost, cmap=CMAP, vmin=0, vmax=vmax)
    axes[0].set_title("Before: Afterglow/Persistence\n(ghost of previous bright exposure)", fontsize=10)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP, vmin=0, vmax=vmax * 0.8)
    axes[1].set_title("After: Decay Model\nSubtraction", fontsize=10)
    axes[1].axis("off")
    fig.suptitle("Afterglow/Persistence — Astronomy / Fast CT", fontsize=11, y=1.01)
    fig.tight_layout()
    _savefig(fig, "afterglow_before_after.png")


# ===================================================================
# Main
# ===================================================================
def main():
    print(f"Output directory: {SCRIPT_DIR}")
    print("=" * 55)
    print("Generating cross-domain noise example images ...")
    print("=" * 55)

    generate_beam_hardening()
    generate_truncation_artifact()
    generate_scatter_artifact()
    generate_gibbs_ringing()
    generate_metal_artifact()
    generate_shot_noise()
    generate_ctf_artifact()
    generate_drift_vibration()
    generate_parasitic_scattering()
    generate_ice_rings()
    generate_phase_wrapping()
    generate_cosmic_ray()
    generate_afterglow()

    print("=" * 55)
    print("Done. All 13 cross-domain images generated.")


if __name__ == "__main__":
    main()
