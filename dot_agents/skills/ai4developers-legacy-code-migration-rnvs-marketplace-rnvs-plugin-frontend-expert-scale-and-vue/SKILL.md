---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-frontend-expert-scale-and-vue
description: Vue 3 + Telekom Scale Design System workflow orchestrator. Start here for any Scale + Vue project. Guides through requirements, setup, and delegates to specialized sub-skills for components, theming, and troubleshooting.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/frontend-expert/skills/scale-and-vue by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Scale Design System with Vue 3 - Orchestrator

**Purpose**: Guide developers through building Vue 3 applications with Telekom Scale Design System using an interactive 8-step workflow.

**This is the entry point skill.** It orchestrates the workflow and invokes specialized sub-skills when detailed information is needed.

---

## Available Sub-Skills

| Skill | Purpose | When to Invoke |
|-------|---------|----------------|
| `scale-components` | Component catalog, events, v-model wrappers | Steps 3, 4, 6 - Component work |
| `scale-theming` | Design tokens, light/dark mode, branding | Step 5 - Theming |
| `scale-quality` | Accessibility, best practices, troubleshooting | Steps 7, 8 - Validation & fixes |

**How to invoke**: Use the Skill tool with the skill name (e.g., `scale-components`).

---

## 8-Step Interactive Workflow

### Step 1: Gather Requirements

**Objective**: Understand the user's project context before starting.

**Ask the user**:
1. **Project Type**: New project or existing? Full app or single SFC mockup?
2. **Build Tool**: Vite (recommended), Vue CLI, or Webpack?
3. **Package**: `@telekom/scale-components` (Telekom-branded) or `@telekom/scale-components-neutral` (open source)?
4. **UI Patterns Needed**: Forms, data display, navigation, feedback?
5. **Theming**: Default only, light/dark mode, or custom branding?
6. **TypeScript**: Yes or no?

**Output**: Document requirements for subsequent steps.

---

### Step 2: Project Setup

**Objective**: Install Scale and configure Vue 3 for custom elements.

**Reference**: `references/02-installation-and-setup.md`

#### Installation
```bash
# Telekom-branded (requires access)
npm install @telekom/scale-components@next

# OR open source neutral
npm install @telekom/scale-components-neutral@next
```

#### package.json (IMPORTANT)
**ALWAYS use an empty string `""` for the version to get the latest release. NEVER use a specific version like `"^3.0.0-beta.171"`.**

```json
{
  "dependencies": {
    "@telekom/scale-components": ""
  }
}
```

Or for the neutral version:
```json
{
  "dependencies": {
    "@telekom/scale-components-neutral": ""
  }
}
```

#### main.ts Configuration
```typescript
import { createApp } from 'vue'
import App from './App.vue'

// Scale imports
import { defineCustomElements } from '@telekom/scale-components/loader'
import '@telekom/scale-components/dist/scale-components/scale-components.css'

defineCustomElements()
createApp(App).mount('#app')
```

#### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

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

#### Validation Checkpoint
Ask user to verify:
```markdown
1. Run `npm run dev`
2. Add to App.vue: `<scale-button>Test</scale-button>`

Expected:
- [ ] No console warnings about unknown elements
- [ ] Button renders with Telekom styling
- [ ] Button is clickable

Does it work? (Yes / No / Issues)
```

**If issues**: Invoke `scale-quality` skill for troubleshooting.

---

### Step 3: Component Selection & Planning

**Objective**: Identify which Scale components are needed.

**Action**: Invoke the `scale-components` skill for detailed component reference.

```
Use Skill tool: scale-components
```

The sub-skill provides:
- Full catalog of 63 components
- Props and events for each
- Which components need v-model wrappers

**Output**: Component plan approved by user.

---

### Step 4: Implement Core Patterns

**Objective**: Create v-model wrappers and establish event handling patterns.

**Action**: Continue using `scale-components` skill (if not already loaded).

Key patterns to implement:
- ScaleInput.vue (text-field wrapper)
- ScaleCheckbox.vue (checkbox wrapper)
- ScaleSelect.vue (dropdown wrapper)

#### Quick Reference: Event Binding
```vue
<!-- Text fields: use $event.target.value -->
<scale-text-field
  :value="email"
  @scale-change="email = $event.target.value"
/>

<!-- Checkboxes: use $event.detail.checked -->
<scale-checkbox
  :checked="agreed"
  @scale-change="agreed = $event.detail.checked"
/>

<!-- Dropdowns: use $event.detail.value -->
<scale-dropdown-select
  :value="selected"
  @scale-change="selected = $event.detail.value"
>
```

**Validation**: Test that two-way binding works correctly.

---

### Step 5: Theming & Design Tokens

**Objective**: Configure light/dark mode and custom branding (if needed).

**Action**: Invoke the `scale-theming` skill.

```
Use Skill tool: scale-theming
```

The sub-skill provides:
- All design token values
- Light/dark mode implementation
- Theme composable with persistence
- Custom branding patterns

**Questions for user**:
- Follow system preference automatically?
- Manual toggle only?
- Both system + manual override?
- Custom brand colors needed?

---

### Step 6: Build Feature Components

**Objective**: Create the actual feature components.

**Action**: Use `scale-components` skill for component details.

For each feature component:
1. Identify required Scale components
2. Plan data/props structure
3. Implement with proper event binding
4. Add validation if needed

**Iterative process**:
```markdown
## Building: [ComponentName]

I'll create this component with:
- [Scale components used]
- [Features implemented]

Does this match your requirements? (Yes / Adjust)
```

---

### Step 7: Present Results & Final Validation

**Objective**: Validate the complete implementation.

**Action**: Invoke `scale-quality` skill for validation checklists and Scale Coverage Audit.

```
Use Skill tool: scale-quality
```

#### 7a: Run Scale Coverage Audit

Before final validation, run the **Scale Coverage Audit** (documented in `scale-quality` skill):

1. Use Grep tool to search all `.vue` files for forbidden HTML elements (`<button`, `<input`, `<select`, `<table`, `<textarea`, etc.)
2. Cross-reference findings with `scale-components` skill catalog
3. Identify valid exceptions (e.g., `<input type="hidden">`, `<input type="file">`)
4. Generate violation report
5. Fix any violations before proceeding

#### 7b: Present Implementation Summary

- Setup complete (packages, config)
- Components created (list with features)
- Theme configuration
- Files modified/created
- **Scale Coverage Audit**: Pass/Fail (violations found: X)

**Validation against anti-patterns**:
- Not using v-model directly on Scale components
- Using kebab-case events (@scale-change)
- isCustomElement configured
- CSS imported
- Semantic tokens used
- Accessible labels on icon-only buttons
- **All interactive elements use Scale components** (verified by audit)

---

### Step 8: Rework & Troubleshooting

**Objective**: Address any issues.

**Action**: Invoke `scale-quality` skill if not already loaded.

Common scenarios covered:
- Components not rendering
- Events not firing
- v-model issues
- TypeScript errors
- Dark mode not working
- Styling issues

**Iteration limit**: Maximum 3 rework cycles per issue.

---

## Workflow Summary

```
Step 1: Requirements     → Ask user questions
Step 2: Setup            → Install & configure (use references/)
Step 3: Component Plan   → Invoke scale-components skill
Step 4: Core Patterns    → Use scale-components skill
Step 5: Theming          → Invoke scale-theming skill
Step 6: Build Features   → Use scale-components skill
Step 7: Validation       → Invoke scale-quality skill
  └─ 7a: Scale Coverage Audit (search for forbidden HTML elements)
  └─ 7b: Present implementation summary
Step 8: Troubleshoot     → Use scale-quality skill
```

---

## Key Principles

1. **Scale-First Development** - ALWAYS use Scale components instead of plain HTML elements. Only use native HTML when NO Scale component exists. See `scale-components` skill for the full catalog and `scale-quality` skill for the anti-pattern checklist.
2. **Scale components are Web Components** - No v-model, use manual binding
3. **Events use `scale-` prefix** - `@scale-change`, not `@change`
4. **Props use kebab-case** - `helper-text`, not `helperText`
5. **Require Vue compiler config** - `isCustomElement` must be set
6. **Design tokens are mode-aware** - Use semantic tokens for theming

---

## Success Criteria

Implementation succeeds when:
- [ ] All `scale-*` components render correctly
- [ ] Events fire with `@scale-*` syntax
- [ ] Form values update correctly
- [ ] Design tokens used for theming
- [ ] Light/dark mode works (if implemented)
- [ ] No console warnings
- [ ] TypeScript types work (if using TS)
- [ ] Accessibility standards met
