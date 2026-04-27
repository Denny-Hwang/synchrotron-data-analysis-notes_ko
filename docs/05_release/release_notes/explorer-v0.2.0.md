---
doc_id: REL-E020
title: "Release Notes — explorer-v0.2.0"
status: draft
version: 0.2.0
last_updated: 2026-04-08
supersedes: null
related: [RMP-001, IA-001, ADR-002, ADR-004, DC-001]
---

# Release Notes — explorer-v0.2.0

**Phase B: IA, Cluster Pages, Note Rendering**

## Summary

Introduces the 3-cluster information architecture, runtime note loading
from the source-of-truth folders, and cluster landing pages with card
navigation.

## What's New

- **IA mapping** (`lib/ia.py`): 9 folders → 3 clusters (Discover/Explore/Build) per ADR-004, defined as a single constant.
- **Note loader** (`lib/notes.py`): Walks note folders, parses YAML frontmatter, validates controlled vocabularies, gracefully degrades for notes without frontmatter.
- **3 cluster pages**: `1_Discover.py`, `2_Explore.py`, `3_Build.py` — each lists notes from its cluster as cards grouped by folder.
- **Card component** (`components/card.py`): Displays note title, summary, and tags per DS-001.
- **Note view component** (`components/note_view.py`): Full note rendering with markdown, code highlighting, and metadata panel.
- **Updated landing page**: Hero + 3 cluster cards with cluster colors and descriptions.
- **Comprehensive tests**: 16 tests covering components, IA mapping, note parsing, vocabulary validation, and real repo loading.

## Files Added/Modified

| File | Change |
|------|--------|
| `explorer/lib/ia.py` | NEW — IA mapping constant and helpers |
| `explorer/lib/notes.py` | NEW — Note loader with frontmatter parsing |
| `explorer/components/card.py` | NEW — Card component |
| `explorer/components/note_view.py` | NEW — Note detail view |
| `explorer/pages/1_Discover.py` | NEW — Discover cluster page |
| `explorer/pages/2_Explore.py` | NEW — Explore cluster page |
| `explorer/pages/3_Build.py` | NEW — Build cluster page |
| `explorer/app.py` | MODIFIED — Landing with cluster cards |
| `explorer/tests/test_ia.py` | NEW — 6 IA mapping tests |
| `explorer/tests/test_notes.py` | NEW — 6 note parser tests |

## Requirements Covered

- FR-001: Landing page with hero and 3 cluster cards
- FR-002: Cluster cards link to cluster pages
- FR-003: Cluster pages list notes as cards
- FR-004: Note detail view renders markdown
- FR-012: Notes without frontmatter load gracefully
- FR-013: Code blocks with syntax highlighting
