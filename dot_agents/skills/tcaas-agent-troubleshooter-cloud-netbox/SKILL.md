---
name: tcaas-agent-troubleshooter-cloud-netbox
description: This skill should be used when the user mentions "NetBox", "DCIM", "virtualization clusters", "caas clusters", asks to "list clusters", "get cluster details", "search netbox", or needs to access infrastructure information from the NetBox DCIM tool.
---

<!-- Imported from tdi-caas/tools/tcaas-agent-troubleshooter/skills/cloud-netbox by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# NetBox Integration

This skill provides tools to interact with the NetBox DCIM (Data Center Infrastructure Management) tool for the CaaS infrastructure.

## Quick Start

1. Set `NETBOX_API_TOKEN` environment variable:
   ```bash
   export NETBOX_API_TOKEN="your-api-token"
   ```
2. Connect to Telekom VPN
3. Run scripts with `.venv/bin/python ${SKILL_DIR}/scripts/<script>.py`

To get an API token: Log in to https://dcim.tools.in.pan-net.eu/ → Profile → API Tokens → Create new token

## Instance Details

- **Base URL**: `https://dcim.tools.in.pan-net.eu/`
- **VPN Required**: Yes - API access only works when connected to Telekom VPN
- **Authentication**: API Token via HTTP header (see `references/api-reference.md` for details)

## Operations

### CaaS Domain Conventions

- **"Site"** (as the team refers to it) is stored as the **`tenant`** field on clusters/devices — not the `site` field. The `site` field points to a physical DC (e.g., `HRZAGD001`). Tenant naming pattern: `[<cloud-type>-<location-code>]` (e.g., `[CL-HRZAGT6]`, `[IC-HRZAGT4]`).
- **Hardware profile** of a server is in `custom_fields.hw_versions` (e.g., `Profile7.1`, `Profile26.6ai.1`), distinct from the hardware model (device type).

### NetBox Architecture Notes

NetBox models network interface cards as **separate device objects** linked to server devices:

- **Server Devices**: Physical servers with roles like "Server Compute" or "Server Management"
- **NIC Devices**: Child devices with naming pattern `<server-name>.NIC1`, `<server-name>.NIC2`, etc.
- **Interfaces**: Actual network ports on NIC devices that connect to switches via cables
- **Link Peers**: Relationships showing which switch port each NIC interface connects to

**Typical Connection Pattern**:
- Servers have multiple NIC devices for redundancy
- Each NIC has 2+ ports (Port 0, Port 1, etc.)
- Ports connect to TOR switches in pairs: Port 0 → TOR Switch A, Port 1 → TOR Switch B
- This provides redundant network paths using bonded interfaces

This structure allows detailed tracking of complex network topologies with multiple NICs per server.

### List Virtualization Clusters

List virtualization clusters in NetBox:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py
```

Options:
- `--group GROUP` - Filter by cluster group name (default: CaaS)
- `--site SITE` - Filter by site (country name/code or exact site name)
  - **Countries**: AT/Austria, SK/Slovakia, DE/Germany, CZ/Czechia, HU/Hungary, HR/Croatia, PL/Poland, MK/Macedonia, ME/Montenegro, US/USA
  - **Exact site**: SKBRAD003, ATGRAD001, etc.
- `--type TYPE` - Filter by cluster type (e.g., baremetal, openstack)
- `--status STATUS` - Filter by status (active, planned, staged, decommissioning, offline)
- `--all` - Show all clusters (ignore group filter)
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Limit results (default: no limit)

Examples:
```bash
# List all CaaS clusters (default)
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py

# List clusters by country (using name or code)
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site slovakia --all
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site SK --all

# List baremetal clusters in Austria
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --type baremetal --site austria --all

# List only baremetal CaaS clusters in Germany
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --type baremetal --site DE

# List clusters in specific group
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --group openstack

# List clusters at specific site
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site ATGRAD001

# List all clusters in Hungary
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site hungary --all

# List all clusters regardless of group
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --all

# Get JSON output for scripting
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --format json

# Combine filters
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --group CaaS --type baremetal --site austria --status active
```

Output shows: ID, Name, Group, Site, Status, Device Count, VM Count, Description

**New: Summary totals** show total clusters, devices, and VMs at the bottom of the output.

### Get Cluster Details

Get detailed information about a specific cluster:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py <cluster-id-or-name>
```

Options:
- `--format FORMAT` - Output format: `detailed` (default), `json`
- `--show-vms` - Include list of virtual machines in the cluster
- `--show-devices` - Include list of devices (physical servers) in the cluster
- `--product` - Include full CaaS product details (functions, versions, actions)
- `--id` - Treat argument as cluster ID (faster lookup)
- `--name` - Treat argument as cluster name (searches by name)

Examples:
```bash
# Get cluster by ID
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py 123

# Get cluster by name
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py "my-cluster-name"

# Show cluster with VMs list
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py 123 --show-vms

# Show cluster with devices (physical servers)
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py 123 --show-devices

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py 123 --format json

# Include full CaaS product details
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py atgraf1-ndl-prod --product
```

Output includes:
- Basic info: ID, name, type, group, site, status, device count, VM count
- Kubernetes version and CaaS product version (always shown if available)
- Metadata: tags, comments, custom fields
- Devices: physical servers in cluster (with --show-devices)
- Virtual machines: count and list (with --show-vms)
- Full CaaS product details: functions, versions, actions (with --product)

### Get Cluster Secrets / Kubeconfig

Retrieve kubeconfigs and other secrets from the NetBox secrets plugin:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py <cluster-name-or-id>
```

Options:
- `--role ROLE` - Secret role to retrieve: `caas_admin` (default), `caas_clab`, `caas_oidc`, `caas_sec`, `caas_customer`
- `--list` - List available secrets for the cluster (no plaintext shown)
- `--save` - Save kubeconfig to auto-named file (`<cluster>-<role>-kubeconfig`)
- `--save-to PATH` - Save kubeconfig to a specific file path
- `--format FORMAT` - Output format: `detailed` (default), `json`, `plain` (raw kubeconfig only)
- `--id` - Treat argument as cluster ID (faster lookup)
- `--name` - Treat argument as cluster name

Examples:
```bash
# List all secrets for a cluster
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --list

# Get admin kubeconfig (default role)
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod

# Get specific role kubeconfig
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --role caas_oidc

# Get raw kubeconfig for piping
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --format plain > kubeconfig.yaml

# Save kubeconfig to auto-named file
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --save

# Save to specific path
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --save-to /tmp/kubeconfig.yaml

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-secret.py hudpxc1-5gc-prod --format json
```

#### Secret Roles Reference

| Role Slug | Description | Typical Use |
|-----------|-------------|-------------|
| `caas_admin` | CaaS admin kubeconfig | Cluster administration (default) |
| `caas_clab` | clab automation kubeconfig | Automated tooling / CI pipelines |
| `caas_oidc` | OIDC user kubeconfig | OIDC-authenticated access |
| `caas_sec` | Security kubeconfig | Security team access |
| `caas_customer` | Customer kubeconfig | Customer/tenant access |

Output includes:
- Secret name, ID, and role
- Decoded kubeconfig content (base64-decoded automatically)
- Save-to-file with 600 permissions (owner read/write only)

### Get Server Network Connections

Show physical network connections (switch/port mappings) for servers:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py <server-identifier>
```

**Input Methods:**
- **Device name**: Exact NetBox device name (e.g., `F.1.1.A1.7`)
- **Hostname**: Server hostname with `--by-hostname` flag
- **Cluster**: Show all servers in cluster with `--cluster` flag

**Options:**
- `--by-hostname` - Treat identifier as hostname instead of device name
- `--cluster` - Treat identifier as cluster name, show all servers in cluster
- `--site SITE` - Filter by site when searching by hostname (optional)
- `--format FORMAT` - Output format: `table` (default), `detailed`, `json`

**Examples:**
```bash
# Get connections by device name
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py F.1.1.A1.7

# Get connections by hostname
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py mkskof2-5gc-lab-d6w5t --by-hostname

# Show all servers in a cluster
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py mkskof2-5gc-lab --cluster

# Get detailed output with full switch information
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py F.1.1.A1.7 --format detailed

# JSON output for scripting
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py mkskof2-5gc-lab --cluster --format json
```

**Output includes:**
- Server device name and hostname
- All NIC devices associated with the server
- Port-to-switch mappings for each NIC
- Switch names, types, and roles (TOR switch A/B, Spine, etc.)
- Connected switch ports/interfaces
- Summary of unique switches connected

**Use cases:**
- Understanding cluster network topology
- Troubleshooting connectivity issues
- Planning network maintenance
- Documenting physical infrastructure
- Verifying redundant connections

### Search NetBox

Search across NetBox objects (clusters, VMs, devices):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py <query>
```

Options:
- `--type TYPE` - Filter by object type: `all` (default), `clusters`, `vms`, `devices`
- `--group GROUP` - Filter clusters by group name
- `--site SITE` - Filter by site name
- `--limit N` - Limit results per type (default: 50)
- `--format FORMAT` - Output format: `table` (default), `json`

Examples:
```bash
# Search everything
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py "kubernetes"

# Search only clusters
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py "prod" --type clusters

# Search VMs in caas group
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py "controller" --type vms --group caas

# Search at specific site
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py "nginx" --site fra01

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/netbox-search.py "database" --format json
```

Searches in:
- **Clusters**: name, description, comments
- **Virtual Machines**: name, description, comments
- **Devices**: name, description, comments

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| NETBOX_API_TOKEN not set | Missing environment variable | `export NETBOX_API_TOKEN="your-token"` |
| Connection failed | Not on VPN | Connect to Telekom VPN |
| HTTP 401 | Invalid or expired token | Generate new token in NetBox UI |
| HTTP 403 | Insufficient permissions | Request read access to NetBox |
| HTTP 404 | Object not found | Check cluster ID/name spelling |
| No results found | Wrong filter or no data | Try different filters or --all flag |

## Tips

- **Site filtering**: Use country names or ISO codes (see `references/sites.md`)
- **Group names** are case-sensitive: Use `CaaS` (not `caas`)
- **Cross-skill integration**: See `references/usage-examples.md` for workflows with PagerDuty, CaaS products, etc.

## Security Notes

1. Never commit NETBOX_API_TOKEN to version control
2. VPN required for all operations
3. All operations are read-only
4. SSL verification disabled for internal certificate - only use on trusted networks
