---
name: schiff-k8s-agent-cluster-upgrade-check
description: Verify that a Kubernetes cluster upgrade completed successfully by checking CAPI component versions, replica readiness, and overall tenant cluster health (nodes, pods, events, workloads, Flux resources).
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/cluster-upgrade-check by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Cluster Upgrade Verification

Read-only skill. Reports findings but does **not** remediate.

## When to use

- A Kubernetes version upgrade was performed on a tenant cluster and you need to confirm it completed successfully.
- A rolling update is in progress and you want to check current state / progress.
- Post-upgrade health check requested by the user or triggered by an alert indicating version mismatch.

Do **not** use this for general cluster health checks unrelated to an upgrade — use the `k8s-incident-response` skill instead.

## Inputs

- **Cluster ID** (required) — full cluster identifier, e.g. `m2m-1.ref.gppng2`
- **Expected Kubernetes version** (required) — e.g. `v1.34.4`

## Procedure

### Step 1: Run the verification script

Run the upgrade check script with JSON output:

```bash
uv run cluster-upgrade-check.py <cluster-id> <version> --output json
```

The script automatically:

- Derives the management cluster context, CAPI namespace, and provider from `$SCHIFF_REPO`
- Checks all CAPI components (Cluster, KCP, MachineDeployments, MachineSets, Machines, Provider resources)
- Checks tenant health (Nodes, Pods, Events, Deployments, DaemonSets, StatefulSets, HelmReleases, Kustomizations)
- Returns structured JSON with per-check status and an overall result

If the script is not available (missing `uv`, missing `$SCHIFF_REPO`, etc.), skip to the **Fallback** section below.

### Step 2: Evaluate results

Parse the JSON output. The top-level `status` field determines the outcome:

- **`PASS`** (exit code 0): All checks passed. Report success to the user. Done.
- **`IN_PROGRESS`** (exit code 2): Upgrade is still rolling out. Report progress from the `phases[0].checks` array (look for checks with `status: "IN_PROGRESS"`). Ask the user whether to wait and re-run, or investigate.
- **`FAIL`** (exit code 1): One or more checks failed. Proceed to Step 3.

### Step 3: Investigate failures

For each check in the JSON with `status: "FAIL"`:

1. **Search the knowledge base** for similar past incidents:

   ```text
   kb_search_incidents(query="<check name> <summary>", affected_component="cluster/<cluster-id>")
   ```

2. **Investigate the specific failure** using kubectl/MCP tools. Common patterns:

   | Failed check | Investigation |
   |---|---|
   | Cluster | `kubectl get cluster <name> -n <ns> -o yaml` on mgmt — check conditions |
   | KubeadmControlPlane | Check KCP conditions, etcd health, CP node logs |
   | MachineDeployments | Check MD events, stuck machines, provision failures |
   | Machines | Check individual Machine status, BMH/vSphereVM state |
   | Provider (metal3) | Check BMH status, Ironic logs, consider `clean-stuck-bmh` skill |
   | Nodes | `kubectl describe node <name>` — check conditions, taints |
   | Pods | `kubectl logs <pod>`, `kubectl describe pod <pod>` — check events, exit codes |
   | Deployments/DaemonSets/StatefulSets | Check replica counts, pod status, resource constraints |
   | HelmReleases/Kustomizations | Check Flux reconciliation status, `flux get hr/ks -A` |

3. **Propose a fix** or escalate to the user with findings.

4. **Store the incident** in the knowledge base if a new root cause is identified:

   ```text
   kb_store_incident(
     title="...",
     description="...",
     affected_component="cluster/<cluster-id>",
     ...
   )
   ```

## Fallback: Manual procedure

If `cluster-upgrade-check.py` cannot be run, perform the checks manually:

### Phase 1: CAPI Components (management cluster)

1. Resolve management cluster context using the `find-mgnt-cluster` skill.

2. Retrieve CAPI resources:

   ```bash
   kubectl get cluster,kubeadmcontrolplane,machinedeployment,machineset,machine \
     -n <namespace> -o wide --context <mgmt-context>
   ```

3. Evaluate against these criteria:

   | Resource | Pass criteria |
   |---|---|
   | Cluster | PHASE=Provisioned, all replica counts equal |
   | KubeadmControlPlane | VERSION=expected, Initialized, not RollingOut |
   | MachineDeployment (each) | VERSION=expected, all counts equal, PHASE=Running |
   | MachineSet (each) | VERSION=expected, all counts equal |
   | Machine (each) | VERSION=expected, READY=True, PHASE=Running |

### Phase 2: Tenant cluster health

Run these on the tenant cluster context:

```bash
kubectl get nodes -o wide
kubectl get pods -A --field-selector 'status.phase!=Running,status.phase!=Succeeded'
kubectl get events -A --field-selector type=Warning --sort-by='.lastTimestamp'
kubectl get deploy,ds,sts -A
kubectl get helmrelease,kustomization -A
```

Report any unhealthy resources.

## Common post-upgrade findings

| Finding | Likely cause |
|---|---|
| Machine stuck at old version | Rolling update in progress or provision failure |
| KCP READY < DESIRED | CP node joining or etcd unhealthy |
| ImagePullBackOff | Registry credentials need rotation |
| HelmRelease/Kustomization not ready | Incompatible chart or reconciliation pending |
| DaemonSet READY < DESIRED | Node not fully ready or tolerations changed |

## Safety

- Entirely **read-only** — no mutations.
- Always verify kubectl context before commands.
