# Output Schema: ruletable.json

**File Location**: `results/${FEATURE}/phase3/ruletable.json`

---

## Complete Schema

```json
{
  "feature": "NBM",
  "extraction_timestamp": "2025-12-16T14:30:00Z",
  "phase1_source": "results/NBM/phase1/file-inventory.json",
  "phase2_sources": [
    "results/NBM/phase2/dependencies.puml",
    "results/NBM/phase2/dependencies_detailed.puml"
  ],
  "specialist_skills_consulted": [
    "rnvs-error-code-specialist: RNBFM002 context",
    "porting-data-exchange-specialist: KCODE timing rules"
  ],

  "rules": [
    {
      "rule_id": "NBM-BR-001",
      "rule_name": "Operator Validation Before RNB Assignment",
      "rule_description": "Operator must exist in TNB table before number block assignment",
      "rule_category": "validation",
      "business_process": "Number Block Management",
      "source_location": "pack_body_rnb.sql:234",
      "source_type": "source_code",
      "source_evidence": "IF p_tnb.get_operator(v_tnb_id) IS NULL THEN RAISE RNBFM002",
      "confidence_score": 5,
      "confidence_rationale": "Explicit code with error code confirms rule",
      "business_impact": "Prevents number block assignment to invalid operators",
      "regulatory_context": "BNetzA operator registration requirement",
      "error_code": "RNBFM002",
      "related_rules": ["NBM-BR-002"],
      "migration_priority": "high",
      "validation_status": "user_confirmed",
      "user_feedback": "Confirmed accurate"
    }
  ],

  "rule_groups": [
    {
      "group_id": "NBM-VALIDATION",
      "group_name": "Number Block Validation Rules",
      "group_description": "Rules governing validation before number block operations",
      "business_process": "Number Block Management",
      "rules": ["NBM-BR-001", "NBM-BR-002"],
      "total_rules": 2,
      "validation_status": "user_confirmed"
    }
  ],

  "summary": {
    "total_rules": 15,
    "rules_by_category": {
      "validation": 8,
      "security": 4,
      "integration": 3
    },
    "rules_by_confidence": {
      "5": 10,
      "4": 3,
      "3": 2
    },
    "rules_by_source_type": {
      "source_code": 12,
      "code_comment": 2,
      "user_confirmed": 1
    }
  },

  "validation_report": {
    "user_validation_completed": true,
    "total_groups_validated": 5,
    "rework_iterations": 1,
    "final_approval_date": "2025-12-16T15:45:00Z",
    "outstanding_questions": []
  }
}
```

---

## Required Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| rule_id | string | Unique identifier (PREFIX-BR-NNN) |
| rule_name | string | Human-readable rule name |
| rule_description | string | Full description of rule behavior |
| source_location | string | file:line or diagram:section |
| source_type | string | source_code, code_comment, user_confirmed |
| source_evidence | string | Quoted code or paraphrase |
| confidence_score | integer | 1-5 based on evidence clarity |
| validation_status | string | user_confirmed, pending_review, requires_clarification |
