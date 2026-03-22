# 스티칭 아티팩트(Stitching Artifact)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 타이코그래피 |
| **노이즈 유형** | 계산(Computational) |
| **심각도** | 경미(Minor) |
| **빈도** | 간헐적(Occasional) |
| **탐지 난이도** | 쉬움(Easy) |

## 시각적 예시

```
타일 A          타일 B                 스티칭 결과 (아티팩트)
┌──────────┐  ┌──────────┐           ┌──────────┬──────────┐
│  위상=    │  │  위상=    │           │  위상=   ┃  위상=    │
│   1.2 rad │  │  1.2 rad  │    →     │  1.2 rad ┃  1.8 rad  │
│           │  │  + 0.6    │           │          ┃ (오프셋!) │
│           │  │  (오프셋) │           │  ────────┃────────── │
└──────────┘  └──────────┘           └──────────┴──────────┘
                                      경계에서 보이는 이음매 ↑

보정 후:
┌─────────────────────┐
│  위상 = 1.2 rad     │  이음매 없음
│  ────────────────── │
└─────────────────────┘
```

## 설명

스티칭 아티팩트는 대면적 타이코그래피 이미징에서 별도로 재구성된 타일 간의 경계에서 보이는 이음매, 강도 불연속 또는 위상 점프로 나타납니다. 시료가 단일 스캔 시야를 초과하면 여러 겹치는 스캔을 수집하고 독립적으로 재구성한 후 결합합니다. 타일 간의 수렴 수준, 위상 오프셋, 프로브 강도 변동, 배경 드리프트의 차이가 합성 이미지에 인공적 경계를 만듭니다.

## 근본 원인

각 타이코그래피 재구성은 고유한 위상 모호성이 있어 절대 위상이 정의되지 않으므로, 다른 타일은 임의의 위상 오프셋으로 수렴합니다. 또한 타일 수집 사이(수분~수시간)에 빔 강도가 드리프트하여 진폭 불일치를 유발할 수 있습니다. 초기 조건이 다르면 다른 타일이 다른 국소 최솟값으로 수렴할 수 있으며, 프로브 상태, 코히어런스 조건, 또는 스캔 중 시료 드리프트의 미세한 차이가 타일 간 불일치를 만듭니다.

## 빠른 진단

```python
import numpy as np

overlap_a = tile_a[:, -50:]
overlap_b = tile_b[:, :50]
phase_diff = np.angle(overlap_a * np.conj(overlap_b))
print(f"평균 위상 오프셋: {np.mean(phase_diff):.3f} rad")
print(f"위상 오프셋 표준편차: {np.std(phase_diff):.3f} rad (>0.1이면 스티칭 문제)")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 인접 타일 간 충분한 겹침(타일 너비의 최소 20-30%)을 보장합니다.
- I0을 모니터링하여 모든 타일 수집에 걸쳐 안정적인 빔 조건을 유지합니다.
- 드리프트를 최소화하기 위해 모든 타일을 빠르게 연속으로 수집합니다.

### 보정 — 전통적 방법

글로벌 위상 오프셋 보정과 겹침 가중 블렌딩이 대부분의 스티칭 아티팩트를 제거합니다.

```python
import numpy as np


def stitch_tiles_with_blending(tiles, positions, overlap_pixels=50):
    """위상 정렬과 겹침 가중 블렌딩으로 타이코그래피 타일을 스티칭합니다."""
    max_row = max(p[0] + t.shape[0] for p, t in zip(positions, tiles))
    max_col = max(p[1] + t.shape[1] for p, t in zip(positions, tiles))
    composite = np.zeros((max_row, max_col), dtype=complex)
    weight_map = np.zeros((max_row, max_col), dtype=float)

    for i, (tile, (r0, c0)) in enumerate(zip(tiles, positions)):
        if i > 0:
            r_end = r0 + tile.shape[0]
            c_end = c0 + tile.shape[1]
            existing_region = composite[r0:r_end, c0:c_end]
            existing_weight = weight_map[r0:r_end, c0:c_end]
            overlap_mask = existing_weight > 0
            if np.sum(overlap_mask) > 100:
                phase_offset = np.angle(
                    np.sum(existing_region[overlap_mask]
                           * np.conj(tile[overlap_mask]))
                )
                tile = tile * np.exp(1j * phase_offset)
                amp_ratio = (
                    np.mean(np.abs(existing_region[overlap_mask]))
                    / (np.mean(np.abs(tile[overlap_mask])) + 1e-10)
                )
                tile = tile * amp_ratio

        wy = np.minimum(np.arange(tile.shape[0]), np.arange(tile.shape[0])[::-1]).astype(float)
        wx = np.minimum(np.arange(tile.shape[1]), np.arange(tile.shape[1])[::-1]).astype(float)
        weight = np.outer(wy, wx)
        weight = np.clip(weight / (overlap_pixels / 2), 0, 1)

        composite[r0:r0 + tile.shape[0], c0:c0 + tile.shape[1]] += tile * weight
        weight_map[r0:r0 + tile.shape[0], c0:c0 + tile.shape[1]] += weight

    valid = weight_map > 0
    composite[valid] /= weight_map[valid]
    return composite
```

## 보정하지 않을 경우의 영향

스티칭 아티팩트는 정성적 이미징에서는 일반적으로 미용적이지만, 타일 경계에서 위상 측정을 평균화하면 정량적 오류를 유발할 수 있습니다. 세그멘테이션 알고리즘이 이음매를 실제 물질 경계로 해석할 수 있으며, 변형 매핑이나 파면 센싱 응용에서 위상 불연속이 기울기 필드를 직접 손상시킵니다.

## 관련 자료

- [위치 오류](position_error.md) — 타일 경계의 위치 오류가 스티칭 불일치를 악화시킴
- [부분 코히어런스 효과](partial_coherence.md) — 타일 간 코히어런스 드리프트가 강도 불일치에 기여

## 핵심 요점

스티칭 아티팩트는 탐지와 보정이 가장 쉬운 타이코그래피 아티팩트입니다 — 타일을 합성할 때 항상 글로벌 위상 정렬과 겹침 가중 블렌딩을 수행하고, 타일 경계를 가로지르는 특징이 연속적이고 일관적인지 확인하여 결과를 검증하세요.
