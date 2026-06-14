# Theming and Light/Dark Mode

This document covers light/dark mode implementation and custom theming for Scale components in Vue 3.

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

---

## Vue 3 Implementation

### Basic Toggle

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

### Theme Composable with Persistence

Create a reusable composable for theme management:

```typescript
// composables/useTheme.ts
import { ref, onMounted, watch } from 'vue'

export function useTheme() {
  const isDarkMode = ref(false)
  const userPreference = ref<'system' | 'light' | 'dark'>('system')

  const updateTheme = () => {
    if (userPreference.value === 'system') {
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    } else {
      isDarkMode.value = userPreference.value === 'dark'
    }
    document.body.setAttribute('data-mode', isDarkMode.value ? 'dark' : 'light')
  }

  onMounted(() => {
    const savedPref = localStorage.getItem('theme-preference') as any
    if (savedPref) userPreference.value = savedPref

    updateTheme()

    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => {
        if (userPreference.value === 'system') updateTheme()
      })
  })

  watch(userPreference, (newPref) => {
    localStorage.setItem('theme-preference', newPref)
    updateTheme()
  })

  const setTheme = (pref: 'system' | 'light' | 'dark') => {
    userPreference.value = pref
  }

  return { isDarkMode, userPreference, setTheme }
}
```

### Using the Theme Composable

```vue
<template>
  <div>
    <scale-dropdown-select
      label="Theme"
      :value="userPreference"
      @scale-change="setTheme($event.detail.value)"
    >
      <scale-dropdown-select-item value="system">System</scale-dropdown-select-item>
      <scale-dropdown-select-item value="light">Light</scale-dropdown-select-item>
      <scale-dropdown-select-item value="dark">Dark</scale-dropdown-select-item>
    </scale-dropdown-select>

    <p>Current mode: {{ isDarkMode ? 'Dark' : 'Light' }}</p>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { isDarkMode, userPreference, setTheme } = useTheme()
</script>
```

---

## Applying Mode-Aware Styles

Use semantic color tokens to style your application - they automatically adapt to the current mode:

```css
body {
  background-color: var(--telekom-color-background-canvas);
  color: var(--telekom-color-text-and-icon-standard);
}

.card {
  background-color: var(--telekom-color-background-surface);
  border: 1px solid var(--telekom-color-ui-border-standard);
}

.secondary-text {
  color: var(--telekom-color-text-and-icon-additional);
}
```

---

## Custom Theming

Scale components use Shadow DOM for style encapsulation. Customization is achieved through scoped CSS variables and shadow parts.

### Three Levels of Customization

1. **Single Instance**: Apply styles directly to one component
2. **Variants**: Create reusable component variations
3. **Themes**: Group customizations under a CSS class for site-wide application

---

## CSS Variable Overrides

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

---

## Shadow Parts

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

---

## Creating a Complete Theme

Group customizations under a CSS class:

```css
/* styles/custom-theme.css */
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

---

## Vue 3 Theme Provider Example

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

## Theme Configuration Questions

When setting up theming for a project, consider:

### 1. Dark Mode Strategy
- Follow system preference automatically
- Manual toggle only
- Both (system default + manual override)
- Light mode only (no dark mode)

### 2. Custom Colors (if applicable)
Override the default Telekom magenta with custom primary colors:
```css
--telekom-color-primary-standard: #0066cc;
--telekom-color-primary-hovered: #0052a3;
--telekom-color-primary-pressed: #003d7a;
```

### 3. Typography
- Use TeleNeoWeb (Telekom font)
- Use system fonts (no custom font)
- Use custom font

### 4. Border Radius Style
- Default Scale (8px standard)
- Sharper/squared (0-4px)
- Rounder (12-16px)

---

## Common Design Token Overrides

| Token | Default | Description |
|-------|---------|-------------|
| `--telekom-color-primary-standard` | `#e20074` | Primary button/link color |
| `--telekom-color-background-canvas` | `#fff` / `#000` | Page background |
| `--telekom-color-background-surface` | `#fff` / `#1c1c1e` | Card/modal backgrounds |
| `--scl-spacing-16` | `16px` | Standard padding |
| `--telekom-radius-standard` | `8px` | Default border radius |

---

## Theme Preview Template

After configuration, present theme details:

```markdown
## Theme Preview

**Mode**: System preference with manual override
**Colors**: Default Telekom magenta (or custom: #XXXXXX)
**Font**: TeleNeoWeb
**Radius**: Default (8px)

### Design Tokens in Use

| Token | Value | Usage |
|-------|-------|-------|
| `--telekom-color-primary-standard` | #e20074 | Primary buttons, links |
| `--telekom-color-background-canvas` | #fff / #000 | Page background |
| `--telekom-color-background-surface` | #fff / #1c1c1e | Card backgrounds |
| `--scl-spacing-16` | 16px | Standard padding |
| `--telekom-radius-standard` | 8px | Default border radius |
```

---

## Troubleshooting Theme Issues

### Dark Mode Not Working

**Diagnosis**:
1. Is `data-mode` attribute set on body or container?
2. Are you using semantic tokens (not hardcoded colors)?

**Check**:
```vue
<div :data-mode="isDarkMode ? 'dark' : 'light'">
  <!-- content -->
</div>
```

**CSS Check**:
```css
/* Good - adapts to mode */
color: var(--telekom-color-text-and-icon-standard);

/* Bad - ignores mode */
color: #000000;
```

### Custom Colors Not Applying

**Check**:
1. Is the theme class applied to the correct container?
2. Are CSS specificity rules blocking your overrides?
3. Is the CSS file imported after Scale's CSS?

```html
<!-- main.ts -->
import '@telekom/scale-components/dist/scale-components/scale-components.css'
import './styles/custom-theme.css'  <!-- After Scale CSS -->
```
