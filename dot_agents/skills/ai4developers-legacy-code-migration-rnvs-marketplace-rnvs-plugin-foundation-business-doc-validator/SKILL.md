---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-business-doc-validator
description: Comprehensive validation framework for Phase 4 business documentation with 5-gate quality system. Use when validating business-documentation.json outputs, ensuring documentation completeness, or assessing business documentation quality in the RNVS-VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/business-doc-validator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Business Documentation Validator Skill

## Purpose

Provides a comprehensive 5-gate validation framework for Phase 4 business documentation outputs. Ensures documentation completeness, terminology consistency, stakeholder coverage, process quality, and JSON schema compliance with automatic quality scoring.

## When to Use

- **Phase 4 Validation**: Validate business-documentation.json after business documentation generation
- **Quality Assurance**: Check documentation completeness against Phase 1, 2, and 3 inputs
- **Automatic Iteration**: Identify validation failures to trigger documentation improvements
- **Production Readiness**: Verify business documentation meets quality thresholds before Phase 5

## Validation Framework

### 5-Gate Validation System

Phase 4 uses a multi-gate validation system similar to Phase 2 and Phase 3:

**Gate 1: Documentation Completeness** (Threshold: ≥80%)
- All required sections present (overview, business_rules_enhanced, business_processes, etc.)
- All Phase 3 rules have business objectives documented
- All Phase 2 flows have process documentation
- Glossary consolidates terms from all phases
- Metric: Percentage of expected documentation complete

**Gate 2: Terminology Consistency** (Threshold: ≥90%)
- German terms in glossary match Phase 3 ruletable
- No conflicting translations between glossary entries
- All key terms defined with proper business definitions
- Terminology usage consistent across documentation
- Metric: Percentage of terminology consistency

**Gate 3: Stakeholder Coverage** (Threshold: ≥70%)
- Critical rules have business owners assigned
- Department responsibilities documented
- Communication channels defined
- Escalation paths identified
- Metric: Percentage of stakeholder assignments

**Gate 4: Process Quality** (Threshold: ≥75%)
- All Phase 2 flows documented as business processes
- Process steps clearly defined in business language
- Decision criteria explained with business rationale
- Exception scenarios documented
- Rules mapped to processes
- Metric: Percentage of process quality

**Gate 5: JSON Schema Validation** (Threshold: 100%)
- business-documentation.json is valid JSON
- All required fields present (feature_name, overview, business_rules_enhanced, etc.)
- Field types match schema (arrays are arrays, strings are strings)
- No malformed or invalid data
- Metric: Pass/Fail

### Quality Score Calculation

```
Overall Quality Score = (
  Gate1_percentage * 0.25 +   (25% weight - completeness critical)
  Gate2_percentage * 0.20 +   (20% weight - terminology consistency)
  Gate3_percentage * 0.20 +   (20% weight - stakeholder coverage)
  Gate4_percentage * 0.25 +   (25% weight - process quality most important)
  Gate5_pass * 10              (10 points if passed, 0 if failed)
)

Where:
- Gate1-4: Percentage values (0-100)
- Gate5: 1 if passed, 0 if failed
- Final score: 0-100
```

**Threshold for COMPLETE Status**: Overall quality score ≥ 75

### Validation Output

The validator generates `doc-quality-report.json`:

```json
{
  "feature": "NBM",
  "phase": 4,
  "timestamp": "2025-11-05T10:00:00Z",
  "validation_gates": {
    "gate_1_documentation_completeness": {
      "status": "PASSED",
      "percentage": 95,
      "details": "7/7 sections present, 61/61 rules with objectives, 8/8 flows documented",
      "errors": [],
      "warnings": []
    },
    "gate_2_terminology_consistency": {
      "status": "PASSED",
      "percentage": 92,
      "details": "38/40 Phase 3 terms in glossary, 0 conflicts, 40/40 terms with definitions",
      "errors": [],
      "warnings": ["Phase 3 terms missing from glossary: Portierungskennung, Datenaustausch"]
    },
    "gate_3_stakeholder_coverage": {
      "status": "PASSED",
      "percentage": 85,
      "details": "36/36 critical rules with owners, 4 departments, 8 responsibilities, 3 communication channels",
      "errors": [],
      "warnings": []
    },
    "gate_4_process_quality": {
      "status": "PASSED",
      "percentage": 88,
      "details": "8 processes: 8 with good steps, 8 with decision criteria, 7 with exceptions, 8 with rules",
      "errors": [],
      "warnings": []
    },
    "gate_5_schema_validation": {
      "status": "PASSED",
      "valid_json": true,
      "required_fields_present": true,
      "field_types_valid": true,
      "details": "Valid JSON schema",
      "schema_errors": [],
      "errors": [],
      "warnings": []
    }
  },
  "overall_status": "COMPLETE",
  "overall_quality_score": 89.5,
  "recommendations": [
    "All validation gates passed",
    "Documentation quality exceeds minimum thresholds (89.5/100)",
    "Ready for Phase 5"
  ]
}
```

## Usage

### Running Validation

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/business-doc-validator/scripts/validate-business-doc.js \
  --phase4-dir results/NBM/phase4 \
  --phase3-dir results/NBM/phase3 \
  --phase2-dir results/NBM/phase2 \
  --phase1-dir results/NBM/phase1 \
  --output results/NBM/phase4/doc-quality-report.json \
  --feature NBM
```

**Parameters**:
- `--phase4-dir`: Directory containing business-documentation.json
- `--phase3-dir`: Directory containing ruletable.json (for rule comparison)
- `--phase2-dir`: Directory containing PHASE2_SUMMARY.md (for flow references)
- `--phase1-dir`: Directory containing analysis.json (for component references)
- `--output`: Path for doc-quality-report.json output
- `--feature`: Feature name for reporting

**Exit Codes**:
- `0`: Validation passed (overall_status: COMPLETE, score ≥ 75)
- `1`: Validation failed (overall_status: INCOMPLETE, score < 75)
- `2`: Script error (invalid inputs, missing files)

### Generating Summary

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/business-doc-validator/scripts/generate-business-summary.js \
  --input results/NBM/phase4/business-documentation.json \
  --output results/NBM/phase4/PHASE4_SUMMARY.md
```

Generates human-readable markdown summary from business-documentation.json.

## Automatic Iteration Pattern

When validation fails, Phase 4 command should iterate:

```markdown
1. Run validation
2. Check doc-quality-report.json status
3. If INCOMPLETE:
   - Gate 1 Failed: Add missing sections, document business objectives for all rules
   - Gate 2 Failed: Add missing Phase 3 terms to glossary, resolve conflicts
   - Gate 3 Failed: Assign business owners to critical rules, add department responsibilities
   - Gate 4 Failed: Enhance process steps, add decision criteria and exceptions
   - Gate 5 Failed: Fix JSON schema errors, ensure all required fields present
   - Re-run validation
4. If COMPLETE: Proceed to summary generation
```

This mirrors Phase 2 and Phase 3's successful automatic iteration pattern.

## Validation Details

### Gate 1: Documentation Completeness

**Checks**:
1. **Required Sections** (30 points):
   - overview, business_rules_enhanced, business_processes
   - stakeholder_analysis, impact_analysis, glossary, recommendations
2. **Business Objectives for All Rules** (40 points):
   - Load Phase 3 ruletable.json
   - For each rule, check if business-documentation.json has:
     - business_objective (min 20 chars)
     - business_owner (min 3 chars)
     - customer_impact (min 20 chars)
3. **Process Documentation for All Flows** (30 points):
   - Load Phase 2 PHASE2_SUMMARY.md
   - For each flow, check if business_processes has matching entry

**Pass Criteria**: Percentage ≥ 80%

**Why This Matters**: Ensures comprehensive documentation of all business aspects

### Gate 2: Terminology Consistency

**Checks**:
1. **Phase 3 Terms in Glossary** (50 points):
   - Extract all german_terms from Phase 3 ruletable.json
   - Check each term exists in glossary with definition
2. **No Translation Conflicts** (25 points):
   - Build map of german_term → english_term
   - Flag any german term with multiple english translations
3. **Proper Definitions** (25 points):
   - Check each glossary entry has definition ≥ 20 chars
   - Check definition provides business context

**Pass Criteria**: Percentage ≥ 90%

**Why This Matters**: Consistent terminology prevents confusion in downstream phases

### Gate 3: Stakeholder Coverage

**Checks**:
1. **Critical Rules Have Owners** (60 points):
   - Load Phase 3 ruletable.json
   - Filter rules with business_impact = "critical"
   - Check each critical rule has business_owner in business-documentation.json
2. **Stakeholder Analysis Complete** (25 points):
   - Check departments array has ≥ 2 entries
   - Check responsibilities array has ≥ 2 entries
3. **Communication Channels** (15 points):
   - Check communication_channels array has ≥ 1 entry

**Pass Criteria**: Percentage ≥ 70%

**Why This Matters**: Clear ownership ensures accountability during migration

### Gate 4: Process Quality

**Checks**:
1. **Good Process Steps** (40 points):
   - For each business_processes entry:
     - Check process_steps has ≥ 3 steps
     - Check each step is ≥ 15 chars (meaningful description)
2. **Decision Criteria Documented** (30 points):
   - Check decision_criteria array has ≥ 1 entry with decision, criteria, outcomes
3. **Exception Scenarios** (20 points):
   - Check exception_scenarios array has ≥ 1 entry
4. **Rules Referenced** (10 points):
   - Check rules_applied array has ≥ 1 rule ID

**Pass Criteria**: Percentage ≥ 75%

**Why This Matters**: High-quality process documentation critical for migration planning

### Gate 5: JSON Schema Validation

**Checks**:
1. **Valid JSON**: Already validated in loadBusinessDoc()
2. **Required Top-Level Fields**:
   - feature_name, feature_full_name, phase, timestamp
   - inputs, overview, business_rules_enhanced, business_processes
   - stakeholder_analysis, impact_analysis, glossary, recommendations
   - validation_report
3. **Field Type Validation**:
   - feature_name is string
   - phase is number = 4
   - business_rules_enhanced is array
   - business_processes is array
   - glossary is array

**Pass Criteria**: All checks pass

**Why This Matters**: Valid schema ensures downstream phase compatibility

## Best Practices

1. **Run After Every Documentation Generation**: Validate immediately after writing business-documentation.json
2. **Iterate on Failures**: Don't accept incomplete documentation - fix and re-validate
3. **Target High Scores**: Aim for Gate 1-4 scores ≥ 85% (not just threshold)
4. **Complete All Gates**: Gate 5 must pass - no exceptions
5. **Leverage Phase 3**: Use ruletable.json as source of truth for rules

## Progressive Disclosure

- **SKILL.md** (this file) - Validation framework overview and usage
- **[scripts/validate-business-doc.js](scripts/validate-business-doc.js)** - Full 5-gate validation implementation
- **[scripts/generate-business-summary.js](scripts/generate-business-summary.js)** - Summary markdown generator
- **[references/schema.json](references/schema.json)** - Complete business-documentation.json JSON schema

**Load validate-business-doc.js when**: Need to see validation implementation details

**Load schema.json when**: Need to understand expected business-documentation.json structure

## Integration with Phase 4 Command

The Phase 4 command should:

1. **Load Inputs** (Phase A):
   - Read Phase 1 analysis.json
   - Read Phase 2 PHASE2_SUMMARY.md and flow diagrams
   - Read Phase 3 ruletable.json (primary input - don't re-extract rules!)

2. **Check Wiki/Confluence Availability** (Phase B):
   - Use ListMcpResourcesTool to check if Wiki/Confluence MCP configured
   - If available: Query for business context
   - If NOT available: Generate from Phase 1+2+3 only (graceful fallback)

3. **Consolidate Glossary** (Phase C):
   - Extract all german_terms from Phase 3 ruletable.json
   - Extract additional terms from Phase 2 flow diagrams
   - Consolidate and enhance with business definitions

4. **Document Business Processes** (Phase D):
   - For each Phase 2 flow diagram:
     - Create business_processes entry
     - Document process steps in business language
     - Add decision criteria and exceptions
     - Map rules from Phase 3 to this process

5. **Enhance Rules with Business Context** (Phase E):
   - For each Phase 3 rule:
     - Add business_objective (WHY does this rule exist?)
     - Add business_owner (WHO owns this?)
     - Add customer_impact (HOW does it affect users?)
     - If Wiki/Confluence available: Map to business use case

6. **Create Stakeholder and Impact Analysis** (Phase F):
   - Document departments and responsibilities
   - Analyze customer, operational, regulatory, financial impact
   - Identify risks and mitigation strategies

7. **Validate** (Phase G):
   ```markdown
   Run validation:
   - Execute validate-business-doc.js
   - Read doc-quality-report.json
   - Check overall_status

   If INCOMPLETE:
   - Review failed gates
   - Fix identified issues
   - Re-run validation
   - Repeat until COMPLETE (max 3 iterations)

   If COMPLETE:
   - Proceed to summary generation
   ```

8. **Generate Summary** (Phase H):
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/business-doc-validator/scripts/generate-business-summary.js
   ```

## Success Criteria

Phase 4 validation succeeds when:

- ✅ overall_status = "COMPLETE"
- ✅ overall_quality_score ≥ 75
- ✅ All 5 gates have status = "PASSED"
- ✅ No errors in validation report
- ✅ Warnings acknowledged (if any)

This ensures Phase 4 outputs are production-ready for Phase 5 (Control Flow Mapping) and downstream phases.

## Comparison to Phase 3 Pattern

| Aspect | Phase 3 (Rules) | Phase 4 (Business Doc) | Similarity |
|--------|-----------------|------------------------|------------|
| **Validation Framework** | 5-gate system | 5-gate system | ✅ Same |
| **Quality Scoring** | 0-100 weighted | 0-100 weighted | ✅ Same |
| **Automatic Iteration** | Max 3 iterations | Max 3 iterations | ✅ Same |
| **PostToolUse Hook** | JSON schema validator | JSON schema validator | ✅ Same |
| **Technology Stack** | Node.js | Node.js | ✅ Same |
| **Threshold** | ≥75 for COMPLETE | ≥75 for COMPLETE | ✅ Same |
| **Input Source** | Phase 1+2 | Phase 1+2+3 | Progressive |
| **Output Format** | JSON + Markdown | JSON + Markdown | ✅ Same |

Phase 4 follows the proven success pattern from Phase 3 while building on its outputs.

---

**For complete validation logic, see [scripts/validate-business-doc.js](scripts/validate-business-doc.js)**

**For JSON schema specification, see [references/schema.json](references/schema.json)**
