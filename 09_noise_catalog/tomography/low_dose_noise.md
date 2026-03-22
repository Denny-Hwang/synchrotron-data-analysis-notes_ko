# 저선량 노이즈(Low-Dose Noise)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 토모그래피 |
| **노이즈 유형** | 통계적(Statistical) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |

## 시각적 예시

![저선량 노이즈 보정 전후 비교](../images/low_dose_noise_before_after.png)

*실제 데이터에서의 저선량 노이즈 보정 전후 비교. 출처: [TomoGAN](https://doi.org/10.1073/pnas.1922713117) 논문*

**왼쪽(보정 전):** 불충분한 광자 통계로 인해 입상(grainy/speckled) 패턴이 나타나는 재구성 이미지.
**오른쪽(보정 후):** 노이즈 저감 알고리즘 적용 후 세부 구조가 선명해진 이미지를 확인할 수 있습니다.

## 설명

저선량 노이즈(Low-Dose Noise)는 불충분한 광자 통계로 인해 재구성 이미지에 나타나는 입상(grainy) 또는 반점(speckled) 패턴입니다. 프로젝션 데이터에서의 포아송 노이즈(Poisson noise)가 재구성 과정을 통해 전파되면서 이미지 품질을 저하시킵니다.

X선 이미징에서 각 픽셀에 도달하는 광자 수는 포아송 분포를 따르므로, 광자 수 $N$에 대한 신호 대 잡음비(SNR)는 $\sqrt{N}$에 비례합니다. 따라서 노출 시간이 짧거나 빔 강도가 낮으면 SNR이 크게 감소합니다.

저선량 조건은 방사선에 민감한 시료(생물학적 시료, 일부 고분자 등), 시간 분해 실험(빠른 스캔), 또는 빔 강도가 제한된 경우에 흔히 발생합니다. 노이즈는 재구성 과정에서 증폭될 수 있으며, 특히 FBP의 고주파 강조 필터(ramp filter)에 의해 더욱 악화됩니다.

## 근본 원인

1. **짧은 노출 시간:** 시간 분해 실험이나 시료 손상 최소화를 위해 노출 시간을 줄인 경우
2. **낮은 빔 강도:** 저에너지 빔 사용, 빔라인 광학 요소의 손실, 또는 저장링 전류 저하
3. **높은 시료 감쇠:** 두꺼운 시료나 고밀도 물질이 광자를 많이 흡수
4. **검출기 양자 효율 저하:** 검출기의 광자 검출 효율이 낮은 경우
5. **프로젝션 수 부족:** 각도 샘플링은 충분하나 각 프로젝션의 광자 통계가 부족

## 빠른 진단

관심 영역(ROI)에서 SNR을 측정합니다:

```python
import numpy as np

def quick_snr_check(reconstruction, roi_signal, roi_background):
    """
    재구성 이미지에서 SNR을 빠르게 측정합니다.

    roi_signal: (row_start, row_end, col_start, col_end) - 시료 영역
    roi_background: (row_start, row_end, col_start, col_end) - 배경 영역
    """
    signal_region = reconstruction[
        roi_signal[0]:roi_signal[1],
        roi_signal[2]:roi_signal[3]
    ]
    bg_region = reconstruction[
        roi_background[0]:roi_background[1],
        roi_background[2]:roi_background[3]
    ]

    signal_mean = np.mean(signal_region)
    bg_std = np.std(bg_region)

    snr = signal_mean / bg_std if bg_std > 0 else float('inf')
    print(f"Signal mean: {signal_mean:.4f}")
    print(f"Background std: {bg_std:.4f}")
    print(f"SNR: {snr:.1f}")

    if snr < 5:
        print("WARNING: Very low SNR - significant noise expected")
    elif snr < 20:
        print("CAUTION: Moderate SNR - some noise visible")
    else:
        print("OK: Adequate SNR")

    return snr
```

## 탐지 방법

### 시각적 지표

- **재구성 이미지:** 균일해야 할 영역에서 입상 패턴 관찰
- **배경 영역:** 공기 영역에서 0이 아닌 무작위 변동이 관찰됨
- **프로파일 분석:** 선 프로파일에서 급격한 무작위 변동
- **주파수 분석:** 파워 스펙트럼에서 고주파 노이즈 성분이 지배적

### 자동 탐지

```python
import numpy as np

def assess_noise_level(reconstruction, background_mask=None):
    """
    재구성 이미지의 노이즈 수준을 평가합니다.

    Parameters
    ----------
    reconstruction : np.ndarray
        2D 재구성 슬라이스
    background_mask : np.ndarray, optional
        배경(공기) 영역을 나타내는 불리언 마스크

    Returns
    -------
    dict
        노이즈 평가 결과를 담은 딕셔너리
    """
    if background_mask is None:
        # 이미지 모서리를 배경으로 가정
        h, w = reconstruction.shape
        margin = min(h, w) // 10
        background_mask = np.zeros_like(reconstruction, dtype=bool)
        background_mask[:margin, :] = True
        background_mask[-margin:, :] = True

    bg_values = reconstruction[background_mask]

    # 기본 통계
    bg_mean = np.mean(bg_values)
    bg_std = np.std(bg_values)
    bg_mad = np.median(np.abs(bg_values - np.median(bg_values))) * 1.4826

    # SNR 추정 (시료 영역 vs 배경)
    signal_values = reconstruction[~background_mask]
    snr = np.mean(signal_values) / bg_std if bg_std > 0 else float('inf')

    # 노이즈 파워 스펙트럼 (NPS)
    bg_patch_size = min(64, margin)
    if bg_patch_size > 10:
        bg_patch = reconstruction[:bg_patch_size, :bg_patch_size]
        fft_patch = np.fft.fft2(bg_patch - np.mean(bg_patch))
        nps = np.abs(fft_patch) ** 2 / bg_patch.size
        nps_mean = float(np.mean(nps))
    else:
        nps_mean = 0.0

    # 심각도 분류
    if snr < 5:
        severity = "critical"
    elif snr < 10:
        severity = "major"
    elif snr < 20:
        severity = "minor"
    else:
        severity = "acceptable"

    return {
        "background_mean": float(bg_mean),
        "background_std": float(bg_std),
        "background_mad": float(bg_mad),
        "snr": float(snr),
        "nps_mean": nps_mean,
        "severity": severity
    }
```

## 해결 및 완화

### 예방 (데이터 수집 전)

- 노출 시간을 최대한 늘려 광자 통계를 개선합니다
- 빔라인 광학을 최적화하여 시료에 도달하는 플럭스(flux)를 극대화합니다
- 프로젝션 수보다 프로젝션당 광자 수를 우선하여 설계합니다
- 검출기의 양자 효율이 높은 에너지 범위에서 실험합니다
- 동일 각도에서 다수 프레임을 촬영하여 평균합니다

### 보정 — 전통적 방법

```python
import numpy as np
from scipy import ndimage

# 방법 1: BM3D 필터링 (블록 매칭 3D)
# 고급 노이즈 저감 필터 (bm3d 패키지 필요)
# pip install bm3d
import bm3d
denoised_bm3d = bm3d.bm3d(
    reconstruction,
    sigma_psd=estimated_noise_std,  # 추정된 노이즈 표준편차
    stage_arg=bm3d.BM3DStages.ALL_STAGES
)

# 방법 2: 비국소 평균 필터링 (NLM)
from skimage.restoration import denoise_nl_means, estimate_sigma
sigma_est = estimate_sigma(reconstruction)
denoised_nlm = denoise_nl_means(
    reconstruction,
    h=1.15 * sigma_est,    # 필터 강도
    fast_mode=True,
    patch_size=5,           # 패치 크기
    patch_distance=6        # 패치 검색 거리
)

# 방법 3: 프로젝션 평균
# 동일 각도에서 여러 프레임을 촬영한 경우
def average_projections(projections_stack, num_averages=4):
    """동일 각도에서 촬영한 다수 프로젝션을 평균합니다."""
    n_angles = projections_stack.shape[0] // num_averages
    averaged = np.zeros((n_angles,) + projections_stack.shape[1:])
    for i in range(n_angles):
        averaged[i] = np.mean(
            projections_stack[i * num_averages:(i + 1) * num_averages],
            axis=0
        )
    return averaged
```

### 보정 — AI/ML 방법

| 방법 | 유형 | 설명 |
|------|------|------|
| **TomoGAN** | 적대적 학습 | 저선량 재구성을 고선량 품질로 변환하는 GAN 기반 노이즈 저감 |
| **Noise2Noise** | 자기지도 학습 | 깨끗한 참조 이미지 없이 노이즈 이미지 쌍만으로 노이즈 저감 학습 |
| **Deep Image Prior** | 비지도 학습 | 네트워크 구조 자체를 정규화로 활용하는 단일 이미지 노이즈 저감 |
| **RED-CNN** | 지도 학습 | 잔차 인코더-디코더 구조의 CT 전용 노이즈 저감 네트워크 |

TomoGAN은 방사광 토모그래피에 특화된 접근 방식으로, 적대적 학습을 통해 저선량 노이즈의 통계적 특성을 학습하여 제거합니다. Noise2Noise는 깨끗한 참조 데이터가 없는 경우에 효과적이며, 동일 시료의 독립적인 노이즈 관측 쌍만으로 학습이 가능합니다.

## 미보정 시 영향

- **대비(Contrast) 저하:** 노이즈로 인해 유사한 밀도의 물질 간 구분이 어려워짐
- **세분화(Segmentation) 정확도 저하:** 노이즈가 임계값 기반 세분화를 방해하여 잘못된 분류 발생
- **정량적 분석 신뢰도 저하:** 노이즈가 밀도, 기공률 등의 정량적 측정에 불확실성을 추가
- **미세 구조 손실:** 노이즈 수준보다 낮은 대비의 미세 구조가 검출 불가능
- **3D 분석 저해:** 슬라이스별 독립적인 노이즈가 3D 연결성 분석을 방해

## 관련 자료

- [TomoPy를 활용한 탐색적 데이터 분석(EDA)](../../03_eda/tomo_eda.md)
- [TomoGAN](../../08_ai_ml/tomogan.md)
- [Noise2Noise](../../08_ai_ml/noise2noise.md)
- [희소각 아티팩트](sparse_angle_artifact.md)
- [빔 강도 저하](beam_intensity_drop.md)

## 핵심 요약

> **노이즈 저감은 재구성 전 사이노그램 도메인에서 수행하는 것이 가장 효과적입니다.** 프로젝션 단계에서의 노이즈 저감은 재구성 후 이미지 도메인에서의 필터링보다 아티팩트를 적게 도입하며, AI/ML 기반 방법(TomoGAN, Noise2Noise)은 전통적 필터링보다 세부 구조를 더 잘 보존하면서 노이즈를 효과적으로 제거할 수 있습니다.
