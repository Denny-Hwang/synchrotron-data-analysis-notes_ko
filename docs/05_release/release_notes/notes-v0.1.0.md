---
doc_id: REL-N010
title: "Release Notes — notes-v0.1.0"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [ADR-006]
---

# Release Notes — notes-v0.1.0

**Content Baseline**

## Summary

Establishes the initial content baseline for the synchrotron-data-analysis-notes
repository. This tag marks the state of all 9 note folders as of 2026-04-08,
prior to any frontmatter annotation or restructuring.

## Content Inventory

| Folder | Files | Description |
|--------|-------|-------------|
| `01_program_overview` | 5 | BER mission, APS facility, 15 beamlines, partners, 7 research domains |
| `02_xray_modalities` | 21 | 6 modalities with data formats and AI/ML method summaries |
| `03_ai_ml_methods` | 26 | 14 AI/ML methods across 5 categories (segmentation, denoising, reconstruction, autonomous, multimodal) |
| `04_publications` | 23 | 14 paper reviews, template, program publications overview |
| `05_tools_and_code` | 28 | 7 tools with reverse engineering, pros/cons, reproduction guides |
| `06_data_structures` | 19 | HDF5 schemas (XRF, tomo, ptychography), EDA guides, data scale analysis |
| `07_data_pipeline` | 7 | Acquisition → streaming → processing → analysis → storage |
| `08_references` | 4 | Glossary, bibliography, useful links |
| `09_noise_catalog` | 76 | 29+ noise/artifact types, troubleshooter, before/after images |

**Total: ~209 markdown files + Jupyter notebooks + images**

## Note Format

- All notes are plain markdown (no YAML frontmatter at baseline).
- Headings use `# H1` for titles, tables for structured data.
- Publication reviews follow `template_paper_review.md`.
- No controlled vocabulary annotations yet — this will be progressively added per ADR-003.

## What's Next

- Progressive frontmatter annotation starting with `02_xray_modalities` and `03_ai_ml_methods`.
- Controlled vocabulary adoption per DC-001.
