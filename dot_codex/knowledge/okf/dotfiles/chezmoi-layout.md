---
type: Reference
title: Chezmoi Layout
description: Dotfiles repository layout conventions used for Codex and T-CaaS knowledge persistence.
tags: [dotfiles, chezmoi, codex]
timestamp: 2026-06-14T00:00:00Z
---

# Layout

This repository follows chezmoi-style source naming:

| Source Path | Target Path |
|---|---|
| `dot_gitconfig.tmpl` | `~/.gitconfig` |
| `private_dot_ssh/config.tmpl` | `~/.ssh/config` |
| `dot_codex/config.toml` | `~/.codex/config.toml` |
| `dot_codex/rules/default.rules` | `~/.codex/rules/default.rules` |
| `dot_codex/knowledge/okf` | `~/.codex/knowledge/okf` |
| `dot_agents/skills` | `~/.agents/skills` |

# Rationale

The OKF bundle is stored under `dot_codex/knowledge/okf` so it lands next to Codex configuration and can be consumed by future local Codex workflows. Skills are stored under `dot_agents/skills` because personal skills are loaded from the user agent skills path.

# Safety

Chezmoi `private_` controls target file permissions; it is not a substitute for secret management. Secrets, kubeconfigs, authentication JSON, browser captures, and raw session state are excluded entirely.
