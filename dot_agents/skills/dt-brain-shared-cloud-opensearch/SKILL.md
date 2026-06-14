---
name: dt-brain-shared-cloud-opensearch
description: This skill should be used when the user mentions "OpenSearch", "logs", "log search", "search logs", "log query", "elasticsearch", "kibana", "dashboards", "investigate cluster", "investigate alert", "cluster investigation", or needs to search and query logs from the CaaS infrastructure logging system.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-opensearch by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# OpenSearch Integration

This skill provides tools to search and query logs from the CaaS infrastructure OpenSearch instance.

## Instance Details

- **Dashboards URL**: `https://infra-os-prod-dashboards.infra-mon.in.pan-net.eu/`
- **Tenant**: `caas-tenant`
- **Index Pattern**: `caas-*,*-caas-*,tcaas-*`
- **Authentication**: IDP-integrated (requires session cookie or API token)
- **VPN Required**: Yes - API access only works when connected to Telekom VPN

## Authentication Setup

Set the following environment variables before using OpenSearch operations:

```bash
# Recommended: Username/Password (basic auth)
export OPENSEARCH_USER="your-username"
export OPENSEARCH_PASSWORD="your-password"
```

Alternative authentication methods (if basic auth doesn't work):

```bash
# Option 2: API Token (if available)
export OPENSEARCH_API_TOKEN="your-api-token"

# Option 3: Session cookie from browser (for IDP auth)
export OPENSEARCH_SESSION_COOKIE="security_authentication=..."
```

### Getting a Session Cookie (IDP Authentication)

If the OpenSearch instance uses IDP authentication:

1. Log in to OpenSearch Dashboards at https://infra-os-prod-dashboards.infra-mon.in.pan-net.eu/
2. Switch to "caas-tenant" in the tenant selector
3. Open browser DevTools (F12) → Application → Cookies
4. Copy the `security_authentication` cookie value
5. Set the environment variable:
   ```bash
   export OPENSEARCH_SESSION_COOKIE="security_authentication=<cookie-value>"
   ```

## Known Limitations

- **Only `kube-system` logs**: Pod logs are typically only indexed for the `kube-system` namespace. Other namespaces (e.g., flux-system, application namespaces) are not available in OpenSearch.
- **Greek clusters (ote-*)**: Logs from Greek clusters are not available in this OpenSearch instance
- **Polish clusters (pl-*)**: Logs from Polish clusters are not available in this OpenSearch instance
- **Log retention**: Logs are retained for a limited period; older incidents may have no available logs

## Operations

### Search Logs

Search logs with time range and cluster filtering:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py [options]
```

Options:
- `--cluster, -c` - Filter by cluster name (partial match supported)
- `--from, -f` - Start time (ISO 8601 or relative: "1h", "30m", "2d")
- `--to, -t` - End time (ISO 8601, default: now)
- `--query, -q` - Free text search query
- `--level, -l` - Filter by log level (error, warn, info, debug)
- `--limit, -n` - Maximum results (default: 100)
- `--format` - Output format: `table` (default), `json`

Examples:
```bash
# Search last hour of logs for a cluster
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py --cluster atgraf1-ndl-prod --from 1h

# Search specific time range (from PagerDuty incident)
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from "2026-02-05T10:00:00Z" \
  --to "2026-02-05T11:00:00Z"

# Search for errors only
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from 24h \
  --level error

# Free text search
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from 1h \
  --query "connection refused"

# JSON output for scripting
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from 1h \
  --format json
```

## Common Use Cases

### Investigate PagerDuty Incident

When investigating a PagerDuty alert, search logs around the incident time:

```bash
# 1. Get incident details from PagerDuty (note the timestamp)
# Example: Alert fired at 2026-02-05T10:30:00Z for cluster atgraf1-ndl-prod

# 2. Search logs 15 minutes before and after
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from "2026-02-05T10:15:00Z" \
  --to "2026-02-05T10:45:00Z"

# 3. Filter for errors only
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from "2026-02-05T10:15:00Z" \
  --to "2026-02-05T10:45:00Z" \
  --level error
```

### Pod-Level Log Queries

Use field-specific query syntax to search logs for specific pods, namespaces, or containers. This is especially useful as an alternative to `kubectl logs` when the `caas_sec` kubeconfig role lacks `pods/log` permissions.

**⚠️ Limitation:** Only `kube-system` namespace logs are typically indexed in OpenSearch.

```bash
# Get logs for a specific pod by name prefix (use .keyword for hyphenated names)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster --from 1h \
  --query 'kubernetes.pod_name.keyword:etcd*'

# Get error logs for kube-apiserver pods
source .env && .venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster --from 1h \
  --query 'kubernetes.pod_name.keyword:kube-apiserver*' --level error

# Get logs for a specific pod (exact name in quotes)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster --from 1h \
  --query 'kubernetes.pod_name:"etcd-my-cluster-node1"'

# Filter by container name (simple tokens work without .keyword)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster --from 1h \
  --query 'kubernetes.container_name:etcd' --level error

# Combined: pod + namespace + error level
source .env && .venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster --from 24h \
  --query 'kubernetes.pod_name.keyword:coredns* AND kubernetes.namespace_name.keyword:kube-system' \
  --level error
```

#### Available Kubernetes Fields

These fields are available in the `--query` parameter using Lucene query syntax:

| Field | Description | Example |
|-------|-------------|---------|
| `kubernetes.pod_name` | Pod name (analyzed — use `.keyword` for wildcards with hyphens) | `kubernetes.pod_name.keyword:kube-apiserver*` |
| `kubernetes.namespace_name` | Namespace (use `.keyword` for exact/wildcard) | `kubernetes.namespace_name.keyword:kube-system` |
| `kubernetes.container_name` | Container name | `kubernetes.container_name:etcd` |
| `kubernetes.host` | Node hostname | `kubernetes.host:my-node-name` |
| `kubernetes.labels.*` | Pod labels | `kubernetes.labels.component:etcd` |

#### Query Syntax Tips

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `.keyword` + wildcard | `kubernetes.pod_name.keyword:etcd*` | Hyphenated pod names (most common) |
| Exact match (quotes) | `kubernetes.pod_name:"etcd-node1-abc"` | Known exact pod name |
| Simple token | `kubernetes.container_name:etcd` | Single-word names (no hyphens) |
| `AND` combination | `...pod_name.keyword:X* AND ...namespace_name.keyword:Y` | Filter by multiple fields |
| Label match | `kubernetes.labels.component:etcd` | Filter by pod label |

### Daily Health Check

Check for errors in the last 24 hours:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster my-cluster \
  --from 24h \
  --level error \
  --limit 50
```

### Search Multiple Clusters

Use partial cluster name matching:

```bash
# All clusters at atgraf1 site
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1 \
  --from 1h
```

## Cross-Skill Integration

### Investigate PagerDuty Incident

Use the **troubleshoot** skill for a complete cluster investigation workflow, or manually correlate PagerDuty incidents with logs:

```bash
# 1. Get recent incidents
.venv/bin/python ../../pagerduty/scripts/pd-incidents.py --since "2026-02-04"

# 2. For each incident, search logs around that time
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster <cluster-from-incident> \
  --from "<incident-time-minus-15min>" \
  --to "<incident-time-plus-15min>"
```

### NetBox + OpenSearch

Get cluster info from NetBox, then search logs:

```bash
# 1. Get cluster details
.venv/bin/python ../../netbox/scripts/netbox-get-cluster.py atgraf1-ndl-prod

# 2. Search logs for that cluster
.venv/bin/python ${SKILL_DIR}/scripts/opensearch-search.py \
  --cluster atgraf1-ndl-prod \
  --from 1h
```

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| Connection failed | Not on VPN | Connect to Telekom VPN |
| HTTP 401 | Invalid credentials | Check OPENSEARCH_* environment variables |
| HTTP 403 | No tenant access | Ensure you have access to caas-tenant |
| No results | Wrong time range or cluster | Adjust filters, try broader search |
| SSL error | Certificate issue | Scripts disable SSL verification for internal CA |

## Security Notes

1. **Credential Storage**: Never commit credentials to version control
2. **VPN Required**: API access requires Telekom VPN connection
3. **Session Cookies**: Browser cookies expire, refresh as needed
4. **Read-Only**: All operations are read-only log queries
5. **SSL Verification**: Disabled for internal certificate compatibility

## Output Formats

### Table (default)
Human-readable table with timestamp, level, cluster, and message columns.

### JSON
Raw OpenSearch hits for programmatic processing.

## Troubleshooting

### Authentication Issues

If authentication fails:

1. **Check VPN**: Ensure you're connected to Telekom VPN
2. **Verify credentials**: Test in browser first
3. **Session expiry**: If using cookie auth, refresh the session
4. **Tenant access**: Confirm you have access to caas-tenant

### No Results Found

If searches return no results:

1. **Check time range**: Ensure logs exist for the specified period
2. **Verify cluster name**: Use exact cluster name from NetBox
3. **Check index pattern**: Logs must be in caas-*,*-caas-*,tcaas-* indices
4. **Try broader search**: Remove filters one at a time
