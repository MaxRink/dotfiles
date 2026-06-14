---
name: dt-brain-shared-caas-cit-product
description: This skill should be used when the user mentions "CaaS product", "tdi-caas product", "CIT CaaS", "CIT product", "product version", "function list", "container images", "image versions", "product documentation", "componentConfig", "component config", "apiserver extraArgs", "kubelet config", "cluster configuration", "cluster definition", "extraParams", "CC_JSON", "NTP servers", "ntp_servers", "chrony", asks about specific product versions like "baremetal-cluster-34.6.10", needs to generate a bill of materials for a CaaS product, or asks about "OPA", "OPA policy", "OPA rules", "OPA exception", "hostPath", "policy violation", or "admission controller" on CaaS clusters, or asks about "velero", "velero config", "backup", "S3 endpoint", "radosgw", "BackupStorageLocation", or "cloud settings", or asks about "image-builder", "caas-image-builder", "node image", "runc", "runc version", "containerd", "containerd version", or needs to understand how CaaS node images are built.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-cit-product by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TDI CaaS Product Navigation

> ⚠️ **Not to be confused with `caas-ct-product`** (CT-CaaS / T-CaaS converged bundles).
> This skill is for **CIT CaaS** products (baremetal, mgmt-cluster, etc.).
> CIT CaaS is also referred to as **TDI-CaaS** — both names refer to the same product family.
> See [docs/cit-vs-ct-caas.md](../../../docs/cit-vs-ct-caas.md) for the full comparison.

Explore CaaS products, functions, and container image versions via GitLab API.

**Data Source:** `tdi-caas/caas-bundles` on GitLab (requires VPN + `GITLAB_API_TOKEN`). Image versions also need `ARTIFACTORY_TOKEN`.

## Cluster Definitions for Running CIT Clusters

Unlike CT-CaaS clusters (which are defined in the workload GitOps repo), **CIT CaaS cluster definitions are stored in DDU/NetBox**. To inspect the definition of a running CIT cluster, use the `caas-ddu` skill:

```bash
# Get full cluster definition as JSON
source .env && .venv/bin/python .claude/skills/caas-ddu/scripts/ddu-report.py <cluster-name> --json
```

The cluster definition is stored in the **`CC_JSON`** field (a JSON string that must be parsed). Its top-level structure is:

| Key | Description |
|-----|-------------|
| `product` | Product name and version (e.g. `baremetal-cluster-34.6.10`) |
| `cloud_id` | Cloud identifier (e.g. `ic-atvief1-baremetal`) |
| `networkProfile` | Network profile version |
| `networking` | Network configuration (pod/service CIDRs) |
| `control_plane` | Control plane node config (count, flavor, etc.) |
| `worker_groups` | Worker group definitions (count, flavor, labels, taints, CPU manager) |
| `owner` | Cluster owner info |
| `juiceGroup` | Juice group assignment |
| `production` | Whether this is a production cluster |
| `extraParams` | **Cluster-specific parameters** (calico, ceph, SR-IOV, OPA, mellanox, velero, etc.) |
| `additionalFunctions` | Extra functions deployed on the cluster |
| `oidc` | OIDC configuration |

### Extracting specific fields

```bash
# Get extraParams (calico, ceph, SR-IOV, OPA whitelists, mellanox, etc.)
source .env && .venv/bin/python .claude/skills/caas-ddu/scripts/ddu-report.py <cluster-name> --json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); cc=d[0]['CC_JSON']; cc=json.loads(cc) if isinstance(cc,str) else cc; print(json.dumps(cc.get('extraParams',{}), indent=2))"

# Get worker groups
source .env && .venv/bin/python .claude/skills/caas-ddu/scripts/ddu-report.py <cluster-name> --json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); cc=d[0]['CC_JSON']; cc=json.loads(cc) if isinstance(cc,str) else cc; print(json.dumps(cc.get('worker_groups',[]), indent=2))"

# Get product version
source .env && .venv/bin/python .claude/skills/caas-ddu/scripts/ddu-report.py <cluster-name> --json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); cc=d[0]['CC_JSON']; cc=json.loads(cc) if isinstance(cc,str) else cc; print(json.dumps(cc.get('product',{}), indent=2))"
```

## Prerequisites

Always prefix commands with `source .env &&` to load credentials. Requires VPN connection.

## Operations

### 1. List Products

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-list-products.py [--type TYPE] [--format FORMAT]
```

- `--type TYPE` - Filter by product type (baremetal, caas, mgmt-cluster, dtit, mom, support)
- `--format` - Output format: table, json, markdown

### 2. List Functions

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-list-functions.py <product-name> [--format FORMAT]
```

### 3. Product Info

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-product-info.py <product-name> [--format FORMAT]
```

Show metadata, functions, and actions for a product.

### 4. Image Versions

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-image-versions.py <product-name> [--format FORMAT]
```

Extract container image versions by querying Artifactory Helm repository.

### 5. Kubernetes Version

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-k8s-version.py <major-version> [--type TYPE] [--all-types] [--format FORMAT]
```

Show `spec.kubernetesVersion` for the latest product in each minor version line.

- `<major-version>` - CaaS major version (e.g., 35)
- `--type TYPE` - Product type to query (default: baremetal)
- `--all-types` - Show all product types, not just one
- `--format` - Output format: table, json, markdown

Examples:
```bash
# Show K8s versions for all baremetal 35.x products
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-k8s-version.py 35

# Show K8s versions for management clusters
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-k8s-version.py 35 --type mgmt-cluster

# Show all product types for version 34
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-k8s-version.py 34 --all-types
```

### 6. Generate Documentation

```bash
# Full documentation (overview, functions, actions, labels)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-generate-doc.py <product-name> [--output FILE]

# Release notes (simple component/version table)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-generate-doc.py <product-name> --release-notes [--format FORMAT]
```

- `--release-notes` - Generate simple component/version table for release notes
- `--format` - Output format for release notes: table, markdown (default)
- `--output FILE` - Write to file instead of stdout

### 7. ComponentConfig

```bash
# List all componentConfigs
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-componentconfig.py --list

# Show componentConfig overview for a product (apiserver extraArgs, kubelet config, etc.)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-componentconfig.py <product-name>

# Show specific section only
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-componentconfig.py <product-name> --section <apiserver|kubelet|etcd|controller-manager|scheduler|features>

# Show raw YAML
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-componentconfig.py <product-name> --raw
```

Show cluster-level Kubernetes configuration defined in the componentConfig referenced by a product. This includes kube-apiserver extraArgs/extraVolumes, kubelet settings, controller-manager/scheduler args, enabled feature flags, networking, and kubeadm configuration.

### 8. Compare Versions

```bash
# Compare functions
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-compare-versions.py <product-1> <product-2> [--format FORMAT]

# Compare image versions
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-compare-versions.py <product-1> <product-2> --images [--format FORMAT]
```

- `--images` - Compare container image versions instead of functions

## Output Formats

All scripts support `--format` with: `table` (default), `json`, `markdown`.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| GITLAB_API_TOKEN not set | Missing token | `export GITLAB_API_TOKEN="..."` |
| Failed to access project | Network/auth | Check VPN and token |
| Product not found | Invalid name | Use list-products to find valid names |
| ARTIFACTORY_TOKEN not set | Missing token | Set for image version lookup |

## References

Reference docs provide background knowledge and known patterns. **Always verify reference claims against live data** before answering — bundles and products evolve, and references may be outdated. Use the reference for context, then confirm with the appropriate script or GitLab API query.

| File | When to Read | How to Verify |
|------|-------------|---------------|
| `references/product-types.md` | When navigating the caas-bundles repo structure, understanding product/function YAML format, or version numbering | Run `caas-list-products.py` to confirm current products |
| `references/opa-policies.md` | When dealing with OPA policy violations, admission controller errors, hostPath denials, or security exceptions on CaaS clusters | Check the latest product's `opa` function version with `caas-list-functions.py` |
| `references/domain-knowledge.md` | When asked about NTP servers, Chrony config, cert-manager, ClusterIssuers, or other cluster-level defaults configured via componentConfig | Run `caas-componentconfig.py` or `caas-list-functions.py` on the latest product to confirm |
| `references/baremetal-testing.md` | When testing a new `baremetal-cluster` product version — lists available dev/test clusters and links to hardware docs | Check NetBox or cluster inventory for current availability |
| `references/velero-cloudsettings.md` | When asked about Velero config, backup storage locations, S3 endpoints, or RadosGW — includes how to fetch live config from `tdi-caas/mom-factory-adopted` | Fetch live Velero config from GitLab as described in the reference |
| `references/image-builder.md` | When asked about CaaS node images, runc/containerd versions, image-builder architecture, or debugging node component versions — covers TDI-CaaS vs CT-CaaS image builders and known issues | Check the latest image-builder repo on GitLab for current versions |
