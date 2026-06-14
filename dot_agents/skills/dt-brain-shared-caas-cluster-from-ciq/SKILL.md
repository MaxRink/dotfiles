---
name: dt-brain-shared-caas-cluster-from-ciq
description: >
  Create TCaasCluster definitions in the converged workload repo from vendor CiQ Excel files.
  Use this skill when the user mentions "CiQ", "cluster from CiQ", "CiQ file", "create cluster",
  "new cluster definition", "onboard cluster", "cluster onboarding", "TCaasCluster from Excel",
  or needs to create a new converged cluster definition based on a vendor requirements spreadsheet.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-cluster-from-ciq by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Cluster from CiQ

## Overview

This skill creates TCaasCluster definition files in the converged workload GitLab repo
from vendor CiQ (Configuration Input Questionnaire) Excel files. It handles multiple
vendors (Mavenir, Nokia, Ericsson) by reading the CiQ interactively and adapting an
existing cluster template from the repo.

## Requirements

- GitLab token: `GITLAB_TOKEN` (read) and `GITLAB_API_TOKEN_RW` (for MR creation) in `.env`
- Python venv with `openpyxl` installed
- CiQ Excel file provided by the user
- Workload repo: `https://gitlab.devops.telekom.de/tdi-caas/runtime/workload`

## Workflow

Creating a cluster from CiQ involves these phases:

### Phase 1: Setup

1. **Pull workload repo**
   ```bash
   cd /Users/ondrejkuchar/projects/caas
   source /Users/ondrejkuchar/projects/caas/dt-brain-shared/.env
   # Clone if not exists, pull if exists
   git clone https://oauth2:${GITLAB_TOKEN}@gitlab.devops.telekom.de/tdi-caas/runtime/workload.git 2>/dev/null || (cd workload && git checkout main && git pull)
   ```

2. **Gather inputs from user** — ask for:
   - Path to CiQ Excel file
   - Cluster name (e.g., `czbrnc1-5gc-prod`)
   - DTH subnet (user must provide this)
   - Any other known values (VLANs, Ceph IPs if available)

### Phase 2: Analyze CiQ

3. **Run the CiQ extractor** to get an overview:
   ```bash
   source .env && .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file>
   ```
   This detects the vendor and dumps priority sheets.

4. **Extract key parameters** by reading relevant sheets. Use `--sheet <name>` for details:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file> --sheet "Platform_pre" --rows 80
   .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file> --sheet "SRIOV" --rows 80
   .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file> --sheet "IP Subnet" --rows 80
   .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file> --sheet "POD_Distribution" --rows 40
   .venv/bin/python ${SKILL_DIR}/scripts/ciq_extract.py <ciq_file> --sheet "Network Config" --rows 40
   ```

   Refer to `references/ciq-sheet-guide.md` for vendor-specific sheet patterns.

   **Data to extract:**
   - Worker node count, AZ distribution, worker group layout
   - Worker labels (isupf, isme, isepdg, mavenir_core, etc.)
   - Hugepages size and count
   - CPU pinning settings
   - Sysctl parameters (net.core.*, fs.*, net.ipv4.*, etc.)
   - GRUB parameters
   - SRIOV resource names with NUMA/side mapping
   - IP subnets: OAM, K8S API VIP, SBA, and all NF interfaces
   - DNS zones and nameservers
   - Storage requirements (RWO/RWX)
   - K8s version requirement

5. **Determine how many sheets to read** based on vendor. For unknown vendors, use `--all` flag
   and look for patterns matching the TCaasCluster fields documented in
   `references/tcaascluster-structure.md`.

### Phase 3: Find Template & Generate

6. **Find a template cluster** in the workload repo:
   ```bash
   cd /Users/ondrejkuchar/projects/caas/workload
   find mgmt-clusters -name "TCaasCluster_tdi-*" -type f | sort
   ```

   Selection priority (see `references/workload-repo-structure.md`):
   1. Same NatCo + same workload type (best)
   2. Same NatCo + different workload
   3. Same vendor + different NatCo
   4. Any production cluster (last resort)

7. **Read the template cluster** thoroughly — understand its full structure including
   SRIOV resources, worker groups, DNS zones, storage config.

8. **Create feature branch**:
   ```bash
   git checkout -b feature/<cluster-name>
   ```

9. **Copy and adapt the template**:
   - Use `sed` to substitute cluster name, location, namespace throughout
   - Then use the `edit` tool to update specific values from CiQ
   - Refer to `references/tcaascluster-structure.md` for which field comes from where

10. **Apply CiQ values** — update these fields from CiQ data:
    - `networkProfile.inputs.oamSubnet` — from CiQ IP Subnet sheet
    - `networkProfile.inputs.dthSubnet` — from user input
    - `compute.controlPlane.bootstrapConfig.apiServer.extraSANs` — K8S API VIP from CiQ
    - `compute.workerGroups[].replicas` — from CiQ POD Distribution
    - `compute.workerGroups[].bootstrapConfig.labels` — from CiQ POD Distribution
    - `compute.workerGroups[].computeProfile.inputs.ExtraSysctlParameters` — from CiQ Platform_pre-requisites
    - `compute.workerGroups[].computeProfile.inputs.ExtraGrubParameters` — from CiQ Platform_pre-requisites
    - `compute.workerGroups[].computeProfile.inputs.Hugepages1G` — from CiQ SRIOV_Hugepage
    - `config.overrides.bundle.functions.sriov-network-device-plugin.config.resourceList` — from CiQ SRIOV sheet
    - `config.overrides.bundle.functions.coredns.extraZones` — from CiQ Network Config

11. **Mark unknown values** with `# TODO:` comments:
    - Ceph monitor IPs and cluster IDs (always TODO — populated during deployment)
    - Service subnet, VLAN IDs (if not in CiQ or user input)
    - Any other values that couldn't be determined

12. **Create supporting files** (see `references/workload-repo-structure.md`):
    - Namespace YAML: `definition/namespaces/c-<cluster-name>.yaml`
    - Cluster kustomization: `kustomization.yaml`
    - Update parent `clusters/kustomization.yaml` to include new cluster

### Phase 4: Deliver

13. **Commit and push**:
    ```bash
    git add mgmt-clusters/mgmt-<site>-prod/clusters/<cluster-name>/
    git add mgmt-clusters/mgmt-<site>-prod/clusters/kustomization.yaml
    git commit -m "feat: add TCaasCluster definition for <cluster-name>"
    source /Users/ondrejkuchar/projects/caas/dt-brain-shared/.env
    git push origin feature/<cluster-name>
    ```

14. **Create GitLab MR** using the GitLab API:
    ```python
    import requests, os, urllib.parse
    token = os.environ.get('GITLAB_API_TOKEN_RW')
    base = 'https://gitlab.devops.telekom.de/api/v4'
    project = urllib.parse.quote('tdi-caas/runtime/workload', safe='')
    r = requests.post(f'{base}/projects/{project}/merge_requests',
        headers={'PRIVATE-TOKEN': token}, verify=False,
        json={
            'source_branch': 'feature/<cluster-name>',
            'target_branch': 'main',
            'title': 'feat: add TCaasCluster definition for <cluster-name>',
            'description': '<generated description>',
            'reviewer_ids': [<reviewer_ids>],
            'remove_source_branch': True,
        })
    ```
    Ask the user who should review the MR. Search for reviewers:
    ```python
    r = requests.get(f'{base}/users', headers=headers, verify=False, params={'search': '<name>'})
    ```

15. **Output provenance summary** — always end with a table showing where each value came from:

    | Data | Source |
    |------|--------|
    | OAM subnet | CiQ: IP Subnet 5GC, row 8 |
    | DTH subnet | User input |
    | Worker group replicas | CiQ: SRIOV_POD_Distribution |
    | SRIOV resources | CiQ: SRIOV_Hugepage |
    | Bundle version | Template: czprgc1-5gc-prod |
    | Ceph IPs | TODO (deployment) |

## Vendor-Specific Guidance

When the CiQ extractor detects the vendor, adapt your approach:

**Mavenir detected?**
→ Look for `SRIOV_Hugepage`, `SRIOV_POD_Distribution`, `Platform_pre-requisites` sheets
→ Expect 3 worker groups: UPF/VLB, iSME, ePDG
→ SRIOV names follow `mellanox_mlx5_dpdk_{side}_{interface}_{numa}` pattern

**Nokia detected?**
→ Look for `Cluster Info`, `Server Configuration`, `Network Configuration` sheets
→ Worker groups may be named differently (by function/product)
→ May use different NIC naming or SRIOV patterns

**Ericsson detected?**
→ Look for `Deployment Info`, `Network Design`, `Compute Design` sheets
→ May use ECCD/CCD-specific configuration patterns

**Unknown vendor?**
→ Use `--all` flag on ciq_extract.py to dump everything
→ Read all sheets and identify patterns matching TCaasCluster fields
→ Ask the user for clarification on vendor-specific conventions

## Important Notes

- **Never generate from scratch** — always start from an existing cluster template
- **Ceph secrets are always added by the user** — just create the directory structure and TODO markers
- **Track provenance** — the MR description must clearly state what came from CiQ, template, user, and what's TODO
- **Preserve template structure** — don't reorganize or reformat the YAML beyond necessary changes
- The workload repo may have the remote URL pointing to old path `cit/t-caas/runtime/workload` — the new path is `tdi-caas/runtime/workload`
