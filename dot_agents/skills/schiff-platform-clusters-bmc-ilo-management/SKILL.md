---
name: schiff-platform-clusters-bmc-ilo-management
description: 'Manage HPE iLO BMC access, serial consoles, and sessions for BM4X bare-metal nodes. USE WHEN: connecting to BMC serial console, troubleshooting VSP session locks, managing iLO sessions, gathering node evidence via serial port, power cycling nodes via Redfish API. Keywords: BMC, iLO, VSP, serial console, Redfish, sshpass, power control, session management.'
---

<!-- Imported from schiff/platform/clusters/.github/skills/bmc-ilo-management by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# BMC / iLO Management

## Overview

HPE iLO (Integrated Lights-Out) provides out-of-band management for bare-metal servers. In the T-CaaS BM4X environment, BMC access goes through an RCS SSH jumphost. This skill covers all BMC operations needed for cluster debugging.

## Connection Architecture

```
Workstation -> SSH (ProxyJump RCS) -> BMC iLO CLI -> VSP (Virtual Serial Port) -> Node OS
```

- **RCS jumphost**: Configured in `~/.ssh/config` as host `RCS`
- **BMC credentials**: Stored in Kubernetes secrets in the infrastructure namespace (e.g., `caprf-dev-bn461`)
- **Node credentials**: user `schiff`, password from cluster config
- **SSH key algorithms**: iLO requires legacy algorithms: `ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-ed25519`

## Helper Scripts

All scripts are in the `scripts/` directory and source `scripts/env.sh` for environment variables.

### Serial Console Access

```bash
# Auto-detect host and connect
./scripts/bmc-console.sh

# Connect to specific host
./scripts/bmc-console.sh bn461com5i63

# Show host info without connecting
./scripts/bmc-console.sh --info

# List all available BMC hosts
./scripts/bmc-console.sh --list
```

### Session Management

When VSP shows "Virtual Serial Port is currently in use by another session":

```bash
# Option 1: Release VSP lock only (other user's SSH stays alive)
./scripts/bmc-console.sh --kill-vsp <host>
# This runs: STOP /system1/oemHPE_vsp1 via iLO CLI

# Option 2: List active sessions to find the blocker
./scripts/bmc-console.sh --sessions <host>

# Option 3: Terminate a specific session entirely (SSH drops)
./scripts/bmc-console.sh --kill-session <host> <session_id>
# This calls: DELETE /redfish/v1/SessionService/Sessions/<id>
```

**Key distinction:**
| Method | Command | Effect |
|--------|---------|--------|
| Kill VSP lock | `STOP /system1/oemhp_vsp1` (iLO 5) or `STOP /system1/oemHPE_vsp1` (iLO 6) | Releases VSP only, SSH stays |
| Delete session (Redfish) | `DELETE .../Sessions/<id>` | Kills entire iLO session |
| Exit own VSP | `ESC+(` (press Escape then open-paren) | Returns to iLO CLI |

### Power Control

```bash
./scripts/bmc-power.sh status              # All cluster machines
./scripts/bmc-power.sh status <host>       # Specific host
./scripts/bmc-power.sh on <host>           # Power on
./scripts/bmc-power.sh off <host>          # Graceful shutdown
./scripts/bmc-power.sh reset <host>        # Force restart
./scripts/bmc-power.sh cycle <host>        # Power cycle
./scripts/bmc-power.sh force-off <host>    # Hard power off
```

### Node SSH (Direct)

```bash
./scripts/bmc-ssh.sh                       # Auto-detect, SSH as schiff
./scripts/bmc-ssh.sh <host> root           # SSH as root
./scripts/bmc-ssh.sh --list                # List hosts with IPs
```

Note: Direct SSH only works if the node's network is up. If unreachable, use BMC serial console instead.

### Evidence Gathering

```bash
# Automated evidence collection via serial console
./scripts/bmc-evidence.sh                  # Auto-detect host
./scripts/bmc-evidence.sh <host> <label>   # Custom label
./scripts/bmc-evidence.sh --commands       # Dry-run: show what commands run
```

Evidence is saved to `evidence/node/<label>/` with per-category log files.

## Redfish API Reference

The Redfish REST API is available at `https://<bmc-host>/redfish/v1/`. Common endpoints:

```bash
# Get system power state and health
curl -sk -u "$USER:$PASS" "https://<bmc>/redfish/v1/Systems/1" | jq '{PowerState, Status}'

# List active sessions
curl -sk -u "$USER:$PASS" "https://<bmc>/redfish/v1/SessionService/Sessions" | jq '.Members'

# Get session details (find UserIP, UserTag, LoginTime)
curl -sk -u "$USER:$PASS" "https://<bmc>/redfish/v1/SessionService/Sessions/<id>" | jq '.Oem.Hpe'

# Delete a session
curl -sk -u "$USER:$PASS" -X DELETE "https://<bmc>/redfish/v1/SessionService/Sessions/<id>"

# Power action
curl -sk -u "$USER:$PASS" -X POST \
  -H "Content-Type: application/json" \
  -d '{"ResetType":"ForceRestart"}' \
  "https://<bmc>/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"
```

## iLO CLI Commands

When connected via SSH to the BMC:

| Command | Purpose |
|---------|---------|
| `VSP` | Start Virtual Serial Port (serial console) |
| `STOP /system1/oemhp_vsp1` | Kill active VSP session (iLO 5: `oemhp_vsp1`, iLO 6: `oemHPE_vsp1`) |
| `SHOW /system1` | System overview |
| `SHOW /system1/log1` | System event log |
| `SHOW /map1/accounts1` | User accounts |
| `power` | Power status |
| `reset /system1` | Reset system |
| `ESC+(` | Exit VSP back to CLI |

## Troubleshooting

### VSP "in use by another session"
1. Try `STOP /system1/oemhp_vsp1` from iLO CLI (use `oemHPE_vsp1` on iLO 6)
2. If that fails, use Redfish API to DELETE the blocking session
3. Check session details to see who's connected (`--sessions`)

### SSH connection reuse / multiplexing closes BMC session
If your SSH config has `ControlMaster auto` and a prior connection to the same BMC was interrupted, new connections may immediately close (`Shared connection closed`). Fix: add `-o ControlPath=none` to bypass SSH multiplexing.

### Running sudo through serial console (VSP)
Heredocs (`<<EOF`) and herestrings (`<<<`) do **not** work through VSP serial console. Use pipe instead:
```bash
# Works:
echo PASSWORD | sudo -S whoami
echo PASSWORD | sudo -S sed -i 's/old/new/' /path/to/file

# Does NOT work through serial console:
sudo -S command <<< 'PASSWORD'
sudo bash -c 'cat > /file << EOF\n...\nEOF'
```
For multi-line file writes, use incremental `sed -i` commands rather than heredocs.

### SSH connection timeout to BMC
- Verify RCS jumphost is accessible: `ssh RCS hostname`
- Check BMC hostname resolves: `dig <bmc-host>`
- Verify credentials: `kubectl get secret <host> -n <infra-ns> -o jsonpath='{.data.password}' | base64 -d`

### Node unreachable via SSH
- Check power state: `./bmc-power.sh status <host>`
- Check if node has booted: BMC event log (`SHOW /system1/log1`)
- Use serial console instead: `./bmc-console.sh <host>`
- Check network config on node via serial console: `ip addr`, `ip route`
