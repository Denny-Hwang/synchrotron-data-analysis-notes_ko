# 단층촬영 데이터 탐색적 데이터 분석

## 개요

단층촬영 데이터셋은 여러 회전 각도에서 수집된 투영 이미지와 플랫필드(개방 빔) 및
다크필드(빔 없음) 참조 이미지로 구성됩니다. 단층촬영 EDA는 투영 품질, 아티팩트 검출,
회전 중심 확인, 시노그램 분석에 초점을 맞추며 -- 이 모든 것이 재구성 품질에
결정적인 영향을 미칩니다.

이 가이드는 [tomo_hdf5_schema.md](../hdf5_structure/tomo_hdf5_schema.md)에 설명된
Data Exchange HDF5 형식의 데이터를 가정합니다.

## 단층촬영용 EDA 체크리스트

### 1. 데이터 완전성

- [ ] 예상되는 모든 투영이 존재 (예: 180도에서 0.1도 간격의 경우 1800개)
- [ ] 플랫필드 이미지 수집됨 (일반적으로 10--40 프레임)
- [ ] 다크필드 이미지 수집됨 (일반적으로 10--20 프레임)
- [ ] Theta 배열 길이가 투영 수와 일치
- [ ] 각도 범위가 정확 (180도 또는 360도)
- [ ] Theta 값이 단조 증가

### 2. 참조 프레임 품질

- [ ] 플랫필드 이미지가 균일 (섬광체에 이물질 없음)
- [ ] 다크필드 이미지가 낮고 일관됨
- [ ] 플랫필드 변동이 시야 전체에서 < 20%
- [ ] 플랫필드에 포화 픽셀 없음

### 3. 투영 품질

- [ ] 시료가 모든 각도에서 시야 내에 완전히 위치
- [ ] 연속 투영 간 큰 강도 점프 없음
- [ ] 모션 블러 없음 (회전 속도에 적합한 노출 시간)
- [ ] 빔 강도(I0)가 스캔 전체에서 안정적

### 4. 아티팩트 평가

- [ ] 시노그램 검사를 통한 링 아티팩트 가능성 평가
- [ ] 징거(우주선 점) 식별
- [ ] 위상 대비 프린지 특성화 (존재하는 경우)

## 투영 품질 평가

### 시각적 검사

```python
import h5py
import numpy as np
import matplotlib.pyplot as plt

with h5py.File("tomo_scan.h5", "r") as f:
    proj = f["/exchange/data"]
    flat = f["/exchange/data_white"][:]
    dark = f["/exchange/data_dark"][:]
    theta = f["/exchange/theta"][:]

    nproj, nrow, ncol = proj.shape
    print(f"Projections: {nproj}, Size: {nrow}x{ncol}")
    print(f"Theta range: {np.degrees(theta[0]):.1f} to {np.degrees(theta[-1]):.1f} deg")

    # Show projections at 0, 45, 90, 135 degrees
    angles_deg = np.degrees(theta)
    target_angles = [0, 45, 90, 135]

    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    for ax, target in zip(axes, target_angles):
        idx = np.argmin(np.abs(angles_deg - target))
        ax.imshow(proj[idx], cmap="gray", origin="lower")
        ax.set_title(f"Projection @ {angles_deg[idx]:.1f} deg")
    plt.tight_layout()
```

### 각도별 프레임 통계

```python
# Compute mean intensity per projection
means = np.zeros(nproj)
for i in range(nproj):
    with h5py.File("tomo_scan.h5", "r") as f:
        means[i] = np.mean(f["/exchange/data"][i])

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(np.degrees(theta), means, lw=0.5)
ax.set_xlabel("Rotation Angle (degrees)")
ax.set_ylabel("Mean Intensity")
ax.set_title("Projection Mean Intensity vs. Angle")

# Flag intensity drops > 10%
median_mean = np.median(means)
drops = np.where(means < 0.9 * median_mean)[0]
if len(drops) > 0:
    ax.scatter(np.degrees(theta[drops]), means[drops], c="red", s=20, zorder=5)
    print(f"WARNING: {len(drops)} projections with >10% intensity drop")
```

## 시노그램 시각화

시노그램(고정된 행에서의 각도 대 수평 위치)은 회전 관련 아티팩트를 드러내며
재구성 문제 진단에 필수적입니다.

```python
with h5py.File("tomo_scan.h5", "r") as f:
    # Extract sinograms at three vertical positions
    rows = [nrow // 4, nrow // 2, 3 * nrow // 4]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, row in zip(axes, rows):
        sino = f["/exchange/data"][:, row, :]
        ax.imshow(sino, cmap="gray", aspect="auto", origin="lower",
                  extent=[0, ncol, np.degrees(theta[0]), np.degrees(theta[-1])])
        ax.set_xlabel("Detector Column")
        ax.set_ylabel("Angle (degrees)")
        ax.set_title(f"Sinogram at row {row}")
    plt.tight_layout()
```

## 링 아티팩트 검출

링 아티팩트는 시노그램에서 수직 줄무늬로 나타납니다. 이는 불량하거나
잘못 보정된 검출기 픽셀에서 발생합니다.

```python
def detect_ring_artifacts(sinogram, threshold=3.0):
    """Detect potential ring artifacts by analyzing column-wise statistics."""
    col_means = np.mean(sinogram, axis=0)
    col_median = np.median(col_means)
    col_mad = np.median(np.abs(col_means - col_median))

    # Columns deviating from median by more than threshold * MAD
    ring_cols = np.where(np.abs(col_means - col_median) > threshold * col_mad)[0]
    return ring_cols, col_means

with h5py.File("tomo_scan.h5", "r") as f:
    sino = f["/exchange/data"][:, nrow // 2, :]

ring_cols, col_profile = detect_ring_artifacts(sino)
print(f"Potential ring artifact columns: {len(ring_cols)}")

fig, ax = plt.subplots(figsize=(12, 3))
ax.plot(col_profile, lw=0.5)
ax.scatter(ring_cols, col_profile[ring_cols], c="red", s=10, zorder=5)
ax.set_xlabel("Column Index")
ax.set_ylabel("Mean Intensity (across angles)")
ax.set_title("Column-wise Profile (ring artifact detection)")
```

## 회전 중심 추정

잘못된 회전 중심은 재구성에서 특징적인 아티팩트를 유발합니다:
커핑, 이중화 또는 흐림.

```python
import tomopy

with h5py.File("tomo_scan.h5", "r") as f:
    proj = f["/exchange/data"][:]
    flat = f["/exchange/data_white"][:]
    dark = f["/exchange/data_dark"][:]
    theta = f["/exchange/theta"][:]

proj_norm = tomopy.normalize(proj, flat, dark)
proj_norm = tomopy.minus_log(proj_norm)

# Automated center finding
center_vo = tomopy.find_center_vo(proj_norm)
center_pc = tomopy.find_center_pc(proj_norm[0], proj_norm[-1])

print(f"Vo method center:  {center_vo:.2f}")
print(f"Phase corr center: {center_pc:.2f}")
print(f"Image center:      {ncol / 2:.1f}")
print(f"Offset from image center: {center_vo - ncol/2:.2f} pixels")

# Visual verification: reconstruct one slice at multiple centers
test_centers = np.arange(center_vo - 5, center_vo + 5.5, 0.5)
fig, axes = plt.subplots(2, 5, figsize=(20, 8))
for ax, c in zip(axes.ravel(), test_centers[:10]):
    sino_slice = proj_norm[:, nrow//2:nrow//2+1, :]
    rec = tomopy.recon(sino_slice, theta, center=c, algorithm="gridrec")
    ax.imshow(rec[0], cmap="gray")
    ax.set_title(f"c={c:.1f}")
    ax.axis("off")
plt.suptitle("Rotation Center Scan")
plt.tight_layout()
```

## 플랫필드 및 다크필드 분석

```python
fig, axes = plt.subplots(2, 3, figsize=(15, 9))

# Dark field analysis
dark_mean = np.mean(dark, axis=0)
dark_std = np.std(dark, axis=0)
axes[0, 0].imshow(dark_mean, cmap="gray")
axes[0, 0].set_title(f"Dark Mean (global mean={dark_mean.mean():.1f})")
axes[0, 1].imshow(dark_std, cmap="hot")
axes[0, 1].set_title(f"Dark Std (max={dark_std.max():.1f})")
axes[0, 2].hist(dark_mean.ravel(), bins=100, log=True)
axes[0, 2].set_title("Dark Mean Histogram")

# Flat field analysis
flat_mean = np.mean(flat, axis=0)
flat_std = np.std(flat, axis=0)
flat_norm = flat_std / (flat_mean + 1e-10)  # Coefficient of variation
axes[1, 0].imshow(flat_mean, cmap="gray")
axes[1, 0].set_title(f"Flat Mean (global mean={flat_mean.mean():.1f})")
axes[1, 1].imshow(flat_norm, cmap="hot", vmax=0.1)
axes[1, 1].set_title("Flat Coeff. of Variation")
axes[1, 2].hist(flat_mean.ravel(), bins=100)
axes[1, 2].set_title("Flat Mean Histogram")

plt.tight_layout()
```

## 히스토그램 분석

```python
with h5py.File("tomo_scan.h5", "r") as f:
    # Sample random projections for histogram
    indices = np.random.choice(nproj, size=min(50, nproj), replace=False)
    sample_data = np.stack([f["/exchange/data"][i] for i in sorted(indices)])

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Raw projection histogram
axes[0].hist(sample_data.ravel(), bins=200, log=True, color="steelblue")
axes[0].set_title("Raw Projection Histogram")
axes[0].set_xlabel("Intensity (counts)")

# After normalization
norm_data = (sample_data - dark_mean) / (flat_mean - dark_mean + 1e-10)
axes[1].hist(norm_data.ravel(), bins=200, log=True, color="darkorange")
axes[1].set_title("Normalized Projection Histogram")
axes[1].set_xlabel("Transmission (I/I0)")

# After -log transform
log_data = -np.log(np.clip(norm_data, 1e-6, None))
axes[2].hist(log_data.ravel(), bins=200, log=True, color="forestgreen")
axes[2].set_title("After -log (Absorption)")
axes[2].set_xlabel("Absorption (a.u.)")

plt.tight_layout()
```

## 징거 (이상 점) 검출

징거는 우주선이나 검출기 잡음 버스트로 인한 고립된 밝은 점입니다:

```python
from scipy.ndimage import median_filter

def detect_zingers(projection, threshold=10.0):
    """Detect zinger pixels in a single projection."""
    filtered = median_filter(projection.astype(float), size=3)
    diff = projection.astype(float) - filtered
    mad = np.median(np.abs(diff))
    zingers = np.abs(diff) > threshold * max(mad, 1.0)
    return zingers

# Check a sample of projections
total_zingers = 0
with h5py.File("tomo_scan.h5", "r") as f:
    for i in range(0, nproj, max(1, nproj // 20)):
        proj_i = f["/exchange/data"][i]
        z = detect_zingers(proj_i)
        count = z.sum()
        total_zingers += count
        if count > 10:
            print(f"  Projection {i}: {count} zingers detected")

print(f"Total zingers found in sampled projections: {total_zingers}")
```

## 관련 자료

- [단층촬영 HDF5 스키마](../hdf5_structure/tomo_hdf5_schema.md)
- [단층촬영 EDA 노트북](notebooks/02_tomo_eda.ipynb)
- [단층촬영 모달리티 개요](../../02_xray_modalities/)
- [TomoPy 문서](https://tomopy.readthedocs.io/)
