---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-microservice-changes-validator
description: Delta computation, change classification, and 5-gate quality validation for Phase 7.1 microservice changes. Computes delta between Phase 6 baseline and Phase 5 requirements, classifies change type (ADDITIVE/BREAKING/ENHANCEMENT/REFACTORING), and validates delta model quality. Use during Phase 7.1 validation stage to prepare inputs for delta model design.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/validation-generation/microservice-changes-validator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Microservice Changes Validator

## Purpose

Provides automated validation infrastructure for Phase 7.1 microservice changes design:

1. **Delta Computation**: Compare Phase 6 baseline (existing microservice) vs Phase 5 requirements (RNVS needs) to identify what needs to change
2. **Change Classification**: Determine change type and complexity score with quality target
3. **Quality Validation**: 5-gate validation framework with transparent scoring

**Key Difference from Phase 7**: Phase 7.1 designs CHANGES to existing services (delta model), not new services from scratch.

## When to Use

Use this skill when you need to:

- **Compute delta** between existing VNRM microservice and RNVS requirements
- **Classify change complexity** to determine quality targets
- **Validate delta model quality** before proceeding to Phase 8.1
- **Generate validation reports** with actionable recommendations

**Phase Integration**: Used by Phase 7.1 workflow during validation stage. Quality checks are defined in Step 0/Final Step of the workflow skill.

## Agent Guidance

When you are invoked to use this skill for Phase 7.1 validation:

**Prerequisites**:
- Phase 5 completed: `results/${FEATURE}/phase5/control-flow-mapping.json`
- Phase 6 completed: `results/${FEATURE}/phase6/analysis.json`

**Validation Pipeline**:
```bash
# Run the wrapper script for complete validation
bash ${CLAUDE_PLUGIN_ROOT}/foundation/skills/validation-generation/microservice-changes-validator/scripts/validate-phase7.1.sh ${FEATURE}
```

**Pipeline Steps**:
1. **compute-delta.js** → `computed-delta.json` (what needs to change)
2. **classify-change-type.js** → `classification.json` (change type and target)
3. **validate-changes.js** → `changes-quality-report.json` (5-gate validation)

**Outputs**:
- `results/${FEATURE}/phase7.1/computed-delta.json`
- `results/${FEATURE}/phase7.1/classification.json`
- `results/${FEATURE}/phase7.1/changes-quality-report.json`

**Exit Codes**:
- `0`: COMPLETE - Ready for delta model design
- `1`: PARTIAL/INCOMPLETE - Review quality report for improvements
- `2`: Fatal error - Missing prerequisites

---

## Key Concepts

### Delta Model vs Full Specification

| Aspect | Phase 7 (NEW) | Phase 7.1 (CHANGES) |
|--------|---------------|---------------------|
| **Output** | Full service specifications | Delta model (only changes) |
| **Size** | 30K-50K tokens per service | 5K-10K tokens |
| **Pattern** | Complete OpenAPI, DDL, Avro | `endpoints_to_add`, `tables_to_add` |

### Change Type Classification

| Type | Breaking | Complexity | Quality Target | When |
|------|----------|------------|----------------|------|
| **ADDITIVE** | No | < 10 | ≥80/100 | Simple additions only |
| **ENHANCEMENT** | No | 10-29 | ≥75/100 | Moderate complexity |
| **BREAKING** | Yes | Any | ≥70/100 | API modifications/deprecations |
| **REFACTORING** | No | ≥30 | ≥70/100 | High complexity, no breaking |

### 5-Gate Validation Framework

| Gate | Weight | Checks |
|------|--------|--------|
| **Completeness** | 30% | All delta categories populated with meaningful data |
| **API Quality** | 30% | Endpoints have path/method/description, schemas, RNVS mapping |
| **Database Quality** | 20% | Tables have purpose, source attribution |
| **Integration Quality** | 10% | Events/dependencies have descriptions, sources |
| **Schema Validation** | 10% | JSON structure valid (baseline, requirements, changes present) |

---

## Scripts Reference

### 1. compute-delta.js

**Purpose**: Compare Phase 6 baseline vs Phase 5 requirements to compute delta.

**Usage**:
```bash
node scripts/compute-delta.js \
  --phase6 results/${FEATURE}/phase6/analysis.json \
  --phase5 results/${FEATURE}/phase5/control-flow-mapping.json \
  --output results/${FEATURE}/phase7.1/computed-delta.json
```

**Inputs**:
- **phase6**: Phase 6 analysis.json (baseline - what EXISTS)
- **phase5**: Phase 5 control-flow-mapping.json (requirements - what's NEEDED)

**Output Structure** (`computed-delta.json`):
```json
{
  "baseline": {
    "service_name": "prt-fcpm-*",
    "version": "1.5.0"
  },
  "requirements": {
    "feature_name": "priority-porting"
  },
  "changes": {
    "api_changes": {
      "endpoints_to_add": [...],
      "endpoints_to_modify": [...],
      "endpoints_to_deprecate": [...]
    },
    "database_changes": {
      "tables_to_add": [...],
      "columns_to_add": [...],
      "indexes_to_add": [...]
    },
    "event_changes": {
      "topics_to_add": [...],
      "subscriptions_to_add": [...]
    },
    "state_machine_changes": {
      "new_states": [...],
      "new_transitions": [...]
    },
    "dependency_changes": {
      "new_internal_dependencies": [...]
    }
  }
}
```

**Algorithm**:
- **API Changes**: Compare by `path + method`, detect schema differences
- **Database Changes**: Extract table names from `database_operations`, compare vs schema
- **Event Changes**: Extract topic names from `events_published/consumed`, compare vs event_flows
- **State Changes**: Infer from `state_transitions`
- **Dependency Changes**: Compare service names from `microservices` list

---

### 2. classify-change-type.js

**Purpose**: Analyze computed delta to determine change type, complexity score, and quality target.

**Usage**:
```bash
node scripts/classify-change-type.js \
  --delta results/${FEATURE}/phase7.1/computed-delta.json \
  --output results/${FEATURE}/phase7.1/classification.json
```

**Output Structure** (`classification.json`):
```json
{
  "change_type": "ADDITIVE",
  "change_description": "Simple additions without modifications",
  "complexity_score": 8,
  "is_breaking_change": false,
  "quality_target": 80,
  "change_summary": {
    "endpoints_to_add": 2,
    "tables_to_add": 1,
    "topics_to_add": 1
  }
}
```

**Complexity Calculation**:
```javascript
complexity =
  endpoints_to_add * 1 +
  endpoints_to_modify * 2 +
  endpoints_to_deprecate * 3 +
  tables_to_add * 5 +
  columns_to_add * 2 +
  indexes_to_add * 1 +
  topics_to_add * 3 +
  subscriptions_to_add * 2 +
  new_states * 4 +
  new_transitions * 2 +
  new_dependencies * 3
```

**Classification Logic**:
```javascript
if (endpoints_to_deprecate > 0 || endpoints_to_modify > 0) {
  changeType = "BREAKING";      // Quality target: ≥70/100
} else if (complexity < 10) {
  changeType = "ADDITIVE";      // Quality target: ≥80/100
} else if (complexity < 30) {
  changeType = "ENHANCEMENT";   // Quality target: ≥75/100
} else {
  changeType = "REFACTORING";   // Quality target: ≥70/100
}
```

---

### 3. validate-changes.js

**Purpose**: 5-gate validation with transparent heuristic scoring.

**Usage**:
```bash
node scripts/validate-changes.js \
  --delta results/${FEATURE}/phase7.1/computed-delta.json \
  --classification results/${FEATURE}/phase7.1/classification.json \
  --output results/${FEATURE}/phase7.1/changes-quality-report.json
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
    {"name": "api_quality", "score": 85, "weight": 0.30, "passed": true},
    {"name": "database_quality", "score": 80, "weight": 0.20, "passed": true},
    {"name": "integration_quality", "score": 75, "weight": 0.10, "passed": true},
    {"name": "schema_validation", "score": 100, "weight": 0.10, "passed": true}
  ],
  "errors": [],
  "warnings": [],
  "recommendations": ["Consider adding more detailed RNVS source attribution"]
}
```

**Status Determination**:
```javascript
if (score >= quality_target) {
  status = "COMPLETE";      // Ready for Phase 8.1
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
bash scripts/validate-phase7.1.sh ${FEATURE}
```

**What it does**:
1. Validates prerequisites (Phase 5 and Phase 6 files exist)
2. Creates output directory `results/${FEATURE}/phase7.1/`
3. Runs all 3 scripts in sequence (compute-delta → classify → validate)
4. Provides colored progress output with status indicators
5. Returns aggregated exit code

**Example Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 7.1 Validation Pipeline
  Feature: priority-porting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Phase 7.1 Validation Pipeline Starting...

📊 Step 1/3: Computing delta (Phase 6 baseline vs Phase 5 requirements)
✅ Delta computed: results/priority-porting/phase7.1/computed-delta.json

🏷️  Step 2/3: Classifying change type and complexity
✅ Classification complete: results/priority-porting/phase7.1/classification.json

   Change Type: ADDITIVE
   Complexity Score: 8
   Breaking Change: false
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
microservice-changes-validator/
├── SKILL.md                               # This file
├── scripts/
│   ├── compute-delta.js                   # Delta computation
│   ├── classify-change-type.js            # Change classification
│   ├── validate-changes.js                # 5-gate validation
│   └── validate-phase7.1.sh               # Wrapper script
├── schemas/
│   ├── microservice-changes-design.schema.json   # Delta model schema
│   └── quality-report.schema.json                # Validation report schema
└── references/
    ├── delta-example.json                 # Sample computed delta
    ├── classification-example.json        # Sample classification
    └── validation-example.json            # Sample validation report
```

---

## Best Practices

### 1. Run Scripts Sequentially

Scripts depend on each other's outputs:
1. **compute-delta.js** → produces `computed-delta.json`
2. **classify-change-type.js** → reads delta, produces `classification.json`
3. **validate-changes.js** → reads both, produces `changes-quality-report.json`

### 2. Check Exit Codes

All scripts use standard exit codes:
- `0` = Success
- `1` = Validation error (recoverable)
- `2` = Fatal error (file not found, parse error)

### 3. Validate Prerequisites

Before running, ensure:
- Phase 6 completed (analysis.json exists)
- Phase 5 completed (control-flow-mapping.json exists)

### 4. Interpret Validation Results

- **COMPLETE**: Ready for delta model design
- **PARTIAL**: Functional but needs improvement
- **INCOMPLETE**: Significant gaps, needs rework

Check `recommendations[]` in quality report for specific fixes.

---

## Mock Validation Transparency

**Important**: This uses heuristic scoring, not real validators:

**What it validates**:
- Completeness: Checks if delta categories have data
- API Quality: Checks if endpoints have basic structure
- Database Quality: Checks if tables have purpose and source
- Integration Quality: Checks if events/deps have descriptions
- Schema Validation: Basic JSON structure validation

**Limitations**:
- Does NOT validate OpenAPI 3.0 syntax
- Does NOT validate PostgreSQL DDL syntax
- Does NOT validate Avro schemas
- Does NOT check business rule consistency
- Does NOT validate against VNRM architecture patterns

**Future Enhancement**: Replace with real validators.

---

## Related Skills

- **vnrm-code-analysis-schema**: Defines Phase 6 baseline schema
- **control-flow-validator**: Phase 5 control flow validation
- **07-1-microservice-delta-workflow**: Phase 7.1 delta model design methodology
- **control-flow-changes-validator**: Phase 8.1 validation (similar pattern)

**Pattern Consistency**: Follows the same pattern as Phase 2-5 validators (one skill, multiple scripts, schemas, references).

---

## See Also

- Phase 7.1 Command: `/rnvs-workflow:phase7.1-design-changes-in-microservice`
- Microservice Delta Workflow: `07-1-microservice-delta-workflow/SKILL.md`
- Examples in `references/` directory
