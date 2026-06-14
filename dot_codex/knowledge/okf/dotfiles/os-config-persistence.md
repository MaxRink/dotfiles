---
type: Policy
title: OS Config Persistence
status: active
last_verified: "2026-06-14"
source_paths:
  - schiff/tools/dev-notebooks-config/dev-notebook.yaml
  - schiff/tools/dev-notebooks-config/roles
  - dot_agents/skills/codex-knowledge-curation/scripts/persist_os_config.py
---

# OS Config Persistence

The dev-notebook Ansible baseline already owns SSH config generation, proxy/autossh services, WSL system files, SOPS age key creation, Bitwarden CLI installation, eget configuration, Krew/Atuin installation, and optional container tooling. Dotfiles should not store live outputs from those areas when they contain generated state, tokens, credentials, or machine-specific service material.

Persisted local preferences are imported with:

```bash
python dot_agents/skills/codex-knowledge-curation/scripts/persist_os_config.py --apply
```

The script currently persists shell preferences, Powerlevel10k prompt preferences, Atuin behavior config, Delve defaults, VS Code MCP prompt-based server definitions, Git/GitHub/GitLab/JGit non-auth preferences, Go private module settings, htop, k9s, Poetry, Fish shell Atuin integration, and MIME handler preferences. It writes `dot_codex/knowledge/local-os-config-inventory.json` with included and excluded paths.

Do not persist GitHub/GitLab host auth files, Helm repository caches, Mondoo config, SOPS age keys, kubeconfigs, Docker token state, Bitwarden state, shell histories, generated Ansible service units, generated update-check state, installer receipts, raw Codex state, or live `.eget.toml`.

Validation command:

```bash
python dot_agents/skills/codex-knowledge-curation/scripts/validate_codex_persistence.py .
```
