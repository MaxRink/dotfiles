# Output Schemas

JSON schema for Phase 5 Control Flow Visualization outputs.

---

## control-flow-mapping.json

```json
{
  "feature": "NBM",
  "phase": 5,
  "timestamp": "2025-12-19T14:00:00Z",
  "source_phase4": "results/NBM/phase4/business-process.json",
  "source_phase3": "results/NBM/phase3/ruletable.json",

  "diagram_plan": {
    "strategy": "master_plus_detailed",
    "total_diagrams": 3,
    "diagrams": [
      {
        "diagram_file": "control-flow-diagram-master.puml",
        "diagram_type": "master",
        "scope": "All NBM processes at high level",
        "processes_included": ["BP-NBM-001", "BP-NBM-002"],
        "node_count": 12
      },
      {
        "diagram_file": "control-flow-diagram-nbm-001.puml",
        "diagram_type": "detailed",
        "scope": "BP-NBM-001 Number Block Assignment",
        "processes_included": ["BP-NBM-001"],
        "node_count": 8,
        "swimlanes_count": 3,
        "decision_points_count": 2
      }
    ]
  },

  "business_processes": [
    {
      "process_id": "BP-NBM-001",
      "process_name": "Number Block Assignment from BNetzA",
      "diagram_file": "control-flow-diagram-nbm-001.puml",
      "flow_nodes": [
        {
          "node_id": "NBM-FLOW-001",
          "node_label": "Receive KCODE 20 Message",
          "node_type": "start",
          "stakeholder": "BNetzA Gateway",
          "source": "Phase 4 BP-NBM-001 Step 1"
        },
        {
          "node_id": "NBM-FLOW-002",
          "node_label": "Validate Operator in TNB",
          "node_type": "process",
          "stakeholder": "Number Resource Management",
          "rules_applied": ["NBM-BR-015"],
          "source": "Phase 4 BP-NBM-001 Step 2"
        }
      ],
      "decision_points": [
        {
          "decision_id": "NBM-DEC-001",
          "decision_label": "Operator Exists in TNB?",
          "source": "Phase 3 NBM-BR-015 validation rule",
          "true_path": "NBM-FLOW-003",
          "true_path_description": "Proceed with block assignment",
          "false_path": "NBM-FLOW-ERR-001",
          "false_path_description": "Reject - Invalid Operator"
        }
      ]
    }
  ],

  "technical_processes": [
    {
      "process_id": "TECH-NBM-001",
      "process_name": "KCODE 20 Message Processing",
      "source": "Phase 1 pack_body_rnb.sql, Phase 2 dependencies.puml",
      "components_involved": ["pack_body_rnb.sql", "RnbMessageParser.java"],
      "description": "Technical implementation of BNetzA message processing"
    }
  ],

  "stakeholder_interaction": {
    "swimlanes": [
      {
        "stakeholder_name": "BNetzA Gateway",
        "stakeholder_type": "External System",
        "source": "Phase 4 stakeholder_analysis",
        "activities": ["Send KCODE Message", "Receive Confirmation"],
        "interaction_nodes": ["NBM-FLOW-001", "NBM-FLOW-CONFIRM"]
      },
      {
        "stakeholder_name": "Number Resource Management",
        "stakeholder_type": "Business Owner",
        "source": "Phase 4 stakeholder_analysis",
        "activities": ["Validate Operator", "Assign Block", "Update Registry"],
        "interaction_nodes": ["NBM-FLOW-002", "NBM-FLOW-003", "NBM-FLOW-004"]
      }
    ],
    "total_stakeholders": 3
  },

  "other_system_interaction": {
    "external_systems": [
      {
        "system_name": "BNetzA Gateway",
        "system_type": "Regulatory Interface",
        "source": "Phase 2 dependencies.puml",
        "integration_protocol": "KCODE Message Format",
        "interaction_points": [
          {
            "flow_node": "NBM-FLOW-001",
            "interaction_type": "receive",
            "description": "Receive KCODE 20 assignment message"
          }
        ]
      }
    ],
    "total_external_systems": 1
  },

  "summary": {
    "total_business_processes": 2,
    "total_flow_nodes": 8,
    "total_decision_points": 2,
    "total_stakeholders": 3,
    "total_external_systems": 1,
    "total_diagrams_created": 3,
    "user_validation_completed": true,
    "rework_iterations": 0
  },

  "user_validation": {
    "validation_completed": true,
    "validation_date": "2025-12-19T14:30:00Z",
    "user_approval_status": "Approved",
    "user_comments": ["Flow accurately represents KCODE processing"]
  }
}
```

---

## PHASE5_SUMMARY.md Template

```markdown
# Phase 5: Control Flow Visualization Summary

**Feature**: ${FEATURE}
**Generated**: ${DATE}
**Status**: User Validated and Approved

## Summary Statistics

- **Business Processes Visualized**: ${COUNT}
- **Flow Diagrams Created**: ${COUNT}
- **Total Flow Nodes**: ${COUNT}
- **Total Decision Points**: ${COUNT}
- **Stakeholder Swimlanes**: ${COUNT}
- **External System Integrations**: ${COUNT}

## Diagrams Created

### 1. Master Diagram
**File**: control-flow-diagram-master.puml
**Scope**: High-level overview of all processes

### 2. Detailed Diagrams
- control-flow-diagram-nbm-001.puml: Number Block Assignment
- control-flow-diagram-nbm-002.puml: Block Modification

## Source Traceability

- **Flow Nodes**: 100% traced to Phase 4
- **Decision Points**: 100% backed by Phase 3
- **Stakeholders**: 100% from Phase 4

## Next Steps

1. **Phase 6**: Use for VNRM microservice design
2. **Gap Analysis**: Any identified gaps for Phase 8

---

**Ready for Phase 6**: Microservice Architecture Design
```

---

## Validation Checklist

Before finalizing outputs:

- [ ] All diagram files created and syntax validated
- [ ] control-flow-mapping.json has all required sections
- [ ] All flow nodes have source citations
- [ ] All decision points backed by Phase 3 rules
- [ ] Node count ≤15 per diagram documented
- [ ] User validation completed
