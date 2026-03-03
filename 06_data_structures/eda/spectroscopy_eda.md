# 분광학 데이터 탐색적 데이터 분석

## 개요

X선 흡수 분광학 (XAS)은 XANES (X선 흡수 근접 에지 구조)와 EXAFS (확장 X선 흡수 미세 구조)를
포괄하며, 두 방법 모두 원소 흡수 에지 전후의 입사 광자 에너지 함수로 흡수 계수를 측정합니다.
분광학 데이터의 EDA는 에지 정렬 확인, 잡음 수준 평가, 정규화 품질 점검, 그리고
스펙트럼 이상치 식별에 초점을 맞춥니다.

APS BER 빔라인에서 분광학 데이터는 다음과 같이 수집될 수 있습니다:
- **점 스펙트럼** -- 단일 위치 에너지 스캔 (1D: 에너지 vs. 흡수)
- **스펙트럼 이미징** -- 각 에너지 포인트에서 전체 이미지가 수집되는 XANES 스택
  (3D: 에너지 x 행 x 열)
- **Quick-EXAFS** -- 시간 분해 연구를 위한 빠른 연속 스캔 스펙트럼

## 분광학용 EDA 체크리스트

### 1. 데이터 완전성

- [ ] 모든 에너지 포인트가 존재 (일반적으로 XANES 200--1000, EXAFS 500--2000)
- [ ] 에너지 배열이 단조 증가
- [ ] 에너지 범위가 에지 아래 최소 50 eV, 에지 위 150 eV 이상 포괄 (XANES)
- [ ] EXAFS의 경우, 에지 위 최소 k = 12 Angstrom^-1까지 에너지 확장
- [ ] 참조 표준 스펙트럼이 포함됨

### 2. 에지 검출 및 정렬

- [ ] 흡수 에지가 예상 에너지에 위치 (1--2 eV 이내)
- [ ] 에지 점프가 잡음 위에서 명확히 보임
- [ ] 스캔 간 에너지 교정 드리프트 없음
- [ ] 참조 포일 에지 위치가 측정 간 안정적임

### 3. 정규화 품질

- [ ] 전에지 영역이 평탄 (잔류 기울기 없음)
- [ ] 후에지 영역이 정규화 후 ~1.0에 도달
- [ ] 에지 점프 크기가 예상 시료 두께/농도와 일치
- [ ] 과흡수 (자기흡수) 왜곡 없음

### 4. 잡음 평가

- [ ] 전에지 및 후에지 영역의 잡음 수준이 정량화됨
- [ ] SNR이 의도된 분석(선형 결합 피팅, PCA 등)에 충분
- [ ] 전에지에 체계적 진동 없음 (가능한 고조파 오염)

## 에지 검출 및 확인

```python
import numpy as np
import matplotlib.pyplot as plt

def find_edge_energy(energy, mu):
    """Find absorption edge energy as the maximum of the first derivative."""
    dmu = np.gradient(mu, energy)
    edge_idx = np.argmax(dmu)
    return energy[edge_idx], edge_idx

# Load spectroscopy data
# Assuming energy (1D) and mu (1D for point spectra, or 3D for imaging)
energy = np.load("energy_axis.npy")         # [nenergy] in eV
mu_spectra = np.load("mu_spectra.npy")       # [nspectra, nenergy]

# Check all spectra for edge position
edge_energies = []
for i in range(mu_spectra.shape[0]):
    e_edge, _ = find_edge_energy(energy, mu_spectra[i])
    edge_energies.append(e_edge)

edge_energies = np.array(edge_energies)
print(f"Edge energy: {np.mean(edge_energies):.2f} +/- {np.std(edge_energies):.2f} eV")
print(f"Range: {edge_energies.min():.2f} to {edge_energies.max():.2f} eV")

# Flag spectra with shifted edges
nominal_edge = np.median(edge_energies)
shifted = np.abs(edge_energies - nominal_edge) > 2.0  # >2 eV shift
if shifted.any():
    print(f"WARNING: {shifted.sum()} spectra have edge shifts > 2 eV")
```

## 정규화 점검

정량적 분석을 위해 적절한 정규화가 필수적입니다. Athena/Larch 표준 절차는
전에지 및 후에지 직선을 피팅합니다:

```python
def normalize_xas(energy, mu, pre_range=(-150, -30), post_range=(50, 300),
                  e0=None):
    """Simple XAS normalization."""
    if e0 is None:
        e0, _ = find_edge_energy(energy, mu)

    # Relative energy
    e_rel = energy - e0

    # Pre-edge fit (linear)
    pre_mask = (e_rel >= pre_range[0]) & (e_rel <= pre_range[1])
    pre_coeffs = np.polyfit(energy[pre_mask], mu[pre_mask], 1)
    pre_line = np.polyval(pre_coeffs, energy)

    # Post-edge fit (linear)
    post_mask = (e_rel >= post_range[0]) & (e_rel <= post_range[1])
    post_coeffs = np.polyfit(energy[post_mask], mu[post_mask], 1)
    post_line = np.polyval(post_coeffs, energy)

    # Normalize
    edge_step = np.polyval(post_coeffs, e0) - np.polyval(pre_coeffs, e0)
    mu_norm = (mu - pre_line) / edge_step

    return mu_norm, e0, edge_step

# Normalize and visualize
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Raw spectrum
axes[0].plot(energy, mu_spectra[0], "b-", lw=0.8)
axes[0].set_title("Raw Spectrum")
axes[0].set_xlabel("Energy (eV)")
axes[0].set_ylabel("mu(E)")

# Normalized spectrum
mu_norm, e0, step = normalize_xas(energy, mu_spectra[0])
axes[1].plot(energy, mu_norm, "b-", lw=0.8)
axes[1].axhline(0, color="gray", ls="--")
axes[1].axhline(1, color="gray", ls="--")
axes[1].set_title(f"Normalized (E0={e0:.1f} eV, step={step:.3f})")
axes[1].set_xlabel("Energy (eV)")

# First derivative
dmu = np.gradient(mu_norm, energy)
axes[2].plot(energy, dmu, "r-", lw=0.8)
axes[2].set_title("First Derivative")
axes[2].set_xlabel("Energy (eV)")

plt.tight_layout()
```

## 잡음 수준 평가

```python
def estimate_noise(energy, mu_norm, region="pre_edge", e0=None):
    """Estimate noise level in a specified spectral region."""
    if e0 is None:
        e0 = energy[np.argmax(np.gradient(mu_norm, energy))]

    e_rel = energy - e0

    if region == "pre_edge":
        mask = (e_rel >= -100) & (e_rel <= -30)
    elif region == "post_edge":
        mask = (e_rel >= 100) & (e_rel <= 300)
    else:
        raise ValueError("region must be 'pre_edge' or 'post_edge'")

    segment = mu_norm[mask]
    # Fit and subtract a linear trend, then measure residual
    x = energy[mask]
    coeffs = np.polyfit(x, segment, 1)
    residual = segment - np.polyval(coeffs, x)

    return np.std(residual)

# Assess noise for all spectra
noise_levels = []
edge_steps = []
for i in range(mu_spectra.shape[0]):
    mu_n, e0, step = normalize_xas(energy, mu_spectra[i])
    noise = estimate_noise(energy, mu_n, "post_edge", e0)
    noise_levels.append(noise)
    edge_steps.append(step)

noise_levels = np.array(noise_levels)
edge_steps = np.array(edge_steps)
snr = edge_steps / noise_levels

print(f"Post-edge noise: {np.mean(noise_levels):.5f} +/- {np.std(noise_levels):.5f}")
print(f"Edge step:       {np.mean(edge_steps):.4f} +/- {np.std(edge_steps):.4f}")
print(f"SNR:             {np.mean(snr):.1f} +/- {np.std(snr):.1f}")
```

## 이상치 검출

모집단에서 크게 벗어나는 스펙트럼을 식별합니다:

```python
from scipy.spatial.distance import cdist

# Normalize all spectra
normed = np.zeros_like(mu_spectra)
for i in range(mu_spectra.shape[0]):
    normed[i], _, _ = normalize_xas(energy, mu_spectra[i])

# Compute mean spectrum and distance of each spectrum
mean_spectrum = np.mean(normed, axis=0)
distances = np.sqrt(np.sum((normed - mean_spectrum) ** 2, axis=1))

threshold = np.mean(distances) + 3 * np.std(distances)
outliers = np.where(distances > threshold)[0]

print(f"Outlier spectra (3-sigma): {outliers}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distance plot
axes[0].bar(range(len(distances)), distances, color="steelblue")
axes[0].axhline(threshold, color="red", ls="--", label="3-sigma threshold")
axes[0].set_xlabel("Spectrum Index")
axes[0].set_ylabel("L2 Distance from Mean")
axes[0].legend()

# Overlay outlier spectra
axes[1].plot(energy, mean_spectrum, "k-", lw=2, label="Mean")
for idx in outliers:
    axes[1].plot(energy, normed[idx], "r-", lw=0.8, alpha=0.6)
axes[1].set_xlabel("Energy (eV)")
axes[1].set_ylabel("Normalized mu")
axes[1].set_title(f"Outlier Spectra ({len(outliers)} found)")
axes[1].legend()

plt.tight_layout()
```

## 주성분 분석 (PCA)

PCA는 데이터셋 내 별개의 스펙트럼 성분 수를 식별하고 체계적인
변동을 드러낼 수 있습니다:

```python
from sklearn.decomposition import PCA

# PCA on normalized spectra
pca = PCA(n_components=min(10, mu_spectra.shape[0]))
scores = pca.fit_transform(normed)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Scree plot
axes[0].bar(range(1, 11), pca.explained_variance_ratio_[:10] * 100)
axes[0].set_xlabel("Component")
axes[0].set_ylabel("Variance Explained (%)")
axes[0].set_title("PCA Scree Plot")

# First 3 components
for i in range(3):
    axes[1].plot(energy, pca.components_[i], label=f"PC{i+1}")
axes[1].set_xlabel("Energy (eV)")
axes[1].set_title("Principal Components")
axes[1].legend()

# Score scatter (PC1 vs PC2)
axes[2].scatter(scores[:, 0], scores[:, 1], c="steelblue", s=20)
if len(outliers) > 0:
    axes[2].scatter(scores[outliers, 0], scores[outliers, 1],
                    c="red", s=40, label="Outliers")
axes[2].set_xlabel("PC1 Score")
axes[2].set_ylabel("PC2 Score")
axes[2].set_title("PCA Score Plot")
axes[2].legend()

plt.tight_layout()
```

해석:
- **유의미한 성분 1--2개**: 시료가 비교적 균질함
- **3--5개 성분**: 여러 화학종이 존재
- **점진적 분산 감소**: 잡음 지배적, 더 많은 평균화 필요 가능
- **PC1은 종종 에지 이동을 포착** -- 산화 상태 변동을 나타냄
- **PC2는 종종 배위 변화를 포착** -- 국소 구조 차이

## 자기흡수 점검

농축된 시료 (형광 검출)의 경우, 자기흡수가 스펙트럼을 왜곡할 수 있습니다:

```python
# Compare transmission and fluorescence if both available
# Self-absorption suppresses XANES features and reduces edge jump

# Quick check: compare white-line height to reference
ref_spectrum = np.load("reference_standard.npy")  # Known good spectrum
ref_norm, _, _ = normalize_xas(energy, ref_spectrum)

sample_norm = normed[0]

wl_range = (energy > e0) & (energy < e0 + 15)
ref_wl_height = np.max(ref_norm[wl_range])
sample_wl_height = np.max(sample_norm[wl_range])
ratio = sample_wl_height / ref_wl_height

if ratio < 0.8:
    print(f"WARNING: White-line ratio = {ratio:.2f} -- possible self-absorption")
else:
    print(f"White-line ratio = {ratio:.2f} -- acceptable")
```

## 관련 자료

- [분광학 EDA 노트북](notebooks/03_spectral_eda.ipynb)
- [Larch XAS 분석](https://xraypy.github.io/xraylarch/)
- [Athena/Artemis (Demeter)](https://bruceravel.github.io/demeter/)
- [분광학 모달리티 개요](../../02_xray_modalities/)
