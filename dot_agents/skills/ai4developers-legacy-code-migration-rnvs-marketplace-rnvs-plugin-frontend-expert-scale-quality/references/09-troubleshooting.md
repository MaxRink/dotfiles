# Troubleshooting Guide

This document covers common issues and solutions when using Scale Design System with Vue 3.

---

## Components Not Rendering

**Symptom**: Scale components appear as unknown elements or plain text.

**Solution**: Ensure custom elements are configured correctly in your build tool:

### Vite Configuration

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

### Vue CLI Configuration

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

### Diagnosis Checklist

1. [ ] Is `defineCustomElements()` called in main.ts?
2. [ ] Is `isCustomElement` configured in vite.config.ts or vue.config.js?
3. [ ] Are you using `scale-button` (lowercase) not `ScaleButton`?
4. [ ] Restart the dev server after config changes?

---

## Styles Not Applied

**Symptom**: Components appear unstyled or with broken layouts.

**Solution**: Ensure the CSS file is imported in your entry file:

```typescript
// main.ts
import '@telekom/scale-components/dist/scale-components/scale-components.css'
```

### Diagnosis Checklist

1. [ ] Is the CSS import present in main.ts?
2. [ ] Is the import path correct?
3. [ ] Is another CSS file overriding Scale styles?
4. [ ] Check for CSS specificity conflicts

---

## Events Not Firing

**Symptom**: Event handlers aren't being called.

**Solution**: Use `scale-` prefixed events in kebab-case:

```vue
<!-- Correct -->
<scale-text-field @scale-change="handleChange" />

<!-- Incorrect - native event -->
<scale-text-field @change="handleChange" />

<!-- Incorrect - camelCase (deprecated) -->
<scale-text-field @scaleChange="handleChange" />
```

### Debugging Events

Add a console log to verify events are firing:

```vue
<scale-text-field
  @scale-change="(e) => { console.log('scale-change', e); handleChange(e) }"
/>
```

### Common Event Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| No events at all | Using native events | Use `@scale-*` events |
| Value not updating | Using `v-model` | Use `:value` + `@scale-change` |
| Wrong value in event | Using `$event.value` | Use `$event.target.value` or `$event.detail.value` |

---

## v-model Not Working

**Symptom**: `v-model` doesn't update values on Scale components.

**Solution**: Use manual binding instead of v-model:

```vue
<!-- v-model doesn't work -->
<scale-text-field v-model="email" />

<!-- Manual binding works -->
<scale-text-field
  :value="email"
  @scale-change="email = $event.target.value"
/>
```

### Different Components, Different Events

| Component | Value Source |
|-----------|--------------|
| `scale-text-field` | `$event.target.value` |
| `scale-checkbox` | `$event.detail.checked` |
| `scale-switch` | `$event.detail.checked` |
| `scale-dropdown-select` | `$event.detail.value` |
| `scale-radio-button-group` | `$event.detail.value` |

---

## ESLint Warnings About slot Attribute

**Symptom**: ESLint complains about deprecated `slot` attribute.

**Solution**: Disable the rule in your ESLint config:

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'vue/no-deprecated-slot-attribute': 'off',
  },
}
```

---

## TypeScript Errors

**Symptom**: TypeScript doesn't recognize Scale elements.

**Solution**: Add type declarations:

```typescript
// src/types/scale.d.ts
declare namespace JSX {
  interface IntrinsicElements {
    'scale-button': any
    'scale-text-field': any
    'scale-checkbox': any
    'scale-dropdown-select': any
    'scale-dropdown-select-item': any
    'scale-modal': any
    'scale-card': any
    'scale-notification-toast': any
    // Add others as needed
  }
}

export {}
```

### More Specific Types

For better type safety with events:

```typescript
// types/scale.d.ts
declare global {
  interface HTMLElementEventMap {
    'scale-change': CustomEvent<{ value: string; checked?: boolean }>
    'scale-input': CustomEvent<KeyboardEvent>
    'scale-focus': CustomEvent<void>
    'scale-blur': CustomEvent<void>
    'scale-close': CustomEvent<void>
  }
}

export {}
```

---

## Dark Mode Not Working

**Symptom**: Dark mode doesn't apply or colors don't change.

**Solution**:

1. Set the `data-mode` attribute on a container element:

```vue
<div :data-mode="isDarkMode ? 'dark' : 'light'">
  <!-- content -->
</div>
```

2. Use semantic color tokens, not hardcoded values:

```css
/* Good - adapts to mode */
color: var(--telekom-color-text-and-icon-standard);

/* Bad - ignores mode */
color: #000000;
```

### Diagnosis Checklist

1. [ ] Is `data-mode` attribute set on body or container?
2. [ ] Are you using semantic color tokens?
3. [ ] Check if custom CSS overrides Scale variables
4. [ ] Verify the theme composable is working

---

## Modal Not Opening/Closing

**Symptom**: Modal doesn't respond to `opened` prop changes.

**Solution**: Ensure you're binding the prop correctly:

```vue
<template>
  <scale-button @click="isOpen = true">Open</scale-button>

  <scale-modal
    :opened="isOpen"
    @scale-close="isOpen = false"
    heading="My Modal"
  >
    Content
  </scale-modal>
</template>

<script setup>
import { ref } from 'vue'
const isOpen = ref(false)
</script>
```

### Common Modal Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Modal won't open | Using `opened` without colon | Use `:opened="isOpen"` |
| Modal won't close | Not handling `scale-close` | Add `@scale-close="isOpen = false"` |
| Close prevented | `preventDefault()` in handler | Check `scale-before-close` handler |

---

## Toast Notifications Not Showing

**Symptom**: Toast component exists but doesn't appear.

**Solution**: Call the `.open()` method on the component:

```vue
<template>
  <scale-button @click="showToast">Show Toast</scale-button>

  <scale-notification-toast
    ref="toastRef"
    variant="success"
    @scale-close="handleClose"
  >
    Success message
  </scale-notification-toast>
</template>

<script setup>
import { ref } from 'vue'

const toastRef = ref(null)

const showToast = () => {
  // Call the open() method on the element
  toastRef.value?.open()
}

const handleClose = () => {
  console.log('Toast closed')
}
</script>
```

---

## Dropdown Select Value Not Updating

**Symptom**: Selecting an option doesn't update the displayed value.

**Solution**: Bind both `:value` and handle `@scale-change`:

```vue
<scale-dropdown-select
  label="Country"
  :value="selectedCountry"
  @scale-change="selectedCountry = $event.detail.value"
>
  <scale-dropdown-select-item value="de">Germany</scale-dropdown-select-item>
  <scale-dropdown-select-item value="us">United States</scale-dropdown-select-item>
</scale-dropdown-select>
```

### Diagnosis

1. [ ] Is the initial value matching one of the item values?
2. [ ] Are you using `$event.detail.value` (not `$event.target.value`)?
3. [ ] Is the reactive variable updating correctly?

---

## Form Validation Not Showing

**Symptom**: Error states aren't visible on form fields.

**Solution**: Set both `:invalid` and `:helper-text`:

```vue
<scale-text-field
  label="Email"
  :value="email"
  :invalid="!!errors.email"
  :helper-text="errors.email"
  @scale-change="email = $event.target.value"
/>
```

### Validation Pattern

```vue
<script setup>
import { reactive, computed } from 'vue'

const form = reactive({ email: '' })

const errors = computed(() => ({
  email: !form.email
    ? 'Email is required'
    : !/\S+@\S+\.\S+/.test(form.email)
      ? 'Enter a valid email address'
      : ''
}))
</script>

<template>
  <scale-text-field
    label="Email"
    :value="form.email"
    :invalid="!!errors.email"
    :helper-text="errors.email || 'We will not share your email'"
    @scale-change="form.email = $event.target.value"
  />
</template>
```

---

## Component Methods Not Working

**Symptom**: Calling methods like `.open()` or `.close()` doesn't work.

**Solution**: Ensure you're accessing the DOM element, not the Vue component:

```vue
<template>
  <scale-modal ref="modalRef" heading="Test" />
</template>

<script setup>
import { ref, onMounted } from 'vue'

const modalRef = ref(null)

onMounted(() => {
  // In Vue 3 Composition API, the ref is the element directly
  modalRef.value?.open()
})
</script>
```

---

## Performance Issues

**Symptom**: Application feels slow with many Scale components.

**Solutions**:

### 1. Use Tree-Shaking

Import only the components you need:

```typescript
import { defineCustomElementScaleButton } from '@telekom/scale-components'
import { defineCustomElementScaleTextField } from '@telekom/scale-components'

defineCustomElementScaleButton()
defineCustomElementScaleTextField()
```

### 2. Lazy Load Heavy Components

```vue
<template>
  <Suspense>
    <scale-data-grid v-if="showGrid" :fields="columns" :rows="data" />
  </Suspense>
</template>
```

### 3. Virtual Scrolling for Long Lists

For large datasets, consider implementing virtual scrolling or pagination.

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown custom element: <scale-button>` | Missing `isCustomElement` config | Add to vite.config.ts |
| `Cannot read property 'value' of undefined` | Wrong event property | Use correct event path (`$event.target.value` or `$event.detail.value`) |
| `Property 'open' does not exist` | TypeScript doesn't know methods | Add type declarations or use `as any` |
| `Failed to resolve component: scale-*` | Vue trying to resolve as component | Configure `isCustomElement` |

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Components not rendering | Add `isCustomElement` to config |
| No styles | Import CSS in main.ts |
| Events not working | Use `@scale-*` prefix |
| v-model not working | Use `:value` + `@scale-change` |
| TypeScript errors | Add type declarations |
| Dark mode broken | Use semantic tokens + `data-mode` |
| ESLint slot warnings | Disable `vue/no-deprecated-slot-attribute` |

---

## Still Having Issues?

If you've tried the solutions above and still have problems:

1. **Check the console** for specific error messages
2. **Verify package versions** - use `@next` for latest features
3. **Review the official docs** at [https://telekom.github.io/scale/](https://telekom.github.io/scale/)
4. **Search GitHub issues** at [https://github.com/telekom/scale/issues](https://github.com/telekom/scale/issues)
5. **Create a minimal reproduction** to isolate the issue
