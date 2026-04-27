---
doc_id: TST-002
title: "Accessibility Audit Checklist"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [NFR-001, DS-001, PRD-001]
---

# Accessibility Audit Checklist

## Target

WCAG 2.1 Level AA conformance, adapted for the Streamlit framework.

## Audit Tools

| Tool | Purpose | When |
|------|---------|------|
| **axe DevTools** (browser extension) | Automated WCAG checks | Every PR with UI changes |
| **Lighthouse** (Chrome DevTools) | Accessibility score + specific issues | Before every explorer release |
| **Manual keyboard test** | Tab order, focus management, skip links | Before every explorer release |
| **Screen reader** (NVDA or VoiceOver) | Real assistive technology verification | Before major releases |

## Checklist

### Perceivable

| # | Check | WCAG | Status | Notes |
|---|-------|------|--------|-------|
| 1 | All images have descriptive `alt` text | 1.1.1 | pending | Logo, diagrams, code screenshots |
| 2 | Color is not the only means of conveying information | 1.4.1 | pending | Tags have text labels, not just color |
| 3 | Text contrast ≥ 4.5:1 (normal) / 3:1 (large) | 1.4.3 | pending | Validate all color token combos |
| 4 | UI component contrast ≥ 3:1 | 1.4.11 | pending | Buttons, inputs, badges |
| 5 | Content readable at 200% zoom | 1.4.4 | pending | No horizontal scroll at 200% |
| 6 | Text spacing adjustable without loss of content | 1.4.12 | pending | Line height, letter spacing |

### Operable

| # | Check | WCAG | Status | Notes |
|---|-------|------|--------|-------|
| 7 | All functionality available via keyboard | 2.1.1 | pending | Tab, Enter, Space, Escape |
| 8 | No keyboard traps | 2.1.2 | pending | Can Tab out of all components |
| 9 | Focus order is logical | 2.4.3 | pending | Top-to-bottom, left-to-right |
| 10 | Focus indicator visible | 2.4.7 | pending | 2px solid outline on all focusable elements |
| 11 | Page titles are descriptive | 2.4.2 | pending | Each page has unique `<title>` |
| 12 | Link purpose is clear from text | 2.4.4 | pending | No "click here" links |
| 13 | No content flashes > 3 times/second | 2.3.1 | pending | No animations by default |

### Understandable

| # | Check | WCAG | Status | Notes |
|---|-------|------|--------|-------|
| 14 | Language of page declared | 3.1.1 | pending | `lang="en"` on HTML element |
| 15 | Consistent navigation across pages | 3.2.3 | pending | Header, footer, breadcrumb on every page |
| 16 | Error identification and suggestion | 3.3.1, 3.3.3 | pending | Search: "No results" message |

### Robust

| # | Check | WCAG | Status | Notes |
|---|-------|------|--------|-------|
| 17 | Valid HTML | 4.1.1 | pending | No duplicate IDs, proper nesting |
| 18 | ARIA roles and properties correct | 4.1.2 | pending | Breadcrumb `nav`, footer `footer`, panels `aside` |

## Streamlit-Specific Considerations

- Streamlit injects its own HTML structure. Custom components via `st.markdown(unsafe_allow_html=True)` must include proper semantic HTML and ARIA attributes.
- Streamlit's sidebar and page navigation have their own keyboard behavior. Test that custom components don't interfere.
- `st.tabs()` provides built-in keyboard support (arrow keys). Verify it works with screen readers.

## Audit Cadence

- **Before every explorer release**: Run axe DevTools + Lighthouse. Fix all Critical and Serious issues.
- **Before major releases (x.0.0)**: Full manual keyboard + screen reader test.
- **On every PR with UI changes**: Automated axe check (can be added to CI).

## Remediation SLA

| Severity | Fix deadline |
|----------|-------------|
| Critical (blocks access) | Before release |
| Serious (major barrier) | Before release |
| Moderate (inconvenience) | Next release |
| Minor (cosmetic) | Backlog |
