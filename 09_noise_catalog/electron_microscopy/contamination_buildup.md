# 오염 축적(Contamination Buildup)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | SEM / TEM |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 보통(Moderate) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |
| **기원 도메인** | 전자현미경 |

## 설명

오염 축적은 전자빔 조사 하에서 시료 표면에 탄소질 물질이 침착되는 현상입니다. 탄화수소 분자(진공 펌프 오일, 시료 준비, 또는 잔류 가스로부터)는 표면에 흡착된 후 전자빔에 의해 중합/분해되어 점차 두꺼워지는 탄소 막을 형성합니다. 이는 SEM에서 표면 디테일을 가리고, TEM에서 비정질 배경을 추가하며, 시간에 따라 이미지 품질을 점진적으로 저하시킵니다.

## 근본 원인

- 진공 챔버 내 탄화수소 분자 존재 (잔류 가스, 펌프 백스트리밍)
- 전자빔이 탄화수소를 분해/중합 → 불용성 탄소 침적물
- 침착률 ∝ 빔 전류 × 탄화수소 부분압
- 집속 빔 → 오염 스폿; 스캐닝 → 오염 막
- TEM에서: 오염은 전자를 산란시키고 대비를 감소시키는 비정질 층을 형성

## 빠른 진단

```python
import numpy as np

def detect_contamination_spot(image_sequence):
    """동일 영역의 순차적 이미지로부터 오염의 성장을 탐지합니다."""
    # 오염은 빔 위치에서 점진적인 어두워짐을 유발
    mean_intensities = [img.mean() for img in image_sequence]
    # 단조 감소는 오염 축적을 시사
    diffs = np.diff(mean_intensities)
    if np.all(diffs < 0):
        rate = abs(np.mean(diffs))
        print(f"Progressive signal loss detected: {rate:.2f}/frame — likely contamination")
    return mean_intensities
```

## 보정 방법

### 예방 (1차)

1. **플라즈마 클리닝:** 로딩 전 Ar/O2 플라즈마로 시료 및 홀더 청소
2. **빔 샤워(Beam shower):** 광폭 빔으로 사전 조사하여 탄화수소 제거
3. **저온 차폐(Cryo-shielding, cold finger):** 시료 근처의 콜드 트랩이 탄화수소를 응축
4. **개선된 진공:** 더 나은 펌핑, 무오일 펌프, 베이킹
5. **청정한 시료 준비:** 유기 오염 최소화

### 데이터 수집 후

- 초기 vs 후기 프레임을 비교하고 오염된 프레임 폐기
- 추정된 오염 배경(저주파 성분) 차감

## 핵심 참고문헌

- **Hren (1979)** — "Barriers to AEM: contamination and etching" — 기초적 설명
- **Egerton et al. (2004)** — "Radiation damage in the TEM and SEM"
- **Mitchell (2015)** — "Contamination mitigation strategies for SEM"

## 방사광 데이터 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 탄소 K-edge STXM/NEXAFS | 오염이 허위 탄소 신호를 추가 |
| In-situ 실험 | 반응 가스로부터의 탄화수소 오염 |
| 상관 EM + 방사광 | EM의 오염이 후속 방사광 측정에 영향 |
| XPS / 연 X선 분광법 | 탄소 오염 층이 신호를 감쇠시킴 |

## 관련 자료

- [방사선 손상](../spectroscopy/radiation_damage.md) — 둘 다 빔에 의한 시료 변형
- [빔 강도 감소](../tomography/beam_intensity_drop.md) — 실험 중 점진적 신호 변화
