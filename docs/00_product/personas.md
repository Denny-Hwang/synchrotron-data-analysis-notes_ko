---
doc_id: PER-001
title: "Target Personas"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [VIS-001, PRD-001, UST-001]
---

# Target Personas

## Persona A: Beamline Scientist

| Attribute | Detail |
|-----------|--------|
| **Name** | Dr. Maria Chen |
| **Role** | Beamline Scientist, APS Sector 2-ID (XRF Microscopy) |
| **Experience** | 8 years at APS, expert in X-ray fluorescence imaging |

### Background

Maria runs experiments on the 2-ID-E microprobe beamline. She collects large XRF datasets (100 GB+ per session post-APS-U) and is increasingly interested in applying AI/ML methods — particularly deep-learning-based denoising and automated segmentation — to reduce analysis turnaround from days to hours.

### Goals

- Find AI/ML methods that are proven for XRF microscopy data.
- Understand which tools (PyXRF, MAPS, custom scripts) integrate with which methods.
- Locate publication reviews that validate method performance on real beamline data.

### Pain Points

- The repository has 14 AI/ML method write-ups, but she has to open each one to check if it's relevant to XRF.
- Cross-references between modalities and methods are buried in prose.
- No quick way to filter by beamline or modality.

### Success Signal

Maria finds a relevant denoising method, its publication review, and the associated tool in under 3 clicks from the landing page.

---

## Persona B: New BER User

| Attribute | Detail |
|-----------|--------|
| **Name** | James Park |
| **Role** | First-year graduate student, Environmental Science, joining BER program |
| **Experience** | Strong biology background, no prior synchrotron experience |

### Background

James just started his PhD studying soil microbiome dynamics. His advisor told him he'll be using X-ray tomography and XRF at APS to image root–soil interfaces. He has never been to a synchrotron and doesn't know the difference between ptychography and crystallography.

### Goals

- Understand what the BER program is and which beamlines he'll use.
- Build a mental model of X-ray modalities relevant to environmental science.
- Find a learning path: "where do I start?" → "what data will I collect?" → "how do I analyze it?"

### Pain Points

- Overwhelmed by the 9 top-level folders and 200+ files.
- Terminology is unfamiliar (HDF5, EPICS, IOC, reconstruction).
- No guided onboarding or progressive disclosure by expertise level.

### Success Signal

James follows a clear path from "Discover the Program" → his research domain → relevant beamlines → data formats → starter analysis tools, all within a single session.

---

## Persona C: Computational Scientist / Software Developer

| Attribute | Detail |
|-----------|--------|
| **Name** | Dr. Alex Rivera |
| **Role** | Research Software Engineer, ALCF (Argonne Leadership Computing Facility) |
| **Experience** | 10 years in scientific computing, Python/C++/CUDA, new to synchrotron domain |

### Background

Alex was assigned to optimize the TomocuPy GPU reconstruction pipeline for the Aurora exascale system. They need to understand the data pipeline end-to-end — from detector acquisition through streaming to reconstruction — and figure out where GPU acceleration has the most impact.

### Goals

- Understand the data pipeline architecture: acquisition → streaming → processing → storage.
- Find tool reverse-engineering docs (TomocuPy, TomoPy, Bluesky/EPICS).
- Locate code examples, HDF5 schemas, and benchmark data to prototype against.

### Pain Points

- The pipeline docs are in `07_data_pipeline/`, tool docs in `05_tools_and_code/`, and data schemas in `06_data_structures/` — three separate trees with no unified view.
- No quick-reference for code entry points, CLI commands, or API surfaces.
- Needs to understand Bluesky/EPICS integration but it's mixed in with science content.

### Success Signal

Alex navigates from "Build and Compute" → data pipeline overview → TomocuPy architecture → GPU kernel benchmarks → relevant HDF5 schema, bookmarking each page along the way.
