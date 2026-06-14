# Bundle Update Log

## 2026-06-14

* **Creation**: Added the initial OKF bundle for Codex integration research, PSA SoC workflow knowledge, T-CaaS evidence sources, DTT/NatCo architectural differences, and dotfiles persistence policy.
* **Policy**: Documented that DTT and NatCo currently have no separate SoC answer set; only architectural differences are stored until PSA exposes separate rows.
* **Safety**: Persisted curated knowledge and sanitized config only; raw Codex auth/state, browser captures, Confluence exports, kubeconfigs, and transient databases stay out of dotfiles.
* **OS Config**: Added a repeatable inventory/import script for local OS preferences not covered by the dev-notebook Ansible baseline.
* **Skills**: Added a repeatable importer for local project skills, with provenance, duplicate/worktree avoidance, template-skill recording, and cache/binary filtering.
