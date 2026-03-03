# APS GitHub 조직 -- 분석 개요

## 목적

이 문서는 Advanced Photon Source (APS) 및 관련 그룹이 GitHub에서 유지 관리하는 오픈소스 저장소를 카탈로그화하고 분류합니다. 목표는 기존 소프트웨어 현황을 파악하여 APS BER 프로젝트에서 재사용 가능한 컴포넌트, 통합 지점 및 격차를 식별하는 것입니다.

## 조사된 GitHub 조직

| 조직 | 주안점 |
|-------------|-------|
| [aps-anl](https://github.com/aps-anl) | APS 빔라인 제어 및 인프라 |
| [tomography](https://github.com/tomography) | 토모그래피 재구성 (TomoPy, TomocuPy) |
| [bluesky](https://github.com/bluesky) | 실험 오케스트레이션 프레임워크 |
| [BCDA-APS](https://github.com/BCDA-APS) | 빔라인 제어 및 데이터 수집 |
| [xraylib](https://github.com/tschoonj/xraylib) | X선 물리 데이터 (커뮤니티) |

## 분류 체계

저장소는 네 가지 카테고리로 분류됩니다:

1. **빔라인 제어** -- EPICS IOC, 모터 드라이버, 검출기 플러그인.
2. **데이터 분석** -- 재구성, 스펙트럼 피팅, 이미지 처리.
3. **시뮬레이션** -- X선 광학, 시료 모델링, 가상 빔라인.
4. **AI / ML** -- 머신러닝 모델, 학습 파이프라인, 추론 서비스.

## 주요 발견 사항

- 토모그래피 재구성은 잘 갖추어져 있음 (TomoPy, TomocuPy, ASTRA).
- XRF 분석은 비공개 소스인 MAPS 패키지에 크게 의존하고 있으며, 오픈소스 대안 (PyXRF, XRF-Maps)이 있지만 성숙도가 낮음.
- Bluesky/EPICS 도입이 APS-U 빔라인 전반에 확대되고 있지만 배포 패턴이 다양함.
- ML 도구가 분산되어 있으며, 단일 APS 전체 플랫폼이 존재하지 않음 (MLExchange가 후보임).

## 관련 문서

| 문서 | 설명 |
|----------|-------------|
| [repo_catalog.md](repo_catalog.md) | 카테고리별 전체 저장소 카탈로그 |
