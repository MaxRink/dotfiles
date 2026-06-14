# Complete Component Reference

This document provides a comprehensive reference for all 63 Scale components organized by category.

---

## All Available Components (63+ Total)

| Category | Components |
|----------|------------|
| **Forms** | `text-field`, `textarea`, `checkbox`, `checkbox-group`, `radio-button`, `radio-button-group`, `switch`, `dropdown`, `dropdown-select`, `dropdown-select-item`, `slider`, `date-picker`, `rating-stars` |
| **Buttons** | `button`, `segmented-button`, `segment`, `toggle-button`, `toggle-group` |
| **Navigation** | `tab-nav`, `tab-header`, `tab-panel`, `sidebar-nav`, `sidebar-nav-item`, `sidebar-nav-collapsible`, `breadcrumb`, `pagination`, `link`, `menu-flyout`, `menu-flyout-list`, `menu-flyout-item`, `menu-flyout-divider` |
| **Layout** | `card`, `accordion`, `collapsible`, `modal`, `grid`, `grid-item`, `divider`, `list`, `list-item` |
| **Data Display** | `data-grid`, `table`, `tag`, `badge`, `notification-badge`, `chip`, `icon` |
| **Feedback** | `notification`, `notification-toast`, `notification-banner`, `notification-message`, `callout`, `alert`, `progress-bar`, `loading-spinner`, `tooltip` |
| **Telekom Brand** | `logo`, `telekom-header`, `telekom-nav-list`, `telekom-nav-item`, `telekom-footer`, `telekom-mega-menu`, `telekom-nav-flyout` |
| **Other** | `carousel`, `chart-stack-card`, `helper-text` |

---

## Form Components

### scale-text-field

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

### scale-checkbox

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

### scale-dropdown-select

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

### scale-radio-button-group

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

### scale-switch

Toggle switch component.

```vue
<scale-switch
  label="Enable notifications"
  :checked="isEnabled"
  @scale-change="isEnabled = $event.detail.checked"
/>
```

---

### scale-textarea

Multi-line text input for longer content.

```vue
<template>
  <scale-textarea
    label="Comments"
    placeholder="Enter your comments..."
    :value="comments"
    :rows="5"
    :max-length="500"
    :counter="true"
    helper-text="Maximum 500 characters"
    :invalid="hasError"
    :required="true"
    resize="vertical"
    @scale-change="comments = $event.target.value"
    @scale-input="handleInput"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const comments = ref('')
const hasError = ref(false)

const handleInput = (event: CustomEvent) => {
  hasError.value = comments.value.length < 10
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `''` | Field label |
| `value` | `string \| number` | `''` | Current value |
| `placeholder` | `string` | `''` | Placeholder text |
| `rows` | `number` | - | Number of visible rows |
| `cols` | `number` | - | Number of visible columns |
| `helper-text` | `string` | `''` | Helper/error text |
| `invalid` | `boolean` | `false` | Show error state |
| `variant` | `'informational' \| 'warning' \| 'danger' \| 'success'` | `'informational'` | Visual variant |
| `disabled` | `boolean` | `false` | Disable input |
| `readonly` | `boolean` | `false` | Read-only mode |
| `required` | `boolean` | `false` | Mark as required |
| `max-length` | `number` | - | Maximum characters |
| `min-length` | `number` | - | Minimum characters |
| `counter` | `boolean` | `false` | Show character counter |
| `resize` | `'unset' \| 'none' \| 'vertical' \| 'horizontal'` | `'unset'` | Resize behavior |
| `transparent` | `boolean` | `false` | Transparent background |
| `input-autofocus` | `boolean` | `false` | Auto-focus on load |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Value changed (on blur) |
| `scale-input` | Value changing (on input) |
| `scale-focus` | Field gained focus |
| `scale-blur` | Field lost focus |
| `scale-keydown` | Key pressed |

---

### scale-checkbox-group

Checkbox group with parent control for selecting multiple related options.

```vue
<template>
  <scale-checkbox-group
    label="Select Features"
    helper-text="Choose the features you want to enable"
    :invalid="hasError"
    @scale-change="handleGroupChange"
  >
    <scale-checkbox
      label="Dark Mode"
      :checked="features.darkMode"
      @scale-change="features.darkMode = $event.detail.checked"
    />
    <scale-checkbox
      label="Notifications"
      :checked="features.notifications"
      @scale-change="features.notifications = $event.detail.checked"
    />
    <scale-checkbox
      label="Auto-save"
      :checked="features.autoSave"
      @scale-change="features.autoSave = $event.detail.checked"
    />
  </scale-checkbox-group>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const features = reactive({
  darkMode: false,
  notifications: true,
  autoSave: false
})
const hasError = ref(false)

const handleGroupChange = (event: CustomEvent) => {
  console.log('Group changed:', event.detail)
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `''` | Group label |
| `name` | `string` | - | Form field name |
| `helper-text` | `string` | - | Helper text |
| `invalid` | `boolean` | `false` | Show error state |
| `value` | `string` | - | Input value |
| `aria-label-checkbox-group` | `string` | - | Accessible label |
| `select-text` | `string` | `'Select all'` | Text for select all action |
| `unselect-text` | `string` | `'Unselect all'` | Text for unselect all action |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Fired when any checkbox changes |

---

### scale-date-picker

Date selection component with calendar popup.

```vue
<template>
  <scale-date-picker
    label="Select Date"
    :value="selectedDate"
    placeholder="YYYY-MM-DD"
    :min="minDate"
    :max="maxDate"
    :required="true"
    helper-text="Choose a date within the next 30 days"
    :invalid="hasError"
    :first-day-of-week="1"
    direction="right"
    @scale-change="handleDateChange"
    @scale-focus="handleFocus"
    @scale-blur="handleBlur"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const selectedDate = ref('')
const hasError = ref(false)

const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const maxDate = computed(() => {
  const future = new Date()
  future.setDate(future.getDate() + 30)
  return future.toISOString().split('T')[0]
})

const handleDateChange = (event: CustomEvent) => {
  selectedDate.value = event.detail.value
  hasError.value = false
}

const handleFocus = () => console.log('Date picker focused')
const handleBlur = () => console.log('Date picker blurred')
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `''` | Field label |
| `value` | `string` | `''` | Selected date (ISO-8601: YYYY-MM-DD) |
| `placeholder` | `string` | `''` | Placeholder text |
| `min` | `string` | `''` | Minimum date (ISO-8601) |
| `max` | `string` | `''` | Maximum date (ISO-8601) |
| `disabled` | `boolean` | `false` | Disable picker |
| `required` | `boolean` | `false` | Mark as required |
| `invalid` | `boolean` | `false` | Show error state |
| `helper-text` | `string` | `''` | Helper text |
| `variant` | `'informational' \| 'warning' \| 'danger' \| 'success'` | `'informational'` | Visual variant |
| `first-day-of-week` | `number` | `1` | Week start (0=Sunday, 1=Monday) |
| `direction` | `'left' \| 'right'` | `'right'` | Calendar opening direction |
| `localization` | `object` | - | Localized text labels |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Date selected |
| `scale-focus` | Input gained focus |
| `scale-blur` | Input lost focus |

**Methods:**
| Method | Description |
|--------|-------------|
| `setFocus()` | Focus the input |
| `show()` | Open the calendar |
| `hide()` | Close the calendar |

---

### scale-dropdown

Native select dropdown for simple option selection.

```vue
<template>
  <scale-dropdown
    label="Select Country"
    :value="selectedCountry"
    :required="true"
    :invalid="hasError"
    helper-text="Please select your country"
    @scale-change="selectedCountry = $event.target.value"
  >
    <option value="">-- Select --</option>
    <option value="de">Germany</option>
    <option value="at">Austria</option>
    <option value="ch">Switzerland</option>
  </scale-dropdown>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedCountry = ref('')
const hasError = ref(false)
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | Field label |
| `value` | `any` | - | Selected value |
| `name` | `string` | - | Form field name |
| `disabled` | `boolean` | `false` | Disable dropdown |
| `required` | `boolean` | `false` | Mark as required |
| `invalid` | `boolean` | `false` | Show error state |
| `helper-text` | `string` | `''` | Helper text |
| `variant` | `'informational' \| 'warning' \| 'danger' \| 'success'` | `'informational'` | Visual variant |
| `multiple` | `boolean` | `false` | Allow multiple selection |
| `visible-size` | `number` | - | Visible options count |
| `transparent` | `boolean` | `false` | Transparent background |
| `hide-label-visually` | `boolean` | `false` | Visually hide label |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Value changed |
| `scale-input` | Keyboard input occurred |
| `scale-focus` | Input gained focus |
| `scale-blur` | Input lost focus |
| `scale-keydown` | Key pressed |

**Slots:**
| Slot | Description |
|------|-------------|
| default | Native `<option>` elements |
| `icon` | Custom dropdown icon |

---

### scale-slider

Range slider for value selection.

```vue
<template>
  <!-- Single value slider -->
  <scale-slider
    label="Volume"
    :value="volume"
    :min="0"
    :max="100"
    :step="5"
    :show-value="true"
    unit="%"
    unit-position="after"
    @scale-change="volume = $event.detail"
    @scale-input="handleInput"
  />

  <!-- Range slider -->
  <scale-slider
    label="Price Range"
    :range="true"
    :value-from="priceMin"
    :value-to="priceMax"
    :min="0"
    :max="1000"
    :step="10"
    :show-value="true"
    unit="€"
    unit-position="before"
    @scale-change="handleRangeChange"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const volume = ref(50)
const priceMin = ref(100)
const priceMax = ref(500)

const handleInput = (event: CustomEvent) => {
  console.log('Current value:', event.detail)
}

const handleRangeChange = (event: CustomEvent) => {
  const [min, max] = event.detail
  priceMin.value = min
  priceMax.value = max
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | Slider label |
| `value` | `number` | `0` | Current value (single mode) |
| `range` | `boolean` | `false` | Enable range mode |
| `value-from` | `number` | `0` | Range start value |
| `value-to` | `number` | `0` | Range end value |
| `min` | `number` | `0` | Minimum value |
| `max` | `number` | `100` | Maximum value |
| `step` | `number` | `1` | Step increment |
| `show-step-marks` | `boolean` | `false` | Show step markers |
| `show-value` | `boolean` | `true` | Show current value |
| `unit` | `string` | `''` | Unit label (%, €, etc.) |
| `unit-position` | `'before' \| 'after'` | `'after'` | Unit placement |
| `decimals` | `0 \| 1 \| 2` | `0` | Decimal places |
| `disabled` | `boolean` | `false` | Disable slider |
| `helper-text` | `string` | - | Helper text |

**Events:**
| Event | Detail | Description |
|-------|--------|-------------|
| `scale-change` | `number \| [number, number]` | Value changed (on release) |
| `scale-input` | `number \| [number, number]` | Value changing (during drag) |

---

### scale-rating-stars

Star rating component for feedback collection.

```vue
<template>
  <!-- Interactive rating -->
  <scale-rating-stars
    label="Rate this product"
    :rating="userRating"
    :max="5"
    size="large"
    info-text="Based on 42 reviews"
    @scale-change="userRating = $event.detail"
  />

  <!-- Read-only display -->
  <scale-rating-stars
    label="Average Rating"
    :rating="averageRating"
    :max="5"
    :readonly="true"
    size="small"
    info-text="4.2 out of 5 stars"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const userRating = ref(0)
const averageRating = ref(4.2)
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `'Rating'` | Accessible label |
| `rating` | `number` | `0` | Current rating value |
| `max` | `number` | `5` | Maximum stars |
| `size` | `'small' \| 'large'` | `'large'` | Star size |
| `readonly` | `boolean` | `false` | Display-only mode |
| `disabled` | `boolean` | `false` | Disable interaction |
| `hide-label` | `boolean` | `false` | Hide the label |
| `info-text` | `string` | - | Additional info text |
| `aria-label-translation` | `string` | `'$rating out of $max stars'` | A11y label pattern |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Rating changed |

---

## Button Components

### scale-button

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

### scale-segmented-button

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

## Layout Components

### scale-card

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

### scale-accordion

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

### scale-modal

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

## Navigation Components

### scale-tab-nav

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

### scale-sidebar-nav

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

### scale-breadcrumb

Breadcrumb navigation.

```vue
<scale-breadcrumb>
  <a href="/">Home</a>
  <a href="/products">Products</a>
  <span>Current Page</span>
</scale-breadcrumb>
```

---

### scale-pagination

Pagination component for navigating through multi-page content.

```vue
<template>
  <scale-pagination
    :total-elements="totalItems"
    :page-size="itemsPerPage"
    :start-element="startIndex"
    :hide-border="false"
    :aria-label-first-page="'Go to first page'"
    :aria-label-previous-page="'Go to previous page'"
    :aria-label-next-page="'Go to next page'"
    :aria-label-last-page="'Go to last page'"
    @scale-pagination="handlePageChange"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalItems = ref(150)

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)

const handlePageChange = (event: CustomEvent) => {
  const { startElement, currentPage: newPage, direction } = event.detail
  currentPage.value = newPage
  console.log(`Navigated ${direction} to page ${newPage}`)
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `total-elements` | `number` | `1` | Total number of items |
| `page-size` | `number` | `10` | Items per page |
| `start-element` | `number` | `0` | Index of first displayed item |
| `hide-border` | `boolean` | `false` | Hide top/bottom borders |
| `aria-label-first-page` | `string` | `'Go to first page'` | A11y label |
| `aria-label-previous-page` | `string` | - | A11y label |
| `aria-label-next-page` | `string` | - | A11y label |
| `aria-label-last-page` | `string` | - | A11y label |

**Events:**
| Event | Detail | Description |
|-------|--------|-------------|
| `scale-pagination` | `{ startElement, currentPage, direction }` | Page changed |

---

### scale-menu-flyout

Flyout menu for contextual actions and navigation.

```vue
<template>
  <scale-menu-flyout
    direction="bottom-right"
    :close-on-select="true"
  >
    <scale-button slot="trigger">
      Actions
      <scale-icon-navigation-collapse-down slot="icon" />
    </scale-button>

    <scale-menu-flyout-list>
      <scale-menu-flyout-item @scale-select="handleEdit">
        <scale-icon-action-edit /> Edit
      </scale-menu-flyout-item>
      <scale-menu-flyout-item @scale-select="handleDuplicate">
        <scale-icon-action-copy-paste /> Duplicate
      </scale-menu-flyout-item>
      <scale-menu-flyout-divider />
      <scale-menu-flyout-item @scale-select="handleDelete">
        <scale-icon-action-remove /> Delete
      </scale-menu-flyout-item>
    </scale-menu-flyout-list>
  </scale-menu-flyout>

  <!-- Nested flyout menu -->
  <scale-menu-flyout direction="bottom-right">
    <scale-button slot="trigger">More Options</scale-button>

    <scale-menu-flyout-list>
      <scale-menu-flyout-item cascade>
        Export As
        <scale-menu-flyout-list slot="sublist">
          <scale-menu-flyout-item @scale-select="exportPDF">PDF</scale-menu-flyout-item>
          <scale-menu-flyout-item @scale-select="exportCSV">CSV</scale-menu-flyout-item>
          <scale-menu-flyout-item @scale-select="exportExcel">Excel</scale-menu-flyout-item>
        </scale-menu-flyout-list>
      </scale-menu-flyout-item>
    </scale-menu-flyout-list>
  </scale-menu-flyout>
</template>

<script setup lang="ts">
const handleEdit = () => console.log('Edit clicked')
const handleDuplicate = () => console.log('Duplicate clicked')
const handleDelete = () => console.log('Delete clicked')
const exportPDF = () => console.log('Export PDF')
const exportCSV = () => console.log('Export CSV')
const exportExcel = () => console.log('Export Excel')
</script>
```

**Props (scale-menu-flyout):**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `direction` | `'bottom-right' \| 'bottom-left' \| 'top-right' \| 'top-left' \| 'right' \| 'left'` | `'bottom-right'` | Menu position |
| `close-on-select` | `boolean` | `true` | Close menu on item selection |
| `trigger-has-popup` | `boolean` | `true` | Add aria-haspopup to trigger |

**Methods:**
| Method | Description |
|--------|-------------|
| `toggle()` | Open/close the menu |
| `closeAll()` | Close all open menus |

**Slots:**
| Slot | Description |
|------|-------------|
| `trigger` | Button that opens the menu |
| default | Menu list content |

**Events (scale-menu-flyout-item):**
| Event | Description |
|-------|-------------|
| `scale-select` | Item was selected |

---

## Data Display Components

### scale-data-grid

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

### scale-table

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

### scale-chip

Chip component for filtering, tagging, and user selections.

```vue
<template>
  <!-- Persistent chip (toggleable) -->
  <scale-chip
    label="Active Filter"
    variant="standard"
    type="persistent"
    :selected="isSelected"
    @scale-change="isSelected = !isSelected"
  />

  <!-- Dynamic chip (dismissible) -->
  <scale-chip
    label="Removable Tag"
    variant="outline"
    type="dynamic"
    @scale-close="handleRemove"
  />

  <!-- Chip with icon -->
  <scale-chip label="Location">
    <scale-icon-navigation-location slot="chip-icon" />
  </scale-chip>

  <!-- Disabled chip -->
  <scale-chip
    label="Unavailable"
    :disabled="true"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isSelected = ref(false)

const handleRemove = () => {
  console.log('Chip removed')
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | Chip label text |
| `variant` | `'standard' \| 'outline'` | `'standard'` | Visual style |
| `type` | `'persistent' \| 'dynamic'` | `'persistent'` | Behavior type |
| `selected` | `boolean` | `false` | Selection state |
| `disabled` | `boolean` | `false` | Disable interaction |
| `dismiss-text` | `string` | `'dismiss'` | Close button label |
| `aria-role-title` | `'switch' \| 'checkbox' \| 'radio'` | `'switch'` | ARIA role |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-change` | Selection state changed |
| `scale-close` | Close button clicked (dynamic type) |

**Slots:**
| Slot | Description |
|------|-------------|
| `chip-icon` | Icon before label |
| default | Label text content |

---

### scale-notification-badge

Badge indicator for notifications and counts.

```vue
<template>
  <!-- Badge on icon -->
  <scale-notification-badge :label="unreadCount" type="icon">
    <scale-icon-communication-email />
  </scale-notification-badge>

  <!-- Badge on text -->
  <scale-notification-badge :label="messageCount" type="text">
    <span>Messages</span>
  </scale-notification-badge>

  <!-- Badge on navigation icon -->
  <scale-notification-badge :label="alertCount" type="nav-icon">
    <scale-icon-alert-imprint-dataprivacy />
  </scale-notification-badge>

  <!-- Large number (auto-formats with SI notation) -->
  <scale-notification-badge :label="1500" :max-characters="3" type="icon">
    <scale-icon-communication-email />
  </scale-notification-badge>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const unreadCount = ref(5)
const messageCount = ref(12)
const alertCount = ref(3)
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `number` | - | Badge count value |
| `max-characters` | `number` | `3` | Max digits before SI notation |
| `type` | `'icon' \| 'text' \| 'nav-icon'` | `'icon'` | Badge placement type |
| `click-handler` | `function` | - | Click handler |

**Slots:**
| Slot | Description |
|------|-------------|
| default | Content the badge is attached to |
| `after-badge` | Content after the badge circle |

---

### scale-list

Ordered and unordered list component.

```vue
<template>
  <!-- Unordered list -->
  <scale-list>
    <scale-list-item>First item</scale-list-item>
    <scale-list-item>Second item</scale-list-item>
    <scale-list-item>
      Third item with nested list
      <scale-list slot="nested">
        <scale-list-item>Nested item 1</scale-list-item>
        <scale-list-item>Nested item 2</scale-list-item>
      </scale-list>
    </scale-list-item>
  </scale-list>

  <!-- Ordered list -->
  <scale-list :ordered="true">
    <scale-list-item>Step one</scale-list-item>
    <scale-list-item>Step two</scale-list-item>
    <scale-list-item>Step three</scale-list-item>
  </scale-list>
</template>
```

**Props (scale-list):**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `ordered` | `boolean` | `false` | Render as numbered list |

**Slots:**
| Slot | Description |
|------|-------------|
| default | `scale-list-item` elements |
| `nested` | Nested list (on scale-list-item) |

---

## Feedback Components

### scale-notification-toast

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

### scale-notification-banner

Banner notification component.

```vue
<scale-notification-banner variant="warning" :opened="showBanner">
  <span slot="heading">Warning</span>
  Your session will expire in 5 minutes.
</scale-notification-banner>
```

---

### scale-notification

Versatile notification component supporting inline, banner, and toast display types.

```vue
<template>
  <!-- Inline notification -->
  <scale-notification
    type="inline"
    variant="success"
    heading="Success!"
    :opened="showInline"
    :dismissible="true"
    @scale-close="showInline = false"
  >
    <span slot="text">Your changes have been saved.</span>
  </scale-notification>

  <!-- Banner notification -->
  <scale-notification
    type="banner"
    variant="warning"
    heading="Maintenance Notice"
    :opened="showBanner"
    :dismissible="true"
    inner-role="status"
    @scale-close="showBanner = false"
  >
    <span slot="text">Scheduled maintenance in 30 minutes.</span>
  </scale-notification>

  <!-- Toast notification with auto-dismiss -->
  <scale-notification
    ref="toastRef"
    type="toast"
    variant="informational"
    heading="New Message"
    :delay="5000"
    :dismissible="true"
    @scale-close="handleToastClose"
  >
    <span slot="text">You have a new message from support.</span>
  </scale-notification>

  <scale-button @click="showToast">Show Toast</scale-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showInline = ref(true)
const showBanner = ref(true)
const toastRef = ref<HTMLElement | null>(null)

const showToast = () => {
  (toastRef.value as any)?.open()
}

const handleToastClose = () => {
  console.log('Toast closed')
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'inline' \| 'banner' \| 'toast'` | `'inline'` | Display type |
| `variant` | `'informational' \| 'success' \| 'warning' \| 'danger'` | `'informational'` | Visual variant |
| `heading` | `string` | - | Notification heading |
| `opened` | `boolean` | `false` | Visibility state |
| `dismissible` | `boolean` | `false` | Show close button |
| `delay` | `number` | - | Auto-close delay (ms) |
| `inner-role` | `'alert' \| 'status'` | `'alert'` | ARIA role |
| `close-button-label` | `string` | `'Close'` | Close button a11y label |
| `close-button-title` | `string` | `'Close'` | Close button title |
| `heading-level` | `number` | `2` | Semantic heading level |
| `aria-heading` | `string` | `'Information'` | Heading a11y prefix |

**Events:**
| Event | Description |
|-------|-------------|
| `scale-open` | Notification opened |
| `scale-before-close` | Before closing (preventable) |
| `scale-close` | Notification closed |

**Methods:**
| Method | Description |
|--------|-------------|
| `open()` | Open the notification |
| `close()` | Close the notification |

**Slots:**
| Slot | Description |
|------|-------------|
| `icon` | Custom icon |
| `heading` | Heading content |
| `text` | Body text content |
| `close-icon` | Custom close icon |

---

### scale-callout

Visual callout component for highlighting important content.

```vue
<template>
  <!-- Primary callout -->
  <scale-callout variant="primary" :rotation="0">
    <span>Important notice!</span>
  </scale-callout>

  <!-- Rotated callout -->
  <scale-callout
    variant="blue"
    :rotation="-5"
    top="20px"
    right="10px"
  >
    <span>New Feature</span>
  </scale-callout>

  <!-- Positioned callout -->
  <div style="position: relative;">
    <scale-callout
      variant="white"
      :rotation="3"
      top="-10px"
      left="50%"
    >
      <span>Sale!</span>
    </scale-callout>
  </div>
</template>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'blue' \| 'white' \| 'black'` | `'primary'` | Color variant |
| `rotation` | `number` | `0` | Rotation angle in degrees |
| `top` | `string` | - | CSS top position |
| `right` | `string` | - | CSS right position |
| `bottom` | `string` | - | CSS bottom position |
| `left` | `string` | - | CSS left position |

**CSS Parts:**
| Part | Description |
|------|-------------|
| `base` | Main container element |

---

### scale-progress-bar

Progress indicator.

```vue
<scale-progress-bar
  :percentage="progress"
  :show-status="true"
  label="Upload Progress"
/>
```

---

### scale-loading-spinner

Loading spinner component.

```vue
<scale-loading-spinner
  :size="48"
  text="Loading..."
  variant="primary"
/>
```

---

## Utility Components

### scale-icon

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

### scale-tooltip

Tooltip component.

```vue
<scale-tooltip content="This is helpful information">
  <scale-button>Hover me</scale-button>
</scale-tooltip>
```

---

### scale-badge

Badge component for labels and counts.

```vue
<scale-badge>New</scale-badge>
<scale-badge count="5">Messages</scale-badge>
```

---

### scale-tag

Tag/chip component.

```vue
<scale-tag>Default</scale-tag>
<scale-tag variant="success">Success</scale-tag>
<scale-tag dismissible @scale-close="handleRemove">Removable</scale-tag>
```

---

### scale-divider

Visual divider.

```vue
<scale-divider />
<scale-divider vertical />
```

---

### scale-link

Styled link component.

```vue
<scale-link href="/about" target="_blank">Learn More</scale-link>
```

---

## Telekom Brand Components

### scale-logo

Telekom brand logo component for header integration.

```vue
<template>
  <!-- Standard magenta logo -->
  <scale-logo
    variant="magenta"
    :size="38"
    href="/"
    logo-title="Telekom Logo - Go to homepage"
    :focusable="true"
  />

  <!-- White logo for dark backgrounds -->
  <scale-logo
    variant="white"
    :size="48"
    href="/"
    :transparent="true"
    logo-title="Telekom"
  />

  <!-- Non-focusable decorative logo -->
  <scale-logo
    variant="magenta"
    :size="32"
    :focusable="false"
    :logo-aria-hidden="true"
  />
</template>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'magenta' \| 'white'` | `'magenta'` | Logo color scheme |
| `size` | `number` | `38` | Height in pixels |
| `href` | `string` | `'javascript:void(0);'` | Link destination |
| `logo-title` | `string` | `'Telekom Logo'` | Title/tooltip text |
| `logo-hide-title` | `boolean` | `false` | Hide title attribute |
| `focusable` | `boolean` | `true` | Enable keyboard focus |
| `scroll-into-view-on-focus` | `boolean` | `false` | Scroll to top on focus |
| `transparent` | `boolean` | `false` | Remove background fill |
| `logo-aria-described-by` | `string` | - | Associated description ID |
| `logo-aria-hidden` | `boolean` | `false` | Hide from screen readers |

---

### scale-telekom-header

Telekom brand header component with navigation slots.

```vue
<template>
  <scale-telekom-header
    app-name="My Application"
    app-name-link="/"
    logo-href="https://telekom.de"
    logo-title="Go to Telekom homepage"
    meta-nav-aria-label="Meta navigation"
    main-nav-aria-label="Main navigation"
  >
    <!-- Logo slot (optional - uses default Telekom logo) -->
    <scale-logo slot="logo" variant="magenta" :size="38" href="/" />

    <!-- Meta navigation (top right) -->
    <nav slot="meta-nav">
      <a href="/help">Help</a>
      <a href="/contact">Contact</a>
    </nav>

    <!-- Language switcher -->
    <div slot="lang-switcher">
      <scale-dropdown-select :value="currentLang" @scale-change="changeLang">
        <scale-dropdown-select-item value="de">DE</scale-dropdown-select-item>
        <scale-dropdown-select-item value="en">EN</scale-dropdown-select-item>
      </scale-dropdown-select>
    </div>

    <!-- Main navigation -->
    <scale-telekom-nav-list slot="main-nav" aria-label="Main Navigation">
      <scale-telekom-nav-item aria-label="Products">
        <a href="/products">Products</a>
      </scale-telekom-nav-item>
      <scale-telekom-nav-item aria-label="Services">
        <a href="/services">Services</a>
      </scale-telekom-nav-item>
      <scale-telekom-nav-item aria-label="About">
        <a href="/about">About</a>
      </scale-telekom-nav-item>
    </scale-telekom-nav-list>

    <!-- Functions slot (e.g., search, user menu) -->
    <div slot="functions">
      <scale-button variant="ghost" icon-only>
        <scale-icon-action-search />
      </scale-button>
      <scale-button variant="ghost" icon-only>
        <scale-icon-user-file-user />
      </scale-button>
    </div>
  </scale-telekom-header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentLang = ref('de')

const changeLang = (event: CustomEvent) => {
  currentLang.value = event.detail.value
}
</script>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `app-name` | `string` | - | Application name display |
| `app-name-link` | `string` | - | App name link URL |
| `app-name-click` | `function` | - | App name click handler |
| `logo-href` | `string` | - | Logo link destination |
| `logo-title` | `string` | - | Logo title attribute |
| `logo-hide-title` | `boolean` | - | Hide logo title |
| `type` | `string` | `''` | Header variant type |
| `meta-nav-aria-label` | `string` | `'Meta navigation'` | A11y label |
| `meta-nav-external-aria-label` | `string` | `'External meta navigation'` | A11y label |
| `lang-switcher-aria-label` | `string` | `'Language switcher'` | A11y label |
| `main-nav-aria-label` | `string` | `'Main navigation'` | A11y label |

**Slots:**
| Slot | Description |
|------|-------------|
| `logo` | Custom logo component |
| `meta-nav-external` | External meta navigation |
| `meta-nav` | Meta navigation links |
| `lang-switcher` | Language selector |
| `main-nav` | Main navigation links (use `scale-telekom-nav-list`) |
| `functions` | Utility buttons (search, user, etc.) |

---

### scale-telekom-nav-list

Container component for navigation items within `scale-telekom-header`. Use in the `main-nav` slot.

```vue
<scale-telekom-nav-list slot="main-nav" aria-label="Main Navigation">
  <scale-telekom-nav-item aria-label="Dashboard">
    <a href="/dashboard">Dashboard</a>
  </scale-telekom-nav-item>
  <scale-telekom-nav-item aria-label="Reports">
    <a href="/reports">Reports</a>
  </scale-telekom-nav-item>
  <scale-telekom-nav-item aria-label="Settings" active>
    <a href="/settings">Settings</a>
  </scale-telekom-nav-item>
</scale-telekom-nav-list>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `aria-label` | `string` | - | Accessible label for the navigation list |
| `alignment` | `'left' \| 'center' \| 'right'` | `'left'` | Alignment of nav items |

---

### scale-telekom-nav-item

Individual navigation item within `scale-telekom-nav-list`. Wraps anchor tags or router-links.

```vue
<!-- Basic usage -->
<scale-telekom-nav-item aria-label="Home">
  <a href="/">Home</a>
</scale-telekom-nav-item>

<!-- Active state -->
<scale-telekom-nav-item aria-label="Current Page" active>
  <a href="/current">Current Page</a>
</scale-telekom-nav-item>

<!-- With Vue Router -->
<scale-telekom-nav-item aria-label="Dashboard">
  <router-link to="/dashboard">Dashboard</router-link>
</scale-telekom-nav-item>

<!-- With dropdown/mega menu -->
<scale-telekom-nav-item aria-label="Products" has-children>
  <a href="/products">Products</a>
  <scale-telekom-mega-menu slot="children">
    <!-- mega menu content -->
  </scale-telekom-mega-menu>
</scale-telekom-nav-item>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `aria-label` | `string` | - | Accessible label for the nav item |
| `active` | `boolean` | `false` | Marks item as currently active |
| `has-children` | `boolean` | `false` | Indicates item has submenu/dropdown |

**Slots:**
| Slot | Description |
|------|-------------|
| default | The navigation link (`<a>` or `<router-link>`) |
| `children` | Submenu content (mega-menu or flyout) |

---

### scale-telekom-footer

Telekom brand footer component.

```vue
<template>
  <!-- Standard footer -->
  <scale-telekom-footer type="standard">
    <div slot="extended-navigation">
      <div class="footer-column">
        <h4>Products</h4>
        <ul>
          <li><a href="/mobile">Mobile</a></li>
          <li><a href="/internet">Internet</a></li>
          <li><a href="/tv">TV</a></li>
        </ul>
      </div>
      <div class="footer-column">
        <h4>Support</h4>
        <ul>
          <li><a href="/help">Help Center</a></li>
          <li><a href="/contact">Contact</a></li>
          <li><a href="/faq">FAQ</a></li>
        </ul>
      </div>
    </div>

    <div slot="copyright">
      © 2024 Deutsche Telekom AG
    </div>

    <nav slot="navigation">
      <a href="/legal">Legal Notice</a>
      <a href="/privacy">Privacy Policy</a>
      <a href="/terms">Terms of Service</a>
    </nav>
  </scale-telekom-footer>

  <!-- Minimal footer -->
  <scale-telekom-footer type="minimal">
    <nav slot="navigation">
      <a href="/legal">Legal Notice</a>
      <a href="/privacy">Privacy</a>
    </nav>
  </scale-telekom-footer>
</template>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'standard' \| 'minimal'` | `'standard'` | Footer variant |

**Slots:**
| Slot | Description |
|------|-------------|
| `extended-navigation` | Sitemap/navigation columns |
| `copyright` | Copyright text |
| `navigation` | Legal links |
| default | Custom footer content |

---

## Component Quick Reference

### Form Components

| Component | Key Props | Key Events |
|-----------|-----------|------------|
| `scale-text-field` | `label`, `value`, `type`, `invalid`, `helper-text` | `scale-change`, `scale-input`, `scale-focus`, `scale-blur` |
| `scale-textarea` | `label`, `value`, `rows`, `max-length`, `counter`, `resize` | `scale-change`, `scale-input`, `scale-focus`, `scale-blur` |
| `scale-checkbox` | `label`, `checked`, `indeterminate` | `scale-change` (detail: `{ checked }`) |
| `scale-checkbox-group` | `label`, `helper-text`, `invalid` | `scale-change` |
| `scale-dropdown-select` | `label`, `value`, `disabled` | `scale-change` (detail: `{ value }`) |
| `scale-dropdown` | `label`, `value`, `multiple` | `scale-change`, `scale-input` |
| `scale-radio-button-group` | `label`, `value` | `scale-change` (detail: `{ value }`) |
| `scale-switch` | `label`, `checked` | `scale-change` (detail: `{ checked }`) |
| `scale-date-picker` | `label`, `value`, `min`, `max`, `first-day-of-week` | `scale-change`, `scale-focus`, `scale-blur` |
| `scale-slider` | `value`, `min`, `max`, `step`, `range` | `scale-change`, `scale-input` |
| `scale-rating-stars` | `rating`, `max`, `size`, `readonly` | `scale-change` |

### Button Components

| Component | Variants | Key Props |
|-----------|----------|-----------|
| `scale-button` | `primary`, `secondary`, `ghost` | `size`, `disabled`, `type`, `icon-only` |
| `scale-segmented-button` | - | Contains `scale-segment` children |

### Navigation Components

| Component | Usage | Key Props |
|-----------|-------|-----------|
| `scale-tab-nav` | Tab navigation | Contains `scale-tab-header` + `scale-tab-panel` |
| `scale-sidebar-nav` | Sidebar navigation | Contains nav items and collapsibles |
| `scale-breadcrumb` | Breadcrumb trail | Contains links |
| `scale-pagination` | Page navigation | `total-elements`, `page-size`, `start-element` |
| `scale-menu-flyout` | Context menu | `direction`, `close-on-select` |

### Layout Components

| Component | Usage | Key Props |
|-----------|-------|-----------|
| `scale-card` | Card container | `to` (clickable link), `label` |
| `scale-modal` | Dialog | `opened`, `heading`, `size`, `align-actions` |
| `scale-accordion` | Collapsible sections | `dependent` (one open at a time) |
| `scale-list` | Ordered/unordered list | `ordered` |

### Data Display Components

| Component | Usage | Key Props |
|-----------|-------|-----------|
| `scale-data-grid` | Data table | `fields`, `rows`, `selectable`, `page-size` |
| `scale-table` | HTML table wrapper | - |
| `scale-chip` | Filter/tag | `label`, `type`, `selected`, `variant` |
| `scale-notification-badge` | Count indicator | `label`, `type`, `max-characters` |
| `scale-tag` | Label tag | `variant`, `dismissible` |

### Feedback Components

| Component | Usage | Key Props |
|-----------|-------|-----------|
| `scale-notification` | All notification types | `type`, `variant`, `heading`, `dismissible`, `delay` |
| `scale-notification-toast` | Toast messages | `variant`, `alignment`, `auto-hide` |
| `scale-notification-banner` | Banner alerts | `variant`, `opened` |
| `scale-callout` | Visual highlight | `variant`, `rotation`, positioning props |
| `scale-progress-bar` | Progress indicator | `percentage`, `show-status` |
| `scale-loading-spinner` | Loading state | `size`, `text` |

### Telekom Brand Components

| Component | Usage | Key Props |
|-----------|-------|-----------|
| `scale-logo` | Brand logo | `variant`, `size`, `href`, `logo-title` |
| `scale-telekom-header` | Page header | `app-name`, `logo-href`, navigation slots |
| `scale-telekom-nav-list` | Navigation container | `aria-label`, `alignment` |
| `scale-telekom-nav-item` | Navigation item | `aria-label`, `active`, `has-children` |
| `scale-telekom-footer` | Page footer | `type` (`standard` or `minimal`) |
