---
doc_id: WF-003
title: "Wireframe — Tool Detail Page v0.1"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [IA-001, DS-001, PRD-001, FR-004]
---

# Wireframe — Tool Detail Page v0.1

## Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│  HEADER                                                 │
│  [Logo]  eBERlight Explorer    Discover | Explore | Build│
├─────────────────────────────────────────────────────────┤
│  BREADCRUMB: Home > Build and Compute > Tools > TomocuPy│
│  ZOOM: [●] Map  [●] Section  [●] Topic  [●] Source     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  SUMMARY CARD                                    │    │
│  │  TomocuPy                              [H1]      │    │
│  │  GPU-accelerated tomographic reconstruction      │    │
│  │                                                  │    │
│  │  [tomography] [GPU] [reconstruction] [CUDA]      │    │
│  │                                                  │    │
│  │  Used at: [2-BM] [7-BM] [32-ID]                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────┐  ┌──────────┐  │
│  │  TABS                               │  │METADATA  │  │
│  │  [Overview] [Code] [Run] [Citation]  │  │PANEL     │  │
│  │                                      │  │          │  │
│  │  ┌──────────────────────────────┐    │  │Beamlines:│  │
│  │  │                              │    │  │ 2-BM     │  │
│  │  │  TAB CONTENT                 │    │  │ 7-BM     │  │
│  │  │                              │    │  │ 32-ID    │  │
│  │  │  (Markdown rendered from     │    │  │          │  │
│  │  │   the note file)             │    │  │Modality: │  │
│  │  │                              │    │  │ Tomo     │  │
│  │  │  ## Architecture             │    │  │          │  │
│  │  │  ...                         │    │  │Related:  │  │
│  │  │                              │    │  │ TomoPy   │  │
│  │  │  ## Pros / Cons              │    │  │ TomoGAN  │  │
│  │  │  ...                         │    │  │          │  │
│  │  │                              │    │  │Pubs:     │  │
│  │  │  ```python                   │    │  │ review_  │  │
│  │  │  import tomocupy             │    │  │ tomocupy │  │
│  │  │  ```                         │    │  │          │  │
│  │  └──────────────────────────────┘    │  │          │  │
│  └─────────────────────────────────────┘  └──────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  FOOTER                                                 │
└─────────────────────────────────────────────────────────┘
```

## Annotations

### Summary Card
- **Title:** H1 (36px, `--color-text`).
- **Description:** First line or frontmatter `description` field.
- **Tags:** Row of `TagChip` components from frontmatter `tags`.
- **"Used at" badges:** Beamline `Badge` components with `--color-primary` bg. Only shown if `beamline` field exists in frontmatter.

### Tabs
- **Overview:** Default tab. Renders the full note markdown.
- **Code:** Code blocks and code-related sections extracted from the note. Shows inline code with syntax highlighting.
- **Run:** Installation and reproduction guide sections (if present in note).
- **Citation:** BibTeX entry and related publication links.
- Tabs implemented via `st.tabs()`. Each tab renders a filtered view of the same source note.

### Metadata Panel (Right Side)
- Width: 280px, sticky.
- Sections:
  - **Beamlines:** List of beamline badges.
  - **Modality:** Modality tag (clickable, links to Explore cluster filtered).
  - **Related Tools:** Links to other tool notes.
  - **Related Publications:** Links to publication review notes.
- Empty sections are hidden.
- On mobile: panel moves below the tab content.

### Code Blocks
- Rendered per `CodeBlock` component in design system.
- Dark theme, JetBrains Mono font, language badge.
- Copy button on hover.

## Responsive Behavior

| Breakpoint | Layout |
|------------|--------|
| Desktop (1200px+) | Tabs (calc(100% - 312px)) + metadata panel (280px) |
| Tablet (768px–1199px) | Tabs full width, metadata panel below |
| Mobile (< 768px) | Tabs full width, metadata panel below, compact |

## See Also

- HTML mockup: [`wireframes/html/tool_v0.1.html`](html/tool_v0.1.html)
