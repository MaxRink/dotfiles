---
name: dt-brain-shared-caas-troubleshoot
description: This skill should be used when the user mentions "troubleshoot", "troubleshooting", "investigate cluster", "cluster investigation", "what's wrong with", "check cluster issues", "cluster problems", or needs to diagnose issues with a CaaS Kubernetes cluster.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-troubleshoot by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Cluster Troubleshooting Workflow

This skill provides a structured workflow for troubleshooting CaaS Kubernetes clusters. Follow these steps in order for consistent, thorough investigations.

## Workflow Overview

```
1. PagerDuty     →  Check for active/recent incidents
2. DDU           →  Get current cluster health status
3. Kubectl       →  Deep-dive into K8s resources (pods, nodes, events, logs)
4. NetBox        →  Get cluster metadata (DC, type, region)
5. AlertManager  →  Check silences if DDU alerts missing from PagerDuty
6. OpenSearch    →  Search logs around incident times (if needed)
7. Network Diag  →  Check TOR switch ports (optional, for network issues)
8. Node Commands →  Run OS diagnostics on nodes (optional, for node issues)
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

## Step 3: Kubectl Investigation (Conditional)

**Goal:** Deep-dive into Kubernetes resources to investigate issues surfaced by DDU or PagerDuty.

**Run this step if:**
- DDU shows pods not running or in error states
- Nodes are `NotReady` (describe node for conditions, taints, events)
- PagerDuty alerts point to specific workloads (TargetDown, OOMKilled, CrashLoopBackOff)
- etcd, DNS, or certificate-related alerts are firing
- Need to check resource usage (CPU/memory pressure on nodes or pods)
- Need pod logs for root-cause analysis

Use the **caas-kubectl** skill for this step. For detailed per-alert runbooks, see `caas-kubectl/references/troubleshooting-runbooks.md`.

> **⚠️ Pod logs limitation:** The default `caas_sec` role **cannot** read pod logs (`Forbidden`). Use **OpenSearch** for pod logs instead — see [Pod Logs via OpenSearch](#pod-logs-via-opensearch) below. OpenSearch indexes `kube-system` namespace logs.

### Alert-to-kubectl Command Mapping

Use this table to select which kubectl commands to run based on issues found in earlier steps:

| Issue / Alert | Recommended kubectl Commands | Rationale |
|---------------|------------------------------|-----------|
| TargetDown (kube-state-metrics) | `get pods -n kube-system -l app.kubernetes.io/name=kube-state-metrics`, `describe pod`, `top nodes` | Check if KSM pod is OOMKilled, check node resource pressure |
| TargetDown (generic) | `get pods -A \| grep <job>`, `describe pod`, `get endpoints -A \| grep <job>` | Find affected pods, check endpoints for missing targets |
| Pod CrashLoopBackOff / OOMKilled | `get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded`, `describe pod` | Find crashing pods, get crash reason. **For logs, use OpenSearch** |
| Node NotReady | `get nodes -o wide`, `describe node <name>`, `get pods -A --field-selector spec.nodeName=<name>` | Check node conditions, taints, pods scheduled on it |
| etcd issues | `get pods -n kube-system -l component=etcd` | Check etcd pod health. **For logs, use OpenSearch** |
| DNS issues | `get pods -n kube-system -l k8s-app=kube-dns` | Check CoreDNS pod status. **For logs, use OpenSearch** |
| PV/PVC issues | `get pvc -A --field-selector=status.phase=Pending`, `describe pvc`, `get pods -A \| grep csi` | Find pending PVCs, check CSI driver pods |
| Certificate issues | `get certificates -A`, `get certificaterequests -A`, `get pods -n cert-manager` | Check cert status, cert-manager health |
| Resource pressure | `top nodes`, `top pods -A --sort-by=memory`, `describe nodes \| grep -A5 Conditions` | Identify resource-constrained nodes and top consumers |
| General investigation | `get events -A --sort-by='.lastTimestamp'`, `get pods -A`, `top nodes` | Broad triage: recent events, pod overview, resource usage |

### Commands

```bash
# Check pod status across all namespaces
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> get pods -A

# Describe a specific pod
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> describe pod <pod-name> -n <namespace>

# Check node status and conditions
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> get nodes -o wide
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> describe node <node-name>

# Resource usage (nodes and pods)
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> top nodes
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> top pods -A --sort-by=memory

# Recent events (useful for spotting patterns)
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster-name> get events -A --sort-by='.lastTimestamp'
```

### Example Investigation Flow

```bash
# DDU reports pods crashing in kube-system → investigate with kubectl
# 1. Get overview of non-running pods
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  my-cluster get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# 2. Describe the crashing pod
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  my-cluster describe pod <crashing-pod> -n kube-system

# 3. Check pod logs via OpenSearch (kube-system pods)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster my-cluster --from 1h \
  --query 'kubernetes.pod_name.keyword:<crashing-pod-prefix>*' --level error

# 4. Check resource pressure on the node
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  my-cluster top nodes
```

### What to Look For

| Output | Likely Cause |
|--------|-------------|
| Pod status `CrashLoopBackOff` | Application crash — check logs and previous logs |
| Pod exit code 137 | OOMKilled — increase memory limits |
| Pod exit code 1 | Application error — check logs for stack trace |
| Node condition `NotReady` | Kubelet or network issue — describe node for details |
| Node condition `MemoryPressure` | Node running out of memory — check top pods |
| Node condition `DiskPressure` | Node running out of disk — check df via node-commands |
| Pending PVCs | Storage provisioning issue — check CSI driver pods |
| etcd leader changes | Unstable control plane — check etcd pod logs and node health |
| Many recent events of same type | Flapping resource — investigate root cause |
| `FailedScheduling` events | Resource constraints or taints preventing scheduling |

### Pod Logs via OpenSearch

When `caas_sec` denies `kubectl logs` access, use OpenSearch to query pod logs for `kube-system` pods. Use the `.keyword` subfield for wildcard patterns on hyphenated pod names.

**⚠️ Limitation:** Only `kube-system` namespace logs are indexed in OpenSearch.

```bash
# Get logs for a specific pod by name prefix
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name.keyword:etcd*'

# Get error logs for kube-apiserver pods
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name.keyword:kube-apiserver*' --level error

# Get logs for a specific pod (exact name)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name:"exact-pod-name-here"'

# Filter by container name
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.container_name:etcd' --level error

# Combined: pod + namespace + error level
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 24h \
  --query 'kubernetes.pod_name.keyword:coredns* AND kubernetes.namespace_name.keyword:kube-system' \
  --level error
```

#### OpenSearch Query Syntax Tips

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `.keyword` + wildcard | `kubernetes.pod_name.keyword:etcd*` | Hyphenated pod names (most pods) |
| Exact match (quotes) | `kubernetes.pod_name:"etcd-node1-abc"` | Known exact pod name |
| Simple token | `kubernetes.container_name:etcd` | Single-token names (no hyphens) |
| Combined fields | `...pod_name.keyword:X* AND ...namespace_name.keyword:Y` | Narrow to specific pod + namespace |

## Step 4: Get Cluster Metadata from NetBox

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

## Step 5: Check AlertManager Silences (Conditional)

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

## Step 6: Search OpenSearch Logs (Conditional)

**Goal:** Find log entries around incident times to identify root cause.

**Only run this step if:**
- Incidents were found in Step 1
- You have specific timestamps to investigate
- Current health check shows issues

## Step 7: Network Diagnostics (Optional)

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

## Step 8: Node Diagnostics (Optional)

**Goal:** Run OS-level diagnostic commands directly on cluster nodes to investigate node-specific issues.

**Run this step if:**
- Node is `NotReady` or flapping between Ready/NotReady
- Kubelet or containerd alerts are firing
- Disk pressure, memory pressure, or OOM alerts are detected
- NTP drift or time-related issues are suspected
- RAID degradation alerts (mdstat)
- Need to verify node-level state beyond what Kubernetes API reports

Use the **caas-node-commands** skill for this step.

### Issue-to-Command Mapping

Use this table to select which commands to run based on the issues found in earlier steps:

| Issue / Alert | Recommended Commands | Rationale |
|---------------|---------------------|-----------|
| Node NotReady | `kubelet_status`, `failed_units`, `dmesg_err` | Check kubelet health, failed systemd units, kernel errors |
| Kubelet issues | `kubelet_status`, `journal_err`, `containerd_status` | Kubelet + containerd health, system journal errors |
| Disk alerts (DiskPressure) | `df_root`, `df_all`, `disk_io` | Check disk usage and I/O stats |
| Memory alerts (OOMKilled) | `free`, `top_mem`, `mem_huge` | Check memory usage, top consumers, hugepages |
| High CPU / load | `top_cpu`, `uptime` | Check load average and top CPU consumers |
| Network issues | `ip_addr`, `dmesg_err` | Check interface status, NIC errors in dmesg |
| NTP / time drift | `ntp_status` | Check time synchronization status |
| RAID degradation | `mdstat` | Check software RAID array status |
| General investigation | `uptime`, `failed_units`, `dmesg_err`, `journal_err` | Broad triage: uptime, failed services, errors |

### Commands

```bash
# Run a diagnostic command on all nodes
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster-name> <command-id>

# Filter to specific nodes (e.g., only workers, or a specific node)
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster-name> <command-id> --node worker

# Get JSON output for structured analysis
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster-name> <command-id> --format json

# List all available diagnostic commands
.venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py --list-commands
```

### Example Investigation Flow

```bash
# Node NotReady detected → run kubelet + failed units + dmesg on affected node
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  my-cluster kubelet_status --node "affected-node-name"

source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  my-cluster failed_units --node "affected-node-name"

source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  my-cluster dmesg_err --node "affected-node-name"
```

### What to Look For

| Output | Likely Cause |
|--------|-------------|
| kubelet `inactive` or `failed` | Kubelet crash — check journal_err for details |
| `df -h /` shows >90% used | Disk pressure — identify large files/dirs |
| `free` shows low available memory | Memory pressure — check top_mem for consumers |
| `dmesg` shows hardware errors | Hardware failure — NIC, disk, memory ECC |
| `failed_units` lists services | Systemd service failures — investigate each |
| High load average vs CPU count | CPU saturation — check top_cpu for offenders |
| NTP not synchronized | Time drift — may cause cert/auth issues |
| mdstat shows degraded array | RAID disk failure — replacement needed |

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

# 3. Kubectl deep-dive (if DDU shows issues)
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get events -A --sort-by='.lastTimestamp'

# 4. NetBox metadata
.venv/bin/python .claude/skills/cloud-netbox/scripts/netbox-get-cluster.py <cluster>

# 5. AlertManager silences (if DDU shows alerts but PagerDuty is empty)
.venv/bin/python .claude/skills/caas-alertmanager/scripts/am-silence-list.py

# 6. OpenSearch logs (if incidents found, use timestamps from step 1)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --query "\"<cluster>\"" --from "<time>" --to "<time>"

# 7. Node diagnostics (if node-level issues found)
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> kubelet_status
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> failed_units
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

### Scenario 4: "Node is NotReady / node issues"

```bash
# 1. DDU health check (confirm node status)
.venv/bin/python .claude/skills/caas-ddu/scripts/ddu-check.py <cluster>

# 2. Kubectl — check node conditions and pods on the affected node
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get nodes -o wide

source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> describe node "<node-name>"

source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get pods -A --field-selector spec.nodeName="<node-name>" -o wide

source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get events -A --sort-by='.lastTimestamp'

# 3. Run node diagnostics on affected node (OS-level)
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> kubelet_status --node "<node-name>"

source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> failed_units --node "<node-name>"

source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> dmesg_err --node "<node-name>"

# 4. Check disk and memory if resource pressure suspected
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> df_root --node "<node-name>"

source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py \
  <cluster> free --node "<node-name>"
```

### Scenario 5: "Pods crashing / CrashLoopBackOff"

```bash
# 1. DDU health check
.venv/bin/python .claude/skills/caas-ddu/scripts/ddu-check.py <cluster>

# 2. Find non-running pods
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# 3. Describe the crashing pod (check Last State, Exit Code, Events)
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> describe pod <pod-name> -n <namespace>

# 4. Check crash logs via OpenSearch (kube-system pods)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name.keyword:<pod-name-prefix>*' --level error

# 5. Check resource pressure on the node
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> top nodes

source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py \
  <cluster> top pods -n <namespace> --sort-by=memory
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
- `NETBOX_API_TOKEN` - For NetBox queries (Step 4) and kubectl kubeconfig fetch (Step 3)
- `ALERTMANAGER_URL` / `ALERTMANAGER_USER` / `ALERTMANAGER_PASSWORD` - For AlertManager silence checks
- `OPENSEARCH_USER` / `OPENSEARCH_PASSWORD` - For log searches
- **SSH key** - Must be loaded in ssh-agent for node commands (Step 8)
- **kubectl** - Required locally for node discovery (Step 8) and kubectl investigation (Step 3)
