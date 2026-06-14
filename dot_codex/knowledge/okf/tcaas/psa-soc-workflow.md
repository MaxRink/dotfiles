---
type: Playbook
title: PSA SoC Workflow
description: Repeatable workflow for capturing, extracting, answering, validating, and later filling PSA SoC rows.
tags: [tcaas, psa, soc, workflow]
timestamp: 2026-06-14T00:00:00Z
---

# Scope

This workflow applies to T-CaaS PSA Statement of Compliance work. The current filing-ready corpus is the captured T-CaaS Core system. DTT and NatCo do not currently have separate SoC rows to answer; keep only their architectural differences until PSA exposes separate rows.

# Steps

1. Start a proxy-backed Chromium instance with DevTools enabled.
2. Let the user authenticate manually.
3. Capture the system snapshot and SoC manifest.
4. Download all available SoC artifacts.
5. Extract XLSX, HTML, and PDF artifacts.
6. Render static requirement material into markdown.
7. Inspect live browser fields for statement radios, justification text, notes, note visibility, and read-only notes.
8. Build `psa_answers_v1` JSON templates.
9. Research each question against GitLab, GitHub, Confluence, Mondoo, and marcel-1 evidence as applicable.
10. Sync vetted evidence URLs into the answer notes.
11. Run answer-quality, completeness, coverage, Confluence, and portal preflight gates.
12. Only after manual review, use the browser filler first in dry-run mode, then apply/save if explicitly approved.

# Evidence Rule

Portal-ready answer evidence must be GitLab, GitHub, or Confluence URLs. Local artifacts under `tcaas-psa/artifacts/` are provenance and reproduction material only; they are not final PSA evidence links.

# Tools

Use the persisted skills:

* [`psa-portal-soc-capture`](../../../../dot_agents/skills/psa-portal-soc-capture/SKILL.md)
* [`tcaas-soc-analysis`](../../../../dot_agents/skills/tcaas-soc-analysis/SKILL.md)

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
[2] [T-CaaS Knowledge Base](https://wiki.telekom.de/spaces/TCAAS/pages/2544994733/Knowledge+Base)
