---
doc_id: IMPL-002
title: "GitHub Pages ↔ Streamlit Explorer sync contract"
status: accepted
version: 0.1.0
last_updated: 2026-04-21
supersedes: null
related: [ADR-007, ADR-004, IA-001, DS-001, PRD-001]
---

# GitHub Pages ↔ Streamlit Explorer sync contract

## Purpose

The Streamlit app under `explorer/` is the canonical interactive client over
the note folders. It requires a Python runtime to serve, so we additionally
publish a **static HTML mirror** of that same app to GitHub Pages. The mirror
exists so that readers without a local Python environment can still browse
the same content through the same information architecture.

This document is the single source of truth for how the two stay aligned.

## Hard rule

> **Every change that ships in `explorer/` MUST be reflected in GitHub Pages
> on the next push to `main`.** There is no manual Pages edit step — the
> mirror is regenerated automatically by CI.

Concretely, this means:

1. No feature, layout, or data shape lives only in Streamlit. If a page
   exists in `explorer/pages/`, it must have a counterpart in the static
   site.
2. No hand-edited HTML is committed under `site/` (the generator output is
   .gitignored).
3. The generator (`scripts/build_static_site.py`) **reuses** the Streamlit
   code path for reading notes (`explorer/lib/notes.py`) and for the IA
   mapping (`explorer/lib/ia.py`). If those contracts change, both
   surfaces change together.

## How it works

```
                       ┌────────────────────────────────────┐
                       │  01_program_overview/ … 09_noise_  │
                       │  catalog/   (source of truth)      │
                       └──────────────┬─────────────────────┘
                                      │  (read at runtime)
                ┌─────────────────────┴────────────────────┐
                │                                          │
                ▼                                          ▼
   ┌─────────────────────────┐            ┌───────────────────────────┐
   │ explorer/  (Streamlit)  │            │ scripts/build_static_site │
   │  app.py                 │   shares   │  imports explorer/lib/    │
   │  pages/ 1_Discover.py   │◀──────────▶│  writes HTML to site/     │
   │  pages/ 2_Explore.py    │   lib/     │                           │
   │  pages/ 3_Build.py      │            └─────────────┬─────────────┘
   │  components/ card, note │                          │
   │  assets/styles.css      │◀── same CSS  ────────────┘
   └───────────┬─────────────┘                          ▼
               │                            ┌────────────────────────┐
               │ streamlit run              │ .github/workflows/     │
               ▼                            │ pages.yml → GitHub     │
         localhost:8501                     │ Pages                  │
                                            └────────────────────────┘
```

The generator never duplicates note content; it only transforms the same
`Note` objects the Streamlit pages render into static HTML.

## Sync requirements when changing Streamlit

When a PR touches any of the following, the same PR must keep Pages
equivalent. The CI build of `.github/workflows/pages.yml` will surface any
divergence by failing, but reviewers should also check manually:

| You changed…                              | You must also…                                              |
|-------------------------------------------|-------------------------------------------------------------|
| `explorer/lib/ia.py` (IA mapping)         | Nothing — the generator imports it. Verify cluster pages.  |
| `explorer/lib/notes.py` (parser)          | Nothing — the generator imports it. Verify note pages.     |
| `explorer/assets/styles.css`              | Nothing — the generator inlines it into `assets/styles.css`.|
| `explorer/components/card.py`             | Update `_card_html()` in `scripts/build_static_site.py`.    |
| `explorer/components/header.py`           | Update `_header_html()` in `scripts/build_static_site.py`.  |
| `explorer/components/footer.py`           | Update `_footer_html()` in `scripts/build_static_site.py`.  |
| `explorer/components/breadcrumb.py`       | Update `_breadcrumb_html()` in `scripts/build_static_site.py`.|
| `explorer/components/note_view.py`        | Update `_render_note()` + `_metadata_panel_html()`.         |
| `explorer/app.py` (landing hero/grid)     | Update `_render_landing()` in `scripts/build_static_site.py`.|
| `explorer/pages/1_Discover.py`            | Update `_render_cluster("discover", …)`.                    |
| `explorer/pages/2_Explore.py`             | Update `_render_cluster("explore", …, group_by_folder=True)`.|
| `explorer/pages/3_Build.py`               | Update `_render_cluster("build", …, group_by_folder=True)`. |
| A new top-level page in `explorer/pages/` | Add a `_render_*()` function and call it from `build()`.    |

## Local verification

Before merging a Streamlit change, regenerate the site locally:

```bash
pip install -r scripts/requirements.txt
python scripts/build_static_site.py --out site
python -m http.server --directory site 8080
# open http://localhost:8080
```

The `site/` directory is git-ignored; do not commit it.

## Deployment

`.github/workflows/pages.yml` runs on every push to `main` that touches any
of the sync-relevant paths (note folders, `explorer/**`, the generator,
wireframes, or the workflow itself). The workflow:

1. Installs `scripts/requirements.txt`.
2. Runs `python scripts/build_static_site.py --out site`.
3. Uploads `site/` as the Pages artifact and deploys it.

## Wireframes

Static design mockups under `docs/02_design/wireframes/html/` are copied to
`site/wireframes/` during the build so the existing wireframe preview URLs
are preserved (see Invariant #5 — versioned wireframe filenames). The
wireframe index is also regenerated at `site/wireframes/index.html`.
