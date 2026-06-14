---
type: Policy
title: Agent Rules
description: Persisted Codex approval-rule policy for this dotfiles repo.
tags: [codex, approvals, rules, policy]
timestamp: 2026-06-14T00:00:00Z
---

# Current Rule Source

The persisted rules live in [`/dot_codex/rules/default.rules`](../../rules/default.rules). They contain reviewed command-prefix approvals for recurring GitLab and Git workflows.

# Policy

1. Keep prefix rules narrow and command-specific.
2. Do not add destructive prefixes such as broad `rm`, `git reset`, or generic language runtimes.
3. Avoid prefix rules for commands that use heredocs, arbitrary shell expansion, or broad scripting entrypoints.
4. Revisit rules after a project or authentication change.

# Dotfiles Handling

Approval rules are safe to persist when they do not include secrets. They still influence future tool behavior, so changes should be reviewed like code.

# Citations

[1] [Codex non-interactive mode permissions and safety](https://developers.openai.com/codex/noninteractive)
