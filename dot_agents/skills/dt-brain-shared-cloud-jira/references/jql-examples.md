# JQL Query Examples for Telekom Jira

Ready-to-use JQL queries for allowed projects (CAASPROD, TCAAS, ONB).

## Table of Contents

- [Basic Queries](#basic-queries)
- [By Status / Assignee / Labels](#by-status--assignee--labels)
- [By Date and Custom Fields](#by-date-and-custom-fields)
- [By Issue Type and Fix Version](#by-issue-type-and-fix-version)
- [Epic Queries](#epic-queries)
- [Combined Queries](#combined-queries)
- [Label Audit Queries](#label-audit-queries)
- [ONB Service Desk Queries](#onb-service-desk-queries)
- [Shell Escaping Gotchas](#shell-escaping-gotchas)
- [Assignee Lookup](#assignee-lookup)

## Basic Queries

```jql
project = TCAAS
project IN (CAASPROD, TCAAS)
project = TCAAS AND status not in (Closed, Done)
```

## By Status / Assignee / Labels

```jql
project = TCAAS AND status = "In Progress"
project IN (CAASPROD, TCAAS) AND assignee = currentUser()
project = TCAAS AND assignee IS EMPTY
project = TCAAS AND labels = "tdi-caas-convergence"
project = CAASPROD AND labels IN ("tdi-caas-operations", "tdi-caas-development")
```

## By Date and Custom Fields

```jql
project = TCAAS AND created >= startOfWeek()
project IN (CAASPROD, TCAAS) AND updated >= -7d
project = TCAAS AND "Target start" IS NOT EMPTY
project = TCAAS AND "Target start" >= "2025-02-01" AND "Target start" <= "2025-02-28"
project IN (CAASPROD, TCAAS) AND duedate < now() AND status not in (Done, Closed)
```

## By Issue Type and Fix Version

```jql
project = TCAAS AND issuetype = Task
project IN (CAASPROD, TCAAS) AND issuetype = Bug
project = TCAAS AND issuetype IN (Story, Task)
project = TCAAS AND fixVersion = "25.12"
project = TCAAS AND fixVersion IS EMPTY AND status not in (Closed, Done)
```

## Epic Queries

```jql
project = CAASPROD AND issuetype = Epic AND status not in (Closed, Done)
project = TCAAS AND "Epic Link" = "TCAAS-100"
project = TCAAS AND "Epic Link" IS EMPTY AND issuetype not in (Epic)
```

## Combined Queries

```jql
# My open convergence tasks
project = TCAAS AND assignee = currentUser() AND labels = "tdi-caas-convergence" AND status not in (Done, Closed)

# Recently updated tasks
project IN (CAASPROD, TCAAS) AND assignee = currentUser() AND updated >= -3d ORDER BY updated DESC

# Convergence work without target dates
project = TCAAS AND labels = "tdi-caas-convergence" AND "Target start" IS EMPTY AND status not in (Done, Closed)
```

## Label Audit Queries

```jql
# CAASPROD tasks missing required ops/dev label (non-Epic)
project = CAASPROD AND status in (Refined, "In Progress") AND type not in (Epic) AND (labels is EMPTY OR labels not in (tdi-caas-operations, tdi-caas-development))

# All CAASPROD operations tasks
project = CAASPROD AND labels = tdi-caas-operations AND status not in (Closed, Done)

# All CAASPROD development tasks
project = CAASPROD AND labels = tdi-caas-development AND status not in (Closed, Done)
```

## ONB Service Desk Queries

ONB is a shared project. Scope to CaaS-relevant tickets using Assignee Group:

```jql
# Recommended — uses Assignee Group (most reliable)
project = ONB AND "Assignee Group" = "gard_team_ CaaS" AND status not in (Resolved, Closed, Canceled, Cancelled, Done)

# Alternative — using CaaS label (may miss tickets)
project = ONB AND labels = CaaS AND resolution = Unresolved
```

Full queue filter (matches https://jira.telekom.de/projects/ONB/queues/custom/6001):

```jql
(issuetype in ("Add Project", "Service Request")
  AND resolution = Unresolved
  AND status != Resolved
  AND labels = CaaS
  AND "Customer Request Type" in (
    "Destroy an existing cluster (ONB)",
    "New Request for a CaaS Cluster (ONB)",
    "Scale an existing cluster (ONB)",
    "CaaS Cluster Upgrade Request (ONB)"
  )
) OR (
  "Assignee Group" = "gard_team_ CaaS"
  AND status not in (
    Resolved, "Resolved, to be accepted", "Resolved - to validate",
    Closed, "Closed / Done", "Closed by customer",
    Canceled, Cancel, Cancelled, "Cancellation requested"
  )
)
```

## Shell Escaping Gotchas

Use **single quotes** for JQL and **`not in`** instead of `!=` (bash interprets `!` as history expansion):

```bash
# WRONG — causes escape errors
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py "project = TCAAS AND status != Closed"

# CORRECT
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = TCAAS AND status not in (Closed, Done)'
```

## Assignee Lookup

The `assignee` field does NOT support the `~` (contains) operator. Use `=` with the **full display name** in double quotes:

```bash
# Correct — full display name
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = TCAAS AND assignee = "Christos Ntogkas"'

# WRONG — ~ not supported for assignee
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = TCAAS AND assignee ~ Christos'
```

To find a full name from a partial name, use text search:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/jira-search.py 'project = TCAAS AND text ~ "Christos"' --max 5
```

**For `--assignee` flag** (create/update), use the **username (email)**, not display name:
```bash
# Best: search users directly by name/email fragment
.venv/bin/python ${SKILL_DIR}/scripts/jira-user-search.py "joan.romero"
# Output: joan.romero-chaparro@t-systems.com   JOAN ROMERO CHAPARRO

# Fallback: find username from a known ticket
.venv/bin/python ${SKILL_DIR}/scripts/jira-get.py CAASPROD-1640 --format json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['fields']['assignee']['name'])"
# Example: display name "ISMAEL ESTEBAN VICENTE" → username "ismael.esteban-vicente@t-systems.com"
```
