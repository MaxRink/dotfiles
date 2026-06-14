---
name: tcaas-agent-troubleshooter-caas-troubleshoot
description: This skill should be used when the user mentions "troubleshoot", "troubleshooting", "investigate cluster", "cluster investigation", "what's wrong with", "check cluster issues", "cluster problems", or needs to diagnose issues with a CaaS Kubernetes cluster.
---

<!-- Imported from tdi-caas/tools/tcaas-agent-troubleshooter/skills/caas-troubleshoot by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Cluster Troubleshooting Workflow

This skill provides a structured workflow for troubleshooting CaaS Kubernetes clusters. Follow these steps in order for consistent, thorough investigations.

## Workflow Overview

```
1. PagerDuty     →  Check for active/recent incidents
2. DDU           →  Get current cluster health status
3. NetBox        →  Get cluster metadata (DC, type, region)
4. AlertManager  →  Check silences if DDU alerts missing from PagerDuty
5. OpenSearch    →  Search logs around incident times (if needed)
6. Network Diag  →  Check TOR switch ports (optional, for network issues)
```

## Step 1: Check PagerDuty Incidents

**Goal:** Identify active or recent incidents for the cluster.

### Default Behavior (IMPORTANT)

| Scenario | Default Time Window | Status Filter |
|----------|---------------------|---------------|
| Quick check / "any issues?" | No time limit | `triggered,acknowledged` only |
| Investigation / "what happened?" | Last 48 hours | `triggered,acknowledged,resolved` |
| User specifies time | Honor user's request | All statuses |

**⚠️ NEVER default to beginning of year or month. Use 48 hours maximum unless explicitly requested.**

### Commands

**Always run BOTH queries:**

```bash
# 1. Check for active incidents (no time limit)
.venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incidents.py \
  --cluster <cluster-name> \
  --status triggered,acknowledged

# 2. Check recent incidents in last 48 hours (including resolved)
.venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incidents.py \
  --cluster <cluster-name> \
  --since "$(date -v-2d +%Y-%m-%d)" \
  --status triggered,acknowledged,resolved
```

**⚠️ IMPORTANT:** Always run both queries. Even if no active incidents, recent resolved incidents provide valuable context about cluster stability.

### What to Report

| Query | Result | Action |
|-------|--------|--------|
| Active incidents | 0 | Report "No active incidents" |
| Active incidents | >0 | Report details, continue to logs |
| Recent (48h) | 0 | Report "No incidents in last 48h" ✅ |
| Recent (48h) | >0 resolved | Report count and summary, offer to investigate |

### What to Look For

- **Active incidents** (triggered/acknowledged) - immediate attention needed
- **Recently resolved** - may explain current symptoms
- **Incident timestamps** - needed for OpenSearch log correlation
- **Alert types** - helps focus investigation (etcd, node, pod issues)

## Step 2: Check Cluster Health with DDU

**Goal:** Get current live status of the cluster.

```bash
.venv/bin/python .claude/skills/caas-ddu/scripts/ddu-check.py <cluster-name>
```

### What to Look For

- **Reconciliation status** - should be `ReconciliationSucceeded`
- **Active alerts** - critical/error severity alerts
- **Node status** - all nodes should be Ready
- **Pod health** - pods in kube-system should be Running

### Output Interpretation

| Status | Meaning |
|--------|---------|
| ReconciliationSucceeded | Cluster is healthy |
| ReconciliationFailed | GitOps sync issue |
| Node NotReady | Node health problem |
| Pods not running | Application/system issue |

## Step 3: Get Cluster Metadata from NetBox

**Goal:** Understand cluster context (location, type, management cluster).

```bash
.venv/bin/python .claude/skills/cloud-netbox/scripts/netbox-get-cluster.py <cluster-name>
```

### Key Information to Extract

- **Cluster type**: baremetal or openstack
- **Site/DC**: Physical location (e.g., ATGRAD001)
- **Management cluster**: Parent mgmt cluster
- **Custom fields**: Kubernetes version, product version

This context helps when:
- Checking if issue is site-wide
- Understanding infrastructure dependencies
- Identifying related clusters

## Step 4: Check AlertManager Silences (Conditional)

**Goal:** Identify if firing alerts from DDU are silenced in AlertManager, explaining why they don't appear in PagerDuty.

**Run this step if:**
- DDU shows firing alerts (Step 2)
- PagerDuty shows no incidents or fewer incidents than expected (Step 1)
- You need to understand why alerts aren't reaching PagerDuty

### Command

```bash
# List all active silences
.venv/bin/python .claude/skills/caas-alertmanager/scripts/am-silence-list.py
```

### How to Correlate

1. **Extract alert names from DDU output** - Look for `[warning]` lines with alert names like `MetalLBBGPSessionDown`, `CaasCustomNodeExporterLldpctlStatus`
2. **Search silences for matching alert names** - Check if any silence matcher includes `alertname=<alert-name>`
3. **Check for global vs cluster-specific silences**:
   - **Global silence**: No `cluster=` matcher → affects ALL clusters
   - **Cluster-specific**: Has `cluster=<name>` matcher → affects only that cluster

### What to Report

| Finding | Action |
|---------|--------|
| Alert silenced globally | Report silence details (author, comment, expiry) |
| Alert silenced for this cluster | Report silence details |
| Alert NOT silenced | Alert should be in PagerDuty - investigate routing |
| Silence expired recently | May explain recent PagerDuty activity |

### Common Silence Patterns

| Matcher Pattern | Meaning |
|-----------------|---------|
| `alertname=X` | All instances of alert X silenced globally |
| `alertname=X, cluster=Y` | Alert X silenced only for cluster Y |
| `cluster=Y` | All alerts for cluster Y silenced |
| `cluster=Y, alertname!=HeartBeat_Prometheus` | Cluster Y silenced except heartbeat |

### Example Analysis

```
DDU shows:    MetalLBBGPSessionDown (30 alerts firing)
PagerDuty:    0 incidents
Silence:      alertname=MetalLBBGPSessionDown (expires 2026-03-09)
Conclusion:   Alert is globally silenced, not a routing issue
```

## Step 5: Search OpenSearch Logs (Conditional)

**Goal:** Find log entries around incident times to identify root cause.

**Only run this step if:**
- Incidents were found in Step 1
- You have specific timestamps to investigate
- Current health check shows issues

## Step 6: Network Diagnostics (Optional)

**Goal:** Check TOR switch ports for physical/L2 connectivity issues.

**Run this step if:**
- Network-related alerts are firing (e.g., `MetalLBBGPSessionDown`, node NotReady with network symptoms)
- Suspected cable, VLAN, or switch port issues
- Need to verify server-to-switch physical connectivity

Use the **caas-network-diag** skill for this step. The workflow:

1. Resolve server hostname → cluster + TOR switches via NetBox
2. Start sshuttle tunnel to the cluster
3. SSH to TOR switches and run port diagnostics

```bash
# Resolve a specific server's switch connections
source .env && \
.venv/bin/python .claude/skills/caas-network-diag/scripts/netbox-resolve-host.py <hostname>

# Then follow caas-network-diag skill workflow for switch diagnostics
```

### What to Look For

| Finding | Likely Cause |
|---------|-------------|
| Port down on switch | Cable issue, NIC failure, admin shutdown |
| No MACs learned | L2 connectivity broken — check cable, VLAN |
| Wrong VLAN on port | Misconfiguration — compare with expected VLANs |
| High error counters | Bad cable, failing optic/SFP |
| Missing LLDP/CDP neighbor | NIC not communicating — driver or hardware issue |

### OpenSearch Log Commands

```bash
# Search logs around an incident time (±15 minutes)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster-name> \
  --from "<incident-time-minus-15min>" \
  --to "<incident-time-plus-15min>" \
  --limit 100

# Search for errors/issues only
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster-name> \
  --query "error OR fail OR NotReady OR rebooted" \
  --from "<start-time>" \
  --to "<end-time>" \
  --limit 100
```

### OpenSearch Tips

1. **Use exact cluster name in quotes**: `--query "\"mc-multitenancy-prod\""`
2. **Load credentials from .env**: `source .env && .venv/bin/python ...`
3. **Time format**: ISO 8601 (e.g., `2026-02-04T16:30:00Z`)
4. **Start narrow, expand if needed**: ±15 min first, then widen

### What to Look For

- **Node events**: `NodeNotReady`, `NodeHasInsufficientMemory`
- **Pod issues**: `CrashLoopBackOff`, `OOMKilled`
- **etcd problems**: `etcdMembersDown`, leader elections
- **Network issues**: connection refused, timeout errors

## Quick Reference: Common Scenarios

### Scenario 1: "Is the cluster healthy?"

```bash
# 1. Quick PagerDuty check (active only)
.venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incidents.py \
  --cluster <cluster> --status triggered,acknowledged

# 2. DDU health check
.venv/bin/python .claude/skills/caas-ddu/scripts/ddu-check.py <cluster>
```

### Scenario 2: "What happened to the cluster?"

```bash
# 1. Check incidents from last 48 hours
.venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incidents.py \
  --cluster <cluster> --since "$(date -v-2d +%Y-%m-%d)" \
  --status triggered,acknowledged,resolved

# 2. DDU health check
.venv/bin/python .claude/skills/caas-ddu/scripts/ddu-check.py <cluster>

# 3. NetBox metadata
.venv/bin/python .claude/skills/cloud-netbox/scripts/netbox-get-cluster.py <cluster>

# 4. AlertManager silences (if DDU shows alerts but PagerDuty is empty)
.venv/bin/python .claude/skills/caas-alertmanager/scripts/am-silence-list.py

# 5. OpenSearch logs (if incidents found, use timestamps from step 1)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --query "\"<cluster>\"" --from "<time>" --to "<time>"
```

### Scenario 3: "Investigate incident X"

```bash
# 1. Get incident details (note the cluster name and timestamp)
.venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incident-get.py <incident-id>

# 2. Search logs around incident time (±15 min)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster-from-incident> \
  --from "<incident-time-minus-15min>" \
  --to "<incident-time-plus-15min>"
```

## Time Window Defaults Summary

| Request Type | PagerDuty Window | OpenSearch Window |
|--------------|------------------|-------------------|
| Active issues | No limit (triggered only) | N/A |
| Recent issues | Last 48 hours | ±15 min of incident |
| Historical investigation | User-specified | ±15-30 min of incident |
| "Check since yesterday" | 24 hours | As needed |

## Presenting Results

After completing the workflow, summarize findings:

1. **Cluster Status**: Healthy ✅ or Issues Found ⚠️
2. **Active Incidents**: Count and brief description
3. **Recent Incidents**: Count and resolution status
4. **Silenced Alerts**: Any alerts firing but silenced (with author/reason)
5. **Root Cause** (if found): What the logs revealed
6. **Recommendations**: Next steps if issues exist

## Environment Requirements

Ensure these environment variables are set (or use `source .env`):

- `DDU_API_TOKEN` - For DDU cluster checks
- `PAGERDUTY_TOKEN` - For PagerDuty queries
- `NETBOX_API_TOKEN` - For NetBox queries
- `ALERTMANAGER_URL` / `ALERTMANAGER_USER` / `ALERTMANAGER_PASSWORD` - For AlertManager silence checks
- `OPENSEARCH_USER` / `OPENSEARCH_PASSWORD` - For log searches
