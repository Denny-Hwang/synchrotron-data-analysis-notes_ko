# 데이터 저장 및 관리

## 개요

저장 단계는 Globus를 통한 데이터 전송 및 복제, 테이프의 장기 보관,
Petrel의 활성 저장, NeXus/HDF5를 통한 메타데이터 표준화, 데이터 공유 메커니즘,
DOI 할당을 포함합니다.

## 저장 계층

| 계층 | 시스템 | 용량 | 접근 지연 | 보존 기간 |
|------|--------|------|----------|----------|
| 핫 | Eagle (GPFS) | 100 TB 할당 | 밀리초 | 90일 |
| 웜 | Petrel (Object Store) | 500 TB 할당 | 초 | 3년 |
| 콜드 | HPSS 테이프 아카이브 | 무제한 | 분~시간 | 10년 이상 |

데이터는 경과 시간과 접근 빈도에 따라 계층 간 자동으로 마이그레이션됩니다.

## Globus 데이터 관리

Globus는 빔라인 저장소, ALCF 파일시스템, Petrel, 협력자 엔드포인트 간
전송을 위한 통합 데이터 관리 레이어 역할을 합니다.

| 엔드포인트 | 위치 | 파일시스템 |
|-----------|------|-----------|
| `aps#data` | APS | GPFS |
| `alcf#eagle` | ALCF | Eagle / GPFS |
| `anl#petrel` | Argonne | Object Store |
| `nersc#dtn` | NERSC | CFS / HPSS |

### 자동화된 전송 정책

```yaml
globus_flows:
  post_processing:
    trigger: "processing_complete"
    steps:
      - transfer:
          source: "alcf#eagle:/eBERlight/processed/${SCAN_ID}"
          destination: "anl#petrel:/eBERlight/archive/${SCAN_ID}"
          verify_checksum: true
      - transfer:
          source: "alcf#eagle:/eBERlight/processed/${SCAN_ID}"
          destination: "hpss#tape:/eBERlight/archive/${YEAR}/${SCAN_ID}"
          verify_checksum: true
      - notify:
          email: "${PI_EMAIL}"
          message: "Dataset ${SCAN_ID} archived successfully"
```

## 테이프 아카이브 (HPSS)

테이프 아카이브는 `/eBERlight/archive/` 아래에 연도/스캔 계층 구조를 따릅니다.
각 스캔 디렉토리에는 `raw/`, `processed/`, `metadata/`, `analysis/`
하위 디렉토리가 포함됩니다.

| 데이터 분류 | 보존 기간 | 복사본 수 | 근거 |
|------------|----------|----------|------|
| 원시 검출기 데이터 | 10년 | 2 (테이프 + Petrel) | DOE 데이터 관리 의무 |
| 처리된 볼륨 | 5년 | 1 (테이프) | 원시 데이터에서 재현 가능 |
| 분석 결과 | 5년 | 1 (Petrel) | 처리 데이터에서 재현 가능 |
| 출판 데이터셋 | 영구 | 2 (테이프 + DOI 저장소) | 출판물과 연결 |

## Petrel Object Store

Petrel은 데이터셋 탐색을 위한 웹 포털, 접근 제어를 위한 Globus Auth,
Globus SDK를 통한 REST API, 메타데이터 기반 데이터셋 검색을 위한
검색 인덱스를 제공합니다.

```python
from globus_sdk import TransferClient, AccessTokenAuthorizer

tc = TransferClient(authorizer=AccessTokenAuthorizer(token))
rule = {
    "DATA_TYPE": "access",
    "principal_type": "identity",
    "principal": "collaborator@university.edu",
    "path": "/eBERlight/archive/scan_0042/",
    "permissions": "r"
}
tc.add_endpoint_acl_rule(petrel_endpoint_id, rule)
```

## 메타데이터 표준 (NeXus)

모든 데이터셋은 HDF5 마스터 파일에서 NeXus 애플리케이션 정의를 준수합니다:

| 기법 | 정의 | 주요 그룹 |
|------|------|----------|
| 단층촬영 | NXtomo | NXsample, NXdetector, NXsource |
| SAXS/WAXS | NXsas | NXcollimator, NXdetector, NXsample |
| XAS/XANES | NXxas | NXmonochromator, NXdetector |
| XRF 매핑 | NXfluo | NXdetector, NXsample |

```
/entry (NXentry)
    /instrument (NXinstrument)
        /source: energy=7.0 GeV, current=100.0 mA
        /detector: description="EIGER2 X 4M", exposure_time=0.001 s
    /sample (NXsample): name, temperature
    /data (NXdata): @signal="data"
    /process (NXprocess): program, version, parameters
```

파일은 수집 시 `cnxvalidate`로 검증됩니다. 실패한 파일은 격리됩니다.

## 데이터 공유

| 방법 | 대상 | 접근 제어 |
|------|------|----------|
| Globus 공유 엔드포인트 | 지정 협력자 | ID 기반 ACL |
| Petrel 웹 포털 | 광범위한 커뮤니티 | Globus Auth 그룹 |
| Materials Data Facility | 공개 데이터셋 | 엠바고 후 오픈 액세스 |
| Zenodo / Figshare | 출판 보충자료 | DOI 연결 오픈 액세스 |

데이터셋은 수집일로부터 (또는 출판 시까지) **12개월** 동안 엠바고된 후,
CC-BY 4.0 라이선스 하에 오픈 액세스로 전환됩니다.

## DOI 할당

1. PI가 APS BER 데이터 포털을 통해 DOI를 요청합니다.
2. 메타데이터가 DataCite 스키마에 대해 검증됩니다.
3. Argonne의 DataCite 회원 자격을 통해 DOI가 발급됩니다.
4. Petrel에 다운로드 링크가 포함된 랜딩 페이지가 생성됩니다.
5. DOI가 등록되고 데이터셋에 연결됩니다.

```json
{
  "doi": "10.18126/eBERlight.scan_0042",
  "creators": [{"name": "Smith, J.", "affiliation": "Argonne"}],
  "title": "In-situ tomography of NMC811 cathode cycling",
  "publisher": "Argonne National Laboratory",
  "publicationYear": 2025,
  "resourceType": "Dataset",
  "rights": "CC-BY 4.0"
}
```

DOI 랜딩 페이지는 보고를 위해 다운로드 횟수와 인용 지표를 추적합니다.

## 관련 문서

- [acquisition.md](acquisition.md) -- 데이터 원본 및 검출기 메타데이터
- [processing.md](processing.md) -- 변환 출처
- [analysis.md](analysis.md) -- 데이터와 함께 저장되는 검증 및 QA 기록
