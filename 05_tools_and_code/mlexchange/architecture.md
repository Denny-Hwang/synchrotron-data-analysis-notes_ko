# MLExchange -- 마이크로서비스 아키텍처

## 상위 수준 아키텍처

```
Browser (React GUI)
  |
  v
API Gateway (FastAPI)
  |
  +---> Auth Service (user management, tokens)
  +---> Data Service (upload, storage, metadata)
  +---> Model Service (model zoo registry)
  +---> Training Service (job submission, monitoring)
  +---> Inference Service (batch / streaming prediction)
  +---> Compute Service (resource allocation)
  |
  v
Compute Back-ends
  +---> Local GPU (Docker containers)
  +---> NERSC / HPC (Slurm via job proxy)
  +---> Kubernetes cluster
```

## 마이크로서비스 설명

### API Gateway

- 모든 클라이언트 요청에 대한 단일 진입점.
- URL 접두사에 따라 다운스트림 서비스로 라우팅.
- CORS, 속도 제한 및 요청 로깅 처리.

### Data Service

- 데이터셋의 업로드, 저장 및 검색을 관리합니다.
- 공유 파일시스템 또는 오브젝트 스토어 (MinIO / S3)에 데이터를 저장합니다.
- MongoDB 컬렉션에서 데이터셋 메타데이터 (형상, dtype, 출처)를 추적합니다.

### Model Service

- 사용 가능한 ML 모델의 레지스트리 ("모델 저장소")를 유지 관리합니다.
- 각 모델 항목에는 아키텍처 클래스, 기본 하이퍼파라미터, 예상 입출력 형상 및 Docker 이미지 참조가 포함됩니다.
- 모델은 버전 관리되며 공개 또는 비공개로 유지할 수 있습니다.

### Training Service

- 학습 작업 요청 (데이터셋 ID, 모델 ID, 하이퍼파라미터)을 수락합니다.
- Compute Service에 작업을 제출하고 상태를 폴링합니다.
- 학습 로그, 메트릭 (손실 곡선) 및 모델 체크포인트를 저장합니다.

### Inference Service

- 학습된 모델 체크포인트를 로드하고 새 데이터에 대해 예측을 실행합니다.
- 배치 모드 (전체 데이터셋) 및 스트리밍 모드 (메시지 큐를 통한 이미지별)를 지원합니다.

### Compute Service

- 통일된 작업 제출 API 뒤에 컴퓨팅 백엔드를 추상화합니다.
- 로컬 GPU: GPU 패스스루가 가능한 Docker 컨테이너를 실행합니다.
- HPC: Slurm 작업 스크립트를 생성하고 SSH 또는 REST 프록시를 통해 제출합니다.
- Kubernetes: K8s API를 통해 Job 또는 Deployment 리소스를 생성합니다.

## DLSIA 통합

DLSIA (Deep Learning for Scientific Image Analysis)는 MLExchange에서 사용하는 기본 모델 라이브러리입니다. 다음을 제공합니다:

- **TUNet** -- 구성 가능한 깊이, 너비 및 스킵 연결을 가진 조절 가능한 U-Net.
- **TUNet3+** -- 다중 스케일 특징 융합을 위한 밀집 스킵 변형.
- **SimCLR encoder** -- 다운스트림 작업을 위한 자기 지도 사전 학습.

모델은 PyTorch에서 정의되며 MLExchange의 Training 및 Inference 서비스가 통일된 `fit()` / `predict()` 인터페이스를 통해 호출하는 표준 `DLSIAModel` 클래스로 래핑됩니다.

## 메시지 큐

- RabbitMQ (또는 Redis Streams)가 비동기 이벤트 처리를 위해 서비스를 연결합니다.
- 학습 완료 이벤트가 검증 세트에 대한 자동 추론을 트리거합니다.
- 결과는 GUI에서 시각화하기 위해 Data Service로 다시 전달됩니다.

## 배포

- 각 마이크로서비스는 Docker 이미지로 패키징됩니다.
- 로컬 개발을 위한 Docker Compose; Kubernetes 프로덕션 배포를 위한 Helm 차트.
- 환경 변수 및 공유 `config.yaml`을 통한 구성.
