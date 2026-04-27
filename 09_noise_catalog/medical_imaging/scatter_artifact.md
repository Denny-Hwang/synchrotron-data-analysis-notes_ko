# 산란 아티팩트(Scatter Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 의료 CT / 방사광 토모그래피 |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 의료 영상(CT) |

## 시각적 예시

![보정 전후 — 산란 아티팩트](../images/scatter_artifact_before_after.png)

> **이미지 출처:** Compton 산란 배경이 시뮬레이션된 합성 팬텀. 왼쪽: 산란으로 인한 대비 감소와 안개 효과. 오른쪽: 산란 커널 차감 후. MIT 라이선스.

## 설명

산란 아티팩트는 X선 광자가 시료 내에서 Compton 또는 코히어런트 산란을 겪고 일차 빔 경로와 일치하지 않는 위치에서 검출기에 도달할 때 발생합니다. 이는 투영에 광범위한 저주파 배경을 추가하여 대비를 감소시키고, 컵핑 아티팩트를 도입하며, 고밀도 구조물 사이에 셰이딩/줄무늬를 만듭니다. 콘빔(cone-beam) 형상(의료 CBCT와 방사광 마이크로 CT에서 흔함)에서 산란은 검출기 신호의 20-80%를 차지할 수 있습니다.

## 근본 원인

- **Compton 산란:** 광자가 외각 전자와 상호작용한 후 방향이 바뀜 (의료 CT 에너지 30-120 keV에서 지배적)
- **코히어런트(Rayleigh) 산란:** 에너지 손실 없이 광자 방향이 바뀜 (저에너지에서 유의미함)
- 산란율(scatter fraction) 증가 요인: 시료 크기, 콘 각도, 광자 에너지, 검출기 면적
- 산란된 광자가 잘못된 검출기 위치에 도달 → 투영에 거짓 신호 추가

## 빠른 진단

```python
import numpy as np

def estimate_scatter_fraction(projection, air_region_mask):
    """Estimate scatter by measuring signal in known air regions."""
    air_signal = projection[air_region_mask].mean()
    max_signal = projection.max()
    scatter_fraction = air_signal / max_signal
    print(f"Estimated scatter fraction: {scatter_fraction:.1%}")
    print(f"{'⚠ High scatter' if scatter_fraction > 0.1 else 'Acceptable'}")
    return scatter_fraction
```

## 탐지 방법

### 시각적 지표

- 예상 값 대비 감소된 대비
- 균일한 팬텀에서의 컵핑 아티팩트(빔 경화와 유사)
- 고밀도 구조물 사이의 확산형 셰이딩
- "공기"(감쇠 0)이어야 할 영역의 신호 존재

### 자동 탐지

```python
import numpy as np

def scatter_cupping_test(recon_slice, object_mask):
    """Differentiate scatter cupping from beam-hardening cupping."""
    # Scatter cupping is broader and lower frequency than BH cupping
    from scipy.ndimage import uniform_filter
    low_freq = uniform_filter(recon_slice, size=50)
    masked_profile = low_freq[object_mask]
    # Check for systematic low-frequency non-uniformity
    cv = np.std(masked_profile) / np.mean(masked_profile)
    return cv  # >0.05 suggests scatter contribution
```

## 보정 방법

### 전통적 접근법

1. **안티스캐터 그리드(Anti-scatter grid):** 검출기 앞의 물리적 콜리메이션 (하드웨어 레벨에서 산란 감소)
2. **에어 갭(Air-gap) 기법:** 시료-검출기 거리를 증가시켜 광각 산란을 거부
3. **산란 커널 추정:** 산란 PSF를 모델링하여 투영으로부터 디컨볼브
4. **몬테카를로 시뮬레이션:** 주어진 형상에 대한 산란 분포를 시뮬레이션하여 차감
5. **빔 차단기(Beam-blocker) 방법:** 빔 경로의 납 스트립을 사용해 산란을 직접 측정

```python
def simple_scatter_correction(projection, scatter_estimate):
    """Subtract estimated scatter from projection."""
    corrected = projection - scatter_estimate
    corrected[corrected < 0] = 0  # Avoid negative values
    return corrected
```

### AI/ML 접근법

- **Deep scatter estimation (DSE):** 몬테카를로 산란 데이터로 학습된 CNN (Maier et al., 2019)
- **Scatter-Net:** 일차 영상으로부터 산란 분포를 예측하는 U-Net
- **물리 정보 네트워크:** 손실 함수에 순방향 산란 모델을 내장

## 주요 참고문헌

- **Siewerdsen & Jaffray (2001)** — "Cone-beam computed tomography with a flat-panel imager: scatter estimation"
- **Rührnschopf & Klingenbeck (2011)** — "A general framework for scatter correction in CT" (2부작 시리즈)
- **Maier et al. (2019)** — "Deep scatter estimation" — 학습 기반 접근법
- **Star-Lack et al. (2009)** — "Efficient scatter correction using asymmetric kernels"

## 방사광 데이터와의 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 콘빔 마이크로 CT | 직접적 유사 사례 — CBCT 형상에서 유의미한 산란 |
| 광시야 토모그래피 | 큰 빔/검출기 → 더 많은 산란 |
| 고밀도/두꺼운 시료 | 산란율이 급격히 증가 |
| 위상대비 영상 | 산란이 위상 복원을 교란 |
| SAXS/WAXS | 기생 산란이 지배적 노이즈 원천 |

## 관련 자료

- [Beam hardening](beam_hardening.md) — 유사한 컵핑 외형이지만 메커니즘이 다름
- [Streak artifact](../tomography/streak_artifact.md) — 고밀도 물체는 산란과 줄무늬 아티팩트를 모두 유발
