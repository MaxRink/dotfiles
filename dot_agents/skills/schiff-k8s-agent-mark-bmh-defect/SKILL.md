---
name: schiff-k8s-agent-mark-bmh-defect
description: Mark a BareMetalHost as defect and hand it over to the bm4x / DC-ops team for repair or return by patching the corresponding bm4x Compute resource with `spec.problem`.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/mark-bmh-defect by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Mark a BareMetalHost as defect (bm4x hand-over)

Use this skill whenever DC-ops or the bm4x team needs to take a host out of service for hardware repair / return, e.g. after a `SystemHealthDegraded` alert, failing CMOS battery, broken PSU, or any other physical defect. The hand-over is done by patching the bm4x `Compute` resource that wraps the BMH — **not** the BMH itself. The bm4x-operator then drives the cordon → drain → deprovision → BMH release workflow automatically.

## When to use

- DC-ops asks to "give back the hardware" for a specific host.
- An iDRAC / Redfish alert indicates a hardware fault that needs physical intervention.
- You detected a BMH that repeatedly fails provisioning due to a hardware issue (e.g. `BmcUnreachable` persisting after credential rotation).

Do **not** use this for transient software issues — silence the alert or fix the config instead.

## Inputs

- BMH hostname (FQDN), e.g. `bmbg10com5ify.inf.bm4x.telekom.de`.
- A short reason for the hand-over (goes into `spec.problem.details`).
- Optional: Alertmanager silence ID and KB incident ID for cross-referencing.

## Source of truth

The `Compute` CRD lives under `bm4x.t-caas.telekom.com/v1alpha1` on the **management cluster** that owns the BMH namespace. Each Compute has labels linking it to the BMH:

```yaml
labels:
  infra.t-caas.telekom.com/host-kind: BareMetalHost
  infra.t-caas.telekom.com/host-name: <bmh-fqdn>
  bm4x.t-caas.telekom.com/compute-pool: <pool-name>
```

The relevant spec field:

```yaml
spec:
  problem:
    reason: <enum>     # required
    details: <string>  # freeform context
```

Valid `reason` enum values (from the CRD):

| Reason | Meaning |
|---|---|
| `ReturnRequested` | Admin-initiated hardware return (DC-ops asked for it back). **Most common for this skill.** |
| `UnknownDefect` | Operator-detected hardware fault, cause unclear |
| `UnknownProblem` | Generic problem, not necessarily hardware |
| `MarkedByInfraController` | Set by infra controller automation — do not set manually |
| `BmcUnreachable` | BMC/iDRAC not responding |
| `BmcWrongFirmware` | BMC firmware blocks management |
| `TogglingLink` | Link flapping detected |

Pick `ReturnRequested` for explicit hand-over requests, `UnknownDefect` when you detected the fault yourself and DC-ops should diagnose.

## Procedure

### 1. Identify the owning management cluster

BMHs live on the management cluster that hosts their metal3 namespace. The BMH FQDN encodes the location (e.g. `bmbg10com5ify` → location `bmbg10`), and the metal3 namespace follows the pattern `metal3-<env>-<location>`. To find which mgmt cluster owns that namespace, use the existing **`find-management-cluster`** skill:

- Treat the metal3 namespace as a tenant context — the SchiffCluster YAML for any tenant in that location points to the same mgmt cluster via `spec.internal.managementCluster`.
- If unsure which tenant to pick, grep `clusters.yaml` in `schiff/platform/infrastructure/cluster-components` for entries with the same location suffix.

Switch context:

```bash
kubectl config use-context <managementCluster>
kubectl config current-context   # verify
```

If you already know the host's namespace, a quick sanity check:

```bash
kubectl get bmh -n <namespace> <bmh-fqdn>
```

### 2. Find the corresponding Compute

```bash
kubectl get computes -A | grep <bmh-fqdn>
```

Note the Compute `name` and `namespace`. The BMH namespace and Compute namespace are the same.

### 3. Inspect the Compute before patching

```bash
kubectl get compute <compute-name> -n <namespace> -o yaml
```

Check:

- **`spec.consumerRef`** — if present, the Compute is bound to a tenant cluster Machine. Hand-over will trigger drain of the node; coordinate with the tenant cluster owner first.
- **`spec.problem`** — if already set, do not overwrite without reviewing existing context.
- **`status.conditions`** — record the pre-patch state for the KB.

For an idle compute you will see `spec.consumerRef` absent and BMH in `state=available` — safe to proceed without tenant coordination.

### 4. Confirm with the user (safety)

Marking defect is a mutating operation on a production mgmt cluster and starts an irreversible return workflow. Always get explicit confirmation before patching, unless the user has authorized autonomous operation.

State clearly:

- Target: `Compute <name> -n <namespace>` on context `<mgmt-cluster>`.
- Chosen `reason` and `details`.
- Whether `consumerRef` is empty (idle) or set (tenant impact).

### 5. Patch the Compute

```bash
kubectl --context=<mgmt-cluster> patch compute <compute-name> -n <namespace> \
  --type=merge \
  -p '{"spec":{"problem":{"reason":"ReturnRequested","details":"<short reason>. Silence <silence-id>. KB <kb-id>."}}}'
```

Example (real case):

```bash
kubectl --context=schiff-mgmt-1.tmdc.b patch compute workers-1-2-1-qxqz8 \
  -n metal3-ref-bmbg10 --type=merge \
  -p '{"spec":{"problem":{"reason":"ReturnRequested","details":"CR2032 coin-cell battery lower-critical (iDRAC SEL 574). DC-ops Berlin 500 requested return. Silence ae379bbf-... KB 14bad280-..."}}}'
```

### 6. Verify the operator reacted

```bash
kubectl get compute <compute-name> -n <namespace> -o yaml | \
  grep -A5 -E 'problem:|lifecycle:|^status:'
```

You should see within seconds:

- `spec.lifecycle.consumer.details: "ComputeReconciler-mark: compute is defect"` — the operator accepted the problem signal.
- Conditions transitioning: `Ready=False (PreDeleteResourceCheck)`, `BoundHostReady=False (ComputeDeletionPending)`.

If the conditions do not transition within a minute, check operator logs:

```bash
kubectl -n bm4x-system logs -l app.kubernetes.io/name=bm4x-operator --tail=100
```

### 7. Silence the alert (if still firing)

If an Alertmanager alert is still firing for this host (e.g. `SystemHealthDegraded`), silence it for a reasonable return window (typically 7 days). Include the KB incident ID in the silence comment.

### 8. Record in the KB

Store an incident via `kb_store_incident` with:

- `title`: `<hostname> handed back to DC-ops via bm4x ReturnRequested`
- `root_cause`: hardware symptom
- `resolution`: the `kubectl patch` command used + operator reaction summary
- `tags`: `bm4x-operator,bmh,compute,return-requested,hardware-return,metal3,<specific-fault>`
- `runbook_url`: https://wiki.telekom.de/display/NSOF/Allgemein+-+BareMetal+Hardware+Issues

Cross-link the Alertmanager silence ID in the KB incident and the KB ID in the silence comment.

## Fallbacks

- **`kubectl explain compute.spec.problem` shows a truncated enum** — get the full list from the CRD:

  ```bash
  kubectl get crd computes.bm4x.t-caas.telekom.com -o json | \
    jq -r '.spec.versions[0].schema.openAPIV3Schema.properties.spec.properties.problem.properties.reason.enum'
  ```

- **BMH has `consumerRef` set (tenant workload running)** — do not mark defect silently. Notify the tenant cluster owner, coordinate a maintenance window, then proceed. The drain may be blocked by PDBs (see AGENTS.md playbook for PDB deadlock patterns).

- **Compute has a stale finalizer after operator starts deprovision** — check `metadata.finalizers` and corresponding operator logs; do not force-remove finalizers without understanding the state.

- **Wrong mgmt cluster context** — always verify with `kubectl config current-context` before patching. The Compute and BMH are namespaced but not all namespaces exist on every mgmt cluster.

## Safety rules

- **Mutating op on prod** — requires explicit user confirmation each time.
- **Never `kubectl delete`** a Compute or BMH to "force" a hand-over — the operator workflow is the only supported path.
- **Never overwrite an existing `spec.problem`** without reviewing its current reason/details.
- **Coordinate** with tenant cluster owners if `consumerRef` is set; a defect mark on a consumed compute will drain a tenant node.
- Re-verify the target one last time by reading `spec.consumerRef` and the BMH `status.provisioning.state` right before patching.
