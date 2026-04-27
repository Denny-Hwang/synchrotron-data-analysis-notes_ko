---
doc_id: PRD-001
title: "Product Requirements Document — eBERlight Explorer"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [VIS-001, PER-001, RMP-001, UST-001, NFR-001]
---

# Product Requirements Document — eBERlight Explorer

## Background

The synchrotron-data-analysis-notes repository contains 200+ markdown files documenting X-ray modalities, AI/ML methods, tools, publications, data structures, and pipeline architecture for the DOE BER program at Argonne's Advanced Photon Source. The existing `eberlight-explorer/` Streamlit app provides basic browsing but lacks task-oriented navigation, ANL visual branding, and accessibility compliance. eBERlight Explorer is a redesigned interactive portal that reads the note folders at runtime and presents them through a structured information architecture.

## Users

Three primary personas (see [PER-001](../00_product/personas.md)):

1. **Beamline Scientist** — finds AI/ML methods by modality and beamline.
2. **New BER User** — follows guided learning paths from program overview to analysis.
3. **Computational Scientist** — locates tools, code, pipeline docs, and data schemas.

## Scope

eBERlight Explorer covers:

- A Streamlit-based web application served locally or via Streamlit Community Cloud.
- Runtime reading and rendering of the 8+ note folders (single source of truth).
- Three task-oriented cluster landing pages with card-based navigation.
- 4-zoom navigation model with breadcrumb and zoom indicator.
- Tag-based filtering by modality, beamline, and method category.
- Full-text search across all notes.
- ANL/APS-aligned visual design with WCAG 2.1 AA compliance.

## Out of Scope

- Raw data hosting or processing.
- User authentication, accounts, or analytics.
- Replacing the official eberlight.aps.anl.gov website.
- Writing or modifying note content (read-only).
- Deployment infrastructure beyond local and Streamlit Cloud.

## Functional Requirements

| ID | Requirement | Persona | Phase |
|----|------------|---------|-------|
| FR-001 | The landing page SHALL display a hero section, search bar, and 3 cluster cards. | All | B |
| FR-002 | Each cluster card SHALL link to its cluster landing page. | All | B |
| FR-003 | Cluster landing pages SHALL list all notes belonging to that cluster as cards with title, summary, and tags. | All | B |
| FR-004 | Clicking a note card SHALL navigate to a detail view rendering the note's markdown content. | All | B |
| FR-005 | The detail view SHALL display a breadcrumb reflecting the full navigation path. | All | A |
| FR-006 | The detail view SHALL show a metadata panel with beamline, modality, and related-publication tags when available. | A, C | C |
| FR-007 | Tags SHALL be clickable, filtering the cluster page to matching notes. | A, C | C |
| FR-008 | A zoom indicator SHALL show the user's current position in the 4-level IA hierarchy (Map → Section → Topic → Source). | All | C |
| FR-009 | A search bar SHALL be available on every page, returning results ranked by relevance with title and snippet. | All | D |
| FR-010 | The DOE acknowledgment footer (Contract No. DE-AC02-06CH11357) SHALL appear on every page. | All | A |
| FR-011 | The header SHALL display a site title and top navigation with links to the 3 clusters. | All | A |
| FR-012 | Notes without YAML frontmatter SHALL still load, using the filename as the title and empty tags. | All | B |
| FR-013 | Code blocks in notes SHALL be rendered with syntax highlighting using a theme consistent with the design system. | C | B |
| FR-014 | The application SHALL load the landing page with TTI < 2 seconds on a cached run. | All | D |
| FR-015 | All pages SHALL be navigable via keyboard only. | All | D |
| FR-016 | Color contrast ratios SHALL meet WCAG 2.1 AA (≥ 4.5:1 for normal text, ≥ 3:1 for large text). | All | A |

## UX Principles

1. **Task-first navigation.** Users enter through intent, not file structure. See [DS-001](../02_design/design_system.md).
2. **Progressive disclosure.** Surface summaries first; details on demand.
3. **Consistency.** Use the design system tokens uniformly. No one-off styles.
4. **Accessibility by default.** Every component is keyboard-navigable and screen-reader-compatible.
5. **Content fidelity.** The explorer renders notes exactly as authored. No silent reformatting.

## Dependencies

- Python 3.10+ and Streamlit 1.30+.
- Markdown rendering library (Python-Markdown or markdown-it-py).
- Pygments for code highlighting.
- Note folders must be present at runtime (no remote fetch).

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Streamlit CSS customization is limited | Design system may not be fully expressible | Use `st.markdown(unsafe_allow_html=True)` for custom components; accept trade-offs per ADR-001 |
| Notes lack YAML frontmatter | Tag filtering and metadata panel have no data | Graceful degradation; progressive annotation plan in data_contracts.md |
| Large note corpus slows search | TTI target missed | Implement caching; index notes at startup |
| APS-U data scale growth | Repository may outgrow local serving | Out of scope for v1; re-evaluate at Phase E |
