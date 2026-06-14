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
| Plugins | Installable bundles of skills, MCP servers, hooks, apps, browser integrations, and Sites. | Keep curated plugin enablement in [`/dot_codex/config.toml`](../../config.toml). |
| MCP | Tool and context connectors for GitLab/GitHub, docs, browser automation, issue trackers, observability, and Codex-as-a-tool workflows. | Store server definitions without tokens; pass credentials through environment variables. |
| GitHub review | PR review and PR task entrypoint. | Put review guidance in each repository `AGENTS.md`; request `@codex review` when applicable. |
| GitHub Action | CI, release, migration, and repeatable quality gates. | Prefer prompt files and least-permission jobs; avoid job-wide API-key exposure. |
| SDK and app-server | Programmatic Codex control from products, scripts, and internal workflow tools. | Prefer SDK for automation; use app-server for rich clients and keep app-server transports local or authenticated. |
| Non-interactive mode | Local or CI scripts that need stable command output. | Use `codex exec --json`, `--output-schema`, and `-o` for machine-readable outputs. |
| Linear and Slack | Cloud task entrypoints from issues and conversations. | Use for triage and handoff; keep sensitive project context in reviewed repositories or issues. |
| Browser, Chrome, and Computer Use | Visual QA, local preview, signed-in browser workflows, and desktop app workflows. | Use in-app Browser for localhost/public pages first; use Chrome only for signed-in browser state; use Computer Use only for scoped GUI tasks. |
| Remote connections | Continue work from another device or connect the app to SSH-hosted projects. | Use existing SSH trust and avoid exposing app-server transports directly on shared/public networks. |
| Sites | Save/deploy hosted sites, apps, and games from compatible projects. | Save versions before deployment, review access mode, and keep runtime secrets in Sites environment variables. |
| Subagents | Explicit parallel exploration, review, testing, or implementation work. | Use only when the prompt asks for subagents or parallel agent work; keep write scopes disjoint. |
| Hooks and memories | Guardrails, summaries, and recurring preferences. | Persist only reviewed rules and curated memory summaries, not raw session state. |

# Recommended Local Setup

1. Keep `tcaas-filesystem` enabled for local source context.
2. Keep GitLab and Kubernetes MCP servers disabled by default until their environment and authorization boundaries are clear.
3. Use MCP tool allowlists and approval modes for browser, GitHub, GitLab, Linear, and observability connectors.
4. Keep credentials in environment variables or the platform secret store, never in `config.toml`.
5. Use skills for PSA portal capture and T-CaaS SoC analysis because both require repeatable scripts, known file formats, and explicit safety rules.
6. Use Browser/Chrome/Computer Use only when the task needs visual or signed-in UI context. Prefer structured APIs, MCP servers, scripts, or repository files when those provide the same evidence.
7. For Codex-internal orchestration, prefer `codex exec` for one-shot automation, the SDK for programmatic control, app-server for rich client integration, and Codex MCP server when another agent runtime should call Codex as a tool.

# CI Pattern

For repeatable checks, commit a prompt and schema next to the workflow and invoke Codex through `openai/codex-action@v1`, `codex exec`, the Codex SDK, or a Codex MCP server owned by an orchestrator. The output should be a file artifact or JSON object that another job can validate. This avoids copy-pasted prompts and makes review criteria diffable.

# Current Surface Guidance

* Use the in-app Browser for local development servers, file-backed previews, public unauthenticated pages, screenshot checks, and CDP-backed diagnostics that can stay inside Codex.
* Use the Chrome extension only when the task needs the user's signed-in browser state, extensions, profile cookies, or internal web tools that are not available through a structured connector.
* Use Computer Use only for macOS/Windows GUI workflows where files, CLI commands, APIs, or browser automation are insufficient. Keep tasks narrow because it can affect state outside the repository.
* Use Remote connections when the project lives on another host or when approvals and follow-up instructions need to happen from another device. Keep SSH trust and host security equivalent to normal production remote-development expectations.
* Use Sites for hosted web output when a production URL is the desired artifact. Save a version before deploying and do not store runtime secrets in `.openai/hosting.json`.
* Use subagents for explicit parallel work such as independent evidence collection, security review, test-gap review, or disjoint implementation slices. Do not spawn subagents implicitly from vague requests for depth.
* Use Codex app-server only for rich client integrations that need threads, approvals, history, and streamed events. Do not expose unauthenticated non-loopback app-server listeners.
* Use the Codex SDK or `codex mcp-server` for internal automation and orchestrated agent workflows. Keep API keys in local secret stores or CI secret stores, not in prompts, skills, or dotfiles.

# Citations

[1] [Codex skills documentation](https://developers.openai.com/codex/skills)
[2] [Codex MCP documentation](https://developers.openai.com/codex/mcp)
[3] [Codex GitHub integration](https://developers.openai.com/codex/integrations/github)
[4] [Codex Slack integration](https://developers.openai.com/codex/integrations/slack)
[5] [Codex Linear integration](https://developers.openai.com/codex/integrations/linear)
[6] [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive)
[7] [Codex GitHub Action](https://developers.openai.com/codex/github-action)
[8] [Codex Chrome extension](https://developers.openai.com/codex/app/chrome-extension)
[9] [Codex in-app browser](https://developers.openai.com/codex/app/browser)
[10] [Codex Computer Use](https://developers.openai.com/codex/app/computer-use)
[11] [Codex app-server](https://developers.openai.com/codex/app-server)
[12] [Codex SDK](https://developers.openai.com/codex/sdk)
[13] [Use Codex with the Agents SDK](https://developers.openai.com/codex/guides/agents-sdk)
[14] [Codex remote connections](https://developers.openai.com/codex/remote-connections)
[15] [Codex Sites](https://developers.openai.com/codex/sites)
[16] [Codex subagents](https://developers.openai.com/codex/subagents)
