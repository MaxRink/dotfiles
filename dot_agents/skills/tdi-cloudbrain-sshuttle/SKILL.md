---
name: tdi-cloudbrain-sshuttle
user-invocable: true
description: Manage sshuttle tunnels to CaaS cluster master nodes for accessing switch management interfaces and internal cluster resources. Use when the user mentions "sshuttle", "tunnel", "connect to cluster network", "open tunnel", "cluster tunnel", or needs to establish a network tunnel to a CaaS cluster.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/sshuttle by codex-knowledge-curation/scripts/persist_project_skills.py. -->

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
source ~/.cloudbrain/.env && \
.venv/bin/python .claude/skills/network-diag/scripts/netbox-resolve-host.py <hostname> --format json
```

The `cluster_name` field in the output is used for the sshuttle connection.

## Environment Requirements

- **VPN**: Must be connected to Telekom VPN
- **sshuttle**: Must be installed (`brew install sshuttle` on macOS)
- **SSH access**: User must have SSH key access to `kube.$CLUSTER.caas.in.pan-net.eu`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check VPN is connected |
| Permission denied | Verify SSH key is loaded (`ssh-add -l`) |
| Already running | Kill existing process first |
| sudo password prompt | sshuttle may require sudo for routing — enter password when prompted |
