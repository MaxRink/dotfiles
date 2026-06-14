---
name: tdi-cloudbrain-tdi-cloud-delivery
user-invocable: true
description: This skill should be used when the user mentions "TDI cloud delivery", "DC deployment", "datacenter deployment", "datacenter extension", "CID epics", "cit-iaas", "deployment status", "cloud infrastructure delivery", or needs to track TDI internal planning for datacenter deployments and extensions from the GitLab CID group.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/tdi-cloud-delivery by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TDI Cloud Delivery

This skill provides tools to track TDI internal planning for datacenter (DC) deployments and extensions using GitLab epics from the CIT-IaaS CID group.

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

## Session Learnings

- **Label conventions**: Use `cid-list-labels.py` to discover existing label patterns (e.g., `status::`, `DC::`, `priority::`)
- **Include subgroups**: All operations include subgroups by default to capture the full project hierarchy
- **Epic progress**: The `cid-get-epic.py` script shows issue counts to track completion status
- **Epic hierarchy**: Epics can have parent-child relationships. Use `--show-hierarchy` to visualize these relationships

## Epic Hierarchy (Umbrella Epics)

The CID group uses **epic hierarchy** to organize related work items. Parent epics (called "umbrella epics") can contain child epics, creating a two-level structure.

### Hierarchy Types

| Type | Description |
|------|-------------|
| **Umbrella Epic** | A parent epic that has one or more child epics |
| **Child Epic** | An epic that belongs to a parent umbrella epic |
| **Standalone Epic** | An independent epic with no parent and no children |

### Current Statistics (as of 2026-02)

- **~31 umbrella epics** contain **~77 child epics**
- **~170+ standalone epics** operate independently
- No multi-level hierarchy (grandparent-parent-child) exists

### Examples of Umbrella Epics

**Large Umbrella Epics (6+ children):**
- `PM bucket Q2-2023` - Groups Nitrogen-related work items
- `[PD0002] Problem Definition: TRANSPARENCY - DOCUMENTATION` - Documentation initiatives
- `INIT07-EPIC08: STORAGE as a Service` - STaaS implementation epics

**Topic-Specific Umbrellas:**
- `INIT02-EPIC30 Jarosova environment - PODs build` - POD1 and POD2 child epics
- `[TMCZ/SK 5G SA go life] Testing support` - SK/CZ testing epics
- `INIT34: New IaaS release - Nitrogen` - Nitrogen release work

### Using Hierarchy Features

**List only umbrella epics:**
```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --umbrella-only --verbose
```

**Show hierarchy column in output:**
```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --show-hierarchy --limit 100
```

**Get epic with hierarchy info:**
```bash
.venv/bin/python ${SKILL_DIR}/scripts/cid-get-epic.py 7  # Shows children if umbrella
.venv/bin/python ${SKILL_DIR}/scripts/cid-get-epic.py 19  # Shows parent if child
```

**JSON output includes hierarchy fields:**
```json
{
  "iid": 7,
  "title": "PM bucket Q2-2023",
  "hierarchy_type": "umbrella",
  "child_count": 7,
  "child_iids": [13, 14, 15, 16, 17, 18, 19]
}
```

### Full Report Hierarchy Section

The `cid-full-report.py` generates a comprehensive report including:
- **Hierarchy summary** in Key Metrics (umbrella/child/standalone counts)
- **Epic Hierarchy section** listing all umbrella epics with their children
- **PDF version** with umbrella epics overview table

## Label Convention Reference

The CID group uses a structured label system. See [references/label-conventions.md](references/label-conventions.md) for the complete label reference including:

- **A - Squad Assignment** (team ownership labels)
- **B - Epic Status & Ownership** (lifecycle and owner labels)
- **C - Issue Status** (issue workflow labels)
- **D - Priority** (priority levels)
- **E - Environment/Datacenter** (location labels)
- **I - DC Squad Work Categories** (work type labels)
- **Numbered Workflow Labels** (procurement process tracking)

### Quick Reference - Common Labels

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

### By Epic Status
```bash
# Epics currently in implementation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::Doing"

# Epics ready for sprint planning
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::ToDo"

# Epics in design/sizing phase
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::Refinement"
```

### By Squad
```bash
# DC Infrastructure squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - DC_squad"

# Networks squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - Networks_squad"

# CDM squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - CDM_squad"
```

### By Datacenter/Environment
```bash
# Slovakia deployments (all locations)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country SK --verbose --sort-by due_date

# Hungary deployments
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country Hungary --verbose

# Multiple countries (Slovakia and Hungary)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country "SK,HU" --verbose --sort-by due_date

# Specific environment label
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "E - IC-ATVIEF1"

# Search by city name
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --search "Budapest"
```

### By Work Category
```bash
# Design work
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - DESIGN"

# Ordering/procurement
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - ORDER & PROCURE"

# Hardware installation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - SITE READINESS"
```

### Combining Filters
```bash
# DC squad epics in implementation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - DC_squad,B - epic::Doing"

# High priority epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "D - 2 - high"
```

## Additional Resources

For detailed API documentation, see:
- [references/api-reference.md](references/api-reference.md) - GitLab Epics API reference
- [references/label-conventions.md](references/label-conventions.md) - Complete label convention reference
