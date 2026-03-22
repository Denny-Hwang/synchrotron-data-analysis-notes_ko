# 검출기 공통 문제(Detector Common Issues)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 교차 분야(Cross-cutting) |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 보통(Moderate) |

## 설명

검출기 공통 문제는 X선 검출의 물리적 특성에서 비롯되는 다양한 아티팩트를 포괄합니다: 비균일 픽셀 응답(게인 변동), 이전 노출의 잔광/고스팅, 픽셀 크로스토크(인접 픽셀 간 전하 공유), 신틸레이터 물질의 시간 의존적 열화 등이 있습니다. 모든 검출기에 어느 정도 존재하며, 모든 싱크로트론 이미징 모달리티에 영향을 미칩니다.

## 근본 원인

- **비균일 응답:** 픽셀 감도의 제조 변동, 신틸레이터 두께 비균일성, 간접 검출기의 광학 결합 변동
- **잔광/고스팅:** 신틸레이터 기반 검출기에서 프레임 판독 시간을 초과하는 발광 감쇠. 직접 검출 광자 계수 검출기(예: Dectris EIGER, Pilatus)는 잔광에 거의 면역
- **픽셀 크로스토크:** 하이브리드 픽셀 검출기의 전하 공유 및 신틸레이터 결합 검출기의 광학 확산
- **신틸레이터 열화:** 누적 방사선 선량에 따른 변환 효율 감소

## 빠른 진단

```python
import numpy as np

mean_flat = np.mean(flats, axis=0)
cv = np.std(mean_flat) / np.mean(mean_flat)
print(f"플랫필드 CV: {cv:.4f} (>0.05이면 상당한 비균일성)")
afterglow_fraction = np.mean(dark_after_bright) / np.mean(mean_flat)
print(f"잔광 비율: {afterglow_fraction:.4e} (>1e-3이면 문제)")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 각 실험 시작 시와 긴 세션 중 주기적으로 플랫필드 및 다크 전류 교정을 수행합니다.
- 가시적 번 마크나 상당한 효율 손실을 보이는 신틸레이터를 교체합니다.
- 잔광에 민감한 실험(빠른 토모그래피, XPCS)에는 광자 계수 검출기를 사용합니다.
- 각 검출기의 불량 픽셀 맵을 유지하고 정기적으로 업데이트합니다.

### 보정 — 전통적 방법

표준 3단계 보정: 다크 차감, 플랫필드 정규화, 불량 픽셀 보간.

```python
import numpy as np
from scipy.ndimage import median_filter


def apply_detector_corrections(raw_data, dark_map, flat_map, bad_pixel_mask,
                                afterglow_correction=False,
                                afterglow_decay=0.005):
    """원시 이미지 데이터에 표준 검출기 보정을 적용합니다."""
    is_single = raw_data.ndim == 2
    if is_single:
        raw_data = raw_data[np.newaxis]

    num_frames = raw_data.shape[0]
    corrected = np.empty_like(raw_data, dtype=np.float32)

    flat_norm = flat_map / (np.mean(flat_map) + 1e-10)
    gain_correction = np.where(flat_norm > 0.1, 1.0 / flat_norm, 0.0)

    previous_frame = None

    for i in range(num_frames):
        frame = raw_data[i].astype(np.float32)
        frame -= dark_map

        if afterglow_correction and previous_frame is not None:
            frame -= afterglow_decay * previous_frame
        previous_frame = frame.copy()

        frame *= gain_correction

        if np.any(bad_pixel_mask):
            median_img = median_filter(frame, size=3)
            frame[bad_pixel_mask] = median_img[bad_pixel_mask]

        corrected[i] = frame

    if is_single:
        corrected = corrected[0]

    return corrected
```

## 보정하지 않을 경우의 영향

비균일 검출기 응답은 모든 모달리티에 걸쳐 정량적 강도 측정을 직접 손상시킵니다. 토모그래피에서는 보정되지 않은 게인 변동이 링 아티팩트를 생성합니다. 타이코그래피에서는 강도 오류가 위상 오류로 전파됩니다. XRF에서는 비균일 효율이 시야 전체에 걸쳐 원소 정량화를 편향시킵니다.

## 관련 자료

- [링 아티팩트](../tomography/ring_artifact.md) — 검출기 비균일성의 직접적 결과
- [데드/핫 픽셀](../xrf_microscopy/dead_hot_pixel.md) — 극단적 픽셀 응답 편차의 특정 사례
- [토모그래피 EDA 노트북](../../06_data_structures/eda/tomo_eda.md) — 플랫필드 품질 검사

## 핵심 요점

검출기 아티팩트는 보편적이며 모든 측정에 영향을 미칩니다 — 새로운 플랫필드 및 다크 이미지로 정기적인 교정을 수행하는 것이 모든 싱크로트론 빔라인에서 가장 중요한 품질 보증 단계이며, 잘 유지된 불량 픽셀 마스크와 적절한 플랫필드 보정의 조합이 검출기 관련 체계적 오류의 대부분을 제거합니다.
