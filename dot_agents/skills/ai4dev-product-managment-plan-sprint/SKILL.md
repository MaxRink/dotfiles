---
name: ai4dev-product-managment-plan-sprint
description: Plan sprints with capacity management, story selection, and sprint goal setting. Use this skill when a user wants to plan a sprint, estimate capacity, assign stories to sprints, set sprint goals, do release planning, or calculate velocity. Also trigger for 'iteration planning', 'what can we fit in the sprint', 'capacity planning', 'velocity check', 'how many points can we take', or any request to organize work into time-boxed iterations.
argument-hint: "[sprint-number] [--capacity=X]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/plan-sprint by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Sprint Planner

Structure sprint planning sessions with capacity analysis, story selection, and clear goals.

## Workflow

1. Set sprint parameters: number, duration, dates, team members
2. Calculate capacity based on team size, availability, and velocity
3. Select stories from backlog, fit to capacity
4. Define a clear, measurable sprint goal
5. Save to `sprint-[number]-plan.md`

## Sprint Plan Template

```markdown
# Sprint [Number] Plan
**Dates:** [Start Date] - [End Date] ([X] weeks)
**Sprint Goal:** [One sentence describing what success looks like]

## Team Capacity

| Team Member | Role | Available Days | Capacity (pts) | Notes |
|-------------|------|---------------|----------------|-------|
| | | | | PTO, meetings |
| **Total** | | **X days** | **X pts** | |

### Capacity Calculation
- Team velocity (last 3 sprints avg): [X] points
- Available capacity this sprint: [X]% of normal
- Recommended commitment: [X] points (80% of capacity for buffer)

## Sprint Backlog

### Committed Stories
| # | Story | Points | Assignee | Priority | Status |
|---|-------|--------|----------|----------|--------|
| 1 | | | | | To Do |

**Total committed:** [X] points / [X] capacity

### Stretch Goals
| # | Story | Points | Notes |
|---|-------|--------|-------|
| 1 | | | Pull in if capacity allows |

## Sprint Risks
- [ ] [Risk and mitigation]

## Carry-Over from Previous Sprint
| Story | Points | Reason | Action |
|-------|--------|--------|--------|
| | | | Continue / Re-estimate / Remove |

## Definition of Done (Reminder)
- Code reviewed and merged
- Tests written and passing
- Documentation updated
- Deployed to staging
- PO sign-off on acceptance criteria
```

## Velocity Tracking

```markdown
## Velocity History
| Sprint | Committed | Completed | % |
|--------|-----------|-----------|---|
| Sprint N-3 | X | X | X% |
| Sprint N-2 | X | X | X% |
| Sprint N-1 | X | X | X% |
| **Average** | **X** | **X** | **X%** |
```

## Release Planning Mode

For multi-sprint planning:

```markdown
# Release Plan: [Release Name]
**Target Date:** [Date]
**Sprints Remaining:** [X]

## Feature Breakdown
| Feature | Total Points | Sprint 1 | Sprint 2 | Sprint 3 | Status |
|---------|-------------|----------|----------|----------|--------|
| | | | | | |

## Burndown Projection
- Total scope: [X] points
- Average velocity: [X] points/sprint
- Sprints needed: [X]
- Buffer sprints: [X]
- Confidence: [High/Medium/Low]
```

## Capacity Rules of Thumb

- **Points per person per sprint**: ~8-10 for a 2-week sprint
- **Buffer**: Reserve 15-20% for unplanned work, bugs, support
- **Focus factor**: Multiply raw capacity by 0.7 for realistic planning
- Never plan at 100% capacity
