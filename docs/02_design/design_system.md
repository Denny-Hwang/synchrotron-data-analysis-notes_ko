---
doc_id: DS-001
title: "Design System — eBERlight Explorer"
status: draft
version: 0.1.0
last_updated: 2026-04-08
supersedes: null
related: [PRD-001, IA-001, ADR-005, NFR-001]
---

# Design System — eBERlight Explorer

## Color Tokens

### Primary Palette

| Token | Hex | Usage | WCAG Notes |
|-------|-----|-------|------------|
| `--color-primary` | `#0033A0` | Headers, primary buttons, links | 8.6:1 on white — passes AA & AAA |
| `--color-secondary` | `#00A3E0` | Accents, secondary buttons, cluster "Explore" | 3.1:1 on white — passes AA for large text only; use on dark bg for body text |
| `--color-accent` | `#F47B20` | Highlights, badges, cluster "Build" | 3.0:1 on white — large text only; pair with dark text |
| `--color-surface` | `#F5F5F5` | Page background, card backgrounds | N/A (background) |
| `--color-surface-alt` | `#FFFFFF` | Card surfaces, panels | N/A (background) |
| `--color-text` | `#1A1A1A` | Body text | 16.6:1 on white, 14.8:1 on #F5F5F5 — passes AA & AAA |
| `--color-text-secondary` | `#555555` | Captions, metadata | 7.5:1 on white — passes AA & AAA |
| `--color-border` | `#E0E0E0` | Card borders, dividers | Decorative only |
| `--color-success` | `#2E7D32` | Status badges (accepted) | 5.9:1 on white — passes AA |
| `--color-warning` | `#F57F17` | Status badges (proposed) | 3.0:1 on white — use with dark text |
| `--color-error` | `#C62828` | Validation errors | 7.1:1 on white — passes AA |

### Cluster Colors

| Cluster | Color | Token |
|---------|-------|-------|
| Discover the Program | `#0033A0` (primary) | `--color-cluster-discover` |
| Explore the Science | `#00A3E0` (secondary) | `--color-cluster-explore` |
| Build and Compute | `#F47B20` (accent) | `--color-cluster-build` |

## Typography

### Font Families

| Purpose | Font | Fallback | Weight |
|---------|------|----------|--------|
| Body text | Source Sans 3 | `system-ui, -apple-system, sans-serif` | 400 (regular), 600 (semibold) |
| Headings | Source Sans 3 | `system-ui, -apple-system, sans-serif` | 700 (bold) |
| Code | JetBrains Mono | `'Fira Code', 'Cascadia Code', monospace` | 400 |

### Type Scale

| Element | Size (px) | Line Height | Weight | Margin Bottom |
|---------|-----------|-------------|--------|---------------|
| H1 | 36 | 1.2 | 700 | 24px |
| H2 | 28 | 1.3 | 700 | 20px |
| H3 | 22 | 1.3 | 700 | 16px |
| H4 | 18 | 1.4 | 600 | 12px |
| H5 | 16 | 1.4 | 600 | 8px |
| H6 | 14 | 1.4 | 600 | 8px |
| Body | 16 | 1.6 | 400 | 8px |
| Caption | 13 | 1.4 | 400 | 4px |
| Code (inline) | 14 | 1.4 | 400 | 0 |
| Code (block) | 14 | 1.5 | 400 | 16px |

## Spacing

- **Base unit:** 8px.
- **Spacing scale:** 4, 8, 12, 16, 24, 32, 48, 64px.
- **Container max-width:** 1200px, centered with `auto` horizontal margins.
- **Card padding:** 24px.
- **Section gap:** 32px.
- **Page margin (mobile):** 16px horizontal.
- **Page margin (desktop):** 48px horizontal (within container).

## Components

### Card

**Purpose:** Primary navigation element on cluster pages. Represents a note or a category.

**Anatomy:**
- Container (border, border-radius 8px, padding 24px)
- Title (H4, `--color-text`)
- Summary (Body, `--color-text-secondary`, max 2 lines with ellipsis)
- Tags (row of TagChip components)
- Hover state: subtle shadow elevation

**States:**
- Default: `--color-surface-alt` background, `--color-border` border
- Hover: `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- Focus: 2px solid `--color-primary` outline

**Accessibility:** Entire card is a clickable link. Focus ring visible on keyboard navigation. Card title serves as accessible name.

**Do:** Use cards for navigable content items. Keep summaries under 2 lines.
**Don't:** Nest interactive elements inside cards. Use cards for non-navigable static content.

### Badge

**Purpose:** Visual label for status, cluster, or category.

**Anatomy:**
- Pill shape (border-radius 12px, padding 4px 12px)
- Label text (Caption size, uppercase)
- Background color from status or cluster token

**States:**
- `draft`: `--color-warning` bg, dark text
- `accepted`: `--color-success` bg, white text
- `superseded`: `--color-text-secondary` bg, white text

**Accessibility:** Text contrast must meet AA on badge background. Use `aria-label` when badge meaning isn't obvious from text alone.

**Do:** Use badges for metadata classification. Keep text to 1–2 words.
**Don't:** Use badges as primary navigation. Stack more than 4 badges per card.

### Breadcrumb

**Purpose:** Shows the user's current position in the IA hierarchy and enables upward navigation.

**Anatomy:**
- Horizontal list of (label, link) pairs separated by `>` chevrons
- Current page label is not a link (bold, `--color-text`)
- Parent labels are links (`--color-primary`)

**States:**
- Link: `--color-primary`, underline on hover
- Current: `--color-text`, bold, not clickable

**Accessibility:** Wrapped in `<nav aria-label="Breadcrumb">`. Links use descriptive text. Current page indicated with `aria-current="page"`.

**Do:** Always show Home as the first breadcrumb segment. Limit to 4 levels.
**Don't:** Truncate breadcrumb segments. Use breadcrumb as the only navigation.

### ZoomIndicator

**Purpose:** Visual stepper showing the user's current level in the 4-zoom model.

**Anatomy:**
- 4 circular steps labeled Map / Section / Topic / Source
- Current level: filled circle with `--color-primary`
- Completed levels: filled circle with `--color-text-secondary`
- Upcoming levels: outlined circle with `--color-border`
- Connecting line between steps

**States:**
- Active: filled `--color-primary`, label bold
- Visited: filled `--color-text-secondary`
- Upcoming: outlined `--color-border`

**Accessibility:** Use `role="progressbar"` with `aria-valuenow` and `aria-valuetext`. Provide screen-reader text: "Level 2 of 4: Section".

**Do:** Display on every page except the landing page.
**Don't:** Make zoom indicator interactive (it's informational only).

### MetadataPanel

**Purpose:** Right-side panel on note detail views showing structured metadata.

**Anatomy:**
- Panel container (sticky, `--color-surface-alt` bg, 280px width)
- Sections: Beamline, Modality, Tags, Related Publications, Related Tools
- Each section: label (Caption, bold) + value (TagChips or links)

**States:**
- Populated: shows all available metadata
- Sparse: shows only available fields, no empty sections

**Accessibility:** Panel is a `<aside>` with `aria-label="Note metadata"`. All links are descriptive.

**Do:** Hide empty metadata sections. Keep panel sticky on scroll.
**Don't:** Put primary content in the metadata panel. Show the panel on mobile (move to bottom).

### TagChip

**Purpose:** Clickable tag label for filtering.

**Anatomy:**
- Pill shape (border-radius 16px, padding 4px 12px)
- Label text (Caption size)
- Background: `--color-surface`, border: `--color-border`
- Active state: `--color-primary` bg, white text

**States:**
- Default: surface bg, border, `--color-text` text
- Hover: `--color-primary` bg at 10% opacity
- Active (selected): `--color-primary` bg, white text
- Focus: 2px solid outline

**Accessibility:** Rendered as `<button>` elements. `aria-pressed` reflects selection state.

**Do:** Use for filterable vocabulary terms. Show tag count when applicable.
**Don't:** Use for non-interactive labels (use Badge instead). Exceed 20px total height.

### CodeBlock

**Purpose:** Renders code snippets with syntax highlighting.

**Anatomy:**
- Container: `--color-text` bg (dark), border-radius 8px, padding 16px
- Code: JetBrains Mono, 14px, `--color-surface` text
- Language badge: top-right corner
- Copy button: top-right, on hover

**States:**
- Default: dark background, light text
- Hover: copy button appears

**Accessibility:** Code blocks are in a `<pre><code>` structure. Language indicated via `aria-label`. Copy button has `aria-label="Copy code"`.

**Do:** Use Pygments with a dark theme matching the design system. Show language badge.
**Don't:** Use code blocks for non-code content. Allow horizontal scroll when avoidable (wrap long lines).

### Footer

**Purpose:** DOE and eBERlight acknowledgment on every page.

**Anatomy:**
- Full-width container, `--color-primary` bg, white text
- DOE acknowledgment text (Contract No. DE-AC02-06CH11357)
- Links: APS, eBERlight, repository
- Last-updated timestamp

**States:**
- Single state (always visible)

**Accessibility:** Footer in a `<footer>` element. Links have sufficient contrast (white on `--color-primary` = 8.6:1).

**Do:** Display on every page. Keep acknowledgment text verbatim.
**Don't:** Add interactive elements beyond links. Override footer styling per page.
