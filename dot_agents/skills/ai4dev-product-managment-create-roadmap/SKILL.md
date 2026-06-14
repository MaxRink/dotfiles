---
name: ai4dev-product-managment-create-roadmap
description: Create and manage product roadmaps with timelines, themes, and feature planning. Use this skill when a user wants to build a roadmap, plan releases, create a timeline, visualize product strategy, or map features to quarters. Also trigger for 'product plan', 'release plan', 'feature timeline', 'what are we building next quarter', 'quarterly planning', or any request to organize features across time horizons.
argument-hint: "[timeframe] [--format=table|mermaid|now-next-later]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-roadmap by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Product Roadmap Creator

Create clear, actionable product roadmaps that communicate strategy and priorities.

## Workflow

1. Ask about timeframe, themes, features, and strategic goals
2. Organize features into themes and time horizons
3. Apply priority levels and dependencies
4. Generate the roadmap in the requested format
5. Save to `roadmap-[name].md`

## Format Detection

- `--format=table` or default: Quarterly table format
- `--format=mermaid`: Mermaid Gantt chart
- `--format=now-next-later`: Simple Now/Next/Later format

## Table Format (Default)

```markdown
# Product Roadmap: [Product/Team Name]
**Period:** [Q1 2026 - Q4 2026]
**Last Updated:** [Date]
**Owner:** [Name]

## Vision & Strategy
One paragraph describing the product vision and how this roadmap advances it.

## Strategic Themes
| Theme | Description | Business Objective |
|-------|-------------|--------------------|
| | | |

## Roadmap

### Now (Current Quarter - [Q1 2026])
High confidence, actively being worked on.

| Feature | Theme | Status | Team | Target Date |
|---------|-------|--------|------|-------------|
| | | In Progress / Planning | | |

### Next (Next Quarter - [Q2 2026])
Medium confidence, scoped and estimated.

| Feature | Theme | Status | Team | Target Date |
|---------|-------|--------|------|-------------|
| | | Planned | | |

### Later ([H2 2026])
Lower confidence, directional.

| Feature | Theme | Status | Team | Target Date |
|---------|-------|--------|------|-------------|
| | | Exploring | | |

## Dependencies
| Feature | Depends On | Team/System | Risk Level |
|---------|-----------|-------------|------------|
| | | | |

## Risks & Assumptions
- **Risk:** [description] — **Mitigation:** [action]
- **Assumption:** [what we're assuming is true]

## Change Log
| Date | Change | Reason |
|------|--------|--------|
| | | |
```

## Mermaid Gantt Format

```
gantt
    title Product Roadmap [Year]
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Theme 1
    Feature A        :active, a1, 2026-01-01, 2026-03-31
    Feature B        :       b1, after a1, 90d

    section Theme 2
    Feature C        :       c1, 2026-04-01, 60d
    Feature D        :       d1, after c1, 45d
```

## Now-Next-Later Format

```markdown
# Roadmap: [Product Name]

## Now (Committed)
- **[Feature]** — [one-line description] — [team] — [status]

## Next (Planned)
- **[Feature]** — [one-line description] — [team]

## Later (Exploring)
- **[Feature]** — [one-line description]

## Icebox (Parking Lot)
- [Feature idea] — [reason it's on hold]
```

## Guidelines

- Use Now/Next/Later for early-stage products; quarterly for mature products
- Always include dependencies — roadmaps without them create false expectations
- Flag risks so leadership can make informed trade-offs
- If features come from existing PRDs or Jira stories, reference them
