#!/usr/bin/env python3
"""
generate_examples.py

Generates synthetic before/after PNG pairs illustrating common synchrotron
noise types and their corrections. Fully self-contained: requires only
numpy, scipy, and matplotlib (no tomopy, no skimage, no external data).

Implements a minimal Shepp-Logan phantom, Radon transform, and filtered
back-projection (FBP) reconstruction using numpy/scipy FFT.

Output: 8 PNG files saved to the same directory as this script.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, uniform_filter
from scipy.interpolate import interp1d

# ---------------------------------------------------------------------------
# Global style settings
# ---------------------------------------------------------------------------
FIGSIZE = (10, 4.5)
DPI = 300
CMAP = "gray"

# Resolve output directory to the same folder as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _savefig(fig, filename):
    """Save figure with consistent style."""
    path = os.path.join(SCRIPT_DIR, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> saved {filename}")


# ===================================================================
# Minimal Shepp-Logan phantom (no skimage / no tomopy)
# ===================================================================

def shepp_logan_phantom(n=256):
    """
    Generate a Shepp-Logan phantom on an n×n grid.

    Uses the modified Shepp-Logan ellipse parameters so that contrast
    is visible in 8-bit-style images.
    """
    # Each row: (A, a, b, x0, y0, phi)  -- intensity, semi-axes, centre, angle
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
# Minimal Radon transform & filtered back-projection
# ===================================================================

def radon_transform(image, angles_deg):
    """
    Compute the Radon transform (sinogram) of a 2-D image for the
    given projection angles (in degrees).

    Parameters
    ----------
    image : 2-D ndarray (n x n)
    angles_deg : 1-D array of angles in degrees

    Returns
    -------
    sinogram : 2-D ndarray (n_det x n_angles), where n_det = n
    """
    n = image.shape[0]
    centre = n / 2.0
    sinogram = np.zeros((n, len(angles_deg)), dtype=np.float64)

    # Detector pixel positions (centred)
    det_pos = np.arange(n) - centre + 0.5

    for i, theta in enumerate(angles_deg):
        cos_t = np.cos(np.deg2rad(theta))
        sin_t = np.sin(np.deg2rad(theta))

        for d_idx, d in enumerate(det_pos):
            # Line integral along the ray at detector position d
            # Parameterise the ray: (x, y) = d*(cos, sin) + t*(-sin, cos)
            t_vals = det_pos  # use same sampling along the ray
            xs = d * cos_t - t_vals * sin_t + centre - 0.5
            ys = d * sin_t + t_vals * cos_t + centre - 0.5

            # Nearest-neighbour sampling
            xi = np.round(xs).astype(int)
            yi = np.round(ys).astype(int)
            valid = (xi >= 0) & (xi < n) & (yi >= 0) & (yi < n)
            sinogram[d_idx, i] = np.sum(image[yi[valid], xi[valid]])

    return sinogram


def fbp_reconstruct(sinogram, angles_deg):
    """
    Filtered back-projection reconstruction from a sinogram.

    Parameters
    ----------
    sinogram : 2-D ndarray (n_det x n_angles)
    angles_deg : 1-D array of angles in degrees

    Returns
    -------
    recon : 2-D ndarray (n_det x n_det)
    """
    n_det, n_angles = sinogram.shape
    centre = n_det / 2.0

    # --- Ram-Lak (ramp) filter in the frequency domain ---
    freqs = np.fft.fftfreq(n_det)
    ramp = np.abs(freqs)

    # Apply filter to each projection
    filtered = np.zeros_like(sinogram)
    for i in range(n_angles):
        proj_fft = np.fft.fft(sinogram[:, i])
        filtered[:, i] = np.real(np.fft.ifft(proj_fft * ramp))

    # --- Back-projection ---
    recon = np.zeros((n_det, n_det), dtype=np.float64)
    det_pos = np.arange(n_det) - centre + 0.5
    xg, yg = np.meshgrid(det_pos, det_pos)

    for i, theta in enumerate(angles_deg):
        cos_t = np.cos(np.deg2rad(theta))
        sin_t = np.sin(np.deg2rad(theta))
        # For each pixel, compute its projection onto the detector
        t = xg * cos_t + yg * sin_t  # detector coordinate
        # Interpolate the filtered projection at these detector positions
        interp_func = interp1d(det_pos, filtered[:, i],
                               kind="linear", bounds_error=False,
                               fill_value=0.0)
        recon += interp_func(t)

    recon *= np.pi / n_angles
    return recon


# ===================================================================
# Helper: quick sinogram + reconstruction at a given size
# ===================================================================

def _quick_phantom_and_sinogram(n=128, n_angles=180):
    """Return (phantom, sinogram, angles) at moderate resolution."""
    phantom = shepp_logan_phantom(n)
    angles = np.linspace(0, 180, n_angles, endpoint=False)
    sino = radon_transform(phantom, angles)
    return phantom, sino, angles


# ===================================================================
# 1. Ring artifact
# ===================================================================

def generate_ring_artifact():
    print("1/8  Ring artifact ...")
    phantom, sino, angles = _quick_phantom_and_sinogram(128, 180)

    # Inject a dead-pixel column into the sinogram (fixed detector element)
    sino_ring = sino.copy()
    dead_cols = [40, 41, 75]
    for c in dead_cols:
        sino_ring[c, :] *= 0.15  # reduce sensitivity significantly

    recon_ring = fbp_reconstruct(sino_ring, angles)

    # Simple ring-removal: replace dead column in sinogram with neighbours
    sino_fixed = sino_ring.copy()
    for c in dead_cols:
        sino_fixed[c, :] = 0.5 * (sino_fixed[c - 1, :] + sino_fixed[c + 1, :])
    recon_fixed = fbp_reconstruct(sino_fixed, angles)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(recon_ring, cmap=CMAP)
    axes[0].set_title("Before: Ring Artifact", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(recon_fixed, cmap=CMAP)
    axes[1].set_title("After: Ring Removal\n(sinogram interpolation)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "ring_artifact_before_after.png")


# ===================================================================
# 2. Zinger (outlier spikes in projections)
# ===================================================================

def generate_zinger():
    print("2/8  Zinger ...")
    phantom = shepp_logan_phantom(256)

    # Simulate a single projection image
    projection = phantom.copy()

    # Inject random high-intensity spots (zingers)
    rng = np.random.default_rng(42)
    n_zingers = 80
    zx = rng.integers(0, 256, n_zingers)
    zy = rng.integers(0, 256, n_zingers)
    proj_zinged = projection.copy()
    for x, y in zip(zx, zy):
        proj_zinged[y, x] = projection.max() * rng.uniform(3, 8)

    # Correction: 3×3 median filter
    proj_fixed = median_filter(proj_zinged, size=3)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmin, vmax = projection.min(), projection.max()
    axes[0].imshow(proj_zinged, cmap=CMAP, vmin=vmin, vmax=vmax * 1.2)
    axes[0].set_title("Before: Zingers (outlier spikes)", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(proj_fixed, cmap=CMAP, vmin=vmin, vmax=vmax * 1.2)
    axes[1].set_title("After: Median Filter (3×3)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "zinger_before_after.png")


# ===================================================================
# 3. Low-dose Poisson noise
# ===================================================================

def generate_low_dose_noise():
    print("3/8  Low-dose Poisson noise ...")
    phantom = shepp_logan_phantom(256)

    # Scale phantom to represent photon counts
    clean = phantom - phantom.min()
    clean = clean / clean.max()  # 0-1

    # Simulate low photon count (e.g., 200 photons at peak)
    photon_count = 200
    rng = np.random.default_rng(99)
    noisy = rng.poisson(clean * photon_count).astype(np.float64)
    noisy /= photon_count  # re-normalise

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(noisy, cmap=CMAP, vmin=0, vmax=1)
    axes[0].set_title("Before: Low-Dose Poisson Noise\n(~200 photons/pixel)", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(clean, cmap=CMAP, vmin=0, vmax=1)
    axes[1].set_title("After: Clean (High-Dose) Image", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "low_dose_noise_before_after.png")


# ===================================================================
# 4. Rotation centre error
# ===================================================================

def generate_rotation_center_error():
    print("4/8  Rotation center error ...")
    n = 128
    phantom = shepp_logan_phantom(n)
    angles = np.linspace(0, 180, 180, endpoint=False)
    sino = radon_transform(phantom, angles)

    # Correct reconstruction
    recon_correct = fbp_reconstruct(sino, angles)

    # Simulate offset rotation centre by shifting the sinogram
    offset = 5  # pixels
    sino_shifted = np.zeros_like(sino)
    for i in range(sino.shape[1]):
        # Shift each column (projection) by offset pixels
        sino_shifted[:, i] = np.roll(sino[:, i], offset)

    recon_offset = fbp_reconstruct(sino_shifted, angles)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(recon_offset, cmap=CMAP)
    axes[0].set_title("Before: Wrong Rotation Center\n(offset = +5 px)", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(recon_correct, cmap=CMAP)
    axes[1].set_title("After: Correct Rotation Center", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "rotation_center_error_before_after.png")


# ===================================================================
# 5. Flat-field non-uniformity
# ===================================================================

def generate_flatfield():
    print("5/8  Flat-field non-uniformity ...")
    rng = np.random.default_rng(7)
    n = 256
    phantom = shepp_logan_phantom(n)
    clean = phantom - phantom.min()
    clean = clean / clean.max()

    # Simulate a non-uniform flat field (smooth illumination gradient +
    # slight detector gain variation)
    y, x = np.mgrid[0:n, 0:n] / float(n)
    flat_field = (0.6
                  + 0.35 * np.exp(-((x - 0.45)**2 + (y - 0.55)**2) / 0.15)
                  + 0.05 * rng.normal(size=(n, n)))
    flat_field = uniform_filter(flat_field, size=15)  # smooth out noise
    flat_field = np.clip(flat_field, 0.3, None)

    # Dark field (small constant + read noise)
    dark_field = 0.02 + 0.005 * rng.normal(size=(n, n))
    dark_field = np.clip(dark_field, 0, None)

    # Raw measurement (Beer-Lambert with non-uniform illumination)
    raw = flat_field * np.exp(-clean * 2.0) + dark_field

    # Without flat-field correction (just take -log)
    raw_no_ff = np.clip(raw, 1e-6, None)
    uncorrected = -np.log(raw_no_ff / raw_no_ff.max())

    # With flat-field correction
    corrected = (raw - dark_field) / (flat_field - dark_field + 1e-9)
    corrected = np.clip(corrected, 1e-6, None)
    corrected = -np.log(corrected)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    axes[0].imshow(uncorrected, cmap=CMAP,
                   vmin=np.percentile(uncorrected, 1),
                   vmax=np.percentile(uncorrected, 99))
    axes[0].set_title("Before: No Flat-Field Correction", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(corrected, cmap=CMAP,
                   vmin=np.percentile(corrected, 1),
                   vmax=np.percentile(corrected, 99))
    axes[1].set_title("After: Flat-Field + Dark-Field\nNormalization", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "flatfield_before_after.png")


# ===================================================================
# 6. Sparse-angle artifact
# ===================================================================

def generate_sparse_angle():
    print("6/8  Sparse-angle artifact ...")
    n = 128
    phantom = shepp_logan_phantom(n)

    # Dense projection set (180 angles)
    angles_dense = np.linspace(0, 180, 180, endpoint=False)
    sino_dense = radon_transform(phantom, angles_dense)
    recon_dense = fbp_reconstruct(sino_dense, angles_dense)

    # Sparse projection set (18 angles)
    angles_sparse = np.linspace(0, 180, 18, endpoint=False)
    sino_sparse = radon_transform(phantom, angles_sparse)
    recon_sparse = fbp_reconstruct(sino_sparse, angles_sparse)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmin = min(recon_dense.min(), recon_sparse.min())
    vmax = max(recon_dense.max(), recon_sparse.max())
    axes[0].imshow(recon_sparse, cmap=CMAP, vmin=vmin, vmax=vmax)
    axes[0].set_title("Before: Sparse Angles (18 proj.)\nStreak artifacts", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(recon_dense, cmap=CMAP, vmin=vmin, vmax=vmax)
    axes[1].set_title("After: Dense Angles (180 proj.)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "sparse_angle_before_after.png")


# ===================================================================
# 7. Dead / hot pixel (XRF elemental map)
# ===================================================================

def generate_dead_hot_pixel():
    print("7/8  Dead/hot pixel (XRF) ...")
    rng = np.random.default_rng(123)
    n = 128

    # Create a synthetic elemental map: smooth blobs representing
    # spatially varying element concentration
    y, x = np.mgrid[0:n, 0:n] / float(n)
    elem_map = (0.5 * np.exp(-((x - 0.3)**2 + (y - 0.4)**2) / 0.02)
                + 0.8 * np.exp(-((x - 0.7)**2 + (y - 0.6)**2) / 0.04)
                + 0.3 * np.exp(-((x - 0.5)**2 + (y - 0.2)**2) / 0.01))
    elem_map += 0.05 * rng.normal(size=(n, n))
    elem_map = np.clip(elem_map, 0, None)

    # Inject dead pixels (value → 0) and hot pixels (very high value)
    corrupted = elem_map.copy()
    n_dead = 50
    n_hot = 50
    dx, dy = rng.integers(0, n, n_dead), rng.integers(0, n, n_dead)
    hx, hy = rng.integers(0, n, n_hot), rng.integers(0, n, n_hot)
    for xi, yi in zip(dx, dy):
        corrupted[yi, xi] = 0.0
    for xi, yi in zip(hx, hy):
        corrupted[yi, xi] = elem_map.max() * rng.uniform(5, 15)

    # Fix with median filter
    fixed = median_filter(corrupted, size=3)

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmax = np.percentile(elem_map, 99.5)
    axes[0].imshow(corrupted, cmap="inferno", vmin=0, vmax=vmax)
    axes[0].set_title("Before: Dead & Hot Pixels\n(XRF elemental map)", fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(fixed, cmap="inferno", vmin=0, vmax=vmax)
    axes[1].set_title("After: Median Filter (3×3)", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "dead_hot_pixel_before_after.png")


# ===================================================================
# 8. I0 drop (incident beam fluctuation in XRF)
# ===================================================================

def generate_i0_drop():
    print("8/8  I0 drop ...")
    rng = np.random.default_rng(77)
    n = 128

    # Synthetic elemental map (raster scan: each row = one scan line)
    y, x = np.mgrid[0:n, 0:n] / float(n)
    true_map = (0.6 * np.exp(-((x - 0.4)**2 + (y - 0.5)**2) / 0.03)
                + 0.4 * np.exp(-((x - 0.7)**2 + (y - 0.3)**2) / 0.02)
                + 0.2)

    # Simulate I0 per scan line (row)
    i0 = np.ones(n)
    # Normal fluctuation
    i0 += 0.02 * rng.normal(size=n)
    # Inject abrupt drops in a few rows (beam dump / top-up events)
    drop_rows = [22, 23, 55, 78, 79, 80, 105]
    for r in drop_rows:
        i0[r] *= rng.uniform(0.15, 0.45)

    # Measured fluorescence counts = true_map * I0 (row-wise)
    measured = true_map * i0[:, np.newaxis]

    # Without I0 normalisation the map shows horizontal stripes
    unnormed = measured.copy()

    # With I0 normalisation
    normed = measured / i0[:, np.newaxis]

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, facecolor="white")
    vmin, vmax = 0, np.percentile(true_map, 99.5)
    axes[0].imshow(unnormed, cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0].set_title("Before: I₀ Drops (no normalization)\nHorizontal stripes visible",
                      fontsize=11)
    axes[0].axis("off")
    axes[1].imshow(normed, cmap="viridis", vmin=vmin, vmax=vmax)
    axes[1].set_title("After: I₀ Normalization", fontsize=11)
    axes[1].axis("off")
    fig.tight_layout()
    _savefig(fig, "i0_drop_before_after.png")


# ===================================================================
# Main
# ===================================================================

def main():
    """Generate all 8 before/after noise-type example images."""
    print(f"Output directory: {SCRIPT_DIR}")
    print("=" * 55)
    print("Generating synchrotron noise-type example images ...")
    print("=" * 55)

    generate_ring_artifact()
    generate_zinger()
    generate_low_dose_noise()
    generate_rotation_center_error()
    generate_flatfield()
    generate_sparse_angle()
    generate_dead_hot_pixel()
    generate_i0_drop()

    print("=" * 55)
    print("Done. All 8 images generated.")


if __name__ == "__main__":
    main()
