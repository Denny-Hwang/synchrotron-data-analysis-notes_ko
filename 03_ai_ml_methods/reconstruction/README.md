# 재구성 방법(Reconstruction Methods)

## 개요

재구성(reconstruction)은 간접 측정으로부터 이미지 또는 볼륨을 복원하는 계산 과정입니다.
방사광 과학에서 이는 토모그래피 재구성(프로젝션 → 3D 볼륨)과 위상 복원(phase retrieval,
회절 패턴 → 복소 이미지)을 포함합니다.

## 방법 현황

```
재구성 방법
├── 고전적 해석적 방법(Classical Analytical)
│   ├── FBP (필터 역투영, Filtered Back Projection)
│   └── Gridrec (FFT 기반 FBP)
│
├── 고전적 반복적 방법(Classical Iterative)
│   ├── SIRT, MLEM, CGLS
│   └── 모델 기반(MBIR, Model-Based)
│
├── GPU 가속 고전적 방법
│   └── TomocuPy (20-30배 속도 향상)
│
├── DL 후처리(Post-Processing)
│   └── FBPConvNet (FBP → CNN 정리)
│
├── 학습된 반복적 방법(Learned Iterative)
│   └── 학습된 구성요소를 포함한 언롤드 최적화(unrolled optimization)
│
├── 신경 표현(Neural Representations)
│   └── INR (연속 좌표 → 값 매핑)
│
├── 생성 모델 기반(Generative Model-Based)
│   └── 확산 모델(Diffusion Models, DDPM/SDE) — 희소·제한 각도 CT
│
└── 물리 정보 기반(Physics-Informed)
    └── PINNs / FNO — PDE 제약을 학습 손실에 결합
```

## 디렉토리 내용

| 파일 | 내용 |
|------|---------|
| [tomocupy.md](tomocupy.md) | GPU 가속 재구성 (CuPy 기반) |
| [ptychonet.md](ptychonet.md) | CNN 기반 ptychography 위상 복원 |
| [inr_dynamic.md](inr_dynamic.md) | 동적 토모그래피를 위한 암시적 신경 표현(Implicit Neural Representations) |
| [diffusion_ct.md](diffusion_ct.md) | 희소/제한 각도 CT를 위한 확산 모델 |
| [pinns_xray.md](pinns_xray.md) | X선 재구성을 위한 물리 정보 기반 신경망(PINN/FNO) |
