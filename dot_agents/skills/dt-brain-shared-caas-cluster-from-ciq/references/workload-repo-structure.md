# Workload Repo Structure

The workload repo (`tdi-caas/runtime/workload` on GitLab) stores all converged cluster
TCaasCluster definitions managed by T-CO (T-CaaS Operator).

**GitLab URL**: `https://gitlab.devops.telekom.de/tdi-caas/runtime/workload`

## Directory Layout

```
workload/
├── mgmt-clusters/
│   ├── mgmt-<site>-<env>/                     # One per management cluster
│   │   ├── kustomization.yaml                  # References ./self, ../../configs, ../../tenants, ./clusters, ../../secrets
│   │   ├── self/                               # Mgmt cluster's own definition
│   │   │   ├── kustomization.yaml
│   │   │   └── definition/
│   │   │       ├── TCaasCluster_mgmt-<site>-<env>_c-mgmt-<site>-<env>.yaml
│   │   │       ├── namespaces/
│   │   │       └── secrets/
│   │   └── clusters/                           # Workload clusters managed by this mgmt
│   │       ├── kustomization.yaml              # Lists all workload cluster dirs
│   │       └── <cluster-name>/                 # One dir per workload cluster
│   │           ├── kustomization.yaml           # References definition + secrets
│   │           ├── definition/
│   │           │   ├── TCaasCluster_tdi-<cluster-name>_c-<cluster-name>.yaml
│   │           │   └── namespaces/
│   │           │       └── c-<cluster-name>.yaml
│   │           └── secrets/                    # Ceph secrets (sops-encrypted)
│   │               ├── ceph-<cluster-name>-rwo.yaml
│   │               ├── ceph-<cluster-name>-rwx.yaml
│   │               └── ceph-<cluster-name>-encryption.yaml
├── configs/                                    # Shared configurations
├── tenants/                                    # Tenant definitions (v1/)
├── secrets/                                    # Shared secrets (image-pull-secret.yaml)
└── patches/                                    # Kustomize patches
```

## Naming Conventions

### Site Codes
Format: `<country><city><dc><seq>` — e.g., `czprgc1` = Czech Republic, Prague, DC1

| Code | Country | City |
|------|---------|------|
| cz | Czech Republic | prgc=Prague, brnc=Brno, thpc=... |
| sk | Slovakia | brac=Bratislava, kosc=Košice |
| hr | Croatia | zagt=Zagreb |
| hu | Hungary | budt=Budapest, dpxc=..., fehc=... |
| at | Austria | vief=Vienna, salf=Salzburg, graf=Graz |

### Cluster Name Pattern
`<site>-<workload>-<env>` — e.g., `czbrnc1-5gc-prod`, `skbrac3-5gc-prod`, `atsalf1-sdv-prod`

### File Naming
- TCaasCluster: `TCaasCluster_tdi-<cluster-name>_c-<cluster-name>.yaml`
- Namespace: `c-<cluster-name>.yaml`
- Secrets: `ceph-<cluster-name>-{rwo,rwx,encryption}.yaml`

## Kustomization Files

### Cluster kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ./definition/TCaasCluster_tdi-<cluster-name>_c-<cluster-name>.yaml
  - ./definition/namespaces/c-<cluster-name>.yaml
  # Secrets added later:
  # - ./secrets/ceph-<cluster-name>-rwo.yaml
  # - ./secrets/ceph-<cluster-name>-rwx.yaml
  # - ./secrets/ceph-<cluster-name>-encryption.yaml
  - ../../../../secrets/image-pull-secret.yaml
patches:
  - target:
      kind: Secret
      name: mcicd-artifactory-prod
    patch: |-
      - op: add
        path: /metadata/namespace
        value: c-<cluster-name>
```

### Parent clusters/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - <cluster-name>/
```

## Namespace YAML
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: c-<cluster-name>
  labels:
    kustomize.toolkit.fluxcd.io/prune: disabled
    t-caas.telekom.com/packet-logging: iptables-events
```

## Finding a Template Cluster

When creating a new cluster, find an existing one to use as template:

1. **Same NatCo + same workload type** (best match) — e.g., for `czbrnc1-5gc-prod`, use `czprgc1-5gc-prod`
2. **Same NatCo + different workload** — shares tenant config
3. **Same vendor + different NatCo** — shares SRIOV layout, worker groups
4. **Any production cluster** — last resort

To list existing clusters:
```bash
find mgmt-clusters -name "TCaasCluster_tdi-*" -type f | sort
```
