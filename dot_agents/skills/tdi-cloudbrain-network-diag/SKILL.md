---
name: tdi-cloudbrain-network-diag
user-invocable: true
description: Diagnose network connectivity on CaaS TOR switches via SSH — check port status, VLANs, MAC tables, LLDP neighbors, counters, and switch logs/alarms. Supports Cisco NX-OS and Juniper JunOS. Use when the user mentions "network-diag", "check ports", "switch ports", "port status", "network connectivity", "TOR switch", "network diagnostics", "VLAN check", "MAC table", "interface status", or needs to diagnose network connectivity issues on CaaS cluster TOR switches.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/network-diag by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Network Diagnostics

Diagnose network connectivity on CaaS infrastructure by connecting to TOR switches and running vendor-specific show commands. Supports both Cisco NX-OS and Juniper switches.

## Workflow

```
1. Resolve hostname → cluster + TOR switches  (netbox-resolve-host.py)
2. Establish sshuttle tunnel                   (sshuttle skill)
3. Run switch diagnostics                      (switch-diag.py)
```

### Step 1: Resolve Hostname

Given a server hostname, resolve it to cluster name, TOR switches, IPs, and port mappings:

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/netbox-resolve-host.py <hostname>
```

JSON output (for scripting):

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/netbox-resolve-host.py <hostname> --format json
```

Output provides:
- `cluster_name` — needed for sshuttle
- `switches[]` — name, primary_ip, vendor (cisco/juniper), role
- `port_mappings[]` — which server NIC port connects to which switch port

### Step 2: Establish sshuttle Tunnel

Use the **sshuttle** skill to open a tunnel to the cluster. The tunnel must be active before SSH to switches will work.

```bash
# Check if tunnel is already running
.venv/bin/python .claude/skills/sshuttle/scripts/sshuttle-status.py

# Start tunnel (use detach: true in async bash)
.venv/bin/python .claude/skills/sshuttle/scripts/sshuttle-connect.py <CLUSTER_NAME>
```

### Step 3: Run Switch Diagnostics

**Default mode** — run predefined commands and show output:

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py <switch_ip> \
  --vendor <cisco|juniper> \
  --ports <port1>,<port2>
```

**Specific commands** — choose which diagnostics to run:

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py <switch_ip> \
  --vendor cisco \
  --ports Ethernet1/1,Ethernet1/2 \
  --commands port_status,mac_table,vlan_port
```

**Interactive mode** — open SSH session for manual investigation:

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py <switch_ip> --interactive
```

Use bash `mode="async"` for interactive sessions so the user can type commands.

**Log & alarm mode** — check switch logs, alarms, and uptime:

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py <switch_ip> \
  --vendor juniper \
  --ports <port1>,<port2> \
  --logs
```

This runs global commands (recent logs, per-port log history, system alarms, chassis alarms, uptime) in addition to any port-specific commands. Can be combined with `--commands` or used standalone.

**Specific log commands only:**

```bash
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py <switch_ip> \
  --vendor juniper \
  --ports <port1>,<port2> \
  --commands log_recent,log_interface,alarms,uptime
```

**List available commands:**

```bash
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py --list-commands
```

## Complete Example

```bash
# 1. Resolve hostname
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/netbox-resolve-host.py hrzagt6-caas-13-dev-7gx8d --format json

# Output shows: cluster_name=hrzagt6-caas-13-dev, switches with IPs and ports

# 2. Start sshuttle tunnel
.venv/bin/python .claude/skills/sshuttle/scripts/sshuttle-connect.py hrzagt6-caas-13-dev

# 3. Diagnose ports on both TOR switches
source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py 100.64.x.x \
  --vendor cisco --ports Ethernet1/1,Ethernet1/2

source ~/.cloudbrain/.env && \
.venv/bin/python ${SKILL_DIR}/scripts/switch-diag.py 100.64.x.y \
  --vendor juniper --ports xe-0/0/1,xe-0/0/2
```

## Vendor Command References

For additional commands beyond defaults:
- **Cisco NX-OS**: See `references/cisco-commands.md`
- **Juniper JunOS**: See `references/juniper-commands.md`

## What to Look For

| Symptom | Check | Meaning |
|---------|-------|---------|
| Port down | `port_status` | Physical link failure, cable issue, or admin shutdown |
| No MACs learned | `mac_table` | No L2 connectivity — check cable, VLAN, STP |
| Wrong VLAN | `vlan_port` | Port assigned to incorrect VLAN |
| Packet errors | `port_counters`/`port_extensive` | CRC errors, input errors — cable/optic issue |
| Missing neighbor | `cdp_neighbor`/`lldp_neighbor` | Server NIC not detected by switch |
| Link flapping | `log_interface` | Repeated up/down events — cable/NIC/optic issue |
| System issues | `alarms`, `chassis_alarms` | Hardware alarms on the switch itself |
| Recent events | `log_recent` | Last 100 log messages — look for errors, config changes |
| Switch stability | `uptime` | How long since last reboot, last config change |

## Environment Requirements

- `NETBOX_API_TOKEN` — for hostname resolution
- `LDAP_ID` — for SSH to switches (read-only account for CaaS team)
- **sshuttle** — tunnel must be active
- **VPN** — must be connected to Telekom VPN

## Switch Access Setup

Your LDAP account must be added to the network devices before you can SSH to switches. This is a **read-only** account — CaaS team members cannot make configuration changes.

To get access, contact:
- **Jaroslav Jurik** — network device access management
- **Robert Petracic** — network device access management

They will add your LDAP_ID to the switch access list. Once added, set your `LDAP_ID` in `~/.cloudbrain/.env`:

```bash
LDAP_ID=f356184  # your LDAP username
```
