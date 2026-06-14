---
type: Reference
title: AI MR Review
description: T-CaaS AI-assisted development and CI review scope for SoC and Codex automation work.
tags: [tcaas, ai, ci, merge-requests, codex]
timestamp: 2026-06-14T00:00:00Z
---

# Scope

T-CaaS is not a tenant-facing runtime AI or ML product. AI still applies to development and CI because the platform uses AI-supported MR summaries, release notes, and review jobs.

# Current CI Evidence

The shared CI definitions include hidden jobs for:

| Job | Purpose | Blocking |
|---|---|---|
| `.ai-summary-mr` | MR summaries and comments. | No, regular summaries are allowed to fail. |
| `.ai-summary-elevated-components` | Risk review for elevated-components and policy exceptions. | Yes, `allow_failure: false`. |
| `.ai-summary-code-tests` | Review code changes without tests. | Yes, `allow_failure: false`. |
| `.ai-summary-release` | Release note generation. | Artifact output, non-blocking by default. |

The CI job maps GAIA credentials from GitLab group variables into runtime environment variables. These values are not persisted in dotfiles.

# SoC Answering Guidance

AI/ML rows need scoped answers:

* Use `SOC` or `SOPC` only for the documented development/CI toolchain.
* Use `NA` for tenant-facing model operation requirements when the row is about runtime AI/ML products rather than T-CaaS development tooling.
* Keep data categories, provider/model, retention, advisory versus blocking behavior, and human review evidence explicit.

# Citations

[1] [Codex GitHub Action](https://developers.openai.com/codex/github-action)
[2] [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive)
