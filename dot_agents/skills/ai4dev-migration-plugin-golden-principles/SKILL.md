---
name: ai4dev-migration-plugin-golden-principles
description: >-
  Golden audit principles library for the llm-as-judge. Provides reusable evaluation
  guidelines that prevent known false positives and ensure consistent verdicts across
  projects. The judge consults and manages principles automatically — no user interaction required.
user-invocable: false
disable-model-invocation: true
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/migration-plugin/skills/golden-principles by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Golden Principles

Golden principles are reusable evaluation guidelines that the llm-as-judge consults
during every audit. They reduce false positives, ensure consistent verdicts across
projects, and capture institutional knowledge from past audits.

The entire lifecycle is managed by the judge automatically — no user intervention needed.

## Principle Sources

1. **Default principles** (shipped with plugin, read-only):
   `${CLAUDE_PLUGIN_ROOT}/skills/golden-principles/references/default-principles.md`

2. **Learned principles** (accumulated from audits):
   `${CLAUDE_PLUGIN_DATA}/golden-principles/*.md` — one file per principle with YAML frontmatter

## Learned Principle File Format

```markdown
---
id: GP-101
title: "Descriptive title"
severity: OBS | WARNING | CRITICAL
applies_to: audit-explore | audit-analysis | both
check: 7
status: candidate | confirmed
source_repo: repo-name-where-discovered
discovered_at: 2026-03-30
confirmed_at: null | 2026-04-02
observations: 1
observed_in:
  - repo-name-1
---

Description of the pattern the judge will encounter and why this principle exists.
```

- IDs for learned principles start at **GP-101** (defaults use GP-001 through GP-099)
- `status: candidate` — proposed by the judge, not yet applied to verdicts
- `status: confirmed` — auto-promoted after consistent observations, applied in all future audits
- `observations` — how many times the judge has seen this pattern across audits
- `observed_in` — list of repo names where the pattern was observed

## Auto-Promotion Rules

The judge promotes a candidate to confirmed when **both** conditions are met:

1. `observations >= 2` — the pattern has been seen in at least 2 separate audits
2. `observed_in` contains at least **2 different repos** — the pattern is not repo-specific

When promoting, the judge updates the file:

- Set `status: confirmed`
- Set `confirmed_at` to today's date

If a candidate is observed again in the **same repo** it was first discovered in,
increment `observations` but do not promote — it may still be repo-specific.
Only add to `observed_in` if the repo is not already listed.

## Principle Application During Audits

When a golden principle (default or confirmed learned) matches a finding:

1. Downgrade the severity to what the principle specifies
2. Note the principle application in the audit report: "GP-XXX applied: <title>"
3. The finding still appears in the report for transparency, just at reduced severity

Candidate principles are **not applied** to verdicts — they are tracked but do not
influence pass/fail decisions until promoted.
