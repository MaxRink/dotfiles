---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-frontend-expert-scale-quality
description: Accessibility, best practices, and troubleshooting for Scale Design System. Invoke when validating implementations, fixing issues, or ensuring WCAG compliance.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/frontend-expert/skills/scale-quality by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Scale Quality & Troubleshooting Reference

**Purpose**: Provide quality assurance guidance including accessibility compliance, best practices, anti-patterns to avoid, and troubleshooting for common issues.

**When to use this skill**:
- Validating a Scale + Vue implementation
- Fixing issues with components not rendering, events not firing, etc.
- Ensuring WCAG 2.1 Level AA accessibility compliance
- Reviewing code for anti-patterns
- Debugging dark mode or styling issues

---

## Context from Orchestrator

When this skill is invoked, you should already have:
- A working Scale + Vue implementation
- Specific issues to troubleshoot OR validation requirements

---

## What This Skill Provides

### 1. Accessibility (07-accessibility.md)
- WCAG 2.1 Level AA compliance built into Scale
- Keyboard navigation patterns
- Screen reader support
- Accessible labels and ARIA
- Testing checklists

### 2. Best Practices (08-best-practices.md)
- Recommended patterns for forms, modals, toasts
- Anti-pattern checklist
- Red flags to watch for
- Performance considerations

### 3. Troubleshooting (09-troubleshooting.md)
- Components not rendering
- Events not firing
- v-model issues
- TypeScript errors
- Dark mode problems
- Common error messages

---

## Anti-Pattern Checklist

Before finalizing any Scale + Vue implementation, verify:

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| **Using `<button>` HTML element** | **Use `<scale-button>`** |
| **Using `<input>` HTML element** | **Use `<scale-text-field>`, `<scale-checkbox>`, etc.** |
| **Using `<select>` HTML element** | **Use `<scale-dropdown-select>`** |
| **Using `<a>` for styled links** | **Use `<scale-link>`** |
| **Using `<table>` HTML element** | **Use `<scale-table>` or `<scale-data-grid>`** |
| **Custom modal/dialog** | **Use `<scale-modal>`** |
| **Custom navbar/header** | **Use `<scale-telekom-header>` + `<scale-telekom-nav-list>`** |
| **Custom footer** | **Use `<scale-telekom-footer>`** |
| `v-model` on Scale component | `:value` + `@scale-change` |
| `@change` event | `@scale-change` event |
| `@scaleChange` (camelCase) | `@scale-change` (kebab-case) |
| Using deprecated proxy package | Direct Web Components |
| Hardcoded colors (`#fff`) | Design tokens (`var(--telekom-...)`) |
| Missing `isCustomElement` config | Configure in vite.config.ts |
| Missing CSS import | Import `@telekom/scale-components/dist/scale-components/scale-components.css` |
| Icon-only button without label | Add `aria-label` attribute |

**Scale-First Rule**: ALWAYS use Scale components instead of plain HTML. Only use `<div>`, `<span>`, `<p>`, `<h1>`-`<h6>`, `<section>`, `<main>`, `<header>`, `<footer>`, `<form>`, `<article>` for layout and semantic structure. For any interactive or styled element, check if Scale has a component first.

---

## Scale Coverage Audit

**Purpose**: Systematically verify that Scale components are used everywhere instead of plain HTML elements.

**Reference**: Invoke the `scale-components` skill for the complete catalog of all 63 Scale components and their HTML equivalents.

### When to Run This Audit

- After completing feature implementation (Step 6)
- Before final validation (Step 7)
- When reviewing existing code for Scale compliance

### Audit Process

#### Step 1: Scan for Forbidden HTML Elements

Use the Grep tool to search all `.vue` files for HTML elements that have Scale equivalents:

| Search Pattern | Scale Replacement | Grep Tool Call |
|----------------|-------------------|----------------|
| `<button` | `<scale-button>` | `Grep pattern="<button" glob="*.vue"` |
| `<input` | `<scale-text-field>`, `<scale-checkbox>`, `<scale-radio-button>`, `<scale-switch>` | `Grep pattern="<input" glob="*.vue"` |
| `<select` | `<scale-dropdown-select>` | `Grep pattern="<select" glob="*.vue"` |
| `<table` | `<scale-table>`, `<scale-data-grid>` | `Grep pattern="<table" glob="*.vue"` |
| `<textarea` | `<scale-textarea>` | `Grep pattern="<textarea" glob="*.vue"` |
| `<a href` | `<scale-link>` | `Grep pattern="<a href" glob="*.vue"` |
| `<progress` | `<scale-progress-bar>` | `Grep pattern="<progress" glob="*.vue"` |
| `<details` | `<scale-accordion>` | `Grep pattern="<details" glob="*.vue"` |
| `<dialog` | `<scale-modal>` | `Grep pattern="<dialog" glob="*.vue"` |

**Run all searches in parallel** using multiple Grep tool calls for efficiency.

#### Step 2: Cross-Reference with Scale Component Catalog

For each HTML element found, consult the `scale-components` skill to identify the correct Scale replacement:

| HTML Element | Scale Component(s) | Notes |
|--------------|-------------------|-------|
| `<button>` | `<scale-button>`, `<scale-icon-action-button>` | Use icon-action-button for icon-only |
| `<input type="text">` | `<scale-text-field>` | |
| `<input type="email">` | `<scale-text-field type="email">` | |
| `<input type="password">` | `<scale-text-field type="password">` | |
| `<input type="number">` | `<scale-text-field type="number">` | |
| `<input type="checkbox">` | `<scale-checkbox>` | |
| `<input type="radio">` | `<scale-radio-button>` | Wrap in `<scale-radio-button-group>` |
| `<input type="date">` | `<scale-date-picker>` | |
| `<input type="range">` | `<scale-slider>` | |
| `<select>` | `<scale-dropdown-select>` | |
| `<table>` | `<scale-table>`, `<scale-data-grid>` | Use data-grid for interactive tables |
| `<textarea>` | `<scale-textarea>` | |
| `<a>` (styled) | `<scale-link>` | Plain prose links may be acceptable |
| `<nav>` (app header) | `<scale-telekom-header>`, `<scale-telekom-nav-list>` | |
| `<footer>` (app footer) | `<scale-telekom-footer>` | |
| `<dialog>` | `<scale-modal>` | |
| `<details>/<summary>` | `<scale-accordion>` | |
| `<progress>` | `<scale-progress-bar>` | |
| Custom tooltip | `<scale-tooltip>` | |
| Custom toast/snackbar | `<scale-notification-toast>` | |
| Custom badge | `<scale-badge>`, `<scale-tag>` | |
| Custom tabs | `<scale-tab-nav>` | |
| Custom breadcrumb | `<scale-breadcrumb>` | |
| Custom pagination | `<scale-pagination>` | |
| Custom loading spinner | `<scale-loading-spinner>` | |

#### Step 3: Identify Valid Exceptions

Some HTML elements are acceptable and should NOT be flagged:

| Element | Reason | Action |
|---------|--------|--------|
| `<input type="hidden">` | No visual representation needed | Skip |
| `<input type="file">` | No Scale equivalent exists | Skip |
| `<a href>` in prose text | Plain navigation links in paragraphs | Skip (unless styled as button) |
| `<div>`, `<span>`, `<p>` | Layout and semantic structure | Skip |
| `<h1>`-`<h6>` | Heading structure | Skip |
| `<section>`, `<main>`, `<article>` | Semantic structure | Skip |
| `<form>` | Form wrapper | Skip |
| `<header>`, `<footer>` (semantic only) | Semantic structure without styling | Skip |

#### Step 4: Generate Violation Report

Document findings in this format:

```markdown
## Scale Coverage Audit Report

**Project**: [project-name]
**Files Scanned**: [count]

### Violations Found

| File | Line | Element | Recommended Replacement |
|------|------|---------|------------------------|
| `src/components/LoginForm.vue` | 24 | `<button>` | `<scale-button>` |
| `src/views/Settings.vue` | 87 | `<input type="text">` | `<scale-text-field>` |
| `src/components/DataTable.vue` | 15 | `<table>` | `<scale-data-grid>` |

### Exceptions (Acceptable)

| File | Line | Element | Reason |
|------|------|---------|--------|
| `src/components/FileUpload.vue` | 12 | `<input type="file">` | No Scale equivalent |

### Summary

- **Total violations**: X
- **Exceptions**: Y
- **Action required**: Fix X violations before proceeding
```

#### Step 5: Fix Violations

For each violation:
1. Invoke `scale-components` skill to get the correct component props and events
2. Replace the HTML element with the Scale equivalent
3. Update event bindings (`@change` → `@scale-change`, etc.)
4. Add required props (`:value`, `:label`, etc.)
5. Re-run the audit to confirm all violations are resolved

---

## Troubleshooting Guide

### Components Not Rendering

**Symptoms**: Blank space where component should be, or raw HTML tags visible

**Diagnosis**:
1. Check browser console for warnings about unknown elements
2. Verify `defineCustomElements()` is called in main.ts
3. Check `isCustomElement` configuration

**Solutions**:

```typescript
// main.ts - Ensure this exists
import { defineCustomElements } from '@telekom/scale-components/loader'
defineCustomElements()
```

```typescript
// vite.config.ts - Ensure isCustomElement is configured
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('scale-')
        }
      }
    })
  ]
})
```

---

### Events Not Firing

**Symptoms**: Click handlers don't trigger, form values don't update

**Diagnosis**:
1. Are you using `@scale-change` (not `@change`)?
2. Are you using kebab-case (not camelCase)?
3. Check browser DevTools > Elements > Event Listeners

**Solutions**:

```vue
<!-- WRONG -->
<scale-text-field @change="handleChange" />
<scale-text-field @scaleChange="handleChange" />

<!-- CORRECT -->
<scale-text-field @scale-change="handleChange" />
```

---

### v-model Not Working

**Symptoms**: Two-way binding doesn't update, values out of sync

**Cause**: Scale components are Web Components, not Vue components. `v-model` doesn't work.

**Solution**: Use manual binding pattern:

```vue
<!-- WRONG - v-model won't work -->
<scale-text-field v-model="email" />

<!-- CORRECT - manual binding -->
<scale-text-field
  :value="email"
  @scale-change="email = $event.target.value"
/>
```

Or create wrapper components (see `scale-components` skill).

---

### TypeScript Errors

**Symptoms**: `Property 'X' does not exist on type 'JSX.IntrinsicElements'`

**Solution**: Add type declarations:

```typescript
// src/types/scale.d.ts
declare namespace JSX {
  interface IntrinsicElements {
    'scale-button': any
    'scale-text-field': any
    'scale-checkbox': any
    'scale-modal': any
    'scale-dropdown-select': any
    'scale-switch': any
    'scale-card': any
    'scale-notification-toast': any
    // Add more as needed
  }
}

// For Vue template type checking
declare module 'vue' {
  interface GlobalComponents {
    'scale-button': any
    'scale-text-field': any
    // ... etc
  }
}
```

---

### Dark Mode Not Working

**Symptoms**: Components stay in light mode, custom styles don't adapt

**Diagnosis**:
1. Is `data-mode="dark"` set on `<body>` or container?
2. Are you using semantic tokens (not hardcoded colors)?

**Solutions**:

```typescript
// Ensure data-mode is set
document.body.setAttribute('data-mode', 'dark')
```

```css
/* Use semantic tokens that adapt automatically */
.my-element {
  background: var(--telekom-color-background-surface);  /* Adapts */
  color: var(--telekom-color-text-and-icon-standard);   /* Adapts */
}
```

---

### Styles Not Applied

**Symptoms**: Components render but look unstyled

**Solution**: Ensure CSS is imported in main.ts:

```typescript
// main.ts
import '@telekom/scale-components/dist/scale-components/scale-components.css'
```

---

### Modal Won't Close

**Symptoms**: Modal stays open after clicking close or backdrop

**Solution**:

```vue
<scale-modal
  :opened="isOpen"
  @scale-close="isOpen = false"  <!-- Must handle this event -->
>
  <!-- content -->
</scale-modal>
```

---

## Accessibility Checklist

### Keyboard Navigation
- [ ] All interactive elements reachable via Tab
- [ ] Focus visible on all elements
- [ ] Escape closes modals/dropdowns
- [ ] Enter/Space activates buttons

### Screen Readers
- [ ] All images have alt text (or are decorative with `alt=""`)
- [ ] Icon-only buttons have `aria-label`
- [ ] Form fields have associated labels
- [ ] Error messages linked with `aria-describedby`

### Visual
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] Not relying on color alone for meaning
- [ ] Focus indicators visible
- [ ] Text resizable to 200%

### Forms
- [ ] Required fields marked (Scale does this automatically)
- [ ] Error states clearly indicated
- [ ] Helper text available for complex inputs

---

## Validation Checklist

Before marking implementation complete:

### Setup
- [ ] `defineCustomElements()` called in main.ts
- [ ] `isCustomElement` configured for `scale-*` tags
- [ ] CSS file imported
- [ ] ESLint `vue/no-deprecated-slot-attribute` rule disabled
- [ ] TypeScript declarations added (if using TS)

### Scale-First Check

**Run the Scale Coverage Audit** (see section above) to systematically verify Scale component usage. The audit will search for forbidden HTML elements and generate a violation report.

Quick manual checklist:
- [ ] **No plain `<button>` elements** - using `<scale-button>` instead
- [ ] **No plain `<input>` elements** - using Scale form components instead
- [ ] **No plain `<select>` elements** - using `<scale-dropdown-select>` instead
- [ ] **No plain `<table>` elements** - using `<scale-table>` or `<scale-data-grid>` instead
- [ ] **No plain `<textarea>` elements** - using `<scale-textarea>` instead
- [ ] **No plain `<a>` styled as buttons** - using `<scale-link>` or `<scale-button>` instead
- [ ] **No custom modals** - using `<scale-modal>` instead
- [ ] **No custom navbar/header** - using `<scale-telekom-header>` + `<scale-telekom-nav-list>` instead
- [ ] **No custom footer** - using `<scale-telekom-footer>` instead
- [ ] **No custom loading spinners** - using `<scale-loading-spinner>` instead
- [ ] **No custom toast notifications** - using `<scale-notification-toast>` instead
- [ ] Plain HTML only used for layout (`<div>`, `<section>`) and text (`<p>`, `<h1>`)

**Reference**: Invoke `scale-components` skill for the complete catalog of all 63 Scale components.

### Components
- [ ] Using `@scale-*` events (not native events)
- [ ] Using manual value binding (not v-model)
- [ ] Slots use `slot` attribute (not `v-slot`)

### Theming
- [ ] Using semantic design tokens (not hardcoded colors)
- [ ] Dark mode tested (if implemented)
- [ ] Custom styles use CSS variables

### Accessibility
- [ ] Icon-only buttons have labels
- [ ] Form validation messages accessible
- [ ] Keyboard navigation works
- [ ] Focus management correct for modals

---

## After Using This Skill

Return to the main `scale-and-vue` workflow to:
- Continue building (Step 6) if issues are resolved
- Present final results (Step 7)

---

## Reference Files

For complete details, consult these reference files in this skill:
- `references/07-accessibility.md` - WCAG compliance details
- `references/08-best-practices.md` - Patterns and anti-patterns
- `references/09-troubleshooting.md` - Issue resolution
