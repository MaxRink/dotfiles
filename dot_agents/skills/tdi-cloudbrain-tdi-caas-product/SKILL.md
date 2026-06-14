---
name: tdi-cloudbrain-tdi-caas-product
user-invocable: true
description: This skill should be used when the user mentions "CaaS product", "product version", "function list", "container images", "image versions", "product documentation", asks about specific product versions like "baremetal-cluster-34.6.10", or needs to generate a bill of materials for a CaaS product.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/tdi-caas-product by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TDI CaaS Product Navigation

Explore CaaS products, functions, and container image versions via GitLab API.

**Data Source:** https://gitlab.devops.telekom.de/tdi-caas/caas-bundles

## Authentication

```bash
export GITLAB_API_TOKEN="your-gitlab-token"      # Required
export ARTIFACTORY_TOKEN="your-identity-token"   # Optional, for image versions
```

**Requirements:** VPN connection to Telekom network.

## Operations

### 1. List Products

```bash
.venv/bin/python ${SKILL_DIR}/scripts/caas-list-products.py [--type TYPE] [--format FORMAT]
```

- `--type TYPE` - Filter by product type (baremetal, caas, mgmt-cluster, dtit, mom, support)
- `--format` - Output format: table, json, markdown

### 2. List Functions

```bash
.venv/bin/python ${SKILL_DIR}/scripts/caas-list-functions.py <product-name> [--format FORMAT]
```

### 3. Product Info

```bash
.venv/bin/python ${SKILL_DIR}/scripts/caas-product-info.py <product-name> [--format FORMAT]
```

Shows metadata, functions, and actions for a product.

### 4. Image Versions

```bash
.venv/bin/python ${SKILL_DIR}/scripts/caas-image-versions.py <product-name> [--format FORMAT]
```

Extracts container image versions by querying Artifactory Helm repository.

### 5. Generate Documentation

```bash
# Full documentation (overview, functions, actions, labels)
.venv/bin/python ${SKILL_DIR}/scripts/caas-generate-doc.py <product-name> [--output FILE]

# Release notes (simple component/version table)
.venv/bin/python ${SKILL_DIR}/scripts/caas-generate-doc.py <product-name> --release-notes [--format FORMAT]
```

- `--release-notes` - Generate simple component/version table for release notes
- `--format` - Output format for release notes: table, markdown (default)
- `--output FILE` - Write to file instead of stdout

### 6. Compare Versions

```bash
# Compare functions
.venv/bin/python ${SKILL_DIR}/scripts/caas-compare-versions.py <product-1> <product-2> [--format FORMAT]

# Compare image versions
.venv/bin/python ${SKILL_DIR}/scripts/caas-compare-versions.py <product-1> <product-2> --images [--format FORMAT]
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

## Reference

See `references/product-types.md` for documentation on product types and folder structure.
