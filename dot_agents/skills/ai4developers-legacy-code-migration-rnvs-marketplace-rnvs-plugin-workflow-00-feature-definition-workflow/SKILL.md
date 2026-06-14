---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-00-feature-definition-workflow
description: Defines feature scope for RNVS migration analysis. Creates feature-definition.json with keywords, components, and business context. Use at the start of any RNVS-to-VNRM migration project, before Phase 1 code analysis.
allowed-tools: Read, Write, AskUserQuestion, Bash
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/00-feature-definition-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Phase 0: Feature Definition Workflow

Define feature scope before RNVS code analysis. This is the critical first step that ensures clear boundaries for Phase 1-5.

---

## Progress Checklist

Copy and track your progress:

```
Phase 0 Progress:
- [ ] Step 1: Gather user requirements
- [ ] Step 2: Create feature definition draft
- [ ] Step 3: Validate with user
- [ ] Step 4: Finalize and write feature-definition.json
- [ ] (Auto) .workflow-state.md created by plugin hook
```

---

## Step 1: Gather User Requirements

**Objective**: Understand what the user wants to analyze.

Use AskUserQuestion (batch up to 4 questions):

1. **Feature/module** - What to analyze?
2. **Purpose** - Migration, documentation, or investigation?
3. **Components** - Specific packages, classes, or KCODEs?
4. **Processes** - Business workflows involved?

**RNVS Terminology to Listen For**:
- Features: NBM, FNPORT, RNB, TNB, PDA, FCM
- KCODEs: 20, 21, 22, 25, 26, 60, 61, 4100+
- Processes: assignment, porting, fusion, owner change
- German: Rufnummernblock, Eigentuemerwechsel, Portierung

---

## Step 2: Create Feature Definition Draft

**Objective**: Build comprehensive feature-definition.json.

**Source Priority** (anti-hallucination):
1. **User Input** - What user explicitly said (HIGHEST)
2. **Expert Skills** - Domain context from rnvs-expert-skills
3. **Mark Uncertain** - Flag anything unclear

**When to Consult Skills**:
- KCODE mentioned → `rnvs-expert-skills:porting-data-exchange-specialist`
- German terms → `rnvs-expert-skills:german-glossary`
- Error codes → `rnvs-expert-skills:rnvs-error-code-specialist`

**Feature Name**: 3-10 chars, UPPERCASE (e.g., NBM, FNPORT, PDA-EXPORT)

**Required Fields** - see [references/schema.json](references/schema.json):
- `feature_name`, `feature_full_name`, `feature_description`
- `analysis_purpose`: migration | documentation | bug-investigation | business-analysis
- `scope.included_components`, `scope.included_processes`, `scope.excluded_scope`
- `keywords.german_terms`, `keywords.english_terms`, `keywords.technical_terms`
- `sources.user_input`, `sources.skill_references`

---

## Step 3: Validate with User

**Objective**: Get user approval before finalizing.

Present the draft summary, then use AskUserQuestion:
- "Yes, proceed" - Definition is correct
- "Minor changes" - Small adjustments needed
- "Major rework" - Significant changes required

Highlight any `uncertainty_flags` for clarification.

**Max 3 iterations** - then confirm and proceed.

---

## Step 4: Finalize and Write

**Objective**: Write approved feature-definition.json.

1. Resolve all `uncertainty_flags`
2. Set `approved_by_user: true`
3. Set `timestamp` to current ISO 8601
4. Write to: `results/${FEATURE_NAME}/feature-definition.json`

**After writing**: A plugin hook automatically creates `.workflow-state.md`.

---

## Output Files

| File | Location | Created By |
|------|----------|------------|
| `feature-definition.json` | `results/${FEATURE}/` | This workflow (Step 4) |
| `.workflow-state.md` | `results/${FEATURE}/` | Plugin hook (automatic) |

---

## Anti-Hallucination Rules

Before writing, verify:
- `feature_description` based on user input, NOT invented
- `included_components` only user-mentioned or confirmed items
- `included_kcodes` only user-mentioned or skill-confirmed values
- `uncertainty_flags` contains ANY unclear areas
- `sources.user_input` accurately reflects what user said
- `sources.skill_references` lists ONLY skills actually consulted

**Do NOT**:
- Invent component names user never mentioned
- Add KCODEs based on assumption
- Expand scope beyond explicit request
- Claim certainty when uncertain

---

## Example

See [references/example-NBM-feature-definition.json](references/example-NBM-feature-definition.json) for complete example.

---

## Next Step

After Phase 0 completes:
```
/01-code-analysis-workflow ${FEATURE_NAME}
```

Phase 1 uses:
- `keywords` for Grep discovery
- `scope.included_components` for boundaries
- Feature name for results directory
