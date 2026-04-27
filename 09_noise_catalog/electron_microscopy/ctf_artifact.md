# CTF 아티팩트 (대비 전달 함수)(CTF Artifact (Contrast Transfer Function))

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | TEM / Cryo-EM |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 심각(Critical) |
| **빈도** | 항상(Always) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 투과 전자 현미경(TEM) |

## 시각적 예시

![CTF 아티팩트 보정 전후](../images/ctf_artifact_before_after.png)

> **이미지 출처:** 푸리에 공간에서 CTF 변조가 적용된 합성 팬텀. 왼쪽: 진동하는 전달 함수로 인한 대비 반전. 오른쪽: Wiener CTF 보정 후. MIT 라이선스.

## 설명

대비 전달 함수(Contrast Transfer Function, CTF)는 공간 주파수를 양/음 대비를 번갈아 가며 변조하는 TEM 이미징 시스템의 진동 전달 함수입니다. 보정되지 않은 CTF는 대비 반전(특징이 디포커스에 따라 밝거나 어둡게 나타날 수 있음), 영점 교차에서의 정보 손실, 그리고 고주파 정보의 엔벨로프 함수 감쇠를 유발합니다. 적절한 CTF 추정과 보정은 고해상도 cryo-EM에서 가장 중요한 단일 단계입니다.

**방사광 관련성:** X선 현미경의 광학 전달 함수(OTF), 전파 기반 위상 대비, X선 검출기의 변조 전달 함수(MTF)와 유사합니다. CTF 보정 개념은 Zernike 위상 대비 X선 현미경에 직접 적용됩니다.

## 근본 원인

- TEM 렌즈 수차(주로 디포커스와 구면 수차 Cs)가 위상 시프트를 생성
- CTF = sin(χ(q)) 여기서 χ(q) = π·λ·Δf·q² - π/2·Cs·λ³·q⁴
- CTF는 +1과 -1 사이를 진동 → 다른 공간 주파수에서 대비 반전
- 영점 교차: CTF = 0인 주파수 → 완전한 정보 손실
- 엔벨로프 함수 (공간/시간적 결맞음)가 고-q 정보를 감쇠

### 수학적 형태

```
CTF(q) = -sin(χ(q)) · E_s(q) · E_t(q)

여기서:
  χ(q) = π·λ·Δf·q² - π/2·Cs·λ³·q⁴
  E_s = 공간 결맞음 엔벨로프
  E_t = 시간 결맞음 엔벨로프
  Δf = 디포커스, Cs = 구면 수차, λ = 파장
```

## 빠른 진단

```python
import numpy as np

def compute_power_spectrum(micrograph):
    """2D 파워 스펙트럼을 계산합니다 (CTF Thon 링을 보여줌)."""
    F = np.fft.fftshift(np.fft.fft2(micrograph))
    power = np.log1p(np.abs(F)**2)
    return power

def radial_average_ps(power_spectrum):
    """CTF 진동을 보기 위해 파워 스펙트럼을 방사형으로 평균합니다."""
    ny, nx = power_spectrum.shape
    cy, cx = ny // 2, nx // 2
    Y, X = np.ogrid[-cy:ny-cy, -cx:nx-cx]
    r = np.sqrt(X**2 + Y**2).astype(int)
    r_max = min(cy, cx)
    radial = np.array([power_spectrum[r == ri].mean() for ri in range(r_max)])
    return radial
```

## 탐지 방법

### 시각적 지표

- **Thon 링:** 마이크로그래프의 2D 파워 스펙트럼에서 동심원 링이 보임
- 링 간격은 디포커스에 따라 달라짐 — 간격이 넓을수록 디포커스가 작음
- 비대칭 링은 비점수차(astigmatism)를 나타냄
- 엔벨로프 함수 감쇠로 인해 고주파에서 링이 희미해짐
- 대비 반전: 특정 디포커스 값에서 특징이 반전된 대비로 나타남

### 자동 탐지

```python
import numpy as np
from scipy.optimize import minimize

def fit_ctf_1d(radial_profile, pixel_size_A, voltage_kV=300):
    """방사형으로 평균된 파워 스펙트럼에 CTF를 피팅합니다."""
    wavelength = 12.26 / np.sqrt(voltage_kV * 1e3 * (1 + voltage_kV * 1e3 / 1.022e6))
    q = np.arange(len(radial_profile)) / (len(radial_profile) * 2 * pixel_size_A)
    def ctf_model(params):
        defocus, Cs = params
        chi = np.pi * wavelength * defocus * q**2 - 0.5 * np.pi * Cs * wavelength**3 * q**4
        ctf = np.sin(chi)**2
        return np.sum((radial_profile / radial_profile.max() - ctf)**2)
    result = minimize(ctf_model, [1e4, 2.7e7], method='Nelder-Mead')
    return result.x  # [defocus_A, Cs_A]
```

## 보정 방법

### 전통적 접근법

1. **CTF 추정:** CTFFIND4, Gctf — Thon 링으로부터 디포커스 및 비점수차 추정
2. **위상 뒤집기(Phase flipping):** sign(CTF)를 곱하여 대비 반전 보정 (단순하지만 손실 있음)
3. **Wiener 필터링:** 노이즈 정규화를 동반한 CTF 보정: `F_corr = CTF* / (|CTF|² + 1/SNR)`
4. **CTF 정제:** RELION/CryoSPARC에서 입자별 디포커스 정제

```python
def wiener_ctf_correction(image_fft, ctf, snr=10.0):
    """Wiener 필터 CTF 보정을 적용합니다."""
    wiener = np.conj(ctf) / (np.abs(ctf)**2 + 1.0 / snr)
    corrected_fft = image_fft * wiener
    return corrected_fft
```

### AI/ML 접근법

- **DeepCTF:** 신경망 CTF 추정
- **CryoDRGN:** 심층 생성 재구성에서의 암묵적 CTF 처리
- **CTFGAN:** 단일 입자 이미지를 위한 GAN 기반 CTF 보정

## 핵심 참고문헌

- **Rohou & Grigorieff (2015)** — "CTFFIND4: Fast and accurate defocus estimation from electron micrographs"
- **Zhang (2016)** — "Gctf: Real-time CTF determination and correction"
- **Wade (1992)** — "A brief look at imaging and contrast transfer" — 교육적 입문서
- **Frank (2006)** — "Three-Dimensional Electron Microscopy of Macromolecular Assemblies" — 교과서
- **Vulovic et al. (2013)** — "Image formation modeling in cryo-EM"

## 방사광 데이터 관련성

| 시나리오 | 관련성 |
|----------|--------|
| Zernike 위상 대비 X선 현미경 | Zernike 위상 링과 직접 유사한 CTF |
| 전파 기반 위상 대비 | 자유 공간 전파가 유사한 진동 전달 함수를 생성 |
| X선 검출기 MTF | CTF 엔벨로프와 유사한 주파수 의존 검출기 응답 |
| Ptychography | 위상 복원이 CTF와 유사한 효과를 본질적으로 처리 |
| 상관 cryo-EM + 방사광 | 다중 모달 데이터 융합을 위해 CTF 이해 필요 |

## 실제 보정 전후 사례

다음 발표된 자료들은 실제 실험적 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림 | 설명 | 라이선스 |
|------|------|------|------|----------|
| [Rohou & Grigorieff 2015 — CTFFIND4](https://doi.org/10.1016/j.jsb.2015.08.008) | 논문 | Fig 1 | 전자 마이크로그래프로부터의 빠르고 정확한 디포커스 추정 — Thon 링 피팅 사례 | -- |
| RELION 문서 | 소프트웨어 문서 | CTF 보정 튜토리얼 | 단일 입자 재구성에서 Wiener 필터링 보정 전후를 보여주는 CTF 보정 사례 | GPL-2.0 |

> **권장 참고자료**: [Rohou & Grigorieff 2015 — CTFFIND4 (J. Struct. Biol.)](https://doi.org/10.1016/j.jsb.2015.08.008)

## 관련 자료

- [부분 결맞음](../ptychography/partial_coherence.md) — 프타이코그래피의 결맞음 엔벨로프 효과
- [Gibbs 링잉](../medical_imaging/gibbs_ringing.md) — 관련된 주파수 공간 절단 아티팩트
- [프로브 흐림](../xrf_microscopy/probe_blurring.md) — PSF/OTF 관련 해상도 한계
