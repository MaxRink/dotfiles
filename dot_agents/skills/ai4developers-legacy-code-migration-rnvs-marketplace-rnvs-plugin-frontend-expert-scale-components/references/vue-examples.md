# Vue 3 + Scale Component Examples

Real-world Vue 3 + TypeScript + Telekom Scale component patterns for enterprise applications.

---

## 1. Simple Login Form

A complete login form using v-model wrapper components, demonstrating form validation, loading states, and design token styling.

### LoginForm.vue

```vue
<!-- components/LoginForm.vue -->
<template>
  <scale-card class="login-form">
    <h2>Login</h2>

    <form @submit.prevent="handleSubmit">
      <ScaleInput
        v-model="form.email"
        label="Email"
        type="email"
        :error="errors.email"
        required
      />

      <ScaleInput
        v-model="form.password"
        label="Password"
        type="password"
        :error="errors.password"
        required
      />

      <ScaleCheckbox
        v-model="form.remember"
        label="Remember me"
      />

      <div class="button-group">
        <scale-button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Logging in...' : 'Login' }}
        </scale-button>
      </div>
    </form>
  </scale-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import ScaleInput from './scale-wrappers/ScaleInput.vue'
import ScaleCheckbox from './scale-wrappers/ScaleCheckbox.vue'

const emit = defineEmits<{
  submit: [data: { email: string; password: string; remember: boolean }]
}>()

const form = reactive({
  email: '',
  password: '',
  remember: false,
})

const errors = reactive({
  email: '',
  password: '',
})

const isSubmitting = ref(false)

const validate = (): boolean => {
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = 'Email is required'
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Please enter a valid email'
  }

  if (!form.password) {
    errors.password = 'Password is required'
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
  }

  return !errors.email && !errors.password
}

const handleSubmit = async () => {
  if (!validate()) return

  isSubmitting.value = true
  try {
    emit('submit', { ...form })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  padding: var(--scl-spacing-24);
}

.login-form h2 {
  margin-bottom: var(--scl-spacing-16);
}

.button-group {
  margin-top: var(--scl-spacing-16);
}
</style>
```

### Usage

```vue
<template>
  <LoginForm @submit="handleLogin" />
</template>

<script setup lang="ts">
import LoginForm from '@/components/LoginForm.vue'

const handleLogin = async (data: { email: string; password: string; remember: boolean }) => {
  try {
    await authService.login(data.email, data.password, data.remember)
    router.push('/dashboard')
  } catch (error) {
    // Handle login error
  }
}
</script>
```

### Key Features Demonstrated

| Feature | Implementation |
|---------|----------------|
| v-model wrappers | `ScaleInput`, `ScaleCheckbox` components |
| Form validation | `validate()` function with error state |
| Error display | `:error` prop on wrapper components |
| Loading state | `isSubmitting` ref with button disabled |
| Design tokens | `var(--scl-spacing-*)` in scoped styles |
| Event emission | Typed `emit('submit', data)` |

---

## 2. Modal Dialogs

### Simple Dialog

```vue
<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  opened: boolean
  initialValue?: string
}

interface Emits {
  (e: 'save', value: string): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  initialValue: ''
})

const emit = defineEmits<Emits>()
const value = ref(props.initialValue)

const handleSave = () => emit('save', value.value)
const handleCancel = () => emit('cancel')
</script>

<template>
  <scale-modal :opened="opened" heading="Edit Value" @scale-close="handleCancel">
    <scale-text-field
      v-model="value"
      label="Value"
      placeholder="Enter value..."
    />

    <div slot="action">
      <scale-button variant="secondary" @click="handleCancel">Cancel</scale-button>
      <scale-button variant="primary" @click="handleSave">Save</scale-button>
    </div>
  </scale-modal>
</template>
```

### Form Dialog with Validation

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { z } from 'zod'

interface Props {
  opened: boolean
}

interface Emits {
  (e: 'submit', data: FormData): void
  (e: 'cancel'): void
}

const emailSchema = z.object({
  to: z.string().email('Invalid email address'),
  subject: z.string().min(1, 'Subject is required'),
  body: z.string().min(1, 'Message is required')
})

type FormData = z.infer<typeof emailSchema>

defineProps<Props>()
const emit = defineEmits<Emits>()

const formData = ref<FormData>({
  to: '',
  subject: '',
  body: ''
})

const { validate, getFieldError, hasErrors } = useFormValidation(emailSchema)
const submitting = ref(false)

const handleSubmit = async () => {
  if (!validate(formData.value)) return

  submitting.value = true
  try {
    emit('submit', formData.value)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <scale-modal :opened="opened" heading="Send Email" size="large" @scale-close="emit('cancel')">
    <scale-text-field
      v-model="formData.to"
      label="To"
      required
      :invalid="!!getFieldError('to')"
      :helper-text="getFieldError('to')"
    />

    <scale-text-field
      v-model="formData.subject"
      label="Subject"
      required
      :invalid="!!getFieldError('subject')"
      :helper-text="getFieldError('subject')"
    />

    <scale-text-area
      v-model="formData.body"
      label="Message"
      required
      rows="8"
      :invalid="!!getFieldError('body')"
      :helper-text="getFieldError('body')"
    />

    <div slot="action">
      <scale-button variant="secondary" @click="emit('cancel')">Cancel</scale-button>
      <scale-button variant="primary" :disabled="hasErrors || submitting" @click="handleSubmit">
        Send
      </scale-button>
    </div>
  </scale-modal>
</template>
```

---

## 3. Search/Filter Forms

### Filter Form with Grid Layout

```vue
<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFilterStore } from '@/stores/filter'

const router = useRouter()
const filterStore = useFilterStore()

const filters = reactive({
  search: '',
  status: '',
  category: '',
  dateFrom: '',
  dateTo: ''
})

onMounted(() => {
  Object.assign(filters, filterStore.filters)
})

const handleSearch = () => {
  filterStore.setFilters(filters)
  router.push({ name: 'results', query: filters })
}

const handleReset = () => {
  filterStore.resetFilters()
  Object.assign(filters, filterStore.filters)
}
</script>

<template>
  <div class="filter-form">
    <h2>Search</h2>

    <form @submit.prevent="handleSearch">
      <div class="filter-grid">
        <scale-text-field v-model="filters.search" label="Search" />

        <scale-dropdown-select v-model="filters.status" label="Status">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="pending">Pending</option>
          <option value="closed">Closed</option>
        </scale-dropdown-select>

        <scale-dropdown-select v-model="filters.category" label="Category">
          <option value="">All Categories</option>
          <option value="type-a">Type A</option>
          <option value="type-b">Type B</option>
        </scale-dropdown-select>

        <scale-text-field v-model="filters.dateFrom" type="date" label="From Date" />
        <scale-text-field v-model="filters.dateTo" type="date" label="To Date" />
      </div>

      <div class="button-bar">
        <scale-button type="submit" variant="primary">Search</scale-button>
        <scale-button type="button" variant="secondary" @click="handleReset">Reset</scale-button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.filter-form {
  padding: 2rem;
  max-width: 1200px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.button-bar {
  display: flex;
  gap: 1rem;
}
</style>
```

---

## 4. Data Tables

### Table with Selection and Toolbar

```vue
<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'

interface Item {
  id: string
  name: string
  status: string
  category: string
  createdAt: string
}

const dataStore = useDataStore()

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'category', label: 'Category' },
  { key: 'createdAt', label: 'Created' }
]

onMounted(() => dataStore.fetchItems())

const handleRowClick = (item: Item) => {
  dataStore.toggleSelection(item.id)
}

const handleRowDoubleClick = (item: Item) => {
  // Navigate to detail view
  console.log('Open detail:', item.id)
}
</script>

<template>
  <div class="data-list">
    <div class="toolbar">
      <scale-button variant="secondary" @click="dataStore.fetchItems">Refresh</scale-button>
      <scale-button variant="primary" :disabled="!dataStore.hasSelection">
        View Selected
      </scale-button>
      <scale-button @click="dataStore.selectAll">Select All</scale-button>
      <scale-button :disabled="dataStore.selectedIds.length < 2">
        Batch Action
      </scale-button>
    </div>

    <div v-if="dataStore.isLoading" class="loading">Loading...</div>
    <div v-else-if="dataStore.error" class="error">{{ dataStore.error }}</div>

    <div v-else class="table-container">
      <scale-table>
        <scale-table-head>
          <scale-table-row>
            <scale-table-cell v-for="col in columns" :key="col.key">
              {{ col.label }}
            </scale-table-cell>
          </scale-table-row>
        </scale-table-head>
        <scale-table-body>
          <scale-table-row
            v-for="item in dataStore.items"
            :key="item.id"
            :class="{ selected: dataStore.selectedIds.includes(item.id) }"
            @click="handleRowClick(item)"
            @dblclick="handleRowDoubleClick(item)"
          >
            <scale-table-cell>{{ item.id }}</scale-table-cell>
            <scale-table-cell>{{ item.name }}</scale-table-cell>
            <scale-table-cell>
              <scale-tag :variant="item.status === 'active' ? 'success' : 'warning'">
                {{ item.status }}
              </scale-tag>
            </scale-table-cell>
            <scale-table-cell>{{ item.category }}</scale-table-cell>
            <scale-table-cell>{{ item.createdAt }}</scale-table-cell>
          </scale-table-row>
        </scale-table-body>
      </scale-table>
    </div>
  </div>
</template>

<style scoped>
.data-list {
  padding: 1rem;
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.table-container {
  overflow-x: auto;
}

:deep(scale-table-row.selected) {
  background-color: var(--scale-color-primary-10);
}

:deep(scale-table-row:hover) {
  background-color: var(--scale-color-background-hover);
  cursor: pointer;
}
</style>
```

---

## 5. Detail/Edit Views

### Detail Form with Actions

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDetailStore } from '@/stores/detail'
import { useNavigation } from '@/composables/useNavigation'

const route = useRoute()
const detailStore = useDetailStore()
const { goBack } = useNavigation()

onMounted(() => {
  detailStore.loadItem(route.params.id as string)
})

const handleSave = async () => {
  const success = await detailStore.saveItem()
  if (success) goBack()
}
</script>

<template>
  <div v-if="detailStore.isLoading" class="loading">Loading...</div>
  <div v-else-if="detailStore.error" class="error">{{ detailStore.error }}</div>
  <div v-else-if="detailStore.currentItem" class="detail-form">
    <header class="form-header">
      <h2>Edit Item - {{ detailStore.currentItem.id }}</h2>
      <div class="nav-buttons">
        <scale-button variant="ghost" size="small">Previous</scale-button>
        <scale-button variant="ghost" size="small">Next</scale-button>
      </div>
    </header>

    <div class="form-content">
      <scale-text-field
        :model-value="detailStore.currentItem.name"
        label="Name"
        @scale-change="detailStore.updateField('name', $event.target.value)"
      />

      <scale-dropdown-select
        :value="detailStore.currentItem.status"
        label="Status"
        @scale-change="detailStore.updateField('status', $event.target.value)"
      >
        <option value="active">Active</option>
        <option value="pending">Pending</option>
        <option value="closed">Closed</option>
      </scale-dropdown-select>

      <scale-text-area
        :model-value="detailStore.currentItem.notes"
        label="Notes"
        rows="5"
        @scale-change="detailStore.updateField('notes', $event.target.value)"
      />
    </div>

    <div class="action-bar">
      <scale-button variant="primary" :disabled="detailStore.isLoading" @click="handleSave">
        Save
      </scale-button>
      <scale-button variant="secondary" @click="goBack">Cancel</scale-button>
    </div>
  </div>
</template>

<style scoped>
.detail-form {
  padding: 1rem;
  max-width: 800px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-bar {
  display: flex;
  gap: 0.5rem;
}
</style>
```

---

## 6. Pinia Store Pattern

### List Store with Selection

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

interface Item {
  id: string
  name: string
  status: string
}

interface Pagination {
  total: number
  limit: number
  offset: number
}

export const useDataStore = defineStore('data', () => {
  // State
  const items = ref<Item[]>([])
  const selectedIds = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref<Pagination>({ total: 0, limit: 100, offset: 0 })

  // Getters
  const selectedItems = computed(() =>
    items.value.filter(item => selectedIds.value.includes(item.id))
  )

  const hasSelection = computed(() => selectedIds.value.length > 0)

  // Actions
  async function fetchItems(filters: Record<string, unknown> = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/items', { params: filters })
      items.value = response.data.data
      pagination.value = response.data.pagination
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch'
      items.value = []
    } finally {
      isLoading.value = false
    }
  }

  function toggleSelection(id: string) {
    const index = selectedIds.value.indexOf(id)
    if (index > -1) {
      selectedIds.value.splice(index, 1)
    } else {
      selectedIds.value.push(id)
    }
  }

  function selectAll() {
    selectedIds.value = items.value.map(item => item.id)
  }

  function clearSelection() {
    selectedIds.value = []
  }

  return {
    items,
    selectedIds,
    isLoading,
    error,
    pagination,
    selectedItems,
    hasSelection,
    fetchItems,
    toggleSelection,
    selectAll,
    clearSelection
  }
})
```

---

## 7. Composables

### Form Validation Composable

```typescript
import { ref, computed } from 'vue'
import type { z } from 'zod'

export function useFormValidation<T extends z.ZodType>(schema: T) {
  const errors = ref<Record<string, string>>({})

  const validate = (data: z.infer<T>): boolean => {
    errors.value = {}
    const result = schema.safeParse(data)

    if (!result.success) {
      result.error.errors.forEach(error => {
        const path = error.path.join('.')
        errors.value[path] = error.message
      })
      return false
    }
    return true
  }

  const getFieldError = (fieldName: string): string => {
    return errors.value[fieldName] || ''
  }

  const hasErrors = computed(() => Object.keys(errors.value).length > 0)

  const clearErrors = () => {
    errors.value = {}
  }

  return { errors, hasErrors, validate, getFieldError, clearErrors }
}
```

### Navigation Composable

```typescript
import { useRouter } from 'vue-router'

export function useNavigation() {
  const router = useRouter()

  const goBack = () => router.back()

  const navigateTo = (name: string, params?: Record<string, string>) => {
    router.push({ name, params })
  }

  return { goBack, navigateTo }
}
```

---

## 8. Vue Router Configuration

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/items',
    children: [
      {
        path: '',
        name: 'items-list',
        component: () => import('@/views/ItemsList.vue')
      },
      {
        path: ':id',
        name: 'item-detail',
        component: () => import('@/views/ItemDetail.vue'),
        props: true
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

export default router
```

---

## 9. API Layer Pattern

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for errors
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  get: <T>(url: string, config?: any) => apiClient.get<T>(url, config),
  post: <T>(url: string, data?: any) => apiClient.post<T>(url, data),
  put: <T>(url: string, data?: any) => apiClient.put<T>(url, data),
  delete: <T>(url: string) => apiClient.delete<T>(url)
}
```

---

## Key Patterns Summary

| Pattern | Description |
|---------|-------------|
| Modal Dialog | `<scale-modal>` with `slot="action"` for buttons |
| Form Validation | Zod schema + `useFormValidation` composable |
| Data Tables | `<scale-table>` with selection state in Pinia |
| State Management | Pinia stores with composition API |
| API Layer | Axios with interceptors for auth/errors |
| Navigation | Vue Router with lazy-loaded components |
| Micro-frontend | single-spa lifecycle exports |
