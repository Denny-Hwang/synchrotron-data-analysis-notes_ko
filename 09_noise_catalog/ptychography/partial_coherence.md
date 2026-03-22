# 부분 코히어런스 효과(Partial Coherence Effects)

## 분류

| 속성 | 값 |
|------|-----|
| **모달리티** | 타이코그래피 |
| **노이즈 유형** | 기기(Instrumental) |
| **심각도** | 주요(Major) |
| **빈도** | 흔함(Common) |
| **탐지 난이도** | 어려움(Hard) |

## 시각적 예시

```
완전 코히어런트 조명                   부분 코히어런트 조명

  ┌──────────────────────┐           ┌──────────────────────┐
  │  선명한 프린지        │           │  희미해진 프린지      │
  │  ╱╲╱╲╱╲╱╲╱╲╱╲╱╲    │           │  ∿∿∿∿∿∿∿∿∿∿∿∿∿     │
  │  명확한 위상 엣지    │    →      │  흐릿한 경계          │
  │  ──┐    ┌──          │           │  ──╲    ╱──          │
  │    │    │            │           │     ╲  ╱             │
  └──────────────────────┘           └──────────────────────┘
```

> **외부 참고자료:**
> - [Thibault & Menzel — 혼합 상태 타이코그래피](https://doi.org/10.1038/nature11806)

## 설명

부분 코히어런스 효과는 조명 X선 빔이 완전히 코히어런트한 평면파 또는 점 광원의 이상적 가정에서 벗어날 때 발생합니다. 공간적, 시간적 코히어런스의 감소는 회절 패턴의 고주파 간섭 특징을 희석시켜 재구성된 위상 및 진폭 이미지의 대비 손실과 해상도 저하를 유발합니다. 이 효과는 특히 교활한데, 부드럽고 그럴듯해 보이지만 세밀한 디테일이 단순히 누락된 재구성을 생성하기 때문에 아티팩트 탐지가 총체적 왜곡보다 어렵습니다.

## 근본 원인

공간적 코히어런스는 유한한 광원 크기에 의해 제한됩니다. 시간적(종방향) 코히어런스는 모노크로메이터 대역폭에 의해 설정됩니다 — Si(111) 모노크로메이터는 ΔE/E ~ 1.4×10⁻⁴를 제공하여 ~1 μm의 종방향 코히어런스 길이를 산출합니다. 광학 요소의 기계적 진동은 노출 중 광원 위치를 번지게 하여 유효 코히어런스를 더 줄입니다. 코히어런스 길이가 조명 영역보다 작으면, 측정된 회절 패턴은 여러 코히어런트 모드의 비코히어런트 합이 되어 표준 타이코그래피 알고리즘의 단일 모드 가정을 위반합니다.

## 빠른 진단

```python
import numpy as np

# 스캔 중앙의 회절 패턴 로드
# dp = diffraction_data[len(diffraction_data)//2]
# 고공간주파수에서 프린지 가시성 확인
radial_profile = np.mean(dp.reshape(-1)[np.argsort(
    np.hypot(*np.mgrid[-dp.shape[0]//2:dp.shape[0]//2,
                        -dp.shape[1]//2:dp.shape[1]//2].reshape(2, -1)).ravel()
)].reshape(-1, 4), axis=1)
visibility = (radial_profile.max() - radial_profile.min()) / (radial_profile.max() + 1e-10)
print(f"프린지 가시성: {visibility:.3f} (< 0.3이면 부분 코히어런스 의심)")
```

## 해결 방법 및 완화

### 예방 (데이터 수집 전)

- 코히어런스 보존 빔라인 광학 레이아웃을 사용하고, 빔의 코히어런트 부분을 선택하기 위해 어퍼처 크기를 최소화합니다.
- 시간적 코히어런스가 제한적일 때 더 고해상도 모노크로메이터(예: Si(220) 또는 채널 컷)를 선택합니다.
- 4세대 광원(MBA 격자), 예를 들어 APS-U, ESRF-EBS, MAX IV로 업그레이드하면 코히어런트 플럭스가 수 배 이상 높아집니다.

### 보정 — 전통적 방법

혼합 상태 타이코그래피(mixed-state ptychography)는 조명을 상호 비코히어런트한 프로브 모드 세트로 분해하여 각각을 동시에 재구성합니다. 이를 통해 부분 코히어런스에서도 올바른 대비로 물체를 복원합니다.

```python
import numpy as np


def mixed_state_ePIE(diffraction_data, positions, num_modes=5,
                     num_iterations=100, probe_init=None, object_init=None):
    """
    부분 코히어런스를 여러 프로브 모드로 처리하는
    간소화된 혼합 상태 ePIE 재구성 (Thibault & Menzel 2013).
    """
    N = len(diffraction_data)
    py, px = diffraction_data.shape[1], diffraction_data.shape[2]

    if probe_init is None:
        probe_init = np.ones((py, px), dtype=complex)
    probe_modes = []
    for m in range(num_modes):
        amplitude_scale = 1.0 / (m + 1)
        mode = probe_init * amplitude_scale
        if m > 0:
            mode *= np.exp(2j * np.pi * np.random.rand(py, px))
        probe_modes.append(mode.copy())

    obj_shape = (
        int(np.max(positions[:, 0])) + py + 10,
        int(np.max(positions[:, 1])) + px + 10,
    )
    obj = np.ones(obj_shape, dtype=complex) if object_init is None else object_init.copy()
    alpha = 1.0

    for iteration in range(num_iterations):
        order = np.random.permutation(N)
        total_error = 0.0
        for idx in order:
            row = int(round(positions[idx, 0]))
            col = int(round(positions[idx, 1]))
            obj_patch = obj[row:row + py, col:col + px]

            exit_waves = [pm * obj_patch for pm in probe_modes]
            exit_fts = [np.fft.fft2(ew) for ew in exit_waves]
            intensity_sum = sum(np.abs(ef)**2 for ef in exit_fts)
            measured_amp = np.sqrt(diffraction_data[idx].astype(float))
            calc_amp = np.sqrt(intensity_sum + 1e-15)
            total_error += np.sum((calc_amp - measured_amp)**2)

            for m in range(num_modes):
                corrected_ft = exit_fts[m] * measured_amp / (calc_amp + 1e-15)
                exit_corrected = np.fft.ifft2(corrected_ft)
                diff = exit_corrected - exit_waves[m]
                obj[row:row + py, col:col + px] += (
                    alpha * np.conj(probe_modes[m])
                    / (np.max(np.abs(probe_modes[m]))**2 + 1e-8) * diff
                )
                probe_modes[m] += (
                    alpha * np.conj(obj_patch)
                    / (np.max(np.abs(obj_patch))**2 + 1e-8) * diff
                )

        if iteration % 10 == 0:
            print(f"반복 {iteration}: 오류 = {total_error:.4e}")

    return obj, probe_modes
```

## 보정하지 않을 경우의 영향

부분 코히어런스는 타이코그래피 재구성의 유효 해상도와 위상 대비를 회절 한계 대비 2-10배 감소시킵니다. 결정립계, 나노스케일 기공, 박막 계면과 같은 미세 특징이 재구성에서 완전히 보이지 않을 수 있습니다. 정량적 위상 측정은 고공간주파수에서 위상 전달 함수가 감쇠되어 신뢰할 수 없게 됩니다.

## 관련 자료

- [위치 오류](position_error.md) — 위치 오류가 코히어런스 문제와 복합됨
- [스티칭 아티팩트](stitching_artifact.md) — 스캔 영역에 걸친 코히어런스 변동이 타일 간 일관성에 영향
- [Thibault & Menzel 2013](https://doi.org/10.1038/nature11806) — 혼합 상태 타이코그래피 원논문

## 핵심 요점

부분 코히어런스는 대부분의 싱크로트론 빔라인에서 불가피한 현실이며 재구성 품질을 무음으로 저하시킵니다. 항상 최소 3-5개의 프로브 모드를 가진 혼합 상태 타이코그래피를 기본값으로 사용하세요 — 계산 오버헤드는 적당하며, 부분 코히어런스가 무시될 때 발생하는 교활한 해상도 및 대비 손실을 방지합니다.
