# Scale Design System with Vue 3 - Comprehensive Developer Guide

This guide provides everything a frontend developer needs to create a Vue 3 application using the Telekom Scale Design System.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Vue 3 Configuration](#vue-3-configuration)
4. [Using Components](#using-components)
5. [Event Handling](#event-handling)
6. [Form Handling](#form-handling)
7. [Design Tokens & Theming](#design-tokens--theming)
8. [Light and Dark Mode](#light-and-dark-mode)
9. [Colors](#colors)
10. [Typography](#typography)
11. [Grid System](#grid-system)
12. [Shadows](#shadows)
13. [Spacing](#spacing)
14. [Border Radius](#border-radius)
15. [Custom Theming](#custom-theming)
16. [Complete Component Reference](#complete-component-reference)
17. [Accessibility](#accessibility)
18. [Best Practices](#best-practices)
19. [Troubleshooting](#troubleshooting)

---

## Overview

Scale is Deutsche Telekom's digital design system providing production-ready web components for building consistent, accessible applications. Key features:

- **63 Production-Ready Components**: Buttons, forms, modals, data grids, and more
- **Framework Agnostic**: Built as Web Components, works natively with Vue 3
- **Accessible by Default**: WCAG 2.1 Level AA compliant
- **Customizable Theming**: Design tokens for consistent styling
- **TypeScript Support**: Full type definitions included

### Packages

| Package | Description |
|---------|-------------|
| `@telekom/scale-components` | Core components (Telekom branded) |
| `@telekom/scale-components-neutral` | Core components (Open source, no branding) |
| `@telekom/scale-design-tokens` | Design tokens (Telekom branded) |
| `@telekom/scale-design-tokens-neutral` | Design tokens (Open source) |

> **Note**: The Vue-specific proxy packages (`@telekom/scale-components-vue`) are deprecated and will be removed in v4. Use the core packages directly.

---

## Installation

### NPM Installation

**Telekom Branded Version:**
```bash
npm install @telekom/scale-components@next
```

**Open Source/Neutral Version:**
```bash
npm install @telekom/scale-components-neutral@next
```

> Use `@next` for the latest version with dark mode support. Omit for stable release.

### Setup in main.ts/main.js

```typescript
import { createApp } from 'vue'
import App from './App.vue'

// Import Scale
import { defineCustomElements } from '@telekom/scale-components/loader'
import '@telekom/scale-components/dist/scale-components/scale-components.css'

// Initialize Scale components
defineCustomElements()

createApp(App).mount('#app')
```

### Tree-Shaking (Optional)

Import only specific components to reduce bundle size:

```typescript
import { defineCustomElementScaleButton } from '@telekom/scale-components'
import { defineCustomElementScaleTextField } from '@telekom/scale-components'

defineCustomElementScaleButton()
defineCustomElementScaleTextField()
```

---

## Vue 3 Configuration

Vue 3 needs to be configured to recognize Scale components as custom elements rather than attempting to resolve them as Vue components.

### Vite (Recommended)

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('scale-'),
        },
      },
    }),
  ],
})
```

### Vue CLI (webpack)

```javascript
// vue.config.js
module.exports = {
  chainWebpack: (config) => {
    config.module
      .rule('vue')
      .use('vue-loader')
      .tap((options) => {
        options.compilerOptions = {
          isCustomElement: (tag) => tag.startsWith('scale-'),
        }
        return options
      })
  },
}
```

### Webpack (Manual Configuration)

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          compilerOptions: {
            isCustomElement: (tag) => tag.startsWith('scale-'),
          },
        },
      },
    ],
  },
}
```

### CDN-loaded Scale components optimized for Vue SFC Playground

```javascript
// Load Scale components from CDN
const loadScaleComponents = async () => {
  if (!customElements.get('scale-button')) {
    try {
      const { defineCustomElements } = await import('https://cdn.jsdelivr.net/npm/@telekom/scale-components@next/loader/index.es2017.js')
      defineCustomElements()
      console.log('✅ Scale components loaded from CDN')
    } catch (error) {
      console.error('❌ Failed to load Scale components:', error)
    }
  }
}
```

### Runtime Compilation

```typescript
// main.ts (for on-the-fly template compilation)
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith('scale-')
app.mount('#app')
```

### ESLint Configuration

If using `eslint-plugin-vue`, disable the deprecated slot attribute rule:

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'vue/no-deprecated-slot-attribute': 'off',
  },
}
```

---

## Using Components

Once configured, Scale components are available as custom HTML elements:

```vue
<template>
  <div>
    <scale-button>Click Me!</scale-button>

    <scale-text-field
      label="Username"
      placeholder="Enter your name"
    />

    <scale-checkbox label="I agree to terms" />
  </div>
</template>
```

### Passing Props

Props are passed as HTML attributes. Use kebab-case for multi-word props:

```vue
<template>
  <scale-button
    variant="primary"
    size="large"
    :disabled="isLoading"
    icon-position="before"
  >
    Submit
  </scale-button>
</template>
```

### Dynamic Props with Vue

Use `:prop` or `v-bind:prop` for dynamic values:

```vue
<template>
  <scale-text-field
    :label="fieldLabel"
    :value="inputValue"
    :invalid="hasError"
    :helper-text="errorMessage"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fieldLabel = ref('Email Address')
const inputValue = ref('')
const hasError = ref(false)
const errorMessage = ref('')
</script>
```

---

## Event Handling

### Event Naming Convention

Scale components emit custom events prefixed with `scale-` using kebab-case:

| Event Pattern | Example |
|---------------|---------|
| `scale-{action}` | `scale-change`, `scale-input`, `scale-click` |
| `scale-{state}` | `scale-focus`, `scale-blur`, `scale-open`, `scale-close` |

> **Legacy Note**: Before v3, events used camelCase (e.g., `scaleChange`). These are deprecated but still available.

### Binding Events

Use Vue's `@` or `v-on:` syntax:

```vue
<template>
  <scale-button @click="handleClick">Click Me</scale-button>

  <scale-text-field
    @scale-change="handleChange"
    @scale-input="handleInput"
    @scale-focus="handleFocus"
    @scale-blur="handleBlur"
  />

  <scale-modal
    :opened="isOpen"
    @scale-close="isOpen = false"
    @scale-before-close="handleBeforeClose"
  >
    Modal Content
  </scale-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)

const handleClick = () => {
  console.log('Button clicked')
}

const handleChange = (event: CustomEvent) => {
  console.log('Value changed:', event.target.value)
}

const handleInput = (event: CustomEvent) => {
  console.log('Input event:', event.detail)
}

const handleFocus = () => {
  console.log('Field focused')
}

const handleBlur = () => {
  console.log('Field blurred')
}

const handleBeforeClose = (event: CustomEvent) => {
  // Prevent closing if needed
  if (!canClose.value) {
    event.preventDefault()
  }
}
</script>
```

---

## Form Handling

### Important: v-model Does NOT Work

The `v-model` directive does not work with custom elements. You must manually bind values and events:

```vue
<template>
  <!-- WRONG - v-model won't work -->
  <scale-text-field v-model="email" />

  <!-- CORRECT - manual binding -->
  <scale-text-field
    :value="email"
    @scale-change="email = $event.target.value"
  />
</template>
```

### Complete Form Example

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <scale-text-field
      label="Email"
      type="email"
      :value="form.email"
      :invalid="errors.email !== ''"
      :helper-text="errors.email"
      @scale-change="form.email = $event.target.value"
      required
    />

    <scale-text-field
      label="Password"
      type="password"
      :value="form.password"
      :invalid="errors.password !== ''"
      :helper-text="errors.password"
      @scale-change="form.password = $event.target.value"
      required
    />

    <scale-checkbox
      label="Remember me"
      :checked="form.remember"
      @scale-change="form.remember = $event.detail.checked"
    />

    <scale-dropdown-select
      label="Country"
      :value="form.country"
      @scale-change="form.country = $event.detail.value"
    >
      <scale-dropdown-select-item value="de">Germany</scale-dropdown-select-item>
      <scale-dropdown-select-item value="us">United States</scale-dropdown-select-item>
      <scale-dropdown-select-item value="uk">United Kingdom</scale-dropdown-select-item>
    </scale-dropdown-select>

    <scale-button type="submit" :disabled="isSubmitting">
      {{ isSubmitting ? 'Submitting...' : 'Submit' }}
    </scale-button>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const form = reactive({
  email: '',
  password: '',
  remember: false,
  country: '',
})

const errors = reactive({
  email: '',
  password: '',
})

const isSubmitting = ref(false)

const handleSubmit = async () => {
  // Reset errors
  errors.email = ''
  errors.password = ''

  // Validate
  if (!form.email) {
    errors.email = 'Email is required'
    return
  }
  if (!form.password || form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    return
  }

  isSubmitting.value = true
  try {
    // Submit form...
    console.log('Submitting:', form)
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

### Creating a Reusable v-model Wrapper

For convenience, create wrapper components:

```vue
<!-- components/ScaleInput.vue -->
<template>
  <scale-text-field
    v-bind="$attrs"
    :value="modelValue"
    @scale-change="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
```

Usage:

```vue
<template>
  <ScaleInput v-model="email" label="Email" type="email" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ScaleInput from './components/ScaleInput.vue'

const email = ref('')
</script>
```

---

## Design Tokens & Theming

Scale uses design tokens to manage design decisions systematically. Design tokens are the single source of truth for colors, typography, spacing, shadows, and other visual properties. They originate in JSON format and are converted into CSS variables, JavaScript objects, and design tool styles using Style Dictionary.

### Installing Design Tokens

```bash
npm install @telekom/scale-design-tokens
# or for neutral/open source version
npm install @telekom/scale-design-tokens-neutral
```

### Token Categories

Scale design tokens are organized into several categories:

| Category | Description | Prefix |
|----------|-------------|--------|
| Colors | Primary, functional, text, background, UI colors | `--telekom-color-*` |
| Typography | Font families, sizes, weights, line heights | `--telekom-typography-*` |
| Spacing | Component and layout spacing scales | `--telekom-spacing-*` |
| Shadows | Elevation levels for depth perception | `--telekom-shadow-*` |
| Radii | Border radius values | `--telekom-radius-*` |

---

## Light and Dark Mode

Scale components fully support light and dark mode, available since the newest version. The implementation leverages CSS custom properties for seamless mode switching.

### Default Behavior

By default, Scale automatically matches operating system preferences through the `prefers-color-scheme` media query.

### Manual Configuration

Override system preferences by setting the `data-mode` attribute on the body or any container element:

```html
<!-- Set light mode explicitly -->
<body data-mode="light">

<!-- Set dark mode explicitly -->
<body data-mode="dark">
```

### Vue 3 Implementation

```vue
<template>
  <div :data-mode="isDarkMode ? 'dark' : 'light'">
    <scale-button @click="toggleTheme">
      {{ isDarkMode ? 'Switch to Light' : 'Switch to Dark' }}
    </scale-button>
    <!-- Your app content -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isDarkMode = ref(false)

// Initialize based on system preference
onMounted(() => {
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  isDarkMode.value = mq.matches

  // Listen for system preference changes
  mq.addEventListener('change', (e) => {
    isDarkMode.value = e.matches
  })
})

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
}
</script>
```

### Applying Mode-Aware Styles

Use the semantic color tokens to style your application:

```css
body {
  background-color: var(--telekom-color-background-canvas);
  color: var(--telekom-color-text-and-icon-standard);
}

.card {
  background-color: var(--telekom-color-background-surface);
  border: 1px solid var(--telekom-color-ui-border-standard);
}
```

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

## Custom Theming

Scale components use Shadow DOM for style encapsulation. Customization is achieved through scoped CSS variables and shadow parts.

### Three Levels of Customization

1. **Single Instance**: Apply styles directly to one component
2. **Variants**: Create reusable component variations
3. **Themes**: Group customizations under a CSS class for site-wide application

### CSS Variable Overrides

Override component-scoped variables directly:

```css
/* Target all buttons */
scale-button {
  --radius: 0;
}

/* Create a variant with a class */
scale-button.squared {
  --radius: 0;
}

/* Use custom attributes */
scale-button[variant='squared'] {
  --radius: 0;
}
```

Inline styles for individual instances:

```html
<scale-button style="--radius: 0">Squared Button</scale-button>
```

### Shadow Parts

Use the `::part()` pseudo-element to target internal component elements:

```css
scale-button::part(base) {
  border-radius: 0;
  text-transform: uppercase;
}

scale-button.custom::part(base):hover {
  background-color: var(--telekom-color-primary-hovered);
}
```

### Creating a Complete Theme

Group customizations under a CSS class:

```css
/* custom-theme.css */
.my-custom-theme {
  /* Override design tokens */
  --telekom-color-primary-standard: #0066cc;
  --telekom-color-primary-hovered: #0052a3;
  --telekom-color-primary-pressed: #003d7a;

  /* Override typography */
  --telekom-typography-font-family-sans: 'Inter', sans-serif;

  /* Override spacing */
  --telekom-radius-standard: 4px;
}

/* Component-specific overrides within theme */
.my-custom-theme scale-button {
  --radius: 4px;
}

.my-custom-theme scale-card {
  --background: var(--telekom-color-background-surface);
}
```

Apply the theme:

```html
<body class="my-custom-theme">
  <!-- All Scale components inherit the theme -->
</body>
```

### Vue 3 Theme Provider Example

```vue
<template>
  <div :class="currentTheme">
    <scale-dropdown-select
      label="Theme"
      :value="currentTheme"
      @scale-change="currentTheme = $event.detail.value"
    >
      <scale-dropdown-select-item value="">Default</scale-dropdown-select-item>
      <scale-dropdown-select-item value="theme-corporate">Corporate</scale-dropdown-select-item>
      <scale-dropdown-select-item value="theme-modern">Modern</scale-dropdown-select-item>
    </scale-dropdown-select>

    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'

const currentTheme = ref('')
provide('currentTheme', currentTheme)
</script>

<style>
.theme-corporate {
  --telekom-color-primary-standard: #003366;
  --telekom-radius-standard: 0;
}

.theme-modern {
  --telekom-color-primary-standard: #6366f1;
  --telekom-radius-standard: 1rem;
}
</style>
```

---

## Complete Component Reference

### Form Components

#### scale-text-field

Text input field with label, helper text, and validation.

```vue
<scale-text-field
  label="Username"
  type="text"
  placeholder="Enter username"
  helper-text="Must be at least 3 characters"
  :value="username"
  :invalid="isInvalid"
  :disabled="isDisabled"
  :readonly="isReadonly"
  :required="true"
  :max-length="50"
  :counter="true"
  @scale-change="handleChange"
  @scale-input="handleInput"
  @scale-focus="handleFocus"
  @scale-blur="handleBlur"
/>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'text' \| 'email' \| 'password' \| 'number' \| 'tel' \| 'url' \| 'date'` | `'text'` | Input type |
| `label` | `string` | `''` | Field label |
| `value` | `string \| number` | `''` | Current value |
| `placeholder` | `string` | `''` | Placeholder text |
| `helper-text` | `string` | `''` | Helper/error text |
| `invalid` | `boolean` | `false` | Show error state |
| `disabled` | `boolean` | `false` | Disable input |
| `readonly` | `boolean` | `false` | Read-only mode |
| `required` | `boolean` | `false` | Mark as required |
| `max-length` | `number` | - | Maximum characters |
| `min-length` | `number` | - | Minimum characters |
| `counter` | `boolean` | `false` | Show character counter |
| `variant` | `'informational' \| 'warning' \| 'danger' \| 'success'` | `'informational'` | Visual variant |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Value changed (on blur) |
| `scale-input` | Value changing (on input) |
| `scale-focus` | Field gained focus |
| `scale-blur` | Field lost focus |
| `scale-keydown` | Key pressed |

---

#### scale-checkbox

Checkbox input with label.

```vue
<scale-checkbox
  label="I agree to the terms"
  :checked="isChecked"
  :indeterminate="isIndeterminate"
  :disabled="isDisabled"
  :required="true"
  helper-text="Please accept to continue"
  @scale-change="handleChange"
/>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `''` | Checkbox label |
| `checked` | `boolean` | `false` | Checked state |
| `indeterminate` | `boolean` | `false` | Indeterminate state |
| `disabled` | `boolean` | `false` | Disable checkbox |
| `required` | `boolean` | `false` | Mark as required |
| `name` | `string` | - | Form field name |
| `value` | `string` | - | Form field value |
| `helper-text` | `string` | - | Helper text |
| `invalid` | `boolean` | `false` | Show error state |

**Events:**
| Event | Detail | Description |
|-------|--------|-------------|
| `scale-change` | `{ checked, indeterminate, value, disabled }` | State changed |

---

#### scale-dropdown-select

Dropdown selection component.

```vue
<scale-dropdown-select
  label="Select Country"
  :value="selectedCountry"
  placeholder="Choose a country"
  :disabled="isDisabled"
  :invalid="hasError"
  helper-text="Required field"
  @scale-change="selectedCountry = $event.detail.value"
>
  <scale-dropdown-select-item value="de">Germany</scale-dropdown-select-item>
  <scale-dropdown-select-item value="at">Austria</scale-dropdown-select-item>
  <scale-dropdown-select-item value="ch">Switzerland</scale-dropdown-select-item>
</scale-dropdown-select>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | Field label |
| `value` | `any` | - | Selected value |
| `disabled` | `boolean` | `false` | Disable dropdown |
| `readonly` | `boolean` | `false` | Read-only mode |
| `invalid` | `boolean` | `false` | Show error state |
| `helper-text` | `string` | `''` | Helper text |
| `variant` | `'informational' \| 'warning' \| 'danger' \| 'success'` | `'informational'` | Visual variant |
| `allow-clear` | `boolean` | `false` | Show clear button |

---

#### scale-radio-button-group

Radio button group for single selection.

```vue
<scale-radio-button-group
  label="Choose Option"
  :value="selectedOption"
  @scale-change="selectedOption = $event.detail.value"
>
  <scale-radio-button value="option1" label="Option 1" />
  <scale-radio-button value="option2" label="Option 2" />
  <scale-radio-button value="option3" label="Option 3" disabled />
</scale-radio-button-group>
```

---

#### scale-switch

Toggle switch component.

```vue
<scale-switch
  label="Enable notifications"
  :checked="isEnabled"
  @scale-change="isEnabled = $event.detail.checked"
/>
```

---

### Button Components

#### scale-button

Primary button component.

```vue
<scale-button
  variant="primary"
  size="large"
  :disabled="isLoading"
  icon-position="before"
  @click="handleClick"
>
  <scale-icon-action-add slot="icon" />
  Add Item
</scale-button>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'ghost'` | `'primary'` | Button style |
| `size` | `'small' \| 'large'` | `'large'` | Button size |
| `disabled` | `boolean` | `false` | Disable button |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | Button type |
| `icon-only` | `boolean` | `false` | Icon-only button |
| `icon-position` | `'before' \| 'after'` | `'before'` | Icon placement |
| `href` | `string` | - | Render as link |
| `target` | `string` | `'_self'` | Link target |

---

#### scale-segmented-button

Segmented button group.

```vue
<scale-segmented-button>
  <scale-segment value="day" :selected="view === 'day'" @click="view = 'day'">
    Day
  </scale-segment>
  <scale-segment value="week" :selected="view === 'week'" @click="view = 'week'">
    Week
  </scale-segment>
  <scale-segment value="month" :selected="view === 'month'" @click="view = 'month'">
    Month
  </scale-segment>
</scale-segmented-button>
```

---

### Layout Components

#### scale-card

Card container component.

```vue
<scale-card>
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
  <scale-button slot="footer">Action</scale-button>
</scale-card>

<!-- Clickable card -->
<scale-card to="/details" label="View Details">
  <h3>Clickable Card</h3>
  <p>Click anywhere to navigate.</p>
</scale-card>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `to` | `string` | - | Link URL (makes card clickable) |
| `target` | `string` | `'_self'` | Link target |
| `label` | `string` | - | Accessible label |

---

#### scale-accordion

Expandable accordion component.

```vue
<scale-accordion :dependent="true">
  <scale-collapsible>
    <span slot="heading">Section 1</span>
    Content for section 1
  </scale-collapsible>
  <scale-collapsible>
    <span slot="heading">Section 2</span>
    Content for section 2
  </scale-collapsible>
  <scale-collapsible>
    <span slot="heading">Section 3</span>
    Content for section 3
  </scale-collapsible>
</scale-accordion>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `dependent` | `boolean` | `false` | Only one section open at a time |
| `expanded` | `boolean` | `false` | All sections open initially |
| `heading-level` | `number` | - | Heading level for accessibility |
| `icon-location` | `'left' \| 'right'` | `'left'` | Expand icon position |

---

#### scale-modal

Modal dialog component.

```vue
<template>
  <scale-button @click="isOpen = true">Open Modal</scale-button>

  <scale-modal
    :opened="isOpen"
    heading="Confirm Action"
    size="default"
    align-actions="right"
    @scale-close="isOpen = false"
    @scale-before-close="handleBeforeClose"
  >
    <p>Are you sure you want to proceed?</p>

    <scale-button slot="action" variant="secondary" @click="isOpen = false">
      Cancel
    </scale-button>
    <scale-button slot="action" @click="handleConfirm">
      Confirm
    </scale-button>
  </scale-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)

const handleBeforeClose = (event: CustomEvent) => {
  // Optionally prevent closing
  // event.preventDefault()
}

const handleConfirm = () => {
  // Handle confirmation
  isOpen.value = false
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `opened` | `boolean` | `false` | Control visibility |
| `heading` | `string` | - | Modal title |
| `size` | `'default' \| 'small' \| 'large'` | `'default'` | Modal size |
| `align-actions` | `'left' \| 'right'` | `'right'` | Button alignment |
| `omit-close-button` | `boolean` | `false` | Hide close button |
| `close-button-label` | `string` | `'Close'` | Close button text |
| `duration` | `number` | `200` | Animation duration (ms) |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-open` | Modal opened |
| `scale-before-close` | Before closing (can prevent) |
| `scale-close` | Modal closed |

---

### Navigation Components

#### scale-tab-nav

Tab navigation component.

```vue
<scale-tab-nav size="small">
  <scale-tab-header slot="tab" :selected="activeTab === 0" @click="activeTab = 0">
    Tab 1
  </scale-tab-header>
  <scale-tab-header slot="tab" :selected="activeTab === 1" @click="activeTab = 1">
    Tab 2
  </scale-tab-header>
  <scale-tab-header slot="tab" :selected="activeTab === 2" @click="activeTab = 2" disabled>
    Tab 3 (Disabled)
  </scale-tab-header>

  <scale-tab-panel :selected="activeTab === 0">
    Content for Tab 1
  </scale-tab-panel>
  <scale-tab-panel :selected="activeTab === 1">
    Content for Tab 2
  </scale-tab-panel>
  <scale-tab-panel :selected="activeTab === 2">
    Content for Tab 3
  </scale-tab-panel>
</scale-tab-nav>
```

---

#### scale-sidebar-nav

Sidebar navigation component.

```vue
<scale-sidebar-nav>
  <scale-sidebar-nav-item>
    <a href="/dashboard">Dashboard</a>
  </scale-sidebar-nav-item>
  <scale-sidebar-nav-collapsible label="Settings">
    <scale-sidebar-nav-item>
      <a href="/settings/profile">Profile</a>
    </scale-sidebar-nav-item>
    <scale-sidebar-nav-item>
      <a href="/settings/security">Security</a>
    </scale-sidebar-nav-item>
  </scale-sidebar-nav-collapsible>
</scale-sidebar-nav>
```

---

#### scale-breadcrumb

Breadcrumb navigation.

```vue
<scale-breadcrumb>
  <a href="/">Home</a>
  <a href="/products">Products</a>
  <span>Current Page</span>
</scale-breadcrumb>
```

---

### Data Display Components

#### scale-data-grid

Data grid for displaying tabular data.

```vue
<template>
  <scale-data-grid
    :fields="columns"
    :rows="data"
    heading="User List"
    :selectable="true"
    :numbered="true"
    :freeze-header="true"
    :page-size="10"
    @scale-sort="handleSort"
    @scale-selection="handleSelection"
    @scale-edit="handleEdit"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const columns = [
  { type: 'text', label: 'Name', sortable: true },
  { type: 'text', label: 'Email', sortable: true },
  { type: 'number', label: 'Age', sortable: true },
  { type: 'text', label: 'Status' },
]

const data = ref([
  ['John Doe', 'john@example.com', 30, 'Active'],
  ['Jane Smith', 'jane@example.com', 25, 'Active'],
  ['Bob Wilson', 'bob@example.com', 35, 'Inactive'],
])

const handleSort = (event: CustomEvent) => {
  console.log('Sort:', event.detail)
}

const handleSelection = (event: CustomEvent) => {
  console.log('Selected rows:', event.detail)
}

const handleEdit = (event: CustomEvent) => {
  console.log('Edit:', event.detail)
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `fields` | `array` | - | Column configuration |
| `rows` | `array` | - | Data rows |
| `heading` | `string` | - | Table heading |
| `selectable` | `boolean` | `false` | Enable row selection |
| `numbered` | `boolean` | `false` | Show row numbers |
| `freeze-header` | `boolean` | `false` | Freeze header on scroll |
| `page-size` | `number` | `Infinity` | Rows per page |
| `shade-alternate` | `boolean` | `true` | Shade alternate rows |

---

#### scale-table

Simple HTML table styling.

```vue
<scale-table>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.name }}</td>
        <td>{{ user.email }}</td>
        <td>{{ user.role }}</td>
      </tr>
    </tbody>
  </table>
</scale-table>
```

---

### Feedback Components

#### scale-notification-toast

Toast notification component.

```vue
<template>
  <scale-button @click="showToast">Show Toast</scale-button>

  <scale-notification-toast
    ref="toastRef"
    variant="success"
    alignment="top-right"
    :auto-hide="true"
    :auto-hide-duration="5000"
    @scale-close="handleClose"
  >
    Operation completed successfully!
  </scale-notification-toast>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const toastRef = ref<HTMLElement | null>(null)

const showToast = () => {
  (toastRef.value as any)?.open()
}

const handleClose = () => {
  console.log('Toast closed')
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'error' \| 'warning' \| 'success' \| 'informational'` | `'informational'` | Toast style |
| `alignment` | `'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right'` | `'top-right'` | Position |
| `auto-hide` | `boolean` | `false` | Auto dismiss |
| `auto-hide-duration` | `number` | `3000` | Duration in ms |
| `opened` | `boolean` | - | Control visibility |

---

#### scale-notification-banner

Banner notification component.

```vue
<scale-notification-banner variant="warning" :opened="showBanner">
  <span slot="heading">Warning</span>
  Your session will expire in 5 minutes.
</scale-notification-banner>
```

---

#### scale-progress-bar

Progress indicator.

```vue
<scale-progress-bar
  :percentage="progress"
  :show-status="true"
  label="Upload Progress"
/>
```

---

#### scale-loading-spinner

Loading spinner component.

```vue
<scale-loading-spinner
  :size="48"
  text="Loading..."
  variant="primary"
/>
```

---

### Utility Components

#### scale-icon

Icon component.

```vue
<!-- Using icon name (references SVG sprite) -->
<scale-icon name="action-add" :size="24" />

<!-- Using path -->
<scale-icon
  :path="svgPath"
  :size="32"
  fill="currentColor"
  accessibility-title="Add item"
/>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | - | Icon name (from sprite) |
| `path` | `string` | - | SVG path data |
| `size` | `number` | `24` | Icon size (px) |
| `fill` | `string` | `'currentColor'` | Fill color |
| `stroke` | `string` | `'transparent'` | Stroke color |
| `decorative` | `boolean` | `false` | Hide from screen readers |
| `accessibility-title` | `string` | - | Accessible label |

---

#### scale-tooltip

Tooltip component.

```vue
<scale-tooltip content="This is helpful information">
  <scale-button>Hover me</scale-button>
</scale-tooltip>
```

---

#### scale-badge

Badge component for labels and counts.

```vue
<scale-badge>New</scale-badge>
<scale-badge count="5">Messages</scale-badge>
```

---

#### scale-tag

Tag/chip component.

```vue
<scale-tag>Default</scale-tag>
<scale-tag variant="success">Success</scale-tag>
<scale-tag dismissible @scale-close="handleRemove">Removable</scale-tag>
```

---

#### scale-divider

Visual divider.

```vue
<scale-divider />
<scale-divider vertical />
```

---

#### scale-link

Styled link component.

```vue
<scale-link href="/about" target="_blank">Learn More</scale-link>
```

---

## All Available Components (63 Total)

| Category | Components |
|----------|------------|
| **Forms** | `text-field`, `textarea`, `checkbox`, `checkbox-group`, `radio-button`, `radio-button-group`, `switch`, `dropdown-select`, `dropdown-select-item`, `slider`, `date-picker`, `rating-stars` |
| **Buttons** | `button`, `segmented-button`, `segment`, `toggle-button`, `toggle-group` |
| **Navigation** | `tab-nav`, `tab-header`, `tab-panel`, `sidebar-nav`, `sidebar-nav-item`, `sidebar-nav-collapsible`, `breadcrumb`, `pagination`, `link`, `menu-flyout`, `menu-flyout-list`, `menu-flyout-item`, `menu-flyout-divider` |
| **Layout** | `card`, `accordion`, `collapsible`, `modal`, `grid`, `grid-item`, `divider`, `list`, `list-item` |
| **Data Display** | `data-grid`, `table`, `tag`, `badge`, `notification-badge`, `chip`, `icon` |
| **Feedback** | `notification-toast`, `notification-banner`, `notification-message`, `notification`, `callout`, `alert`, `progress-bar`, `loading-spinner`, `tooltip` |
| **Other** | `carousel`, `chart-stack-card`, `dropdown`, `helper-text`, `telekom` (header/footer) |

---

## Accessibility

Scale components are built with accessibility in mind, meeting WCAG 2.1 Level AA standards.

### Built-in Accessibility Features

- **Keyboard Navigation**: All interactive components support keyboard operation
- **Screen Reader Support**: Proper ARIA attributes and announcements
- **Focus Management**: Visible focus indicators and focus trapping in modals
- **High Contrast Mode**: Support for Windows High Contrast mode
- **Reduced Motion**: Respects `prefers-reduced-motion` settings

### Best Practices

```vue
<!-- Always provide accessible labels -->
<scale-button aria-label="Close dialog">
  <scale-icon name="action-close" decorative />
</scale-button>

<!-- Use helper text for form fields -->
<scale-text-field
  label="Email Address"
  helper-text="We'll never share your email"
  required
/>

<!-- Provide accessible names for icon-only buttons -->
<scale-button icon-only inner-aria-label="Add new item">
  <scale-icon name="action-add" />
</scale-button>
```

---

## Best Practices

### 1. Use Direct Custom Element Import

```typescript
// Recommended: Import directly
import { defineCustomElements } from '@telekom/scale-components/loader'
defineCustomElements()

// NOT recommended: Using deprecated Vue wrapper package
// import { ScaleButton } from '@telekom/scale-components-vue'
```

### 2. Handle Events Properly

```vue
<!-- Use scale-prefixed events -->
<scale-text-field @scale-change="handleChange" />

<!-- NOT camelCase (deprecated) -->
<scale-text-field @scaleChange="handleChange" />
```

### 3. Create Wrapper Components for Reusability

```vue
<!-- components/FormInput.vue -->
<template>
  <scale-text-field
    :label="label"
    :value="modelValue"
    :invalid="!!error"
    :helper-text="error || helperText"
    v-bind="$attrs"
    @scale-change="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
  error?: string
  helperText?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
```

### 4. Type Custom Element Events

```typescript
// types/scale.d.ts
declare global {
  interface HTMLElementEventMap {
    'scale-change': CustomEvent<{ value: string }>
    'scale-input': CustomEvent<KeyboardEvent>
    'scale-focus': CustomEvent<void>
    'scale-blur': CustomEvent<void>
  }
}

export {}
```

### 5. Use Slots Correctly

```vue
<scale-modal>
  <!-- Default slot for body content -->
  <p>Modal body content</p>

  <!-- Named slots -->
  <template #action>
    <scale-button>Confirm</scale-button>
  </template>
</scale-modal>
```

---

## Troubleshooting

### Components Not Rendering

**Problem**: Scale components appear as unknown elements.

**Solution**: Ensure custom elements are configured correctly:

```typescript
// vite.config.ts
vue({
  template: {
    compilerOptions: {
      isCustomElement: (tag) => tag.startsWith('scale-'),
    },
  },
})
```

### Events Not Firing

**Problem**: Event handlers aren't being called.

**Solution**: Use `scale-` prefixed events:

```vue
<!-- Correct -->
<scale-text-field @scale-change="handleChange" />

<!-- Incorrect -->
<scale-text-field @change="handleChange" />
```

### v-model Not Working

**Problem**: `v-model` doesn't update values.

**Solution**: Use manual binding:

```vue
<scale-text-field
  :value="myValue"
  @scale-change="myValue = $event.target.value"
/>
```

### Styles Not Applied

**Problem**: Components appear unstyled.

**Solution**: Ensure CSS is imported:

```typescript
import '@telekom/scale-components/dist/scale-components/scale-components.css'
```

### ESLint Warnings About slot Attribute

**Problem**: ESLint complains about deprecated `slot` attribute.

**Solution**: Disable the rule:

```javascript
// .eslintrc.js
rules: {
  'vue/no-deprecated-slot-attribute': 'off',
}
```

### TypeScript Errors

**Problem**: TypeScript doesn't recognize Scale elements.

**Solution**: Add type declarations:

```typescript
// src/shims-scale.d.ts
declare namespace JSX {
  interface IntrinsicElements {
    'scale-button': any
    'scale-text-field': any
    // Add other components as needed
  }
}
```

---

## Resources

- **GitHub Repository**: [https://github.com/telekom/scale](https://github.com/telekom/scale)
- **Documentation**: [https://telekom.github.io/scale/](https://telekom.github.io/scale/)
- **NPM Package**: [@telekom/scale-components](https://www.npmjs.com/package/@telekom/scale-components)
- **Vue 3 Examples**: Check `/examples/vue3-vite-boilerplate` in the repository

---

## License

- **Code**: Mozilla Public License 2.0 (MPL-2.0)
- **Telekom Brand Assets** (logos, magenta color, typeface, icons): Require Deutsche Telekom's express permission for commercial use

For open-source projects, use the neutral packages (`@telekom/scale-components-neutral`) to avoid brand licensing restrictions.
