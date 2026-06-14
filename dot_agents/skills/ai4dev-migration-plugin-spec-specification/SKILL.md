---
name: ai4dev-migration-plugin-spec-specification
description: Generate implementation-ready specifications from migration artifacts. Produces contracts.md, functional-requirements.md, nonfunctional-requirements.md, and technical-plan.md with full BR traceability.
argument-hint: <feature-name>
user-invocable: true
disable-model-invocation: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/spec-specification by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Spec Specification Workflow

Generate implementation-ready specifications by spawning a single generator
agent multiple times with different step parameters (contracts, functional,
nonfunctional, technical).

**Feature name**: use `$ARGUMENTS` if provided; otherwise read from
`.migration/migration.json` (`active_feature`).

## Before Starting — Validate Prerequisites

Required artifacts (validated by PreToolUse hook):

- `.migration/<feature>/plan/plan.json`
- `.migration/<feature>/analysis/analysis.json`
- `.migration/<feature>/architect/target-architecture.md`
- `.migration/<feature>/gap-analysis/gaps.json`

**Hard stop** if any artifact is missing — the hook will deny the tool call
and list missing files.

## Output

All files written to `.migration/<feature>/spec-specification/`.

```text
.migration/<feature>/spec-specification/
├── contracts.md                  # API contracts and integration specs
├── functional-requirements.md    # Functional requirements from BRs
├── nonfunctional-requirements.md # NFRs: performance, security, etc.
├── technical-plan.md            # Implementation plan
└── spec.json                     # Structured data for code generation
```

## Workflow

### Step 1 — Load Context

Read all required artifacts (hook injection provides them):

- `.migration/<feature>/plan/plan.json`
- `.migration/<feature>/analysis/analysis.json`
- `.migration/<feature>/architect/target-architecture.md`
- `.migration/<feature>/gap-analysis/gaps.json`

Build a unified context summary:

- Feature name and migration goals
- Business rules count and categories
- Components and architecture style
- Integration points and constraints
- Known gaps and severity

### Step 2 — Create Output Directory

Ensure the output directory exists:

```bash
mkdir -p .migration/<feature>/spec-specification/
```

### Step 3 — Spawn Parallel Specification Agents (Wave 1)

**IMPORTANT:** These three agents have NO dependencies on each other and
should be spawned **in parallel** for optimal performance.

**Spawn all three in a SINGLE message.** Do NOT send three separate messages.
Send ONE message with THREE `Agent` tool calls inside it.

Each agent reads its reference file from `skills/spec-specification/references/`.
Your prompt must tell the agent which reference file to read.

#### Agent 1: Contracts

- `subagent_type`: `one-modernizer:spec-specification-agent`
- `description`: "Generate API contracts"
- `prompt`:

  ```text
  Read `skills/spec-specification/references/contracts-reference.md` and follow it.

  Feature: <feature-name>

  Generate contracts.md for this feature.

  Context artifacts:
  [Paste relevant sections from:]
  - architect/target-architecture.md (Section 5: Integration Design)
  - analysis/analysis.json (dependencies array)
  - plan/plan.json (constraints.integration.systems)
  ```

#### Agent 2: Functional Requirements

- `subagent_type`: `one-modernizer:spec-specification-agent`
- `description`: "Generate functional requirements"
- `prompt`:

  ```text
  Read `skills/spec-specification/references/functional-reference.md` and follow it.

  Feature: <feature-name>

  Generate functional-requirements.md for this feature.

  Context artifacts:
  [Paste relevant sections from:]
  - analysis/analysis.json (business_rules, control_flows, entities)
  - architect/target-architecture.md (Section 3: Component Design)
  - plan/plan.json (migration_goals, scope, focus_areas)
  ```

#### Agent 3: Non-Functional Requirements

- `subagent_type`: `one-modernizer:spec-specification-agent`
- `description`: "Generate NFRs"
- `prompt`:

  ```text
  Read `skills/spec-specification/references/nonfunctional-reference.md` and follow it.

  Feature: <feature-name>

  Generate nonfunctional-requirements.md for this feature.

  Context artifacts:
  [Paste relevant sections from:]
  - plan/plan.json (focus_areas, constraints, target_stack)
  - architect/target-architecture.md (Sections 6, 7, 8: Security,
    Cross-Cutting, Performance)
  - gap-analysis/gaps.json
  ```

**Wait for all three agents to complete before proceeding to Step 4.**

### Step 4 — Spawn Technical Plan Agent (Wave 2)

**IMPORTANT:** This step depends on the outputs from Step 3, so it must run
**sequentially** after all three agents complete.

Use the `Agent` tool to spawn a single `spec-specification-agent`:

#### Agent 4: Technical Plan

- `subagent_type`: `one-modernizer:spec-specification-agent`
- `description`: "Generate technical implementation plan"
- `prompt`:

  ```text
  Read `skills/spec-specification/references/technical-reference.md` and follow it.

  Feature: <feature-name>

  Generate technical-plan.md for this feature.

  Context artifacts:
  [Paste relevant sections from:]
  - architect/target-architecture.md (all sections)
  - analysis/analysis.json (components, dependencies)
  - plan/plan.json (target_stack, constraints)
  - spec-specification/contracts.md (previously generated - READ THIS)
  - spec-specification/functional-requirements.md (previously generated -
    READ THIS)
  ```

**Wait for the agent to complete before proceeding to Step 5.**

### Step 5 — Generate spec.json

After all four markdown files are written, read them and create a structured
JSON file for code generation.

**Read the generated files:**

- `.migration/<feature>/spec-specification/contracts.md`
- `.migration/<feature>/spec-specification/functional-requirements.md`
- `.migration/<feature>/spec-specification/nonfunctional-requirements.md`
- `.migration/<feature>/spec-specification/technical-plan.md`

**Extract and structure:**

```json
{
  "feature": "<feature-name>",
  "generated": "<timestamp>",
  "components": [
    {
      "name": "ComponentName",
      "business_rules": ["BR001", "BR002"],
      "functional_requirements": ["FR-001", "FR-002"],
      "technology": "Spring Boot / FastAPI / etc",
      "api_endpoints": [],
      "dependencies": ["ExternalSystem1"]
    }
  ],
  "functional_requirements": [
    {
      "id": "FR-001",
      "br_id": "BR001",
      "component": "ComponentName",
      "priority": "High",
      "source": "file.java:123"
    }
  ],
  "nonfunctional_requirements": [
    {
      "id": "NFR-P001",
      "category": "performance",
      "priority": "High",
      "metric": "<100ms p95",
      "component": "ComponentName"
    }
  ],
  "contracts": [
    {
      "system": "PaymentGateway",
      "type": "REST",
      "endpoint": "POST /api/payment",
      "component": "PaymentService"
    }
  ],
  "traceability": {
    "BR001": {
      "functional_requirement": "FR-001",
      "component": "ComponentName",
      "control_flow": "CF001"
    }
  }
}
```

**Write:** `.migration/<feature>/spec-specification/spec.json`

### Step 6 — Cross-Specification Validation

After spec.json is generated, validate consistency:

1. **BR Coverage**: Every BR ID from analysis.json appears in
   functional-requirements.md
2. **Component Coverage**: Every component from architect appears in
   technical-plan.md
3. **Contract Coverage**: Every external system from contracts.md appears in
   technical-plan.md Section 5
4. **NFR Coverage**: All focus areas from plan.json have NFRs in
   nonfunctional-requirements.md
5. **Gap Coverage**: All gaps from gaps.json are documented in
   nonfunctional-requirements.md or functional-requirements.md
6. **Edge Cases**: Complex business rules (confidence < 0.8) have edge cases
   documented in functional-requirements.md

If any validation fails, regenerate spec.json after fixing the affected
markdown file.

### Step 7 — Present for Review

Show a summary to the user via `AskUserQuestion`:

```text
Specifications generated for <feature-name>:

  contracts.md: N integration points documented
  functional-requirements.md: N functional requirements (from N BRs)
  nonfunctional-requirements.md: N NFRs (Performance: N, Security: N,
  Reliability: N, Scalability: N)
  technical-plan.md: N component specs across N phases
  spec.json: Structured data for code generation

Cross-validation:
  ✓ BR coverage: N/N business rules mapped
  ✓ Component coverage: N/N components specified
  ✓ Contract coverage: N/N external systems documented
  ✓ NFR coverage: N/N focus areas covered
  ✓ Gap coverage: N gaps documented
  ✓ Edge case coverage: N complex rules have edge cases
```

Options: `["Approve and save", "Needs changes — I'll describe what to
adjust", "Regenerate a specific section"]`

If "Needs changes": accept feedback, spawn the appropriate agent(s) again
with the feedback to regenerate affected sections, re-present. Loop until
approved.

If "Regenerate a specific section": ask which section (contracts, functional,
nonfunctional, technical), spawn the specific agent again with feedback,
re-validate, re-present.

## Constraints

- **No new decisions** — follow architect output exactly; do not introduce
  new architectural choices
- **Technology stack fidelity** — target stack must match plan.json; do not
  substitute technologies
- **Full BR traceability** — every business rule from analysis must appear in
  functional-requirements.md with source references
- **Evidence-based** — all requirements trace back to specific artifacts
  (plan, analysis, architect, gaps)
- **Write only to `.migration/<feature>/spec-specification/`** — never touch
  source code or other artifacts
- **Sufficient for code generation** — technical-plan must have enough detail
  for automated implementation
- **Agent orchestration** — Wave 1: spawn 3 agents in parallel (step:
  contracts, functional, nonfunctional); Wave 2: spawn 1 agent sequentially
  (step: technical)
- **Sub-skill invocation** — use Agent tool with `subagent_type:
  one-modernizer:spec-specification-agent` and skill name in prompt

## Completion

After all five documents are saved and cross-validation passes:

```text
Specifications complete for <feature-name>.
Output: .migration/<feature-name>/spec-specification/
  - contracts.md (N integration points)
  - functional-requirements.md (N functional requirements)
  - nonfunctional-requirements.md (N NFRs)
  - technical-plan.md (N component specs)
  - spec.json (structured data for code generation)

Next step: /audit-spec
```

Do not invoke `/audit-spec` yourself — chaining handles it.
