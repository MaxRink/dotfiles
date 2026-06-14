---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-04-business-documentation-workflow
description: Transform technical analysis (Phases 1-3) into comprehensive business documentation consumable by stakeholders, migration planners, and downstream phases. This skill should be used for Phase 4 after Phases 1-3 completion. ENHANCES existing Phase 3 ruletable.json with business context using rnvs-expert-skills (does NOT re-extract rules). Includes interactive user validation workflow with grouped presentation and iterative rework capability. Outputs business-documentation.json (business_rules_enhanced, business_processes, glossary, stakeholder_analysis) and business-process.json with logical grouping for non-technical presentation.
allowed-tools: Read, Glob, Write, Skill, AskUserQuestion
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/04-business-documentation-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode, completed phases, and session context.
</required_reading>

# Phase 4: Business Documentation Workflow

**Purpose**: Transform technical Phase 3 business rules into stakeholder-consumable business documentation with enhanced context, logical grouping, and business objectives.

**When to use**: After Phase 3 (Business Rule Extraction) is complete, with ruletable.json validated and available.

---

## Prerequisites (Execute First)

<prerequisites>
**Feature Identification** - check in order, stop at first match:

1. **User provided feature name** (e.g., "/04-business-documentation-workflow NBM") → use directly
2. **Conversation context** → use feature from earlier in session
3. **Single feature in results/** → `Glob results/*/feature-definition.json` - if exactly one, use it
4. **Multiple features** → use AskUserQuestion to let user select
5. **No features** → "Run /00-feature-definition-workflow first"

**Verify Phase 3 output exists**:
- `results/${FEATURE}/phase3/ruletable.json`

If missing → "Complete /03-business-rule-extraction-workflow first."
</prerequisites>

---

## Step 0: Load Workflow State

Read `results/${FEATURE}/.workflow-state.md` and verify:

1. **Phase Check**: Phase 3 must be ✅ Complete
2. **Status**: Should be "In Progress"

If state file missing: "Run /00-feature-definition-workflow first to initialize workflow state."

**Update state**: Set Phase 4 to 🔄 In Progress, update Last Activity.

---

## Workflow Steps

1. **Load Phase 3 results** → ruletable.json (PRIMARY), optionally Phase 2 dependencies.puml
2. **Enrich rules with business context**:
   - Add `business_objective` (WHY this rule exists)
   - Add `stakeholder_owner` (department/role responsible)
   - Add `business_terminology` (non-technical description)
   - Add `regulatory_rationale` (BNetzA/compliance context)
   - Consult RNVS-expert-skills for enrichment (see [RNVS-ENRICHMENT.md](RNVS-ENRICHMENT.md))
3. **Group rules by business process** → organize for non-technical presentation
4. **Perform stakeholder analysis** → derive from rule categories, Phase 2 flows, specialist skills
5. **Create business process dependency map** → sequence and relationships
6. **Present to user** → grouped by business process for validation
7. **Rework if needed** → incorporate feedback (max 3 cycles)
8. **Finalize outputs** → business-documentation.json, business-process.json

---

## Key Principle: ENHANCE, Do Not Re-Extract

**CRITICAL**: Phase 4 builds on Phase 3 ruletable.json - DO NOT re-extract rules from code.

**What to ADD** (new fields):
- `business_objective`: WHY this rule exists (business value, regulatory compliance)
- `business_process`: Which business workflow uses this rule
- `stakeholder_owner`: Department/role responsible for this rule
- `business_terminology`: Non-technical description for stakeholders
- `regulatory_rationale`: BNetzA/GDPR/PDA compliance context
- `enhancement_sources`: Where business context came from

**What to PRESERVE** from Phase 3:
- All technical fields (rule_id, source_location, confidence_score, etc.)
- Source accountability (file:line citations)
- Validation status (user_confirmed, etc.)

---

## RNVS-Specific Enrichment

Consult specialist skills based on rule content:

| Rule Contains | Consult Skill | For |
|--------------|---------------|-----|
| PDA, Portierung, KCODE, porting | porting-data-exchange-specialist | Business workflow, BNetzA compliance |
| ECRM, PFM, RNBFM, BFM error codes | rnvs-error-code-specialist | Error business impact, recovery |
| German terms (Rufnummer, Eigentuemer) | german-glossary | Translation, business context |

For detailed patterns, see [RNVS-ENRICHMENT.md](RNVS-ENRICHMENT.md).

---

## Source Priority Hierarchy

**Priority 1**: Phase 3 ruletable.json (PRIMARY)
**Priority 2**: RNVS Code Comments (SUPPLEMENTARY)
**Priority 3**: RNVS-expert-skills (ENRICHMENT)

**NOT ALLOWED**: All business context must be backed by sources. No speculation.

---

## Output Files

- `results/${FEATURE}/phase4/business-documentation.json` - Enhanced rules with business context
- `results/${FEATURE}/phase4/business-process.json` - Business process definitions
- `results/${FEATURE}/phase4/PHASE4_SUMMARY.md` - Summary report

For schemas, see [OUTPUT-SCHEMA.md](OUTPUT-SCHEMA.md).

---

## Anti-Hallucination Checklist

Before finalizing:

- Every `business_objective` cites enhancement_sources
- Every `stakeholder_owner` has derivation source (rule category, Phase 2, specialist skill)
- Every `regulatory_rationale` cites specific regulation from specialist skill
- All Phase 3 technical fields preserved unchanged
- If business context uncertain, mark as "Requires stakeholder clarification"

**Red Flags** (DO NOT DO):
- Re-extracting rules from code (use Phase 3 only)
- Inventing business objectives without specialist skill evidence
- Modifying Phase 3 technical fields (confidence_score, source_location)

For complete checklist, see [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md).

---

## Phase Integration

**From Phase 3 (PRIMARY Input)**:
- `ruletable.json` → Validated technical rules (ENHANCE these)

**From Phase 2 (Optional)**:
- `dependencies.puml` → Flow diagrams for stakeholder identification

**To Phase 5 (Output)**:
- `business-documentation.json` → Business rules with objectives and stakeholders
- `business-process.json` → Process flows with business context

---

## Success Criteria

Phase 4 succeeds when:

1. business-documentation.json exists with all Phase 3 rules enhanced
2. Every enhanced rule has business_objective, stakeholder_owner, business_terminology
3. All Phase 3 technical fields preserved unchanged
4. Enhancement sources documented for every added field
5. Business processes grouped in logical flow for non-technical presentation
6. Stakeholder analysis identifies business owners, technical owners, regulatory authorities
7. User has validated business processes and documentation
8. Ready to proceed to Phase 5

---

## Final Step: Update Workflow State

After user validates business documentation, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 4**: Set to ✅ Complete with timestamp
2. **Last Activity**: "Completed Phase 4 business documentation"
3. **Next Action**: "Run /05-control-flow-visualization-workflow ${FEATURE}"
4. **Decisions Log**: Add any business process grouping decisions

---

## Quick Reference

| Document | Purpose |
|----------|---------|
| [RNVS-ENRICHMENT.md](RNVS-ENRICHMENT.md) | RNVS-specific skill triggers and enrichment patterns |
| [OUTPUT-SCHEMA.md](OUTPUT-SCHEMA.md) | Complete JSON schemas for outputs |
| [ANTI-HALLUCINATION.md](ANTI-HALLUCINATION.md) | Source verification checklist |
| [references/](references/) | Example business-documentation.json |

---

**Remember**: Phase 4 transforms technical analysis into business-consumable documentation. ENHANCE Phase 3 rules with business WHY using rnvs-expert-skills. Group by business process flow for stakeholder presentation. All business context must be backed by sources - no speculation.
