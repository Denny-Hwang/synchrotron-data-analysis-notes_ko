# APS GitHub 저장소 카탈로그

저장소는 카테고리별로 분류되어 있습니다. 각 항목에는 저장소 이름, 조직, 언어 및 간단한 설명이 포함됩니다.

---

## 1. 빔라인 제어

| 저장소 | 조직 | 언어 | 설명 |
|-----------|-----|----------|-------------|
| epics-base | epics-base | C | EPICS 코어 런타임, Channel Access, pvAccess |
| ADCore | areaDetector | C++ | EPICS areaDetector 코어 프레임워크 |
| ADSimDetector | areaDetector | C++ | 테스트용 시뮬레이션 검출기 |
| ADPilatus | areaDetector | C++ | Dectris Pilatus 검출기 드라이버 |
| ADEiger | areaDetector | C++ | Dectris Eiger 검출기 드라이버 |
| motor | epics-modules | C | EPICS 모터 레코드 및 장치 지원 |
| ioc-deploy-tools | BCDA-APS | Python | IOC 배포 및 버전 관리 |
| aps-dm | aps-anl | Python | APS 데이터 관리 시스템 CLI/API |

## 2. 데이터 분석

| 저장소 | 조직 | 언어 | 설명 |
|-----------|-----|----------|-------------|
| tomopy | tomography | Python/C | 토모그래피 재구성 라이브러리 |
| tomocupy | tomography | Python/CUDA | GPU 가속 토모그래피 재구성 |
| dxchange | tomography | Python | Data Exchange HDF5 I/O 유틸리티 |
| dxfile | tomography | Python | Data Exchange 파일 사양 |
| tomobank | tomography | Python | 토모그래피 테스트 데이터셋 저장소 |
| xrf-maps | aps-anl | C++ | 오픈소스 XRF 맵 피팅 (MAPS 대안) |
| PyXRF | NSLS-II | Python | Python XRF 피팅 및 시각화 |
| larch | xraypy | Python | XAFS/XRF 분석 (Larch) |
| xraylarch | xraypy | Python | X선 분광 분석 도구 |

## 3. 시뮬레이션

| 저장소 | 조직 | 언어 | 설명 |
|-----------|-----|----------|-------------|
| shadow3 | oasys-kit | Fortran/C | X선 광학용 광선 추적 |
| SRW | ochubar | C++/Python | Synchrotron Radiation Workshop (파동 광학) |
| OASYS1 | oasys-kit | Python | Shadow3 및 SRW를 통합하는 GUI |
| xoppy | oasys-kit | Python | X선 광학 유틸리티 (언듈레이터 스펙트럼 등) |
| aps-undulator | aps-anl | Python | APS 언듈레이터 자기장 및 스펙트럼 계산 |

## 4. AI / ML

| 저장소 | 조직 | 언어 | 설명 |
|-----------|-----|----------|-------------|
| mlexchange | mlexchange | Python | ML 플랫폼 (mlexchange/ 문서 참조) |
| DLSIA | mlexchange | Python | 과학 이미지 분석을 위한 딥러닝 |
| tike | tomography | Python | ML 사전 정보를 활용한 타이코그래피 및 토모그래피 |
| pvauto | aps-anl | Python | EPICS PV에서 ML을 사용한 자동 정렬 |
| ai-science-training | argonne-lcf | Python | Argonne AI/ML 교육 자료 |

## 5. 워크플로우 및 오케스트레이션

| 저장소 | 조직 | 언어 | 설명 |
|-----------|-----|----------|-------------|
| bluesky | bluesky | Python | 실험 오케스트레이션 RunEngine |
| ophyd | bluesky | Python | Bluesky를 위한 하드웨어 추상화 |
| databroker | bluesky | Python | Bluesky 문서의 데이터 접근 및 검색 |
| bluesky-queueserver | bluesky | Python | 원격 실험 대기열 서버 |
| tiled | bluesky | Python | 데이터 접근 서비스 (REST + Python 클라이언트) |
| happi | pcdshds | Python | 장치 구성을 위한 하드웨어 데이터베이스 |

---

## 참고 사항

- 나열된 저장소는 BER 프로그램 범위 (XRF, 토모그래피, ML, 빔라인 제어)와 가장 관련성이 높은 것들입니다.
- 일부 저장소는 여러 카테고리에 걸쳐 있습니다 (예: `tike`는 데이터 분석과 AI를 연결함).
- 패키지를 도입하기 전에 저장소의 활동 상태 및 유지 관리 현황을 확인해야 합니다.
