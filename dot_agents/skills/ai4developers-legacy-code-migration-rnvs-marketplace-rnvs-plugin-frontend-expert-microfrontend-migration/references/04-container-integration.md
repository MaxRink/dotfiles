# Container Integration

This document provides complete patterns for integrating a Vue 3 microfrontend with the VNRM container using single-spa.

---

## Overview

The VNRM container uses **single-spa** to orchestrate multiple microfrontends. Each microfrontend must:

1. Export lifecycle hooks (`bootstrap`, `mount`, `unmount`)
2. Accept container-provided props (`el`, `eventBus`, `idp`)
3. Load configuration at runtime
4. Communicate via the shared EventBus

---

## single-spa Lifecycle

### Lifecycle Hooks

| Hook | When Called | Purpose |
|------|-------------|---------|
| `bootstrap` | Once, when first loaded | Initialize resources |
| `mount` | Each time app becomes active | Create and mount Vue app |
| `unmount` | Each time app becomes inactive | Destroy Vue app, cleanup |

### Complete Implementation

```typescript
// src/main.ts
import singleSpaVue from "single-spa-vue";
import { createApp, h } from "vue";
import { createPinia } from "pinia";
import type { EventEmitter } from "eventemitter3";

import App from "./app.vue";
import { router } from "./pages/router";
import { createContext } from "./composables/context";
import type { Idp } from "./types/idp";

/**
 * Props provided by the VNRM container.
 */
interface ContainerProps {
  /** DOM element selector for mounting */
  el: string;

  /** Shared event bus for inter-app communication */
  eventBus: EventEmitter;

  /** Identity provider with user info and tokens */
  idp: Idp;

  /** Optional: App-specific configuration from container */
  appConfig?: Record<string, unknown>;
}

/**
 * Exported lifecycle hooks for single-spa.
 */
export const { bootstrap, mount, unmount } = singleSpaVue({
  createApp,

  /**
   * App options - defines how the Vue app is created.
   * Receives container props as argument.
   */
  appOptions: async (props: ContainerProps) => ({
    // Mount point provided by container
    el: props.el,

    // Root component render function
    render: () => h(App),
  }),

  /**
   * Handle instance - called after app is created, before mount.
   * Install plugins and configure the app here.
   */
  async handleInstance(app, props: ContainerProps) {
    // Load runtime configuration
    const config = await loadConfig();

    // Merge with app-specific config from container
    const mergedConfig = {
      ...config,
      ...props.appConfig,
    };

    // Install plugins
    app.use(createPinia());
    app.use(router);
    app.use(
      createContext({
        eventBus: props.eventBus,
        idp: props.idp,
        config: mergedConfig,
      })
    );

    // Optional: Register global error handler
    app.config.errorHandler = (err, instance, info) => {
      console.error("[Microfrontend Error]", err, info);
      props.eventBus.emit("error", {
        source: "my-microfrontend",
        error: err,
        info,
      });
    };
  },

  /**
   * Replace mode - ensures clean DOM on unmount.
   */
  replaceMode: true,
});

/**
 * Load runtime configuration.
 */
async function loadConfig() {
  const response = await fetch(new URL("../config.json", import.meta.url));
  if (!response.ok) {
    console.warn("[Config] Failed to load config.json, using defaults");
    return {};
  }
  return response.json();
}
```

---

## Container Props Reference

### el (Mount Point)

The container provides a CSS selector where the microfrontend should mount:

```typescript
// Container creates a mount point like:
// <div id="single-spa-application:@vnrm/my-microfrontend"></div>

props.el = "#single-spa-application\\:@vnrm/my-microfrontend";
```

**Note**: The selector may contain special characters that need escaping.

### eventBus (Communication)

EventEmitter3 instance shared across all microfrontends:

```typescript
import type { EventEmitter } from "eventemitter3";

interface EventBusEvents {
  // Toast notifications
  toast: {
    title: string;
    detail?: string;
    type: "success" | "error" | "warning" | "info";
    timeout?: number;
  };

  // Error reporting
  error: {
    source: string;
    error: Error;
    info?: string;
  };

  // Navigation requests
  navigate: {
    path: string;
    params?: Record<string, string>;
  };

  // Custom app events
  [key: string]: unknown;
}
```

### idp (Identity Provider)

Container-provided authentication:

```typescript
interface Idp {
  // User information
  name: string;
  email: string;
  sub: string;
  roles: string[];

  // Role checking
  hasRole(role: string): boolean;

  // Token access
  getAccessToken(): Promise<string>;
  getIdToken(): Promise<string>;

  // Token management
  refreshToken(): Promise<void>;
  signOut(): Promise<void>;
}
```

---

## EventBus Communication Patterns

### Emitting Events (App → Container)

```typescript
import { useContext } from "@/composables/context";

const { eventBus } = useContext();

// Toast notification
eventBus.emit("toast", {
  title: "Success",
  detail: "Operation completed successfully",
  type: "success",
  timeout: 5000,
});

// Error reporting
eventBus.emit("error", {
  source: "my-microfrontend",
  error: new Error("Something went wrong"),
  info: "While saving user preferences",
});

// Navigation request (to container or other MFE)
eventBus.emit("navigate", {
  path: "/other-app/details",
  params: { id: "123" },
});

// Custom event
eventBus.emit("user-action", {
  action: "item-selected",
  itemId: "456",
  timestamp: Date.now(),
});
```

### Listening for Events (Container → App)

```typescript
import { onMounted, onUnmounted } from "vue";
import { useContext } from "@/composables/context";

const { eventBus } = useContext();

onMounted(() => {
  // Listen for global events
  eventBus.on("theme-changed", handleThemeChange);
  eventBus.on("language-changed", handleLanguageChange);
  eventBus.on("user-updated", handleUserUpdate);
});

onUnmounted(() => {
  // Clean up listeners
  eventBus.off("theme-changed", handleThemeChange);
  eventBus.off("language-changed", handleLanguageChange);
  eventBus.off("user-updated", handleUserUpdate);
});

function handleThemeChange(theme: "light" | "dark") {
  console.log("Theme changed to:", theme);
}

function handleLanguageChange(lang: string) {
  console.log("Language changed to:", lang);
}

function handleUserUpdate(user: { name: string; roles: string[] }) {
  console.log("User updated:", user);
}
```

### Event Composable

Create a reusable composable for event handling:

```typescript
// src/composables/useEventBus.ts
import { onMounted, onUnmounted } from "vue";
import { useContext } from "./context";

type EventHandler<T = unknown> = (data: T) => void;

export function useEventBus() {
  const { eventBus } = useContext();
  const listeners: Array<{ event: string; handler: EventHandler }> = [];

  function on<T>(event: string, handler: EventHandler<T>) {
    eventBus.on(event, handler as EventHandler);
    listeners.push({ event, handler: handler as EventHandler });
  }

  function emit<T>(event: string, data: T) {
    eventBus.emit(event, data);
  }

  // Cleanup on unmount
  onUnmounted(() => {
    listeners.forEach(({ event, handler }) => {
      eventBus.off(event, handler);
    });
  });

  return { on, emit };
}

// Usage in component
const { on, emit } = useEventBus();

on("some-event", (data) => {
  console.log("Received:", data);
});

emit("my-event", { foo: "bar" });
```

---

## IDP Integration Patterns

### Accessing User Information

```typescript
import { computed } from "vue";
import { useContext } from "@/composables/context";

const { idp } = useContext();

// Reactive user info
const userName = computed(() => idp.name);
const userEmail = computed(() => idp.email);
const userRoles = computed(() => idp.roles);

// Check permissions
const isAdmin = computed(() => idp.hasRole("admin"));
const canEdit = computed(() => idp.hasRole("editor") || idp.hasRole("admin"));
```

### Making Authenticated API Calls

```typescript
import { useContext } from "@/composables/context";

const { idp, config } = useContext();

async function fetchData() {
  const token = await idp.getAccessToken();

  const response = await fetch(`${config.apiBaseUrl}/api/data`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, try refresh
      await idp.refreshToken();
      return fetchData(); // Retry
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

### API Composable

Create a reusable API composable:

```typescript
// src/composables/useApi.ts
import { ref } from "vue";
import { useContext } from "./context";

export function useApi() {
  const { idp, config } = useContext();
  const loading = ref(false);
  const error = ref<Error | null>(null);

  async function request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    loading.value = true;
    error.value = null;

    try {
      const token = await idp.getAccessToken();

      const response = await fetch(`${config.apiBaseUrl}${endpoint}`, {
        ...options,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    } catch (err) {
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    get: <T>(endpoint: string) => request<T>(endpoint),
    post: <T>(endpoint: string, data: unknown) =>
      request<T>(endpoint, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    put: <T>(endpoint: string, data: unknown) =>
      request<T>(endpoint, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: <T>(endpoint: string) =>
      request<T>(endpoint, { method: "DELETE" }),
  };
}

// Usage
const api = useApi();
const data = await api.get<UserData>("/users/me");
```

---

## Runtime Configuration

### Configuration Loading

Configuration is loaded at mount time from `config.json`:

```typescript
// Load config relative to the entry module
const config = await fetch(
  new URL("../config.json", import.meta.url)
).then((r) => r.json());
```

### Configuration Structure

```json
{
  "apiBaseUrl": "https://api.vnrm.telekom.de",
  "featureFlags": {
    "newDashboard": true,
    "experimentalFeatures": false
  },
  "integrations": {
    "analytics": {
      "enabled": true,
      "endpoint": "/api/analytics"
    }
  }
}
```

### Environment-Specific Configuration

Use Helm ConfigMaps to inject environment-specific values:

```yaml
# helm/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  config.json: |
    {
      "apiBaseUrl": "{{ .Values.api.baseUrl }}",
      "featureFlags": {{ .Values.featureFlags | toJson }}
    }
```

---

## Routing Integration

### Catch-All Route Pattern

The microfrontend uses a catch-all route to handle all its internal paths:

```typescript
// src/pages/router.ts
import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Catch-all for all sub-routes
    {
      name: "CATCH_ALL",
      path: "/:pathMatch(.*)*",
      component: () => import("./app-shell.vue"),
      children: [
        {
          name: "HOME",
          path: "",
          component: () => import("./home-page.vue"),
        },
        {
          name: "DETAIL",
          path: "detail/:id",
          component: () => import("./detail-page.vue"),
          props: true,
        },
        {
          name: "SETTINGS",
          path: "settings",
          component: () => import("./settings-page.vue"),
        },
      ],
    },
  ],
});
```

### Navigation Guards with IDP

```typescript
import { useContext } from "@/composables/context";

router.beforeEach((to, from, next) => {
  // Note: useContext() may not work in guards outside component context
  // Use the context from the app instance instead

  // For permission checks, use meta fields
  if (to.meta.requiresAdmin) {
    // Check will happen in component
    next();
  } else {
    next();
  }
});
```

### Permission Check in Components

```typescript
// In component
import { onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useContext } from "@/composables/context";

const router = useRouter();
const route = useRoute();
const { idp, eventBus } = useContext();

onMounted(() => {
  if (route.meta.requiresAdmin && !idp.hasRole("admin")) {
    eventBus.emit("toast", {
      title: "Access Denied",
      detail: "You do not have permission to view this page",
      type: "error",
    });
    router.push("/");
  }
});
```

---

## Error Handling

### Global Error Handler

```typescript
// In handleInstance
app.config.errorHandler = (err, instance, info) => {
  console.error("[MFE Error]", err);

  // Report to container
  props.eventBus.emit("error", {
    source: "my-microfrontend",
    error: err instanceof Error ? err : new Error(String(err)),
    info: info,
    component: instance?.$options?.name,
  });

  // Show user-friendly message
  props.eventBus.emit("toast", {
    title: "An error occurred",
    detail: "Please try again or contact support",
    type: "error",
  });
};
```

### Async Error Handling

```typescript
// Promise rejection handler
app.config.warnHandler = (msg, instance, trace) => {
  console.warn("[MFE Warning]", msg, trace);
};

// Unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.error("[MFE Unhandled Rejection]", event.reason);
});
```

---

## Testing Container Integration

### Mock Container for Tests

```typescript
// src/test-utils/mock-container.ts
import { EventEmitter } from "eventemitter3";
import type { Idp } from "@/types/idp";

export function createMockContainer() {
  const eventBus = new EventEmitter();

  const idp: Idp = {
    name: "Test User",
    email: "test@example.com",
    sub: "test-123",
    roles: ["user"],
    hasRole: (role) => ["user"].includes(role),
    getAccessToken: async () => "mock-token",
    getIdToken: async () => "mock-id-token",
    refreshToken: async () => {},
    signOut: async () => {},
  };

  const config = {
    apiBaseUrl: "https://api.test.local",
    featureFlags: {
      testFeature: true,
    },
  };

  return { eventBus, idp, config };
}
```

### Component Test Example

```typescript
// src/pages/__tests__/home-page.spec.ts
import { describe, it, expect, vi } from "vitest";
import { shallowMount } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import HomePage from "../home-page.vue";
import { createContext } from "@/composables/context";
import { createMockContainer } from "@/test-utils/mock-container";

describe("HomePage", () => {
  function mount() {
    const { eventBus, idp, config } = createMockContainer();
    const context = createContext({ eventBus, idp, config });

    return {
      wrapper: shallowMount(HomePage, {
        global: {
          plugins: [createTestingPinia(), context],
          stubs: {
            "scale-button": true,
            "scale-card": true,
          },
        },
      }),
      eventBus,
      idp,
    };
  }

  it("displays user name from IDP", () => {
    const { wrapper } = mount();
    expect(wrapper.text()).toContain("Test User");
  });

  it("emits toast event on button click", async () => {
    const { wrapper, eventBus } = mount();
    const emitSpy = vi.spyOn(eventBus, "emit");

    await wrapper.find("scale-button").trigger("click");

    expect(emitSpy).toHaveBeenCalledWith("toast", expect.any(Object));
  });
});
```

---

## Validation Checklist

### Lifecycle

- [ ] `bootstrap`, `mount`, `unmount` exported from `main.ts`
- [ ] `handleInstance` installs all plugins
- [ ] `replaceMode: true` is set
- [ ] Config loads correctly at mount time

### EventBus

- [ ] Toast events work correctly
- [ ] Error events are emitted on failures
- [ ] Event listeners are cleaned up on unmount

### IDP

- [ ] User info is accessible in components
- [ ] `hasRole()` works for permission checks
- [ ] Token retrieval works for API calls
- [ ] Token refresh handles 401 errors

### Configuration

- [ ] `config.json` loads at runtime
- [ ] Configuration is accessible via `useContext()`
- [ ] Environment-specific values can be injected

---

## Next Steps

After completing container integration:

1. **Phase 5**: Deployment Setup - See `05-deployment-setup.md`
2. **Phase 6**: Troubleshooting - See `06-troubleshooting.md`
