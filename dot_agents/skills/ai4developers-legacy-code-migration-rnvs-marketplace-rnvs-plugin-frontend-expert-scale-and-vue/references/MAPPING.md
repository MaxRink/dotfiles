# Hybrid Architecture: Skill Mapping

This document explains how the 8-step workflow maps to skills and reference files in the hybrid architecture.

---

## Architecture Overview

```
frontend-expert-v3/skills/
├── scale-and-vue/              ← ORCHESTRATOR (entry point)
│   ├── SKILL.md                   Lightweight workflow guide
│   └── references/
│       ├── 01-overview.md         Scale introduction
│       └── 02-installation.md     Setup instructions
│
├── scale-components/           ← SUB-SKILL (components)
│   ├── SKILL.md                   Component patterns & wrappers
│   └── references/
│       ├── 03-events.md           Event handling
│       ├── 06-component-ref.md    All 63 components
│       └── vue-examples.md        Complete examples
│
├── scale-theming/              ← SUB-SKILL (theming)
│   ├── SKILL.md                   Theme implementation
│   └── references/
│       ├── 04-design-tokens.md    Token values
│       └── 05-theming-modes.md    Light/dark mode
│
└── scale-quality/              ← SUB-SKILL (quality)
    ├── SKILL.md                   Validation & troubleshooting
    └── references/
        ├── 07-accessibility.md    WCAG compliance
        ├── 08-best-practices.md   Patterns & anti-patterns
        └── 09-troubleshooting.md  Issue resolution
```

---

## Step-to-Skill Mapping

| Step | Name | Skill Used | References |
|------|------|------------|------------|
| 1 | Gather Requirements | `scale-and-vue` | 01-overview.md |
| 2 | Project Setup | `scale-and-vue` | 02-installation.md |
| 3 | Component Planning | `scale-components` | 06-component-ref.md |
| 4 | Core Patterns | `scale-components` | 03-events.md, vue-examples.md |
| 5 | Theming | `scale-theming` | 04-design-tokens.md, 05-theming.md |
| 6 | Build Features | `scale-components` | All component references |
| 7 | Validation | `scale-quality` | 08-best-practices.md, 07-accessibility.md |
| 8 | Troubleshooting | `scale-quality` | 09-troubleshooting.md |

---

## Invocation Flow

```
User starts → scale-and-vue (orchestrator)
                    │
                    ├── Step 1-2: Uses own references
                    │
                    ├── Step 3: Invoke scale-components
                    │                   │
                    │                   └── Returns component plan
                    │
                    ├── Step 4: Continue with scale-components
                    │
                    ├── Step 5: Invoke scale-theming
                    │                   │
                    │                   └── Returns theme config
                    │
                    ├── Step 6: Use scale-components
                    │
                    ├── Step 7: Invoke scale-quality
                    │                   │
                    │                   └── Returns validation results
                    │
                    └── Step 8: Use scale-quality if issues
```

---

## Benefits of Hybrid Architecture

1. **Lighter Initial Load**: Only orchestrator + basic refs loaded first
2. **On-Demand Loading**: Heavy component/theming refs loaded when needed
3. **Better Context Efficiency**: Not wasting tokens on unused content
4. **Modular Maintenance**: Each skill is independently updatable
5. **Reusable Sub-Skills**: Can invoke sub-skills directly for specific needs

---

## Direct Sub-Skill Invocation

Users can also invoke sub-skills directly for focused tasks:

- **Just need component help?** → Invoke `scale-components` directly
- **Just need theming help?** → Invoke `scale-theming` directly
- **Have a specific issue?** → Invoke `scale-quality` directly

The orchestrator is for full project workflows; sub-skills work standalone too.
