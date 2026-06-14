---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-frontend-expert-scale-theming
description: Design tokens and theming for Scale Design System. Invoke when implementing light/dark mode, custom branding, or needing design token values for colors, typography, spacing, and shadows.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/frontend-expert/skills/scale-theming by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Scale Theming Reference

**Purpose**: Provide comprehensive theming capabilities for Telekom Scale Design System including design tokens, light/dark mode implementation, and custom branding.

**When to use this skill**:
- Implementing light/dark mode switching
- Customizing colors or branding
- Looking up design token values
- Creating mode-aware custom styles
- Understanding the Scale design token system

---

## Context from Orchestrator

When this skill is invoked, you should already have:
- User's theming requirements (from Step 1)
- Project setup completed (from Step 2)
- Component selection done (Steps 3-4)

Use this information to configure appropriate theming.

---

## What This Skill Provides

### 1. Design Tokens (04-design-tokens.md)
Complete token reference organized by category:
- **Colors**: Primary, text, background, functional (success, warning, error, info)
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Component spacing (4-64px) and layout spacing
- **Shadows**: 5 elevation levels for depth
- **Border Radius**: From sharp (0) to pill (9999px)
- **Breakpoints**: Grid system and responsive design

### 2. Theming & Modes (05-theming-and-modes.md)
- Light/dark mode implementation
- Theme composable with localStorage persistence
- CSS variable overrides for custom branding
- Shadow parts for component customization
- Vue 3 theme provider patterns

---

## Quick Reference: Essential Tokens

### Primary Colors
```css
--telekom-color-primary-standard: #e20074;    /* Magenta */
--telekom-color-primary-hovered: #d4006d;
--telekom-color-primary-pressed: #bd0063;
```

### Text Colors (Mode-Aware)
```css
/* Light mode */
--telekom-color-text-and-icon-standard: #191919;
--telekom-color-text-and-icon-additional: #6c6c6c;

/* Dark mode (automatic when data-mode="dark") */
--telekom-color-text-and-icon-standard: #ffffff;
--telekom-color-text-and-icon-additional: #a6a6a6;
```

### Background Colors (Mode-Aware)
```css
/* Light mode */
--telekom-color-background-canvas: #ffffff;
--telekom-color-background-surface: #ffffff;
--telekom-color-background-surface-subtle: #f4f4f4;

/* Dark mode */
--telekom-color-background-canvas: #0d0d0d;
--telekom-color-background-surface: #1c1c1e;
--telekom-color-background-surface-subtle: #2c2c2e;
```

### Spacing Scale
```css
--scl-spacing-2: 2px;
--scl-spacing-4: 4px;
--scl-spacing-8: 8px;
--scl-spacing-12: 12px;
--scl-spacing-16: 16px;   /* Standard padding */
--scl-spacing-24: 24px;
--scl-spacing-32: 32px;
--scl-spacing-48: 48px;
--scl-spacing-64: 64px;
```

### Shadow Elevations
```css
--scl-shadow-level-0: none;
--scl-shadow-level-1: 0 2px 8px rgba(0,0,0,0.08);   /* Cards */
--scl-shadow-level-2: 0 4px 16px rgba(0,0,0,0.12);  /* Dropdowns */
--scl-shadow-level-3: 0 8px 24px rgba(0,0,0,0.16);  /* Modals */
--scl-shadow-level-4: 0 16px 48px rgba(0,0,0,0.24); /* Overlays */
```

---

## Light/Dark Mode Implementation

### Option 1: Follow System Preference (Automatic)
```vue
<!-- App.vue -->
<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // Check system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)')

  const setTheme = (dark: boolean) => {
    document.body.setAttribute('data-mode', dark ? 'dark' : 'light')
  }

  setTheme(prefersDark.matches)
  prefersDark.addEventListener('change', (e) => setTheme(e.matches))
})
</script>
```

### Option 2: Manual Toggle with Persistence
```typescript
// composables/useTheme.ts
import { ref, watch, onMounted } from 'vue'

type ThemeMode = 'light' | 'dark' | 'auto'

export function useTheme() {
  const mode = ref<ThemeMode>('auto')
  const resolvedMode = ref<'light' | 'dark'>('light')

  function applyTheme() {
    let targetMode: 'light' | 'dark'

    if (mode.value === 'auto') {
      targetMode = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
    } else {
      targetMode = mode.value
    }

    resolvedMode.value = targetMode
    document.body.setAttribute('data-mode', targetMode)
  }

  function setMode(newMode: ThemeMode) {
    mode.value = newMode
    localStorage.setItem('theme-mode', newMode)
    applyTheme()
  }

  function toggleMode() {
    const next = resolvedMode.value === 'light' ? 'dark' : 'light'
    setMode(next)
  }

  onMounted(() => {
    const saved = localStorage.getItem('theme-mode') as ThemeMode | null
    if (saved) {
      mode.value = saved
    }
    applyTheme()

    // Listen for system changes when in auto mode
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => {
        if (mode.value === 'auto') applyTheme()
      })
  })

  return { mode, resolvedMode, setMode, toggleMode }
}
```

### Option 3: Theme Toggle Component
```vue
<!-- ThemeToggle.vue -->
<template>
  <scale-switch
    :checked="resolvedMode === 'dark'"
    label="Dark mode"
    @scale-change="toggleMode"
  />
</template>

<script setup>
import { useTheme } from '@/composables/useTheme'
const { resolvedMode, toggleMode } = useTheme()
</script>
```

---

## Custom Branding

### Override Primary Color
```css
/* In your global CSS or App.vue <style> */
:root {
  --telekom-color-primary-standard: #0066cc;  /* Your brand blue */
  --telekom-color-primary-hovered: #0052a3;
  --telekom-color-primary-pressed: #004080;
}
```

### Override for Specific Component
```css
/* Target specific components with shadow parts */
scale-button::part(base) {
  border-radius: 4px;  /* Sharper corners */
}

scale-card::part(base) {
  border: 1px solid var(--telekom-color-ui-border-standard);
}
```

### Full Custom Theme
```css
:root {
  /* Primary colors */
  --telekom-color-primary-standard: #0066cc;
  --telekom-color-primary-hovered: #0052a3;
  --telekom-color-primary-pressed: #004080;

  /* Adjust radius for sharper look */
  --telekom-radius-standard: 4px;
  --telekom-radius-large: 8px;

  /* Custom font */
  --telekom-typography-font-family-sans: 'Inter', system-ui, sans-serif;
}
```

---

## Mode-Aware Custom Styles

When writing custom CSS, use semantic tokens that automatically adapt:

```css
.my-custom-card {
  /* These automatically change in dark mode */
  background: var(--telekom-color-background-surface);
  color: var(--telekom-color-text-and-icon-standard);
  border: 1px solid var(--telekom-color-ui-border-standard);
  box-shadow: var(--scl-shadow-level-1);
}

.my-custom-card:hover {
  box-shadow: var(--scl-shadow-level-2);
}
```

**Avoid hardcoded colors:**
```css
/* BAD - won't adapt to dark mode */
.card { background: #ffffff; color: #191919; }

/* GOOD - mode-aware */
.card {
  background: var(--telekom-color-background-surface);
  color: var(--telekom-color-text-and-icon-standard);
}
```

---

## After Using This Skill

Return to the main `scale-and-vue` workflow to:
- Continue building feature components (Step 6) - invoke `scale-components` skill
- Validate implementation (Step 7)
- Troubleshoot issues (Step 8) - invoke `scale-quality` skill

---

## Reference Files

For complete details, consult these reference files in this skill:
- `references/04-design-tokens.md` - Complete token reference
- `references/05-theming-and-modes.md` - Theming implementation details
