---
doc_id: TST-001
title: "Test Plan"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [PRD-001, IMP-002, NFR-001]
---

# Test Plan

## Test Pyramid

### Unit Tests (Automated)

| Area | What is tested | Tool | Location |
|------|---------------|------|----------|
| Note parser | Frontmatter extraction, graceful degrade, title inference | pytest | `explorer/tests/test_notes.py` |
| Frontmatter validator | Controlled vocabulary validation, warning on invalid values | pytest | `explorer/tests/test_notes.py` |
| IA mapping | Exhaustive and disjoint folder-to-cluster mapping | pytest | `explorer/tests/test_ia.py` |
| Component smoke | Each `render_*` function runs without error, produces output | pytest | `explorer/tests/test_components.py` |

### Integration Tests (Automated)

| Area | What is tested | Tool | Location |
|------|---------------|------|----------|
| Page rendering | Each Streamlit page loads without error with real note data | pytest + Streamlit testing | `explorer/tests/test_pages.py` |
| Note loading | Full corpus loads within performance budget (< 5s) | pytest + timing | `explorer/tests/test_notes.py` |

### Manual Tests (Pre-release)

| Area | What is tested | Tool |
|------|---------------|------|
| Visual QA | Layout matches wireframes, colors match design tokens | Browser inspection |
| Accessibility | WCAG 2.1 AA checklist (see `accessibility_audit.md`) | axe DevTools, Lighthouse |
| Keyboard navigation | All interactive elements reachable via Tab/Enter/Space | Manual |
| Responsive | Layout at 360px, 768px, 1200px+ breakpoints | Browser DevTools |
| Cross-browser | Chrome, Firefox, Safari, Edge | Manual |

## Tooling

| Tool | Purpose |
|------|---------|
| **pytest** | Unit and integration test runner |
| **pytest-cov** | Coverage reporting |
| **Streamlit testing utilities** | `st.testing.v1.AppTest` for page-level tests |
| **axe DevTools** | Automated accessibility checks |
| **Lighthouse** | Performance and accessibility scoring |

## Coverage Target

- **Unit tests:** ≥ 80% line coverage on `explorer/lib/`.
- **Component tests:** Every public `render_*` function has at least one smoke test.
- **Integration tests:** Every Streamlit page file has a load test.

## What is Explicitly Not Tested

- **Note content correctness.** The explorer renders notes as-is; content accuracy is the author's responsibility.
- **Streamlit framework internals.** We test our code, not Streamlit's rendering engine.
- **Network behavior.** The explorer makes no network requests at runtime.
- **Deployment infrastructure.** Streamlit Cloud deployment is out of scope for automated tests.
