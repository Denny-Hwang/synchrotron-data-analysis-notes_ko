---
doc_id: IMP-001
title: "Developer Setup Guide"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [PRD-001, IMP-002, ADR-001]
---

# Developer Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | 3.11 recommended |
| pip or uv | Latest | `uv` preferred for faster installs |
| Git | 2.30+ | For version control |
| Browser | Chrome/Firefox/Safari 90+ | For viewing the explorer |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Denny-Hwang/synchrotron-data-analysis-notes.git
cd synchrotron-data-analysis-notes

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r explorer/requirements.txt

# 4. Run the explorer
streamlit run explorer/app.py
```

The app opens at `http://localhost:8501`.

### Using uv (faster alternative)

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r explorer/requirements.txt
streamlit run explorer/app.py
```

## Running Linters and Tests

```bash
# Lint with ruff
ruff check explorer/

# Format check with black
black --check explorer/

# Run tests
pytest explorer/tests/ -v
```

## Project Layout

```
explorer/
├── app.py              # Streamlit entry point
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Streamlit theme config
├── pages/              # Multi-page Streamlit pages
├── components/         # Reusable UI components
├── lib/                # Core logic (notes loader, IA mapping)
├── assets/
│   └── styles.css      # Custom CSS
└── tests/              # pytest test suite
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

Ensure you activated the virtual environment:
```bash
source .venv/bin/activate
```

### Streamlit shows a blank page

Check that you're running from the repository root:
```bash
cd synchrotron-data-analysis-notes
streamlit run explorer/app.py
```

### Port 8501 already in use

Kill the existing Streamlit process or use a different port:
```bash
streamlit run explorer/app.py --server.port 8502
```

### Notes not loading

The explorer reads from the 8 note folders at runtime. Ensure they exist in the repository root:
```bash
ls -d 0*/
```

### CSS not applying

Ensure `explorer/assets/styles.css` exists and is loaded in `app.py` via `st.markdown`.
