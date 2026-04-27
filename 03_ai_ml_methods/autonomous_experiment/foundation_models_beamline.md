# 빔라인 제어를 위한 파운데이션 모델

**참고문헌**: Nature Scientific Data (2025), DOI: [10.1038/s41597-025-04605-9](https://doi.org/10.1038/s41597-025-04605-9); tomoCAM, J. Synchrotron Rad. (2024), DOI: [10.1107/S1600577523009876](https://doi.org/10.1107/S1600577523009876)

## 개념

**파운데이션 모델**은 싱크로트론 빔라인 운영에 적용되는 대규모 사전 학습 모델(LLM, vision transformer, 멀티모달 모델)입니다. 각 빔라인 기능에 대해 작업별 모델을 처음부터 학습시키는 대신, 파운데이션 모델은 대규모 사전 학습을 활용하여 zero-shot 또는 few-shot 적응을 통해 다양한 작업에 일반화합니다.

```
Traditional ML pipeline:
  Beamline task A → Collect data A → Train model A
  Beamline task B → Collect data B → Train model B
  Beamline task C → Collect data C → Train model C

Foundation model approach:
  Large pre-trained model → Fine-tune/prompt for task A, B, C
                          → Zero-shot generalization to new tasks
```

## 아키텍처

### LLM 기반 빔라인 인터페이스

```
User natural language input
    │  "Set the energy to 12 keV and collect 720 projections
    │   with 0.5 second exposure"
    │
    ├─→ LLM (GPT-4 / Claude) with beamline context
    │       System prompt: beamline capabilities, safety limits,
    │                      EPICS PV names, standard procedures
    │
    ├─→ Structured command generation
    │       {
    │         "action": "configure_scan",
    │         "parameters": {
    │           "energy_keV": 12.0,
    │           "n_projections": 720,
    │           "exposure_s": 0.5
    │         }
    │       }
    │
    ├─→ Safety validation layer
    │       Check: energy within range? exposure safe? dose limit?
    │
    └─→ EPICS/Bluesky execution
        caput("energy", 12.0)
        RE(ct_scan(n_proj=720, exp=0.5))
```

### 시료 스크리닝을 위한 Vision Transformer

```
Sample microscope image (H×W×3)
    │
    ├─→ Patch embedding (16×16 patches)
    │       Each patch → linear projection → token
    │       + positional embedding + [CLS] token
    │
    ├─→ Transformer encoder (12 layers)
    │       Multi-head self-attention (12 heads)
    │       Layer norm + MLP + residual connections
    │       Pre-trained on ImageNet + fine-tuned on synchrotron data
    │
    ├─→ Task heads (multi-task):
    │       [CLS] → Sample type classification
    │       [CLS] → Quality score regression
    │       Patch tokens → ROI segmentation
    │       [CLS] → Recommended scan parameters
    │
    └─→ Outputs:
        - Sample type: "biological tissue, hydrated"
        - Quality: 0.87 (suitable for measurement)
        - ROI mask: highlighted regions of interest
        - Parameters: {energy: 10 keV, resolution: 0.5 µm}
```

### 멀티모달 파운데이션 모델

```
Inputs (any combination):
    │
    ├── Optical microscope image ──→ Vision encoder (ViT)
    ├── Previous X-ray data ───────→ Spectral encoder (1D CNN)
    ├── Sample metadata ───────────→ Text encoder (BERT)
    ├── Experimental log ──────────→ Text encoder (BERT)
    │
    ├─→ Cross-attention fusion
    │       All modalities attend to each other
    │       Learns correlations: optical appearance ↔ X-ray properties
    │
    ├─→ Unified representation
    │
    └─→ Task-specific heads:
        ├── Predict optimal beamline parameters
        ├── Estimate expected data quality
        ├── Suggest measurement strategy
        └── Flag potential issues (sample damage, alignment)
```

## 핵심 기능

### 자연어 실험 제어

```python
# LLM-based beamline assistant example
class BeamlineAssistant:
    def __init__(self, llm_client, beamline_config):
        self.llm = llm_client
        self.config = beamline_config
        self.system_prompt = f"""
        You are a beamline control assistant for {beamline_config['name']}.
        Available motors: {beamline_config['motors']}
        Energy range: {beamline_config['energy_range']} keV
        Safety limits: {beamline_config['safety']}
        Available scan types: {beamline_config['scan_types']}

        Convert user requests into structured commands.
        Always validate against safety limits before execution.
        """

    def process_request(self, user_input):
        response = self.llm.generate(
            system=self.system_prompt,
            user=user_input,
            output_format="json"
        )
        command = self.validate_safety(response)
        return command
```

### 자동 시료 스크리닝

```
Workflow:
  1. Robot loads sample onto stage
  2. Optical microscope captures overview image
  3. Vision transformer classifies sample:
     - Type (biological, geological, materials, ...)
     - Condition (intact, damaged, dried, ...)
     - Regions of interest (edges, inclusions, interfaces)
  4. Foundation model recommends:
     - Scan type (tomo, SAXS, XRF, ...)
     - Energy (K-edge selection for elements of interest)
     - Resolution (feature size dependent)
     - Dose budget (radiation sensitivity)
  5. Beamline executes recommended scan autonomously

Zero-shot capability: Can handle new sample types not seen during training
by leveraging pre-trained visual understanding.
```

### 싱크로트론 데이터를 위한 멀티태스크 파운데이션 모델

다양한 싱크로트론 데이터셋(CT, 회절, 분광법, 산란)으로 학습되어 다음을 수행할 수 있습니다.

```
Pre-training tasks:
  ├── Masked image modeling (reconstruct masked patches)
  ├── Contrastive learning (match related measurements)
  ├── Next-measurement prediction (temporal context)
  └── Cross-modal alignment (optical ↔ X-ray correspondence)

Downstream tasks (fine-tuned or zero-shot):
  ├── Anomaly detection across modalities
  ├── Phase identification from diffraction
  ├── Segmentation of tomographic volumes
  ├── Spectral decomposition of XRF maps
  └── Quality assessment of incoming data
```

## 3차원 멀티모달 싱크로트론 데이터셋

2025년 Nature Scientific Data 논문은 파운데이션 모델 학습 및 벤치마킹을 위한 표준화된 3D 멀티모달 싱크로트론 데이터셋을 제공합니다.

```
Dataset contents:
  ├── Tomographic volumes (absorption, phase contrast)
  ├── XRF elemental maps (co-registered)
  ├── SAXS/WAXS patterns (spatially resolved)
  ├── Sample metadata and experimental parameters
  └── Annotations and segmentation labels

Use cases for foundation models:
  - Pre-training on diverse synchrotron data
  - Benchmarking cross-modal transfer learning
  - Evaluating zero-shot generalization
```

## tomoCAM 통합

tomoCAM(2024)은 파운데이션 모델 기반 실험을 위한 계산 백본 역할을 할 수 있는 빠른 모델 기반 반복 재구성을 제공합니다.

```
Foundation model decides: "Collect 180 sparse projections at 15 keV"
    │
    tomoCAM executes: Fast GPU reconstruction in <1 second
    │
    Foundation model evaluates: "Quality sufficient for segmentation task"
    │
    Decision: "Proceed to next sample" or "Collect additional angles"

tomoCAM enables the fast feedback loop required for autonomous operation.
```

## 파운데이션 모델을 활용한 자율성 수준

| 수준 | 전통적 ML | 파운데이션 모델 |
|-------|---------------|-----------------|
| **1 - 자문(Advisory)** | 특화된 detector | LLM이 자연어로 결과를 설명 |
| **2 - 감독(Supervised)** | 작업별 모델 | 멀티태스크 모델이 다양한 의사결정 처리 |
| **3 - 조건부(Conditional)** | 다수의 특화 모델 | 단일 모델이 전체 워크플로우를 담당 |
| **4 - 완전 자율(Full autonomous)** | 복잡한 모델 파이프라인 | 파운데이션 모델이 모든 것을 오케스트레이션 |

## 강점

1. **Zero-shot 일반화**: 재학습 없이 새로운 시료 유형 처리
2. **자연어 인터페이스**: 비전문 빔라인 사용자의 진입 장벽을 낮춤
3. **멀티태스크 능력**: 단일 모델로 분류, 분할, 최적화 처리
4. **전이 학습**: 사전 학습된 지식이 빔라인 및 모달리티 간에 전이됨
5. **빠른 적응**: 빔라인별 작업에 대한 few-shot 미세 조정
6. **해석 가능성**: LLM이 자연어로 의사결정을 설명할 수 있음

## 한계점

1. **환각(Hallucination) 위험**: LLM이 그럴듯하지만 잘못된 명령을 생성할 수 있음
2. **안전 우려**: 명령 실행 전 견고한 검증 계층 필수
3. **계산 비용**: 대형 모델은 상당한 GPU 리소스를 요구
4. **데이터 요구사항**: 사전 학습에 크고 다양한 싱크로트론 데이터셋 필요
5. **지연 시간(Latency)**: 대형 모델 추론이 실시간 제어에 너무 느릴 수 있음
6. **도메인 격차**: 일반 사전 학습이 싱크로트론 특유의 물리를 포착하지 못할 수 있음
7. **재현성**: LLM 출력이 실행마다 달라질 수 있음(temperature 의존적)

## 안전 아키텍처

```
User request
    │
    ├─→ LLM generates command
    │
    ├─→ Layer 1: Schema validation
    │       Is the command well-formed?
    │
    ├─→ Layer 2: Parameter bounds checking
    │       Are all values within safe ranges?
    │
    ├─→ Layer 3: Physics consistency
    │       Is the combination of parameters physically meaningful?
    │
    ├─→ Layer 4: Human approval (for Level 1-2 autonomy)
    │       Display proposed action, wait for confirmation
    │
    └─→ Execute via EPICS/Bluesky

Critical: NEVER allow LLM to directly control hardware without validation.
```

## 코드 예제

```python
import torch
import torch.nn as nn
from transformers import ViTModel, ViTConfig

class SynchrotronVisionModel(nn.Module):
    """Vision transformer for automated sample screening at synchrotron beamlines."""

    def __init__(self, n_sample_types=20, n_scan_params=8):
        super().__init__()
        # Pre-trained ViT backbone
        config = ViTConfig(
            image_size=224,
            patch_size=16,
            num_channels=3,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12,
        )
        self.backbone = ViTModel(config)

        # Task heads
        self.sample_classifier = nn.Sequential(
            nn.Linear(768, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, n_sample_types),
        )

        self.quality_scorer = nn.Sequential(
            nn.Linear(768, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

        self.param_predictor = nn.Sequential(
            nn.Linear(768, 256),
            nn.GELU(),
            nn.Linear(256, n_scan_params),
        )

    def forward(self, images):
        """Predict sample type, quality, and recommended parameters."""
        outputs = self.backbone(images)
        cls_token = outputs.last_hidden_state[:, 0]  # [CLS] token

        sample_type = self.sample_classifier(cls_token)
        quality = self.quality_scorer(cls_token)
        params = self.param_predictor(cls_token)

        return {
            'sample_type': sample_type,      # (batch, n_types) logits
            'quality_score': quality,         # (batch, 1) in [0, 1]
            'scan_parameters': params,        # (batch, n_params) predicted values
        }


class BeamlineLLMController:
    """LLM-based natural language interface for beamline control."""

    def __init__(self, llm_client, beamline_name="2-BM"):
        self.llm = llm_client
        self.beamline = beamline_name
        self.safety_limits = {
            "energy_keV": (5.0, 40.0),
            "exposure_s": (0.001, 10.0),
            "n_projections": (1, 10000),
            "sample_x_mm": (-50.0, 50.0),
            "sample_y_mm": (-25.0, 25.0),
        }

    def parse_command(self, natural_language_request):
        """Convert natural language to structured beamline command."""
        prompt = f"""
        Beamline: {self.beamline}
        Request: {natural_language_request}

        Generate a JSON command with fields:
        - action: one of [move, scan, configure, query]
        - parameters: dict of parameter names and values
        - estimated_time_s: expected execution time
        """
        response = self.llm.generate(prompt)
        command = self._parse_json(response)
        return command

    def validate_command(self, command):
        """Check command against safety limits."""
        errors = []
        for param, value in command.get("parameters", {}).items():
            if param in self.safety_limits:
                lo, hi = self.safety_limits[param]
                if not (lo <= value <= hi):
                    errors.append(
                        f"{param}={value} outside safe range [{lo}, {hi}]"
                    )
        return len(errors) == 0, errors

    def execute(self, natural_language_request):
        """Full pipeline: parse → validate → execute."""
        command = self.parse_command(natural_language_request)
        is_safe, errors = self.validate_command(command)

        if not is_safe:
            return {"status": "rejected", "errors": errors}

        # Execute via EPICS/Bluesky (placeholder)
        result = self._execute_epics(command)
        return {"status": "executed", "result": result}
```

## APS BER 프로그램과의 관련성

### 주요 응용

- **자동화된 BER 시료 스크리닝**: Vision 모델이 토양, 뿌리, 바이오필름 시료를 분류하고, 시료 유형에 따라 이미징 파라미터를 추천
- **자연어 실험 로그**: LLM이 실험 노트를 파싱하고 구조화하여 검색 가능하고 기계 판독 가능한 메타데이터 생성
- **빔라인 간 전이**: 2-BM에서 학습된 파운데이션 모델이 최소한의 미세 조정으로 26-ID로 전이됨
- **실시간 의사결정 지원**: 멀티모달 모델이 수신 데이터 품질을 기반으로 측정 전략을 운영자에게 조언

### 빔라인 통합

- **2-BM**: Vision transformer 시료 분류를 통한 자동 토모그래피 스크리닝
- **26-ID**: 실시간 품질 평가에 의해 안내되는 지능형 ptychography 스캐닝
- **9-ID**: 자연어 인터페이스를 통한 SAXS/WAXS 실험 계획
- **모든 빔라인**: FAIR 데이터 관행을 위한 LLM 기반 로그 파싱 및 메타데이터 추출
- 대규모 파운데이션 모델 호스팅 및 실행을 위한 ALCF의 계산 지원

### Zero-Shot 및 Few-Shot 일반화 가능성

```
Scenario: New beamline commissioning
Traditional: Collect months of training data → Train specialized models
Foundation:  Deploy pre-trained model → Few-shot adapt with 10-50 examples
             or zero-shot with detailed prompt engineering

Scenario: Novel sample type (never measured before)
Traditional: No ML assistance available
Foundation:  Vision model leverages general visual understanding
             LLM leverages scientific knowledge from pre-training
             → Provides reasonable initial parameters

This dramatically reduces the barrier to deploying ML at new beamlines
and for new experimental campaigns.
```

## 참고문헌

1. "Three-dimensional, multimodal synchrotron data for machine learning applications."
   Nature Scientific Data, 2025. DOI: [10.1038/s41597-025-04605-9](https://doi.org/10.1038/s41597-025-04605-9)
2. Nikitin, V., et al. "tomoCAM: fast model-based iterative reconstruction."
   J. Synchrotron Rad., 2024. DOI: [10.1107/S1600577523009876](https://doi.org/10.1107/S1600577523009876)
3. Dosovitskiy, A., et al. "An Image is Worth 16x16 Words: Transformers for Image
   Recognition at Scale." ICLR 2021. arXiv: 2010.11929
4. Brown, T., et al. "Language Models are Few-Shot Learners." NeurIPS 2020.
   DOI: [10.48550/arXiv.2005.14165](https://doi.org/10.48550/arXiv.2005.14165)
