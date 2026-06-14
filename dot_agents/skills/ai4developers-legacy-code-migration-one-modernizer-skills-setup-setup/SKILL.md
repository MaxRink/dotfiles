---
name: ai4developers-legacy-code-migration-one-modernizer-skills-setup-setup
description: "Install and validate the one-modernizer environment. Creates venv, installs CLI, detects host/OS, generates IDE instruction files. Run on first use or when something seems broken."
---

<!-- Imported from ai4developers/legacy-code-migration/one-modernizer/skills/setup by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Setup Environment

Checks the environment, installs what's missing, generates config for the user's IDE.

## Step 1: Diagnose & Install

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/diagnose.py
```

Auto-fixes:

| Check              | Action                 |
| ------------------ | ---------------------- |
| venv missing       | Creates it             |
| CLI not installed  | Installs from servers/ |
| Windows long paths | Enables via git config |

Cannot auto-fix (reports to user):

| Check                                | User action needed      |
| ------------------------------------ | ----------------------- |
| Python < 3.10                        | Install from python.org |
| output-styles/goal-driven.md missing | Check git status        |

## Step 2: Generate IDE Instruction File (if needed)

Pre-generated files already exist at the plugin repo root for all major IDEs. If the user needs one regenerated or wants it in a different project:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/generate_host_configs.py --host <name>
```

Available hosts: `copilot`, `cursor`, `windsurf`, `junie`, `cline`, `aider`.

Ask the user which host they use before running — don't generate all of them.

## Step 3: Confirm

One-line status: ready or list of unresolved issues.
