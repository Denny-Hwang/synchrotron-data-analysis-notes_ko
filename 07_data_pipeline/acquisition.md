# 데이터 수집

## 개요

데이터 수집(data acquisition)은 APS 데이터 파이프라인의 첫 번째 단계입니다. 이 단계는
X선 광자(photon)를 디지털 신호로 변환하는 물리적 검출기(detector), 하드웨어를 조율하는
EPICS IOC 계층, 그리고 원시 프레임을 메타데이터와 함께 패키징하여 다운스트림에서
사용할 수 있도록 하는 Area Detector 프레임워크를 포함합니다.

## 검출기 유형

### EIGER (Dectris)

- **기술**: 하이브리드 광자 계수(Hybrid photon-counting, HPC) 실리콘 센서
- **픽셀 배열**: 4M 픽셀 (EIGER2 X 4M) -- 2070 x 2167 픽셀
- **프레임 속도**: 최대 750 Hz (4M), 2.3 kHz (1M)
- **비트 심도(Bit depth)**: 픽셀당 8, 16, 또는 32 비트
- **인터페이스**: 10 GbE / 100 GbE 직접 연결
- **용도**: SAXS/WAXS, 타이코그래피(ptychography), 직렬 결정학(serial crystallography)
- **출력 형식**: bitshuffle-LZ4 압축 적용 HDF5

### Jungfrau (PSI)

- **기술**: 전하 적분 하이브리드 픽셀 검출기(Charge-integrating hybrid pixel detector)
- **픽셀 배열**: 모듈형 -- 모듈당 512 x 1024, 4M 이상으로 타일링 가능
- **동적 범위(Dynamic range)**: 적응형 이득 전환(Adaptive gain switching, 3단계 이득)
- **프레임 속도**: 최대 2.2 kHz (풀 프레임)
- **인터페이스**: 모듈당 10 GbE
- **용도**: 분광학(spectroscopy), XPCS, 고동적범위 이미징
- **출력 형식**: 원시 바이너리 프레임; 수신기에서 HDF5로 변환

### Vortex (Hitachi)

- **기술**: 에너지 분산 XRF용 실리콘 드리프트 검출기(Silicon drift detector, SDD)
- **채널**: 단일 소자 또는 4소자 어레이
- **에너지 분해능**: 5.9 keV에서 FWHM < 130 eV
- **계수율(Count rate)**: 소자당 최대 1 Mcps (출력 계수율)
- **인터페이스**: 디지털 펄스 프로세서 (xMAP / Mercury)
- **용도**: X선 형광(X-ray fluorescence) 매핑, XANES
- **출력 형식**: 픽셀당 MCA 스펙트럼, HDF5로 저장

## EPICS IOC 및 Area Detector 프레임워크

### EPICS IOC 아키텍처

EPICS(Experimental Physics and Industrial Control System)는 검출기 하드웨어와
상위 레벨 소프트웨어 사이의 실시간 제어 계층을 제공합니다.

```
Detector Hardware
    |
    v
Device Support Layer  (driver-specific C/C++ code)
    |
    v
EPICS IOC             (records, databases, sequencer)
    |
    v
Channel Access / PV Access  (network protocol)
    |
    v
Client Applications   (CSS, caput, pvget, Python scripts)
```

수집을 위한 주요 IOC 데이터베이스:

| 데이터베이스 | 용도 |
|---|---|
| `cam.db` | 검출기 모드, 노출, 이득, 트리거 설정 |
| `image.db` | 이미지 크기, 데이터 유형, 배열 포트 |
| `file.db` | 파일 경로, 이름 패턴, 쓰기 플러그인 구성 |
| `stats.db` | 실시간 통계 (최소, 최대, 평균, 시그마) |

### Area Detector 플러그인

areaDetector 프레임워크는 IOC 내에서 플러그인 기반 파이프라인을 제공합니다:

1. **NDPluginStdArrays** -- Channel Access / PV Access를 통해 프레임 게시
2. **NDPluginROI** -- 저장 전 관심 영역(region of interest) 추출
3. **NDPluginProcess** -- IOC 내에서 배경 차감 및 플랫 필드(flat-field) 적용
4. **NDPluginHDF5** -- SWMR 지원으로 NeXus/HDF5 파일 기록
5. **NDPluginCodec** -- 스트리밍을 위한 프레임 압축 (Blosc, JPEG, LZ4)

## 데이터 수집 트리거

### 트리거 모드

| 모드 | 설명 | 일반적인 용도 |
|---|---|---|
| Internal | 설정된 속도로 검출기가 자유 실행 | 정렬, 테스트 |
| External (TTL) | 타이밍 시스템의 하드웨어 트리거 | 플라이 스캔(fly scan) |
| Software | IOC가 Channel Access를 통해 트리거 전송 | 스텝 스캔(step scan) |
| Gated | 외부 게이트 신호가 노출 창을 정의 | 펌프-프로브(pump-probe) |

### 플라이 스캔 트리거 체인

```
Motor Controller (Delta Tau / Aerotech)
    |-- position-compare output (TTL pulse)
    v
Timing Fanout (SIS3820 / SoftGlue FPGA)
    |-- trigger to detector
    |-- trigger to scaler
    |-- trigger to MCS
    v
Detector captures frame per trigger
```

플라이 스캔은 동기화된 데이터 캡처와 함께 연속 모션을 구현하여,
스텝 앤 슛(step-and-shoot) 시퀀스의 오버헤드를 제거합니다. 일반적인 각도 스텝:
180 deg/s에서 0.1 deg로 1초에 1800개의 투영(projection)을 얻습니다.

## 메타데이터 기록

모든 수집에서 HDF5 마스터 파일에 다음 메타데이터를 기록합니다:

- **빔라인 파라미터**: 에너지 (keV), 링 전류 (mA), 언듈레이터(undulator) 갭
- **검출기 설정**: 노출 시간, 이득 모드, 임계 에너지
- **모터 위치**: 시료 x/y/z, 회전 각도, 검출기 거리
- **환경**: 온도, 습도, 시료 ID, 과제 번호(proposal number)
- **타임스탬프**: ISO-8601 시작/종료, 프레임별 EPICS 타임스탬프

메타데이터는 **NeXus 애플리케이션 정의**
(`NXtomo`, `NXsas`, `NXxas`)에 따라 기록되어 DAWN, silx, Xi-CAM 등
커뮤니티 도구와의 상호운용성(interoperability)을 보장합니다.

## 데이터 전송률

| 검출기 | 해상도 | 프레임 속도 | 원시 전송률 |
|---|---|---|---|
| EIGER2 X 4M | 2070 x 2167 x 16 bit | 750 Hz | ~6.7 GB/s |
| Jungfrau 4M | 2048 x 2048 x 16 bit | 2.2 kHz | ~18.4 GB/s |
| Vortex ME-4 | 4 x 4096 channels | 1 kHz | ~32 MB/s |

이러한 전송률은 고대역폭 스트리밍 및 처리 인프라를 요구하며,
[streaming.md](streaming.md)와 [processing.md](processing.md)에서 설명합니다.
