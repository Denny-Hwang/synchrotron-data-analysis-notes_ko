---
doc_id: RMP-001
title: "12-Week Delivery Roadmap"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [VIS-001, PRD-001, PER-001]
---

# 12-Week Delivery Roadmap

## Overview

Five phases (A–E) over 12 weeks. Each phase produces a shippable increment.

| Phase | Theme | Duration | Weeks |
|-------|-------|----------|-------|
| A | Theme + Footer + Breadcrumb | 2 weeks | 1–2 |
| B | IA Restructure + Cluster Landing + Cards | 3 weeks | 3–5 |
| C | 4-Zoom Indicator + Metadata Panel + Tag System | 3 weeks | 6–8 |
| D | Search + Accessibility Audit + Responsive | 2 weeks | 9–10 |
| E | Interview Polish + User Testing Round 1 | 2 weeks | 11–12 |

---

## Phase A: Theme + Footer + Breadcrumb (Weeks 1–2)

### Goals

- Establish the visual foundation: ANL-aligned color tokens, typography, and spacing.
- Ship the DOE acknowledgment footer on every page.
- Implement breadcrumb navigation as the primary wayfinding affordance.

### Deliverables

- `explorer/.streamlit/config.toml` with design-system theme.
- `explorer/components/header.py`, `footer.py`, `breadcrumb.py`.
- `explorer/assets/styles.css` with component-level CSS.
- Smoke tests for all components.
- Release note: `explorer-v0.1.0`.

### Exit Criteria

- App runs locally with correct ANL color palette.
- DOE Contract No. DE-AC02-06CH11357 visible in footer on every page.
- Breadcrumb renders on every page with correct hierarchy.
- All smoke tests pass.

---

## Phase B: IA Restructure + Cluster Landing + Cards (Weeks 3–5)

### Goals

- Implement the 3-cluster information architecture (Discover / Explore / Build).
- Render note content from the 8 source-of-truth folders at runtime.
- Replace placeholder content with real cluster landing pages.

### Deliverables

- `explorer/lib/notes.py` — note loader with frontmatter parsing.
- `explorer/lib/ia.py` — folder-to-cluster mapping.
- Three cluster pages: `1_Discover.py`, `2_Explore.py`, `3_Build.py`.
- `explorer/components/card.py`, `note_view.py`.
- Landing page with hero + 3 cluster cards.
- Unit tests for note parsing, IA mapping.
- Release note: `explorer-v0.2.0`.

### Exit Criteria

- All 8 note folders are mapped to exactly one cluster.
- Notes without YAML frontmatter load gracefully (inferred title, empty tags).
- Cluster pages display cards with title, summary, and tags.
- Note detail view renders markdown with code highlighting.

---

## Phase C: 4-Zoom Indicator + Metadata Panel + Tag System (Weeks 6–8)

### Goals

- Implement the 4-zoom navigation model (Map → Section → Topic → Source).
- Add a metadata panel showing beamline, modality, and related publications.
- Ship a tag-based filtering system across cluster pages.

### Deliverables

- `explorer/components/zoom_indicator.py` — visual breadcrumb showing zoom level.
- `explorer/components/metadata_panel.py` — right-side panel on note views.
- `explorer/components/tag_chip.py` — clickable tag badges.
- Tag filtering on cluster landing pages.
- Release note: `explorer-v0.3.0`.

### Exit Criteria

- Zoom indicator correctly reflects the user's position in the IA tree.
- Metadata panel shows beamline, modality, and related-publication tags when present.
- Clicking a tag filters the current cluster page to matching notes.
- Tags use controlled vocabulary from `data_contracts.md`.

---

## Phase D: Search + Accessibility Audit + Responsive (Weeks 9–10)

### Goals

- Add full-text search across all notes.
- Pass a WCAG 2.1 AA accessibility audit.
- Ensure responsive layout at mobile, tablet, and desktop breakpoints.

### Deliverables

- Search component with instant results (title + snippet).
- Accessibility audit report (`docs/04_testing/accessibility_audit.md` updated).
- Responsive CSS for 360px, 768px, and 1200px+ breakpoints.
- Release note: `explorer-v0.4.0`.

### Exit Criteria

- Search returns relevant results within 500ms on cached data.
- Lighthouse accessibility score ≥ 90.
- All pages usable via keyboard navigation only.
- Layout does not break at any tested breakpoint.

---

## Phase E: Interview Polish + User Testing Round 1 (Weeks 11–12)

### Goals

- Polish visual details for stakeholder demo readiness.
- Conduct first round of user testing with 3–5 representative users.
- Triage and fix critical usability issues.

### Deliverables

- Visual polish pass: consistent spacing, hover states, transitions.
- User testing protocol and findings document.
- Bug fixes from user testing (P0/P1 only).
- Release note: `explorer-v0.5.0`.

### Exit Criteria

- At least 3 users complete a task scenario without assistance.
- No P0 bugs remaining.
- Stakeholder sign-off for continued development.
