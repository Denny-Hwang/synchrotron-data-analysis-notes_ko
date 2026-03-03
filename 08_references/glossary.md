# 방사광 과학 용어집

## A

**Absorption edge (흡수 에지)**: 핵심 전자의 여기로 인해 X선 흡수가 급격히 증가하는 에너지. 각 원소는 고유한 에지 에너지를 가집니다 (K, L, M 에지).

**ALCF (Argonne Leadership Computing Facility)**: Argonne에 위치한 DOE 슈퍼컴퓨팅 센터로, Aurora 엑사스케일 시스템을 운영합니다.

**APS (Advanced Photon Source)**: Argonne National Laboratory에 위치한 DOE 방사광 X선 광원.

**APS-U (Advanced Photon Source Upgrade)**: 저장링을 MBA 격자로 교체하여 최대 500배 더 밝은 X선 빔을 달성하는 8억 1,500만 달러 규모의 프로젝트.

## B

**Beam time (빔타임)**: 방사광 빔라인에서 실험을 위해 할당된 시간. 일반적으로 할당당 3-5일.

**Beamline (빔라인)**: 저장링에서 X선을 받아 시료에 전달하는 방사광의 실험 스테이션.

**BER (Office of Biological and Environmental Research)**: eBERlight에 자금을 지원하는 DOE 사무소.

**Bluesky**: 방사광 빔라인을 위한 Python 기반 실험 오케스트레이션 프레임워크.

**Bragg peak (브래그 피크)**: 브래그 법칙 (nλ = 2d sin θ)을 만족하는 날카로운 회절 피크로, 결정면에서의 보강 간섭을 나타냅니다.

## C

**CBF (Crystallographic Binary File)**: 회절 이미지를 위한 레거시 파일 형식.

**CDI (Coherent Diffraction Imaging, 코히어런트 회절 이미징)**: 코히어런트 X선을 사용한 렌즈 없는 이미징.

**Coherence (코히어런스)**: X선 파동이 잘 정의된 위상 관계를 갖는 속성. APS-U는 코히어런트 플럭스를 극적으로 증가시킵니다.

**CuPy**: TomocuPy에서 GPU 계산에 사용하는 GPU 가속 NumPy 라이브러리.

**CXI (Coherent X-ray Imaging format)**: 타이코그래피 및 CDI 데이터를 위한 HDF5 기반 표준.

## D

**DBA (Double-Bend Achromat)**: 원래 APS 저장링 격자 설계 (3세대).

**DLSIA (Deep Learning for Scientific Image Analysis)**: LBNL에서 방사광 이미지 분석을 위해 개발한 프레임워크.

## E

**eBERlight (enabling Biological and Environmental Research with light)**: APS의 DOE BER 프로그램.

**Emittance (에미턴스)**: 방사광의 전자 빔 크기와 발산을 나타내는 척도. 낮은 에미턴스 = 더 밝은 X선. APS-U는 42 pm·rad를 달성합니다.

**EPICS (Experimental Physics and Industrial Control System)**: 방사광 장비 제어를 위한 소프트웨어 프레임워크.

**EXAFS (Extended X-ray Absorption Fine Structure, 확장 X선 흡수 미세 구조)**: 에지 위 ~50 eV 이상에서 X선 흡수 스펙트럼의 진동으로, 결합 거리와 배위 정보를 인코딩합니다.

## F

**FBP (Filtered Back Projection, 필터 역투영)**: 단층촬영 재구성을 위한 표준 해석적 알고리즘.

**FICUS (Facilities Integrating Collaborations for User Science)**: 다중 시설 과제를 가능하게 하는 DOE 프로그램.

**Flat field (플랫필드)**: X선 빔이 있지만 시료가 없는 상태에서 촬영한 이미지 (단층촬영에서 정규화에 사용).

**Fresnel zone plate (프레넬 존 플레이트)**: X선을 나노미터 스케일 초점으로 집속하는 데 사용되는 회절 광학 소자.

## G

**GMM (Gaussian Mixture Model, 가우시안 혼합 모델)**: XRF 데이터 분석에 사용되는 확률적 클러스터링 방법.

**Gridrec**: TomoPy에서 기본 알고리즘으로 사용되는 FBP의 FFT 기반 구현.

## H

**HDF5 (Hierarchical Data Format version 5)**: 방사광 데이터에 널리 사용되는 자기 기술적 파일 형식. 계층적 그룹, 대용량 데이터셋, 압축을 지원합니다.

## I

**INR (Implicit Neural Representation, 암묵적 신경 표현)**: 좌표를 값에 매핑하여 연속 필드를 표현하는 신경망.

**Ion chamber (이온 챔버)**: 정규화에 사용되는 X선 빔 강도를 측정하는 가스 충전 검출기.

## K

**KB mirrors (Kirkpatrick-Baez mirrors)**: X선 빔을 집속하는 데 사용되는 한 쌍의 직교 곡면 거울.

## M

**MAPS (Microanalysis Toolkit)**: APS의 주요 XRF 스펙트럼 분석 소프트웨어.

**MBA (Multi-Bend Achromat, 다중 굴곡 아크로매트)**: APS-U 저장링 격자 설계 (4세대)로, 에미턴스를 최소화하기 위해 섹터당 7개의 굴곡을 사용합니다.

**MX (Macromolecular Crystallography, 거대분자 결정학)**: X선 회절에 의한 단백질/핵산 3D 구조 결정.

**µCT (Micro-Computed Tomography, 마이크로 CT)**: 마이크로미터 스케일 분해능의 X선 CT 이미징.

## N

**NeXus**: 중성자, X선, 뮤온 과학을 위한 HDF5 기반 데이터 형식 표준. 표준화된 스키마를 정의합니다.

**nnU-Net**: 최적의 분할 아키텍처를 자동으로 결정하는 자가 구성 U-Net 프레임워크.

## O

**Ophyd**: Bluesky 제어 장치에 대한 하드웨어 추상화를 제공하는 Python 라이브러리.

**Otsu thresholding (오쓰 임계값)**: 이봉 히스토그램에서 클래스 내 분산을 최소화하는 자동 임계값 방법.

## P

**PCA (Principal Component Analysis, 주성분 분석)**: ROI-Finder에서 특징 추출에 사용되는 선형 차원 축소 기법.

**Phase retrieval (위상 복원)**: 측정된 강도(진폭²만 기록)로부터 X선 파동의 위상을 계산적으로 복원하는 것.

**Ptychography (타이코그래피)**: 겹치는 스캔 위치를 사용하여 위상 문제를 풀고 진폭 및 위상 이미지를 재구성하는 코히어런트 이미징 기법.

**PtychoNet**: 빠른 타이코그래피 위상 복원을 위한 CNN 기반 접근법.

## R

**Radon transform (라돈 변환)**: 객체 함수를 선적분(투영)과 관련시키는 수학적 변환. CT 재구성의 기초.

**ROI (Region of Interest, 관심 영역)**: 상세 측정을 위해 선택된 영역.

**ROI-Finder**: XRF 현미경에서 관심 영역 선택을 위한 ML 가이드 도구.

## S

**SAXS (Small-Angle X-ray Scattering, 소각 X선 산란)**: 작은 각도의 산란으로부터 나노구조 (1-100 nm)를 측정합니다.

**Sinogram (시노그램)**: 각 행이 하나의 각도에 해당하는 투영 데이터의 재배열. 재구성 알고리즘의 입력 형식.

**SIREN (Sinusoidal Representation Networks)**: 연속 신호를 표현하기 위해 사인 활성화를 사용하는 신경망.

**SSX (Serial Synchrotron Crystallography, 직렬 방사광 결정학)**: 무작위로 배향된 많은 마이크로결정에서 회절 데이터를 수집하는 것.

## T

**TomocuPy**: CuPy를 사용한 GPU 가속 단층촬영 재구성 도구. TomoPy보다 20-30배 빠릅니다.

**TomoGAN**: 저선량 방사광 단층촬영을 위한 GAN 기반 노이즈 제거 방법.

**TomoPy**: 단층촬영 데이터 처리 및 재구성을 위한 표준 Python 패키지.

## U

**U-Net**: 스킵 연결이 있는 인코더-디코더 CNN 아키텍처로, 이미지 분할에 널리 사용됩니다.

**UMAP (Uniform Manifold Approximation and Projection)**: 시각화를 위한 비선형 차원 축소.

## V

**Voxel (복셀)**: 3D 픽셀 -- 재구성된 단층촬영 볼륨의 체적 요소.

## W

**WAXS (Wide-Angle X-ray Scattering, 광각 X선 산란)**: 넓은 각도의 산란으로부터 원자/분자 스케일 구조를 측정합니다.

## X

**XANES (X-ray Absorption Near-Edge Structure, X선 흡수 근접 에지 구조)**: 흡수 에지 근처의 XAS 스펙트럼 미세 구조로, 산화 상태와 배위 기하학에 민감합니다.

**XAS (X-ray Absorption Spectroscopy, X선 흡수 분광학)**: 에너지 함수로 X선 흡수를 측정하여 국소 원자 환경과 화학적 상태를 탐색합니다.

**XPCS (X-ray Photon Correlation Spectroscopy, X선 광자 상관 분광학)**: 코히어런트 X선 스페클 패턴의 시간적 요동을 분석하여 동역학을 측정합니다.

**XRF (X-ray Fluorescence, X선 형광)**: 입사 X선에 의해 여기된 원소에서 방출되는 특성 X선으로, 원소 매핑에 사용됩니다.

## Z

**Zone plate (존 플레이트)**: 프레넬 존 플레이트 참조.
