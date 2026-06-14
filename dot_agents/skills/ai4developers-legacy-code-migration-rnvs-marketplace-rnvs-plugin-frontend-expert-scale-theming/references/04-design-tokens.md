# Design Tokens Reference

This document provides a comprehensive reference for Scale design tokens including colors, typography, spacing, shadows, border radius, and grid system.

---

## Overview

Scale uses design tokens to manage design decisions systematically. Design tokens are the single source of truth for colors, typography, spacing, shadows, and other visual properties. They originate in JSON format and are converted into CSS variables, JavaScript objects, and design tool styles using Style Dictionary.

### Installing Design Tokens

```bash
npm install @telekom/scale-design-tokens
# or for neutral/open source version
npm install @telekom/scale-design-tokens-neutral
```

### Token Categories

| Category | Description | Prefix |
|----------|-------------|--------|
| Colors | Primary, functional, text, background, UI colors | `--telekom-color-*` |
| Typography | Font families, sizes, weights, line heights | `--telekom-typography-*` |
| Spacing | Component and layout spacing scales | `--telekom-spacing-*` |
| Shadows | Elevation levels for depth perception | `--telekom-shadow-*` |
| Radii | Border radius values | `--telekom-radius-*` |

---

## Colors

Scale provides a comprehensive color system with semantic naming for consistent usage across light and dark modes.

### Primary Colors (Magenta)

The Telekom brand's signature magenta color with interactive states:

| Token | Value | Usage |
|-------|-------|-------|
| `--telekom-color-primary-standard` | `#e20074` | Default primary color |
| `--telekom-color-primary-hovered` | `#c00063` | Hover state |
| `--telekom-color-primary-pressed` | `#9e0051` | Active/pressed state |

### Text & Icon Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--telekom-color-text-and-icon-standard` | `#000000` | `#ffffff` | Primary text |
| `--telekom-color-text-and-icon-additional` | `hsla(0,0%,0%,0.65)` | `hsla(0,0%,100%,0.65)` | Secondary text |
| `--telekom-color-text-and-icon-disabled` | `hsla(0,0%,0%,0.41)` | `hsla(0,0%,100%,0.41)` | Disabled text |
| `--telekom-color-text-and-icon-link-standard` | Blue | Blue | Hyperlinks |

### Background Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--telekom-color-background-canvas` | `#ffffff` | `#000000` | Page background |
| `--telekom-color-background-canvas-subtle` | Light gray | Dark gray | Card layouts |
| `--telekom-color-background-surface` | `#ffffff` | `#1c1c1e` | Component backgrounds |
| `--telekom-color-background-surface-highlight` | Light gray | Dark gray | Emphasized areas (footers) |
| `--telekom-color-background-backdrop` | Semi-transparent | Semi-transparent | Dialog overlays |

### Functional/Semantic Colors

| State | Standard | Hovered | Pressed |
|-------|----------|---------|---------|
| **Success** | `#00b367` | `#00c26d` | `#1bd27f` |
| **Danger** | `#e82010` | `#f2321e` | `#f84934` |
| **Warning** | `#f97012` | `#fc7e21` | `#fd9038` |
| **Informational** | `#2238df` (light) / `#7d94f9` (dark) | - | - |

### UI Colors

For borders, fills, and interactive states:

- `--telekom-color-ui-border-standard` - Standard borders
- `--telekom-color-ui-border-hovered` - Hovered borders
- `--telekom-color-ui-border-pressed` - Pressed borders
- `--telekom-color-ui-border-disabled` - Disabled borders
- `--telekom-color-functional-focus` - Focus ring color

### Data Visualization Colors

Scale includes ten color families for charts and data visualization, each with 10 tones (0-900):

- Violet, Blue, Cyan, Teal, Green
- Olive, Brown, Yellow, Orange, Red

---

## Typography

Scale uses **TeleNeo** (web version: TeleNeoWeb) as the primary corporate typeface, a central element for brand recognition.

### Font Families

```css
--telekom-typography-font-family-sans: TeleNeoWeb, sans-serif;
--telekom-typography-font-family-mono: monospace;

/* Short aliases */
--scl-font-family-sans: TeleNeoWeb, sans-serif;
--scl-font-family-mono: monospace;
```

### Font Weights

| Weight Name | Value | CSS Variable |
|-------------|-------|--------------|
| Thin | 200 | `--telekom-typography-font-weight-thin` |
| Regular | 400 | `--telekom-typography-font-weight-regular` |
| Medium | 500 | `--telekom-typography-font-weight-medium` |
| Bold | 700 | `--telekom-typography-font-weight-bold` |
| Extra Bold | 800 | `--telekom-typography-font-weight-extra-bold` |
| Ultra | 900 | `--telekom-typography-font-weight-ultra` |

### Font Sizes

| Token | Value (rem) | Value (px at 16px base) |
|-------|-------------|-------------------------|
| `--scl-font-size-10` | 0.625rem | 10px |
| `--scl-font-size-12` | 0.75rem | 12px |
| `--scl-font-size-14` | 0.875rem | 14px |
| `--scl-font-size-16` | 1rem | 16px |
| `--scl-font-size-20` | 1.25rem | 20px |
| `--scl-font-size-24` | 1.5rem | 24px |
| `--scl-font-size-32` | 2rem | 32px |
| `--scl-font-size-40` | 2.5rem | 40px |
| `--scl-font-size-56` | 3.5rem | 56px |

### Line Heights

Scale provides line height values ranging from 114% to 160%, with standard values including 120%, 125%, 133%, and 150%.

### Typography Best Practices

- Use **italic** style only as an exception (e.g., for quotations or references)
- Maintain a minimum contrast ratio of **4.5:1** for small text (accessibility requirement)
- Use semantic color tokens for text colors to ensure proper contrast in both light and dark modes

---

## Grid System

Scale's grid is built on an **8-pixel square base unit**, with all dimensions derived from multiples of this unit.

### Grid Components

1. **Margin** - Fixed spacing around the grid edges
2. **Columns** - Dynamic width elements that adapt to content
3. **Gutter** - Fixed 32px space between columns

### Responsive Breakpoints

| Breakpoint | Range | Margins | Columns | Column Width | Gutter |
|------------|-------|---------|---------|--------------|--------|
| **S** (Small) | 320-639px | 16px | 4 | Dynamic | 32px |
| **M** (Medium) | 640-1039px | 16px | 8 | Dynamic | 32px |
| **L** (Large) | 1040-1295px | 24px | 16 | Dynamic | 32px |
| **XL** (Extra Large) | 1296-1679px | 24px | 16 | Dynamic | 32px |
| **XXL** (Extra Extra Large) | 1680px+ | Dynamic | 16 | 64px (fixed) | 32px |

### Grid Usage in CSS

```css
.container {
  max-width: 1680px;
  margin: 0 auto;
  padding: 0 var(--telekom-spacing-composition-space-08); /* 16px for S/M */
}

@media (min-width: 1040px) {
  .container {
    padding: 0 var(--telekom-spacing-composition-space-12); /* 24px for L/XL */
  }
}
```

---

## Shadows

Scale uses elevation shadows to create depth hierarchy in the interface.

### Shadow Categories

| Category | Usage |
|----------|-------|
| **Raised** | Elements visually elevated above the surface |
| **Floating** | Floating elements like FABs and notifications |
| **Top** | Elements positioned above main content (navigation, bottom sheets) |
| **Overlay** | Temporary overlays (modals, dialogs) |
| **App Bar Top** | Fixed headers and top app bars |
| **App Bar Bottom** | Fixed bottom bars |

### Shadow Elevation Levels

| Level | CSS Variable | Value |
|-------|--------------|-------|
| 0 | `--telekom-shadow-raised-standard` | `0px 2px 8px 0px hsla(0,0%,0%,0.1), 0px 1px 2px 0px hsla(0,0%,0%,0.1)` |
| 1 | `--telekom-shadow-level-1` | `0px 4px 16px 0px hsla(0,0%,0%,0.1), 0px 2px 4px 0px hsla(0,0%,0%,0.1)` |
| 2 | `--telekom-shadow-level-2` | `0px 8px 32px 0px hsla(0,0%,0%,0.1), 0px 4px 8px 0px hsla(0,0%,0%,0.1)` |
| 3 | `--telekom-shadow-level-3` | `0px 12px 48px 0px hsla(0,0%,0%,0.1), 0px 6px 12px 0px hsla(0,0%,0%,0.1)` |
| 4 | `--telekom-shadow-level-4` | `0px 16px 64px 0px hsla(0,0%,0%,0.1), 0px 8px 16px 0px hsla(0,0%,0%,0.1)` |
| 5 | `--telekom-shadow-level-5` | `0px 20px 80px 0px hsla(0,0%,0%,0.1), 0px 10px 20px 0px hsla(0,0%,0%,0.1)` |

### Shadow Usage

```css
.card {
  box-shadow: var(--telekom-shadow-raised-standard);
}

.card:hover {
  box-shadow: var(--telekom-shadow-raised-hovered);
}

.modal {
  box-shadow: var(--telekom-shadow-overlay);
}
```

---

## Spacing

Scale provides two spacing scales for different use cases: component-level and layout-level.

### Component Spacing Scale

Used for detail-level designs within components:

| CSS Variable | Pixels | Rem |
|--------------|--------|-----|
| `--scl-spacing-1` | 1px | 0.0625rem |
| `--scl-spacing-2` | 2px | 0.125rem |
| `--scl-spacing-4` | 4px | 0.25rem |
| `--scl-spacing-8` | 8px | 0.5rem |
| `--scl-spacing-12` | 12px | 0.75rem |
| `--scl-spacing-16` | 16px | 1rem |
| `--scl-spacing-24` | 24px | 1.5rem |
| `--scl-spacing-32` | 32px | 2rem |

### Layout Spacing Scale (Composition)

Used for page-level layouts with larger increments:

| CSS Variable | Pixels | Rem |
|--------------|--------|-----|
| `--telekom-spacing-composition-space-04` | 8px | 0.5rem |
| `--telekom-spacing-composition-space-06` | 12px | 0.75rem |
| `--telekom-spacing-composition-space-08` | 16px | 1rem |
| `--telekom-spacing-composition-space-10` | 20px | 1.25rem |
| `--telekom-spacing-composition-space-12` | 24px | 1.5rem |
| `--telekom-spacing-composition-space-14` | 32px | 2rem |
| `--telekom-spacing-composition-space-16` | 40px | 2.5rem |
| `--telekom-spacing-composition-space-18` | 48px | 3rem |
| `--telekom-spacing-composition-space-20` | 64px | 4rem |
| `--telekom-spacing-composition-space-21` | 96px | 6rem |

### Baseline Spacing Scale

For larger structural spacing:

| CSS Variable | Value |
|--------------|-------|
| `--telekom-spacing-baseline-space-01` | 0.25rem (4px) |
| `--telekom-spacing-baseline-space-02` | 0.5rem (8px) |
| `--telekom-spacing-baseline-space-03` | 0.75rem (12px) |
| `--telekom-spacing-baseline-space-04` | 1rem (16px) |
| `--telekom-spacing-baseline-space-05` | 1.5rem (24px) |
| `--telekom-spacing-baseline-space-06` | 2rem (32px) |
| `--telekom-spacing-baseline-space-07` | 3rem (48px) |
| `--telekom-spacing-baseline-space-08` | 4rem (64px) |
| `--telekom-spacing-baseline-space-09` | 6rem (96px) |

### Spacing Best Practices

- **Relationships**: Elements near each other are perceived as related; consistent spacing signals groupings
- **Hierarchy**: Strategic spacing conveys importance; more surrounding space = greater prominence
- **White Space**: Empty space prevents cognitive overload and highlights important elements

---

## Border Radius

Scale provides semantic border radius tokens for consistent rounded corners.

| Token | Value | Usage |
|-------|-------|-------|
| `--telekom-radius-none` | 0rem | No rounding |
| `--telekom-radius-extra-small` | 0.125rem (2px) | Subtle rounding |
| `--telekom-radius-small` | 0.25rem (4px) | Small elements |
| `--telekom-radius-medium-small` | 0.375rem (6px) | Medium-small elements |
| `--telekom-radius-standard` | 0.5rem (8px) | Default for most components |
| `--telekom-radius-large` | 0.75rem (12px) | Larger elements, cards |
| `--telekom-radius-pill` | 62.4375rem | Pill-shaped buttons |
| `--telekom-radius-circle` | 50% | Circular elements |

---

## Usage in Vue Components

### Using Semantic Tokens in CSS

Always use semantic tokens that adapt to light/dark mode:

```css
/* Good - adapts to mode */
.my-component {
  color: var(--telekom-color-text-and-icon-standard);
  background: var(--telekom-color-background-surface);
  border: 1px solid var(--telekom-color-ui-border-standard);
  border-radius: var(--telekom-radius-standard);
  padding: var(--scl-spacing-16);
  box-shadow: var(--telekom-shadow-raised-standard);
}

/* Bad - hardcoded values */
.my-component {
  color: #000000;
  background: #ffffff;
  border-radius: 8px;
}
```

### Using Tokens in Scoped Styles

```vue
<style scoped>
.login-form {
  max-width: 400px;
  padding: var(--scl-spacing-24);
  background: var(--telekom-color-background-surface);
  border-radius: var(--telekom-radius-large);
  box-shadow: var(--telekom-shadow-raised-standard);
}

.login-form h2 {
  margin-bottom: var(--scl-spacing-16);
  font-weight: var(--telekom-typography-font-weight-bold);
}

.button-group {
  margin-top: var(--scl-spacing-16);
}
</style>
```
