---
type: Reference
title: Codex Workspace Setup
description: Durable summary of the local Codex setup used for the T-CaaS multi-repository workspace.
tags: [codex, workspace, tcaas, mcp]
timestamp: 2026-06-14T00:00:00Z
---

# Current Shape

The T-CaaS workspace is a multi-repository tree under `/home/a92615428/git/devops.telekom.de/cit/t-caas`. The reproducible setup records trusted repository roots, baseline `AGENTS.md` coverage, MCP definitions, and the curated Codex Security plugin.

# Persisted Defaults

The dotfiles config keeps only a compact trust surface:

* `/home/a92615428`
* `/home/a92615428/git/devops.telekom.de`
* `/home/a92615428/git/devops.telekom.de/cit/t-caas`

The local workspace helper in `cit/t-caas/codex` can expand this into per-repository trust entries. Dotfiles should keep the portable baseline, not every transient nested checkout.

# Operating Rules

1. Keep `tcaas-filesystem` enabled and scoped to the workspace path.
2. Keep GitLab and Kubernetes MCP servers disabled until the session explicitly needs them.
3. Never put GitLab tokens, kubeconfigs, or API keys into Codex config.
4. Restart Codex after installing or updating plugins so plugin skills are visible.

# Citations

[1] [T-CaaS Codex workspace setup README](https://gitlab.devops.telekom.de/cit/t-caas/codex)
[2] [Codex MCP documentation](https://developers.openai.com/codex/mcp)
[3] [Codex skills documentation](https://developers.openai.com/codex/skills)
