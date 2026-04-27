# 차징 아티팩트 (SEM)(Charging Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | SEM |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 쉬움(Easy) |
| **기원 도메인** | 주사 전자 현미경(SEM) |

## 설명

차징(charging) 아티팩트는 비전도성 또는 접지가 부적절한 시료가 입사 전자빔으로부터 전하를 축적할 때 SEM에서 발생합니다. 축적된 전하는 국소 전기장을 형성하여 입사 및 방출 전자를 편향시키고, 밝은 패치, 이미지 왜곡, 이미지 드리프트, 비정상적인 대비를 유발합니다. 이 효과는 동적입니다 — 차징은 스캐닝 중에 축적되어 갑작스러운 밝기 변화 또는 이미지 "점프"를 일으킬 수 있습니다.

## 근본 원인

- 비전도성 시료가 입사 전자 전하를 분산시킬 수 없음
- 전하 축적 → 국소 표면 전위가 상승 (수백 볼트에 도달 가능)
- 전기장이 1차 빔을 편향시킴 → 기하학적 왜곡
- 전기장이 2차 전자 방출 및 수집을 변경 → 비정상적 밝기
- 악화 요인: 빔 전류 증가, 가속 전압 증가, 접지 불량, 절연성 시료

## 빠른 진단

```python
import numpy as np

def detect_charging(image, direction='horizontal'):
    """스캔 방향을 따른 밝기 변화로 차징을 탐지합니다."""
    if direction == 'horizontal':
        # 스캔 라인을 따라 점진적인 밝아짐 확인
        row_means = image.mean(axis=1)
    else:
        row_means = image.mean(axis=0)
    # 차징은 체계적인 강도 추세를 유발
    trend = np.polyfit(np.arange(len(row_means)), row_means, 1)
    print(f"Intensity slope: {trend[0]:.4f} (non-zero suggests charging)")
    # 갑작스러운 점프 확인
    diffs = np.abs(np.diff(row_means))
    jumps = np.where(diffs > 3 * np.std(diffs))[0]
    if len(jumps) > 0:
        print(f"Sudden intensity jumps at lines: {jumps}")
    return trend[0], jumps
```

## 탐지 방법

### 시각적 지표

- 절연 영역의 밝고 포화된 패치
- 스캔 라인 사이의 이미지 "스트리킹" 또는 밝기 변화
- 기하학적 왜곡 (특징이 이동하거나 일그러져 보임)
- 연속 스캔 사이의 동적 변화 (시간이 지나며 차징이 축적)
- 절연성 입자에 비정상적으로 밝은 가장자리

### 자동 탐지

```python
import numpy as np

def charging_map(image_sequence):
    """순차적 프레임을 비교하여 점진적인 차징을 탐지합니다."""
    diffs = []
    for i in range(1, len(image_sequence)):
        diff = image_sequence[i].astype(float) - image_sequence[i-1].astype(float)
        diffs.append(diff)
    cumulative_drift = np.abs(np.array(diffs)).mean(axis=0)
    return cumulative_drift  # 높은 값 = 차징 영역
```

## 보정 방법

### 전통적 접근법 (예방 중심)

1. **전도성 코팅:** Au, Pt, C, 또는 Ir로 스퍼터 코팅 (5-20 nm)
2. **저전압 SEM:** 입력 = 출력 전자가 되는 전하 균형 전압(0.5-2 kV)에서 운영
3. **가변 압력 / ESEM:** 가스 분자가 표면 전하를 중화
4. **전하 보상:** 플러드 건(flood gun) 또는 질소 가스 주입
5. **전하 분산을 동반한 프레임 평균화:** 프레임 사이에 안정 시간 부여

### 데이터 수집 후 보정

```python
def destripe_charging(image, sigma=50):
    """행 정규화로 스캔 라인 차징 줄무늬를 제거합니다."""
    from scipy.ndimage import gaussian_filter1d
    row_means = image.mean(axis=1)
    smooth_baseline = gaussian_filter1d(row_means, sigma)
    correction = smooth_baseline / row_means
    corrected = image * correction[:, np.newaxis]
    return corrected
```

## 핵심 참고문헌

- **Cazaux (2004)** — "Charging in scanning electron microscopy" — 종합적인 물리 리뷰
- **Joy & Joy (1996)** — "Low voltage SEM" — 전하 균형 이미징
- **Thiel & Toth (2005)** — "Secondary electron contrast in ESEM" — 환경 SEM 접근법

## 방사광 데이터 관련성

| 시나리오 | 관련성 |
|----------|--------|
| STXM / X-PEEM | 절연체로부터의 광전자 방출이 유사한 차징을 유발 |
| 방사광 XPS | 표면 차징이 결합 에너지를 이동시킴 |
| 상관 SEM + 방사광 | SEM 차징 이해가 다중 모달 정합에 도움 |
| In-situ 전기화학 | 전극의 전하 축적이 SEM과 X선 모두에 영향 |

## 관련 자료

- [스캔 줄무늬](../xrf_microscopy/scan_stripe.md) — 유사한 행별 강도 변화
- [빔 강도 감소](../tomography/beam_intensity_drop.md) — 시간 의존적 강도 변화
