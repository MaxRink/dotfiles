# Anti-Hallucination Checklist

Before finalizing business-documentation.json and business-process.json.

---

## Core Principle

**ENHANCE, Do Not Invent**: Phase 4 builds on Phase 3 - it does NOT create new rules or modify technical fields.

---

## Pre-Finalization Checklist

### Phase 3 Preservation
- [ ] All Phase 3 rule_id values present unchanged
- [ ] All Phase 3 source_location values preserved
- [ ] All Phase 3 confidence_score values preserved
- [ ] All Phase 3 validation_status values preserved

### Enhancement Sources
- [ ] Every business_objective cites enhancement_sources
- [ ] Every stakeholder_owner has derivation_source
- [ ] Every regulatory_rationale cites source (skill or user feedback)
- [ ] If uncertain, marked "Requires stakeholder clarification"

---

## Red Flags (DO NOT DO)

| Action | Why It's Wrong |
|--------|----------------|
| Re-extracting rules from code | Use Phase 3 ruletable.json only |
| Modifying Phase 3 technical fields | Technical fields are read-only |
| Inventing business objectives | No source evidence |
| Guessing stakeholders | No derivation logic |
| Adding regulations without skill citation | Unsupported compliance claims |

---

## When Uncertain

1. **Do NOT invent** - Never add content without source
2. **Mark as uncertain**: "Requires stakeholder clarification"
3. **Present in validation**: Ask user in Step 6
