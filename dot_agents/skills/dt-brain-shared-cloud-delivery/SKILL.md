---
name: dt-brain-shared-cloud-delivery
description: This skill should be used when the user mentions "TDI cloud delivery", "DC deployment", "datacenter deployment", "datacenter extension", "CID epics", "cit-iaas", "deployment status", "cloud infrastructure delivery", or needs to track TDI internal planning for datacenter deployments and extensions from the GitLab CID group.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-delivery by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TDI Cloud Delivery

This skill provides CID-specific tools to track TDI internal planning for datacenter (DC) deployments and extensions using GitLab epics from the CIT-IaaS CID group.

> **Note**: This skill focuses on CID-specific features: country filtering, delivery manager/assignee search, squad labels, subgroup filtering, hierarchy analysis, and deployment reports. For generic GitLab operations on CID projects, use the **GitLab skill** instead (see [Cross-Skill Operations](#cross-skill-operations) below).

## Instance Details

- **Base URL**: `https://gitlab.devops.telekom.de/`
- **API Version**: v4
- **Authentication**: Personal Access Token via `GITLAB_API_TOKEN`
- **VPN Required**: Yes - API access only works when connected to Telekom VPN
- **SSL Verification**: Disabled (internal certificate)

## IMPORTANT: Allowed Groups

Operations are **restricted** to this group only (including subgroups):

| Group Path | Description |
|------------|-------------|
| `cit-iaas/cid` | CIT IaaS Cloud Infrastructure Delivery group |

All scripts validate the group path and will refuse operations on groups outside this list.

## Authentication Setup

Set the environment variable before using any operations:

```bash
export GITLAB_API_TOKEN="your-personal-access-token"
```

To get a PAT:
1. Log in to GitLab at https://gitlab.devops.telekom.de/
2. Go to User Settings > Access Tokens
3. Create a token with `read_api` scope

## Operations

All scripts are Python-based and should be run with the project venv:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/<script>.py [arguments]
```

### List Epics

List epics from the CID group (includes subgroups):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py [options]
```

Options:
- `--state STATE` - Filter by state: `opened` (default), `closed`, `all`
- `--labels LABELS` - Filter by comma-separated labels
- `--author USERNAME` - Filter by author username
- `--search TEXT` - Search in title and description
- `--country COUNTRIES` - Filter by country codes or names (comma-separated)
- `--subgroup NAME` - Filter to specific subgroup: `nitrogen`, `dc-devops`, `gangs`, `cit-product-management`, `test-ccp-nexus`, `kawappa-environments`, `ldap-components`, or `parent` for cid only
- `--updated-after DATE` - Only epics updated after this date (ISO format)
- `--created-after DATE` - Only epics created after this date (ISO format)
- `--sort-by FIELD` - Sort results by: `due_date`, `created_at`, `updated_at`, `title`
- `--format FORMAT` - Output format: `table` (default), `json`
- `--verbose` - Show enhanced output with squad, location, status columns
- `--show-hierarchy` - Show parent/child epic relationships in output
- `--umbrella-only` - Show only umbrella (parent) epics that have children
- `--standalone-only` - Show only standalone epics (no parent, no children)
- `--limit N` - Maximum results (default: 50)

Examples:
```bash
# List all open epics (from all subgroups)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py

# List epics from nitrogen subgroup only
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --subgroup nitrogen

# List epics from parent group only (excluding subgroups)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --subgroup parent --limit 300

# List epics from dc-devops subgroup
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --subgroup dc-devops --state all

# Filter by labels
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "status::in-progress"

# Filter by country (Slovakia)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country SK --verbose

# Filter by multiple countries
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country "Slovakia,Hungary" --sort-by due_date

# Sort by due date with verbose output
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --sort-by due_date --verbose --limit 100

# Search for specific deployment
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --search "AMS datacenter"

# Filter by assignee/delivery manager (partial name search)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --assignee "Angel"

# Filter by assignee with username
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --assignee "angel.vivas-vivas"

# Combine filters: assignee + country + state
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --assignee "Angel" --country SK --state opened

# Get JSON output with verbose fields
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --format json --verbose --limit 100

# List only umbrella (parent) epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --umbrella-only --verbose

# List with hierarchy column showing parent/child relationships
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --show-hierarchy --limit 100

# List standalone epics (no parent, no children)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --standalone-only
```

**Country Filter**: The `--country` option matches epics by:
1. **Title patterns** - City codes in epic titles (e.g., "skbra" for Bratislava)
2. **Label patterns** - Environment labels like `E - IC-SK*`, `E - SC-SK*`, `E - HC-SK*`

**Assignee Filter**: The `--assignee` option searches for users within the CID group and filters epics by delivery manager:
- Supports partial name search (e.g., "Angel" matches "Angel Vivas-Vivas")
- Searches only CID group members
- If multiple users match, prompts for selection
- Parses epic descriptions for "Delivery manager: @username" pattern

Output shows: IID, Title, State, Start Date, Due Date, Labels (or Squad, Location, Status in verbose mode)

### Get Epic Details

Get detailed information about a specific epic:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-get-epic.py <epic-iid> [options]
```

Arguments:
- `epic_iid` (positional) - Epic IID number

Options:
- `--format FORMAT` - Output format: `detailed` (default), `json`

Examples:
```bash
# Get epic details
.venv/bin/python ${SKILL_DIR}/scripts/cid-get-epic.py 42

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/cid-get-epic.py 42 --format json
```

Output includes:
- Title, state, confidential status
- Start and due dates
- Author
- Labels
- Description
- Progress (issues count, completed)
- Web URL

### List Epic Issues

List all issues linked to an epic:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-epic-issues.py <epic-iid> [options]
```

Arguments:
- `epic_iid` (positional) - Epic IID number

Options:
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 100)

Examples:
```bash
# List issues for an epic
.venv/bin/python ${SKILL_DIR}/scripts/cid-epic-issues.py 42

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/cid-epic-issues.py 42 --format json
```

Output shows: IID, Project, Title, State, Assignee, Labels, Due Date

### List Issues

List issues from the CID group (includes subgroups):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py [options]
```

Options:
- `--state STATE` - Filter by state: `opened` (default), `closed`, `all`
- `--labels LABELS` - Filter by comma-separated labels
- `--squad NAME` - Filter by squad shorthand (e.g., `CaaS`, `CDM`, `DC`, `Networks`)
- `--assignee NAME` - Filter by assignee (supports partial name search)
- `--author USERNAME` - Filter by author username
- `--search TEXT` - Search in title and description
- `--country COUNTRIES` - Filter by country codes or names (comma-separated)
- `--subgroup NAME` - Filter to specific subgroup: `nitrogen`, `dc-devops`, `gangs`, etc.
- `--updated-after DATE` - Only issues updated after this date (ISO format)
- `--created-after DATE` - Only issues created after this date (ISO format)
- `--sort-by FIELD` - Sort results by: `due_date`, `created_at`, `updated_at`, `title`
- `--format FORMAT` - Output format: `table` (default), `json`
- `--verbose` - Show enhanced output with squad, location columns
- `--limit N` - Maximum results (default: 50)

Examples:
```bash
# List all open issues
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py

# Filter by squad shorthand (expands to label "A - CaaS_squad")
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --squad CaaS

# Filter by squad with verbose output
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --squad CaaS --verbose

# Filter by country
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --country SK --verbose

# Filter by assignee (partial name search)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --assignee "Angel"

# Combine filters: squad + country + state
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --squad CaaS --country CZ --state all

# Filter by subgroup
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --subgroup gangs --squad Networks

# Sort by due date with limit
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --squad CaaS --sort-by due_date --limit 100

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-issues.py --squad CDM --format json --verbose
```

**Squad Shorthand**: `--squad CaaS` expands to label `A - CaaS_squad`. Can be combined with `--labels` for additional label filters.

**Country Filter**: Matches issues by title patterns (city codes) and environment labels, same as epic filtering.

Output shows: IID, Project, Title, State, Assignee, Due Date (or Squad, Location in verbose mode)

### List Labels

List all labels in the CID group to discover label conventions:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-labels.py [options]
```

Options:
- `--search TEXT` - Filter labels by name
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 100)

Examples:
```bash
# List all labels
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-labels.py

# Search for status labels
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-labels.py --search "status"

# Search for DC-related labels
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-labels.py --search "DC"
```

Output shows: Name, Color, Description

### Generate Deployment Report

Generate a PDF report of deployment status from epics and issues:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-deployment-report.py [options]
```

Options:
- `--state STATE` - Epic state filter: `opened` (default), `closed`, `all`
- `--labels LABELS` - Filter epics by comma-separated labels
- `--output PATH` - Output PDF path (default: `deployment-report-YYYY-MM-DD.pdf`)
- `--title TITLE` - Report title (default: "TDI Cloud Delivery Status Report")

Examples:
```bash
# Generate report for all open epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-deployment-report.py

# Generate report for specific labels
.venv/bin/python ${SKILL_DIR}/scripts/cid-deployment-report.py --labels "priority::high"

# Custom output path
.venv/bin/python ${SKILL_DIR}/scripts/cid-deployment-report.py --output reports/dc-status.pdf
```

### Generate Full Squad Report

Generate a comprehensive Markdown and PDF report for one or more squads:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py [options]
```

Options:
- `--squad LABELS` - Squad label(s) to filter by, comma-separated (default: `A - CDM_squad`)
- `--output PATH` - Output file path without extension (auto-generated from squad names if not specified)
- `--title TITLE` - Report title (auto-generated if not specified)
- `--limit N` - Maximum epics to fetch (default: 500)

Examples:
```bash
# Generate report for CDM squad (default)
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py

# Generate report for CaaS squad
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py --squad "A - CaaS_squad"

# Generate multi-squad report
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py --squad "A - CDM_squad,A - CaaS_squad"

# Generate report for Networks squad with custom output
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py --squad "A - Networks_squad" --output reports/networks-report

# Custom title
.venv/bin/python ${SKILL_DIR}/scripts/cid-full-report.py --squad "A - DC_squad" --title "DC Infrastructure Status"
```

**Output Files:**
- Markdown report: `reports/cid-<squad>-report-YYYY-MM-DD.md`
- PDF report (landscape A4): `reports/cid-<squad>-report-YYYY-MM-DD.pdf`

**Report Contents:**
- Executive Summary with total epic count
- Key Metrics (due dates, overdue, squad coverage, hierarchy)
- Epic Status Distribution
- Squad Workload breakdown
- Epic Hierarchy (umbrella epics with children)
- Overdue Epics table (with assignee)
- Due This Month table (with assignee)
- Epics In Progress table (with assignee)
- Complete Epic List (with assignee)
- Analysis & Recommendations

## Cross-Skill Operations

The following operations are **not provided by this skill** — use the **GitLab skill** instead. The GitLab skill supports the `cit-iaas/cid` group (and its subgroups/projects).

| Need | GitLab Skill Script | Example |
|------|---------------------|---------|
| Get issue details | `gitlab-get-issue.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-get-issue.py cit-iaas/cid/caas-devops 124` |
| Get issue comments | `gitlab-get-issue-comments.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-get-issue-comments.py cit-iaas/cid/caas-devops 124` |
| List issues (generic, no CID filters) | `gitlab-list-issues.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-list-issues.py cit-iaas/cid --labels "A - CaaS_squad"` |
| List epics (generic, no CID filters) | `gitlab-list-epics.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-list-epics.py cit-iaas/cid --limit 20` |
| Get epic details (generic) | `gitlab-get-epic.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-get-epic.py cit-iaas/cid 42` |
| List epic issues (generic) | `gitlab-epic-issues.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-epic-issues.py cit-iaas/cid 922` |
| List labels (generic) | `gitlab-list-labels.py` | `.venv/bin/python ${GITLAB_SKILL_DIR}/scripts/gitlab-list-labels.py cit-iaas/cid --search "status"` |

**When to use which skill:**
- Use **this skill** (cloud-delivery) when you need CID-specific features: `--country`, `--squad` (shorthand), `--subgroup`, `--assignee` (delivery manager for epics), `--umbrella-only`, `--show-hierarchy`, `--verbose` (squad/location columns), or deployment/squad reports
- Use the **GitLab skill** when you need generic operations: issue details, issue comments, simple issue/epic listing without CID filters, or label discovery

## Epic Hierarchy

The CID group uses epic hierarchy: parent (umbrella) epics contain child epics.

| Type | Description |
|------|-------------|
| **Umbrella Epic** | Parent epic with one or more children |
| **Child Epic** | Epic belonging to a parent |
| **Standalone Epic** | Independent epic (no parent, no children) |

Use `--umbrella-only`, `--standalone-only`, or `--show-hierarchy` flags with `cid-list-epics.py` to filter/display hierarchy. The `cid-get-epic.py` script shows parent/children info in detail view.

## Label Convention Reference

See [references/label-conventions.md](references/label-conventions.md) for the complete label reference.

| Category | Example Labels |
|----------|----------------|
| Squad | `A - CDM_squad`, `A - DC_squad`, `A - CaaS_squad` |
| Epic Status | `B - epic::Doing`, `B - epic::ToDo`, `B - epic::Backlog` |
| Priority | `D - 2 - high`, `D - 3 - medium` |
| Work Type | `I - DESIGN`, `I - ORDER & PROCURE`, `I - SITE READINESS` |

## Group Structure

```
cit-iaas/cid/
├── gangs/                    # Cross-functional working groups
│   ├── networks              # Network team (issues linked to epics)
│   ├── boron-gang            # Boron release gang
│   ├── gpu-integration       # GPU integration work
│   ├── k8s-integration       # Kubernetes integration
│   ├── monitoring-checks-lifecycle
│   ├── validation-and-testing
│   └── ...
├── dc-devops/                # DC DevOps automation
├── nitrogen/                 # Nitrogen release
├── kawappa-environments/     # Kawappa environments
├── squad-monitoring          # Monitoring squad project
├── squad-security            # Security squad project
├── squad-onboarding          # Onboarding squad project
├── beryllium                 # Beryllium release
├── magenta                   # Magenta project
├── overlay-*                 # Overlay network projects
├── underlay-*                # Underlay network projects
└── ...
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `GITLAB_API_TOKEN not set` | Missing env variable | Export the token: `export GITLAB_API_TOKEN="..."` |
| `Connection refused` | Not on VPN | Connect to Telekom VPN |
| `404 Not Found` | Invalid epic IID | Verify the epic exists in cit-iaas/cid |
| `403 Forbidden` | Insufficient permissions | Ensure PAT has `read_api` scope |

## Useful Queries

See [references/useful-queries.md](references/useful-queries.md) for common query patterns (by status, squad, country, work category, assignee).

## Additional Resources

- [references/useful-queries.md](references/useful-queries.md) - Common query patterns by status, squad, country, work category
- [references/api-reference.md](references/api-reference.md) - GitLab Epics API reference
- [references/label-conventions.md](references/label-conventions.md) - Complete label convention reference
