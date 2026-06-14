# Code Migration

This document provides complete code examples for migrating a Vue 3 SPA to microfrontend architecture.

---

## Overview

The code migration involves creating a dual-entry architecture where:
- **Production**: App is mounted by the container via single-spa
- **Development**: App runs standalone with mocked container services

---

## File Structure After Migration

```
src/
├── main.ts                    # single-spa entry (production)
├── standalone/
│   └── main.ts                # Standalone entry (development)
├── app.vue                    # Root component
├── pages/
│   ├── router.ts              # Vue Router configuration
│   ├── index-page.vue         # Demo/home page
│   └── [feature]/             # Feature pages
│       └── [page].vue
├── components/
│   └── [shared components]
├── composables/
│   ├── context.ts             # Container context provider
│   └── [other composables]
├── stores/
│   └── [pinia stores]
├── types/
│   └── idp.ts                 # Identity provider interface
└── assets/
    └── [static assets]

public/
└── config.json                # Runtime configuration

index.html                     # Standalone dev entry HTML
```

---

## Step 1: Create Type Definitions

### src/types/idp.ts

```typescript
/**
 * Identity Provider interface provided by the VNRM container.
 * Provides access to user authentication and authorization.
 */
export interface Idp {
  /** User's display name */
  name: string;

  /** User's email address */
  email: string;

  /** User's unique identifier */
  sub: string;

  /** User's roles/groups */
  roles: string[];

  /** Check if user has a specific role */
  hasRole(role: string): boolean;

  /** Get the current access token */
  getAccessToken(): Promise<string>;

  /** Get the current ID token */
  getIdToken(): Promise<string>;

  /** Force token refresh */
  refreshToken(): Promise<void>;

  /** Sign out the user */
  signOut(): Promise<void>;
}
```

---

## Step 2: Create Context Provider

### src/composables/context.ts

```typescript
import { inject, type App, type InjectionKey } from "vue";
import type { EventEmitter } from "eventemitter3";
import type { Idp } from "@/types/idp";
import type Config from "../../public/config.json";

/**
 * Context provided by the VNRM container to microfrontends.
 */
export type Context = {
  /** Event bus for inter-microfrontend communication */
  eventBus: EventEmitter;

  /** Identity provider for authentication */
  idp: Idp;

  /** Runtime configuration loaded at startup */
  config: typeof Config;
};

/** Injection key for type-safe context access */
const CONTEXT: InjectionKey<Context> = Symbol("CONTEXT");

/**
 * Creates a Vue plugin that provides container context.
 * Used in main.ts to inject context into the app.
 *
 * @example
 * ```typescript
 * app.use(createContext({ eventBus, idp, config }));
 * ```
 */
export function createContext(context: Context) {
  return {
    install: (app: App) => {
      app.provide(CONTEXT, context);
    },
  };
}

/**
 * Composable to access container context from any component.
 * Throws if called outside of a properly configured app.
 *
 * @example
 * ```typescript
 * const { idp, eventBus, config } = useContext();
 * console.log(`Hello, ${idp.name}!`);
 * ```
 */
export function useContext(): Context {
  const context = inject(CONTEXT);
  if (!context) {
    throw new Error(
      "Context not available. Ensure the app is initialized with " +
      "app.use(createContext({ eventBus, idp, config }))."
    );
  }
  return context;
}
```

---

## Step 3: Create Runtime Configuration

### public/config.json

```json
{
  "apiBaseUrl": "https://api.vnrm.telekom.de",
  "featureFlags": {
    "darkMode": true,
    "experimentalFeatures": false
  },
  "logging": {
    "level": "info",
    "endpoint": "/api/logs"
  }
}
```

**Note**: This file is loaded at runtime, allowing configuration changes without rebuilding. In production, Helm ConfigMaps can override these values.

---

## Step 4: Create Main Entry Point (Production)

### src/main.ts

```typescript
import singleSpaVue from "single-spa-vue";
import { createApp, h } from "vue";
import { createPinia } from "pinia";
import type { EventEmitter } from "eventemitter3";

import App from "./app.vue";
import { router } from "./pages/router";
import { createContext } from "./composables/context";
import type { Idp } from "./types/idp";

/**
 * Props received from the VNRM container when mounting.
 */
type ContainerProps = {
  /** CSS selector for the mount point */
  el: string;

  /** Event bus for container communication */
  eventBus: EventEmitter;

  /** Identity provider instance */
  idp: Idp;
};

/**
 * single-spa lifecycle hooks exported for container orchestration.
 */
export const { bootstrap, mount, unmount } = singleSpaVue({
  createApp,

  /**
   * App options factory - receives container props.
   */
  appOptions: async (props: ContainerProps) => ({
    el: props.el,
    render: () => h(App),
  }),

  /**
   * Called after app instance is created, before mounting.
   * Install plugins and configure the app here.
   */
  async handleInstance(app, props: ContainerProps) {
    // Load runtime configuration
    const config = await fetch(
      new URL("../config.json", import.meta.url)
    ).then((response) => response.json());

    // Install plugins
    app
      .use(createPinia())
      .use(router)
      .use(
        createContext({
          eventBus: props.eventBus,
          idp: props.idp,
          config,
        })
      );
  },

  /**
   * Replace mode ensures clean DOM when unmounting.
   */
  replaceMode: true,
});
```

---

## Step 5: Create Standalone Entry Point (Development)

### src/standalone/main.ts

```typescript
import { createApp } from "vue";
import { createPinia } from "pinia";
import { EventEmitter } from "eventemitter3";

import App from "../app.vue";
import { router } from "../pages/router";
import { createContext } from "../composables/context";
import type { Idp } from "../types/idp";
import config from "../../public/config.json";

/**
 * Mock IDP for standalone development.
 * Simulates container-provided identity.
 */
const mockIdp: Idp = {
  name: "Developer User",
  email: "developer@telekom.de",
  sub: "dev-user-123",
  roles: ["admin", "developer"],

  hasRole(role: string): boolean {
    return this.roles.includes(role);
  },

  async getAccessToken(): Promise<string> {
    return "mock-access-token-for-development";
  },

  async getIdToken(): Promise<string> {
    return "mock-id-token-for-development";
  },

  async refreshToken(): Promise<void> {
    console.log("[Mock IDP] Token refreshed");
  },

  async signOut(): Promise<void> {
    console.log("[Mock IDP] User signed out");
  },
};

/**
 * Event bus for standalone development.
 * Logs all events for debugging.
 */
const eventBus = new EventEmitter();

// Log all events for debugging
const originalEmit = eventBus.emit.bind(eventBus);
eventBus.emit = (event: string, ...args: unknown[]) => {
  console.log(`[EventBus] ${event}:`, ...args);
  return originalEmit(event, ...args);
};

/**
 * Create and mount the standalone app.
 */
const app = createApp(App);

app
  .use(createPinia())
  .use(router)
  .use(
    createContext({
      eventBus,
      idp: mockIdp,
      config,
    })
  );

app.mount("#app");

console.log("[Standalone] App mounted in development mode");
```

---

## Step 6: Update index.html for Development

### index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>VNRM Microfrontend - Development</title>

    <!-- Scale Design System (for standalone development) -->
    <link
      rel="stylesheet"
      href="node_modules/@telekom/scale-components/dist/scale-components/scale-components.css"
    />
    <script
      type="module"
      src="node_modules/@telekom/scale-components/dist/scale-components/scale-components.esm.js"
    ></script>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/standalone/main.ts"></script>
  </body>
</html>
```

**Note**: Scale components are loaded via `node_modules` for development. In production, the container provides Scale globally.

---

## Step 7: Simplify Root Component

### src/app.vue

```vue
<script setup lang="ts">
// Root component is intentionally minimal.
// All content is rendered via router-view.
</script>

<template>
  <router-view />
</template>

<style>
/* Global styles (if any) should use design tokens */
:root {
  font-family: var(--telekom-typography-font-family-sans);
}
</style>
```

---

## Step 8: Configure Router

### src/pages/router.ts

```typescript
import { createRouter, createWebHistory } from "vue-router";
import IndexPage from "./index-page.vue";

/**
 * Router configuration for microfrontend.
 *
 * Uses a catch-all pattern to handle all sub-routes.
 * The container manages top-level routing.
 */
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      name: "INDEX",
      path: "/:furtherPath(.*)*",
      component: IndexPage,
    },
    // Add more routes as needed
    // {
    //   name: "FEATURE",
    //   path: "/feature/:id",
    //   component: () => import("./feature/feature-page.vue"),
    // },
  ],
});

/**
 * Optional: Global navigation guard
 */
// router.beforeEach((to, from, next) => {
//   // Add navigation logic here
//   next();
// });
```

---

## Step 9: Create Demo Page

### src/pages/index-page.vue

```vue
<script setup lang="ts">
import { useContext } from "@/composables/context";
import { useCounterStore } from "@/stores/counter";

// Access container-provided context
const { idp, eventBus, config } = useContext();

// Access Pinia store
const counterStore = useCounterStore();

/**
 * Emit a toast notification to the container.
 */
function showToast() {
  eventBus.emit("toast", {
    title: "Hello from Microfrontend",
    detail: `Clicked by ${idp.name}`,
    type: "success",
    timeout: 5000,
  });
}

/**
 * Emit a custom event to other microfrontends.
 */
function broadcastEvent() {
  eventBus.emit("custom-event", {
    source: "my-microfrontend",
    timestamp: Date.now(),
    data: { counter: counterStore.count },
  });
}
</script>

<template>
  <scale-card>
    <h2 class="headline">Hello, {{ idp.name }}!</h2>

    <p>Welcome to the VNRM microfrontend.</p>

    <div class="actions">
      <scale-button @click="counterStore.increment">
        Count: {{ counterStore.count }}
      </scale-button>

      <scale-button variant="secondary" @click="showToast">
        Show Toast
      </scale-button>

      <scale-button variant="secondary" @click="broadcastEvent">
        Broadcast Event
      </scale-button>
    </div>

    <scale-tag v-for="role in idp.roles" :key="role">
      {{ role }}
    </scale-tag>

    <details>
      <summary>Configuration</summary>
      <pre>{{ JSON.stringify(config, null, 2) }}</pre>
    </details>
  </scale-card>
</template>

<style scoped>
.headline {
  font: var(--telekom-text-style-heading-4);
  margin-bottom: var(--telekom-spacing-composition-space-06);
}

.actions {
  display: flex;
  gap: var(--telekom-spacing-composition-space-04);
  margin: var(--telekom-spacing-composition-space-06) 0;
}

details {
  margin-top: var(--telekom-spacing-composition-space-06);
}

pre {
  background: var(--telekom-color-background-surface-subtle);
  padding: var(--telekom-spacing-composition-space-04);
  border-radius: var(--telekom-radius-small);
  overflow: auto;
  font-size: var(--telekom-typography-font-size-small);
}
</style>
```

---

## Step 10: Keep Pinia Stores

Pinia stores typically don't need changes. Ensure they use the Composition API style:

### src/stores/counter.ts

```typescript
import { defineStore } from "pinia";
import { ref } from "vue";

/**
 * Example Pinia store using Composition API.
 */
export const useCounterStore = defineStore("counter", () => {
  const count = ref(0);

  function increment() {
    count.value++;
  }

  function decrement() {
    count.value--;
  }

  function reset() {
    count.value = 0;
  }

  return {
    count,
    increment,
    decrement,
    reset,
  };
});
```

---

## Migration Checklist

### Entry Points

- [ ] Created `src/main.ts` with single-spa lifecycle exports
- [ ] Created `src/standalone/main.ts` with mock IDP and EventBus
- [ ] Updated `index.html` to use standalone entry
- [ ] Both entry points install the same plugins (Pinia, Router, Context)

### Context System

- [ ] Created `src/types/idp.ts` with IDP interface
- [ ] Created `src/composables/context.ts` with provider and hook
- [ ] All components use `useContext()` instead of direct globals

### Root Component

- [ ] `src/app.vue` contains only `<router-view />`
- [ ] No business logic in root component
- [ ] Global styles use design tokens

### Routing

- [ ] Router uses catch-all pattern `/:path(.*)*`
- [ ] Router uses `createWebHistory()`
- [ ] Navigation guards updated to use context

### Components

- [ ] Components use `useContext()` for IDP, EventBus, Config
- [ ] Components use Scale components (not plain HTML)
- [ ] Scoped styles use design tokens
- [ ] No direct window/document access (use context)

### Stores

- [ ] Stores use Composition API style
- [ ] No direct axios/fetch (use context config for base URL)
- [ ] Store actions handle errors appropriately

---

## Common Migration Patterns

### Before: Direct API Call

```typescript
// OLD: Direct axios call
import axios from "axios";

const response = await axios.get("https://api.example.com/data");
```

### After: Context-Based API Call

```typescript
// NEW: Use context config for base URL
const { config, idp } = useContext();

const token = await idp.getAccessToken();
const response = await fetch(`${config.apiBaseUrl}/data`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

---

### Before: Direct Authentication Check

```typescript
// OLD: Check localStorage
const token = localStorage.getItem("token");
if (!token) {
  router.push("/login");
}
```

### After: IDP-Based Authentication

```typescript
// NEW: Use IDP from context
const { idp } = useContext();

// IDP is always authenticated (container handles login)
const user = idp.name;
const hasAccess = idp.hasRole("admin");
```

---

### Before: Custom Toast/Notification

```typescript
// OLD: Custom toast library
import { toast } from "my-toast-library";
toast.success("Operation completed!");
```

### After: Container EventBus Toast

```typescript
// NEW: Emit to container
const { eventBus } = useContext();
eventBus.emit("toast", {
  title: "Success",
  detail: "Operation completed!",
  type: "success",
  timeout: 5000,
});
```

---

## Next Steps

After completing code migration:

1. **Phase 3**: Build Configuration - See `03-build-configuration.md`
2. **Phase 4**: Container Integration - See `04-container-integration.md`
