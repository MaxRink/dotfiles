# Anti-Hallucination Checklist

Before finalizing control-flow-mapping.json and diagrams.

---

## Core Principle

**Source-Backed Only**: Every flow element must trace to Phase 1-4 artifacts or explicit user feedback.

---

## Pre-Finalization Checklist

### Flow Nodes
- [ ] Every business flow node cited to Phase 4 business-process.json (process_id, step_number)
- [ ] Every technical flow node cited to Phase 1 file-inventory.json (file_path, method)

### Decision Points
- [ ] Every decision point backed by Phase 3 conditional rule (rule_id)

### Stakeholders
- [ ] Every swimlane from Phase 4 stakeholder_analysis
- [ ] User corrections documented with "User feedback" source

### External Systems
- [ ] Every external system from Phase 2 dependencies.puml or Phase 1 dependency-graph.json

### Node Counts
- [ ] All diagrams ≤15 nodes
- [ ] Sub-diagrams created and referenced if exceeded

---

## Red Flags (DO NOT DO)

| Action | Why It's Wrong |
|--------|----------------|
| Adding process steps not in Phase 4 | Inventing functionality |
| Inventing decision conditions without Phase 3 rules | No source evidence |
| Creating swimlanes for undocumented stakeholders | Speculation |
| Adding external systems not in Phase 2/Phase 1 | Unsupported integration |
| Exceeding 15-node limit without sub-diagrams | Violates readability rules |

---

## When Uncertain

1. **Do NOT invent** - Never add content without source
2. **Mark as gap** - "Requires stakeholder clarification"
3. **Ask user** - Present ambiguity in validation step
4. **Document** - Add to recommendations for Phase 8 gap analysis
