---
name: schiff-k8s-agent-unblock-stuck-md-drain
description: Prevent CAPI MachineDeployments from getting stuck indefinitely on node drain or volume detach by setting `deletionTimeoutMinutes` on the SchiffCluster workers definition (GitOps path via cluster-components + `schiff cluster create`). This is the structural remediation that corresponds to MR !16928.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/unblock-stuck-md-drain by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Unblock stuck MachineDeployment drains (GitOps / deletionTimeoutMinutes)

Use this skill whenever the `MachineDeploymentStuck` alert fires because a node drain is blocked indefinitely — typically by a PDB (single-replica deadlock, dual-PDB conflict, CrashLoopBackOff / ImagePullBackOff replacement pod) or by a `WaitingForVolumeDetach` condition.

The root cause of the *indefinite* wait is that CAPI `nodeDrainTimeoutSeconds` and `nodeVolumeDetachTimeoutSeconds` default to `0` (= infinite). This skill gives the MachineDeployment a bounded timeout (default 15 minutes) so CAPI gives up, force-deletes the node, and the rolling upgrade continues even when a tenant PDB is temporarily misbehaving.

## What this skill covers

- **GitOps-only, structural fix.** Edit the SchiffCluster YAML in `schiff/platform/infrastructure/cluster-components`, regenerate with `schiff cluster create`, commit, open an MR.
- Applies to **all future MachineSets** of that MachineDeployment.
- Does **not** unblock Machines that are *already* in `Deleting` phase — their timeout is frozen in their owning MachineSet and the MachineSet controller will revert direct patches. See the Confluence runbook below for the per-MachineSet emergency patch procedure (explicitly out of scope for this skill).

## Reference material

- **Runbook (Confluence):** [Unblocking Stuck MachineDeployment Drains via nodeDrainTimeoutSeconds](https://wiki.telekom.de/pages/viewpage.action?pageId=4047277759) — full procedure including emergency per-MachineSet patch. This skill implements the GitOps half.
- **Template MR:** `schiff/platform/infrastructure/cluster-components!16928` — *"a4/ipadb/dtrc tst: set deletionTimeoutMinutes=15 on stuck MachineDeployments"*, branch `fix/stuck-md-drain-timeout`, merged 2026-04-17.
- **AGENTS.md** — recurring PDB patterns (single-replica deadlock, dual-PDB conflict, ImagePullBackOff Artifactory 401).
- **KB incident** `7082d66c-9fe9-45fd-b296-19ad7dacab4e` — a4-3 gitlab-runner / Artifactory 401 PDB pattern.

## When to use

- `MachineDeploymentStuck` alert has fired and a CAPI Machine is in phase `Deleting` with `status.deletion.nodeDrainStartTime` older than ~2 hours.
- On the Machine (or the owning MachineSet) you observe `spec.deletion.nodeDrainTimeoutSeconds: 0` — i.e. the cluster is not yet using `deletionTimeoutMinutes`.
- Root cause is a tenant-side PDB / ImagePullBackOff / volume-detach issue that will take time to fix and you want to stop the upgrade from blocking indefinitely on future rolls.

Do **not** use this skill when:

- The drain is stuck because a BMH provisioned but the Node never joined (`NodeStartupTimeout`). That is not a drain problem — hand over the BMH via the `mark-bmh-defect` skill or investigate the provisioning image instead.
- The Machine is only briefly stuck (<2 h) on a transient ImagePullBackOff — fix the imagePullSecret (see AGENTS.md) instead.

## Inputs

- Affected cluster name(s), e.g. `a4-2`, `dtrc-2`.
- Affected MachineDeployment / worker pool name, e.g. `md-1`, `pool-tst-2`.
- Desired timeout in minutes (default and recommended: **15**).
- GitLab MR title + reason for the KB / commit message.

## Procedure

### 1. Confirm the symptom is a drain timeout (not a BMH issue)

```bash
# Active management cluster + namespace for the stuck cluster
kubectl config use-context <mgmt-cluster>

# Machine stuck in Deleting?
kubectl get machines -n <ns> \
  -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,DRAINSTART:.status.deletion.nodeDrainStartTime'

# Current drain timeout on the stuck Machine and its MachineSet
kubectl get machine -n <ns> <stuck-machine> \
  -o jsonpath='{.spec.deletion}{"\n"}'
# Expect: {"nodeDrainTimeoutSeconds":0,...}  → skill applies
```

If `nodeDrainTimeoutSeconds` is already non-zero, this skill is not the right fix — investigate the underlying blocker directly.

### 2. Identify the SchiffCluster and worker pool

The SchiffCluster YAMLs live in `schiff/platform/infrastructure/cluster-components`, commonly under `clusters.yaml` or per-cluster files. The field to edit is `spec.workers[].machineDeployment` for the pool whose MachineDeployment is stuck.

The mapping CAPI MachineDeployment name → SchiffCluster worker name typically follows `<cluster>-<worker.name>`, e.g. MachineDeployment `a4-2-md-1` comes from SchiffCluster `a4-2` worker `md-1`.

If unsure, use the `find-mgnt-cluster` skill to locate the SchiffCluster file and inspect `spec.workers`.

### 3. Edit the SchiffCluster — add `deletionTimeoutMinutes`

Add `deletionTimeoutMinutes: 15` under the affected worker's `machineDeployment` block. Example diff (from MR !16928 pattern):

```yaml
spec:
  workers:
    - name: md-1
      machineDeployment:
        replicas: 3
        deletionTimeoutMinutes: 15    # <-- add this
      # ... rest unchanged
```

Apply to every worker pool whose MachineDeployment is stuck or at risk. If multiple clusters are affected in the same management cluster / namespace, batch them in one MR (see MR !16928 which covered `a4-2`, `a4-4`, `a4-5`, `ipadb-1`, `dtrc-2`).

**Value choice:**

- `15` (= `nodeDrainTimeoutSeconds: 900`) is the standard recommendation — enough time for a well-behaved PDB-respecting drain, not so long that a bad PDB blocks upgrades for days.
- Do not set below `5`. A too-short timeout will force-evict pods during normal rolls.
- `deletionTimeoutMinutes` also maps to `nodeVolumeDetachTimeoutSeconds: 900`, which handles the `WaitingForVolumeDetach` case.

### 4. Regenerate the CAPI manifests

From the repo root, re-run the generator for each affected cluster:

```bash
schiff cluster create <cluster-name>
```

This updates the rendered manifests under `cluster-definitions/<cluster-name>/` — specifically the MachineDeployment YAML should now contain:

```yaml
spec:
  template:
    spec:
      deletion:
        nodeDeletionTimeoutSeconds: 0
        nodeDrainTimeoutSeconds: 900
        nodeVolumeDetachTimeoutSeconds: 900
```

Review the diff — only the three `deletion.*` fields on the affected MachineDeployment(s) should change.

### 5. Commit, push, MR

Branch name convention (from template MR): `fix/stuck-md-drain-timeout` or `fix/<cluster>-drain-timeout`.

Commit message template:

```text
<clusters>: set deletionTimeoutMinutes=15 on <workers>

Prevent MachineDeploymentStuck alerts from blocking upgrades when tenant
PDBs or drains misbehave. CAPI will now give up after 15 min and proceed
with node deletion instead of waiting indefinitely.

Refs MR !16928, runbook https://wiki.telekom.de/pages/viewpage.action?pageId=4047277759
```

Open the MR to `main`. Once merged, Flux reconciles the change onto each management cluster within minutes.

### 6. Verify Flux propagation

On each affected management cluster:

```bash
kubectl get machinedeployment -n <ns> <md-name> \
  -o jsonpath='{.spec.template.spec.deletion}{"\n"}'
# Expect: {"nodeDeletionTimeoutSeconds":0,"nodeDrainTimeoutSeconds":900,"nodeVolumeDetachTimeoutSeconds":900}
```

If Flux is slow:

```bash
flux -n schiff-system reconcile kustomization <kustomization>
```

### 7. What changes (and what does NOT)

- ✅ **New MachineSets** created for this MachineDeployment inherit the new timeout → future rolls are bounded.
- ✅ **Running Machines in the current MachineSet** also get the new timeout via the MachineSet template → their *next* drain (e.g. when replaced) is bounded.
- ❌ **Machines already in `Deleting` phase** keep the timeout they started with. They will remain stuck until either the drain unblocks organically or an operator applies the emergency per-MachineSet patch documented in the Confluence runbook.

If you need to unblock Machines that are already draining, stop here and follow the Confluence runbook's Step 3 (per-MachineSet `kubectl patch`) separately — that operation is mutating and out of scope for this GitOps skill. Always confirm with the user before running it.

### 8. Record in the KB

Store an incident via `kb_store_incident` with:

- `title`: `<clusters> MachineDeploymentStuck: set deletionTimeoutMinutes=15 (GitOps)`
- `root_cause`: tenant-specific PDB / ImagePullBackOff / volume-detach, plus the default `nodeDrainTimeoutSeconds=0` allowing indefinite blocking.
- `resolution`: SchiffCluster `deletionTimeoutMinutes: 15` + `schiff cluster create` + MR link.
- `tags`: `machinedeployment-stuck,capi,pdb,node-drain,deletiontimeoutminutes,gitops`
- `runbook_url`: https://wiki.telekom.de/pages/viewpage.action?pageId=4047277759

Cross-link the MR URL in the KB entry and the KB ID in the MR description.

## Safety rules

- **Read-only on clusters — mutating only via GitOps.** This skill does not run `kubectl patch` or `kubectl delete` against any cluster. All changes flow through `main` + Flux.
- **Do not set `deletionTimeoutMinutes` below 5 minutes.** Short timeouts will force-evict healthy pods during routine rolls.
- **Do not use this skill to "fix" a stuck Group-1 (BMH-provisioned-but-node-never-joined) alert** — it won't help; the Machine isn't waiting on drain, it's waiting on `providerID`. Use `mark-bmh-defect` or investigate the node image instead.
- **Coordinate with tenant teams** when the underlying blocker is a PDB — the timeout prevents your upgrade from hanging, but the tenant workload will still be disrupted (pod force-evicted after 15 min). Create a ticket for the tenant to fix the PDB root cause in parallel.
- **Always verify the Flux reconciliation** actually propagated `nodeDrainTimeoutSeconds: 900` onto the MachineDeployment before closing the incident.

## Fallbacks

- **`schiff cluster create` fails** — check the tool version and that the SchiffCluster YAML still validates. Compare against a clean worker block from MR !16928.
- **MR merged but MachineDeployment still shows `nodeDrainTimeoutSeconds: 0`** — Flux kustomization for that cluster may be failing. Check `flux get kustomizations -A` on the management cluster and its events.
- **Alert still firing after fix applied** — the already-`Deleting` Machines are not affected by the template change (see Step 7). Escalate to the emergency per-MachineSet patch in the Confluence runbook, with user confirmation.
- **Uncertain which management cluster owns the SchiffCluster** — use the `find-mgnt-cluster` skill.
