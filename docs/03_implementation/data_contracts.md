---
doc_id: DC-001
title: "Data Contracts — Note Frontmatter Schema"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [IA-001, ADR-003, PRD-001]
---

# Data Contracts — Note Frontmatter Schema

## YAML Frontmatter Schema for Notes

All markdown files in the 8 note folders (01–08) and 09\_noise\_catalog may include YAML frontmatter at the top of the file. The explorer reads this frontmatter at runtime for filtering, metadata display, and IA mapping.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable title of the note |
| `cluster` | enum | Which task cluster this note belongs to (see controlled vocabulary) |
| `tags` | list[string] | Free-form tags for filtering |
| `modality` | enum \| null | Primary X-ray modality (see controlled vocabulary) |
| `beamline` | list[enum] \| null | Associated beamlines (see controlled vocabulary) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `related_publications` | list[string] | Filenames of related publication review notes |
| `related_tools` | list[string] | Filenames of related tool notes |
| `last_reviewed` | date (YYYY-MM-DD) | Date the note was last reviewed for accuracy |
| `description` | string | One-line summary for card display |
| `category` | string | Sub-category within the folder (e.g., "denoising", "segmentation") |

### Example

```yaml
---
title: "TomoGAN: Low-Dose CT Denoising"
cluster: explore
tags: [denoising, GAN, tomography, deep-learning]
modality: tomography
beamline: [2-BM, 32-ID]
related_publications: [review_tomogan_2020.md]
related_tools: [tomocupy, tomopy]
last_reviewed: 2026-03-15
---
```

## Controlled Vocabularies

### `cluster` Values

| Value | Maps To | Folders |
|-------|---------|---------|
| `discover` | Discover the Program | 01\_program\_overview, 08\_references |
| `explore` | Explore the Science | 02\_xray\_modalities, 03\_ai\_ml\_methods, 04\_publications, 09\_noise\_catalog |
| `build` | Build and Compute | 05\_tools\_and\_code, 06\_data\_structures, 07\_data\_pipeline |

### `modality` Values

| Value | Full Name |
|-------|-----------|
| `tomography` | X-ray Tomography / Computed Tomography |
| `xrf_microscopy` | X-ray Fluorescence Microscopy |
| `ptychography` | Ptychography / Coherent Diffraction Imaging |
| `spectroscopy` | X-ray Absorption Spectroscopy (XAS/XANES/EXAFS) |
| `crystallography` | X-ray Crystallography / Macromolecular Crystallography |
| `scattering` | Small/Wide-Angle X-ray Scattering (SAXS/WAXS) |
| `cross_cutting` | Applies to multiple modalities |

### `beamline` Values

| Value | Sector | Primary Technique |
|-------|--------|-------------------|
| `2-BM` | 2-BM-A,B | Tomography |
| `2-ID-D` | 2-ID-D | Ptychography, XRF nanoprobe |
| `2-ID-E` | 2-ID-E | XRF microprobe |
| `3-ID` | 3-ID | Nuclear resonant scattering |
| `5-BM` | 5-BM-D | XAS, XANES |
| `7-BM` | 7-BM-B | Tomography (fast) |
| `9-BM` | 9-BM-B,C | XAS |
| `9-ID` | 9-ID-B,C | USAXS/SAXS/WAXS |
| `11-BM` | 11-BM-B | Powder diffraction |
| `11-ID-B` | 11-ID-B | High-energy XRD |
| `11-ID-C` | 11-ID-C | High-energy XRD |
| `12-ID` | 12-ID-B,C,D | SAXS/WAXS |
| `17-BM` | 17-BM-B | XAS |
| `20-BM` | 20-BM-B | XAS |
| `20-ID` | 20-ID-B,C | XAS microprobe |
| `26-ID` | 26-ID-C | Nanoprobe, ptychography |
| `32-ID` | 32-ID-B,C | Tomography (high-resolution) |
| `34-ID` | 34-ID-C | Ptychography, Bragg CDI |

### Validation Rules

1. `cluster` must be one of: `discover`, `explore`, `build`.
2. `modality` must be one of the values listed above, or `null`.
3. Each entry in `beamline` must be one of the values listed above.
4. Unknown values generate a **warning** at runtime, not an error.
5. The explorer logs warnings to the console but continues rendering.

## Migration Note

Existing notes do **not** have YAML frontmatter. They will be progressively annotated over time. The explorer MUST handle notes without frontmatter gracefully:

- **Title:** Inferred from the filename (replace `_` with spaces, title-case).
- **Cluster:** Inferred from the parent folder using the IA mapping in `explorer/lib/ia.py`.
- **Tags:** Empty list.
- **Modality/Beamline:** `null`.
- **Metadata panel:** Shows only the inferred cluster; other sections hidden.

This graceful degradation ensures the explorer remains functional during the migration period. Notes with partial frontmatter (e.g., only `title` and `tags`) are also supported — missing fields use the default/inferred values.
