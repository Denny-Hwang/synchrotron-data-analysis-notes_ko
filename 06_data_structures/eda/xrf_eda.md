# XRF 데이터 탐색적 데이터 분석

## 개요

X선 형광 (XRF) 현미경 데이터셋은 각 픽셀이 완전한 에너지 분산 스펙트럼을 포함하는
다채널 2D 맵입니다. XRF 데이터의 EDA는 스펙트럼 품질 확인, 원소 맵 분포 평가,
검출기 아티팩트 식별, 그리고 원소 간 공간 상관관계 발견에 초점을 맞춥니다.

이 가이드는 [xrf_hdf5_schema.md](../hdf5_structure/xrf_hdf5_schema.md)에 설명된
MAPS HDF5 형식의 데이터를 가정합니다.

## XRF 데이터용 EDA 체크리스트

### 1. 파일 무결성

- [ ] HDF5 파일이 오류 없이 열림
- [ ] `/MAPS/Spectra/mca_arr` 형태가 예상과 일치 (nrow, ncol, nchan)
- [ ] `/MAPS/XRF_Analyzed/Fitted/Counts_Per_Sec`에 피팅된 맵 포함
- [ ] 채널 이름이 채워져 있고 예상 원소와 일치
- [ ] 스캔 좌표(x_axis, y_axis)가 의도된 스캔 영역을 포괄

### 2. 적분 스펙트럼 검사

- [ ] 합산 스펙트럼에 예상되는 형광 피크가 표시됨
- [ ] 피크 위치가 알려진 방출 에너지와 일치
- [ ] 컴프턴 및 탄성 산란 피크가 올바른 에너지에 존재
- [ ] 오염을 시사하는 예상치 못한 피크 없음
- [ ] 배경 수준이 합리적 (산란에 의해 지배되지 않음)

### 3. 원소별 맵 품질

- [ ] 각 원소 맵이 합리적인 동적 범위를 가짐
- [ ] 전체가 0이거나 NaN인 맵 없음
- [ ] 공간 특징이 알려진 시료 형태와 일치
- [ ] 스캔 이동 오류로 인한 줄무늬 아티팩트 없음

### 4. 잡음 및 SNR 평가

- [ ] 각 원소에 대해 SNR 추정
- [ ] 잠재적 제외 대상인 저농도 원소 식별
- [ ] 시료가 없는 영역에서 잡음 바닥 특성화

## 채널 히스토그램

강도 히스토그램은 원소 농도의 분포를 나타내며 이상치, 포화,
배경 수준을 식별하는 데 도움이 됩니다.

```python
import h5py
import numpy as np
import matplotlib.pyplot as plt

with h5py.File("xrf_scan.h5", "r") as f:
    maps = f["MAPS/XRF_Analyzed/Fitted/Counts_Per_Sec"][:]
    names = [n.decode() for n in f["MAPS/XRF_Analyzed/Channel_Names"][:]]

fig, axes = plt.subplots(4, 5, figsize=(20, 12))
axes = axes.ravel()

for i, (ax, name) in enumerate(zip(axes, names)):
    data = maps[i].ravel()
    data = data[data > 0]  # Exclude zeros
    if len(data) > 0:
        ax.hist(data, bins=100, log=True, color="steelblue", edgecolor="none")
        ax.set_title(f"{name} (median={np.median(data):.1f})")
        ax.axvline(np.percentile(data, 99), color="red", ls="--", label="99th pct")
    ax.set_xlabel("Counts/sec")

plt.tight_layout()
plt.savefig("xrf_channel_histograms.png", dpi=150)
```

## 신호 대 잡음비 (SNR) 분석

원소별 SNR은 어떤 채널에 의미 있는 신호가 포함되어 있는지 우선순위를 정하는 데 도움이 됩니다:

```python
def compute_snr(element_map, background_roi=None):
    """Estimate SNR for an elemental map.

    Args:
        element_map: 2D array of fitted counts
        background_roi: tuple (row_slice, col_slice) for noise estimation
    """
    if background_roi is not None:
        noise_region = element_map[background_roi[0], background_roi[1]]
    else:
        # Use lowest 10% of pixels as noise estimate
        threshold = np.percentile(element_map, 10)
        noise_region = element_map[element_map <= threshold]

    signal = np.mean(element_map)
    noise = np.std(noise_region) if len(noise_region) > 0 else 1e-10
    return signal / noise

# Compute SNR for all elements
bg_roi = (slice(0, 10), slice(0, 10))  # Top-left corner assumed background
snr_values = {}
for i, name in enumerate(names):
    snr_values[name] = compute_snr(maps[i], bg_roi)

# Sort and display
for name, snr in sorted(snr_values.items(), key=lambda x: -x[1]):
    quality = "HIGH" if snr > 10 else "MED" if snr > 3 else "LOW"
    print(f"  {name:4s}: SNR = {snr:8.1f}  [{quality}]")
```

## 상관관계 행렬

원소 상관관계 행렬은 광물 상, 생물학적 구조 또는 오염을 나타낼 수 있는
공동 국소화 패턴을 보여줍니다:

```python
import seaborn as sns

# Reshape maps to (nelem, npixels) for correlation
nelem, nrow, ncol = maps.shape
flat_maps = maps.reshape(nelem, -1)

# Compute Pearson correlation
corr_matrix = np.corrcoef(flat_maps)

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, xticklabels=names, yticklabels=names,
            cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            annot=True, fmt=".2f", ax=ax)
ax.set_title("XRF Element Correlation Matrix")
plt.tight_layout()
plt.savefig("xrf_correlation_matrix.png", dpi=150)
```

해석:
- **강한 양의 상관관계** (r > 0.7): 원소가 공동 국소화됨, 같은 상일 가능성
- **강한 음의 상관관계** (r < -0.3): 반상관, 다른 상
- **Fe-Mn 상관관계**: 토양에서 흔함 -- 철/망간 산화물 상을 나타냄
- **Ca-P 상관관계**: 생물학적 -- 인산칼슘(뼈, 세포)을 나타냄

## RGB 합성 맵

의사 색상 합성은 세 원소를 R, G, B 채널에 할당하여 빠른 공간
패턴 인식을 가능하게 합니다:

```python
def make_rgb_composite(maps, names, r_elem, g_elem, b_elem,
                       percentile_clip=99):
    """Create an RGB composite from three elemental maps."""
    rgb = np.zeros((*maps[0].shape, 3))

    for ch, elem in enumerate([r_elem, g_elem, b_elem]):
        idx = names.index(elem)
        channel = maps[idx].astype(float)
        vmin = np.percentile(channel, 1)
        vmax = np.percentile(channel, percentile_clip)
        channel = np.clip((channel - vmin) / (vmax - vmin + 1e-10), 0, 1)
        rgb[:, :, ch] = channel

    return rgb

# Example composites
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

combos = [("Fe", "Ca", "Zn"), ("Cu", "Mn", "P"), ("S", "K", "Fe")]
for ax, (r, g, b) in zip(axes, combos):
    rgb = make_rgb_composite(maps, names, r, g, b)
    ax.imshow(rgb, origin="lower")
    ax.set_title(f"R={r}, G={g}, B={b}")
    ax.axis("off")

plt.tight_layout()
plt.savefig("xrf_rgb_composites.png", dpi=150)
```

## 불량 픽셀 검출

불량 또는 핫 픽셀은 분석을 왜곡할 수 있는 고립된 비정상 값으로 나타납니다:

```python
from scipy.ndimage import median_filter

def detect_dead_pixels(image, threshold=5.0):
    """Detect dead/hot pixels by comparing to local median."""
    median_img = median_filter(image, size=3)
    diff = np.abs(image - median_img)
    mad = np.median(diff)  # Median absolute deviation
    mask = diff > threshold * mad
    return mask

# Check all elemental maps
total_dead = np.zeros((nrow, ncol), dtype=bool)
for i, name in enumerate(names):
    dead = detect_dead_pixels(maps[i])
    n_dead = dead.sum()
    if n_dead > 0:
        print(f"  {name}: {n_dead} dead/hot pixels ({100*n_dead/(nrow*ncol):.2f}%)")
    total_dead |= dead

print(f"\nTotal unique dead pixel positions: {total_dead.sum()}")
```

## I0 정규화 점검

입사 플럭스(I0) 정규화가 올바르게 적용되었는지 확인합니다:

```python
with h5py.File("xrf_scan.h5", "r") as f:
    scaler_names = [n.decode() for n in f["MAPS/Scalers/Names"][:]]
    scalers = f["MAPS/Scalers/Values"][:]
    i0_idx = scaler_names.index("I0")
    i0_map = scalers[i0_idx]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].imshow(i0_map, cmap="viridis", origin="lower")
axes[0].set_title("I0 (Incident Flux) Map")
plt.colorbar(axes[0].images[0], ax=axes[0])

axes[1].hist(i0_map.ravel(), bins=100, color="steelblue")
axes[1].set_title("I0 Distribution")
axes[1].set_xlabel("I0 counts")

# Check for I0 drops (beam dumps, top-up events)
i0_mean = np.mean(i0_map)
low_i0 = i0_map < 0.5 * i0_mean
if low_i0.any():
    print(f"WARNING: {low_i0.sum()} pixels have I0 < 50% of mean")
    print("  This may indicate beam dump or shutter issues")

plt.tight_layout()
```

## 요약 통계 테이블

문서화를 위한 종합 요약 테이블을 생성합니다:

```python
import pandas as pd

rows = []
for i, name in enumerate(names):
    m = maps[i]
    rows.append({
        "Element": name,
        "Min": f"{m.min():.2f}",
        "Max": f"{m.max():.2f}",
        "Mean": f"{m.mean():.2f}",
        "Median": f"{np.median(m):.2f}",
        "Std": f"{m.std():.2f}",
        "SNR": f"{snr_values[name]:.1f}",
        "Dead Px": detect_dead_pixels(m).sum(),
    })

df = pd.DataFrame(rows)
print(df.to_markdown(index=False))
```

## 관련 자료

- [XRF HDF5 스키마](../hdf5_structure/xrf_hdf5_schema.md)
- [XRF EDA 노트북](notebooks/01_xrf_eda.ipynb)
- [XRF 모달리티 개요](../../02_xray_modalities/)
