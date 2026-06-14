---
name: schiff-platform-clusters-tcaas-function-deployment
description: End-to-end pipeline for deploying a T-CaaS function (operator image + Helm chart + function definition + bundle update + flux sync)
---

<!-- Imported from schiff/platform/clusters/.github/skills/tcaas-function-deployment by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS Function Deployment Pipeline

## Overview

Deploying a T-CaaS function involves a multi-stage pipeline across several repositories. Each stage must complete successfully before proceeding to the next.

## Full Pipeline Sequence

### 1. Tag the Operator Repository

Create a semantic version tag on the operator repo. This triggers CI to build and publish the container image and Helm chart.

```bash
git tag v0.X.Y
git push origin v0.X.Y
```

### 2. CI Publishes Chart and Image

CI automatically:
- Builds the container image
- Pushes the image to the OCI registry
- Packages and publishes the Helm chart

**GOTCHA: Image tag is branch-derived, not git-tag-derived.** The CI pipeline derives the image tag from the branch name (e.g., `main` becomes a sanitized slug), NOT from the git tag. Check `.gitlab-ci.yml` or the pipeline output to confirm the actual image tag used.

### 3. Tag the Function Repository

Once the chart and image are published, tag the function definition repository:

```bash
git tag v0.X.Y
git push origin v0.X.Y
```

### 4. Publish the Function Definition

The function definition CI publishes the function manifest (HelmRelease template, values schema, etc.) to the function registry.

### 5. Update the Bundle

In the clusters repo, update the bundle to reference the new function version:

```yaml
# bundles/<bundle-name>/functions.yaml
- name: t-caas-integrations-operator
  version: 0.X.Y
```

### 6. Flux Sync

Flux detects the bundle change and reconciles the HelmRelease in the target cluster.

```bash
# Force immediate reconciliation
flux reconcile source git <source-name> -n flux-system
flux reconcile kustomization <kustomization-name> -n flux-system
```

## Key Gotchas

### Image Tag is Branch-Derived

The container image tag is derived from the CI branch, NOT the git tag. For example:
- Branch `main` produces image tag like `main-<short-sha>` or similar
- The git tag `v0.5.0` does NOT produce an image tagged `v0.5.0` unless CI is explicitly configured to do so

Always verify the actual image tag from the CI pipeline output before updating values.

### Chart Values Must Use Flat Structure

The function template renders chart values using a flat key structure. Do NOT nest values under arbitrary keys:

```yaml
# CORRECT - flat structure
image: registry.example.com/org/operator:tag
featureGates:
  zamIntegration: true
operator:
  replicas: 1

# WRONG - nested under chart name
t-caas-integrations-operator:
  image: registry.example.com/org/operator:tag
```

### image-extraction-values.yaml Must Match CI Tag

The `image-extraction-values.yaml` file in the function repo must specify the exact image tag that CI produced. If there is a mismatch, the image will not be found during deployment:

```yaml
image:
  registry: mtr.devops.telekom.de
  repository: cit/t-caas/t-caas-integrations-operator
  tag: "main-abc1234"  # Must match actual CI output
```

### Never Reuse Tags

Never reuse a git tag (deleting and re-creating). This causes:
- Registry caching issues (old artifacts served)
- Flux not detecting changes (same semver = no upgrade)
- Confusion in audit trails

If a tag was published with errors, bump to the next patch version.

## Iterative Debugging Process

When a deployment fails, work through the chain:

1. **Check image exists:** `crane manifest <registry>/<repo>:<tag>`
2. **Check chart exists:** `helm show chart oci://<registry>/<chart> --version <version>`
3. **Check function definition:** Verify the function manifest references correct chart version and image
4. **Check bundle:** Confirm the bundle references the correct function version
5. **Check flux:** `flux get helmreleases -A | grep <name>` and inspect events
6. **Check pod:** `kubectl describe pod` for image pull errors or crash loops

```bash
# Quick diagnostic sequence
crane manifest mtr.devops.telekom.de/cit/t-caas/t-caas-integrations-operator:<tag>
flux get sources chart -A | grep integrations
flux get helmreleases -A | grep integrations
kubectl -n <ns> get pods -l app.kubernetes.io/name=t-caas-integrations-operator
kubectl -n <ns> describe pod <pod-name>
kubectl -n <ns> logs <pod-name> --tail=50
```
