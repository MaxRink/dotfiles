---
name: tdi-cloudbrain-ct-caas-product
user-invocable: true
description: This skill should be used when the user mentions "CT-CaaS", "T-CaaS", "converged", "netbox bundle", "openstack bundle", "function definitions", "container images for CT-CaaS", asks about specific bundle versions like "netbox-workload-34.0.19" or "openstack-management-33.6.6", or needs to generate documentation for a CT-CaaS bundle.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/ct-caas-product by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CT-CaaS Bundle Navigation

This skill provides tools to explore CT-CaaS (Converged T-CaaS) bundles, their functions, and container image versions.

## Path Setup

```bash
export CT_CAAS_BUNDLES_PATH="/path/to/tcaas/bundles"   # Optional, auto-detected
```

## Path Auto-Detection

The skill auto-detects `tcaas/bundles` location:
1. If `CT_CAAS_BUNDLES_PATH` is set, use it
2. Else, search common locations:
   - `./tcaas/bundles`
   - `../tcaas/bundles`
   - `~/git/tcaas/bundles`
   - `/Users/*/git/tcaas/bundles`

## Available Operations

### 1. List Bundles

Lists all available CT-CaaS bundles with their versions.

```bash
${SKILL_DIR}/scripts/ct-list-bundles.sh [--type TYPE] [--latest]
```

**Options:**
- `--type TYPE` - Filter by bundle type (netbox, openstack)
- `--latest` - Show only the latest version per bundle

**Examples:**
```bash
# List all netbox bundles
${SKILL_DIR}/scripts/ct-list-bundles.sh --type netbox

# List latest version of each bundle type
${SKILL_DIR}/scripts/ct-list-bundles.sh --latest
```

### 2. List Functions

Lists all functions for a specific bundle version.

```bash
${SKILL_DIR}/scripts/ct-list-functions.sh <bundle-name>
```

**Example:**
```bash
${SKILL_DIR}/scripts/ct-list-functions.sh netbox-workload-34.0.19
```

### 3. Bundle Info

Shows detailed information about a bundle including metadata and functions.

```bash
${SKILL_DIR}/scripts/ct-bundle-info.sh <bundle-name>
```

**Output includes:**
- Bundle metadata (K8s version)
- Function list with versions

**Example:**
```bash
${SKILL_DIR}/scripts/ct-bundle-info.sh netbox-workload-34.0.19
```

### 4. Image/Component Versions

Extracts component versions from function definitions including Helm charts (with actual container image versions), Kustomize releases, and container images.

```bash
${SKILL_DIR}/scripts/ct-image-versions.sh <bundle-name> [--format table|json|markdown]
```

**Options:**
- `--format table` - Output as ASCII table (default)
- `--format json` - Output as JSON
- `--format markdown` - Output as Markdown table

**Extracts:**
- **Helm charts**: Chart name, version, AND container image version (appVersion from Helm index)
- **Kustomize releases**: Release name and OCI reference (e.g., `cni (kustomize) 3.30.3-r.0`)
- **Container images**: Full image names from kustomize image overrides (e.g., `docker.io/calico/node`)

**Environment:**
- `ARTIFACTORY_TOKEN` - Required for Helm image version lookup. Without this, chart versions are shown but image versions will be empty.

**Requires:** `yq` (https://github.com/mikefarah/yq)

**Example:**
```bash
# Get component versions in markdown format
${SKILL_DIR}/scripts/ct-image-versions.sh netbox-workload-34.0.19 --format markdown
```

**Sample Output:**
```markdown
| Function | Version | Component | Type/Version | Image Version | Notes |
|----------|---------|-----------|--------------|---------------|-------|
| coredns | 0.3.1 | coredns (helm) | v1.43.1 | 1.11.1 |  |
| calico | 0.4.8 | cni (kustomize) | 3.30.3-r.0 | 3.30.3-r.0 |  |
| calico | 0.4.8 | docker.io/calico/node | image | - |  |
```

**Column Meanings:**
- **Type/Version**: Helm chart version or Kustomize OCI reference
- **Image Version**: Actual container image version (appVersion for Helm, same as Type/Version for Kustomize, "-" for image entries)

### 5. Release Notes Table

Generates a component version table for release notes documentation. Auto-detects bundle type (netbox vs OpenStack) and shows relevant components.

```bash
${SKILL_DIR}/scripts/ct-release-notes.sh <bundle-name> [--format markdown|confluence|plain]
```

**Options:**
- `--format markdown` - Markdown table (default)
- `--format confluence` - Confluence wiki markup
- `--format plain` - Plain text format

**Supported Bundle Types:**

| Bundle Pattern | Type | Description |
|----------------|------|-------------|
| `netbox-workload-*` | Netbox | Baremetal Kubernetes clusters |
| `openstack-management-*` | OpenStack | OpenStack management clusters |
| `openstack-workload-*` | OpenStack | OpenStack workload clusters |

**Netbox Components:**
- Cluster Services (metrics-server, coredns)
- Networking (calico, metallb-standalone, ingress-nginx-controller)
- SR-IOV & Multus (multus-cni, sriov-cni, sriov-network-device-plugin, whereabouts, ovs-cni)
- Storage (ceph-csi)
- Security (cert-manager, kyverno)
- Monitoring (prometheus, blackbox-exporter, goldpinger)
- Logging (fluent-bit)
- GitOps (flux-workload)

**OpenStack Components:**
- Cluster Services (metrics-server, coredns)
- Networking (calico, ingress-nginx-controller)
- OpenStack Integration (openstack-cloud-controller-manager, cinder-csi-plugin)
- Security (cert-manager, kyverno)
- Monitoring (prometheus, blackbox-exporter, goldpinger)
- Logging (fluent-bit)
- GitOps (flux-workload)

**Examples:**
```bash
# Generate netbox release notes
${SKILL_DIR}/scripts/ct-release-notes.sh netbox-workload-34.0.19

# Generate OpenStack release notes
${SKILL_DIR}/scripts/ct-release-notes.sh openstack-management-33.6.6

# Generate Confluence format for wiki
${SKILL_DIR}/scripts/ct-release-notes.sh netbox-workload-34.0.19 --format confluence
```

### 6. Generate Documentation

Generates comprehensive bundle documentation.

```bash
${SKILL_DIR}/scripts/ct-generate-doc.sh <bundle-name> [--output FILE] [--format FORMAT]
```

**Options:**
- `--output FILE` - Write to file (default: stdout)
- `--format FORMAT` - Output format: `markdown` (default), `confluence`, `json`

**Output includes:**
- Bundle overview (name, K8s version)
- Functions table with versions
- Container images table with versions
- Generation timestamp

**Examples:**
```bash
# Generate markdown documentation
${SKILL_DIR}/scripts/ct-generate-doc.sh netbox-workload-34.0.19

# Generate Confluence wiki markup
${SKILL_DIR}/scripts/ct-generate-doc.sh netbox-workload-34.0.19 --format confluence

# Save to file
${SKILL_DIR}/scripts/ct-generate-doc.sh netbox-workload-34.0.19 --output /tmp/bundle-doc.md
```

## Output Formats

### Markdown
```markdown
| Function | Version | Component | Type/Version | Image Version | Notes |
|----------|---------|-----------|--------------|---------------|-------|
| coredns | 0.3.1 | coredns (helm) | v1.43.1 | 1.11.1 |  |
| calico | 0.4.8 | cni (kustomize) | 3.30.3-r.0 | 3.30.3-r.0 |  |
| calico | 0.4.8 | docker.io/calico/node | image | - |  |
```

### Confluence Wiki Markup
```
||Function||Version||Component||Type/Version||Image Version||Notes||
|coredns|0.3.1|coredns (helm)|v1.43.1|1.11.1| |
|calico|0.4.8|cni (kustomize)|3.30.3-r.0|3.30.3-r.0| |
```

### JSON
```json
{
  "bundle": "netbox-workload-34.0.19",
  "components": [
    {"function": "coredns", "function_version": "0.3.1", "component": "coredns (helm)", "type_version": "v1.43.1", "image_version": "1.11.1", "notes": ""},
    {"function": "calico", "function_version": "0.4.8", "component": "cni (kustomize)", "type_version": "3.30.3-r.0", "image_version": "3.30.3-r.0", "notes": ""},
    {"function": "calico", "function_version": "0.4.8", "component": "docker.io/calico/node", "type_version": "image", "image_version": "-", "notes": ""}
  ]
}
```

## Error Handling

- Scripts exit with code 0 on success, non-zero on failure
- Invalid bundle names will show available bundles
- Missing function definition files will be reported

### 7. Compare Versions

Compares component versions between two bundle versions side-by-side.

```bash
${SKILL_DIR}/scripts/ct-compare-versions.sh <bundle-1> <bundle-2> [OPTIONS]
```

**Default Behavior:**
- Shows ALL components (not just differences) - use `--diff-only` to show only changes
- Auto-sorts versions from older to newer, regardless of argument order
- It's OK if there are no component differences - bundles may differ only in Kubernetes version or metadata

**Options:**
- `--format table` - ASCII table output (default)
- `--format markdown` - Markdown table
- `--format json` - JSON with comparison metadata
- `--diff-only` - Show only components with version differences (not default)

**Status Indicators:**
- `same` - Version unchanged between bundles
- `changed` - Version differs (marked with `*`)
- `added` - Component only in older bundle (marked with `+`)
- `removed` - Component only in newer bundle (marked with `-`)

**Examples:**
```bash
# Compare two netbox-workload versions - shows ALL components, auto-sorted older to newer
${SKILL_DIR}/scripts/ct-compare-versions.sh netbox-workload-34.0.19 netbox-workload-33.0.0
# Note: Will auto-reorder to compare from 33.0.0 (older) to 34.0.19 (newer)

# Show only differences in markdown
${SKILL_DIR}/scripts/ct-compare-versions.sh netbox-workload-34.0.19 netbox-workload-33.0.0 --diff-only --format markdown

# Export comparison as JSON
${SKILL_DIR}/scripts/ct-compare-versions.sh netbox-workload-34.0.19 netbox-workload-33.0.0 --format json
```

## Reference

See `references/bundle-types.md` for documentation on bundle types and folder structure.
