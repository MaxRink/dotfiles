---
name: schiff-platform-clusters-tcaas-integrations-operator-deployment
description: Deploying the T-CaaS integrations operator — chart values, env vars, feature gates, RBAC, and cross-namespace limitations
---

<!-- Imported from schiff/platform/clusters/.github/skills/tcaas-integrations-operator-deployment by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS Integrations Operator Deployment

## Overview

The T-CaaS integrations operator is deployed via a Helm chart that uses a flat values structure rendered by the T-CaaS function template system. This document covers the specific deployment concerns for this operator.

## Chart Values Structure

The chart uses flat top-level keys. Values are NOT nested under the chart name because the function template renders them directly:

```yaml
# values.yaml — flat structure required by function template
image: mtr.devops.telekom.de/cit/t-caas/t-caas-integrations-operator:main-abc1234

featureGates:
  zamIntegration: true
  resourceSyncIntegration: false
  teleSecIntegration: true
  objectStorageIntegration: false

operator:
  replicas: 1
  logLevel: info
```

**Do NOT nest values under a chart name key:**

```yaml
# WRONG — function template will not find these values
t-caas-integrations-operator:
  image: ...
  featureGates: ...
```

## Environment Variable Fallback

The operator binary accepts configuration via CLI flags with environment variable fallbacks:

| CLI Flag | Env Var | Required | Description |
|----------|---------|----------|-------------|
| `--management-cluster-id` | `MANAGEMENT_CLUSTER_ID` | Yes | Unique ID of the management cluster |
| `--namespace` | `OPERATOR_NAMESPACE` | No | Namespace where the operator runs (default: auto-detected) |

In the Helm chart, these are typically set via:

```yaml
env:
  - name: MANAGEMENT_CLUSTER_ID
    value: "{{ .Values.managementClusterId }}"
  - name: OPERATOR_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
```

If neither the CLI flag nor the env var is set, the operator will fail to start with a clear error message.

## Feature Gates

Feature gates control which controllers are registered at startup. They are passed as a comma-separated list to the `--feature-gates` CLI argument:

```bash
# CLI format
--feature-gates=ZAMIntegration=true,ResourceSyncIntegration=true,TeleSecIntegration=true

# In Helm values
featureGates:
  zamIntegration: true
  resourceSyncIntegration: true
  teleSecIntegration: true
  objectStorageIntegration: false
```

The chart template converts the values map to the CLI format:

```yaml
args:
  - --feature-gates={{ include "featureGates" . }}
```

### Available Feature Gates

| Gate | Stage | Default | Description |
|------|-------|---------|-------------|
| `ZAMIntegration` | Alpha | false | ZAM compliance controllers |
| `ResourceSyncIntegration` | Alpha | false | Cross-cluster resource sync |
| `TeleSecIntegration` | Alpha | false | TeleSec ACME certificate provisioning |
| `ObjectStorageIntegration` | Alpha | false | S3 object storage lifecycle |

**Important:** Enabling a feature gate without the corresponding CRDs installed will cause the operator to crash on startup. Always ensure CRDs are applied before enabling a gate.

## RBAC: New CRDs Need ClusterRole Update

When adding a new CRD to the operator, the ClusterRole must be updated to grant permissions. The RBAC manifests are generated from controller annotations:

```go
//+kubebuilder:rbac:groups=compliance.tcaas.telekom.de,resources=zamconfigs,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=compliance.tcaas.telekom.de,resources=zamconfigs/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=compliance.tcaas.telekom.de,resources=zamconfigs/finalizers,verbs=update
```

After adding annotations, regenerate:

```bash
make manifests
```

The generated ClusterRole in `config/rbac/role.yaml` must be included in the chart. If the ClusterRole is not updated, the operator will log RBAC errors like:

```
Failed to watch *v1alpha1.ZAMConfig: failed to list *v1alpha1.ZAMConfig: zamconfigs.compliance.tcaas.telekom.de is forbidden
```

### Verifying RBAC in Cluster

```bash
# Check what the service account can do
kubectl auth can-i list zamconfigs.compliance.tcaas.telekom.de \
  --as=system:serviceaccount:<namespace>:t-caas-integrations-operator

# Check ClusterRole bindings
kubectl get clusterrolebinding | grep integrations
kubectl describe clusterrole t-caas-integrations-operator
```

## Cross-Namespace Owner Reference Limitation

Kubernetes does not allow owner references to span namespaces. This means:

- A cluster-scoped resource (e.g., ClusterRole) cannot be owned by a namespace-scoped resource
- A resource in namespace A cannot have an owner reference pointing to a resource in namespace B

The operator works around this by:
1. Using finalizers instead of owner references for cross-namespace cleanup
2. Storing the "logical owner" reference in labels/annotations rather than `metadata.ownerReferences`
3. Implementing explicit garbage collection in the reconciler's cleanup phase

**Impact on deployment:** If the operator namespace changes, existing finalizers on resources in other namespaces will become orphaned. The old operator instance must complete cleanup before the new instance starts, or manual finalizer removal is required:

```bash
# Remove orphaned finalizer manually (use with caution)
kubectl patch <resource> <name> -n <namespace> \
  --type=json -p='[{"op": "remove", "path": "/metadata/finalizers/0"}]'
```

## Deployment Verification

After deploying, verify the operator is healthy:

```bash
# Check pod is running
kubectl -n <namespace> get pods -l app.kubernetes.io/name=t-caas-integrations-operator

# Check logs for startup errors
kubectl -n <namespace> logs -l app.kubernetes.io/name=t-caas-integrations-operator --tail=50

# Verify feature gates are active
kubectl -n <namespace> logs -l app.kubernetes.io/name=t-caas-integrations-operator | grep "feature gate"

# Check CRD registration
kubectl get crd | grep tcaas.telekom.de

# Verify controller is reconciling
kubectl -n <namespace> logs -l app.kubernetes.io/name=t-caas-integrations-operator | grep "Reconciling"
```
