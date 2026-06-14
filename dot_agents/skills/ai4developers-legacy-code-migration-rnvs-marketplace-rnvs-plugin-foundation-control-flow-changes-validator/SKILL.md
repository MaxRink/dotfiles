---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-control-flow-changes-validator
description: Delta computation, change classification, and 5-gate quality validation for Phase 8.1 control flow changes. Computes delta from Phase 7.1 microservice changes, classifies change type (ADDITIVE/ENHANCEMENT/COMPLEX), and validates delta model quality. Use during Phase 8.1 validation stage to prepare inputs for control flow delta design.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/validation-generation/control-flow-changes-validator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Control Flow Changes Validator

## Purpose

Provides automated validation infrastructure for Phase 8.1 control flow changes design:

1. **Delta Computation**: Analyze Phase 7.1 microservice changes to determine which control flows need to be added or modified
2. **Change Classification**: Determine change type and complexity score with quality target
3. **Quality Validation**: 5-gate validation framework with transparent scoring

**Key Difference from Phase 8**: Phase 8.1 designs CHANGES to control flows (delta model), not complete flows from scratch.

## When to Use

Use this skill when you need to:

- **Compute control flow delta** from Phase 7.1 microservice changes
- **Classify change complexity** to determine quality targets
- **Validate delta model quality** before proceeding to diagram design
- **Generate validation reports** with actionable recommendations

**Phase Integration**: Used by Phase 8.1 workflow during validation stage. Quality checks are defined in Step 0/Final Step of the workflow skill.

## Agent Guidance

When you are invoked to use this skill for Phase 8.1 validation:

**Prerequisites**:
- Phase 5 completed: `results/${FEATURE}/phase5/control-flow-mapping.json`
- Phase 7.1 completed: `results/${FEATURE}/phase7.1/microservice-changes-design.json`

**Validation Pipeline**:
```bash
# Run the wrapper script for complete validation
bash ${CLAUDE_PLUGIN_ROOT}/foundation/skills/validation-generation/control-flow-changes-validator/scripts/validate-phase8.1.sh ${FEATURE}
```

**Pipeline Steps**:
1. **compute-control-flow-delta.js** → `computed-control-flow-delta.json` (what flows need to change)
2. **classify-change-type.js** → `classification.json` (change type and target)
3. **validate-changes.js** → `changes-quality-report.json` (5-gate validation)

**Outputs**:
- `results/${FEATURE}/phase8.1/computed-control-flow-delta.json`
- `results/${FEATURE}/phase8.1/classification.json`
- `results/${FEATURE}/phase8.1/changes-quality-report.json`

**Exit Codes**:
- `0`: COMPLETE - Ready for control flow delta design
- `1`: PARTIAL/INCOMPLETE - Review quality report for improvements
- `2`: Fatal error - Missing prerequisites

---

## Key Concepts

### Delta Model vs Full Specification

| Aspect | Phase 8 (NEW) | Phase 8.1 (CHANGES) |
|--------|---------------|---------------------|
| **Output** | Complete diagrams from scratch | Delta model (only changes) |
| **Size** | Many large PlantUML files | Focused changes, smaller output |
| **Pattern** | Full sequence, activity, saga, event | `sequences_to_add`, `sequences_to_modify` |

### Change Type Classification

| Type | Complexity | Quality Target | When |
|------|------------|----------------|------|
| **ADDITIVE** | < 10 | ≥80/100 | Simple additions, high clarity |
| **ENHANCEMENT** | 10-29 | ≥75/100 | Modifications, moderate complexity |
| **COMPLEX** | ≥30 | ≥70/100 | Many changes, comprehensive design |

### Microservice Change to Control Flow Impact

| Phase 7.1 Change | Control Flow Impact |
|------------------|---------------------|
| API endpoint added | New sequence diagram OR modify existing sequence |
| API endpoint modified | Modify sequence diagram (update interactions) |
| Database table added | New activity diagram (if complex logic) |
| Message Bus topic added | Modify event architecture diagram |
| Service dependency added | New sequence showing service interaction |
| Saga compensation added | New saga choreography diagram |

### 5-Gate Validation Framework

| Gate | Weight | Checks |
|------|--------|--------|
| **Completeness** | 30% | Delta categories populated, baseline/requirements present |
| **PlantUML Quality** | 30% | Diagram entries have name, use_case, rationale, source |
| **Documentation** | 20% | Changes have rationale explaining WHY |
| **Traceability** | 10% | Links to Phase 7.1 source changes |
| **Schema Validation** | 10% | JSON structure valid |

---

## Scripts Reference

### 1. compute-control-flow-delta.js

**Purpose**: Analyze Phase 7.1 microservice changes to determine control flow changes needed.

**Usage**:
```bash
node scripts/compute-control-flow-delta.js \
  --phase7.1 results/${FEATURE}/phase7.1/microservice-changes-design.json \
  --phase5 results/${FEATURE}/phase5/control-flow-mapping.json \
  --output results/${FEATURE}/phase8.1/computed-control-flow-delta.json
```

**Inputs**:
- **phase7.1**: Phase 7.1 microservice-changes-design.json (what microservices changed)
- **phase5**: Phase 5 control-flow-mapping.json (RNVS → VNRM flow requirements)

**Output Structure** (`computed-control-flow-delta.json`):
```json
{
  "baseline": {
    "source": "Phase 7.1 microservice changes",
    "version": "1.0.0"
  },
  "requirements": {
    "phase5_mapping": "control-flow-mapping.json",
    "phase7.1_design": "microservice-changes-design.json"
  },
  "changes": {
    "sequences_to_add": [...],
    "sequences_to_modify": [...],
    "activities_to_add": [...],
    "activities_to_modify": [...],
    "sagas_to_add": [...],
    "event_flows_to_modify": [...]
  }
}
```

**Exit Codes**:
- `0`: Success
- `1`: Validation error
- `2`: File not found or parse error

---

### 2. classify-change-type.js

**Purpose**: Analyze computed delta to determine change type, complexity score, and quality target.

**Usage**:
```bash
node scripts/classify-change-type.js \
  --delta results/${FEATURE}/phase8.1/computed-control-flow-delta.json \
  --output results/${FEATURE}/phase8.1/classification.json
```

**Output Structure** (`classification.json`):
```json
{
  "change_type": "ADDITIVE",
  "change_description": "Simple additions without modifications",
  "complexity_score": 9,
  "is_breaking_change": false,
  "quality_target": 80,
  "change_summary": {
    "sequences_to_add": 1,
    "activities_to_add": 1
  }
}
```

**Complexity Calculation**:
```javascript
complexity =
  sequences_to_add * 5 +
  sequences_to_modify * 3 +
  activities_to_add * 4 +
  activities_to_modify * 2 +
  sagas_to_add * 6 +
  event_flows_to_modify * 2
```

**Classification Logic**:
```javascript
if (hasModifications) {
  changeType = "ENHANCEMENT";   // Quality target: ≥75/100
} else if (complexity < 10) {
  changeType = "ADDITIVE";      // Quality target: ≥80/100
} else {
  changeType = "COMPLEX";       // Quality target: ≥70/100
}
```

---

### 3. validate-changes.js

**Purpose**: 5-gate validation with transparent heuristic scoring.

**Usage**:
```bash
node scripts/validate-changes.js \
  --delta results/${FEATURE}/phase8.1/computed-control-flow-delta.json \
  --classification results/${FEATURE}/phase8.1/classification.json \
  --output results/${FEATURE}/phase8.1/changes-quality-report.json
```

**Output Structure** (`changes-quality-report.json`):
```json
{
  "overall_status": "COMPLETE",
  "overall_quality_score": 85,
  "quality_target": 80,
  "gates_passed": 5,
  "validation_gates": [
    {"name": "completeness", "score": 90, "weight": 0.30, "passed": true},
    {"name": "plantuml_quality", "score": 85, "weight": 0.30, "passed": true},
    {"name": "documentation", "score": 80, "weight": 0.20, "passed": true},
    {"name": "traceability", "score": 75, "weight": 0.10, "passed": true},
    {"name": "schema_validation", "score": 100, "weight": 0.10, "passed": true}
  ],
  "errors": [],
  "warnings": [],
  "recommendations": ["Consider adding more detailed rationale for complex sequences"]
}
```

**Status Determination**:
```javascript
if (score >= quality_target) {
  status = "COMPLETE";      // Ready for Phase 8.1 design
} else if (score >= quality_target - 15) {
  status = "PARTIAL";       // Functional but needs improvement
} else {
  status = "INCOMPLETE";    // Significant gaps, needs rework
}
```

---

## Wrapper Script

**Simplified Usage** - orchestrates all 3 scripts:

```bash
bash scripts/validate-phase8.1.sh ${FEATURE}
```

**What it does**:
1. Validates prerequisites (Phase 5 and Phase 7.1 files exist)
2. Creates output directory `results/${FEATURE}/phase8.1/`
3. Runs all 3 scripts in sequence (compute-delta → classify → validate)
4. Provides colored progress output with status indicators
5. Returns aggregated exit code

**Example Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 8.1 Validation Pipeline
  Feature: priority-porting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Phase 8.1 Validation Pipeline Starting...

📊 Step 1/3: Computing control flow delta (from Phase 7.1 changes)
✅ Delta computed: results/priority-porting/phase8.1/computed-control-flow-delta.json

🏷️  Step 2/3: Classifying change type and complexity
✅ Classification complete: results/priority-porting/phase8.1/classification.json

   Change Type: ADDITIVE
   Complexity Score: 9
   Quality Target: ≥80/100

✔️  Step 3/3: Validating delta model quality

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Validation PASSED (COMPLETE status)
   Quality score ≥ target threshold
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Directory Structure

```
control-flow-changes-validator/
├── SKILL.md                               # This file
├── scripts/
│   ├── compute-control-flow-delta.js      # Delta computation
│   ├── classify-change-type.js            # Change classification
│   ├── validate-changes.js                # 5-gate validation
│   └── validate-phase8.1.sh               # Wrapper script
├── schemas/
│   ├── control-flow-delta.schema.json     # Delta model schema
│   └── quality-report.schema.json         # Validation report schema
└── references/
    ├── delta-example.json                 # Sample computed delta
    ├── classification-example.json        # Sample classification
    └── validation-example.json            # Sample validation report
```

---

## Best Practices

### 1. Run Scripts Sequentially

Scripts depend on each other's outputs:
1. **compute-control-flow-delta.js** → produces `computed-control-flow-delta.json`
2. **classify-change-type.js** → reads delta, produces `classification.json`
3. **validate-changes.js** → reads both, produces `changes-quality-report.json`

### 2. Check Exit Codes

All scripts use standard exit codes:
- `0` = Success
- `1` = Validation error (recoverable)
- `2` = Fatal error (file not found, parse error)

### 3. Validate Prerequisites

Before running, ensure:
- Phase 7.1 completed (microservice-changes-design.json exists)
- Phase 5 completed (control-flow-mapping.json exists)

### 4. Interpret Validation Results

- **COMPLETE**: Ready for control flow delta design
- **PARTIAL**: Functional but needs improvement
- **INCOMPLETE**: Significant gaps, needs rework

Check `recommendations[]` in quality report for specific fixes.

---

## Mock Validation Transparency

**Important**: This uses heuristic scoring, not real validators:

**What it validates**:
- Completeness: Checks if delta categories have data
- PlantUML Quality: Checks if diagram entries have basic structure
- Documentation: Checks if changes have rationale
- Traceability: Checks if entries link to Phase 7.1 sources
- Schema Validation: Basic JSON structure validation

**Limitations**:
- Does NOT validate PlantUML syntax
- Does NOT validate diagram semantics
- Does NOT check UML best practices
- Does NOT validate business logic consistency
- Does NOT validate against VNRM architecture patterns

**Future Enhancement**: Replace with real validators.

---

## Related Skills

- **microservice-changes-validator**: Phase 7.1 validator (same pattern)
- **control-flow-delta-design-guide**: Phase 8.1 delta model design methodology
- **control-flow-validator**: Phase 5 control flow validation
- **plantuml-generator**: PlantUML diagram generation

**Pattern Consistency**: Follows the same pattern as Phase 7.1 validators (one skill, multiple scripts, schemas, references).

---

## See Also

- Phase 8.1 Command: `/rnvs-workflow:phase8.1-design-control-flow-changes`
- Control Flow Delta Workflow: `08-1-control-flow-delta-workflow/SKILL.md`
- Examples in `references/` directory
