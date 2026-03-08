# 샘플 데이터 링크

## 개요

이 페이지는 분석 파이프라인 테스트, 데이터 형식 학습, 알고리즘 벤치마킹에 적합한
공개적으로 사용 가능한 방사광 데이터셋 링크를 제공합니다. 여기에 나열된 모든
데이터셋은 오픈 데이터 라이선스 하에 자유롭게 접근할 수 있습니다.

## 단층촬영 데이터셋

### TomoBank

Argonne National Laboratory의 **TomoBank** 저장소는 Data Exchange HDF5 형식의
완전한 메타데이터가 포함된 큐레이션된 단층촬영 데이터셋을 제공합니다.

- **저장소**: [https://tomobank.readthedocs.io/](https://tomobank.readthedocs.io/)
- **형식**: Data Exchange HDF5
- **포함 내용**: 투영, 플랫/다크 필드, theta 배열, 메타데이터

| 데이터셋 ID | 설명 | 크기 | 빔라인 |
|-------------|------|------|--------|
| tomo_00001 | 셰일 암석 코어 | 12 GB | APS 2-BM |
| tomo_00002 | 등쪽 뿔 (신경과학) | 8 GB | APS 2-BM |
| tomo_00003 | 화산암 | 5 GB | APS 2-BM |
| tomo_00004 | 치아 상아질 | 6 GB | APS 32-ID |
| tomo_00005 | 연료전지 전극 | 3 GB | APS 32-ID |
| tomo_00006 | 금속 폼 | 4 GB | APS 2-BM |
| tomo_00007 | 습윤 시멘트 수화 (시계열) | 45 GB | APS 2-BM |

**다운로드 예시**:
```bash
# Using Globus CLI
globus transfer <tomobank-endpoint-id>:/tomo_00001/ <local-endpoint>:/data/tomo/
```

### 동적 단층촬영

- **알루미늄 합금 응고의 4D 단층촬영**
  - DOI: [10.13139/OLCF/1347542](https://doi.org/10.13139/OLCF/1347542)
  - 600 시간 단계, 각 1200개 투영
  - 형식: Data Exchange HDF5

## XRF 현미경 데이터셋

### ROI-Finder 샘플 데이터

**ROI-Finder** 도구에는 자동화된 관심 영역 검출 파이프라인 테스트를 위한
샘플 XRF 데이터셋이 포함되어 있습니다.

- **저장소**: [https://github.com/arshadzahangirchowdhury/ROI-Finder](https://github.com/arshadzahangirchowdhury/ROI-Finder)
- **형식**: MAPS HDF5
- **포함 내용**: 피팅된 원소 맵, 원시 스펙트럼, 스캔 좌표

| 데이터셋 | 설명 | 원소 | 크기 |
|----------|------|------|------|
| roi_finder_sample_1 | 식물 뿌리 단면 | Fe, Zn, Ca, K | 200 MB |
| roi_finder_sample_2 | 토양 응집체 | Fe, Mn, Cu, Zn, As | 350 MB |

### IXRF 샘플 스펙트럼

- **IXRF 표준**: [https://www.ixrfsystems.com/resources/](https://www.ixrfsystems.com/resources/)
- 교정 및 에너지 확인을 위한 참조 XRF 스펙트럼

## NeXus 예제 파일

NeXus 국제 표준은 리더 테스트를 위한 예제 HDF5/NeXus 파일을 제공합니다:

- **저장소**: [https://github.com/nexusformat/exampledata](https://github.com/nexusformat/exampledata)
- **형식**: NeXus/HDF5
- **포함 내용**: 다양한 NXclass 유형에 대한 예제

| 파일 | NX 클래스 | 설명 |
|------|----------|------|
| `chopper.nxs` | NXentry | 비행시간 초퍼 분광기 |
| `powder.nxs` | NXentry | 분말 회절 패턴 |
| `sans.nxs` | NXentry | 소각 중성자 산란 |
| `tomo.nxs` | NXentry | 기본 단층촬영 예제 |

## 코히어런트 이미징 / 타이코그래피

### CXIDB (Coherent X-ray Imaging Data Bank)

- **저장소**: [https://www.cxidb.org/](https://www.cxidb.org/)
- **형식**: CXI (HDF5 기반)
- **포함 내용**: 회절 패턴, 스캔 위치, 재구성

| 항목 | 설명 | 분해능 | 크기 |
|------|------|--------|------|
| CXIDB-22 | 금 나노입자 테스트 패턴 | 15 nm | 1.2 GB |
| CXIDB-54 | 집적회로 (IC) 이미징 | 20 nm | 3.5 GB |
| CXIDB-88 | 생물학적 세포 | 30 nm | 2.1 GB |
| CXIDB-110 | 배터리 전극 | 25 nm | 4.0 GB |

### PtychoNN 훈련 데이터

- **저장소**: [https://github.com/mcherukara/PtychoNN](https://github.com/mcherukara/PtychoNN)
- 신경망 타이코그래피 재구성을 위한 훈련 데이터셋

### edgePtychoNN 실험 데이터 (Babu et al. 2023)

- **Zenodo DOI**: [10.5281/zenodo.8121606](https://zenodo.org/records/8121606)
- **코드**: [https://github.com/vbanakha/edgePtychoNN](https://github.com/vbanakha/edgePtychoNN)
- **형식**: NumPy `.npy` 배열 + `positions.csv`
- **라이선스**: CC BY 4.0
- **포함 내용**: 121개 나선형 스캔 × 963개 회절 이미지 (128×128 픽셀), Medipix3 검출기로 50 nm 간격 / 0.4 s 노출로 수집
- **논문**: "Deep learning at the edge enables real-time streaming ptychographic imaging"
  ([10.1038/s41467-023-41496-z](https://doi.org/10.1038/s41467-023-41496-z))

**빠른 시작 예시**:
```python
import numpy as np
import matplotlib.pyplot as plt

# 단일 스캔 로드 (963개 회절 패턴, 128x128)
scan = np.load("diff_scan_810.npy")
print(f"스캔 형태: {scan.shape}")  # (963, 128, 128)

# 단일 회절 패턴 시각화 (로그 스케일)
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for i, idx in enumerate([0, 480, 962]):
    axes[i].imshow(np.log1p(scan[idx]), cmap="viridis")
    axes[i].set_title(f"패턴 #{idx}")
plt.suptitle("타이코그래피 회절 패턴")
plt.tight_layout()
plt.show()

# 스캔 위치 로드
import pandas as pd
positions = pd.read_csv("positions.csv")
print(f"위치: {len(positions)}개 포인트")
```

## 분광학 데이터셋

### XAS 참조 스펙트럼

- **IXAS Spectra Database**: [https://xaslib.xrayabsorption.org/](https://xaslib.xrayabsorption.org/)
  - 커뮤니티가 기여한 참조 XANES 및 EXAFS 스펙트럼
  - 대부분의 원소에 대한 다중 에지 (K, L, M)
  - 형식: 일반 텍스트, Athena 프로젝트 파일

### XANES 표준 라이브러리

| 라이브러리 | 원소 | 에지 | 형식 |
|-----------|------|------|------|
| APS XANES Library | Fe, Mn, S, P, As | K-edge | ASCII |
| ESRF ID21 Standards | 다양 | K, L | HDF5/NeXus |
| Diamond I18 Standards | 전이 금속 | K-edge | Athena (.prj) |

## 과학 데이터 논문

동료 심사 논문과 함께 발표된 데이터셋:

| 논문 | 데이터셋 유형 | DOI |
|------|-------------|-----|
| De Carlo et al. (2014) "Scientific Data Exchange" | 단층촬영 참조 | [10.1088/0957-0233/25/11/115501](https://doi.org/10.1088/0957-0233/25/11/115501) |
| Gursoy et al. (2014) "TomoPy benchmarks" | 단층촬영 + 팬텀 | [10.1107/S1600577514013939](https://doi.org/10.1107/S1600577514013939) |
| Vogt (2003) "MAPS paper" | XRF 참조 | [10.1051/jp4:20030218](https://doi.org/10.1051/jp4:20030218) |
| Cherukara et al. (2020) "PtychoNN" | 타이코그래피 훈련 | [10.1063/5.0013065](https://doi.org/10.1063/5.0013065) |

## 대용량 데이터셋 다운로드

수 GB를 초과하는 데이터셋의 경우 다음을 권장합니다:

1. **Globus Transfer** -- DOE 시설의 다중 GB 파일에 최적
   ```bash
   pip install globus-cli
   globus login
   globus transfer <src-endpoint>:<src-path> <dst-endpoint>:<dst-path>
   ```

2. **wget/curl** -- 웹 접근 가능한 저장소의 소규모 파일에 적합
   ```bash
   wget -c https://tomobank.readthedocs.io/data/tomo_00001.h5
   ```

3. **Petrel** -- Globus를 통한 Argonne의 데이터 공유 플랫폼
   - [https://petrel.alcf.anl.gov/](https://petrel.alcf.anl.gov/)

## 관련 자료

- [HDF5 구조 가이드](../hdf5_structure/)
- [EDA 노트북](../eda/notebooks/)
- [데이터 파이프라인 아키텍처](../../07_data_pipeline/)
