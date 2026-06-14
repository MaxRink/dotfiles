---
name: ai4dev-telecontext-leanix
description: >-
  Look up LeanIX factsheets via Telecontext. Use when the user asks about applications,
  governance, or organizations in LeanIX, including ICTO numbers, lifecycles, responsible
  persons, or application details. Supports Application, Governance, and Organisation factsheets.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/leanix by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# LeanIX - Factsheet Lookup

Retrieve factsheet information from LeanIX.

The user's query is: "$ARGUMENTS"

## Tool

### `leanix-factsheet`

Parameters:
- `type` (required): Factsheet type - `app` (Application), `gov` (Governance), `org` (Organisation)
- `factSheetId` (optional): Factsheet ID (e.g., "T-APP-09698"). No wildcards.
- `name` (optional): Factsheet name. Use wildcard `*` if no exact match (e.g., "One*" to match "OneShop Portal").
- `email` (optional): Email of a responsible person. No wildcards.

## Examples

| Question | Parameters |
|----------|-----------|
| "ICTO number of T-APP-09698" | `type: "app", factSheetId: "T-APP-09698"` |
| "Lifecycle of OneShop Portal" | `type: "app", name: "OneShop Portal"` |
| "Lifecycle of One App and related apps" | `type: "app", name: "One App"` |
| "Responsible person for Magenta Developer Experience" | `type: "app", name: "Magenta Developer Experience"` |
| "Find apps by email" | `type: "app", email: "user@telekom.de"` |

## Tips

- Use `name` with wildcard `*` when unsure of exact name
- Provide `factSheetId` when you have it - it's the most precise lookup
- Only Application, Governance, and Organisation types are currently supported
