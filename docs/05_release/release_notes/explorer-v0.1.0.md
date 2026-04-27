---
doc_id: REL-E010
title: "Release Notes — explorer-v0.1.0"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [RMP-001, ADR-001, ADR-005, DS-001]
---

# Release Notes — explorer-v0.1.0

**Phase A: Theme + Header + Breadcrumb + Footer**

## Summary

First release of the redesigned eBERlight Explorer. Establishes the visual
foundation with ANL-aligned design tokens, DOE acknowledgment footer,
breadcrumb navigation, and a placeholder landing page.

## What's New

- **Streamlit theme** configured with ANL-aligned color tokens (`#0033A0` primary, `#F5F5F5` surface, `#1A1A1A` text).
- **Header component** with logo placeholder, site title, and disabled top navigation stubs for 3 clusters.
- **Breadcrumb component** rendering linked navigation per IA-001.
- **Footer component** with DOE Contract No. DE-AC02-06CH11357 acknowledgment, eBERlight program reference, and git-based last-updated timestamp.
- **Custom CSS** (`assets/styles.css`) with component-level classes for header, breadcrumb, footer, card, and tag.
- **Placeholder landing page** with "Hello, eBERlight" hero.
- **Smoke tests** for all 3 components (header, breadcrumb, footer).

## Files Added

| File | Purpose |
|------|---------|
| `explorer/app.py` | Streamlit entry point |
| `explorer/.streamlit/config.toml` | Theme configuration |
| `explorer/components/header.py` | Header component |
| `explorer/components/breadcrumb.py` | Breadcrumb component |
| `explorer/components/footer.py` | Footer component |
| `explorer/components/__init__.py` | Package init |
| `explorer/assets/styles.css` | Custom CSS |
| `explorer/lib/__init__.py` | Lib package init |
| `explorer/requirements.txt` | Python dependencies |
| `explorer/tests/test_components.py` | Component smoke tests |

## Requirements Covered

- FR-005: Breadcrumb on detail views
- FR-010: DOE footer on every page
- FR-011: Header with site title and top navigation
- FR-016: Color contrast meets WCAG 2.1 AA
