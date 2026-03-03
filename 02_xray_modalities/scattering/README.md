# X선 산란 (SAXS / WAXS / XPCS)

## 원리

**X선 산란(X-ray scattering)** 기법은 시료에 의해 산란된 X선의 각도 분포를 분석하여 재료의 구조와 동역학을 탐구합니다. 장거리 질서(long-range order)가 필요한 결정학(crystallography)과 달리, 산란 방법은 무질서, 부분 질서 및 비정질(amorphous) 시스템에서도 작동합니다.

### 물리적 기초
- X선은 시료 내 전자 밀도 요동(electron density fluctuation)에 의해 산란됨
- 산란 각도는 구조적 길이 스케일과 관련: d = 2π/q
- 산란 벡터(scattering vector): q = (4π/λ)sin(θ), 여기서 2θ는 산란 각도
- 소각(small angle) → 대형 구조 (nm–µm); 광각(wide angle) → 원자/분자 스케일 (Å–nm)

### 기법 변형

| 기법 | q 범위 (Å⁻¹) | 길이 스케일 | 탐구 대상 |
|-----------|---------------|-------------|----------------|
| **USAXS** | 10⁻⁴ – 0.1 | 0.06–60 µm | 대규모 비균질성, 공극, 입자 |
| **SAXS** | 0.001 – 0.5 | 1–600 nm | 나노구조, 단백질 형태, 응집 |
| **WAXS** | 0.5 – 10 | 0.06–1 nm | 결정 구조, 분자 패킹 |
| **XPCS** | 0.001 – 0.1 | 6–600 nm | 동역학 (확산, 완화, 에이징) |

### SAXS vs. WAXS

```
                     SAXS              WAXS
                  (small angle)    (wide angle)
                       ↓                ↓
X-ray beam → ┌────────┬────────────────────┐
              │ Sample │→ 2θ < 5°   │ 2θ > 5°  │
              └────────┘    ↓        │    ↓      │
                       2D pattern   │ 2D pattern │
                       (ring-like)  │ (Debye rings)
                            ↓        │     ↓      │
                       I(q) profile │ I(q) profile │
                       Nanostructure│ Atomic/molecular
```

## XPCS: X선 광자 상관 분광법(X-ray Photon Correlation Spectroscopy)

XPCS는 동적 광산란(Dynamic Light Scattering, DLS)의 X선 대응 기법입니다:

### 원리
- 결맞음 X선 빔이 **스페클 패턴(speckle pattern)** (개별 산란체로부터의 간섭)을 생성
- 산란체가 움직이면 스페클 패턴이 요동
- 스페클 강도의 **시간 자기상관(temporal autocorrelation)** → 동역학 정보

```
g₂(q, τ) = <I(q,t) × I(q,t+τ)> / <I(q,t)>²

g₂ = 1 + β|f(q,τ)|²

where f(q,τ) = intermediate scattering function
      β = speckle contrast (coherence factor)
      τ = time delay
```

### XPCS에 대한 APS-U의 영향
- 결맞음 플럭스가 약 100배 증가 → XPCS가 획기적으로 강력해짐
- 더 빠른 동역학에 접근 가능 (마이크로초 영역)
- 더 작은 구조적 특징을 위한 더 높은 q-분해능
- 다중 스페클 XPCS (단일 점 대신 2D 상관) 구현 가능

## 실험 장치

### SAXS/WAXS 장치 (12-ID-B)

```
Monochromatic X-ray beam
    │
    ▼
Sample (capillary, flow cell, or thin film)
    │
    ├──→ WAXS detector (close, ~200 mm) → wide-angle pattern
    │
    └──→ SAXS detector (far, 2–10 m) → small-angle pattern
              │
              └── Beamstop (absorbs direct beam)
```

### XPCS 장치 (12-ID-E)

```
Coherent X-ray beam (small source, high brightness)
    │
    ▼
Collimation (define coherence volume)
    │
    ▼
Sample
    │
    └──→ Fast area detector (EIGER 500K, 10 kHz+)
              │
              └── Records speckle patterns as function of time
```

### APS BER 빔라인

| 빔라인 | 기법 | 에너지 | 검출기 | 특화 분야 |
|----------|-----------|--------|----------|-----------|
| **12-ID-B** | SAXS/WAXS, GISAXS | 7.9–14 keV | PILATUS 2M/300K | 용액 산란, 박막 |
| **12-ID-E** | USAXS/SAXS/WAXS | 10–28 keV | Bonse-Hart + 면적검출기 | 위계적 구조(hierarchical structures) |
| **12-BM** | XAS, SAXS/WAXS | 4.5–40 keV | 복수 | 분광법 + 산란 결합 |

## 데이터 수집

### SAXS/WAXS
1. **교정(calibration)**: q-교정을 위한 표준 시료(AgBeh, glassy carbon) 측정
2. **배경(background)**: 빈 캐필러리 / 용매 측정
3. **시료 측정**: 농도에 따라 0.1 s – 60 s 노출
4. **농도 시리즈**: 단백질 SAXS를 위한 다중 농도
5. **온도/시간 시리즈**: 반응 속도론 또는 상거동(phase behavior) 연구

### XPCS
1. **정렬**: 결맞음 및 스페클 대비 최적화
2. **시계열(time series)**: 고속 프레임 레이트(100–10,000 Hz)로 연속 취득
3. **다중 q값**: 검출기가 여러 q에서의 동역학을 동시에 포착
4. **온도/전기장 스캔**: 외부 파라미터의 함수로 동역학 탐구

### 일반적 파라미터

| 파라미터 | SAXS (12-ID-B) | XPCS (12-ID-E, APS-U 이후) |
|-----------|----------------|---------------------------|
| **에너지** | 12 keV | 8–12 keV |
| **빔 크기** | 120×80 µm | 1–20 µm |
| **노출** | 0.1–60 s | 0.1–10 ms/프레임 |
| **프레임 수** | 10–100 | 10,000–1,000,000 |
| **q 범위** | 0.002–10 Å⁻¹ | 0.001–0.1 Å⁻¹ |
| **시료-검출기 거리** | 0.2–10 m | 2–10 m |

## 데이터 규모

| 구성 요소 | 크기 |
|-----------|------|
| 단일 SAXS 프레임 (2M 검출기) | ~4 MB |
| SAXS 데이터셋 (100 프레임) | ~400 MB |
| XPCS 시계열 (100K 프레임) | 10–100 GB |
| 처리된 1D 프로파일 | 각 ~100 KB |
| 상관 함수(correlation functions) | ~1 MB |

## APS BER 응용 분야

- **구조생물학**: 단백질 용액 구조 및 구조적 상태 (SAXS)
- **토양 과학**: 토양 응집체 나노구조 (USAXS/SAXS)
- **환경**: 현탁액 내 나노입자 크기 분포 및 안정성 (SAXS)
- **지구화학**: 광물 핵생성 및 성장 반응 속도론 (SAXS 시분해)
- **미생물학**: 생물막(biofilm) 초미세구조, 세균 막 조직
- **재료 동역학**: 콜로이드 겔 에이징, 나노입자 확산 (XPCS)
