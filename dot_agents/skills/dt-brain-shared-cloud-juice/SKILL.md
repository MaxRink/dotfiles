---
name: dt-brain-shared-cloud-juice
description: Interact with JUICE — the in-house service for application onboarding, capacity management, and resource allocation on pan-net cloud environments. Use when the user mentions "JUICE", "juice-group", "juice group", "capacity", "cloud capacity", "quota", "quotas", "total quotas", "capacity check", "cloud stats", "group stats", "project stats", "reservation", "allocated capacity", "available capacity", asks about cloud resource usage, onboarding, or needs to query capacity and quota information for OpenStack clouds managed via JUICE.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-juice by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# JUICE Integration

JUICE is a microservice-based platform that manages application onboarding on cloud environments and tracks reservations and allocated capacities.

## Key Concepts

- **juice-group**: Identifies an application — serves as the parent container. Cloud resources (OpenStack Domains, OpenStack Projects, cloud instances, NetBox objects) are assigned to a juice-group. Users of a juice-group have access to these assigned resources.
- **Roles**:
  - `admin` — read/write on all groups; sets access, limits, quotas for juice-groups in clouds and inventory (NetBox)
  - `admin-read-only` — can read all data from/via JUICE but cannot write
  - `user` — access only to resources configured by admins for their assigned juice-groups
- **Product types**: `compute`, `caas`, `caasbm`, `baremetal`

## Quick Start

1. Add JUICE credentials to the project root `.env` file:
   ```bash
   export JUICE_USERNAME=your-username
   export JUICE_PASSWORD=your-password
   export JUICE_GROUP=your-default-juice-group
   export JUICE_CACERT=~/path/to/ca-cert.crt
   ```
2. Connect to Telekom VPN
3. Run scripts:
   ```bash
   source .env && .venv/bin/python ${SKILL_DIR}/scripts/<script>.py [options]
   ```

The `JUICE_GROUP` env var provides the default auth scope. It can be overridden per-command with `--juice-group`.
The `JUICE_CACERT` env var points to a CA certificate for SSL verification. If not set, SSL verification is disabled.

## Instance Details

- **Prod URL**: `https://prod.juice.in.pan-net.eu`
- **Stage URL**: `https://stage.juice.in.pan-net.eu`
- **VPN Required**: Yes
- **Authentication**: HTTP Basic → scoped JWT Bearer token via `/v2/auth/local/token/{juice_group}`

## Auth Flow

All scripts use `juice_common.py` which handles authentication automatically:
1. Basic auth with JUICE_USERNAME / JUICE_PASSWORD to get a scoped JWT
2. JWT is cached for the session and passed as Bearer token to subsequent API calls
3. The token is scoped to a juice-group, which determines what resources are visible

## Operations

### List JUICE Groups

List juice-groups accessible to the current user:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/juice-list-groups.py
```

Options:
- `--juice-group GROUP` — JUICE group for auth scope (default: `JUICE_GROUP` env var)
- `--product-type TYPE` — Filter by product type: `compute`, `caas`, `caasbm`, `baremetal`
- `--format FORMAT` — Output format: `table` (default), `json`
- `--limit N` — Max results (default: 1000)
- `--env ENV` — JUICE environment: `prod` (default), `stage`

Examples:
```bash
# List all accessible groups (uses JUICE_GROUP from .env)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-list-groups.py

# List only CaaS groups
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-list-groups.py --product-type caas

# Override auth scope with a different group
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-list-groups.py --juice-group other-group
```

Output shows: Name, Product Type, OS Domain, State, Tags, Description

### Cloud Capacity — Total Quotas

Get hypervisor capacity and usage for an OpenStack cloud (with JUICE-calculated sellable data):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-total-quotas.py <cloud_name>
```

Options:
- `--juice-group GROUP` — JUICE group for auth scope (default: `JUICE_GROUP` env var)
- `--compute-type TYPE` — Filter: `shared`, `shared-local`, `dedicated`, `dedicated-local`
- `--hw-version VER` — Filter by hardware version
- `--consumer NAME` — Filter by consumer
- `--show-hosts` — Include per-host details
- `--format FORMAT` — Output: `table` (default), `json`
- `--env ENV` — JUICE environment: `prod` (default), `stage`

Examples:
```bash
# Get total quotas for a cloud
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-total-quotas.py cloudname

# Filter by compute type
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-total-quotas.py cloudname --compute-type dedicated

# Show per-host breakdown
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-total-quotas.py cloudname --show-hosts
```

Output shows: Total vCPU/RAM/Disk capacity, current usage, and availability broken down by compute type (shared/dedicated).

### Cloud Capacity — Statistics

Get reservation/quota statistics stored in the JUICE capacity database at cloud, group, or project level:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-stats.py <level>
```

Where `<level>` is one of: `cloud`, `group`, `project`

Options:
- `--juice-group GROUP` — JUICE group for auth scope (default: `JUICE_GROUP` env var)
- `--cloud CLOUD` — Filter by cloud name/id
- `--group GROUP` — Filter by juice-group name (admin only)
- `--list-all` — List all entries (admin only)
- `--quota QUOTA` — Filter: `cores`, `ram`, `gigabytes`, `object-megabytes`, `floatingips`
- `--quota-group QGROUP` — Filter: `compute`, `volume`, `network`
- `--format FORMAT` — Output: `table` (default), `json`
- `--env ENV` — JUICE environment: `prod` (default), `stage`

Examples:
```bash
# Cloud-level stats (total vs allocated)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-stats.py cloud

# Group-level stats for a specific group on a cloud
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-stats.py group --cloud cloudname --group targetgroup

# Project-level stats (used vs allocated)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-stats.py project --cloud cloudname

# Filter to compute quotas only
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-stats.py cloud --quota-group compute
```

**Stats hierarchy**:
- **Cloud level**: total capacity vs what's allocated to groups
- **Group level**: what's allowed (quota limits) vs what's allocated to projects
- **Project level**: what's allocated vs what's actually used

### Cloud Capacity — Check Availability

Check if requested resources are available in a cloud:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-check.py <cloud_name>
```

Options:
- `--juice-group GROUP` — JUICE group for auth scope (default: `JUICE_GROUP` env var)
- `--cores N` — Requested CPU cores
- `--ram N` — Requested RAM in MB
- `--gigabytes N` — Requested volume storage in GB
- `--floatingip N` — Requested floating IPs
- `--env ENV` — JUICE environment: `prod` (default), `stage`

Example:
```bash
# Check if 32 cores and 64GB RAM are available
source .env && .venv/bin/python ${SKILL_DIR}/scripts/juice-capacity-check.py cloudname --cores 32 --ram 65536
```

Output: Boolean per resource type (available: yes/no)
