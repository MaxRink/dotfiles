---
type: Reference
title: Answer Storage Model
description: Common structured format for PSA SoC answers and portal filling.
tags: [tcaas, psa, soc, answers, json]
timestamp: 2026-06-14T00:00:00Z
---

# Format

Use `psa_answers_v1` JSON for answer data. Each row stores:

| Field | Meaning |
|---|---|
| `answer.statement` | `SOC`, `SOPC`, `SONC`, `NA`, or blank while researching. |
| `answer.explanation` | Portal `Begruendung`; this is the authoritative answer narrative. |
| `answer.note` | Notes field, used for reviewed references and reviewer context. |
| `answer.evidence` | GitLab, GitHub, and Confluence URLs that support the answer. |
| `answer.status` | `draft`, `research_needed`, `ready_for_review`, or `approved_for_portal`. |

# Source Files

| Artifact | Role |
|---|---|
| `answers/tcaas-core_answers.template.json` | Captured template with static requirement context. |
| `analysis/soc-answers/answer_rebuild_manifest.json` | Ordered batch manifest for reproducible rebuilds. |
| `analysis/soc-answers/tcaas-core_scope_draft_answers.json` | Generated full draft, ignored and rebuilt locally. |
| `analysis/soc-answers/tcaas-core_scope_fillable_answers.json` | Compact portal-fill answer set. |
| `analysis/soc-answers/tcaas-core_scope_draft_answers.md` | Human-readable review copy. |

# Current State

The latest Core gate summary reports `991` captured rows, all in `ready_for_review`, with portal-reference hygiene at zero issues. DTT has zero manifest rows and NatCo has no separate manifest, so they have no current row-level answer files.

# Citations

[1] [PSA SoC Workflow](psa-soc-workflow.md)
[2] [Manual Review And Portal Filing](manual-review-and-portal-filing.md)
