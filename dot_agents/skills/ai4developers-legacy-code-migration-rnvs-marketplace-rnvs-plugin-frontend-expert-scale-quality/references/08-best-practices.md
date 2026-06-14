# Best Practices

This document covers best practices for using Scale Design System with Vue 3.

---

## 1. Use Direct Custom Element Import

Always use the core package directly, not the deprecated Vue wrapper:

```typescript
// Recommended: Import directly
import { defineCustomElements } from '@telekom/scale-components/loader'
defineCustomElements()

// NOT recommended: Using deprecated Vue wrapper package
// import { ScaleButton } from '@telekom/scale-components-vue'
```

---

## 2. Handle Events Properly

Use `scale-` prefixed events in kebab-case:

```vue
<!-- Correct: scale-prefixed, kebab-case -->
<scale-text-field @scale-change="handleChange" />

<!-- Incorrect: camelCase (deprecated) -->
<scale-text-field @scaleChange="handleChange" />

<!-- Incorrect: native event (won't work) -->
<scale-text-field @change="handleChange" />
```

---

## 3. Create Wrapper Components for Reusability

Wrap Scale components to add v-model support and reduce boilerplate:

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

**Usage:**
```vue
<FormInput v-model="email" label="Email" :error="errors.email" />
```

---

## 4. Use Semantic Color Tokens

Always use semantic tokens that adapt to light/dark mode:

```css
/* Good - adapts to mode */
color: var(--telekom-color-text-and-icon-standard);
background: var(--telekom-color-background-surface);

/* Avoid hardcoded colors */
color: #000000;
background: #ffffff;
```

---

## 5. Type Custom Element Events

Add TypeScript declarations for better IDE support:

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

---

## 6. Use Slots Correctly

Named slots for complex components:

```vue
<scale-modal>
  <!-- Default slot for body content -->
  <p>Modal body content</p>

  <!-- Named slots -->
  <template #action>
    <scale-button variant="secondary">Cancel</scale-button>
    <scale-button>Confirm</scale-button>
  </template>
</scale-modal>
```

---

## 7. Configure Custom Elements Correctly

Always configure Vue to recognize Scale components:

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

---

## 8. Import CSS Styles

Never forget to import Scale's CSS:

```typescript
// main.ts
import '@telekom/scale-components/dist/scale-components/scale-components.css'
```

---

## 9. Form Validation Pattern

Implement consistent form validation:

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <scale-text-field
      label="Email"
      :value="form.email"
      :invalid="submitted && !!errors.email"
      :helper-text="submitted ? errors.email : 'Required'"
      @scale-change="form.email = $event.target.value"
      @scale-blur="validateField('email')"
    />

    <scale-button type="submit" :disabled="isSubmitting">
      Submit
    </scale-button>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'

const form = reactive({
  email: '',
})

const submitted = ref(false)
const isSubmitting = ref(false)

const errors = computed(() => ({
  email: !form.email
    ? 'Email is required'
    : !isValidEmail(form.email)
      ? 'Enter a valid email'
      : '',
}))

const isValid = computed(() => !Object.values(errors.value).some(Boolean))

const validateField = (field: string) => {
  // Trigger validation on blur
}

const handleSubmit = async () => {
  submitted.value = true
  if (!isValid.value) return

  isSubmitting.value = true
  try {
    // Submit form
  } finally {
    isSubmitting.value = false
  }
}

function isValidEmail(email: string) {
  return /\S+@\S+\.\S+/.test(email)
}
</script>
```

---

## 10. Modal Management Pattern

Handle modals with proper state management:

```vue
<template>
  <scale-button @click="openModal">Open</scale-button>

  <scale-modal
    :opened="isOpen"
    heading="Confirm Action"
    @scale-before-close="handleBeforeClose"
    @scale-close="closeModal"
  >
    <p>Are you sure?</p>

    <scale-button slot="action" variant="secondary" @click="closeModal">
      Cancel
    </scale-button>
    <scale-button slot="action" :disabled="isProcessing" @click="confirm">
      {{ isProcessing ? 'Processing...' : 'Confirm' }}
    </scale-button>
  </scale-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)
const isProcessing = ref(false)

const openModal = () => {
  isOpen.value = true
}

const closeModal = () => {
  if (!isProcessing.value) {
    isOpen.value = false
  }
}

const handleBeforeClose = (event: CustomEvent) => {
  // Prevent closing while processing
  if (isProcessing.value) {
    event.preventDefault()
  }
}

const confirm = async () => {
  isProcessing.value = true
  try {
    await performAction()
    closeModal()
  } finally {
    isProcessing.value = false
  }
}
</script>
```

---

## 11. Toast Notification Pattern

Create a composable for toast notifications:

```typescript
// composables/useToast.ts
import { ref } from 'vue'

export type ToastVariant = 'success' | 'error' | 'warning' | 'informational'

interface Toast {
  id: string
  message: string
  variant: ToastVariant
}

const toasts = ref<Toast[]>([])

export function useToast() {
  const show = (message: string, variant: ToastVariant = 'informational') => {
    const id = Date.now().toString()
    toasts.value.push({ id, message, variant })

    // Auto-remove after delay
    setTimeout(() => {
      remove(id)
    }, 5000)
  }

  const remove = (id: string) => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  const success = (message: string) => show(message, 'success')
  const error = (message: string) => show(message, 'error')
  const warning = (message: string) => show(message, 'warning')
  const info = (message: string) => show(message, 'informational')

  return {
    toasts,
    show,
    remove,
    success,
    error,
    warning,
    info,
  }
}
```

**Toast Container Component:**

```vue
<!-- components/ToastContainer.vue -->
<template>
  <div class="toast-container">
    <scale-notification-toast
      v-for="toast in toasts"
      :key="toast.id"
      :variant="toast.variant"
      :opened="true"
      @scale-close="remove(toast.id)"
    >
      {{ toast.message }}
    </scale-notification-toast>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
```

---

## 12. Loading State Pattern

Manage loading states consistently:

```vue
<template>
  <div>
    <!-- Loading overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <scale-loading-spinner text="Loading..." />
    </div>

    <!-- Content -->
    <div v-else>
      <scale-button :disabled="isSaving" @click="save">
        <scale-loading-spinner v-if="isSaving" :size="16" />
        {{ isSaving ? 'Saving...' : 'Save' }}
      </scale-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isLoading = ref(true)
const isSaving = ref(false)

// Load data
onMounted(async () => {
  isLoading.value = true
  try {
    await fetchData()
  } finally {
    isLoading.value = false
  }
})

const save = async () => {
  isSaving.value = true
  try {
    await saveData()
  } finally {
    isSaving.value = false
  }
}
</script>
```

---

## 13. Responsive Design with Scale Breakpoints

Use Scale's breakpoint system consistently:

```css
/* Mobile first approach */
.container {
  padding: var(--scl-spacing-16);
}

/* Small (640px+) */
@media (min-width: 640px) {
  .container {
    padding: var(--scl-spacing-24);
  }
}

/* Large (1040px+) */
@media (min-width: 1040px) {
  .container {
    padding: var(--telekom-spacing-composition-space-12);
    max-width: 1680px;
    margin: 0 auto;
  }
}
```

---

## Anti-Pattern Checklist

Before finalizing your implementation, verify you're NOT doing these:

- [ ] Using `v-model` directly on Scale components
- [ ] Using camelCase events (`@scaleChange`) instead of kebab-case (`@scale-change`)
- [ ] Using deprecated `@telekom/scale-components-vue` proxy package
- [ ] Forgetting to configure `isCustomElement` in Vue compiler options
- [ ] Skipping the Scale CSS import
- [ ] Using native `@change` events instead of `@scale-change`
- [ ] Using `<ScaleButton>` instead of `<scale-button>`
- [ ] Hardcoding colors instead of using design tokens
- [ ] Missing accessible labels on icon-only buttons
- [ ] Not handling form validation states properly

---

## Red Flags

Watch for these symptoms of incorrect setup. If you see any of these, something is wrong:

### Visual Red Flags

- **Components rendering as plain HTML text** - Scale elements appear as `<scale-button>Text</scale-button>` in the DOM without any styling
- **No Telekom magenta styling** - Buttons are plain browser defaults instead of styled
- **Console warnings about unknown elements** - Vue complains about `scale-*` custom elements

### Behavioral Red Flags

- **Form values not updating on user input** - Typing in fields doesn't update your data
- **Events not firing** - Click handlers and change handlers don't execute
- **v-model not working** - Two-way binding appears broken

### Code Red Flags

- **Using `<ScaleButton>` instead of `<scale-button>`** - PascalCase indicates Vue component, not custom element
- **Using `@change` instead of `@scale-change`** - Native events won't work
- **Using `@scaleChange` (camelCase)** - Events must be kebab-case
- **Importing from `@telekom/scale-components-vue`** - This package is deprecated

### Symptom-to-Cause Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Components render as plain HTML | Missing CSS import | Add `import '@telekom/scale-components/dist/scale-components/scale-components.css'` |
| Unknown element warnings in console | Missing `isCustomElement` config | Configure Vue compiler options |
| Form values not updating | Using `v-model` or wrong event | Use `:value` + `@scale-change` pattern |
| Events not firing | Using wrong event names | Use `@scale-change` (kebab-case, scale- prefix) |
| TypeScript errors on scale-* | Missing type declarations | Add `scale.d.ts` with JSX declarations |
| Dark mode not working | Not using semantic color tokens | Replace hardcoded colors with CSS variables |
| Styles look wrong in dark mode | Hardcoded colors in CSS | Use `var(--telekom-color-*)` tokens |
