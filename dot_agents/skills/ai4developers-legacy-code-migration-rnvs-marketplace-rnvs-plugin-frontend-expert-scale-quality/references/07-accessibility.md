# Accessibility Guidelines

This document covers accessibility features and best practices for Scale components in Vue 3 applications.

---

## Overview

Scale components are built with accessibility in mind, meeting WCAG 2.1 Level AA standards. This ensures your applications are usable by people with disabilities, including those using assistive technologies.

---

## Built-in Accessibility Features

Scale components include the following accessibility features out of the box:

### Keyboard Navigation
All interactive components support keyboard operation:
- **Tab** to navigate between focusable elements
- **Enter/Space** to activate buttons and links
- **Arrow keys** for navigation within components (tabs, radio groups, etc.)
- **Escape** to close modals and dropdowns

### Screen Reader Support
- Proper ARIA attributes (`role`, `aria-label`, `aria-describedby`, etc.)
- Live region announcements for dynamic content
- Semantic HTML structure

### Focus Management
- Visible focus indicators on all interactive elements
- Focus trapping in modals and dialogs
- Focus restoration after modal close

### High Contrast Mode
- Support for Windows High Contrast mode
- Clear visual boundaries between elements
- Icons and graphics remain visible

### Reduced Motion
- Respects `prefers-reduced-motion` OS settings
- Animations can be disabled system-wide

---

## Best Practices

### Always Provide Accessible Labels

For icon-only buttons, provide descriptive labels:

```vue
<!-- Icon-only button with aria-label -->
<scale-button aria-label="Close dialog">
  <scale-icon name="action-close" decorative />
</scale-button>

<!-- Using inner-aria-label prop -->
<scale-button icon-only inner-aria-label="Add new item">
  <scale-icon name="action-add" />
</scale-button>
```

### Use Helper Text for Form Fields

Provide context and instructions for form inputs:

```vue
<scale-text-field
  label="Email Address"
  helper-text="We'll never share your email"
  required
/>

<scale-text-field
  label="Password"
  helper-text="Must be at least 8 characters with one uppercase letter"
  type="password"
  required
/>
```

### Mark Required Fields

Always indicate which fields are required:

```vue
<scale-text-field
  label="Username"
  required
  helper-text="Required field"
/>
```

### Provide Error Messages

Clear, descriptive error messages help all users:

```vue
<scale-text-field
  label="Email"
  :invalid="!!errors.email"
  :helper-text="errors.email || 'Enter your email address'"
  type="email"
/>
```

---

## Component-Specific Accessibility

### Buttons

```vue
<!-- Standard button - accessible by default -->
<scale-button>Submit Form</scale-button>

<!-- Icon-only button needs accessible name -->
<scale-button icon-only inner-aria-label="Delete item">
  <scale-icon name="action-delete" />
</scale-button>

<!-- Button as link -->
<scale-button href="/about" target="_blank">
  Learn More
  <span class="visually-hidden">(opens in new tab)</span>
</scale-button>
```

### Form Controls

```vue
<!-- Text fields with proper labeling -->
<scale-text-field
  label="Full Name"
  helper-text="Enter your first and last name"
  required
/>

<!-- Checkbox group with fieldset-like grouping -->
<fieldset>
  <legend>Notification Preferences</legend>
  <scale-checkbox label="Email notifications" />
  <scale-checkbox label="SMS notifications" />
  <scale-checkbox label="Push notifications" />
</fieldset>

<!-- Radio group with accessible label -->
<scale-radio-button-group label="Select your plan">
  <scale-radio-button value="basic" label="Basic - $9/month" />
  <scale-radio-button value="pro" label="Professional - $29/month" />
  <scale-radio-button value="enterprise" label="Enterprise - Custom pricing" />
</scale-radio-button-group>
```

### Modals and Dialogs

```vue
<scale-modal
  :opened="isOpen"
  heading="Confirm Deletion"
  @scale-close="isOpen = false"
>
  <p>Are you sure you want to delete this item? This action cannot be undone.</p>

  <scale-button slot="action" variant="secondary" @click="isOpen = false">
    Cancel
  </scale-button>
  <scale-button slot="action" @click="confirmDelete">
    Delete
  </scale-button>
</scale-modal>
```

**Modal Accessibility Features:**
- Focus is trapped within the modal
- Focus moves to the first focusable element when opened
- ESC key closes the modal
- Focus returns to the trigger element when closed
- Background content is hidden from screen readers

### Tables and Data Grids

```vue
<scale-data-grid
  :fields="columns"
  :rows="data"
  heading="Employee Directory"
  :selectable="true"
/>
```

For simple tables:

```vue
<scale-table>
  <table>
    <caption class="visually-hidden">Employee Directory</caption>
    <thead>
      <tr>
        <th scope="col">Name</th>
        <th scope="col">Email</th>
        <th scope="col">Department</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="employee in employees" :key="employee.id">
        <td>{{ employee.name }}</td>
        <td>{{ employee.email }}</td>
        <td>{{ employee.department }}</td>
      </tr>
    </tbody>
  </table>
</scale-table>
```

### Navigation

```vue
<!-- Tab navigation -->
<scale-tab-nav aria-label="Account settings">
  <scale-tab-header slot="tab" :selected="activeTab === 0">
    Profile
  </scale-tab-header>
  <scale-tab-header slot="tab" :selected="activeTab === 1">
    Security
  </scale-tab-header>
  <scale-tab-header slot="tab" :selected="activeTab === 2">
    Notifications
  </scale-tab-header>
  <!-- Tab panels... -->
</scale-tab-nav>

<!-- Breadcrumb navigation -->
<nav aria-label="Breadcrumb">
  <scale-breadcrumb>
    <a href="/">Home</a>
    <a href="/products">Products</a>
    <span aria-current="page">Product Details</span>
  </scale-breadcrumb>
</nav>
```

### Icons

```vue
<!-- Decorative icon (hidden from screen readers) -->
<scale-icon name="service-settings" decorative />

<!-- Meaningful icon (needs accessible name) -->
<scale-icon
  name="alert-warning"
  accessibility-title="Warning: This action is irreversible"
/>
```

---

## Keyboard Navigation Reference

| Component | Keys | Action |
|-----------|------|--------|
| `scale-button` | Enter, Space | Activate |
| `scale-checkbox` | Space | Toggle |
| `scale-switch` | Space | Toggle |
| `scale-dropdown-select` | Enter, Space, Arrow keys | Open/navigate |
| `scale-tab-nav` | Arrow keys | Navigate tabs |
| `scale-accordion` | Enter, Space | Expand/collapse |
| `scale-modal` | Escape | Close |
| `scale-data-grid` | Arrow keys | Navigate cells |

---

## Color and Contrast

### Minimum Contrast Ratios

| Text Type | Minimum Ratio | WCAG Level |
|-----------|---------------|------------|
| Normal text (< 18px) | 4.5:1 | AA |
| Large text (≥ 18px or 14px bold) | 3:1 | AA |
| UI components & graphics | 3:1 | AA |
| Enhanced (optional) | 7:1 | AAA |

### Using Semantic Colors

Always use Scale's semantic color tokens which are designed for accessibility:

```css
/* Good - meets contrast requirements */
.my-text {
  color: var(--telekom-color-text-and-icon-standard);
  background: var(--telekom-color-background-surface);
}

/* Avoid hardcoded colors that may not meet contrast requirements */
.my-text {
  color: #666666; /* May fail contrast check */
  background: #ffffff;
}
```

---

## Screen Reader Tips

### Visually Hidden Content

Provide context for screen readers that shouldn't be visible:

```vue
<template>
  <scale-button>
    <scale-icon name="action-download" decorative />
    Download
    <span class="visually-hidden">annual report PDF (2.5 MB)</span>
  </scale-button>
</template>

<style>
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
```

### Live Regions for Dynamic Content

Announce dynamic changes to screen readers:

```vue
<template>
  <div>
    <scale-button @click="saveData">Save</scale-button>
    <div role="status" aria-live="polite" class="visually-hidden">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const statusMessage = ref('')

const saveData = async () => {
  statusMessage.value = 'Saving...'
  try {
    await api.save()
    statusMessage.value = 'Data saved successfully'
  } catch {
    statusMessage.value = 'Failed to save data'
  }
}
</script>
```

---

## Testing Accessibility

### Automated Testing

Use tools like:
- **axe-core** / **@axe-core/playwright**
- **pa11y**
- **Lighthouse** accessibility audits
- **ESLint plugin vue-a11y**

### Manual Testing Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] Focus is visible on all focusable elements
- [ ] Focus order is logical
- [ ] Screen reader announces content correctly
- [ ] Color is not the only way information is conveyed
- [ ] Text can be resized to 200% without loss of functionality
- [ ] Animations respect reduced-motion preference

### Screen Reader Testing

Test with at least one of:
- **NVDA** (Windows, free)
- **JAWS** (Windows, commercial)
- **VoiceOver** (macOS/iOS, built-in)
- **Narrator** (Windows, built-in)
- **TalkBack** (Android, built-in)

---

## Common Accessibility Issues and Fixes

### Issue: Missing labels on buttons

```vue
<!-- Problem: Icon-only button without label -->
<scale-button>
  <scale-icon name="action-close" />
</scale-button>

<!-- Solution: Add accessible label -->
<scale-button aria-label="Close dialog">
  <scale-icon name="action-close" decorative />
</scale-button>
```

### Issue: Form fields without labels

```vue
<!-- Problem: No label -->
<scale-text-field placeholder="Enter email" />

<!-- Solution: Always provide label -->
<scale-text-field label="Email address" placeholder="example@email.com" />
```

### Issue: Poor error messaging

```vue
<!-- Problem: Error not associated with field -->
<scale-text-field :value="email" :invalid="hasError" />
<p class="error">Invalid email format</p>

<!-- Solution: Use helper-text for error -->
<scale-text-field
  :value="email"
  :invalid="hasError"
  :helper-text="hasError ? 'Please enter a valid email address' : ''"
/>
```

### Issue: Links that don't indicate new windows

```vue
<!-- Problem: No indication that link opens in new tab -->
<scale-link href="/external" target="_blank">External Site</scale-link>

<!-- Solution: Indicate behavior -->
<scale-link href="/external" target="_blank">
  External Site (opens in new tab)
</scale-link>
```
