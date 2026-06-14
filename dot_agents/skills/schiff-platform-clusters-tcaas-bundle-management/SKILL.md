---
name: schiff-platform-clusters-tcaas-bundle-management
description: 'Manage T-CaaS Bundles, FunctionDefinitions, and cluster software. USE WHEN: creating or bumping FunctionDefinition versions, fixing missing FDs, debugging bundle references, understanding FD dependencies, working with hack.py, fixing function repos, Flux GitOps workflow, kustomize namespace issues, adding FD yaml to bundles, dev tag for FD, releases.git vs releases-dev.git, bundles-fds-sync, semver tag for function, FD from CI. Keywords: Bundle, FunctionDefinition, FunctionInstance, hack.py, version bump, semver, bundles repo, t-caas-operator-system, Flux, kustomize, releases-sync, GitRepository, glab, releases.git, dev.0, bundles-fds-sync.'
---

<!-- Imported from schiff/platform/clusters/.github/skills/tcaas-bundle-management by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS Bundle Management

## Overview

T-CaaS uses a Bundle/FunctionDefinition system to define what software gets deployed to clusters. Bundles reference FunctionDefinitions, which define Helm/Kustomize releases. All live in namespace `t-caas-operator-system`.

**Source of truth is Git — Flux reconciles everything.** Never fix things by `kubectl apply/patch` on the cluster directly; changes will be rolled back by Flux. Always fix at the source (function repo, bundles repo, or clusters repo) and let Flux propagate.

## CRITICAL: Never Add FunctionDefinition Yamls to the Bundles Repo

**NEVER add FunctionDefinition yamls to `functiondefinitions/` in the bundles repo.** FDs from CI are automatically synced to clusters via the `releases-sync` Flux GitRepository — no manual copy is needed or correct.

### Why
The `releases-sync` GitRepository in `t-caas-operator-system` syncs directly from `releases.git`. Adding FD yamls to the bundles repo duplicates this, creates maintenance burden, and was a mistake that caused confusion.

### Correct Workflow: Get a New FD Onto a Cluster

```bash
# 1. Tag the function repo with a semver pre-release tag (NO 'v' prefix!)
cd functions/<component>/
git tag 0.5.0-dev.0
git push origin 0.5.0-dev.0
# Tags matching ^[0-9]+\.[0-9]+\.[0-9]+(|-.+)$ → publish to releases.git with clean names
# MR pipelines → releases-dev.git with messy branch-slug+IID names — only use for quick local iteration

# 2. Wait for CI pipeline on that tag to succeed

# 3. Flux automatically syncs the FD — NO ignore-list changes needed
# releases-sync and releases-dev-sync are configured to sync all FDs without filters
flux reconcile source git releases-sync -n t-caas-operator-system
# Verify:
kubectl get fd -n t-caas-operator-system | grep "<component>"

# 4. Update Bundle to reference the new FD name and push
```

### Semver Tag Naming

| Tag Pattern | Where Published | FD Name Example |
|-------------|----------------|------------------|
| `0.5.0-dev.0` | `releases.git` ✅ | `kube-proxy-0.5.0-dev.0` |
| `0.5.0-rc.1` | `releases.git` ✅ | `kube-proxy-0.5.0-rc.1` |
| `0.5.0` | `releases.git` ✅ | `kube-proxy-0.5.0` |
| MR pipeline (no tag) | `releases-dev.git` ❌ | `kube-proxy-0.4.3-fix-branch-name.42` (messy — do not use) |

## Key Resources

| Kind | Naming Pattern | Location |
|------|----------------|----------|
| `Bundle` | `{provider}-{role}-{semver}` | `bundles/{provider}/` |
| `FunctionDefinition` | `{name}-{semver}` | `functiondefinitions/{component}/` |

**Critical rule:** `metadata.name` MUST match filename (without `.yaml`).

## Flux GitOps Architecture

Three Flux GitRepositories drive the platform:

| GitRepository | Namespace | Source | Purpose |
|---------------|-----------|--------|---------|
| `t-caas-clusters-sync` | `t-caas-controllers` | clusters repo (`main`) | TCaasClusters, SharedConfigs, tenants, IDPProviders |
| `t-caas-bundles-sync` | `t-caas-controllers` | bundles repo (branch varies) | Bundles, FDs, profiles, bootstrap configs |
| `releases-sync` | `t-caas-operator-system` | `releases.git` (stable tags) | All FDs published by CI tag pipelines |
| `releases-dev-sync` | `t-caas-operator-system` | `releases-dev.git` (dev/MR) | All FDs from dev tags and MR pipelines |

**Key detail:** The bundles repo may track a non-main branch (e.g., `vsr-converged-bootstrap-config`). Check the GitRepository to see which branch Flux syncs.

### Force Flux Reconciliation

```bash
# Reconcile a specific source
flux reconcile source git t-caas-bundles-sync -n t-caas-controllers
flux reconcile source git t-caas-clusters-sync -n t-caas-controllers
flux reconcile source git releases-sync -n t-caas-operator-system
flux reconcile source git releases-dev-sync -n t-caas-operator-system

# Reconcile a kustomization
flux reconcile kustomization t-caas-bundles-sync -n t-caas-controllers
flux reconcile kustomization t-caas-clusters-sync -n t-caas-controllers
```

## Git-Based Workflow: Fixing a FunctionDefinition

**NEVER patch around issues on the cluster.** Always fix at the source through Git:

### Full Workflow

```
1. Fix in function repo → 2. Create MR → 3. Tag new version → 4. CI publishes →
5. Create new FD in bundles repo → 6. Update bundle ref → 7. Update releases-sync →
8. Commit & push → 9. Flux reconciles
```

### Step-by-Step

#### 1. Fix the Function Source

```bash
cd functions/<component>/
git checkout -b fix/<description>
# Edit definition.yaml or other sources
git add -A && git commit -m "fix: <description>"
git push -u origin fix/<description>
```

#### 2. Create a Merge Request

```bash
/home/a92615428/go/bin/glab mr create \
  --title "fix: <description>" \
  --target-branch main \
  --source-branch fix/<description>
```

#### 3. Tag a New Version

**CRITICAL: Tags must NOT have a `v` prefix.** CI regex: `^[0-9]+\.[0-9]+\.[0-9]+(|-.+)$`

```bash
# Correct:
git tag 0.3.0-rc.1 && git push origin 0.3.0-rc.1

# WRONG (CI will skip it):
git tag v0.3.0-rc.1   # ← NO! No 'v' prefix!
```

Wait for CI pipeline to succeed (publishes the release artifact).

#### 4. Create New FD in Bundles Repo

```bash
cd bundles/
cp functiondefinitions/<component>/<latest>.yaml \
   functiondefinitions/<component>/<new-version>.yaml
# Update metadata.name to match filename
# Update release source refs (tag, version, etc.)
```

#### 5. Update Bundle to Reference New FD

```bash
# Edit bundles/<provider>/<bundle>.yaml
# Update the functionDefinitionRef for this component
```

#### 6. Update releases-sync (if needed)

If the FD references kustomize releases from the releases repo, add the new version to the releases-sync GitRepository ignore list:

```bash
# Edit mgmt-clusters/<cluster>/self/configs/gitrepositories/releases-sync_t-caas-operator-system.yaml
# Add: !/<component>/<new-version>/**
```

#### 7. Commit, Push, Wait for Flux

```bash
git add -A && git commit -m "feat: bump <component> to <version>" && git push
# Force Flux reconciliation if impatient:
flux reconcile source git t-caas-bundles-sync -n t-caas-controllers
```

### Merging Function MRs

```bash
cd functions/<component>/
# Merge with squash:
/home/a92615428/go/bin/glab mr merge <MR-number> --squash --yes
# Or via API:
/home/a92615428/go/bin/glab api -X PUT \
  "projects/<url-encoded-path>/merge_requests/<id>/merge" -f squash=true
```

## Kustomize Namespace Transformation Gotcha

**CRITICAL:** Kustomize applies patches BEFORE the `targetNamespace` transformation.

If a FunctionDefinition uses kustomize with `targetNamespace: t-caas-breakglass`, but the source manifests define resources in `namespace: breakglass-system`:

- **Patches must target the SOURCE namespace** (`breakglass-system`), NOT the final namespace (`t-caas-breakglass`)
- Kustomize order: load bases → apply patches → apply namespace transformation
- If patches target the wrong namespace, they silently fail to match (no error, just no effect)

**Example of the bug:**
```yaml
# WRONG - targets transformed namespace (patch won't match)
patches:
  - target:
      kind: Deployment
      namespace: t-caas-breakglass    # ← WRONG
    patch: |
      ...

# CORRECT - targets source namespace
patches:
  - target:
      kind: Deployment
      namespace: breakglass-system    # ← matches source manifests
    patch: |
      ...
```

**Symptoms when wrong:** Pods deploy but patches aren't applied (e.g., missing imagePullSecrets, wrong args). No kustomize error — patches just silently don't match.

## Creating a FunctionDefinition

When a bundle references a FD that doesn't exist:

### 1. Find the Source

Check the `functions/` repo for the component's `definition.yaml`:
```bash
ls functions/<component>/
cat functions/<component>/definition.yaml
```

### 2. Find the Latest Existing Version

```bash
ls bundles/functiondefinitions/<component>/
# e.g., calico-0.4.0.yaml, calico-0.4.1.yaml, ...
```

### 3. Create the New Version

```bash
# Copy latest version
cp functiondefinitions/<component>/<latest>.yaml \
   functiondefinitions/<component>/<new-version>.yaml

# Update metadata.name to match filename
# Update any changed references (images, charts, config)
```

### 4. Apply Locally (for testing)

```bash
kubectl apply -f functiondefinitions/<component>/<new-version>.yaml
```

**Note:** Direct `kubectl apply` changes will be overwritten by Flux. Only use for emergency testing. For permanent fixes, commit to Git.

### CRD Validation Gotchas

When manually creating FDs, watch for these validation constraints:
- **`spec.name`**: Maximum 50 chars. Must be a valid label value and start with a letter.
- **`metadata.name`**: Must match `{spec.name}-{semver}` (e.g. `calico-0.5.0`). Must be a valid DNS-1123 subdomain.
- **`metadata.namespace`**: Must be `t-caas-operator-system`.
- **Input names**: Must match pattern `[a-z][a-z0-9]+` (lowercase alphanumeric, starting with letter, at least 2 chars). Names must be unique.
- **Input type vs schema**: Mutually exclusive — set `type` (string/integer/float/boolean) OR `schema`, not both. Complex types (array, object) must use `schema`.
- **Releases**: Max 20. Each must have exactly one of `helm` or `kustomize` (XOR). Names must be unique. Helm releases require `releaseName`.
- **`spec.releases[].kustomize.build`**: May not exist in older CRD versions. Use `path` directly under `kustomize` instead.
- **Always test against the deployed CRD**, not the latest in the bundles repo. Use `kubectl apply --validate=false` as a last resort if schema validation fails on valid content.
- **`--validate=false`** bypasses client-side validation but webhook validation still applies.

### Build-Time Validation (`tcaas build`)

The `tcaas-cli` now validates FunctionDefinitions at two stages during `tcaas build`, catching errors before they reach the Kubernetes API server:

**1. At load time** (`ValidateFunctionDefinition`): validates the `definition.yaml`
- `spec.name` max length (50 chars)
- Input name pattern, uniqueness, type enum, type XOR schema
- Release count (max 20), name uniqueness, helm XOR kustomize

**2. At export time** (`ValidateGeneratedFunctionDefinitionManifest`): validates the generated manifest
- `metadata.name` DNS-1123 compliance and `{spec.name}-{semver}` pattern
- `metadata.namespace` must be `t-caas-operator-system`
- `spec.name` must be a valid label value
- All input and release rules from stage 1
- `helm.releaseName` required

This catches issues like invalid input types (e.g. `type: array` instead of using `schema`) at build time instead of at `kubectl apply` time.

## Using hack.py

The `functiondefinitions/hack.py` script automates version bumps:

```bash
# Bump ALL functions + all affected bundles
python functiondefinitions/hack.py

# Bump specific function(s)
python functiondefinitions/hack.py --function calico
python functiondefinitions/hack.py --function calico --function coil

# Run from repo root or functiondefinitions/ directory
```

**What it does:**
1. Scans all FDs, validates name-file consistency
2. Applies config path migration patches
3. Bumps FD versions (patch or prerelease)
4. Deduplicates if new version is identical to latest
5. Updates bundles referencing bumped FDs

## SharedConfig Management

SharedConfig provides global platform settings referenced by TCaasCluster.

### Upgrading SharedConfig Version

1. Create the new SharedConfig file (or verify it exists):
   ```bash
   ls clusters/configs/SharedConfig/
   ```

2. Add it to the kustomization resources:
   ```bash
   # Edit clusters/configs/SharedConfig/kustomization.yaml
   # Add the new file to the resources list
   ```

3. Update TCaasCluster to reference the new version:
   ```yaml
   spec:
     config:
       ref:
         name: <new-sharedconfig-name>
   ```

4. Commit & push to clusters repo (auto-synced by Flux on `main` branch).

### Key SharedConfig Differences (example: 0.1.0 → 0.2.0)

- Removed unused container registry mirrors (dockerIo, gcrIo, ghcrIo, registryK8sIo, quayIo)
- Updated `capiProviders` path
- Changed registry configuration structure

**Impact:** FDs that reference missing SharedConfig fields (e.g., `.config.sources.registry.mirrors.dockerIo`) will fail to render. Ensure FDs are compatible with the SharedConfig version.

## FunctionDefinition Structure

```yaml
apiVersion: t-caas.telekom.com/v1alpha1
kind: FunctionDefinition
metadata:
  name: calico-0.5.0           # MUST match filename
  namespace: t-caas-operator-system
spec:
  dependencies:
    requires: [prerequisites, cni-config]  # must deploy first
    provides: [cni]                         # capability offered
  releases:
    - name: calico
      type: kustomize           # or helm
      source:
        type: git               # or oci
        # ... source details with Go template variables
  schema: |                     # OpenAPI v3 schema for inputs
    type: object
    properties: ...
```

## Debugging FunctionInstance Issues

```bash
# List all FIs with status
kubectl get fi -n <cluster-ns>

# Check specific FI
kubectl get fi <name> -n <cluster-ns> -o yaml

# Find what FD a FI references
kubectl get fi <name> -n <cluster-ns> -o jsonpath='{.spec.functionDefinitionRef}'

# Check if the referenced FD exists
kubectl get fd <fd-name> -n t-caas-operator-system

# List all FDs
kubectl get fd -n t-caas-operator-system

# Quick status summary (count by phase)
kubectl get fi -n <cluster-ns> --no-headers | awk '{print $4}' | sort | uniq -c | sort -rn
```

### Common FI Issues

| Status | Cause | Fix |
|--------|-------|-----|
| `Failed` + "not found" | Missing FunctionDefinition | Create the FD in bundles repo, commit, let Flux sync |
| `WaitingForDependencies` | Upstream FI not ready | Fix the upstream FI first (check dependency chain) |
| `Failed` + source error | Flux source (OCIRepo/GitRepo) failing | Check source auth/URL, releases-sync ignore list |
| `Deploying` indefinitely | Workload cluster API unreachable | Fix control plane first |
| `Failed` + template error | SharedConfig field missing | Check SharedConfig version compatibility with FD |
| `ImagePullBackOff` on pods | Kustomize patch didn't apply (namespace mismatch) | Check patch target namespace matches source namespace |
| `CrashLoopBackOff` on pods | Broken entrypoint/config in release | Fix in function repo, tag new version, update FD |

### FI Dependency Chain

FIs deploy in dependency order (DAG). If one fails, all downstream FIs show `WaitingForDependencies`.

Typical ordering:
```
prerequisites → certs → kube-proxy/meta-cni-config → calico (provides: cni) →
coredns/flux/multus → auth-operator → kyverno → tenant-resources → ...
```

Find the root blocker:
```bash
# Show failed FIs
kubectl get fi -n <cluster-ns> --no-headers | grep -v Deployed | grep -v WaitingForDependencies
```

## TCaasCluster Phases

| Phase | Meaning |
|-------|---------|
| `Provisioning` | Infrastructure being set up (machines, network, storage) |
| `DeployingBundle` | FIs being deployed (may show even when all FIs are Deployed — wait for reconciliation) |
| `Deployed` | All FIs deployed successfully |
| `UpgradingBundle` | Bundle version changed, FIs being updated |
| `Deleting` | Cluster being torn down |

## Bundle References

To see what FDs a bundle references:
```bash
kubectl get bundle <name> -n t-caas-operator-system -o yaml | grep -A2 "functionDefinitionRef"
```

To find which bundle a cluster uses:
```bash
kubectl get tcaascluster <name> -n <ns> -o jsonpath='{.spec.bundle.ref}'
```

## Go Template Variables in FDs

FDs use Go templates that get resolved at deploy time:

| Variable | Source |
|----------|--------|
| `.config.sources.registry` | SharedConfig registries |
| `.config.sources.helm` | SharedConfig Helm repos |
| `.config.sources.git.platform` | SharedConfig Git repos |
| `.config.bundle.*` | Per-function config from SharedConfig |
| `.inputs.*` | User-provided values |
| `.network.pod.ipv4.cidr` | Network profile |
| `.tenant.*` | TCaasTenant data |
| `.cluster.*` | Cluster info (provider, env, location) |

## Validation

```bash
# Render a FD locally (from t-co repo)
go run . bundle functiondefinition render <fd.yaml> \
    --cluster-context-file-path test/samples/bundle/render/context-full.yaml

# Validate with kubeconform
kubeconform -ignore-missing-schemas <fd.yaml>
```

## Management Cluster Self-Upgrade

The mgmt cluster manages itself via Flux. To upgrade mgmt cluster FIs:

1. Create/update FDs in bundles repo
2. Create new bundle version referencing updated FDs
3. Update releases-sync GitRepository ignore list (clusters repo)
4. Update TCaasCluster spec to reference new bundle
5. Optionally update SharedConfig reference
6. Commit & push both repos
7. Force Flux reconciliation if needed

**Key difference from workload clusters:** The mgmt cluster's Flux runs ON the mgmt cluster itself, so changes are self-referential. Be careful with changes that could break Flux's own reconciliation loop.
