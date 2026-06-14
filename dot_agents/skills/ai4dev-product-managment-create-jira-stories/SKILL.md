---
name: ai4dev-product-managment-create-jira-stories
description: Generate Jira stories, epics, and tasks with proper structure. Use this skill when a user wants to create Jira tickets, write user stories, break down work into tasks, generate stories from a PRD, or prepare items for sprint planning. Also trigger when someone says 'create tickets', 'write stories', 'break this into tasks', 'Jira', 'backlog items', or wants to structure development work into trackable items.
argument-hint: "[prd-file-or-description] [--from-prd|--manual]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-jira-stories by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Jira Story Creator

Generate well-structured Jira stories, epics, and tasks — either from an existing PRD or from scratch.

## Mode Detection

- If `--from-prd` is passed or $ARGUMENTS points to a `.md` file, auto-generate from PRD
- If `--manual` is passed or $ARGUMENTS is a description, guide manual creation
- If empty, ask: "Do you have an existing PRD to generate stories from, or create from scratch?"

## Mode 1: Auto-Generate from PRD

1. Read the PRD file
2. Extract user stories, requirements, and acceptance criteria
3. Organize into Epic > Story > Task hierarchy
4. Map PRD priorities: Must Have = Highest, Should Have = High, Could Have = Medium, Won't Have = Low
5. Include NFRs as separate technical stories

## Mode 2: Manual Creation

1. Ask: What feature or work are you describing?
2. Ask: Who is the user/persona?
3. Ask: What are the key capabilities needed?
4. Generate stories with proper structure

## Story Output Format

```markdown
# Jira Stories: [Feature Name]
Generated from: [PRD filename or "manual creation"]
Date: [date]

## Summary
| Type | Count | Total Points |
|------|-------|-------------|
| Epics | X | - |
| Stories | X | XX |
| Tasks | X | XX |
```

For each epic and story:

```markdown
## [EPIC] Epic Title
Epic description summarizing the initiative.

### Story: [Story Title]
**Type:** Story | Bug | Task | Spike
**Priority:** Highest | High | Medium | Low
**Story Points:** [estimate]
**Labels:** [relevant labels]

**Description:**
As a [persona], I want [capability] so that [benefit].

[Additional context]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]

**Technical Notes:**
- Implementation hints or constraints

**Dependencies:**
- Blocked by: [other story if applicable]
- Blocks: [other story if applicable]
```

## Estimation Reference

| Points | Complexity | Example |
|--------|-----------|---------|
| 1 | Trivial | Config change, copy update |
| 2 | Small | Simple UI change, add a field |
| 3 | Medium | New component, API endpoint |
| 5 | Large | Feature with multiple components |
| 8 | Very Large | Cross-system feature |
| 13 | Epic-sized | Break down further |

## Guidelines

- Stories must be INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable
- Each story should be completable in a single sprint
- If a story is >8 points, suggest breaking it down
- Save output as `jira-stories-[feature-name].md`
- After generating, offer to help with sprint planning
