---
doc_id: CON-001
title: "Contributing Guide"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [IMP-002, ADR-003, ADR-006]
---

# Contributing Guide

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<scope>-<description>` | `feat/explorer-phase-b` |
| Bug fix | `fix/<scope>-<description>` | `fix/explorer-breadcrumb-links` |
| Documentation | `docs/<description>` | `docs/product-layer-v0.1` |
| Chore | `chore/<description>` | `chore/bootstrap-docs-and-explorer` |

## PR Flow

1. Create a branch from `main` following the naming convention.
2. Make changes, ensuring all commits follow Conventional Commits (see `coding_standards.md`).
3. Run linters and tests: `ruff check explorer/ && black --check explorer/ && pytest explorer/tests/`.
4. Open a PR with:
   - Title following Conventional Commits format.
   - Description referencing the requirement (FR-*, US-*, ADR-*).
   - Completed PR checklist (see `coding_standards.md`).
5. Address review feedback.
6. Merge via squash-and-merge to keep `main` history clean.

## How to Propose a New ADR

1. Create a new file in `docs/02_design/decisions/` named `ADR-NNN.md` where NNN is the next sequential number.
2. Use the ADR template (see any existing ADR for the format).
3. Set `status: proposed` in frontmatter.
4. Open a PR titled `docs: propose ADR-NNN <title>`.
5. After review and approval, update status to `accepted`.
6. Update `docs/README.md` with the new ADR entry.

## How to Add a Note

1. Choose the appropriate folder (01–09) based on the content topic.
2. Create the markdown file with YAML frontmatter:

```yaml
---
title: "Your Note Title"
cluster: explore  # discover | explore | build
tags: [relevant, tags]
modality: tomography  # or null if not modality-specific
beamline: [2-BM]  # or null if not beamline-specific
---
```

3. Use the controlled vocabularies from `docs/03_implementation/data_contracts.md`.
4. Frontmatter is required for new notes going forward.
5. Existing notes without frontmatter will continue to work (graceful degradation).

## Versioning

This repository uses two independent SemVer streams (see ADR-006):

- **`notes-vX.Y.Z`**: Version bumped when notes are added or substantially revised.
- **`explorer-vX.Y.Z`**: Version bumped per feature phase delivery.

For feature PRs, update both:
- `docs/05_release/release_notes/<stream>-vX.Y.Z.md`
- `CHANGELOG.md`
