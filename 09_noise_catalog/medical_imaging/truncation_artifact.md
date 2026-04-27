# 절단 아티팩트(Truncation Artifact, 시야 클리핑)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 의료 CT / 방사광 토모그래피 |
| **노이즈 유형** | 계통적(Systematic) |
| **심각도** | 주요(Major) |
| **빈도** | 가끔(Occasional) |
| **탐지 난이도** | 쉬움(Easy) |
| **기원 도메인** | 의료 영상(CT) |

## 시각적 예시

![보정 전후 — 절단 아티팩트](../images/truncation_artifact_before_after.png)

> **이미지 출처:** FOV 클리핑이 시뮬레이션된 합성 팬텀. 왼쪽: 불완전한 투영으로 인한 FOV 경계의 밝은 헤일로. 오른쪽: 사이노그램 외삽 보정 후. MIT 라이선스.

## 설명

절단 아티팩트는 시료가 하나 이상의 투영에서 검출기의 시야(FOV)를 넘어 확장될 때 발생합니다. 누락된 데이터는 재구성 볼륨에 밝은 가장자리 헤일로와 컵핑 같은 강도 왜곡을 일으킵니다. 의료 CT에서는 "환자가 스캔 FOV를 초과함"이라고 부르며, 방사광 토모그래피에서는 빔/검출기 폭보다 넓은 시료에서 발생합니다("국소 토모그래피" 또는 "관심 영역 CT").

## 근본 원인

- 시료가 검출기 폭보다 물리적으로 큼 → 가장자리에서 투영이 절단됨
- 불완전한 사이노그램의 역투영 → DC 오프셋 오류와 가장자리 밝아짐
- 수학적으로: Radon 역변환의 충분 샘플링 조건 위반
- 국소/내부 토모그래피: 의도적인 부분 FOV 스캐닝이 유사한 계통적 편향을 도입

## 빠른 진단

```python
import numpy as np

def detect_truncation(sinogram):
    """Check if sinogram is truncated at detector edges."""
    left_edge = sinogram[:, :5].mean(axis=1)
    right_edge = sinogram[:, -5:].mean(axis=1)
    center = sinogram[:, sinogram.shape[1]//2-2:sinogram.shape[1]//2+3].mean(axis=1)
    # Truncated if edge values are significantly non-zero (above background)
    threshold = center.mean() * 0.1
    left_truncated = (left_edge > threshold).sum() / len(left_edge)
    right_truncated = (right_edge > threshold).sum() / len(right_edge)
    print(f"Left edge active: {left_truncated:.1%}, Right edge active: {right_truncated:.1%}")
    if left_truncated > 0.3 or right_truncated > 0.3:
        print("⚠ Truncation likely — sample extends beyond FOV")
    return left_truncated, right_truncated
```

## 탐지 방법

### 시각적 지표

- 재구성 FOV의 경계에 밝거나 어두운 "헤일로" 링
- 재구성 전반에 걸친 점진적 강도 램프(컵핑 또는 캡핑)
- 사이노그램에서: 신호가 검출기 가장자리에서 0으로 감쇠하지 않고 갑자기 끊김

### 자동 탐지

```python
import numpy as np

def sinogram_edge_analysis(sinogram, margin=10):
    """Analyze sinogram edges for truncation."""
    edge_left = np.mean(np.abs(sinogram[:, :margin]))
    edge_right = np.mean(np.abs(sinogram[:, -margin:]))
    interior = np.mean(np.abs(sinogram[:, margin:-margin]))
    ratio = max(edge_left, edge_right) / (interior + 1e-10)
    return ratio  # >0.5 suggests truncation
```

## 보정 방법

### 전통적 접근법

1. **사이노그램 외삽:** 사이노그램 가장자리를 매끄럽게 감쇠하는 함수(코사인, 지수)로 패딩
2. **물 실린더 확장:** 객체가 FOV를 넘어 확장된 물 실린더에 매립되어 있다고 가정
3. **Helgason-Ludwig 일관성:** 데이터 일관성 조건을 이용해 누락 데이터를 추정
4. **다중 스캔 스티칭:** 여러 오프셋 스캔을 획득하여 사이노그램을 이어붙임

```python
def sinogram_padding(sinogram, pad_width=100, mode='cosine'):
    """Pad truncated sinogram with smooth extension."""
    n_angles, n_det = sinogram.shape
    padded = np.zeros((n_angles, n_det + 2 * pad_width))
    padded[:, pad_width:pad_width + n_det] = sinogram
    # Cosine decay at edges
    for i in range(pad_width):
        weight = 0.5 * (1 + np.cos(np.pi * i / pad_width))
        padded[:, pad_width - 1 - i] = sinogram[:, 0] * weight
        padded[:, pad_width + n_det + i] = sinogram[:, -1] * weight
    return padded
```

### AI/ML 접근법

- **사이노그램 인페인팅 네트워크:** U-Net 또는 GAN 기반 사이노그램 완성
- **DOLCE (2023):** 딥 모델 기반 국소 토모그래피 재구성
- **학습된 일관성:** 국소 CT에 대한 데이터 일관성을 강제하는 신경망

## 주요 참고문헌

- **Ohnesorge et al. (2000)** — CT 절단 아티팩트의 효율적 보정
- **Hsieh et al. (2004)** — "A novel reconstruction for truncation artifacts"
- **Kudo et al. (2008)** — 내부 토모그래피 이론 (정확한 내부 재구성)
- **Bao et al. (2019)** — "Convolutional sparse coding for truncation artifact reduction in CT"

## 방사광 데이터와의 관련성

| 시나리오 | 관련성 |
|----------|--------|
| 국소 / 내부 토모그래피 | 직접 적용 — 큰 시료의 경우 방사광에서 흔함 |
| 관심 영역 스캐닝 | 해상도 극대화를 위한 의도적 부분 FOV |
| 다중 해상도 스티칭 CT | 스티칭 경계가 유사한 가장자리 효과를 일으킬 수 있음 |
| 위상대비 국소 CT | 위상 복원과 절단이 사소하지 않게 상호작용 |

## 실제 보정 전후 사례

다음의 출판된 자료들은 실제 실험 보정 전후 비교를 제공합니다:

| 출처 | 유형 | 그림/위치 | 설명 | 라이선스 |
|------|------|-----------|------|----------|
| [Ohnesorge et al. 2000](https://doi.org/10.1118/1.598535) | 논문 | 다수 | Efficient correction for CT image artifacts caused by objects extending outside the scan field of view — 절단 보정 전후 | -- |

**출판된 보정 전후 비교를 포함한 주요 참고문헌:**
- **Ohnesorge et al. (2000)**: FOV 확장을 보여주는 보정 전후 예시가 포함된 CT 절단 아티팩트의 효율적 보정. DOI: 10.1118/1.598535

## 관련 자료

- [Rotation center error](../tomography/rotation_center_error.md) — 절단 효과를 가중시킬 수 있음
- [Sparse-angle artifact](../tomography/sparse_angle_artifact.md) — 둘 다 불완전 데이터 재구성 문제를 야기
- [Stitching artifact](../ptychography/stitching_artifact.md) — 타일링 획득의 관련 경계 아티팩트
