# Migration Overview

This document provides the complete assessment process for migrating a Vue 3 SPA to the VNRM microfrontend architecture.

---

## What is a VNRM Microfrontend?

A VNRM microfrontend is a Vue 3 application that:

1. **Runs inside a container** - The VNRM shell (container) loads and orchestrates multiple microfrontends
2. **Uses single-spa** - Lifecycle hooks (`bootstrap`, `mount`, `unmount`) manage the app's lifecycle
3. **Shares dependencies** - Vue, Vue Router, and Scale components are provided by the container
4. **Communicates via EventBus** - Inter-app communication uses a shared event emitter
5. **Receives identity from container** - Authentication and user info come from the container's IDP

---

## Architecture Comparison

### Before: Traditional SPA

```
┌─────────────────────────────────────────┐
│              Browser                    │
│  ┌────────────────────────────────────┐ │
│  │         Your Vue 3 SPA             │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │  Vue + Vue Router + Pinia    │  │ │
│  │  │  Scale Components            │  │ │
│  │  │  Your Components             │  │ │
│  │  │  Authentication              │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### After: VNRM Microfrontend

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              VNRM Container (Shell)                    │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Vue + Vue Router (shared)                       │  │ │
│  │  │  Scale Components (shared)                       │  │ │
│  │  │  Authentication (IDP)                            │  │ │
│  │  │  EventBus (inter-app communication)              │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │ Your App    │  │ Other MFE   │  │ Other MFE   │     │ │
│  │  │ (mounted)   │  │ (mounted)   │  │ (unmounted) │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Pre-Migration Checklist

### Required Conditions

| Requirement | Check Command | Expected |
|-------------|---------------|----------|
| Vue 3.4+ | `npm ls vue` | `vue@3.4.x` or higher |
| Vue Router 4+ | `npm ls vue-router` | `vue-router@4.x` |
| Node 18+ | `node --version` | `v18.x` or higher |
| npm 9+ | `npm --version` | `9.x` or higher |

### Recommended Conditions

| Recommendation | Check | Benefit |
|----------------|-------|---------|
| Composition API | Check components for `<script setup>` | Easier context injection |
| TypeScript | Check for `tsconfig.json` | Type-safe container integration |
| Vite | Check for `vite.config.ts` | Simplest build migration |
| Pinia | Check for `src/stores/` | Compatible state management |
| Scoped CSS | Check for `<style scoped>` | No CSS conflicts |

---

## Source SPA Analysis

### Step 1: Analyze Entry Points

```bash
# Find all entry points
find src -name "main.ts" -o -name "main.js"

# Check current entry point content
cat src/main.ts
```

**What to look for**:
- How Vue app is created (`createApp`)
- What plugins are installed (router, store, etc.)
- Global component registrations
- Direct DOM mounting (`app.mount('#app')`)

### Step 2: Analyze Routing

```bash
# Find router configuration
find src -name "router*.ts" -o -name "router*.js" -o -name "index.ts" -path "*/router/*"

# Check route definitions
cat src/router/index.ts
```

**What to look for**:
- Route structure (flat vs nested)
- Navigation guards (beforeEach, afterEach)
- Dynamic imports (lazy loading)
- Base path configuration

### Step 3: Analyze State Management

```bash
# Check for Pinia
ls src/stores/ 2>/dev/null

# Check for Vuex
ls src/store/ 2>/dev/null

# Find store definitions
find src -name "*.store.ts" -o -name "*Store.ts"
```

**What to look for**:
- Store structure (modules, single store)
- Persistence plugins
- Global state dependencies

### Step 4: Analyze Components

```bash
# Count components
find src -name "*.vue" | wc -l

# Check for global component registrations
grep -r "app.component" src/

# Check for third-party UI libraries
grep -E "element-ui|vuetify|quasar|ant-design" package.json
```

**What to look for**:
- Total component count (complexity indicator)
- Global vs local component registration
- Third-party UI library usage (conflicts with Scale)
- Custom directive usage

### Step 5: Analyze Dependencies

```bash
# List production dependencies
npm ls --depth=0 --prod

# Check for problematic dependencies
grep -E "webpack|@vue/cli" package.json
```

**Problematic dependencies**:
| Dependency | Issue | Solution |
|------------|-------|----------|
| `@vue/cli-*` | Not Vite-compatible | Migrate to Vite |
| `webpack` | Different bundler | Migrate to Vite |
| `vuetify` | Conflicts with Scale | Remove, use Scale |
| `element-ui` | Conflicts with Scale | Remove, use Scale |
| `bootstrap-vue` | Conflicts with Scale | Remove, use Scale |

### Step 6: Analyze CSS

```bash
# Check for global CSS
find src -name "*.css" -not -path "*node_modules*"

# Check for CSS frameworks
grep -E "tailwind|bootstrap|bulma" package.json

# Check for scoped styles
grep -l "<style scoped>" src/**/*.vue 2>/dev/null | wc -l
```

**What to look for**:
- Global CSS files (need isolation)
- CSS frameworks (potential conflicts)
- Scoped vs unscoped styles ratio
- CSS custom properties usage

---

## Migration Complexity Matrix

### Complexity Score Calculation

| Factor | Low (1) | Medium (2) | High (3) |
|--------|---------|------------|----------|
| **Entry points** | Single main.ts | main.ts + plugins | Multiple entries |
| **Routing** | Simple flat routes | Nested routes, guards | Dynamic imports, complex guards |
| **State** | Local state only | Single Pinia store | Multiple stores, persistence |
| **External deps** | < 10, all ESM | 10-20, mostly ESM | > 20, non-ESM deps |
| **Components** | < 20 | 20-50 | > 50 |
| **CSS** | All scoped | Mixed scoped/global | Global, CSS framework |
| **Third-party UI** | None | Partial Scale | Full alternative framework |
| **Authentication** | None/simple | Token-based | Complex auth flows |

**Scoring**:
- 8-12: Low complexity (~1-2 days)
- 13-18: Medium complexity (~3-5 days)
- 19-24: High complexity (~1-2 weeks)

---

## Migration Strategy Selection

### Strategy A: Clean Migration (Recommended)

**When to use**: Complexity score < 15, or significant refactoring needed anyway

**Approach**:
1. Start from `microfrontend-vue-starter` template
2. Copy business logic and components
3. Adapt to new patterns as you go
4. Test incrementally

**Benefits**:
- Clean architecture from start
- No legacy patterns carried over
- Easier to maintain

### Strategy B: In-Place Migration

**When to use**: Complexity score >= 15, or tight timeline

**Approach**:
1. Modify existing project structure
2. Add dual-entry architecture
3. Update build configuration
4. Adapt component by component

**Benefits**:
- Preserves git history
- Gradual transition possible
- Less initial disruption

### Strategy C: Parallel Development

**When to use**: Critical production app, can't risk downtime

**Approach**:
1. Create new microfrontend project
2. Develop features in parallel
3. Gradually migrate users
4. Deprecate old SPA when ready

**Benefits**:
- Zero production risk
- Side-by-side testing
- Rollback always possible

---

## Pre-Migration Preparation

### 1. Create Migration Branch

```bash
git checkout -b feature/microfrontend-migration
```

### 2. Document Current State

Create `MIGRATION-NOTES.md`:
```markdown
# Migration Notes

## Source SPA Analysis
- Vue version: X.X.X
- Entry points: [list]
- Route count: X
- Component count: X
- Store count: X
- Complexity score: X

## Migration Strategy
[Selected strategy]

## Known Issues
[List any known issues that need addressing]

## Dependencies to Remove
[List deps that conflict with microfrontend architecture]

## Dependencies to Add
[List new deps needed for microfrontend]
```

### 3. Create Backup Points

```bash
# Tag current state
git tag pre-migration-backup

# Create branch for original SPA (if needed)
git branch original-spa-backup
```

### 4. Set Up Reference Template

```bash
# Clone or reference the starter template
# This will be your guide throughout migration
```

---

## Next Steps

After completing the assessment:

1. **Phase 2**: Code Migration - See `02-code-migration.md`
2. **Phase 3**: Build Configuration - See `03-build-configuration.md`
3. **Phase 4**: Container Integration - See `04-container-integration.md`
4. **Phase 5**: Deployment Setup - See `05-deployment-setup.md`

---

## Quick Reference: File Mapping

| Original SPA | Microfrontend | Notes |
|--------------|---------------|-------|
| `src/main.ts` | `src/main.ts` | Rewrite for single-spa |
| - | `src/standalone/main.ts` | Create for dev mode |
| `src/App.vue` | `src/app.vue` | Simplify to router-view only |
| `src/router/index.ts` | `src/pages/router.ts` | Catch-all pattern |
| `src/stores/` | `src/stores/` | Keep, no changes needed |
| `src/components/` | `src/components/` | Keep, update context usage |
| `src/views/` | `src/pages/` | Rename convention |
| - | `src/composables/context.ts` | Create for container context |
| - | `src/types/idp.ts` | Create for IDP types |
| - | `public/config.json` | Create for runtime config |
| `index.html` | `index.html` | Modify for standalone dev |
| `vite.config.ts` | `vite.config.ts` | Significant changes |
| - | `Dockerfile` | Create |
| - | `nginx/` | Create |
| - | `helm/` | Create |
