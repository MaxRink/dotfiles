---
name: ai4dev-telecontext-psa
description: >-
  Look up Privacy and Security Assessment (PSA) requirements from Deutsche Telekom.
  Use when the user asks about PSA, security requirements, privacy requirements,
  compliance requirements, data privacy policies, or security assessments at DT-IT.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/psa by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PSA - Privacy and Security Assessment

Look up DT's Privacy and Security Assessment requirements.

The user's query is: "$ARGUMENTS"

## Tools

Three tools, used in a drill-down workflow:

### 1. `psa_list_subject_areas_and_req_docs` (no params)
Lists all subject areas and their associated requirement documents. Start here to discover what's available.

### 2. `psa_list_requirements`
Given a requirement document name, returns all individual requirements (id + name) in that document.

Parameter:
- `reqdocname` (required): The requirement document name from step 1

### 3. `psa_get_requirement`
Get full details of specific requirements from a document.

Parameters:
- `reqdocname` (required): The requirement document name
- `ids` (required): Array of requirement IDs - only request IDs strictly necessary for the current task

## Workflow

```
psa_list_subject_areas_and_req_docs → find the right document
    ↓
psa_list_requirements(reqdocname) → list requirements in that document
    ↓
psa_get_requirement(reqdocname, ids) → get specific requirement details
```

## Tips

- Start broad with subject areas, then narrow down
- Only fetch requirement details you actually need (minimize `ids` array)
- Requirements are grouped by document - you can only fetch requirements from the same document at once
