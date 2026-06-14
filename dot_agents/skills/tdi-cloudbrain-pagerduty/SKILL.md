---
name: tdi-cloudbrain-pagerduty
user-invocable: true
description: This skill should be used when the user mentions "PagerDuty", "PD", "incidents", "on-call", "oncall", "who is on call", "paging", "alerts", "T-CaaS incidents", "CaaS incidents", asks about "current incidents", "incident statistics", "incident summary", "recent alerts", or needs to check the on-call schedule for the T-CaaS team.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/pagerduty by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PagerDuty Integration

This skill provides tools to interact with the Deutsche Telekom PagerDuty instance for the T-CaaS team.

## Instance Details

- **Web URL**: `https://dt-tdi.eu.pagerduty.com/`
- **API Base URL**: `https://api.pagerduty.com`
- **API Version**: v2
- **Authentication**: API Token (REST API Key)
- **VPN Required**: Yes - API access only works when connected to Telekom VPN

## IMPORTANT: Team Restriction

Operations are restricted to the configured team. Default: T-CaaS.

| Team Name | Team ID | Description |
|-----------|---------|-------------|
| T-CaaS | P5TDGFM | TDI CaaS Operations Team (default) |

All scripts validate the team restriction and will only query/display data for the configured team.

## Configuration

This skill reads team-specific settings from `cloudbrain.yaml` (via `CLOUDBRAIN_CONFIG` env var).

| Setting | Env Variable | Config Key | Default |
|---------|-------------|------------|---------|
| Team ID | `TCAAS_TEAM_ID` | `pagerduty.team_id` | `P5TDGFM` |

Priority: Environment variable → `cloudbrain.yaml` → built-in default.

## Authentication Setup

Set the environment variable before using any PagerDuty operations:

```bash
export PAGERDUTY_TOKEN="your-api-token"
```

To get an API token:
1. Log in to PagerDuty at https://dt-tdi.eu.pagerduty.com/
2. Go to Integrations > Developer Tools > API Access Keys
3. Create a new API Key (Read-only is sufficient for queries)

## Operations

### List Incidents

List incidents for the T-CaaS team:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py
```

Options:
- `--since "YYYY-MM-DD"` - Start date (default: 24 hours ago, or no limit when filtering active)
- `--until "YYYY-MM-DD"` - End date (default: now)
- `--status "triggered,acknowledged,resolved"` - Filter by status (comma-separated)
- `--cluster "name"` - Filter by cluster name (partial match, case-insensitive)
- `--site "name"` - Filter by site name (partial match, case-insensitive)
- `--all` - Show all incidents (no time limit)
- `--max N` - Limit results (default: 1000, or 10000 when filtering by cluster/site)
- `--format` - Output format: `table` (default), `json`, `summary`
- `--no-url` - Hide incident URLs in output

**Note:** When filtering by active statuses only (`triggered,acknowledged`), no time limit is applied by default - this shows ALL open incidents regardless of when they were created.

**Cluster/Site Filtering:** When using `--cluster` or `--site`, the default max results is automatically increased to 10000 to ensure incidents aren't missed due to pagination. This may take longer to fetch but ensures accurate results.

Examples:
```bash
# Default: incidents from last 24 hours
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py

# All active incidents (no time limit applied)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --status triggered,acknowledged

# Incidents from last 7 days
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22"

# All incidents in January 2026
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31"

# Filter by cluster name (automatically fetches more incidents for accurate filtering)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31" --cluster czthpc2-mco-prod

# Filter by site
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --site hc-czthpc2

# Get summary statistics
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --format summary

# All incidents ever (no time limit)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --all
```

#### Understanding Alert Title Format

Incident titles from AlertManager follow this format:

```
[site | cluster] AlertName alert description...
```

| Position | Field | Example |
|----------|-------|---------|
| First bracket value | **Site** | `hc-czbrnc1-baremetal` |
| Second bracket value | **Cluster** | `czbrnc1-ims-prod` |

Example incident title:
```
[hc-czbrnc1-baremetal | czbrnc1-ims-prod] KubePodNotReady Pod kube-system/ceph-csi...
```

- **Site**: `hc-czbrnc1-baremetal` (the physical/logical site location)
- **Cluster**: `czbrnc1-ims-prod` (the Kubernetes cluster name)
- **Alert**: `KubePodNotReady` (the alert rule name)

### Get Incident Details

Retrieve detailed information about a specific incident:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py PXXXXXX
```

Options:
- `--json` - Output raw JSON response

### Who is On-Call

Show who is currently on-call for the T-CaaS team:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py
```

Options:
- `--schedule "Schedule Name"` - Filter by specific schedule
- `--since "YYYY-MM-DDTHH:MM:SSZ"` - Start time (default: now)
- `--until "YYYY-MM-DDTHH:MM:SSZ"` - End time for schedule range
- `--hours N` - Show schedule for next N hours (convenience option)
- `--json` - Output as JSON

Examples:
```bash
# Current on-call
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py

# On-call schedule for next 48 hours (2 days)
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --hours 48

# On-call schedule for next week
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --hours 168

# Filter by specific schedule
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --schedule "First Level" --hours 48

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --json
```

### List Services

List all services associated with the T-CaaS team:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-services.py
```

Options:
- `--status "active,disabled"` - Filter by service status
- `--json` - Output as JSON

### Incident Summary/Statistics

Get incident statistics for the T-CaaS team:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-summary.py
```

Options:
- `--since "YYYY-MM-DD"` - Start date (default: 30 days ago)
- `--until "YYYY-MM-DD"` - End date (default: now)
- `--json` - Output as JSON

This shows:
- Total incident count by status
- Incidents by service
- Incidents by urgency (high/low)
- Most frequently triggered services

### Generate Incident Report

Generate a comprehensive markdown incident report:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py
```

Options:
- `--since "YYYY-MM-DD"` - Start date (default: yesterday)
- `--until "YYYY-MM-DD"` - End date (default: yesterday)
- `--output FILE` - Output file path (default: stdout for text, `reports/` for PDF)
- `--format FORMAT` - Output format: `markdown` (default) or `confluence`
- `--pdf` - Generate PDF output with Telekom branding

The report includes:
- Executive summary with key metrics
- Incidents by service breakdown
- Open incidents (triggered/acknowledged)
- High urgency incidents summary
- Incidents by alert type
- Affected sites
- Timeline of significant events
- Auto-generated recommendations
- Full incident list (collapsible)

Examples:
```bash
# Generate report for yesterday (default)
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py

# Generate report for a specific date
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --since "2026-01-27" --until "2026-01-27"

# Generate weekly report to file
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --since "2026-01-20" --until "2026-01-27" --output reports/weekly-report.md

# Generate Confluence-formatted report
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --format confluence --output report.wiki

# Generate PDF report for yesterday (reproducible daily command)
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --pdf

# Generate PDF report for a specific date
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --pdf --since "2026-01-27" --until "2026-01-27"

# Generate PDF report with custom output path
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --pdf --output /path/to/report.pdf
```

**PDF Output Details:**
- Default output: `reports/tcaas-incidents-YYYY-MM-DD.pdf`
- For date ranges: `reports/tcaas-incidents-YYYY-MM-DD-to-YYYY-MM-DD.pdf`
- Features Telekom magenta branding
- Professional typography with styled tables
- Suitable for sharing and archiving

### AlertManager Rules Reference

Show CaaS AlertManager configuration (routing, inhibit rules, receivers):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py
```

Options:
- `--inhibit` - Show only inhibit rules (which alerts suppress others)
- `--routes` - Show only routing rules
- `--receivers` - Show only receivers
- `--all` - Show all configuration (default)

This reads from the caas-bundles repository (latest version) and shows:
- **Inhibit rules**: Which alerts suppress other alerts
- **Receivers**: OpenNMS, PagerDuty destinations
- **Routes**: How alerts are routed based on severity, environment

Examples:
```bash
# Show all alertmanager configuration
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py

# Show only routing rules
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py --routes

# Show inhibit rules (useful for understanding why an alert wasn't fired)
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py --inhibit
```

**Note:** Requires access to `~/git/caas/caas-bundles` or set `CAAS_BUNDLES_DIR` environment variable.

### Discover Team ID (Utility)

Find the T-CaaS team ID:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-team-info.py "T-CaaS"
```

Options:
- `--json` - Output as JSON

This is typically run once during initial setup.

### Create Jira Tickets

Create well-formatted Jira tickets from PagerDuty incident analysis:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py
```

Options:
- `--incident ID` - Single incident mode - create ticket for specific PagerDuty incident
- `--pattern` - Pattern analysis mode - create ticket for recurring issues
- `--since "YYYY-MM-DD"` - Start date for pattern analysis
- `--until "YYYY-MM-DD"` - End date for pattern analysis
- `--filter TEXT` - Filter incidents by text in title (for pattern mode)
- `--project PROJECT` - Jira project key (default: CAASPROD)
- `--type TYPE` - Issue type (default: Task)
- `--assignee EMAIL` - Assignee email/username
- `--dry-run` - Preview ticket without creating

**Ticket Format Features:**
- Professional Confluence wiki markup (h2. headers, bold, bullets)
- Formatted PagerDuty incident links
- Problem/Analysis/Solution/Acceptance Criteria structure
- Auto-generated solutions based on alert type
- Pattern detection with statistics
- Smart acceptance criteria suggestions

Examples:
```bash
# Create ticket for single incident
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py \
  --incident Q32G3MTCMP2QBZ \
  --project CAASPROD \
  --assignee "angel.vivas-vivas@t-systems.com"

# Preview ticket first (dry-run)
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py \
  --incident Q32G3MTCMP2QBZ \
  --dry-run

# Create ticket for pattern analysis (e.g., flapping alerts)
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py \
  --pattern \
  --since "2026-02-03" \
  --until "2026-02-03" \
  --project CAASPROD \
  --assignee "angel.vivas-vivas@t-systems.com"

# Pattern analysis with filter
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py \
  --pattern \
  --since "2026-02-03" \
  --until "2026-02-03" \
  --filter "TargetDown" \
  --dry-run
```

**Note:** Requires both PAGERDUTY_TOKEN and Jira credentials to be configured.

## Common Use Cases

### Quick Status Check
```bash
# See ALL active incidents (most common use case)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --status triggered,acknowledged

# Check who is on-call now
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py

# On-call schedule for next 2 days
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --hours 48

# List team services
.venv/bin/python ${SKILL_DIR}/scripts/pd-services.py
```

### Incident Investigation
```bash
# Get incidents from last 24 hours
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py

# Get details on specific incident
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py Q32G3MTCMP2QBZ

# Get incident as JSON for scripting
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py Q32G3MTCMP2QBZ --json

# Check alertmanager routing rules (why did this alert fire/not fire?)
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py --routes

# Check inhibit rules (is this alert being suppressed by another?)
.venv/bin/python ${SKILL_DIR}/scripts/pd-alertmanager-rules.py --inhibit
```

### Reporting
```bash
# Weekly incident summary (quick stats)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --format summary

# Monthly statistics
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31" --format summary

# Generate comprehensive daily report (yesterday)
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py

# Generate weekly incident report to file
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --since "$(date -v-7d +%Y-%m-%d)" --output reports/weekly-report.md

# Generate report for Confluence
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --format confluence --output report.wiki

# Generate daily PDF report (reproducible command for daily use)
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --pdf

# Generate weekly PDF report
.venv/bin/python ${SKILL_DIR}/scripts/pd-report.py --pdf --since "$(date -v-7d +%Y-%m-%d)"
```

### Cluster-Specific Queries
```bash
# Check incidents for specific cluster (January 2026)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31" --cluster czthpc2-mco-prod

# Get summary for cluster incidents
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31" --cluster czthpc2-mco-prod --format summary

# All incidents at a site
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --site hc-czthpc2

# Active incidents for a cluster
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --status triggered,acknowledged --cluster my-cluster
```

### Creating Tickets for Issues
```bash
# Analyze yesterday's incidents and create ticket for recurring issues
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-02-03" --format summary
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py --pattern --since "2026-02-03" --until "2026-02-03" --dry-run

# Create ticket for specific problematic incident
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py Q32G3MTCMP2QBZ
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py --incident Q32G3MTCMP2QBZ --assignee "user@t-systems.com"

# Investigate flapping alerts and create deduplication ticket
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2026-02-03" --filter "TargetDown"
.venv/bin/python ${SKILL_DIR}/scripts/pd-create-jira.py --pattern --since "2026-02-03" --filter "TargetDown" --project CAASPROD
```

## Security Notes

1. **Token Storage**: Never commit PAGERDUTY_TOKEN to version control
2. **Team Restriction**: Scripts enforce T-CaaS team filter
3. **Read-Only**: All operations are read-only queries
4. **Audit**: API calls may be logged in PagerDuty

## Additional Resources

For detailed API documentation and advanced query patterns, see:
- [references/api-reference.md](references/api-reference.md) - Full PagerDuty API documentation
- [references/common-queries.md](references/common-queries.md) - Advanced query examples and patterns
