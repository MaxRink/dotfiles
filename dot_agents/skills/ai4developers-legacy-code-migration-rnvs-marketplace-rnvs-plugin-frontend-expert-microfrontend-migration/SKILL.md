---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-frontend-expert-microfrontend-migration
description: Migrate Vue 3 SPA to VNRM microfrontend architecture with single-spa integration, container communication, and Kubernetes deployment. Full-stack guide covering code, build, Docker, Helm, and CI/CD.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/frontend-expert/skills/microfrontend-migration by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Vue 3 SPA to Microfrontend Migration

**Purpose**: Guide developers through transforming a standard Vue 3 Single Page Application into a deployable microfrontend that integrates with the VNRM container ecosystem.

**When to use this skill**:
- Migrating an existing Vue 3 SPA to microfrontend architecture
- Setting up a new microfrontend from scratch
- Integrating with VNRM container (single-spa)
- Configuring deployment pipeline (Docker, Helm, CI/CD)
- Troubleshooting microfrontend integration issues

---

## Reference Template

This skill uses the **microfrontend-vue-starter** as the reference implementation:
`C:\Users\A200367014\Programmieren\Hyperion\VNRM\microfrontend-vue-starter`

All patterns, configurations, and best practices are derived from this production-ready template.

---

## Migration Phases

| Phase | Scope | Reference File |
|-------|-------|----------------|
| 1. Assessment | Analyze current SPA structure | `01-migration-overview.md` |
| 2. Code Migration | Entry points, routing, state, components | `02-code-migration.md` |
| 3. Build Configuration | Vite, TypeScript, external dependencies | `03-build-configuration.md` |
| 4. Container Integration | single-spa lifecycle, context, events | `04-container-integration.md` |
| 5. Deployment Setup | Docker, Nginx, Helm, CI/CD | `05-deployment-setup.md` |
| 6. Troubleshooting | Common issues and solutions | `06-troubleshooting.md` |

---

## Phase 1: Assessment Checklist

Before starting migration, verify the source application:

### Compatibility Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| Vue 3.4+ | Required | Check `package.json` |
| Composition API | Recommended | Options API works but harder to refactor |
| TypeScript | Recommended | Improves container type safety |
| Vite | Recommended | Easiest migration path |
| Vue Router 4+ | Required | For routing integration |
| Pinia | Recommended | For state management |

### Current Structure Analysis

Run these commands to understand the source SPA:

```bash
# Check Vue version
npm ls vue

# List entry points
ls src/main.ts src/main.js 2>/dev/null

# Check router configuration
cat src/router/index.ts 2>/dev/null || cat src/router/index.js

# Check state management
ls src/stores/ 2>/dev/null || ls src/store/ 2>/dev/null
```

### Migration Complexity Assessment

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Entry points | Single main.ts | main.ts + plugins | Multiple entry points |
| Routing | Simple routes | Nested routes | Dynamic imports, guards |
| State | Local state only | Pinia stores | Vuex, global state |
| External deps | Few, tree-shakeable | Moderate | Many, non-ESM |
| CSS | Scoped, tokens | Mixed | Global styles, frameworks |

---

## Phase 2: Code Migration Summary

### Dual-Entry Architecture

The migrated app must support two modes:

**1. Microfrontend Mode** (`src/main.ts`)
- Exports single-spa lifecycle hooks
- Receives container props (`eventBus`, `idp`, `el`)
- No direct DOM mounting

**2. Standalone Mode** (`src/standalone/main.ts`)
- Direct Vue app creation
- Mocked container services
- Used for local development

### Key Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/main.ts` | Rewrite | single-spa entry point |
| `src/standalone/main.ts` | Create | Development entry |
| `src/composables/context.ts` | Create | Container context provider |
| `src/types/idp.ts` | Create | Identity provider types |
| `src/app.vue` | Simplify | Root component with router-view |
| `src/pages/router.ts` | Modify | Catch-all route pattern |
| `index.html` | Modify | Standalone dev entry |
| `public/config.json` | Create | Runtime configuration |

### Container Context Pattern

```typescript
// src/composables/context.ts
import type { App, InjectionKey } from "vue";
import type { EventEmitter } from "eventemitter3";
import type { Idp } from "@/types/idp";
import type Config from "../public/config.json";

type Context = {
  idp: Idp;
  eventBus: EventEmitter;
  config: typeof Config;
};

const CONTEXT: InjectionKey<Context> = Symbol("CONTEXT");

export function createContext(context: Context) {
  return {
    install: (app: App) => app.provide(CONTEXT, context),
  };
}

export function useContext(): Context {
  const context = inject(CONTEXT);
  if (!context) {
    throw new Error("Context not provided. Ensure app.use(createContext({...})) is called.");
  }
  return context;
}
```

**Reference**: See `references/02-code-migration.md` for complete implementation details.

---

## Phase 3: Build Configuration Summary

### Vite Configuration Requirements

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";

export default defineConfig({
  build: {
    sourcemap: true,
    rollupOptions: {
      input: "src/main.ts",
      preserveEntrySignatures: "exports-only",
      external: ["vue", "vue-router"],  // Provided by container
      output: {
        entryFileNames: "entry/main.js",  // No hash for container import
        assetFileNames: "assets/[name]-[hash][extname]",
        format: "esm",
      },
    },
    assetsInlineLimit: Infinity,  // Embed all assets as data URIs
  },
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith("scale-"),
        },
      },
    }),
    cssInjectedByJsPlugin(),  // Inline CSS into JS bundle
  ],
});
```

### Key Build Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| External deps | `vue`, `vue-router` | Container provides these |
| Entry filename | No hash | Container imports by fixed path |
| Asset handling | Inline as data URI | Avoid path resolution issues |
| CSS handling | Inject via JS | No separate CSS file to load |
| Sourcemaps | Enabled | Production debugging |

**Reference**: See `references/03-build-configuration.md` for complete configuration.

---

## Phase 4: Container Integration Summary

### single-spa Lifecycle

```typescript
// src/main.ts
import singleSpaVue from "single-spa-vue";
import { createApp, h } from "vue";
import { createPinia } from "pinia";
import App from "./app.vue";
import { router } from "./pages/router";
import { createContext } from "./composables/context";

type Props = {
  el: string;
  eventBus: EventEmitter;
  idp: Idp;
};

export const { bootstrap, mount, unmount } = singleSpaVue({
  createApp,
  appOptions: async (props: Props) => ({
    el: props.el,
    render: () => h(App),
  }),
  async handleInstance(app, props) {
    const config = await fetch(
      new URL("../config.json", import.meta.url)
    ).then((r) => r.json());

    app
      .use(createPinia())
      .use(router)
      .use(createContext({
        eventBus: props.eventBus,
        idp: props.idp,
        config,
      }));
  },
  replaceMode: true,
});
```

### Container Communication

| Pattern | Direction | Example |
|---------|-----------|---------|
| EventBus emit | App → Container | Toast notifications |
| EventBus listen | Container → App | Global events |
| IDP access | Container → App | User info, tokens, roles |
| Config | Container → App | Runtime settings |

```typescript
// Emit toast to container
const { eventBus } = useContext();
eventBus.emit("toast", {
  title: "Success",
  detail: "Operation completed",
  type: "success",
  timeout: 5000,
});

// Access user info from IDP
const { idp } = useContext();
const userName = idp.name;
const accessToken = await idp.getAccessToken();
```

**Reference**: See `references/04-container-integration.md` for complete patterns.

---

## Phase 5: Deployment Setup Summary

### Docker Configuration

```dockerfile
# Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/security.conf /etc/nginx/conf.d/security.conf
EXPOSE 8080
USER 1001
```

### Nginx Security Headers

```nginx
# nginx/security.conf
add_header Strict-Transport-Security "max-age=15768000" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### Helm Chart Structure

```
helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
```

### Security Context

```yaml
# values.yaml (excerpt)
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

**Reference**: See `references/05-deployment-setup.md` for complete deployment configuration.

---

## Phase 6: Troubleshooting Quick Reference

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| App doesn't mount | Missing lifecycle exports | Verify `export const { bootstrap, mount, unmount }` |
| "Vue is not defined" | Missing external | Add `vue` to `rollupOptions.external` |
| CSS not applied | CSS not bundled | Use `vite-plugin-css-injected-by-js` |
| Route not matching | Wrong base path | Use catch-all route `/:path(.*)*` |
| Context undefined | Missing provider | Ensure `app.use(createContext(...))` |
| Events not received | Wrong event name | Check container's expected event names |
| Build hash in filename | Wrong output config | Set `entryFileNames: "entry/main.js"` |
| Scale components missing | Not provided by container | Use container's Scale, don't bundle |

### Diagnostic Commands

```bash
# Check bundle output
ls -la dist/entry/

# Verify exports
cat dist/entry/main.js | head -20

# Check external deps
grep -r "from 'vue'" dist/

# Test container integration locally
npm run dev  # Uses standalone mode
```

**Reference**: See `references/06-troubleshooting.md` for detailed diagnostics.

---

## Migration Workflow

### Interactive 6-Step Process

```
Step 1: Assessment
├── Analyze source SPA structure
├── Check compatibility requirements
└── Estimate migration complexity

Step 2: Code Migration
├── Create dual-entry architecture
├── Implement context provider
├── Simplify root component
└── Configure catch-all routing

Step 3: Build Configuration
├── Configure Vite for ESM output
├── Set external dependencies
├── Configure CSS injection
└── Set up TypeScript

Step 4: Container Integration
├── Implement single-spa lifecycle
├── Set up container communication
├── Configure runtime config loading
└── Test with mocked container

Step 5: Deployment Setup
├── Create Dockerfile
├── Configure Nginx
├── Set up Helm charts
├── Configure CI/CD pipeline

Step 6: Validation & Troubleshooting
├── Test standalone mode
├── Test in container
├── Verify security configuration
└── Run deployment checklist
```

---

## Validation Checklist

### Code Migration

- [ ] `src/main.ts` exports `bootstrap`, `mount`, `unmount`
- [ ] `src/standalone/main.ts` exists for development
- [ ] `src/composables/context.ts` provides container context
- [ ] `src/types/idp.ts` defines identity provider interface
- [ ] `src/app.vue` contains only `<router-view />`
- [ ] Router uses catch-all pattern `/:path(.*)*`
- [ ] All components use `useContext()` for container services

### Build Configuration

- [ ] `vue` and `vue-router` are external dependencies
- [ ] Entry output is `entry/main.js` (no hash)
- [ ] CSS is injected via JavaScript
- [ ] Sourcemaps are enabled
- [ ] Scale components are NOT bundled
- [ ] `isCustomElement` configured for `scale-*`

### Container Integration

- [ ] Lifecycle hooks work correctly
- [ ] EventBus communication works
- [ ] IDP access provides user info
- [ ] Runtime config loads correctly
- [ ] Standalone mode works for development

### Deployment

- [ ] Docker image builds successfully
- [ ] Nginx serves on port 8080
- [ ] Security headers are set
- [ ] Helm chart deploys correctly
- [ ] Non-root user configured
- [ ] Read-only filesystem enabled
- [ ] Health probes configured

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| `scale-and-vue` | After migration, for Scale component integration |
| `scale-components` | Component selection and event binding |
| `scale-theming` | Design tokens and dark mode |
| `scale-quality` | Accessibility and best practices |

---

## Reference Files

For complete implementation details, consult these reference files:

- `references/01-migration-overview.md` - Full assessment process
- `references/02-code-migration.md` - Complete code examples
- `references/03-build-configuration.md` - Full Vite/TypeScript config
- `references/04-container-integration.md` - single-spa patterns
- `references/05-deployment-setup.md` - Docker, Nginx, Helm, CI/CD
- `references/06-troubleshooting.md` - Diagnostic procedures
