---
name: ai4dev-product-managment-create-prd
description: Create Product Requirements Documents (PRDs) with structured templates. Use this skill whenever a user wants to write a PRD, product spec, requirements document, feature brief, or product proposal. Also trigger when someone mentions 'product requirements', 'feature spec', 'product brief', 'document what we're building', or wants to capture what a product or feature should do. Supports both full enterprise PRDs and lean startup-style PRDs.
argument-hint: "[feature-name] [--lean|--full]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-prd by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PRD Creator

Create well-structured Product Requirements Documents that align teams and drive clarity.

## Workflow

1. **Select template**
   - If `--lean` is passed, use the Lean PRD template
   - If `--full` is passed, use the Full PRD template
   - Otherwise, ask: "Full PRD (enterprise features, cross-team projects) or Lean PRD (MVPs, experiments, quick features)?"

2. **Gather context**
   - If a feature name is provided via $ARGUMENTS, use it as the starting point
   - Ask clarifying questions: What problem does this solve? Who is the target user? What does success look like?
   - Check the codebase for relevant existing documentation or code that provides context

3. **Generate the PRD** using the pm-best-practices skill for template guidance

4. **Save** as `prd-[feature-name].md` in the current directory

## Full PRD Template

```markdown
# PRD: [Feature/Product Name]

| Field | Value |
|-------|-------|
| Author | [Name] |
| Status | Draft |
| Created | [Date] |
| Last Updated | [Date] |
| Target Release | [Quarter/Date] |
| Priority | [P0/P1/P2/P3] |

## 1. Problem Statement
What problem are we solving? Who has this problem? How do we know this is a real problem?
Include data, user research, or support tickets that validate the problem.

## 2. Goals & Success Metrics
### Goals
- Primary goal
- Secondary goals

### Success Metrics (KPIs)
| Metric | Current | Target | Measurement Method |
|--------|---------|--------|--------------------|
| | | | |

### Non-Goals
What is explicitly out of scope for this initiative.

## 3. User Personas
### Primary Persona
- **Who**: Role/description
- **Pain Points**: What they struggle with today
- **Goal**: What they want to achieve

## 4. User Stories & Requirements
### Epic: [Epic Name]

| ID | User Story | Acceptance Criteria | Priority |
|----|-----------|---------------------|----------|
| US-001 | As a [persona], I want [action] so that [benefit] | Given/When/Then criteria | Must Have |

### Functional Requirements
- FR-001: [Requirement description]

### Non-Functional Requirements
- NFR-001: Performance - [requirement]
- NFR-002: Security - [requirement]
- NFR-003: Accessibility - [requirement]

## 5. User Experience
### User Flow
Describe the primary user flow step by step.

### Wireframes / Mockups
Reference or describe key screens/interactions.

## 6. Technical Considerations
- Architecture impact
- API changes needed
- Data model changes
- Third-party dependencies
- Migration requirements

## 7. Dependencies & Risks
### Dependencies
| Dependency | Team/System | Status | Impact if Delayed |
|-----------|-------------|--------|-------------------|
| | | | |

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| | | | |

## 8. Timeline & Milestones
| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Design Complete | | |
| Dev Start | | |
| Alpha/Beta | | |
| GA Release | | |

## 9. Stakeholders
| Name | Role | Responsibility |
|------|------|---------------|
| | | RACI: Responsible/Accountable/Consulted/Informed |

## 10. Open Questions
- [ ] Question 1

## Appendix
Additional context, research data, competitive analysis.
```

## Lean PRD Template

```markdown
# Lean PRD: [Feature Name]

**Author:** [Name] | **Date:** [Date] | **Status:** Draft

## Problem
One paragraph. What's broken? Who's affected? What evidence do we have?

## Hypothesis
We believe that [building this feature] for [these users] will [achieve this outcome].
We'll know we're right when [measurable signal].

## Solution
Describe the proposed solution in 2-3 paragraphs. Focus on the "what", not the "how".

## Key User Stories
1. As a [user], I want [capability] so that [benefit]
2. As a [user], I want [capability] so that [benefit]
3. As a [user], I want [capability] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Success Metrics
| Metric | Target | How We Measure |
|--------|--------|---------------|
| | | |

## Scope
**In scope:** What we're building
**Out of scope:** What we're explicitly not building

## Open Questions
- [ ] Question 1
```

## After Generation

- After generating, offer to create Jira stories from the PRD
- Pre-fill sections with intelligent defaults based on context
- If the user provides rough notes, expand them into proper PRD format
