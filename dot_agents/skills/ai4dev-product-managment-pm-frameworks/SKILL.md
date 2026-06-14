---
name: ai4dev-product-managment-pm-frameworks
description: Background knowledge for prioritization and planning frameworks — RICE scoring details, MoSCoW decision rules, Impact/Effort calibration, weighted scoring setup, velocity calculation methods, and roadmap communication levels. This is a reference skill (not an action skill) that provides deep framework knowledge when Claude needs to apply or explain these frameworks. Auto-loads alongside the prioritize, plan-sprint, and create-roadmap skills to provide detailed scoring guidance.
user-invocable: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/pm-frameworks by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PM Frameworks Reference

## Prioritization Frameworks

### RICE Scoring Deep Dive

**Reach** — How many users affected per quarter?

| Source | How to Estimate |
|--------|----------------|
| Analytics | Active users of affected feature area |
| Sales pipeline | Prospects who asked for this |
| Support tickets | Volume of related requests |
| Survey data | % respondents who want this x total users |

**Impact** — Effect on each user

| Score | Meaning | Example |
|-------|---------|---------|
| 3 | Massive | Solves core pain, saves hours/week |
| 2 | High | Significant improvement, users notice |
| 1 | Medium | Nice improvement, some users care |
| 0.5 | Low | Minor improvement |
| 0.25 | Minimal | Barely noticeable |

**Confidence** — How sure are we?

| Score | Meaning | Evidence Level |
|-------|---------|---------------|
| 100% | High | Data-backed, validated with users |
| 80% | Medium | Some data, reasonable assumptions |
| 50% | Low | Gut feel, limited evidence |

**Effort** — Person-months (all disciplines combined)

### MoSCoW Decision Rules

- **Must Have**: "If we ship without this, does the release make sense?" If yes, it's not a Must.
- **Should Have**: "Would users be disappointed but could work around it?"
- **Could Have**: "Would some users appreciate this but most wouldn't miss it?"
- **Won't Have**: Listing these is as important as Must Haves — prevents scope creep.

For detailed framework reference, read `${CLAUDE_SKILL_DIR}/references/framework-details.md`.

## Planning Frameworks

### Velocity Calculation

**Simple Average:**
```
Velocity = Sum of completed points (last 3 sprints) / 3
```

**Weighted Average (responds to trends):**
```
Velocity = (Sprint N-1 x 3 + Sprint N-2 x 2 + Sprint N-3 x 1) / 6
```

**When Velocity is Unreliable:**
- Team composition changed
- Sprint length changed
- Story point calibration shifted

Use capacity-based planning instead:
```
Capacity = Members x Available days x Focus factor (0.6-0.8) x Points per person-day
```

### Roadmap Communication Levels

| Audience | Detail | Time Horizon | Update Frequency |
|----------|--------|-------------|-----------------|
| Executive/Board | Themes + key bets | 12-18 months | Quarterly |
| Stakeholders | Features + timelines | 6-12 months | Monthly |
| Engineering | Stories + estimates | 1-3 months | Per sprint |
| Customers | Highlights + outcomes | 3-6 months | Quarterly |
