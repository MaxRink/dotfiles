---
name: tcaas-agent-troubleshooter-cloud-pagerduty
description: Interact with PagerDuty for incident management, on-call schedules, and alerting. Query incidents, generate reports, manage on-call rotations, add notes to incidents, and resolve incidents. Use when the user mentions "PagerDuty", "PD", "incidents", "on-call", "oncall", "who is on call", "paging", "alerts", "T-CaaS incidents", "CaaS incidents", asks about "current incidents", "incident statistics", "incident summary", "recent alerts", needs to add notes or resolve incidents, or needs to check the on-call schedule for the T-CaaS team.
---

<!-- Imported from tdi-caas/tools/tcaas-agent-troubleshooter/skills/cloud-pagerduty by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PagerDuty Integration

Interact with the Deutsche Telekom PagerDuty instance for the T-CaaS team.

- **Web URL**: `https://dt-tdi.eu.pagerduty.com/`
- **API Base URL**: `https://api.pagerduty.com`
- **VPN Required**: Yes
- **Team**: T-CaaS (ID: `P5TDGFM`) — all scripts enforce this restriction
- **Auth**: `PAGERDUTY_TOKEN` env var (loaded via `source .env`)

## Usage

All scripts use the project venv and require environment variables:

```bash
source .env && .venv/bin/python .claude/skills/pagerduty/scripts/<script>.py [args]
```

See [references/common-queries.md](references/common-queries.md) for detailed examples and common workflows.

## Script Selection — Decision Tree

| User Request | Script | Key Flags |
|---|---|---|
| "show open/active incidents", "what's firing" | `pd-incidents.py` | `--status triggered,acknowledged` |
| "list incidents from [date]" | `pd-incidents.py` | `--since X --until Y` |
| "incidents for cluster X" | `pd-incidents.py` | `--cluster X` |
| "summary", "statistics", "how many incidents" | `pd-incidents.py` | `--format summary` |
| "report", "generate report", "PDF" | `pd-report.py` | `--pdf` for PDF output |
| "who is on call" | `pd-oncall.py` | `--hours N` for future schedule |
| "incident details", specific ID | `pd-incident-get.py` | incident ID as argument |
| "add note", "comment on incident" | `pd-incident-note.py` | incident ID + note text |
| "resolve incident", "close incident" | `pd-incident-resolve.py` | `--note "reason"` optional |
| "list services" | `pd-services.py` | |
| "create Jira ticket from incident" | `pd-jira-prepare.py` → **cloud-jira skill** | two-step workflow |
| "alertmanager rules", "why did this alert fire" | `pd-alertmanager-rules.py` | `--routes`, `--inhibit` |
| "team info" | `pd-team-info.py` | one-time utility |

### Key Distinctions

- **pd-incidents.py** = default for any incident query. `--format summary` for stats, `--format table` (default) for listing, `--format json` for raw data.
- **pd-report.py** = ONLY when user wants a formatted, shareable report (markdown, Confluence, PDF). Superset of incidents + summary.
- **pd-jira-prepare.py** = analysis only, outputs JSON. Does NOT create tickets. Use cloud-jira skill for actual creation.

## Operations

Quick command reference (see [common-queries.md](references/common-queries.md) for detailed examples):

**Querying & Reporting:**
- **pd-incidents.py** - List and summarize incidents. Use `--status`, `--cluster`, `--site`, `--format summary`
- **pd-report.py** - Generate formatted reports (markdown, PDF). Use `--pdf` for PDF output
- **pd-incident-get.py** - Get single incident details by ID

**Incident Actions:**
- **pd-incident-note.py** - Add notes/comments to incidents. Args: `INCIDENT_ID "note text"`
- **pd-incident-resolve.py** - Resolve incidents. Use `--note "reason"` to add explanation

**On-Call & Services:**
- **pd-oncall.py** - Check on-call schedules. Use `--hours N` for future schedule
- **pd-services.py** - List PagerDuty services

**Integration:**
- **pd-jira-prepare.py** - Prepare Jira ticket data from incidents (use with cloud-jira skill)
- **pd-alertmanager-rules.py** - Query AlertManager configuration. Use `--routes`, `--inhibit`

**Utility:**
- **pd-team-info.py** - Team ID lookup (one-time utility)

## Alert Title Format

Incident titles from AlertManager: `[site | cluster] AlertName description`

Example: `[hc-czbrnc1-baremetal | czbrnc1-ims-prod] KubePodNotReady Pod kube-system/ceph-csi...`
- **Site**: `hc-czbrnc1-baremetal` — physical/logical location
- **Cluster**: `czbrnc1-ims-prod` — Kubernetes cluster
- **Alert**: `KubePodNotReady` — alert rule name

Convergence format: `CONVERGENCE [T: type | L: location | C: cluster] A: AlertName description`

## References

- [references/common-queries.md](references/common-queries.md) — Detailed examples, shell aliases, troubleshooting
- [references/api-reference.md](references/api-reference.md) — PagerDuty API documentation
