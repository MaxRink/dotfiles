---
name: dt-brain-shared-caas-ddu
description: This skill should be used when the user mentions "ddu", "cluster", "kubernetes", "cluster check", "cluster status", "cluster report", "cluster info", asks about cluster passwords, secrets, or needs to check Kubernetes cluster status in the CaaS infrastructure.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-ddu by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# DDU Integration

This skill provides tools to interact with the DDU internal tool for Kubernetes cluster status checking, information gathering, and password retrieval.

## CaaS Product Version → Kubernetes Version Mapping

The **major version of the CaaS product equals the minor version of Kubernetes**:

- CaaS product `32.x.y` → Kubernetes `1.32.x`
- CaaS product `33.x.y` → Kubernetes `1.33.x`
- CaaS product `34.x.y` → Kubernetes `1.34.x`

When asked about the Kubernetes version of a cluster, the CaaS product version from DDU is sufficient — no need to query NetBox separately.

## Instance Details

- **Base URL**: `https://ddu.caas.in.pan-net.eu`
- **Authentication**: API Token via `X-API-TOKEN` header
- **VPN Required**: Yes - API access only works when connected to Telekom VPN

## Authentication Setup

Set the environment variable before using any DDU operations:

```bash
export DDU_API_TOKEN="your-api-token"
```

## Operations

### Check Cluster Status

Check the health status of a Kubernetes cluster:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/ddu-check.py <cluster-name>
```

Examples:
```bash
# Check status of a specific cluster
.venv/bin/python ${SKILL_DIR}/scripts/ddu-check.py hrzagt5-skynet-dev
```

Output includes: cluster info, reconciliation status, alerts, node status, and pod health.

### Get Cluster Secrets

Retrieve passwords and secrets for a Kubernetes cluster:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py <cluster-name> [OPTIONS]
```

Options:
- `--field, -f FIELD` - Extract a specific field value (e.g., `GRAFANA_ADMIN_PASSWORD`)
- `--json` - Output raw JSON response

**Available secrets:**

| Secret | Description |
|--------|-------------|
| `GRAFANA_ADMIN_PASSWORD` | Admin password for Grafana dashboard |
| `PROMETHEUS_PASSWORD` | Password for Prometheus access |
| `AUTOMATION_KUBECONFIG` | Kubeconfig for automation/CI pipelines |
| `CUSTOMER_KUBECONFIG` | Kubeconfig for customer access |
| `OIDC_KUBECONFIG` | Kubeconfig with OIDC authentication |
| `OPENRC` | OpenStack credentials file (only for clusters running on OpenStack VMs) |
| `CLUSTER_NAME` | Name of the cluster |
| `PARENT` | Parent management cluster |

Examples:
```bash
# Get all secrets for a cluster
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py hrzagt5-skynet-dev

# Get only the Grafana password
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py hrzagt5-skynet-dev --field GRAFANA_ADMIN_PASSWORD

# Get the Prometheus password
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py hrzagt5-skynet-dev -f PROMETHEUS_PASSWORD

# Get raw JSON output
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py hrzagt5-skynet-dev --json
```

### Get Cluster Report

Get a detailed report for a specific Kubernetes cluster:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py <cluster-name> [OPTIONS]
```

Options:
- `--json` - Output raw JSON response
- `--field FIELD [FIELD ...]` - Extract specific field(s) from the report (case-insensitive, also searches nested CC_JSON)

Examples:
```bash
# Get report for a specific cluster
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py hrzagt5-skynet-dev

# Get raw JSON output
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py hrzagt5-skynet-dev --json

# Quick owner lookup
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py hrzagt5-skynet-dev --field owner owner_mail

# Get multiple fields at once
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py hrzagt5-skynet-dev --field owner dc version juice_group
```

### Get All Clusters Report

Get a report for all Kubernetes clusters:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py [OPTIONS]
```

Options:
- `--json` - Output raw JSON response
- `--filter, -f FIELD=PATTERN` - Filter clusters by field (regex, case-insensitive). Can be used multiple times.
- `--count, -c` - Only output count of matching clusters

Examples:
```bash
# Get report for all clusters
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py

# Get raw JSON output
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --json
```

### Search and Filter Clusters

The all clusters report now has built-in filtering support:

```bash
# Find clusters by name pattern (e.g., all TUPL clusters)
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter name=tupl

# Find clusters by owner/group
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter group=TDI

# Find clusters by datacenter
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter dc=atgraf

# Multiple filters (AND logic)
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter group=TDI --filter dc=atgraf

# Count clusters matching a pattern
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter name=tupl --count

# Find clusters by product version
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter version=33.1

# Get filtered results as JSON
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter group=AT --json
```

**Available filter fields:**
| Field | Description |
|-------|-------------|
| `name` | Cluster name |
| `dc` | Datacenter location |
| `group` | Owner group (AT, TDI, etc.) |
| `juice_group` | Juice group for the cluster |
| `owner` | Owner name |
| `version` | Product version |
| `parent` | Parent management cluster |
| `product_type` | Type (customer-cluster, etc.) |
| `type` | Infrastructure type (openstack, etc.) |

## Common Use Cases

### Quick Cluster Health Check
```bash
# Check if a cluster is healthy
.venv/bin/python ${SKILL_DIR}/scripts/ddu-check.py hrzagt5-skynet-dev

# Get cluster report for troubleshooting
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report.py hrzagt5-skynet-dev
```

### Retrieve Cluster Credentials
```bash
# Get passwords for a cluster
.venv/bin/python ${SKILL_DIR}/scripts/ddu-secrets.py hrzagt5-skynet-dev
```

### Infrastructure Overview
```bash
# Get status of all clusters
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py

# Count all TDI clusters
.venv/bin/python ${SKILL_DIR}/scripts/ddu-report-all.py --filter group=TDI --count
```

## Additional Resources

For detailed API documentation including error codes and raw curl examples, see [references/api-reference.md](references/api-reference.md).

## Security Notes

1. **Token Storage**: Never commit DDU_API_TOKEN to version control
2. **VPN Required**: Operations only work when connected to Telekom VPN
3. **Sensitive Data**: Secrets endpoint returns sensitive credentials - handle with care
4. **Audit**: API calls may be logged
