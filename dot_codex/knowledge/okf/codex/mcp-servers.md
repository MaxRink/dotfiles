---
type: Reference
title: MCP Servers
description: MCP server policy and connector candidates for Codex work.
tags: [codex, mcp, connectors, security]
timestamp: 2026-06-14T00:00:00Z
---

# Current Servers

| Server | Default | Purpose | Credential Policy |
|---|---|---|---|
| `tcaas-filesystem` | enabled | Read T-CaaS workspace files through a scoped filesystem MCP server. | No credentials. |
| `tcaas-gitlab` | disabled | GitLab project, MR, issue, and repository API access. | Requires `GITLAB_PERSONAL_ACCESS_TOKEN` from environment. |
| `tcaas-kubernetes-non-destructive` | disabled | Kubernetes inspection and limited operations. | Requires current kube context; keep opt-in. |
| `Telecontext` | configured | Internal Telekom context server. | Server-side auth/context; no local token in config. |

# Candidate Servers

Add only when needed, with tool allowlists and approval modes:

* OpenAI Docs MCP for official OpenAI API and Codex documentation.
* Context7 for current developer library documentation.
* Chrome DevTools or Playwright for instrumented browser workflows.
* GitHub MCP for public GitHub repository inspection and PR work.
* Linear MCP for local issue context.
* Sentry or observability MCPs for incident and runtime-debug context.

# Controls

1. Prefer `enabled_tools` over broad server access.
2. Use `default_tools_approval_mode = "prompt"` for tools that can mutate state or access sensitive systems.
3. Set `required = true` only for automation that must fail closed when a server is unavailable.
4. Put bearer tokens in environment variables or a managed secret store.

# Citations

[1] [Codex MCP documentation](https://developers.openai.com/codex/mcp)
[2] [Codex Linear integration](https://developers.openai.com/codex/integrations/linear)
