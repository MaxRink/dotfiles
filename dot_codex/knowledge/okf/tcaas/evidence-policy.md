---
type: Policy
title: Evidence Policy
description: Source priority and durable-reference rules for PSA SoC answers.
tags: [tcaas, psa, evidence, links, confluence, gitlab]
timestamp: 2026-06-14T00:00:00Z
---

# Source Priority

1. PSA export and browser capture for requirement text, IDs, current statements, explanations, notes, and field IDs.
2. Local project documentation and implementation code/configuration.
3. Captured Confluence and Fact Sheet material.
4. Public upstream/GitHub sources for component purpose or upstream provenance, not production compliance claims unless the row specifically needs upstream evidence.
5. Human owner confirmation for process evidence not visible in repositories.

# Portal-Ready References

Final answer evidence must be:

* GitLab URLs.
* GitHub URLs.
* Confluence URLs.

Do not use local paths, local browser captures, extracted PDFs, generated markdown, or `tcaas-psa/artifacts/...` as final PSA evidence links.

# Notes Field

The notes field should contain the reviewed reference list. Local runtime observations, Mondoo console review, and marcel-1 collections may be summarized as review provenance only when backed by durable GitLab/GitHub/Confluence links for the final answer.

# Link Quality

Prefer pinned commit and line-range links. A vetted link should prove that:

1. The path exists at the cited commit.
2. The line range is valid at the cited commit.
3. The commit is reachable from a remote branch or otherwise explicitly reviewed as durable.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
[2] [T-CaaS Knowledge Base](https://wiki.telekom.de/spaces/TCAAS/pages/2544994733/Knowledge+Base)
