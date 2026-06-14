---
type: Procedure
title: Project Skill Persistence
status: active
last_verified: "2026-06-14"
source_paths:
  - dot_agents/skills/codex-knowledge-curation/scripts/persist_project_skills.py
  - dot_agents/skills/imported-skills.json
---

# Project Skill Persistence

Local project skills are imported into `dot_agents/skills` so they can be direct-loaded by Codex from `~/.agents/skills` after chezmoi apply. Imports are deterministic and should be rerun through the script, not by manually copying directories.

```bash
python dot_agents/skills/codex-knowledge-curation/scripts/persist_project_skills.py --apply
```

The importer scans local project repositories for `SKILL.md`, skips `.worktrees`, caches, bytecode, transient databases, and large binary artifacts, normalizes direct-load skill names to globally unique kebab-case names, and writes provenance to `dot_agents/skills/imported-skills.json`.

Template/example skills and empty `SKILL.md` files are recorded in the manifest but not direct-loaded. This prevents placeholder instructions from becoming active skills while still preserving the audit trail.

Before committing skill imports, run the persistence validator and a normal Git whitespace check. If a skill needs credentials at runtime, keep only placeholders or environment-variable names in the skill; never commit the credential value or auth file.
