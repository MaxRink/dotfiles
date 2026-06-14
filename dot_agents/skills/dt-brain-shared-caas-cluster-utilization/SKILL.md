---
name: dt-brain-shared-caas-cluster-utilization
description: >
  Calculate worker CPU utilization by QoS pool on CaaS baremetal clusters. Use when the user mentions
  "cluster utilization", "CPU utilization", "worker utilization", "QoS utilization", "exclusive CPU",
  "shared CPU", "isolcpus", "CPU allocation", "cluster capacity", "worker capacity", "how much CPU is used",
  "how many CPUs are allocated", "CPU overcommit", "overcommitted", "reserved CPUs", "CPU Manager",
  asks "how full is the cluster", "what is the utilization", or needs to understand how worker node CPUs
  are split between Guaranteed (exclusive) and Burstable/BestEffort (shared) workloads.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-cluster-utilization by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Cluster CPU Utilization

Calculate worker node CPU utilization split by QoS-based CPU pools.

On CaaS baremetal clusters with static CPU Manager policy, worker CPUs are divided into two pools:

- **Exclusive pool** (isolcpus range): Guaranteed QoS pods with integer CPU requests get pinned cores
- **Shared pool** (reservedSystemCPUs): system daemons + Burstable + BestEffort + Guaranteed pods with fractional CPU requests

Pool sizes are auto-detected from node `capacity` vs `allocatable` — no hardcoded ranges needed.

## ⚠️ READ-ONLY

The script only runs `kubectl get nodes` and `kubectl get pods` — no writes, no exec, safe for production.

## Usage

```bash
# By cluster name (fetches kubeconfig from NetBox)
source .env && .venv/bin/python .claude/skills/caas-cluster-utilization/scripts/cluster-utilization.py <cluster-name>

# With explicit kubeconfig (no NetBox needed)
.venv/bin/python .claude/skills/caas-cluster-utilization/scripts/cluster-utilization.py --kubeconfig /path/to/kubeconfig

# JSON output
source .env && .venv/bin/python .claude/skills/caas-cluster-utilization/scripts/cluster-utilization.py <cluster-name> --format json
```

## kubectl Plugin

A wrapper script lets you run the analysis as `kubectl cpu-utilization`, using your current `$KUBECONFIG`:

```bash
# Install (symlink into PATH — one time)
ln -s "$(pwd)/.claude/skills/caas-cluster-utilization/scripts/kubectl-cpu_utilization" /usr/local/bin/kubectl-cpu_utilization

# Use with current kubeconfig
kubectl cpu-utilization
kubectl cpu-utilization --format json
```

The plugin picks up `$KUBECONFIG` automatically (falls back to `~/.kube/config`).

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--kubeconfig` | (none) | Use explicit kubeconfig file instead of NetBox |
| `--role` | `caas_sec` | NetBox secret role for kubeconfig retrieval |
| `--format` | `text` | Output format: `text` or `json` |

## Output

The text report shows per-node, per-worker-group, and cluster-wide utilization:

```
============================================================
  Cluster Worker CPU Utilization
============================================================
  Cluster:  my-cluster
  Workers:  6
  Date:     2026-03-16 12:00

------------------------------------------------------------
  Worker Group: profile266ai1  (3 nodes)
  Per-node: 128 CPU total = 112 exclusive + 16 shared

  Exclusive Pool (Guaranteed pods with integer CPU):
    node-1:     38 / 112 CPUs  (33.9%)
    node-2:     35 / 112 CPUs  (31.3%)
    ...
  Shared Pool (Burstable + BestEffort + Guaranteed fractional):
    node-1:   14.9 / 16 CPUs  (93.1%)
    ...

============================================================
  Cluster Summary
============================================================
  Exclusive (Guaranteed):  163 / 672 CPUs   24.3%
  Shared (Burst+BE+frac): 175.1 / 96 CPUs  182.4%
  Overall (all CPUs):      338.1 / 768 CPUs  44.0%
```

Shared pool utilization above 100% is normal — Burstable pods overcommit by design using CFS scheduling.

## How It Works

1. Queries nodes and groups workers by `caas.in.pan-net.eu/worker-group` label
2. Derives pool sizes: exclusive = allocatable, shared = capacity − allocatable
3. Queries all pods and classifies each running pod on worker nodes:
   - **Exclusive**: QoS = Guaranteed AND all containers have integer CPU requests ≥ 1
   - **Shared**: everything else (Burstable, BestEffort, Guaranteed with fractional CPU)
4. Aggregates CPU requests per node → per group → cluster-wide

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `NETBOX_API_TOKEN` | Only for cluster-name mode | NetBox API token for kubeconfig retrieval |

Also requires `kubectl` in PATH and VPN connection (for NetBox mode).

## Batch Mode (Multiple Clusters)

Analyze all active baremetal CaaS clusters in parallel and save results to local files:

```bash
# All active baremetal clusters (default 5 parallel workers)
source .env && .venv/bin/python .claude/skills/caas-cluster-utilization/scripts/batch-cluster-utilization.py

# Only Slovakia clusters, 10 workers
source .env && .venv/bin/python .claude/skills/caas-cluster-utilization/scripts/batch-cluster-utilization.py --site SK --workers 10

# Custom output directory
source .env && .venv/bin/python .claude/skills/caas-cluster-utilization/scripts/batch-cluster-utilization.py --output-dir /tmp/util-report
```

### Batch Options

| Flag | Default | Description |
|------|---------|-------------|
| `--workers` | `5` | Max parallel cluster queries |
| `--role` | `caas_sec` | NetBox secret role for kubeconfig |
| `--site` | (none) | Filter clusters by site/country (e.g., SK, AT, HR) |
| `--timeout` | `120` | Per-cluster timeout in seconds |
| `--output-dir` | `reports/cluster-utilization/<timestamp>` | Override output directory |

### Batch Output

Results are saved to a timestamped directory:

```
reports/cluster-utilization/2026-03-16T14-09/
├── summary.json          # Combined results + aggregate stats
├── cluster-abc.json      # Per-cluster detail (same as --format json)
├── cluster-xyz.json
└── ...
```

The `summary.json` includes:
- Per-cluster status (ok/error) with utilization summaries
- Cross-cluster aggregate stats (total workers, total CPUs, overall utilization)
- Metadata (timestamp, duration, worker count, filters used)

Failed clusters are logged but don't block the rest — their errors appear in the summary.

## Tips

- Use `--kubeconfig` to skip NetBox when you already have a kubeconfig file
- The `caas_sec` role is read-only — safe for all clusters
- Combine with `caas-kubectl` skill's `top nodes` for actual (real-time) vs allocated utilization
- JSON output (`--format json`) includes per-pod breakdowns for deeper analysis
- Use batch mode with `--site` to analyze all clusters in a specific country
