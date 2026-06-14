---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-rule-validator
description: Comprehensive validation framework for Phase 3 business rule extraction with 5-gate quality system. Use when validating ruletable.json outputs, ensuring rule completeness, or assessing business rule quality in the RNVS-VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/rule-validator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Business Rule Validator Skill

## Purpose

Provides a comprehensive 5-gate validation framework for Phase 3 business rule extraction outputs. Ensures rule completeness, confidence quality, source traceability, categorization accuracy, and JSON schema compliance with automatic quality scoring.

## When to Use

- **Phase 3 Validation**: Validate ruletable.json after rule extraction
- **Quality Assurance**: Check rule extraction completeness against Phase 1 and Phase 2 inputs
- **Automatic Iteration**: Identify validation failures to trigger rule extraction improvements
- **Production Readiness**: Verify business rules meet quality thresholds before Phase 4

## Validation Framework

### 5-Gate Validation System

Similar to Phase 2's diagram validation, Phase 3 uses a multi-gate validation system:

**Gate 1: Rule Completeness** (Threshold: ≥80%)
- Every component from Phase 1 analysis.json has at least one extracted rule
- Every flow from Phase 2 PHASE2_SUMMARY.md has associated rules
- All database operations have validation or business logic rules
- Metric: Percentage of expected sources with rules

**Gate 2: Confidence Quality** (Threshold: ≥70%)
- Percentage of rules with confidence score ≥ 4 (High/Very High)
- All confidence scores have documented reasoning
- Critical business impact rules have confidence ≥ 4
- Metric: Percentage of high-confidence rules

**Gate 3: Source Traceability** (Threshold: 100%)
- Every rule references source location (Phase 1 component/function or Phase 2 flow diagram)
- All source locations are valid (files exist, line numbers reasonable)
- No generic "Unknown" or empty source locations
- Metric: Percentage of rules with valid source references

**Gate 4: Categorization Completeness** (Threshold: 100%)
- Every rule has type (validation/business_logic/integration/compliance)
- Every rule has business_impact (critical/high/medium/low)
- Flow-based rules reference business_flow name or KCODE
- All required metadata fields populated
- Metric: Percentage of rules with complete categorization

**Gate 5: JSON Schema Validation** (Threshold: 100%)
- ruletable.json is valid JSON
- All required fields present (rule_id, description, type, confidence, etc.)
- Field types match schema (numbers are numbers, strings are strings)
- No malformed or invalid data
- Metric: Pass/Fail

### Quality Score Calculation

```
Overall Quality Score = (
  Gate1_percentage * 0.25 +
  Gate2_percentage * 0.30 +
  Gate3_percentage * 0.20 +
  Gate4_percentage * 0.15 +
  Gate5_pass * 10
) * 100 / 100

Where:
- Gate1-4: Percentage values (0-100)
- Gate5: 1 if passed, 0 if failed
- Final score: 0-100
```

**Threshold for COMPLETE Status**: Overall quality score ≥ 75

### Validation Output

The validator generates `rule-quality-report.json`:

```json
{
  "feature": "NBM",
  "phase": 3,
  "timestamp": "2025-11-05T10:00:00Z",
  "validation_gates": {
    "gate_1_rule_completeness": {
      "status": "PASSED",
      "percentage": 95,
      "components_in_phase1": 4,
      "components_with_rules": 4,
      "flows_in_phase2": 8,
      "flows_with_rules": 8,
      "missing_components": [],
      "missing_flows": [],
      "errors": [],
      "warnings": []
    },
    "gate_2_confidence_quality": {
      "status": "PASSED",
      "percentage": 78,
      "total_rules": 45,
      "high_confidence_rules": 35,
      "rules_without_reasoning": [],
      "critical_rules_low_confidence": [],
      "errors": [],
      "warnings": []
    },
    "gate_3_source_traceability": {
      "status": "PASSED",
      "percentage": 100,
      "total_rules": 45,
      "rules_with_valid_sources": 45,
      "rules_missing_sources": [],
      "invalid_source_locations": [],
      "errors": [],
      "warnings": []
    },
    "gate_4_categorization_completeness": {
      "status": "PASSED",
      "percentage": 100,
      "total_rules": 45,
      "rules_fully_categorized": 45,
      "rules_missing_type": [],
      "rules_missing_impact": [],
      "rules_missing_flow": [],
      "errors": [],
      "warnings": []
    },
    "gate_5_json_schema": {
      "status": "PASSED",
      "valid_json": true,
      "required_fields_present": true,
      "field_types_valid": true,
      "schema_errors": [],
      "errors": [],
      "warnings": []
    }
  },
  "overall_status": "COMPLETE",
  "overall_quality_score": 88.5,
  "recommendations": [
    "All validation gates passed",
    "Rule quality exceeds minimum thresholds",
    "Ready for Phase 4"
  ]
}
```

## Usage

### Running Validation

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/rule-validator/scripts/validate-ruletable.js \
  --phase3-dir results/NBM/phase3 \
  --phase1-dir results/NBM/phase1 \
  --phase2-dir results/NBM/phase2 \
  --output results/NBM/phase3/rule-quality-report.json \
  --feature NBM
```

**Parameters**:
- `--phase3-dir`: Directory containing ruletable.json
- `--phase1-dir`: Directory containing analysis.json (for component/function references)
- `--phase2-dir`: Directory containing PHASE2_SUMMARY.md and flow diagrams
- `--output`: Path for rule-quality-report.json output
- `--feature`: Feature name for reporting

**Exit Codes**:
- `0`: Validation passed (overall_status: COMPLETE, score ≥ 75)
- `1`: Validation failed (overall_status: INCOMPLETE, score < 75)
- `2`: Script error (invalid inputs, missing files)

### Generating Summary

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/rule-validator/scripts/generate-rule-summary.js \
  --input results/NBM/phase3/ruletable.json \
  --output results/NBM/phase3/PHASE3_SUMMARY.md
```

Generates human-readable markdown summary from ruletable.json.

## Automatic Iteration Pattern

When validation fails, Phase 3 command should iterate:

```markdown
1. Run validation
2. Check rule-quality-report.json status
3. If INCOMPLETE:
   - Gate 1 Failed: Extract rules for missing components/flows
   - Gate 2 Failed: Improve confidence scores with better reasoning
   - Gate 3 Failed: Add source locations for all rules
   - Gate 4 Failed: Complete categorization metadata
   - Gate 5 Failed: Fix JSON schema errors
   - Re-run validation
4. If COMPLETE: Proceed to summary generation
```

This mirrors Phase 2's successful automatic iteration pattern.

## Validation Details

### Gate 1: Rule Completeness

**Checks**:
1. Load Phase 1 analysis.json and count components
2. Load Phase 2 PHASE2_SUMMARY.md and count flows
3. For each component in Phase 1:
   - Check if any rule has source_location referencing this component
   - If missing: Add to missing_components list
4. For each flow in Phase 2:
   - Check if any rule has business_flow matching this flow name/KCODE
   - If missing: Add to missing_flows list
5. Calculate percentage: (components_with_rules + flows_with_rules) / (total_components + total_flows) * 100

**Pass Criteria**: Percentage ≥ 80%

**Why This Matters**: Ensures comprehensive rule extraction across all code and flows

### Gate 2: Confidence Quality

**Checks**:
1. For each rule in ruletable.json:
   - Count rules with confidence ≥ 4 (High/Very High)
   - Check if reasoning field is populated
   - If business_impact is "critical" and confidence < 4: Flag as warning
2. Calculate percentage: high_confidence_rules / total_rules * 100

**Pass Criteria**: Percentage ≥ 70%

**Why This Matters**: High confidence rules are more reliable for downstream phases

### Gate 3: Source Traceability

**Checks**:
1. For each rule:
   - Check source_location field is not empty/null/"Unknown"
   - If references Phase 1: Verify component/function exists in analysis.json
   - If references Phase 2: Verify .puml file exists
   - If references file:line: Check file exists
2. Calculate percentage: valid_sources / total_rules * 100

**Pass Criteria**: Percentage = 100%

**Why This Matters**: Traceability is essential for verification and maintenance

### Gate 4: Categorization Completeness

**Checks**:
1. For each rule:
   - Check type field is one of: validation/business_logic/integration/compliance
   - Check business_impact field is one of: critical/high/medium/low
   - If extracted from flow diagram: Check business_flow field references flow name
   - Check affected_components array has at least one component
2. Calculate percentage: fully_categorized / total_rules * 100

**Pass Criteria**: Percentage = 100%

**Why This Matters**: Proper categorization enables filtering and prioritization

### Gate 5: JSON Schema Validation

**Checks**:
1. Parse ruletable.json as valid JSON
2. Check required top-level fields: feature_name, phase, rules, summary
3. For each rule, check required fields:
   - rule_id (string, format BR-XXX)
   - description (string, non-empty)
   - type (string, valid enum)
   - confidence (number, 1-5)
   - reasoning (string, non-empty)
   - source_location (string, non-empty)
   - business_impact (string, valid enum)
4. Check field types match schema

**Pass Criteria**: All checks pass

**Why This Matters**: Valid schema ensures downstream phase compatibility

## Best Practices

1. **Run After Every Rule Extraction**: Validate immediately after writing ruletable.json
2. **Iterate on Failures**: Don't accept incomplete rule extraction - fix and re-validate
3. **Target High Confidence**: Aim for Gate 2 score ≥ 80% (not just 70% threshold)
4. **Complete Categorization**: Gate 4 must be 100% - no exceptions
5. **Leverage Phase 2**: Extract rules from all flow diagrams, not just Phase 1

## Progressive Disclosure

- **SKILL.md** (this file) - Validation framework overview and usage
- **[scripts/validate-ruletable.js](scripts/validate-ruletable.js)** - Full 5-gate validation implementation
- **[scripts/generate-rule-summary.js](scripts/generate-rule-summary.js)** - Summary markdown generator
- **[references/schema.json](references/schema.json)** - Complete ruletable.json JSON schema
- **[references/examples/](references/examples/)** - Example validation reports and summaries

**Load validate-ruletable.js when**: Need to see validation implementation details

**Load schema.json when**: Need to understand expected ruletable.json structure

**Load examples when**: Need to see what good validation reports look like

## Integration with Phase 3 Command

The Phase 3 command should:

1. **Load Inputs** (Phase A):
   - Read Phase 1 analysis.json
   - Read Phase 2 PHASE2_SUMMARY.md and flow diagrams

2. **Extract Rules** (Phase B-D):
   - Extract from Phase 1 components and functions
   - Extract from Phase 2 flow diagrams
   - Categorize and score

3. **Validate** (Phase F):
   ```markdown
   Run validation:
   - Execute validate-ruletable.js
   - Read rule-quality-report.json
   - Check overall_status

   If INCOMPLETE:
   - Review failed gates
   - Fix identified issues
   - Re-run validation
   - Repeat until COMPLETE

   If COMPLETE:
   - Proceed to summary generation
   ```

4. **Generate Summary** (Phase G):
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/rule-validator/scripts/generate-rule-summary.js
   ```

## Success Criteria

Phase 3 validation succeeds when:

- ✅ overall_status = "COMPLETE"
- ✅ overall_quality_score ≥ 75
- ✅ All 5 gates have status = "PASSED"
- ✅ No errors in validation report
- ✅ Warnings acknowledged (if any)

This ensures Phase 3 outputs are production-ready for Phase 4 (business logic analysis) and downstream phases.

---

**For complete validation logic, see [scripts/validate-ruletable.js](scripts/validate-ruletable.js)**

**For JSON schema specification, see [references/schema.json](references/schema.json)**
