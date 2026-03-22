# 이미지 출처 및 재생성 가이드

## 실제 데이터 이미지

다음 이미지는 공개된 오픈소스 저장소의 실제 실험 데이터를 사용합니다.

| 이미지 파일 | 노이즈 유형 | 데이터 출처 | 라이선스 |
|-----------|-----------|------------|---------|
| `ring_artifact_before_after.png` | 링 아티팩트 | [Sarepy](https://github.com/nghia-vo/sarepy) — Vo et al., 실제 중성자 CT 데이터 | BSD-3 |
| `low_dose_noise_before_after.png` | 저선량 포아송 노이즈 | [TomoGAN](https://github.com/lzhengchun/TomoGAN) — Liu et al. 2020, 실제 APS 싱크로트론 데이터 | BSD-2 |

## 합성 예시 이미지

다음 이미지는 합성 데이터(Shepp-Logan 팬텀 및 시뮬레이션된 원소 맵)를 사용하여 프로그래밍 방식으로 생성됩니다.

| 이미지 파일 | 노이즈 유형 | 생성 방법 | 라이선스 |
|-----------|-----------|----------|---------|
| `zinger_before_after.png` | 징거 | Shepp-Logan 팬텀, 사이노그램에 랜덤 징거 → 미디언 필터 | MIT (이 저장소) |
| `rotation_center_error_before_after.png` | 회전 중심 오류 | Shepp-Logan 팬텀, ±5 px 중심 오프셋 → 올바른 중심 | MIT (이 저장소) |
| `flatfield_before_after.png` | 플랫필드 비균일성 | Shepp-Logan 팬텀, 빔 프로파일 비균일성 → 정규화 | MIT (이 저장소) |
| `sparse_angle_before_after.png` | 희소 각도 아티팩트 | Sarepy 중성자 CT 데이터 — 희소 투영 FBP vs. 전체 각도 | BSD-3 |
| `dead_hot_pixel_before_after.png` | 데드/핫 픽셀 (XRF) | 합성 원소 맵 → 이상치 주입 → 미디언 필터 | MIT (이 저장소) |
| `i0_drop_before_after.png` | I0 저하 | I0 빔 저하가 있는 합성 XRF 맵 → 정규화 | MIT (이 저장소) |

## 외부 이미지 참고자료

다음 외부 소스가 노이즈 카탈로그 문서에서 실제 데이터 예시로 참조됩니다.

| 출처 | URL | 라이선스 | 참조 위치 |
|------|-----|---------|----------|
| Sarepy 문서 | https://sarepy.readthedocs.io/toc/section3.html | BSD-3 | `tomography/ring_artifact.md` |
| TomoGAN GitHub | https://github.com/lzhengchun/TomoGAN | BSD-2 | `tomography/low_dose_noise.md` |
| TomoPy 문서 | https://tomopy.readthedocs.io/ | BSD-3 | `tomography/rotation_center_error.md` |

## 이미지 추가 기여

이 카탈로그에 예시 이미지를 추가하려면:

1. **합성 이미지**: `generate_examples.py`에 생성 코드를 추가하고 재실행
2. **실제 데이터 이미지**: 허용적 라이선스(CC BY, BSD, MIT, 퍼블릭 도메인) 소스의 이미지 확인
3. **출처 표기**: 위 표에 소스 URL 및 라이선스 항목 추가
4. **형식**: PNG, 300 DPI, 흰색 배경, 전후 비교 나란히 배치 권장
5. **명명**: 비교 이미지는 `{노이즈_유형}_before_after.png`

이미지와 업데이트된 출처 표기 표와 함께 PR을 제출하세요.
