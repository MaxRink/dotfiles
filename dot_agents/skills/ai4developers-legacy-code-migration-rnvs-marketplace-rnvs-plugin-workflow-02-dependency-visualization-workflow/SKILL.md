---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-02-dependency-visualization-workflow
description: Generate validated PlantUML dependency diagrams (module-level and component-level) from Phase 1 analysis with automatic syntax validation. This skill should be used for Phase 2 dependency visualization after Phase 1 completion. Creates dependencies.puml (module view) and dependencies_detailed.puml (component view) with RNVS-specific color schemes, PL/SQL priority highlighting, and renderability checks. Includes PostToolUse hook auto-validation and user-interactive rework workflow.
allowed-tools: Read, Write, Bash, AskUserQuestion
hooks:
  PostToolUse:
    - matcher: "Write"
      pattern: "*.puml"
      hooks:
        - type: command
          command: "python /home/ron/claude4rnvs/rnvs-marketplace/rnvs-plugin/foundation/skills/plantuml-generator/scripts/validate.py"
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/02-dependency-visualization-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

# Phase 2: Dependency Visualization Workflow

**Purpose**: Transform Phase 1's structured dependency data into visual PlantUML diagrams.

**When to use**: After Phase 1 (Code Analysis) is complete, with file-inventory.json and dependency-graph.json available.

---

## Prerequisites (Execute First)

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/02-dependency-visualization-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/feature-definition.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features** → "Run /00-feature-definition-workflow first"

**Verify Phase 1 outputs exist**:
- `results/${FEATURE}/phase1/file-inventory.json`
- `results/${FEATURE}/phase1/dependency-graph.json`

If missing → "Complete /01-code-analysis-workflow first."
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 1 must be ✅ Complete
2. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**Update state**: Set Phase 2 to 🔄 In Progress, update Last Activity.

---

## Workflow Steps

1. **Load Phase 1 results** → file-inventory.json, dependency-graph.json
2. **Create module diagram** → dependencies.puml (high-level architecture)
3. **Create detailed diagram** → dependencies_detailed.puml (file-level, split if >20 components)
4. **Validate syntax** → PostToolUse hook auto-validates after each write
5. **Present to user** → show diagrams, ask for validation
6. **Rework if needed** → adjust per feedback (max 5 cycles)

---

## Output Files

- `results/${FEATURE}/phase2/dependencies.puml` - Module-level diagram (stakeholders, architects)
- `results/${FEATURE}/phase2/dependencies_detailed.puml` - File-level diagram (developers, migration)
- Split diagrams if >20 components: `dependencies_detailed_${module}.puml`

---

## RNVS-Specific Visualization Rules

**Visual Priority** (place prominently in diagrams):
1. PL/SQL packages at center/top - core business logic (`pack_body_*.sql`, `p_*.pks`)
2. C++ orchestration layer around PL/SQL
3. TCL scripts as integration layer

**Color Scheme**:
- Green (#LightGreen): High relevance (≥70)
- Yellow (#LightYellow): Medium relevance (40-69)

**Complexity Management**:
- ≤20 components: Single detailed diagram
- >20 components: Split by module

**External Systems** (use cloud/database icons):
- BNetzA Gateway (KCODE message exchange)
- CRM-T (operator data sync)
- Number Block Registry DB (T_RNB, T_HRNB tables)

For PlantUML templates, see [PLANTUML-PATTERNS.md](PLANTUML-PATTERNS.md).

---

## Source Priority: Phase 1 Only

All diagram content must come from Phase 1:
- Components from `file-inventory.json files[]`
- Dependencies from `dependency-graph.json edges[]`
- External systems from `external_dependencies[]`
- Relevance scores for color coding

**Do NOT invent** modules or dependencies not in Phase 1 data.

---

## Anti-Hallucination Checklist

Before finalizing diagrams:

- Every component exists in file-inventory.json
- Every dependency arrow exists in dependency-graph.json
- Every external system exists in external_dependencies
- Module groupings derived from file paths (not invented)
- Color coding matches relevance_score from Phase 1
- No components added based on "logical assumptions"

**Red Flags** (DO NOT DO):
- Adding components not in Phase 1
- Adding dependencies "because module A probably calls module B"
- Creating diagrams without reading Phase 1 results
- Ignoring validation errors

---

## Phase Integration

**From Phase 1 (Input)**:
- `files[]` → Components in diagram
- `files[].language` → Package grouping (PL/SQL, C++, TCL)
- `files[].relevance_score` → Color coding
- `edges[]` → Dependency arrows
- `external_dependencies[]` → External system nodes

**To Phase 3 (Output)**:
- dependencies.puml → Module boundaries for rule categorization
- dependencies_detailed.puml → Files implementing business rules

---

## Success Criteria

Phase 2 succeeds when:

1. dependencies.puml exists with module-level diagram
2. dependencies_detailed.puml exists (single or split)
3. All diagrams pass PlantUML syntax validation
4. All Phase 1 components and dependencies visualized
5. External systems clearly distinguished
6. Color coding and legend present
7. User has approved diagrams

---

## Final Step: Update Workflow State

After user approves diagrams, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 2**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 2 dependency visualization"
3. **Next Action**: "Run /03-business-rule-extraction-workflow ${FEATURE}"
4. **Decisions Log**: Add any visualization decisions (e.g., split diagrams)

---

## Quick Reference

| Document | Purpose |
|----------|---------|
| [PLANTUML-PATTERNS.md](PLANTUML-PATTERNS.md) | RNVS-specific PlantUML templates and patterns |
| [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md) | Complete verification checklist |
| [references/](references/) | Example PlantUML diagrams |

---

**Remember**: Phase 2 is about **visualization**, not new discovery. All data comes from Phase 1.
