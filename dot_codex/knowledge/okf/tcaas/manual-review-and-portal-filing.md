---
type: Playbook
title: Manual Review And Portal Filing
description: Gatekeeping rules before PSA answer data is written back through the portal browser.
tags: [tcaas, psa, portal, review]
timestamp: 2026-06-14T00:00:00Z
---

# Filing Preconditions

Before writing anything into the PSA portal:

1. Rebuild the answer draft from the manifest and ordered batch files.
2. Sync answer notes so the PSA note field contains reviewed GitLab, GitHub, and Confluence references.
3. Export human-readable markdown for manual review.
4. Run the full SoC gate wrapper.
5. Run portal preflight against the exact manifest to be filled.
6. Run browser filling in dry-run mode and review the report.
7. Use `--apply` and `--save` only after explicit human approval.

# Notes Field

The PSA notes field should contain the vetted reference list. It must not contain local artifact paths such as `tcaas-psa/artifacts/...` as evidence. Local artifact paths can appear only in internal reproduction or provenance docs.

# DTT And NatCo

DTT and NatCo remain future filing scopes. They currently have no separate SoC rows, so do not prepare portal-fill answer files for them yet. Keep the architecture-difference record current for later manual review.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
