---
doc_id: WF-001
title: "Wireframe — Landing Page v0.1"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [IA-001, DS-001, PRD-001, FR-001]
---

# Wireframe — Landing Page v0.1

## Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│  HEADER                                                 │
│  [Logo]  eBERlight Explorer    Discover | Explore | Build│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              HERO SECTION                        │    │
│  │                                                  │    │
│  │  eBERlight Research Explorer                     │    │
│  │  Navigate synchrotron data analysis knowledge    │    │
│  │  at Argonne's Advanced Photon Source             │    │
│  │                                                  │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │  🔍  Search notes, methods, tools...     │    │    │
│  │  └──────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  DISCOVER   │  │  EXPLORE    │  │  BUILD       │     │
│  │  the Program│  │  the Science│  │  and Compute │     │
│  │             │  │             │  │              │     │
│  │ BER mission,│  │ 6 modality, │  │ 7 tools,    │     │
│  │ 15 beamlines│  │ 14 methods, │  │ data schemas│     │
│  │ facilities  │  │ publications│  │ pipeline     │     │
│  │             │  │             │  │              │     │
│  │  [Enter →]  │  │  [Enter →]  │  │  [Enter →]  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  LATEST ADDITIONS                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Note 1   │  │ Note 2   │  │ Note 3   │              │
│  │ tags...  │  │ tags...  │  │ tags...  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  FOOTER                                                 │
│  DOE acknowledgment · Contract No. DE-AC02-06CH11357    │
│  APS | eBERlight | Repository                           │
│  Last updated: YYYY-MM-DD                               │
└─────────────────────────────────────────────────────────┘
```

## Annotations

### Hero Section
- **Background:** `--color-surface` with subtle gradient to white.
- **Title:** H1 (36px, `--color-primary`).
- **Subtitle:** Body (16px, `--color-text-secondary`).
- **Search bar:** Full width within container, placeholder text "Search notes, methods, tools...". Phase D implementation.

### Cluster Cards (3)
- **Layout:** Equal-width row, flexbox with 24px gap.
- **Card style:** Per `Card` component in design system.
- **Cluster color:** Top border 4px in respective cluster color.
- **Content:** Cluster name (H3), 2-line description with key stats, "Enter →" link.
- **Responsive:** Stack vertically on mobile.

### Latest Additions
- **Content:** 3 most recently modified notes across all clusters.
- **Card style:** Compact card variant (title + tags, no summary).
- **Update logic:** Determined by git last-modified timestamp or frontmatter `last_updated`.

### Header
- Reference: `components/header.py`, design system `Header` section.

### Footer
- Reference: `components/footer.py`, design system `Footer` section.
- DOE acknowledgment text is mandatory on every page.

## Responsive Behavior

| Breakpoint | Layout |
|------------|--------|
| Desktop (1200px+) | 3 cluster cards in a row, hero centered |
| Tablet (768px–1199px) | 3 cluster cards in a row (narrower), hero centered |
| Mobile (< 768px) | Cluster cards stack vertically, search full width |

## See Also

- HTML mockup: [`wireframes/html/landing_v0.1.html`](html/landing_v0.1.html)
