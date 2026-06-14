---
name: dt-brain-shared-caas-ct-product
description: This skill should be used when the user mentions "CT-CaaS", "T-CaaS", "converged", "netbox bundle", "openstack bundle", "function definitions", "container images for CT-CaaS", "image versions", "artifactory", "compute profile", "NTP servers", "chrony", "ExtraNTPServers", "kyverno", "kyverno policies", "platform-policies", "enforcement level", "policy engine", "allowed registries", "elevated-components", "elevated components", "tenant RBAC", "vendor RBAC", "vendor permissions", "policy exceptions", asks about specific bundle versions like "netbox-workload-34.0.19" or "openstack-management-33.6.6", needs to generate documentation for a CT-CaaS bundle, or needs to update T-CaaS wiki release notes with component versions.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-ct-product by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CT-CaaS Bundle Navigation

> ⚠️ **Not to be confused with `caas-cit-product`** (CIT CaaS baremetal/mgmt products).
> This skill is for **CT-CaaS (T-CaaS) converged** bundles (netbox, openstack).
> See [docs/cit-vs-ct-caas.md](../../../docs/cit-vs-ct-caas.md) for the full comparison.

Explore CT-CaaS (Converged T-CaaS) bundles, functions, and container image versions via GitLab API.

**Data Source:** https://gitlab.devops.telekom.de/cit/t-caas/software/bundles

## Prerequisites

Always prefix commands with `source .env &&` to load credentials. Requires VPN connection.

**Note:** `${SKILL_DIR}` is automatically set to this skill's directory by the skill loader.

## Common Workflows

1. **Investigate a bundle:** List bundles → Get bundle info → Get image versions
2. **Compare releases:** List bundles → Compare two versions → Review diff
3. **Generate release notes:** List bundles → Generate release notes → Update wiki page
4. **Document a bundle:** List bundles → Generate full documentation

## Operations

### 1. List Bundles

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-list-bundles.py [--type TYPE] [--latest] [--format FORMAT]
```

- `--type TYPE` - Filter by bundle type (netbox, openstack)
- `--latest` - Show only the latest version per bundle
- `--format` - Output format: table, json, markdown

### 2. List Functions

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-list-functions.py <bundle-name> [--format FORMAT]
```

### 3. Bundle Info

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-bundle-info.py <bundle-name> [--format FORMAT]
```

Show metadata (K8s version) and functions for a bundle.

### 4. Image/Component Versions

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-image-versions.py <bundle-name> [--format FORMAT]
```

Extract component versions from function definitions:
- **Helm charts**: Chart name, version, AND container image version (appVersion from OCI registry)
- **Kustomize releases**: Release name and OCI reference
- **Container images**: Full image names from kustomize image overrides

### 5. Kubernetes Version

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-k8s-version.py <major-version> [--type TYPE] [--format FORMAT]
```

Show `spec.k8sVersion` for the latest bundle in each minor version line.

- `<major-version>` - CT-CaaS major version (e.g., 35)
- `--type TYPE` - Bundle type (netbox, openstack). Default: all types
- `--format` - Output format: table, json, markdown

Examples:
```bash
# Show K8s versions for all 35.x bundles
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-k8s-version.py 35

# Show only netbox bundles
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-k8s-version.py 35 --type netbox
```

### 6. Release Notes Table

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-release-notes.py <bundle-name> [--format FORMAT]
```

Generate a component version table for release notes. Auto-detects bundle type (netbox vs OpenStack) and shows relevant components.

- `--format` - Output format: markdown (default), confluence, plain

**Supported Bundle Types:**

| Bundle Pattern | Type | Description |
|----------------|------|-------------|
| `netbox-workload-*` | Netbox | Baremetal Kubernetes clusters |
| `openstack-management-*` | OpenStack | OpenStack management clusters |
| `openstack-workload-*` | OpenStack | OpenStack workload clusters |

### 7. Generate Documentation

```bash
# Full documentation (overview, functions, image versions)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-generate-doc.py <bundle-name> [--output FILE] [--format FORMAT]

# Release notes (simple component/version table)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-generate-doc.py <bundle-name> --release-notes [--format FORMAT]
```

- `--release-notes` - Generate simple component/version table for release notes
- `--format` - Output format: markdown (default), confluence, json, plain
- `--output FILE` - Write to file instead of stdout

### 8. Compare Versions

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-compare-versions.py <bundle-1> <bundle-2> [--format FORMAT] [--diff-only]
```

- `--diff-only` - Show only components with version differences
- Auto-sorts versions from older to newer regardless of argument order

### 9. Update Wiki Release Notes

```bash
# By page ID
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-update-wiki-versions.py <bundle-name> --page-id PAGE_ID [--dry-run]

# Auto-discover page by version
source .env && .venv/bin/python ${SKILL_DIR}/scripts/ct-update-wiki-versions.py <bundle-name> --version 34.0 [--dry-run]
```

Fill the component versions table in T-CaaS wiki release notes pages. Extract versions from the bundle, map them to wiki table component names, and update the Confluence page.

- `--dry-run` - Preview changes without updating the wiki
- `--version` - Auto-discovers the wiki page by searching for "T-CaaS version X.Y" in the TCAAS space
- `--page-id` - Direct page ID (use when auto-discovery doesn't find the page)

**Wiki pages** are in the TCAAS space under "Release notes", named "T-CaaS version X.0".

**Requires:** `CONFLUENCE_USER` and `CONFLUENCE_TOKEN` environment variables (in addition to `GITLAB_API_TOKEN` and `ARTIFACTORY_TOKEN`).

**Workflow for each release:**
1. Identify the latest netbox bundle for the version (e.g., `ct-list-bundles.py --type netbox`)
2. Run with `--dry-run` first to preview
3. Run without `--dry-run` to update the wiki

## Output Formats

All scripts support `--format` with: `table` (default), `json`, `markdown`.
Release notes additionally support: `confluence`, `plain`.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| GITLAB_API_TOKEN not set | Missing token | `export GITLAB_API_TOKEN="..."` |
| Failed to access project | Network/auth | Check VPN and token |
| Bundle not found | Invalid name | Use list-bundles to find valid names |
| ARTIFACTORY_TOKEN not set | Missing token | Set for image version lookup |
| CONFLUENCE_USER not set | Missing wiki user | `export CONFLUENCE_USER="..."` (for wiki update) |
| CONFLUENCE_TOKEN not set | Missing wiki token | `export CONFLUENCE_TOKEN="..."` (for wiki update) |

## Reference

Reference docs provide background knowledge and known patterns. **Always verify reference claims against live data** before answering — bundles evolve, and references may be outdated. Use the reference for context, then confirm with the appropriate script or GitLab API query.

| File | When to Read | How to Verify |
|------|-------------|---------------|
| `references/bundle-types.md` | When navigating the bundles repo structure, understanding bundle/function YAML format, or version numbering | Run `ct-list-bundles.py` to confirm current bundles |
| `references/compute-profiles.md` | When asked about compute profiles, NTP configuration, node-level provisioning (Chrony, hugepages, CPU pinning, etc.) | Check the latest compute-profile definitions on GitLab |
| `references/kyverno-policies.md` | When asked about Kyverno policies, platform-policies, enforcement levels, allowed registries, or policy engine configuration | Run `ct-list-functions.py` on the latest bundle to confirm kyverno function version, and check the kyverno kustomization on GitLab |
| `references/cert-manager.md` | When asked about cert-manager, ClusterIssuers, TLS certificates, ACME, TelesecCA, Infoblox DNS-01, or certificate issuers on CT-CaaS clusters | Run `ct-list-functions.py` on the latest bundle to confirm whether `cert-manager-issuers` is included, and check the FD in the bundles repo |
| `references/elevated-components.md` | When asked about elevated-components, tenant RBAC, vendor permissions, Kyverno policy exceptions, or the `elevated-components-tdi` repo | Check the repo on GitLab for current tenants, clusters, and resource files |
