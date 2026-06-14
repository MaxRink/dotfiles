---
type: Reference
title: Codex Integration Surfaces
description: Current Codex integration options to use for local, repository, and CI automation work.
tags: [codex, integrations, mcp, skills, automation]
timestamp: 2026-06-14T00:00:00Z
---

# Summary

Use Codex integrations in layers:

| Layer | Use For | Dotfiles Action |
|---|---|---|
| Skills | Repeatable domain workflows with scripts and references. | Store personal skills in [`/dot_agents/skills`](../../../../dot_agents/skills/). |
| Plugins | Installable bundles of skills, MCP servers, hooks, and apps. | Keep curated plugin enablement in [`/dot_codex/config.toml`](../../config.toml). |
| MCP | Tool and context connectors for GitLab/GitHub, docs, browser automation, issue trackers, and observability. | Store server definitions without tokens; pass credentials through environment variables. |
| GitHub review | PR review and PR task entrypoint. | Put review guidance in each repository `AGENTS.md`; request `@codex review` when applicable. |
| GitHub Action | CI, release, migration, and repeatable quality gates. | Prefer prompt files and least-permission jobs; avoid job-wide API-key exposure. |
| Non-interactive mode | Local or CI scripts that need stable command output. | Use `codex exec --json`, `--output-schema`, and `-o` for machine-readable outputs. |
| Linear and Slack | Cloud task entrypoints from issues and conversations. | Use for triage and handoff; keep sensitive project context in reviewed repositories or issues. |
| Hooks and memories | Guardrails, summaries, and recurring preferences. | Persist only reviewed rules and curated memory summaries, not raw session state. |

# Recommended Local Setup

1. Keep `tcaas-filesystem` enabled for local source context.
2. Keep GitLab and Kubernetes MCP servers disabled by default until their environment and authorization boundaries are clear.
3. Use MCP tool allowlists and approval modes for browser, GitHub, GitLab, Linear, and observability connectors.
4. Keep credentials in environment variables or the platform secret store, never in `config.toml`.
5. Use skills for PSA portal capture and T-CaaS SoC analysis because both require repeatable scripts, known file formats, and explicit safety rules.

# CI Pattern

For repeatable checks, commit a prompt and schema next to the workflow and invoke Codex through `openai/codex-action@v1` or `codex exec`. The output should be a file artifact or JSON object that another job can validate. This avoids copy-pasted prompts and makes review criteria diffable.

# Citations

[1] [Codex skills documentation](https://developers.openai.com/codex/skills)
[2] [Codex MCP documentation](https://developers.openai.com/codex/mcp)
[3] [Codex GitHub integration](https://developers.openai.com/codex/integrations/github)
[4] [Codex Slack integration](https://developers.openai.com/codex/integrations/slack)
[5] [Codex Linear integration](https://developers.openai.com/codex/integrations/linear)
[6] [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive)
[7] [Codex GitHub Action](https://developers.openai.com/codex/github-action)
