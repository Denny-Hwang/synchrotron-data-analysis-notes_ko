# X선 흡수 분광법(XAS / XANES / EXAFS)

## 원리

**X선 흡수 분광법(X-ray Absorption Spectroscopy, XAS)**은 광자 에너지(photon energy)가 특정 원소의 흡수 모서리(absorption edge) 부근에서 변할 때 X선 흡수가 어떻게 달라지는지를 측정하여, 해당 원소의 국소 원자 환경과 화학적 상태를 조사하는 기법입니다.

### 물리적 기초
1. X선 에너지가 내각 전자 결합 에너지와 일치할 때 → **흡수 모서리(absorption edge)**
2. 방출된 광전자파(photoelectron wave)가 인접 원자에 의해 산란됨
3. 방출파와 후방 산란파 사이의 간섭이 흡수를 변조함
4. 결과적인 진동(oscillation)에 다음 정보가 부호화됨:
   - **산화 상태(oxidation state)** (모서리 위치)
   - **배위 기하 구조(coordination geometry)** (근접 모서리 미세 구조)
   - **결합 거리(bond distances)** (확장 진동)
   - **배위수(coordination numbers)** (진동 진폭)

### XAS 영역

```
                 ┌── XANES ──┐┌──── EXAFS ────────────────┐
                 │            ││                            │
Absorption │    ╱╲          │╱╲ ╱╲ ╱╲                      │
           │   ╱  ╲         ╱  ╲╱  ╲╱  ╲ ...              │
           │  ╱    ╲───────╱                               │
           │ ╱                                             │
           │╱                                              │
           └──────────────────────────────────────────────→
                     Energy (eV) →
              Edge    -50 to +50 eV    +50 to +1000 eV
```

| 영역 | 에너지 범위 | 정보 | 민감도 |
|--------|-------------|-------------|-------------|
| **Pre-edge** | -20 ~ 0 eV | 전자 전이, 대칭성 | 산화 상태 |
| **XANES** | -10 ~ +50 eV | 산화 상태, 배위 기하 구조 | 화학종 |
| **EXAFS** | +50 ~ +1000 eV | 결합 거리, 배위수 | 국소 구조 |

### 변형 기법

| 변형 | 설명 | 공간 분해능 |
|---------|-------------|-------------------|
| **벌크 XAS(Bulk XAS)** | 투과/형광, mm 빔 | 벌크 평균 |
| **µ-XANES** | 집속 빔, 공간 매핑 | 1–20 µm |
| **µ-EXAFS** | 집속 빔, 전체 EXAFS | 1–20 µm |
| **XANES 이미징** | 각 픽셀에서의 에너지 스택 | 1–20 µm |
| **RIXS** | 공명 비탄성 X선 산란(Resonant inelastic X-ray scattering) | 1–20 µm |

## 실험 장치

```
Monochromatic X-ray beam (tunable energy)
    │
    ├─→ I₀ (incident flux monitor, ion chamber)
    │
    ▼
Sample
    │
    ├─→ I₁ (transmitted flux, ion chamber) → Transmission mode
    │
    └─→ Fluorescence detector (SDD/Vortex) → Fluorescence mode
            (for dilute samples, preferred for environmental)
```

### APS BER 빔라인

| 빔라인 | 에너지 범위 | 모드 | 특화 분야 |
|----------|-------------|------|-----------|
| **9-BM** | 2.1–23 keV | 투과, 형광 | 저에너지 X선(tender X-ray) (P, S, Cl, K, Ca 모서리) |
| **20-BM** | 2.7–32 keV | 투과, 형광 | 중금속 (As, Pb, Hg, U 등) |
| **25-ID** | 5–28 keV | RIXS, µ-XANES | 고분해능, 마이크로빔 |

## 데이터 수집 과정

1. **에너지 교정(energy calibration)**: 원소 모서리에서 알려진 참조 화합물 측정
2. **Pre-edge 스캔**: 모서리 아래에서 조대한 에너지 간격으로 스캔 (배경)
3. **모서리 스캔(edge scan)**: 모서리 영역을 미세한 에너지 간격으로 스캔 (XANES)
4. **Post-edge 스캔**: k-공간에서 점진적으로 넓어지는 간격 (EXAFS)
5. **다중 스캔**: 신호 대 잡음비 향상을 위해 3–20회 스캔 평균

### 일반적 파라미터 (벌크 XAS)

| 파라미터 | XANES 전용 | 전체 EXAFS |
|-----------|-----------|------------|
| **에너지 범위** | 모서리 ± 100 eV | 모서리 - 200 ~ + 1000 eV |
| **에너지 간격** | 0.25–0.5 eV (모서리), 5 eV (pre/post) | + 0.05 Å⁻¹ (k-공간) |
| **측정점 수** | 200–500 | 500–1000 |
| **측정점당 시간** | 1–5 s | 1–10 s |
| **총 스캔 횟수** | 3–5 | 5–20 |
| **총 소요 시간** | 30–60 min | 1–6 hr |

## 데이터 규모

| 구성 요소 | 일반적 크기 |
|-----------|-------------|
| 단일 XAS 스펙트럼 | 10–100 KB |
| 평균 스펙트럼 + 메타데이터 | 1 MB |
| µ-XANES 이미징 스택 | 0.5–10 GB |
| 전체 실험 데이터셋 | 0.1–10 GB |

## APS BER 응용 분야

- **토양 과학**: Fe/Mn 산화 환원 종분화, P 결합 환경, S 화학종 식별
- **환경 화학**: As(III)/As(V) 종분화, Cr(III)/Cr(VI), 폐기물 내 U 종분화
- **식물 과학**: 금속 내성 기작, 뿌리혹(root nodule) 내 영양소 종분화
- **지구화학**: 광물상 식별, 원소 산화 상태 매핑
- **미생물학**: 박테리아의 금속 흡수 및 저장 기작
