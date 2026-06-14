# Installation and Project Setup

This document covers installing Scale components and configuring Vue 3 for custom elements.

---

## NPM Installation

### Telekom Branded Version

```bash
npm install @telekom/scale-components@next
```

### Open Source/Neutral Version

```bash
npm install @telekom/scale-components-neutral@next
```

> Use `@next` for the latest version with dark mode support. Omit for stable release.

---

## package.json Version (CRITICAL)

**ALWAYS use an empty string `""` for the version to get the latest release. NEVER use a specific version like `"^3.0.0-beta.171"`.**

### Telekom Branded
```json
{
  "dependencies": {
    "@telekom/scale-components": ""
  }
}
```

### Open Source/Neutral
```json
{
  "dependencies": {
    "@telekom/scale-components-neutral": ""
  }
}
```

This ensures you always get the latest version without pinning to outdated beta releases.

---

## Setup in main.ts/main.js

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

---

## Tree-Shaking (Optional)

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

### Runtime Compilation

```typescript
// main.ts (for on-the-fly template compilation)
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith('scale-')
app.mount('#app')
```

---

## CDN-loaded Scale Components (Vue SFC Playground)

For Vue SFC Playground or prototyping without a build step:

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

---

## ESLint Configuration

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

## TypeScript Declarations

Add type declarations for Scale elements:

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

### Typing Custom Element Events

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

## Validation Checklist

After setup, verify everything works:

1. Run your dev server: `npm run dev`
2. Add a test component to App.vue:
   ```vue
   <scale-button>Test Button</scale-button>
   ```

**Expected Results**:
- [ ] No console warnings about unknown custom elements
- [ ] Button renders with Telekom magenta styling
- [ ] Button is clickable and shows hover state

**If Issues Occur**:
- Components not rendering → Check vite.config.ts `isCustomElement`
- No styling → Check CSS import in main.ts
- TypeScript errors → Add type declarations
