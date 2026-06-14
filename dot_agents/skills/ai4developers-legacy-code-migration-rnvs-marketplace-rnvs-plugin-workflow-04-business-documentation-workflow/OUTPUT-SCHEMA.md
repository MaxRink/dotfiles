# Output Schemas

JSON schemas for Phase 4 Business Documentation outputs.

---

## business-documentation.json

```json
{
  "feature_name": "NBM",
  "phase": 4,
  "created_timestamp": "2025-12-19T14:30:00Z",
  "phase3_source": "results/NBM/phase3/ruletable.json",

  "business_rules_enhanced": [
    {
      "// Phase 3 fields (preserved unchanged)": "",
      "rule_id": "NBM-BR-015",
      "rule_name": "Operator Validation Before RNB Assignment",
      "rule_description": "Operator must exist in TNB table before number block assignment",
      "source_location": "pack_body_rnb.sql:234",
      "confidence_score": 5,
      "validation_status": "user_confirmed",

      "// Phase 4 enhancement fields": "",
      "business_objective": "Prevent invalid number block assignments to non-existent operators",
      "business_process": "BP-NBM-001",
      "business_terminology": "Before assigning a block of phone numbers to a telecommunications operator, the system verifies the operator is registered in the national operator database",
      "stakeholder_owner": {
        "department": "Number Resource Management",
        "role": "Number Management Team Lead",
        "derivation_source": "Rule prefix: NBM"
      },
      "regulatory_rationale": {
        "regulations": [{"regulation": "BNetzA Number Administration", "requirement": "Valid operator registration"}],
        "compliance_status": "Implemented"
      },
      "enhancement_sources": [
        "porting-data-exchange-specialist: KCODE 20 validation requirements",
        "Rule category: number_block → Number Resource Management"
      ]
    }
  ],

  "glossary": [
    {
      "term": "Rufnummernblock",
      "definition": "Number Block - contiguous range of telephone numbers assigned to an operator",
      "german_equivalent": "Rufnummernblock",
      "source": "german-glossary"
    }
  ],

  "stakeholder_analysis": {
    "business_owners": [
      {
        "stakeholder_id": "STK-001",
        "name": "Number Resource Management",
        "type": "business_owner",
        "responsibilities": ["Number block allocation", "Operator verification"],
        "rules_owned": ["NBM-BR-015", "NBM-BR-016"],
        "derivation_source": "Rule prefix: NBM"
      }
    ],
    "technical_owners": [],
    "regulatory_authorities": [
      {
        "stakeholder_id": "STK-002",
        "name": "BNetzA",
        "type": "regulatory_authority",
        "responsibilities": ["Number resource oversight", "Operator licensing"],
        "derivation_source": "porting-data-exchange-specialist"
      }
    ],
    "end_users": []
  },

  "summary": {
    "total_rules_enhanced": 15,
    "enhancement_coverage": {
      "business_objective": 15,
      "stakeholder_owner": 15,
      "regulatory_rationale": 8
    },
    "specialist_skills_consulted": ["porting-data-exchange-specialist", "german-glossary"]
  },

  "validation_report": {
    "user_validation_completed": true,
    "rework_iterations": 1,
    "final_approval_date": "2025-12-19T15:45:00Z"
  }
}
```

---

## business-process.json

```json
{
  "feature_name": "NBM",
  "phase": 4,
  "created_timestamp": "2025-12-19T14:30:00Z",

  "business_processes": [
    {
      "process_id": "BP-NBM-001",
      "process_name": "Number Block Assignment from BNetzA",
      "process_description": "Process for receiving and validating new number block assignments from regulatory authority",
      "business_objective": "Ensure compliant number block assignments to licensed operators",
      "trigger": "KCODE 20 message received from BNetzA",
      "process_steps": [
        {
          "step_number": 1,
          "step_name": "KCODE Message Reception",
          "description": "System receives KCODE 20 assignment message from BNetzA gateway",
          "rules_applied": ["NBM-BR-010"],
          "stakeholder": "BNetzA Gateway Integration"
        },
        {
          "step_number": 2,
          "step_name": "Operator Validation",
          "description": "Verify operator exists in TNB registry",
          "rules_applied": ["NBM-BR-015"],
          "stakeholder": "Number Resource Management"
        },
        {
          "step_number": 3,
          "step_name": "Block Range Validation",
          "description": "Verify number range is valid and not already assigned",
          "rules_applied": ["NBM-BR-016", "NBM-BR-017"],
          "stakeholder": "Number Resource Management"
        }
      ],
      "stakeholders": ["BNetzA", "Number Resource Management", "RNVS RNB Team"],
      "source_rule_groups": ["NBM-ASSIGNMENT"],
      "validation_status": "user_confirmed"
    }
  ],

  "process_flow_sequence": [
    {
      "process_id": "BP-NBM-001",
      "follows": null,
      "precedes": ["BP-NBM-002"],
      "trigger": "KCODE 20 message"
    }
  ],

  "summary": {
    "total_processes": 3,
    "total_process_steps": 12,
    "stakeholders_involved": ["BNetzA", "Number Resource Management", "Operators"]
  }
}
```

---

## Validation Checklist Before Output

- [ ] All Phase 3 technical fields preserved unchanged
- [ ] All rules have business_objective field
- [ ] All rules have stakeholder_owner with derivation_source
- [ ] All rules have enhancement_sources field
- [ ] Business processes have process_steps array
- [ ] Stakeholder analysis complete
