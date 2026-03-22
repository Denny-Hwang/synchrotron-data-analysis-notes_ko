# 위치 오류(Position Error)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 타이코그래피 |
| **노이즈 유형** | 체계적(Systematic) |
| **심각도** | 심각(Critical) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 어려움(Hard) |

## 시각적 예시

```
예상 (올바른 위치)                관측 (위치 오류)

  +---+---+---+---+               +---+--+----+---+
  | . | . | . | . |               | . |. |  . | . |
  +---+---+---+---+        →     +--+---+--+----+
  | . | . | . | . |               |  .| .  |. |  .|
  +---+---+---+---+               +---+--+---+----+

  선명한 재구성                     흐릿/고스팅된 특징
```

> **외부 참고자료:**
> - [edgePtychoNN — DL 위치 보정 (Babu et al. 2023)](https://doi.org/10.1038/s41467-023-41496-z)

## 설명

위치 오류는 기록된 프로브의 스캔 위치가 시료의 실제 물리적 위치에서 벗어날 때 발생합니다. 이 불일치로 반복 재구성 알고리즘이 회절 패턴을 잘못 겹치게 되어 흐린 특징, 고스팅, 수렴 실패를 초래합니다. 위치 오류는 스캐닝 타이코그래피에서 가장 흔하고 파괴적인 아티팩트 중 하나이며, 서브픽셀 정확도가 요구되는 고해상도에서 특히 심각합니다.

## 근본 원인

위치 오류의 주요 원인은 간섭계 드리프트, 피에조 스테이지 히스테리시스와 크리프, 엔코더 양자화 오류, 시료 스테이지의 열팽창입니다. 시설(바닥, 펌프, 크라이오쿨러)의 진동이 각 노출 중 유효 프로브 위치를 번지게 하는 고주파 지터를 도입합니다. 나노미터 규모 해상도에서는 수 나노미터의 추적되지 않은 움직임도 위상 복원에 필요한 겹침 조건을 초과할 수 있습니다.

## 빠른 진단

```python
import numpy as np

dy = np.diff(positions[:, 0])
dx = np.diff(positions[:, 1])
step_sizes = np.sqrt(dy**2 + dx**2)
irregularity = np.std(step_sizes) / np.mean(step_sizes)
print(f"스텝 크기 CV: {irregularity:.4f} (>0.05이면 위치 문제 의심)")
print(f"평균 스텝에서 최대 편차: {np.max(np.abs(step_sizes - np.mean(step_sizes))):.2e} m")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 스테이지 엔코더만 의존하지 말고 레이저 간섭계를 위치 피드백에 사용합니다.
- 진동원을 최소화합니다: 불필요한 펌프를 끄고 진동 격리 광학 테이블을 사용합니다.
- 스캐닝 전 피에조 히스테리시스와 크리프를 특성화하고 보상합니다.
- 인접 스캔 위치 간 충분한 겹침(>60%)을 보장합니다.

### 보정 — 전통적 방법

반복 재구성 중 공동 위치 보정이 회절 데이터 자체를 사용하여 기록된 위치를 보정합니다.

```python
import numpy as np

def position_correction_annealing(
    diffraction_stack, positions, probe, object_est,
    num_iterations=50, step_size=1e-9, anneal_start=10
):
    """ePIE 재구성 중 단순 기울기 기반 위치 보정."""
    refined_positions = positions.copy().astype(float)
    py, px = probe.shape
    num_pos = len(positions)

    for iteration in range(num_iterations):
        order = np.random.permutation(num_pos)
        for idx in order:
            row, col = int(round(refined_positions[idx, 0])), int(round(refined_positions[idx, 1]))
            obj_patch = object_est[row:row+py, col:col+px]
            exit_wave = probe * obj_patch

            exit_ft = np.fft.fft2(exit_wave)
            measured_amp = np.sqrt(diffraction_stack[idx])
            corrected_ft = measured_amp * np.exp(1j * np.angle(exit_ft))
            exit_corrected = np.fft.ifft2(corrected_ft)

            diff = exit_corrected - exit_wave
            object_est[row:row+py, col:col+px] += (
                np.conj(probe) / (np.max(np.abs(probe))**2 + 1e-8) * diff
            )

            if iteration >= anneal_start:
                grad_y = np.real(np.sum(
                    np.conj(diff) * np.roll(exit_wave, 1, axis=0) -
                    np.conj(diff) * np.roll(exit_wave, -1, axis=0)
                ))
                grad_x = np.real(np.sum(
                    np.conj(diff) * np.roll(exit_wave, 1, axis=1) -
                    np.conj(diff) * np.roll(exit_wave, -1, axis=1)
                ))
                refined_positions[idx, 0] -= step_size * np.sign(grad_y)
                refined_positions[idx, 1] -= step_size * np.sign(grad_x)

    return refined_positions
```

### 보정 — AI/ML 방법

**edgePtychoNN** (Babu et al. 2023)은 알려진 위치 오류를 가진 시뮬레이션된 타이코그래피 데이터셋에서 훈련된 CNN을 사용하여 서브픽셀 위치 오프셋을 예측합니다.

## 보정하지 않을 경우의 영향

위치 오류는 타이코그래피 재구성에서 달성 가능한 해상도를 직접 제한합니다. 수 나노미터의 체계적 오류도 이론적 한계 대비 2-5배 유효 해상도를 줄일 수 있습니다. 재구성이 전혀 수렴하지 않아 의미 없는 위상 맵을 생성할 수 있습니다. 플라이 스캔 타이코그래피에서 보정되지 않은 위치 오류는 실제 시료 특징을 모방하거나 가리는 스트리킹 아티팩트를 만듭니다.

## 관련 자료

- [부분 코히어런스 효과](partial_coherence.md) — 코히어런스 문제가 위치 오류 효과를 복합시킴
- [스티칭 아티팩트](stitching_artifact.md) — 타일 경계의 위치 오류가 스티칭 불일치를 악화시킴
- [edgePtychoNN (Babu et al. 2023)](https://doi.org/10.1038/s41467-023-41496-z)

## 핵심 요점

위치 오류는 타이코그래피에서 해상도 저하의 가장 흔한 단일 원인입니다. 재구성 중 항상 공동 위치 보정을 활성화하고, 가능하면 독립적인 간섭계 판독으로 위치를 검증하세요 — 회절 데이터 자체를 사용한 사후 위치 보정은 효과적이며 회절 한계 해상도 달성에 필수적입니다.
