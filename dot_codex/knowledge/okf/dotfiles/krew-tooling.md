---
type: Reference
title: Krew Tooling
description: Kubernetes CLI plugin bootstrap stored in dotfiles.
tags: [dotfiles, kubernetes, krew]
timestamp: 2026-06-14T00:00:00Z
---

# Managed Scripts

The repository already contains:

| Script | Purpose |
|---|---|
| `run_once_install-krew.sh` | Bootstrap krew once. |
| `run_install-krew-plugins.sh` | Install or refresh the selected kubectl plugin set. |

# Relationship To Codex

These tools support Kubernetes investigation and cluster review. They do not replace the safety boundary for live clusters: Codex should still prefer read-only collectors and explicit user approval for any cluster-changing action.

# Policy

1. Keep plugin installation scripts idempotent.
2. Do not embed kubeconfigs, tokens, or cluster credentials.
3. Document new Kubernetes tooling here when it changes the SoC/runtime verification workflow.
