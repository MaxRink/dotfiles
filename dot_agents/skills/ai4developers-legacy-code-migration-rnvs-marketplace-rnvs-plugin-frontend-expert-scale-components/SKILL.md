---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-frontend-expert-scale-components
description: Detailed Scale component reference with all 63 components, event binding patterns, and v-model wrapper implementations. Invoke when selecting components, implementing forms, or needing specific component props/events.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/frontend-expert/skills/scale-components by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Scale Components Reference

**Purpose**: Provide detailed component specifications, event handling patterns, and implementation examples for Telekom Scale Design System components in Vue 3.

**CRITICAL: Scale-First Development**
ALWAYS use Scale components instead of plain HTML elements. Only use native HTML (`<div>`, `<span>`, etc.) when NO Scale component exists for that purpose. Before using any HTML element, check if Scale has a component for it.

**When to use this skill**:
- Selecting which Scale components to use for a feature
- Implementing form components with proper event binding
- Creating v-model wrapper components
- Looking up specific component props and events
- Understanding slot usage patterns

---

## Context from Orchestrator

When this skill is invoked, you should already have:
- User's project requirements (from Step 1)
- Project setup completed (from Step 2)

Use the information from the orchestrator conversation to guide component selection.

---

## What This Skill Provides

### 1. Component Catalog (06-component-reference.md)
Complete reference for all 63 Scale components organized by category:
- **Form Controls**: text-field, checkbox, switch, dropdown-select, radio-button, textarea, date-picker
- **Buttons & Actions**: button, icon-button, link, chip, tag
- **Navigation**: tab-nav, sidebar-nav, breadcrumb, pagination, menu-flyout
- **Layout**: card, accordion, modal, tooltip, popover
- **Feedback**: notification-toast, notification-banner, progress-bar, loading-spinner
- **Data Display**: table, data-grid, list, badge
- **Telekom Brand**: telekom-header, telekom-nav-list, telekom-nav-item, telekom-footer (use these for app header/navigation/footer)

**IMPORTANT**: Always check this catalog FIRST before using any plain HTML element. If Scale has a component for it, use the Scale component.

Each component includes:
- All available props with types and defaults
- Event names and payload structures
- Vue 3 usage examples

### 2. Event Handling Patterns (03-component-usage-and-events.md)
- Scale-prefixed event binding (`@scale-change`, `@scale-input`)
- How to extract values from events
- Component-specific event reference table
- Anti-patterns to avoid

### 3. Vue Integration Examples (vue-examples.md)
- Complete form implementations
- Modal management patterns
- Search form with validation
- Data table integration
- Pinia store integration

---

## Quick Reference: Event Binding

| Component | Event | Value Extraction |
|-----------|-------|------------------|
| `scale-text-field` | `@scale-change` | `$event.target.value` |
| `scale-checkbox` | `@scale-change` | `$event.detail.checked` |
| `scale-switch` | `@scale-change` | `$event.detail.checked` |
| `scale-dropdown-select` | `@scale-change` | `$event.detail.value` |
| `scale-radio-button-group` | `@scale-change` | `$event.detail.value` |
| `scale-modal` | `@scale-close` | (no value) |
| `scale-date-picker` | `@scale-change` | `$event.detail.value` |

---

## v-Model Wrapper Templates

Since Scale components are Web Components, `v-model` doesn't work directly. Use these wrapper patterns:

### ScaleInput.vue
```vue
<template>
  <scale-text-field
    :value="modelValue"
    :label="label"
    :type="type"
    :helper-text="helperText"
    :invalid="invalid"
    @scale-change="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
  type?: string
  helperText?: string
  invalid?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
```

### ScaleCheckbox.vue
```vue
<template>
  <scale-checkbox
    :checked="modelValue"
    :label="label"
    :disabled="disabled"
    @scale-change="$emit('update:modelValue', $event.detail.checked)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
  label: string
  disabled?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>
```

### ScaleSelect.vue
```vue
<template>
  <scale-dropdown-select
    :value="modelValue"
    :label="label"
    @scale-change="$emit('update:modelValue', $event.detail.value)"
  >
    <slot />
  </scale-dropdown-select>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
```

---

## Common Component Patterns

### Form with Validation
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <scale-text-field
      :value="email"
      label="Email"
      type="email"
      :invalid="!!errors.email"
      :helper-text="errors.email"
      @scale-change="email = $event.target.value"
    />

    <scale-text-field
      :value="password"
      label="Password"
      type="password"
      :invalid="!!errors.password"
      :helper-text="errors.password"
      @scale-change="password = $event.target.value"
    />

    <scale-checkbox
      :checked="remember"
      label="Remember me"
      @scale-change="remember = $event.detail.checked"
    />

    <scale-button type="submit">Login</scale-button>
  </form>
</template>
```

### Modal Management
```vue
<template>
  <scale-button @click="isOpen = true">Open Modal</scale-button>

  <scale-modal
    :opened="isOpen"
    heading="Confirm Action"
    @scale-close="isOpen = false"
    @scale-before-close="handleBeforeClose"
  >
    <p>Are you sure you want to proceed?</p>
    <scale-button slot="action" @click="confirm">Confirm</scale-button>
    <scale-button slot="action" variant="secondary" @click="isOpen = false">
      Cancel
    </scale-button>
  </scale-modal>
</template>

<script setup>
import { ref } from 'vue'

const isOpen = ref(false)

function handleBeforeClose(event) {
  // Optionally prevent close
  // event.preventDefault()
}

function confirm() {
  // Handle confirmation
  isOpen.value = false
}
</script>
```

---

## After Using This Skill

Return to the main `scale-and-vue` workflow to:
- Continue with theming (Step 5) - invoke `scale-theming` skill
- Validate implementation (Step 7)
- Troubleshoot issues (Step 8) - invoke `scale-quality` skill

---

## Reference Files

For complete details, consult these reference files in this skill:
- `references/06-component-reference.md` - Full component catalog
- `references/03-component-usage-and-events.md` - Event patterns
- `references/vue-examples.md` - Complete Vue examples
