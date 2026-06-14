---
name: schiff-platform-clusters-tcaas-flux-sync-debugging
description: 'Debug Flux GitOps sync issues for T-CaaS clusters — GitRepository, Kustomization, OCI sources, FD sync failures. USE WHEN: FunctionDefinitions not appearing on cluster, Flux kustomization stuck, GitRepository not picking up new commits, OCI repository SourcesNotReady, releases-sync ignore list blocking FDs, force reconciliation needed. Keywords: Flux, GitRepository, Kustomization, OCIRepository, releases-sync, bundles-sync, reconcile, sync, SourcesNotReady, FD not found, force reconcile, spec.ignore.'
---

<!-- Imported from schiff/platform/clusters/.github/skills/tcaas-flux-sync-debugging by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS Flux Sync Debugging

## Overview

T-CaaS uses Flux to sync Git repositories into the management cluster. FunctionDefinitions, Bundles, TCaasClusters, and SharedConfigs all flow from Git repos through Flux Kustomizations. When FDs don't appear or updates don't propagate, the issue is usually in the Flux sync chain.

## Flux Sync Architecture

```
Git Repos → GitRepository (source) → Kustomization (applies to cluster)
OCI Repos → OCIRepository (source) → HelmRelease/Kustomization (deploys to workload)
```

### Key Flux Resources

| Resource | Namespace | Source Repo | Purpose |
|----------|-----------|-------------|---------|
| `releases-sync` (GitRepo) | `t-caas-operator-system` | `functions/releases` | FDs from CI-generated releases |
| `releases-sync` (Kustomization) | `t-caas-operator-system` | ↑ | Applies FDs to cluster |
| `bundles-sync` (GitRepo) | `t-caas-operator-system` | `software/bundles` | Bundles, profiles, bootstrap configs |
| `bundles-fds-sync` (Kustomization) | `t-caas-operator-system` | ↑ | Applies FDs from bundles |
| `bundles-bundles-sync` (Kustomization) | `t-caas-operator-system` | ↑ | Applies Bundle CRs |
| `t-caas-clusters-sync` (Kustomization) | `t-caas-controllers` | clusters repo | TCaasClusters, SharedConfigs |

## Debugging: FD Not Appearing on Cluster

### 1. Verify FD Exists in Git

```bash
cd functions/releases
git fetch origin main
git log origin/main --oneline -5
# Look for: "Add manifests for <component> version <version>"

# Check file exists:
ls <component>/<component>-<version>.yaml
```

### 2. Check GitRepository Source

```bash
# Is the GitRepository fetching the latest commit?
kubectl -n t-caas-operator-system get gitrepository releases-sync \
  -o jsonpath='{.status.artifact.revision}'
# Compare with: git log origin/main --oneline -1
```

If the revision doesn't match the latest commit, the GitRepository hasn't synced yet.

### 3. Check for spec.ignore Blocking

```bash
kubectl -n t-caas-operator-system get gitrepository releases-sync -o yaml | grep -A 100 "ignore:"
```

If `spec.ignore` uses `/*` (exclude all) with explicit includes, new FDs won't sync unless added to the include list. **Fix options:**

**Option A: Remove spec.ignore entirely** (preferred for dev clusters):
```bash
# Live fix (will be reverted by Flux if source file has ignore):
kubectl -n t-caas-operator-system patch gitrepository releases-sync \
  --type=json -p='[{"op":"remove","path":"/spec/ignore"}]'

# Permanent fix: edit the source file in clusters repo
# mgmt-clusters/<cluster>/self/configs/gitrepositories/releases-sync_t-caas-operator-system.yaml
```

**Option B: Add the new FD path to the include list:**
```yaml
spec:
  ignore: |
    /*
    !/<component>/<component>-<version>.yaml
```

### 4. Check Kustomization Status

```bash
kubectl -n t-caas-operator-system get kustomization releases-sync \
  -o jsonpath='{.status.conditions}' | python3 -m json.tool
```

Look for:
- `ReconciliationSucceeded` — sync is working
- `ReconciliationFailed` — check the error message
- Compare `lastAppliedRevision` with GitRepository's `artifact.revision`

### 5. Force Reconciliation

```bash
# Force GitRepository to re-fetch
kubectl -n t-caas-operator-system annotate gitrepository releases-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite

# Force Kustomization to re-apply
kubectl -n t-caas-operator-system annotate kustomization releases-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite

# Wait ~30s, then verify:
kubectl -n t-caas-operator-system get fd <component>-<version>
```

## Debugging: OCI Source Not Ready

FunctionInstances reference OCI artifacts for Helm charts/Kustomize overlays. If FI shows `SourcesNotReady`:

### 1. Check OCIRepository Status

```bash
# Find the OCI repos for the FI:
kubectl -n t-caas-operator-system get ocirepository | grep <component>

# Check status:
kubectl -n t-caas-operator-system get ocirepository <name> -o yaml | grep -A 10 "status:"
```

### 2. Common OCI Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `authentication required` | Missing/expired credentials | Check `imagePullSecret` in namespace |
| `manifest unknown` | OCI artifact doesn't exist yet | Wait for CI to publish, or check CI pipeline |
| `timeout` | Network/firewall issue | Check connectivity to registry |

### 3. OCI Repo Takes Time

After CI pushes a new artifact, OCIRepository needs 1-5 minutes to detect and pull it. The FI will show `SourcesNotReady` until all OCI sources report `Ready: True`:

```bash
# Monitor OCI repo readiness:
watch 'kubectl -n t-caas-operator-system get ocirepository | grep <component>'
```

## Debugging: Bundle Not Syncing

### Check bundles-sync GitRepository Branch

```bash
kubectl -n t-caas-operator-system get gitrepository bundles-sync \
  -o jsonpath='{.spec.ref}'
```

**Important:** The bundles GitRepository might track a non-main branch (e.g., `vsr-converged-bootstrap-config`). Commits to `main` won't sync if Flux is watching a different branch.

### Force Bundle Sync

```bash
kubectl -n t-caas-operator-system annotate gitrepository bundles-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite
kubectl -n t-caas-operator-system annotate kustomization bundles-bundles-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite
kubectl -n t-caas-operator-system annotate kustomization bundles-fds-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite
```

## Debugging: TCaasCluster Not Updating

### Check clusters-sync

```bash
# Find the kustomization
kubectl -n t-caas-controllers get kustomization | grep cluster

# Check last applied revision
kubectl -n t-caas-controllers get kustomization t-caas-clusters-sync \
  -o jsonpath='{.status.lastAppliedRevision}'

# Force reconcile
kubectl -n t-caas-controllers annotate kustomization t-caas-clusters-sync \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite
```

## Quick Diagnostic Script

```bash
#!/bin/bash
# Run on management cluster (unset KUBECONFIG)
echo "=== GitRepository Status ==="
kubectl -n t-caas-operator-system get gitrepository -o custom-columns=\
NAME:.metadata.name,READY:.status.conditions[0].status,REVISION:.status.artifact.revision

echo ""
echo "=== Kustomization Status ==="
kubectl -n t-caas-operator-system get kustomization -o custom-columns=\
NAME:.metadata.name,READY:.status.conditions[0].status,MESSAGE:.status.conditions[0].message

echo ""
echo "=== FDs not Ready ==="
kubectl -n t-caas-operator-system get fd | grep -v "True"

echo ""
echo "=== FIs not Deployed ==="
kubectl -n <cluster-ns> get fi | grep -v Deployed
```

## Live Fix vs Permanent Fix

| Action | Live Fix (kubectl) | Permanent Fix (Git) |
|--------|-------------------|---------------------|
| Remove spec.ignore | `kubectl patch gitrepository ...` | Edit file in clusters repo, push |
| Force reconcile | `kubectl annotate ...` | N/A (one-time action) |
| Add missing FD | `kubectl apply -f <fd.yaml>` | Commit FD to releases/bundles repo |
| Fix TCaasCluster | `kubectl edit tcaascluster` | Edit in clusters repo, push |

**Rule:** Live fixes via kubectl will be reverted by Flux on next sync cycle. Always follow up with the permanent Git fix. The only exception is `annotate reconcile.fluxcd.io/requestedAt` which is a trigger, not state.

## Sync Intervals

| Resource | Default Interval | Notes |
|----------|-----------------|-------|
| GitRepository | 2-5m | Time to detect new commits |
| Kustomization | 5m | Time to re-apply after source update |
| OCIRepository | 5m | Time to detect new OCI artifacts |
| HelmRelease | 5m | Time to reconcile Helm state |

**Total worst-case delay:** Up to 10-15 minutes from Git push to workload deployment (GitRepo poll + Kustomization apply + FI reconcile + OCI pull + HelmRelease). Use force reconcile to skip wait times.
