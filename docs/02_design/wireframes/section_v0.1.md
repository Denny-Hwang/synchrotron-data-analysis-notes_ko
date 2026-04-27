---
doc_id: WF-002
title: "Wireframe — Section Page v0.1"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [IA-001, DS-001, PRD-001, FR-003]
---

# Wireframe — Section Page v0.1

## Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│  HEADER                                                 │
│  [Logo]  eBERlight Explorer    Discover | Explore | Build│
├─────────────────────────────────────────────────────────┤
│  BREADCRUMB: Home > Explore the Science                 │
│  ZOOM: [●] Map  [●] Section  [ ] Topic  [ ] Source     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Explore the Science                         [H1]       │
│  Browse modalities, AI/ML methods,           [Subtitle] │
│  publications, and noise handling                       │
│                                                         │
│  FILTERS:  [All] [Modality ▾] [Method ▾] [Beamline ▾]  │
│                                                         │
│  ┌──────────────────────────────┐                       │
│  │ STICKY TOC (Left)           │  MAIN CONTENT          │
│  │                             │                        │
│  │ ◆ X-ray Modalities (6)     │  ┌──────────────────┐  │
│  │ ◆ AI/ML Methods (14)       │  │ Card: Tomography │  │
│  │ ◆ Publications (14)        │  │ tags: tomo, ...  │  │
│  │ ◆ Noise Catalog (29)       │  └──────────────────┘  │
│  │                             │  ┌──────────────────┐  │
│  │                             │  │ Card: XRF Micro  │  │
│  │                             │  │ tags: xrf, ...   │  │
│  │                             │  └──────────────────┘  │
│  │                             │  ┌──────────────────┐  │
│  │                             │  │ Card: TomoGAN    │  │
│  │                             │  │ tags: denoise,...│  │
│  │                             │  └──────────────────┘  │
│  └──────────────────────────────┘  ...                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  FOOTER                                                 │
└─────────────────────────────────────────────────────────┘
```

## Annotations

### Breadcrumb
- Shows: Home > [Cluster Name].
- "Home" links to landing page. Current cluster name is bold, not linked.
- Rendered by `components/breadcrumb.py`.

### Zoom Indicator
- Shows 4 steps. "Section" (L1) is the active level.
- "Map" (L0) is shown as completed (filled).
- "Topic" and "Source" are upcoming (outlined).

### Sticky TOC (Left Sidebar)
- Lists the source folders within this cluster with note counts.
- Clicking a folder heading scrolls to or filters to that category.
- Sticky on desktop (position: sticky, top: 80px).
- Hidden on mobile — replaced by a dropdown.

### Filters
- Tag-based filtering: Modality, Method category, Beamline.
- "All" resets filters.
- Implemented as `TagChip` components with `aria-pressed` state.

### Main Content
- Grid of `Card` components (2 columns on desktop, 1 on mobile).
- Each card: title, 2-line summary, tag chips.
- Cards sorted by folder, then alphabetically.

### Right-Side Metadata Panel
- **Not shown on section pages.** Only appears on note detail views (L3).

## Responsive Behavior

| Breakpoint | Layout |
|------------|--------|
| Desktop (1200px+) | Left TOC (240px) + main content (2-col cards) |
| Tablet (768px–1199px) | Left TOC (200px) + main content (1-col cards) |
| Mobile (< 768px) | TOC becomes dropdown, full-width single-column cards |

## See Also

- HTML mockup: [`wireframes/html/section_v0.1.html`](html/section_v0.1.html)
