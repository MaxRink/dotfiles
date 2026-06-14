---
name: codex-knowledge-curation
description: Use when updating this dotfiles repo's Codex configuration, OKF knowledge bundle, persisted skills, or persistence policy. Keeps reusable knowledge versioned while preventing raw Codex state, browser captures, credentials, and cache files from entering dotfiles.
---

# Codex Knowledge Curation

Use this skill for dotfiles changes that touch Codex configuration, reusable skills, or the OKF knowledge bundle.

## Workflow

1. Keep durable knowledge in `dot_codex/knowledge/okf`.
2. Keep personal reusable skills in `dot_agents/skills`.
3. Keep Codex config in `dot_codex/config.toml` and approval rules in `dot_codex/rules/default.rules`.
4. Do not copy raw `~/.codex` state, auth, credentials, caches, shell snapshots, SQLite files, browser captures, kubeconfigs, or secrets.
5. Prefer scripts over one-off prompt instructions when a check will be run more than once.
6. After edits, run:

```bash
python dot_agents/skills/codex-knowledge-curation/scripts/validate_codex_persistence.py .
```

## OKF Rules

- `index.md` and `log.md` are reserved.
- Root `index.md` may declare `okf_version`.
- Every other markdown file must have YAML frontmatter with a non-empty `type`.
- Use bundle-relative links for internal OKF relationships where practical.

## Secret Hygiene

Treat findings from the validator as blockers unless they are proven false positives. Do not persist:

- API keys, PATs, bearer tokens, private keys, kubeconfigs, or auth JSON.
- Confluence or browser HTML exports that can contain transient tokens.
- Codex SQLite, JSONL histories, shell snapshots, cache, tmp, or package state.
