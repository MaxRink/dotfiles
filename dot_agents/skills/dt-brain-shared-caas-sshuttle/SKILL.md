---
name: dt-brain-shared-caas-sshuttle
description: Manage sshuttle tunnels to CaaS cluster master nodes for accessing switch management interfaces, BMC/BOR networks, and internal cluster resources. Use when the user mentions "sshuttle", "tunnel", "connect to cluster network", "open tunnel", "cluster tunnel", "BMC", "BOR", "BOR network", "xClarity", "iLO", "baremetal BMC", "management interface", or needs to establish a network tunnel to a CaaS cluster or access baremetal device BMCs.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-sshuttle by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# sshuttle Tunnel Management

Manage sshuttle tunnels to CaaS cluster master nodes. These tunnels route traffic through the cluster's kube API server, enabling SSH access to TOR switches and other internal infrastructure.

## Connection Command

```bash
sshuttle --no-latency-control -r kube.$CLUSTER_NAME.caas.in.pan-net.eu 100.64.0.0/10
```

- `100.64.0.0/10` covers switch management network
- `--no-latency-control` required for stable connections
- Connects via cluster's kube endpoint as SSH jump host

## Workflow

### 1. Check for Existing sshuttle Process

Before starting a new tunnel, always check if one is already running:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-status.py
```

If a process is found, **ask the user** whether to kill it before proceeding.

### 2. Start Tunnel

Use bash with `mode="async"` and `detach: true` so the tunnel persists:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-connect.py <CLUSTER_NAME>
```

To auto-kill existing processes first:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-connect.py <CLUSTER_NAME> --kill
```

The script outputs the PID on success. Wait a few seconds, then verify with `sshuttle-status.py`.

### 3. Verify Connection

```bash
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-status.py
```

Confirm the process is running and the target cluster matches expectations.

## Obtaining Cluster Name

The cluster name is typically obtained from NetBox. When given a server hostname:

```bash
source .env && \
.venv/bin/python .claude/skills/caas-network-diag/scripts/netbox-resolve-host.py <hostname> --format json
```

The `cluster_name` field in the output is used for the sshuttle connection.

## Environment Requirements

- **VPN**: Must be connected to Telekom VPN
- **sshuttle**: Must be installed (`brew install sshuttle` on macOS)
- **SSH access**: User must have SSH key access to `kube.$CLUSTER.caas.in.pan-net.eu`

## BMC Connectivity (BOR Network)

BMCs (xClarity, iLO) on baremetal CaaS cluster devices are on the **BOR network**, not directly reachable. Access requires an sshuttle tunnel through the **management cluster** for that tenant.

### How it works

1. Each baremetal cluster belongs to a NetBox **tenant** (e.g., `ic-defraf2`)
2. The tenant maps to a **management cluster** (e.g., `mgmt-05-prod`)
3. sshuttle tunnels through the mgmt cluster's kube API to reach BMC IPs
4. Device **Primary IPv4** in NetBox = BMC management IP

### Connect to a BMC

1. **Look up the mgmt cluster** for the tenant:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/bmc-lookup.py <tenant-slug>
# Or as JSON:
.venv/bin/python ${SKILL_DIR}/scripts/bmc-lookup.py --json <tenant-slug>
```

2. **Open sshuttle** to the mgmt cluster (use values from lookup):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-connect.py <mgmt-cluster> --kill
# If extra subnets needed (lookup output will show them):
.venv/bin/python ${SKILL_DIR}/scripts/sshuttle-connect.py <mgmt-cluster> --kill --extra-subnets <subnet1> <subnet2>
```

3. **Access the BMC**:

```bash
curl -k https://<bmc-ip>
```

### List all tenant → mgmt mappings

```bash
.venv/bin/python ${SKILL_DIR}/scripts/bmc-lookup.py --list
```

Mapping data is in `bmc_config.py` (`TENANT_MGMT_MAP`). Built from `kubectl get cc -A` on all prod mgmt clusters (32 tenants).

### Test BMC Connectivity Across All Tenants

```bash
# Dry-run: show mapping without opening tunnels
source .env && .venv/bin/python ${SKILL_DIR}/scripts/sshuttle-bmc-test.py --dry-run

# Test all tenants
source .env && .venv/bin/python ${SKILL_DIR}/scripts/sshuttle-bmc-test.py --non-interactive --skip-no-mgmt

# Test a specific tenant
source .env && .venv/bin/python ${SKILL_DIR}/scripts/sshuttle-bmc-test.py --tenant ic-defraf2
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check VPN is connected |
| Permission denied | Verify SSH key is loaded (`ssh-add -l`) |
| Already running | Kill existing process first |
| sudo password prompt | sshuttle may require sudo for routing — enter password when prompted |
