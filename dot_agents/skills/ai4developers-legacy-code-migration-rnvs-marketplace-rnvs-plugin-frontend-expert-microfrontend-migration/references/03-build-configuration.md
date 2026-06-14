# Build Configuration

This document provides complete build configuration for transforming a Vue 3 SPA into a deployable microfrontend.

---

## Overview

The build configuration must:

1. **Output ES Module format** for single-spa loading
2. **Externalize shared dependencies** (Vue, Vue Router) provided by container
3. **Bundle CSS into JavaScript** for seamless loading
4. **Produce stable entry filename** without content hash
5. **Inline assets as data URIs** to avoid path resolution issues
6. **Enable sourcemaps** for production debugging

---

## Complete Vite Configuration

### vite.config.ts

```typescript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";
import { resolve } from "path";

export default defineConfig({
  /**
   * Path alias for clean imports.
   */
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },

  /**
   * Build configuration for microfrontend output.
   */
  build: {
    /**
     * Enable sourcemaps for production debugging.
     */
    sourcemap: true,

    /**
     * Rollup-specific options for microfrontend bundling.
     */
    rollupOptions: {
      /**
       * Single entry point for single-spa.
       */
      input: "src/main.ts",

      /**
       * Preserve export signatures for single-spa lifecycle.
       */
      preserveEntrySignatures: "exports-only",

      /**
       * External dependencies provided by the container.
       * These are NOT bundled into the microfrontend.
       */
      external: ["vue", "vue-router"],

      /**
       * Output configuration.
       */
      output: {
        /**
         * Fixed filename without hash for container import.
         * Container imports: import('https://mfe.example.com/entry/main.js')
         */
        entryFileNames: "entry/main.js",

        /**
         * Hashed filenames for cache-busting of chunks and assets.
         */
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",

        /**
         * ES Module format required by single-spa.
         */
        format: "esm",

        /**
         * Global variable mappings for external dependencies.
         * These resolve to window globals provided by container.
         */
        globals: {
          vue: "Vue",
          "vue-router": "VueRouter",
        },
      },
    },

    /**
     * Inline all assets as data URIs.
     * Avoids path resolution issues when loaded from container.
     */
    assetsInlineLimit: Infinity,

    /**
     * Target modern browsers only.
     * Container only supports modern browsers.
     */
    target: "esnext",

    /**
     * Minify for production.
     */
    minify: "esbuild",

    /**
     * Clean output directory before build.
     */
    emptyOutDir: true,
  },

  /**
   * Plugin configuration.
   */
  plugins: [
    /**
     * Vue plugin with custom element recognition.
     */
    vue({
      template: {
        compilerOptions: {
          /**
           * Treat scale-* tags as custom elements (Web Components).
           * Prevents Vue from trying to resolve them as Vue components.
           */
          isCustomElement: (tag) => tag.startsWith("scale-"),
        },
      },
    }),

    /**
     * Inject CSS into JavaScript bundle.
     * Eliminates separate CSS file, simplifying container loading.
     */
    cssInjectedByJsPlugin(),
  ],

  /**
   * Development server configuration.
   */
  server: {
    /**
     * Port for standalone development.
     */
    port: 5173,

    /**
     * Open browser automatically.
     */
    open: true,

    /**
     * CORS headers for cross-origin development.
     */
    cors: true,
  },

  /**
   * Preview server configuration (for testing production build).
   */
  preview: {
    port: 4173,
    cors: true,
  },
});
```

---

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "importHelpers": true,
    "experimentalDecorators": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "useDefineForClassFields": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "types": ["vite/client"]
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.d.ts",
    "src/**/*.tsx",
    "src/**/*.vue",
    "env.d.ts"
  ],
  "exclude": ["node_modules", "dist"]
}
```

### env.d.ts

```typescript
/// <reference types="vite/client" />

/**
 * Vue Single File Component type declaration.
 */
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

/**
 * JSON module type declaration.
 */
declare module "*.json" {
  const value: any;
  export default value;
}

/**
 * Scale Web Components JSX declarations.
 * Add components as needed.
 */
declare namespace JSX {
  interface IntrinsicElements {
    "scale-button": any;
    "scale-card": any;
    "scale-text-field": any;
    "scale-checkbox": any;
    "scale-switch": any;
    "scale-dropdown-select": any;
    "scale-modal": any;
    "scale-notification-toast": any;
    "scale-tag": any;
    "scale-link": any;
    "scale-loading-spinner": any;
    "scale-progress-bar": any;
    "scale-accordion": any;
    "scale-tab-nav": any;
    "scale-breadcrumb": any;
    "scale-pagination": any;
    "scale-table": any;
    "scale-data-grid": any;
    "scale-tooltip": any;
    "scale-popover": any;
    "scale-menu-flyout": any;
    "scale-sidebar-nav": any;
    "scale-telekom-header": any;
    "scale-telekom-nav-list": any;
    "scale-telekom-nav-item": any;
    "scale-telekom-footer": any;
    // Add more as needed
  }
}

/**
 * Vue Global Components type declaration.
 */
declare module "vue" {
  interface GlobalComponents {
    "scale-button": any;
    "scale-card": any;
    "scale-text-field": any;
    // Add more as needed for better IDE support
  }
}
```

---

## ESLint Configuration

### eslint.config.js (Flat Config)

```javascript
import js from "@eslint/js";
import typescript from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import vue from "eslint-plugin-vue";
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,

  // TypeScript configuration
  {
    files: ["**/*.ts", "**/*.tsx", "**/*.vue"],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
    plugins: {
      "@typescript-eslint": typescript,
    },
    rules: {
      ...typescript.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },

  // Vue configuration
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: vue.parser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
    plugins: {
      vue,
    },
    rules: {
      ...vue.configs["vue3-recommended"].rules,
      // Allow slot attribute for Scale components
      "vue/no-deprecated-slot-attribute": "off",
      // Allow v-html for trusted content
      "vue/no-v-html": "warn",
      // Component naming
      "vue/component-name-in-template-casing": ["error", "kebab-case"],
      "vue/multi-word-component-names": "off",
    },
  },

  // Prettier compatibility
  prettier,

  // Ignore patterns
  {
    ignores: ["dist/**", "node_modules/**", "*.d.ts"],
  },
];
```

---

## package.json Configuration

### Complete package.json

```json
{
  "name": "@vnrm/my-microfrontend",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "node scripts/update-version.js && vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest run --coverage",
    "lint": "prettier --write . && eslint --fix .",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "pinia": "^3.0.0",
    "single-spa-vue": "^3.0.0",
    "vue-router": "^4.5.0"
  },
  "peerDependencies": {
    "vue": "^3.5.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "@pinia/testing": "^0.1.0",
    "@telekom/scale-components": "",
    "@types/node": "^22.0.0",
    "@typescript-eslint/eslint-plugin": "^8.0.0",
    "@typescript-eslint/parser": "^8.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "@vitest/coverage-v8": "^4.0.0",
    "@vue/test-utils": "^2.4.0",
    "eslint": "^9.0.0",
    "eslint-config-prettier": "^10.0.0",
    "eslint-plugin-vue": "^10.0.0",
    "eventemitter3": "^5.0.0",
    "jsdom": "^27.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.9.0",
    "vite": "^7.0.0",
    "vite-plugin-css-injected-by-js": "^3.5.0",
    "vitest": "^4.0.0",
    "vitest-mock-extended": "^3.0.0",
    "vue": "^3.5.0",
    "vue-tsc": "^2.2.0"
  }
}
```

**Important Notes**:

1. `vue` is a `peerDependency` - container provides it
2. `@telekom/scale-components` uses `""` for version - always get latest
3. `type: "module"` - ESM package
4. `private: true` - not published to npm

---

## Version Update Script

### scripts/update-version.js

```javascript
/**
 * Updates package.json version based on CI environment.
 * - Uses CI_COMMIT_TAG for releases
 * - Falls back to branch + commit for development
 */

import { readFileSync, writeFileSync, execSync } from "fs";
import { resolve } from "path";

// Only run in CI environment
if (!process.env.CI) {
  console.log("[update-version] Not in CI, skipping version update");
  process.exit(0);
}

const packagePath = resolve(process.cwd(), "package.json");
const pkg = JSON.parse(readFileSync(packagePath, "utf-8"));

let version;

if (process.env.CI_COMMIT_TAG) {
  // Release: use tag as version (strip 'v' prefix if present)
  version = process.env.CI_COMMIT_TAG.replace(/^v/, "");
} else {
  // Development: use branch + commit
  const branch = process.env.CI_COMMIT_REF_SLUG || "unknown";
  const commit = execSync("git rev-parse --short HEAD").toString().trim();
  version = `0.0.0+${branch}.${commit}`;
}

pkg.version = version;
writeFileSync(packagePath, JSON.stringify(pkg, null, 2) + "\n");

console.log(`[update-version] Updated version to: ${version}`);
```

---

## Vitest Configuration

### vitest.config.ts

```typescript
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      /**
       * Use jsdom for DOM testing.
       */
      environment: "jsdom",

      /**
       * Global test utilities (describe, it, expect).
       */
      globals: true,

      /**
       * Setup files run before each test file.
       */
      setupFiles: ["./src/test-setup.ts"],

      /**
       * Include patterns.
       */
      include: ["src/**/*.{test,spec}.{js,ts,vue}"],

      /**
       * Coverage configuration.
       */
      coverage: {
        provider: "v8",
        reporter: ["text", "cobertura", "html"],
        reportsDirectory: "./coverage",
        exclude: [
          "node_modules/",
          "dist/",
          "src/standalone/",
          "src/types/",
          "src/main.ts",
          "src/app.vue",
          "**/*.d.ts",
          "**/*.config.{js,ts}",
        ],
      },

      /**
       * Reporter configuration.
       */
      reporters: ["default", "junit"],
      outputFile: {
        junit: "./test-results/junit.xml",
      },
    },
  })
);
```

### src/test-setup.ts

```typescript
/**
 * Global test setup.
 */
import { vi } from "vitest";

// Mock Scale components globally
vi.mock("@telekom/scale-components/loader", () => ({
  defineCustomElements: vi.fn(),
}));

// Mock IntersectionObserver (used by some Scale components)
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

---

## Build Output Structure

After running `npm run build`:

```
dist/
├── entry/
│   └── main.js          # Main entry (no hash, ~50-200KB)
├── chunks/
│   └── [chunk]-[hash].js  # Code-split chunks (if any)
├── assets/
│   └── [asset]-[hash].ext  # Hashed assets (if not inlined)
└── config.json          # Runtime configuration (copied from public/)
```

**Key characteristics**:

1. `entry/main.js` - Fixed path, no hash (container imports this)
2. Single JavaScript file contains all code + CSS
3. Assets inlined as data URIs (no separate asset files)
4. Sourcemaps included for debugging

---

## Validation Checklist

### Build Configuration

- [ ] `rollupOptions.external` includes `vue` and `vue-router`
- [ ] `entryFileNames` is `entry/main.js` (no hash)
- [ ] `preserveEntrySignatures` is `exports-only`
- [ ] `format` is `esm`
- [ ] `assetsInlineLimit` is `Infinity`
- [ ] `sourcemap` is `true`

### Vue Configuration

- [ ] `isCustomElement` recognizes `scale-*` tags
- [ ] `cssInjectedByJsPlugin` is installed

### TypeScript Configuration

- [ ] `moduleResolution` is `bundler`
- [ ] `isolatedModules` is `true`
- [ ] Path alias `@/*` is configured

### ESLint Configuration

- [ ] `vue/no-deprecated-slot-attribute` is `off`
- [ ] Vue 3 recommended rules are enabled

### Package Configuration

- [ ] `type: "module"` is set
- [ ] `vue` is a `peerDependency`
- [ ] Scale version is `""` (empty string)

---

## Next Steps

After completing build configuration:

1. **Phase 4**: Container Integration - See `04-container-integration.md`
2. **Phase 5**: Deployment Setup - See `05-deployment-setup.md`
