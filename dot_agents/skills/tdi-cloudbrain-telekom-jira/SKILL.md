---
name: tdi-cloudbrain-telekom-jira
user-invocable: true
description: This skill should be used when the user mentions "Jira", "CAASPROD", "TCAAS", "Telekom Jira", "DT Jira", "caas", "tdi caas", "converged", "ONB", "onboarding", asks to "search issues", "create ticket", "create task", "create Jira", "update issue", "check issue status", "get issue", "transition issue", or needs Jira field mappings for the Deutsche Telekom Jira instance.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/telekom-jira by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Telekom Jira Integration

- **Base URL**: `https://jira.telekom.de/`
- **Auth**: Bearer Token via `JIRA_API_TOKEN` env var
- **VPN Required**: Yes

## Allowed Projects

Projects, aliases, and required labels are configurable via `cloudbrain.yaml`.
Default values (used when no config is set) are shown below.

| Key | Aliases | Description |
|-----|---------|-------------|
| CAASPROD | "caas", "tdi caas" | Production CaaS operations and incidents |
| TCAAS | "tcaas", "converged" | TDI CaaS development and convergence tasks |
| ONB | "onb", "onboarding" | Jira Service Desk - CaaS cluster requests (shared project) |

> **IMPORTANT:** When the user says "caas" without specifying "tcaas" or "both projects",
> ONLY search/operate on **CAASPROD**. Ask for clarification if unclear.

## Configuration

This skill reads team-specific settings from `cloudbrain.yaml` (via `CLOUDBRAIN_CONFIG` env var).

| Setting | Env Variable | Config Key | Default |
|---------|-------------|------------|---------|
| Allowed projects | `JIRA_PROJECTS` | `jira.projects` | `CAASPROD, TCAAS, ONB` |
| Project aliases | — | `jira.aliases` | See table above |
| Required labels | — | `jira.required_labels` | `tdi-caas-operations, tdi-caas-development` (CAASPROD) |

Priority: Environment variable → `cloudbrain.yaml` → built-in default.

## Custom Fields

| Purpose | Field ID | Script Flag | Format |
|---------|----------|-------------|--------|
| Target Start Date | customfield_21920 | --target-start | YYYY-MM-DD |
| Target End Date | customfield_21921 | --target-end | YYYY-MM-DD |
| Epic Link | customfield_17615 | --epic | Epic key |
| Sprint | customfield_12810 | --sprint | Sprint ID |

See [field-mappings.md](references/field-mappings.md) for complete field documentation.

## Operations

All scripts run with the project venv: `.venv/bin/python ${SKILL_DIR}/scripts/<script>.py`

### Search Issues

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = TCAAS AND status not in (Closed, Done)'
```

**Important:** Use single quotes and `not in` instead of `!=` to avoid shell escaping issues.

Options: `--max N` (default: 50), `--fields "f1,f2"`, `--format table|json`

### Get Epic Children

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-epic-children.py TCAAS-100
```

Uses Agile API since `cf[17615]` in JQL doesn't reliably return all children.

Options: `--max N`, `--format table|json`

### Create Issue

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-create.py \
  --project TCAAS --type Task --summary "Issue title" --description "Details"
```

Required: `--project`, `--type` (Task/Bug/Story/Epic/Sub-task), `--summary`
Optional: `--description`, `--labels`, `--assignee` (email), `--target-start`, `--target-end`, `--fix-version`, `--epic`, `--parent`

### Update Issue

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-update.py TCAAS-123 --summary "New title" --add-labels "label1"
```

Options: `--summary`, `--description`, `--add-labels`, `--remove-labels`, `--assignee` (email), `--target-start`, `--target-end`, `--epic`

### Get Issue Details

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-get.py TCAAS-123
```

Options: `--format table|json`

### Transition Issue

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-transition.py TCAAS-123 "In Progress"
```

Options: `--list` (list available transitions). Common: "To Do", "In Progress", "In Review", "Done", "Closed"

### Batch Label Issues

Add labels to all issues matching a JQL query:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-batch-label.py \
  --jql 'project = CAASPROD AND status in (Refined, "In Progress") AND type not in (Epic) AND (labels is EMPTY OR labels not in (tdi-caas-operations, tdi-caas-development))' \
  --add-labels tdi-caas-operations
```

Options: `--jql` (required), `--add-labels` (required, comma-separated), `--max N` (default: 200), `--dry-run`

Always use `--dry-run` first to preview changes. For mixed ops/dev results, run twice with different labels and use `key in (...)` in the JQL to target subsets.

## Required Labels

### CAASPROD — MANDATORY

All CAASPROD tickets **must** have one of:

| Label | Use When |
|-------|----------|
| `tdi-caas-operations` | Operational: incidents, on-call, monitoring, cluster migrations, maintenance |
| `tdi-caas-development` | Development: features, improvements, automation, tooling |

### TCAAS

| Label | Use When |
|-------|----------|
| `tdi-caas-convergence` | Convergence work items |
| `migration-tdi` | Migration-related tasks |

## ONB Project (Service Desk)

ONB is a shared project. Scope to CaaS-relevant tickets:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = ONB AND "Assignee Group" = "gard_team_ CaaS" AND status not in (Resolved, Closed, Canceled, Cancelled, Done)'
```

See [jql-examples.md](references/jql-examples.md#onb-service-desk-queries) for the full queue filter.

## JQL Reference

See [jql-examples.md](references/jql-examples.md) for comprehensive queries, shell escaping tips, and assignee lookup guidance.

Key gotchas:
- Use `not in` instead of `!=` (bash history expansion breaks `!`)
- Wrap JQL in single quotes
- `assignee` field does NOT support `~` — use `=` with full display name
- `--assignee` flag requires username (email), not display name — see [lookup instructions](references/jql-examples.md#assignee-lookup)

## Security Notes

1. **Token Storage**: Never commit JIRA_API_TOKEN to version control
2. **Project Restriction**: Scripts enforce allowed projects list
3. **Audit**: All API calls use your personal token — actions are attributed to you
