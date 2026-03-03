# 변경 이력

이 프로젝트의 주요 변경 사항을 이 파일에 기록합니다.

## [1.0.0] - 2026-02-27

### 추가

#### 1단계: 저장소 구조 구축
- 8개 주요 섹션을 위한 디렉토리 구조
- 네비게이션 가이드가 포함된 루트 README
- MIT 라이선스

#### 2단계: 프로그램 개요 (01_program_overview/)
- BER 프로그램 미션, 연혁, 연구 분야
- APS 시설 사양 및 APS-U 업그레이드 세부사항
- 기법별로 구성된 15개 빔라인 프로파일
- 파트너 시설 설명 (EMSL, JGI, NEON, HFIR, ALCF, CNM)
- X선 기법 연결이 포함된 7개 연구 분야 매핑

#### 3단계: X선 모달리티 (02_xray_modalities/)
- 6개 모달리티 디렉토리: 결정학, 토모그래피, XRF 현미경, 분광학, 타이코그래피, 산란
- 각 모달리티의 HDF5 스키마 세부사항이 포함된 데이터 형식 사양
- 모달리티별 AI/ML 방법 요약
- 총 21개 문서 파일

#### 4단계: AI/ML 방법 분류체계 (03_ai_ml_methods/)
- 이미지 분할: U-Net 변형, XRF 세포 분할, 토모그래피 3D 분할
- 노이즈 제거: TomoGAN, Noise2Noise, 딥 잔차 XRF 향상
- 재구성: TomocuPy GPU 가속, PtychoNet CNN 위상 복원, 동적 데이터용 INR
- 자율 실험: ROI-Finder, 베이지안 최적화, AI-NERD
- 다중모달 통합: XRF+타이코그래피, CT+XAS 상관관계, 광학-X선 정합

#### 5단계: 출판물 아카이브 (04_publications/)
- 논문 리뷰 템플릿
- BER 프로그램 출판물 개요
- ROI-Finder, TomoGAN, XRF GMM, AI-NERD, PtychoNet, AI@Edge 타이코그래피, 딥 잔차 XRF, 풀스택 DL 토모, 실시간 µCT HPC, AI@ALS 워크숍을 다루는 10개의 상세 논문 리뷰

#### 6단계: 도구 및 코드 리버스 엔지니어링 (05_tools_and_code/)
- ROI-Finder: 리버스 엔지니어링, 장단점, 재현 가이드, 4개 Jupyter 노트북
- TomocuPy: 아키텍처 분석, GPU 커널 세부사항, TomoPy 대비 벤치마크
- TomoPy: 모듈 구조, 재구성 알고리즘
- MAPS 소프트웨어: 워크플로우 분석
- MLExchange: 마이크로서비스 아키텍처, 장단점
- APS GitHub 저장소: 주요 저장소 카탈로그
- Bluesky/EPICS: 아키텍처 개요, RunEngine, ophyd, 문서 모델

#### 7단계: 데이터 구조 및 EDA (06_data_structures/)
- HDF5 스키마: XRF (MAPS 형식), 토모그래피 (Data Exchange), 타이코그래피 (CXI)
- HDF5 탐색 및 시각화 노트북
- 데이터 규모 분석: APS-U 전후 예측
- EDA 가이드: XRF, 토모그래피, 분광학 (코드 예제 포함)
- 3개 EDA Jupyter 노트북
- TomoBank, CXIDB, PDB 링크가 포함된 샘플 데이터 디렉토리

#### 8단계: 데이터 파이프라인 아키텍처 (07_data_pipeline/)
- 수집 레이어: 검출기 사양, EPICS IOC 통합
- 스트리밍: ZMQ, PV Access, Globus 전송
- 처리: 전처리 → 재구성 → 노이즈 제거 → 분할
- 분석: ML 추론, 시각화 (Jupyter, Streamlit, Napari)
- 저장: 3계층 아키텍처 (GPFS/Petrel/HPSS), NeXus 준수
- 아키텍처 다이어그램 (5개 Mermaid 플로우차트)

#### 9단계: 참고자료 및 유틸리티 (08_references/)
- 20개 이상의 항목이 포함된 BibTeX 참고문헌
- 싱크로트론 과학 용어 사전 (A-Z)
- 유용한 링크: APS BER 프로그램, 파트너 시설, 도구, 데이터셋, 튜토리얼
