# Component Usage, Events, and Form Handling

This document covers how to use Scale components in Vue 3, handle events, and implement forms.

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

---

## Passing Props

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

## Event Reference by Component

| Component | Event | How to Get Value |
|-----------|-------|------------------|
| `scale-text-field` | `@scale-change` | `$event.target.value` |
| `scale-checkbox` | `@scale-change` | `$event.detail.checked` |
| `scale-switch` | `@scale-change` | `$event.detail.checked` |
| `scale-dropdown-select` | `@scale-change` | `$event.detail.value` |
| `scale-radio-button-group` | `@scale-change` | `$event.detail.value` |
| `scale-modal` | `@scale-close` | No value (just close) |
| `scale-modal` | `@scale-before-close` | Can `preventDefault()` |

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

---

## Creating Reusable v-model Wrappers

For convenience, create wrapper components that support v-model:

### ScaleInput.vue

```vue
<!-- components/scale-wrappers/ScaleInput.vue -->
<template>
  <scale-text-field
    v-bind="$attrs"
    :value="modelValue"
    :invalid="!!error"
    :helper-text="error || helperText"
    @scale-change="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  error?: string
  helperText?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
```

### ScaleCheckbox.vue

```vue
<!-- components/scale-wrappers/ScaleCheckbox.vue -->
<template>
  <scale-checkbox
    v-bind="$attrs"
    :checked="modelValue"
    @scale-change="$emit('update:modelValue', $event.detail.checked)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>
```

### ScaleSelect.vue

```vue
<!-- components/scale-wrappers/ScaleSelect.vue -->
<template>
  <scale-dropdown-select
    v-bind="$attrs"
    :value="modelValue"
    @scale-change="$emit('update:modelValue', $event.detail.value)"
  >
    <slot />
  </scale-dropdown-select>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string | number
}>()

defineEmits<{
  'update:modelValue': [value: string | number]
}>()
</script>
```

### Usage with Wrappers

```vue
<template>
  <div>
    <ScaleInput v-model="email" label="Email" type="email" />
    <ScaleCheckbox v-model="agreed" label="I agree" />
    <p>Email: {{ email }}, Agreed: {{ agreed }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ScaleInput from './scale-wrappers/ScaleInput.vue'
import ScaleCheckbox from './scale-wrappers/ScaleCheckbox.vue'

const email = ref('')
const agreed = ref(false)
</script>
```

---

## Using Slots

Scale components use standard HTML slots:

```vue
<!-- Default slot -->
<scale-button>Click Me</scale-button>

<!-- Named slots -->
<scale-modal>
  <p>Modal body content</p>

  <template #action>
    <scale-button variant="secondary">Cancel</scale-button>
    <scale-button>Confirm</scale-button>
  </template>
</scale-modal>

<!-- Icon slot -->
<scale-button>
  <scale-icon-action-add slot="icon" />
  Add Item
</scale-button>
```

---

## Anti-Patterns to Avoid

- **DO NOT** use `v-model` directly on Scale components
- **DO NOT** use camelCase events (`@scaleChange`) - use kebab-case (`@scale-change`)
- **DO NOT** use deprecated `@telekom/scale-components-vue` proxy package
- **DO NOT** forget to configure `isCustomElement` in Vue compiler options
- **DO NOT** skip importing Scale CSS file
- **DO NOT** use native `@change` events - use `@scale-change`

**Red Flags**:
- Using `<ScaleButton>` instead of `<scale-button>`
- Components rendering as plain HTML without styling
- Form values not updating on user input
- Console warnings about unknown custom elements
