---
doc_id: IMP-002
title: "Coding Standards"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [PRD-001, IMP-001, ADR-001]
---

# Coding Standards

## Python Style

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| **ruff** | Linting + import sorting | `pyproject.toml` or `ruff.toml` |
| **black** | Code formatting (88-char line width) | Default config |

Run before every commit:
```bash
ruff check explorer/ --fix
black explorer/
```

### Type Hints

Type hints are **required on all public functions**. Private functions (prefixed `_`) are encouraged but not required.

```python
# Good
def load_notes(root: Path) -> list[Note]:
    ...

# Good (private, hints optional)
def _parse_frontmatter(content: str) -> dict:
    ...
```

### Docstrings

Use **Google-style** docstrings on all public functions and classes:

```python
def render_breadcrumb(items: list[tuple[str, str | None]]) -> None:
    """Render a breadcrumb navigation bar.

    Renders an HTML breadcrumb via st.markdown with each item as a
    clickable link except the last (current page).

    Args:
        items: List of (label, href) tuples. If href is None, the
            item is rendered as plain text (current page).

    Ref:
        IA-001 (information_architecture.md) — Navigation rules.
    """
```

## File Layout (`explorer/`)

```
explorer/
├── app.py              # Entry point only — imports and page config
├── lib/                # Pure logic, no Streamlit imports
│   ├── notes.py        # Note loading, frontmatter parsing
│   └── ia.py           # IA mapping constant
├── components/         # Reusable UI components (st.markdown-based)
│   ├── breadcrumb.py
│   ├── footer.py
│   ├── header.py
│   ├── card.py
│   └── ...
├── pages/              # Streamlit multi-page files
│   ├── 1_Discover.py
│   ├── 2_Explore.py
│   └── 3_Build.py
├── assets/
│   └── styles.css
└── tests/
    ├── test_notes.py
    ├── test_ia.py
    └── test_components.py
```

### Rules

1. **`lib/` is framework-agnostic.** No `import streamlit` in `lib/` files. This allows unit testing without a Streamlit runtime.
2. **`components/` contains Streamlit-specific UI.** Each file exports one or more `render_*` functions.
3. **`pages/` files are thin.** They import from `lib/` and `components/`, compose the page, and call `render_*` functions.
4. **One component per file.** Exceptions: tightly coupled components (e.g., `tag_chip.py` may include `tag_filter()`).

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case.py` | `note_view.py` |
| Functions | `snake_case` | `render_breadcrumb()` |
| Classes | `PascalCase` | `Note`, `ClusterMapping` |
| Constants | `UPPER_SNAKE_CASE` | `FOLDER_TO_CLUSTER` |
| Streamlit pages | `N_Name.py` | `1_Discover.py` |

## Commit Message Convention

Follow **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature for users |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build, CI, tooling changes |

### Scopes

| Scope | Area |
|-------|------|
| `explorer` | Explorer application code |
| `notes` | Note content changes |
| `docs` | Documentation in `docs/` |

### Examples

```
feat(explorer): add breadcrumb component per IA-001
fix(explorer): handle notes without frontmatter gracefully
docs: update PRD with new functional requirement FR-017
chore: add ruff configuration to pyproject.toml
```

## PR Checklist

Every pull request must satisfy:

- [ ] Linked to a requirement (FR-*, US-*, ADR-*) in the PR description
- [ ] All new public functions have type hints and docstrings
- [ ] Tests pass (`pytest explorer/tests/ -v`)
- [ ] Lints pass (`ruff check explorer/ && black --check explorer/`)
- [ ] `docs/05_release/release_notes/` updated (for feature PRs)
- [ ] `CHANGELOG.md` updated (for feature PRs)
- [ ] No changes to note folders (unless explicitly intended)
