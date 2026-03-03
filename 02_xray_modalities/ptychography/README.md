# 타이코그래피(Ptychography) (결맞음 X선 이미징)

## 원리

**타이코그래피(Ptychography)**는 일련의 중첩된 회절 패턴으로부터 물체의 진폭(amplitude)과 위상(phase)을 모두 복원하는 결맞음 이미징(coherent imaging) 기법입니다. 렌즈 한계를 초과하는 공간 분해능을 달성하며 정량적 위상 정보를 제공합니다.

### 물리적 기초
1. 결맞음 X선 빔을 시료 위의 한 점에 집속
2. 출사파(exit wave)는 조명(probe)과 시료(object)의 곱
3. 각 스캔 위치에서 원거리장(far-field) 회절 패턴을 기록
4. 중첩된 조명 영역이 위상 복원을 위한 중복 정보를 제공
5. 반복 알고리즘이 probe와 object 복소 투과 함수(complex transmission function)를 모두 복원

### 핵심 개념: 위상 문제의 해결

다른 X선 기법과 달리, 타이코그래피는 **위상 문제(phase problem)**를 직접 해결합니다:
- 검출기는 강도 |ψ|²만 기록 (위상 정보 손실)
- 인접 스캔 위치 간의 중첩 조건(overlap constraint)이 추가 방정식을 제공
- 반복 알고리즘이 진폭과 위상 모두에 대한 유일한 해로 수렴

### 타이코그래피의 측정 대상

| 물리량 | 물리적 의미 | 분해능 |
|----------|-----------------|------------|
| **진폭(Amplitude)** | X선 흡수 | 5–20 nm |
| **위상(Phase)** | 전자 밀도 (굴절률) | 5–20 nm |
| **Probe** | 조명 함수 | 자체 교정 |

위상 대비(phase contrast) 민감도는 흡수 대비보다 약 1000배 뛰어나, 저원자번호(low-Z) 생물학적 및 환경 시료에 이상적입니다.

## 실험 장치

```
Coherent X-ray beam (undulator + monochromator)
    │
    ▼
Focusing optics (zone plate or KB mirrors)
    │
    ▼
Sample on piezo scanning stage
    │    ├── Step size: 50–500 nm (with ~60-80% overlap)
    │    └── Scan pattern: raster, spiral, or Fermat spiral
    │
    ▼
Pixelated area detector (in far field)
    │    ├── EIGER 500K, Lambda
    │    └── 256×256 to 512×512 pixels per pattern
    │
    ▼
Diffraction pattern per scan position
```

### APS BER 빔라인

| 빔라인 | 광원 | 분해능 | 에너지 | 특화 분야 |
|----------|--------|-----------|--------|-----------|
| **2-ID-E** | 언듈레이터(Undulator) | 10–50 nm | 5–30 keV | XRF + 타이코그래피 결합 |
| **33-ID-C** | 언듈레이터 | 5–20 nm | 6–25 keV | APS-U 주력 결맞음 이미징 |

### APS-U의 영향
APS-U는 결맞음 플럭스(coherent flux)를 약 100배 증가시켜 타이코그래피를 획기적으로 개선합니다:
- 더 높은 처리량 (더 빠른 스캔)
- 각 스캔 위치에서 더 나은 신호 대 잡음비
- 실용적인 시간 내에 타이코그래피 토모그래피(tomography) 구현 가능

## 변형 기법

| 변형 | 설명 | 차원 |
|---------|-------------|---------------|
| **2D 타이코그래피** | 표준 전방 산란 | 2D (x, y) |
| **타이코-토모그래피(Ptycho-tomography)** | 다중 회전에서의 타이코그래피 | 3D (x, y, z) |
| **Bragg 타이코그래피** | 결정면으로부터의 회절 | 3D 변형률(strain) 매핑 |
| **다중 슬라이스 타이코그래피(Multi-slice ptychography)** | 두꺼운 시료 모델링 | 확장된 초점 심도 |
| **분광-타이코그래피(Spectro-ptychography)** | 에너지 분해능 포함 | 2D + 화학적 종분화 |

## 데이터 수집 과정

1. **정렬(alignment)**: 시료 중심 맞추기, 검출기 기하 구조 설정
2. **스캔 정의**: 스캔 영역, 스텝 크기, 패턴 유형 정의
3. **데이터 취득**: 각 위치에서 회절 패턴 기록 (100–10,000개 위치)
4. **배경 수집**: 검출기 배경 및 암전류(dark current) 측정
5. **복원(reconstruction)**: 반복 위상 복원(iterative phase retrieval) 알고리즘 수행

### 일반적 파라미터

| 파라미터 | 표준 | 고속 | 타이코-토모 |
|-----------|---------|-----------|-------------|
| **스캔 위치 수** | 500–5,000 | 100–500 | 500–2,000 × 180 각도 |
| **위치당 노출 시간** | 10–100 ms | 0.5–5 ms | 10–50 ms |
| **검출기 픽셀** | 256×256 또는 512×512 | 256×256 | 256×256 |
| **중첩도(overlap)** | 60–80% | 50–70% | 60–70% |
| **스캔 영역** | 10–100 µm | 5–50 µm | 10–50 µm |
| **총 스캔 시간** | 5–60 min | 10–60 s | 1–24 hr |
| **달성 분해능** | 5–20 nm | 20–50 nm | 10–30 nm |

## 데이터 규모

| 구성 요소 | 크기 |
|-----------|------|
| 단일 회절 패턴 | 0.5–2 MB |
| 전체 2D 스캔 (2,000개 위치) | 1–4 GB |
| 타이코-토모그래피 (180개 각도) | 100 GB – 1 TB |
| 복원된 2D 이미지 | 10–100 MB |
| 복원된 3D 볼륨 | 1–50 GB |

## 복원 알고리즘

### 반복법(Iterative Methods)

| 알고리즘 | 유형 | 주요 특징 |
|-----------|------|-------------|
| **PIE** | 투영법(Projective) | 최초의 타이코그래피 알고리즘 |
| **ePIE** | Extended PIE | probe와 object를 동시에 복원 |
| **DM** | Difference Map | 더 견고한 수렴성 |
| **LSQ-ML** | 최대우도법(Maximum Likelihood) | 포아송 잡음(Poisson noise)을 최적으로 처리 |
| **rPIE** | Regularized PIE | 완화 파라미터(relaxation parameter)로 수렴성 개선 |

### 복원 파이프라인
```
Diffraction patterns + scan positions
    │
    ├─→ Preprocessing (background subtraction, hot pixel removal)
    │
    ├─→ Initial guess (probe from simulation, object = uniform)
    │
    ├─→ Iterative reconstruction (100-1000 iterations)
    │       ├── Forward: probe × object → exit wave → propagate → predicted pattern
    │       ├── Constraint: replace predicted amplitude with measured √intensity
    │       └── Update: back-propagate → update probe and object estimates
    │
    └─→ Reconstructed complex images
            ├── Amplitude image (absorption)
            └── Phase image (electron density / refractive index)
```

## APS BER 응용 분야

- **미생물학**: 나노미터 분해능에서의 비염색 세포 초미세구조
- **식물 과학**: 세포벽 나노구조, 세포 소기관 이미징
- **토양 과학**: 나노스케일에서의 광물-유기물 계면
- **환경**: 나노입자 특성화, 에어로졸 내부 구조
- **맥락 내 재료**: 생체광물화(biomineralization) 과정, 뼈 미세구조
