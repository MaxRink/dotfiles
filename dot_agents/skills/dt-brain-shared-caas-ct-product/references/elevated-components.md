# Elevated Components

## Overview

The **elevated-components-tdi** repository manages tenant-specific elevated RBAC permissions, Kyverno policy exceptions, and other cluster-level configurations that go beyond the standard T-CaaS platform defaults.

**Repository:** `https://gitlab.devops.telekom.de/cit/t-caas/tdi/elevated-components-tdi`

## Directory Structure

```
tenants/
├── <tenant>/                          # NatCo or org (clab, sk, mta, nfvi-caas, dummy)
│   ├── apps/
│   │   └── <vendor>/                  # Vendor name (mavenir, titanium, automation)
│   │       └── <app>/                 # Application (5gc, mco, sepp, sdv, vmas)
│   │           ├── RBAC/              # Vendor-wide RBAC (ClusterRoles, ClusterRoleBindings)
│   │           └── Kyverno/           # Vendor-wide Kyverno policy exceptions
│   └── clusters/
│       └── <cluster-name>/            # Cluster-specific overrides
│           ├── extra-rbac/                        # Additional RBAC for the cluster
│           ├── extra-app-rbac/                    # Additional app-specific RBAC
│           ├── extra-app-policy-exceptions/       # App-specific Kyverno exceptions
│           ├── extra-automation-policy-exceptions/ # Automation Kyverno exceptions
│           └── automation-policy-exceptions/      # MTA automation Kyverno exceptions
```

## Tenants

| Tenant | Description |
|--------|-------------|
| `clab` | Central Lab clusters (development, sandbox, PoC) |
| `sk` | Slovak Telekom (production 5GC) |
| `mta` | Magyar Telekom / Austria (SDV workloads) |
| `nfvi-caas` | Legacy NFVi-CaaS clusters |
| `dummy` | Template/example tenant |

## Common Content Types

| Directory | Contains | Example |
|-----------|----------|---------|
| `RBAC/` | ClusterRoles, ClusterRoleBindings for vendor deployments | Ericsson 5GC permissions, Mavenir RBAC |
| `Kyverno/` | ClusterPolicy exceptions (e.g., allow privileged containers, hostPath) | Vendor containers needing elevated privileges |
| `extra-rbac/` | Cluster-specific RBAC beyond the vendor defaults | Per-cluster permission overrides |
| `resources/` | Other K8s resources (ConfigMaps, Secrets, NetworkPolicies) | ISBC config, vMAS resources |

## Deployment

Resources are deployed via Flux/Kustomize. Each directory typically contains a `kustomization.yaml` listing the resources to apply.
