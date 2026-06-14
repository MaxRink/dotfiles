# ADR Markdown Template

Render `plan.adr.md` strictly from `plan.adr.json`. Do not add decisions, risks, scope, or technologies that are not present in the JSON.

Use this structure:

```markdown
# ADR: {{title}}

Status: {{status}}
Date: {{date}}
Feature: {{feature_name}}
Knowledge Level: {{knowledge_level}}
Migration Type: {{migration_type}}

## Context

{{context.summary}}
{{^context.summary}}
No context summary provided.
{{/context.summary}}

### Drivers

{{#context.drivers}}
- {{.}}
{{/context.drivers}}
{{^context.drivers}}
- None identified
{{/context.drivers}}

### Current State

{{context.current_state}}
{{^context.current_state}}
No current state defined.
{{/context.current_state}}

### Cross-Cutting Findings

{{#context.cross_cutting_findings}}
- {{.}}
{{/context.cross_cutting_findings}}
{{^context.cross_cutting_findings}}
- None identified
{{/context.cross_cutting_findings}}

## Decision

{{decision.summary}}
{{^decision.summary}}
No decision summary provided.
{{/decision.summary}}

Selected option: {{decision.selected_option}}
{{^decision.selected_option}}
Selected option not specified.
{{/decision.selected_option}}

Rationale: {{decision.rationale}}
{{^decision.rationale}}
No rationale provided.
{{/decision.rationale}}

### Rejected Options

{{#decision.rejected_options}}
- {{option}}: {{reason}}
{{/decision.rejected_options}}
{{^decision.rejected_options}}
- None identified
{{/decision.rejected_options}}

## Migration Goal

{{migration_goal.goal}}
{{^migration_goal.goal}}
No migration goal defined.
{{/migration_goal.goal}}

{{migration_goal.description}}
{{^migration_goal.description}}
No migration description provided.
{{/migration_goal.description}}

## Source Stack

### Languages
{{#source_stack.languages}}
- {{.}}
{{/source_stack.languages}}
{{^source_stack.languages}}
- None identified
{{/source_stack.languages}}

### Frameworks
{{#source_stack.frameworks}}
- {{.}}
{{/source_stack.frameworks}}
{{^source_stack.frameworks}}
- None identified
{{/source_stack.frameworks}}

### Infrastructure
{{#source_stack.infrastructure}}
- {{.}}
{{/source_stack.infrastructure}}
{{^source_stack.infrastructure}}
- None identified
{{/source_stack.infrastructure}}

## Target Stack

### Languages
{{#target_stack.languages}}
- {{.}}
{{/target_stack.languages}}
{{^target_stack.languages}}
- None identified
{{/target_stack.languages}}

### Frameworks
{{#target_stack.frameworks}}
- {{.}}
{{/target_stack.frameworks}}
{{^target_stack.frameworks}}
- None identified
{{/target_stack.frameworks}}

### Infrastructure
{{#target_stack.infrastructure}}
- {{.}}
{{/target_stack.infrastructure}}
{{^target_stack.infrastructure}}
- None identified
{{/target_stack.infrastructure}}

## Scope

Mode: {{scope.mode}}
{{^scope.mode}}
Mode not specified.
{{/scope.mode}}

### In Scope

{{#scope.include}}
- {{.}}
{{/scope.include}}
{{^scope.include}}
- None identified
{{/scope.include}}

### Out Of Scope

{{#scope.exclude}}
- {{.}}
{{/scope.exclude}}
{{^scope.exclude}}
- None identified
{{/scope.exclude}}

### Critical Components

{{#scope.critical_components}}
- {{.}}
{{/scope.critical_components}}
{{^scope.critical_components}}
- None identified
{{/scope.critical_components}}

### Boundaries

{{#scope.boundaries}}
- {{.}}
{{/scope.boundaries}}
{{^scope.boundaries}}
- None identified
{{/scope.boundaries}}

## Dependencies

### Internal

{{#dependencies.internal}}
- {{.}}
{{/dependencies.internal}}
{{^dependencies.internal}}
- None identified
{{/dependencies.internal}}

### External

{{#dependencies.external}}
- {{.}}
{{/dependencies.external}}
{{^dependencies.external}}
- None identified
{{/dependencies.external}}

## Constraints

### Unchanged

{{#constraints.unchanged}}
- {{.}}
{{/constraints.unchanged}}
{{^constraints.unchanged}}
- None identified
{{/constraints.unchanged}}

### Integration Systems

{{#constraints.integration}}
{{#systems}}
- {{.}}
{{/systems}}
{{^systems}}
- None identified
{{/systems}}
{{/constraints.integration}}
{{^constraints.integration}}
- None identified
{{/constraints.integration}}

## Risks

{{#risks}}
- {{severity}}: {{description}} Mitigation: {{mitigation}}
{{/risks}}
{{^risks}}
- None identified
{{/risks}}

## Success Criteria

{{#success_criteria}}
- {{.}}
{{/success_criteria}}
{{^success_criteria}}
- None identified
{{/success_criteria}}

## Focus Areas

{{#focus_areas}}
- {{.}}
{{/focus_areas}}
{{^focus_areas}}
- None identified
{{/focus_areas}}

## Modules

{{#modules}}
- **{{name}}** ({{role}}, source: {{source}}){{#notes}} — {{notes}}{{/notes}}
{{/modules}}
{{^modules}}
- None identified
{{/modules}}

## Consequences

### Positive

{{#consequences.positive}}
- {{.}}
{{/consequences.positive}}
{{^consequences.positive}}
- None identified
{{/consequences.positive}}

### Negative

{{#consequences.negative}}
- {{.}}
{{/consequences.negative}}
{{^consequences.negative}}
- None identified
{{/consequences.negative}}

### Follow-Up Decisions

{{#consequences.follow_up_decisions}}
- {{.}}
{{/consequences.follow_up_decisions}}
{{^consequences.follow_up_decisions}}
- None identified
{{/consequences.follow_up_decisions}}

## Source Documents

{{#source_documents}}
- {{path}}: {{used_for}}
{{/source_documents}}
{{^source_documents}}
- None identified
{{/source_documents}}

## Approval

Approved by: {{approvals.approved_by}}
{{^approvals.approved_by}}
Approved by not specified.
{{/approvals.approved_by}}

Approved at: {{approvals.approved_at}}
{{^approvals.approved_at}}
Approval date not specified.
{{/approvals.approved_at}}

Review iterations: {{approvals.review_iterations}}
{{^approvals.review_iterations}}
0
{{/approvals.review_iterations}}
```
