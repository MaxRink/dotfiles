---
name: dt-brain-shared-caas-vendor-requirements
description: Analyze vendor infrastructure requirements (Ericsson SDM/CCDM, Nokia, Mavenir) against CaaS baremetal product capabilities and publish compliance analysis to the wiki. Use when the user mentions "vendor requirements", "SDM requirements", "CCDM requirements", "infrastructure requirements", "requirements analysis", "compliance analysis", "requirement mapping", "compare requirements", "requirements vs CaaS", "vendor compatibility", "NF requirements", asks to check if CaaS supports a vendor's requirements, provides a vendor requirements Excel file, or needs to evaluate CaaS platform readiness for a specific network function deployment.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-vendor-requirements by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Vendor Requirements Compliance Analysis

Analyzes vendor infrastructure requirement documents against T-CaaS baremetal product capabilities and publishes a structured compliance report to the Confluence wiki.

## Workflow Overview

```
Excel File ──► Parse Requirements ──► Query CaaS Product ──► Map Compliance ──► Generate Wiki Page
                                           │                       │
                                    componentConfig          CIT CaaS Wiki
                                    functions list           (supplementary)
```

## Phase 1: Understand the Input

Ask the user for:

1. **Vendor requirements file** — typically an Excel file (`.xlsx`) with sheets per category (Compute, Network, Storage, Security, etc.)
2. **CaaS product version** — which baremetal-cluster version to compare against (e.g., `baremetal-cluster-35.4.4`). Use `caas-cit-product` skill to list available versions if needed.
3. **Target wiki space and parent page** — where to publish the analysis (default: CKBSH space under Customers page ID `2042864589`)
4. **NatCo / customer name** — for the page title (e.g., "Magyar Telekom", "Hrvatski Telekom")

## Phase 2: Parse Requirements

Use the parsing script to extract requirements from the Excel file:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/parse_requirements.py \
  "<path-to-excel-file>" \
  --output /tmp/vendor_reqs.json
```

The script auto-detects common vendor Excel formats:
- **Ericsson SDM/CCDM**: Sheets like "Runtime Environment Requirement", "Compute Requirements", etc. with columns: Category, Description, Requirement, Consequence, customer comment
- **Generic format**: Any Excel with identifiable requirement columns

Output is a standardized JSON array where each item has: `id`, `sheet`, `row_num`, `category`, `requirement_text`, `consequence`, `customer_comment`.

If the Excel format is unusual, the script may need manual column mapping via `--category-col`, `--requirement-col`, etc. Review the parse output to ensure requirements were correctly extracted.

### Consolidation Rules

Some vendor documents nest sub-items under parent requirements (e.g., individual kernel modules listed under a "Kernel modules" parent row). The parser consolidates these by:
- Detecting rows where column A has a parent label and column B has sub-items
- Grouping sub-items under the parent requirement text
- Preserving the full detail in the requirement text

## Phase 3: Query CaaS Product Capabilities

Use the `caas-cit-product` skill to gather platform capabilities. Run these queries against the target product version:

```bash
# Get full component configuration (kubelet, apiserver, features, etcd, etc.)
source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/caas-componentconfig.py \
  <product-version> --section kubelet --format json

source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/caas-componentconfig.py \
  <product-version> --section apiserver --format json

source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/caas-componentconfig.py \
  <product-version> --section features --format json

# Get raw YAML for kernel modules, sysctl, chrony, file limits
source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/caas-componentconfig.py \
  <product-version> --raw

# Get deployed functions (CoreDNS, MetalLB, Calico, Ceph, OPA, etc.)
source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/caas-generate-doc.py \
  <product-version>
```

### Key CaaS Capabilities to Extract

| Area | What to Look For |
|------|-----------------|
| **OS / Runtime** | Ubuntu version, kernel version, containerd version, cgroups mode |
| **Kernel modules** | `/etc/modules-load.d/9-caas.conf` entries, extraModulesLoadOverride |
| **Kernel parameters** | sysctl settings, extraSysctlOverride |
| **Kubelet** | cgroup driver, container runtime, PidsLimit, kubeletDropIn |
| **API Server** | admission plugins, audit logging, profiling, encryption |
| **Networking** | Calico, MetalLB, Multus, SR-IOV, OVS-CNI, MTU settings |
| **Storage** | Ceph RBD, CephFS, storage classes, IOPS |
| **Security** | OPA policies (CPBRN*), PSA, RBAC, network policies |
| **Monitoring** | Prometheus, Grafana, fluentbit, alertmanager |
| **Backup** | Velero configuration |
| **NTP** | chrony, configurable ntp_servers |
| **File limits** | nofile, core dump settings |
| **ExtraParams** | Override mechanisms available to customers |

### Supplementary: CIT CaaS Wiki Pages

For capabilities not fully documented in product code, consult these wiki pages using the `cloud-wiki` skill:

| Page ID | Title | Covers |
|---------|-------|--------|
| 1499499273 | CIT CaaS 1.0 | Root documentation page |
| 1478511397 | CaaS on Baremetal Components | OS, containerd, deployed components |
| 1382794879 | CaaS on Baremetal Storage | Ceph RBD/CephFS, storage classes |
| 1377043242 | CaaS on Baremetal Network Design | Network architecture, MTU, MetalLB |
| 1448911229 | CaaS on Baremetal DC Requirements | Storage IOPS, connectivity requirements |
| 1486868707 | CaaS on Baremetal Failure Domains | 3 AZs, topology labels |
| 1768078246 | T-CaaS Cluster Policy | OPA policies CPBRN2-15 |
| 1960971820 | T-CaaS OS Security | OpenSCAP, CIS benchmarks |

```bash
source .env && .venv/bin/python .claude/skills/cloud-wiki/scripts/wiki-get-page.py --id <page-id>
```

## Phase 4: Map Compliance

For each requirement, determine a compliance status:

| Status | Meaning | Use When |
|--------|---------|----------|
| Fulfilled | CaaS meets the requirement | Direct match in product config or deployed function |
| Partial | Partially met | Some aspects covered, others need attention |
| Configurable | Can be enabled via ExtraParams | Not default but achievable via cluster customization |
| Needs review | Requires human assessment | Cannot determine from product code alone |
| Needs verification | Requires cluster-level check | Need to verify on actual deployment |
| Gap | Not supported | No mechanism to fulfill this requirement |
| N/A | Not applicable | Customer marked N/A or requirement doesn't apply |
| Info | Informational only | No action needed, provided for context |
| Customer responsibility | Outside CaaS scope | Client-side tooling or configuration |

### Building the Compliance JSON

As you analyze each requirement, build a JSON file (`/tmp/compliance.json`) mapping requirement IDs (from the parse output) to their analysis. Each entry must have:

```json
{
  "1": {
    "status": "Fulfilled",
    "reference": "Ubuntu 22.04 ships with kernel 5.15+",
    "notes": "Exceeds the 4.19/5.3.18 requirement",
    "wiki_url": "https://wiki.telekom.de/pages/viewpage.action?pageId=1478511397",
    "wiki_title": "CaaS on Baremetal Components"
  },
  "2": {
    "status": "Configurable",
    "reference": "extraSysctlOverride in componentConfig",
    "notes": "vm.max_map_count can be set via ExtraParams",
    "wiki_url": "",
    "wiki_title": ""
  }
}
```

Fields:
- `status` (required) — One of the statuses from the table above
- `reference` (required) — Specific evidence: componentConfig path, function name, or wiki source
- `notes` (required) — Additional context, caveats, or explanation
- `wiki_url` (optional) — Link to supporting wiki page
- `wiki_title` (optional) — Title of the linked wiki page

Save this file before proceeding to Phase 5. It is the reusable analysis artifact.

### Mapping Guidelines

- **Be specific in references**: Point to exact componentConfig sections, function names, or wiki pages
- **Note ExtraParams overrides**: Many seemingly "missing" features are available via `extraSysctlOverride`, `extraModulesLoadOverride`, `kubeletDropIn`, `hugepages`, `crash_dumps.enabled`, etc.
- **OPA vs PSA**: CaaS uses OPA (not Pod Security Admission) — vendor requirements about Linux capabilities may need OPA exceptions (CPBRN10)
- **kube-proxy mode**: CaaS uses iptables mode, not IPVS — mark IPVS requirements as N/A
- **Network**: CaaS uses Calico for CNI with MetalLB for LoadBalancer services
- **Storage**: Ceph RBD and CephFS are the primary storage backends

### Common Patterns

These patterns appear across most vendor requirement documents:

1. **Kernel modules**: Cross-reference vendor list against `/etc/modules-load.d/9-caas.conf`. Most iptables/netfilter modules are auto-loaded by the kernel.
2. **Kernel parameters (sysctl)**: Check ramdiskCommands in raw config. Common gaps: `vm.max_map_count` (needs extraSysctlOverride).
3. **Container runtime**: Always fulfilled — containerd is OCI 1.0.0 compliant.
4. **Helm version**: Customer responsibility — not part of CaaS platform.
5. **Pod resource limits**: Configurable per namespace — not a platform constraint.
6. **Network policies**: Supported via Calico NetworkPolicy and GlobalNetworkPolicy.
7. **Persistent volumes**: Ceph RBD (block) and CephFS (filesystem) available.
8. **Topology awareness**: 3 AZs with topology.kubernetes.io labels.
9. **Log collection**: fluentbit deployed, logs forwarded to central logging.
10. **Monitoring**: Prometheus + Grafana deployed, custom ServiceMonitors supported.

## Phase 5: Generate Wiki Page

Use the generation script to create Confluence storage format HTML from the requirements and compliance JSON produced in Phases 2 and 4:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/generate_wiki.py \
  --requirements /tmp/vendor_reqs.json \
  --compliance /tmp/compliance.json \
  --product-version "<product-version>" \
  --customer "<customer-name>" \
  --output /tmp/wiki_content.html
```
```

Save the compliance JSON before generating the wiki page — this is the reusable analysis artifact.

### Wiki Page Structure

The generated page includes:
1. **Header** — Product version, date, source document
2. **Summary table** — Count by status category with color coding
3. **Legend** — Status definitions
4. **Action items** — Panel highlighting items that need follow-up (Partial/Gap/Needs review)
5. **Per-sheet tables** — Each vendor requirement sheet as a separate section with columns: #, Category, Requirement (FULL text), Customer Comment, T-CaaS Status, Reference, Notes
6. **References** — Links to CIT CaaS wiki pages used

## Phase 6: Publish to Wiki

```bash
source .env && .venv/bin/python .claude/skills/cloud-wiki/scripts/wiki-create-page.py \
  --title "<Vendor> Infrastructure Requirements - <Customer> - Analysis" \
  --space CKBSH \
  --parent-id <parent-page-id> \
  --content-file /tmp/wiki_content.html
```

Default parent page: Customers (ID: `2042864589`) in CKBSH space.

To update an existing page:
```bash
source .env && .venv/bin/python .claude/skills/cloud-wiki/scripts/wiki-update-page.py \
  --id <page-id> \
  --content-file /tmp/wiki_content.html
```

## Dependencies

This skill depends on:
- **caas-cit-product** — For querying CaaS product configuration and functions
- **cloud-wiki** — For reading CIT CaaS documentation and publishing the analysis page
- **openpyxl** — Available in `.venv` for Excel parsing

If `caas-cit-product` is not available, use the `references/caas-capabilities.md` file as a fallback reference for platform capabilities. If `cloud-wiki` is not available, generate the HTML output locally and let the user publish it manually.

## Environment Variables

Scripts in this skill don't require environment variables directly. However, cross-skill calls to `caas-cit-product` and `cloud-wiki` require tokens. The project convention is to prepend `source .env` before those calls:

```bash
source .env && .venv/bin/python .claude/skills/caas-cit-product/scripts/...
source .env && .venv/bin/python .claude/skills/cloud-wiki/scripts/...
```

This loads `CONFLUENCE_USER`, `CONFLUENCE_TOKEN`, `GITLAB_TOKEN`, etc. from the project `.env` file.

## Error Handling

| Issue | Solution |
|-------|----------|
| Excel column mismatch | Use `--category-col` / `--requirement-col` to specify column letters |
| Product version not found | Run `caas-list-products.py` to find available versions |
| Wiki update returns 400 | Content may have non-ASCII characters; the generate script ensures ASCII-clean output |
| Large wiki page fails on update | Delete and recreate instead of updating (Confluence API limitation with large content) |
| Missing wiki references | Check VPN connectivity; fetch pages individually to verify access |

## References

| File | When to Read |
|------|-------------|
| `references/caas-capabilities.md` | Quick reference of CaaS platform capabilities by category |
