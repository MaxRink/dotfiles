
# Functional Requirements Generation Reference

## Your Task

Generate functional requirements from business rules and control flows.

**Output:** `.migration/<feature>/spec-specification/functional-requirements.md`

## Input Context

Your prompt provides:

- Feature name
- `.migration/<feature>/analysis/analysis.json` (business_rules, control_flows, entities)
- `.migration/<feature>/architect/target-architecture.md` (Section 3: Component Design)
- `.migration/<feature>/plan/plan.json` (migration_goals, scope, focus_areas)

## Workflow

### 1. Extract Business Rules

From **analysis.json business_rules:**

- Group by category (validation, business logic, decision flows)
- Extract BR ID, summary, location, confidence score
- Extract pseudocode for each rule

### 2. Map Control Flows to Use Cases

From **analysis.json control_flows:**

- Identify actors (users, systems, external triggers)
- Extract preconditions and postconditions
- Map steps to business rules (using BR IDs)
- Identify alternate flows and exception scenarios

### 3. Component Assignment

From **architect target-architecture.md Section 3:**

- Identify which component owns each business rule
- Cross-reference component responsibilities
- Verify no BR is orphaned (every BR must be assigned to exactly one component)

### 4. Generate Functional Requirements

For each business rule, create a functional requirement:

```markdown
FR-{ID}: {Title}

**Business Rule Reference:** BR{NNN}
**Component:** {Component Name}
**Priority:** {High|Medium|Low}
**Description:** {What the system shall do}
**Source:** {file:line from analysis.json}
**Pseudocode:**
{language-agnostic pseudocode from analysis.json}

**Validation Rules:** (if BR involves input validation)
- Format: {standard name}
- Regex: {regular expression pattern}
- Min/Max: {numeric ranges or length constraints}
- Allowed values: {enum values or whitelist}
- Cross-field validation: {rules involving multiple fields}
- Error code: {error code to return if validation fails}
- Example valid: {concrete example of valid input}
- Example invalid: {concrete example of invalid input with error}

**Formula:** (if BR involves calculation)
- Expression: {mathematical formula with variable names}
- Precision: {decimal places for rounding, rounding strategy}
- Units: {currency code, measurement unit}
- Constants: {list all constants with values}
- Example calculation: {worked example with actual numbers}

**Acceptance Criteria:**
- {Specific, testable criterion 1}
- {Specific, testable criterion 2}

**Edge Cases:**
- {Edge case 1 with expected behavior}
- {Edge case 2 with expected behavior}
```

### 5. Generate Use Cases

For each control flow:

```markdown
UC-{ID}: {Use Case Name}

**Control Flow Reference:** CF{NNN}
**Primary Actor:** {Actor}
**Preconditions:** {List}
**Postconditions:** {List}

**Main Flow:**
1. {Step 1} — [BR{NNN}]
2. {Step 2} — [BR{NNN}]

**Alternate Flows:**
- AF1: {Condition} → {Behavior}

**Exception Flows:**
- EF1: {Error condition} → {Recovery behavior}

**Related Functional Requirements:** FR-{ID}, FR-{ID}
```

### 6. Pre-Write Validation

Before writing, verify:

- ✓ Every BR ID from analysis.json appears in at least one FR
- ✓ Every component from architect Section 3 is assigned at least one BR
- ✓ Edge cases documented for complex business rules (confidence < 0.8)
- ✓ Use cases trace back to control flows (CF IDs)
- ✓ Traceability matrix is complete

## Output Format

```markdown
# Functional Requirements

## Executive Summary
- Total business rules: N
- Total functional requirements: N
- Total use cases: N
- Component coverage: N/N components assigned

## 1. Validation Requirements
## 2. Business Logic Requirements
## 3. Decision Flow Requirements
## 4. Use Cases
## 5. Traceability Matrix

| BR ID | Functional Requirement | Component | Control Flow |
|-------|------------------------|-----------|--------------|
| BR001 | FR-001                 | ComponentA | CF001       |
```

## Completion

Return to orchestrator:

```text
DONE: functional-requirements.md written
- Functional requirements: N
- Use cases: N
- Business rules mapped: N/N
- Components covered: N/N
```
