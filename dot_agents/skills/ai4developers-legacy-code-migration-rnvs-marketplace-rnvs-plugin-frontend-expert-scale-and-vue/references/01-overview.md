# Scale Design System - Overview

This document provides an overview of the Telekom Scale Design System for Vue 3 applications.

---

## What is Scale?

Scale is Deutsche Telekom's digital design system providing production-ready web components for building consistent, accessible applications. Key features:

- **63 Production-Ready Components**: Buttons, forms, modals, data grids, and more
- **Framework Agnostic**: Built as Web Components, works natively with Vue 3
- **Accessible by Default**: WCAG 2.1 Level AA compliant
- **Customizable Theming**: Design tokens for consistent styling
- **TypeScript Support**: Full type definitions included

---

## Packages

| Package | Description |
|---------|-------------|
| `@telekom/scale-components` | Core components (Telekom branded) |
| `@telekom/scale-components-neutral` | Core components (Open source, no branding) |
| `@telekom/scale-design-tokens` | Design tokens (Telekom branded) |
| `@telekom/scale-design-tokens-neutral` | Design tokens (Open source) |

> **Note**: The Vue-specific proxy packages (`@telekom/scale-components-vue`) are deprecated and will be removed in v4. Use the core packages directly.

---

## Architecture

Scale components are built as **Web Components** using Stencil.js. This means:

1. **Native Browser Support**: Works in all modern browsers without polyfills
2. **Framework Agnostic**: Same components work in Vue, React, Angular, or vanilla JS
3. **Shadow DOM Encapsulation**: Styles are scoped to components by default
4. **Custom Elements**: Components are used as HTML elements (`<scale-button>`)

---

## Key Concepts

### Web Components vs Vue Components

Scale components are **custom HTML elements**, not Vue components:

```vue
<!-- Scale components (custom elements) -->
<scale-button>Click Me</scale-button>
<scale-text-field label="Email" />

<!-- NOT Vue component syntax -->
<ScaleButton>Click Me</ScaleButton>  <!-- Wrong! -->
```

### Event Naming

Scale uses `scale-` prefixed events in kebab-case:

```vue
<scale-text-field @scale-change="handleChange" />
```

### No v-model Support

Web Components don't support Vue's `v-model`. Use manual binding:

```vue
<scale-text-field
  :value="email"
  @scale-change="email = $event.target.value"
/>
```

---

## License

- **Code**: Mozilla Public License 2.0 (MPL-2.0)
- **Telekom Brand Assets** (logos, magenta color, typeface, icons): Require Deutsche Telekom's express permission for commercial use

For open-source projects, use the neutral packages (`@telekom/scale-components-neutral`) to avoid brand licensing restrictions.

---

## Resources

- **GitHub Repository**: [https://github.com/telekom/scale](https://github.com/telekom/scale)
- **Documentation**: [https://telekom.github.io/scale/](https://telekom.github.io/scale/)
- **NPM Package**: [@telekom/scale-components](https://www.npmjs.com/package/@telekom/scale-components)
- **Vue 3 Examples**: Check `/examples/vue3-vite-boilerplate` in the repository
