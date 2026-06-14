---
name: dt-brain-shared-caas-node-commands
description: Run diagnostic OS commands on CaaS cluster nodes via SSH or kubectl debug. Fetches a read-only kubeconfig from NetBox (or uses a local one), discovers nodes via kubectl, and executes allowed commands in parallel over SSH (using API server as ProxyJump bastion) or via kubectl debug node as a fallback. Use when the user mentions "node commands", "run command on nodes", "node diagnostics", "run on all nodes", "ssh to nodes", "check nodes", "node health", "disk usage nodes", "memory nodes", "node check", "cluster node ssh", "caas node", or needs to run diagnostic commands like uptime, df, free, dmesg, kubelet status on CaaS cluster nodes.
compatibility: Requires kubectl. SSH method also requires ssh, ssh-agent with loaded key, and Telekom VPN connection. kubectl-debug method only requires kubectl and a valid kubeconfig.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-node-commands by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Node Commands

Run diagnostic commands on all (or filtered) nodes of a CaaS cluster via SSH.

Use this skill when you need **OS-level** diagnostics — disk, memory, processes, dmesg, systemd services.
For Kubernetes-level queries (pods, deployments, events), use `caas-kubectl` instead.
This skill is also invoked as Step 7 of `caas-troubleshoot` for node-level investigation.

## Workflow

```
1. Identify the symptom or alert (see references/diagnostic-guide.md for mapping)
2. Pick the right command ID(s) from the table below
3. Run node-cmd.py — optionally filter to specific nodes with --node
4. Interpret the output (see references/diagnostic-guide.md)
```

The script automatically:
- Fetches the `caas_sec` kubeconfig from NetBox (or uses a local kubeconfig via `--kubeconfig`)
- Extracts the API server hostname as an SSH bastion (SSH method)
- Discovers nodes via `kubectl get nodes`
- Executes commands via SSH through the bastion, or via `kubectl debug node` as a fallback

### Run Command

```bash
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py <cluster-name> <command-id>
```

Examples:

```bash
# Check disk usage on all nodes
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py atgraf1-ndl-prod df_root

# Check kubelet status only on worker nodes
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py atgraf1-ndl-prod kubelet_status --node worker

# Use a local kubeconfig instead of fetching from NetBox
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py my-cluster uptime --kubeconfig /path/to/kubeconfig

# Use kubectl debug when SSH is not available (no VPN, no SSH key)
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py my-cluster ip_addr --kubeconfig /path/to/kubeconfig --method kubectl-debug

# Get JSON output for processing
source .env && .venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py atgraf1-ndl-prod free --format json

# List all available commands
.venv/bin/python .claude/skills/caas-node-commands/scripts/node-cmd.py --list-commands
```

### CLI Options

```
node-cmd.py <cluster-name> <command-id> [options]
  --kubeconfig PATH  Path to a local kubeconfig (skips NetBox fetch)
  --method METHOD   Execution method: ssh (default) or kubectl-debug (fallback)
  --node PATTERN    Filter nodes by name (substring or regex)
  --user USER       SSH user (default: ubuntu)
  --jobs N          Max parallel SSH connections (default: 10)
  --timeout SECS    SSH timeout per connection (default: 120)
  --format FORMAT   Output format: text (default), json
  --list-commands   List allowed command IDs and exit
```

## Command Reference

| ID | Command | Category |
|----|---------|----------|
| `uptime` | `uptime` | System |
| `hostname` | `cat /etc/hostname` | System |
| `uname` | `uname -a` | System |
| `df_root` | `df -h /` | Disk |
| `df_all` | `df -h` | Disk |
| `disk_io` | `iostat -xz 1 3` | Disk |
| `mdstat` | `cat /proc/mdstat` | Disk |
| `free` | `free -h` | Memory |
| `mem_huge` | `grep -i huge /proc/meminfo` | Memory |
| `top_cpu` | `ps aux --sort=-%cpu \| head -15` | Processes |
| `top_mem` | `ps aux --sort=-%mem \| head -15` | Processes |
| `zombie_parents` | Count zombies, show top parent processes and oldest samples | Processes |
| `zombie_pods` | Map zombie-spawning PIDs to Kubernetes pods via cgroup/crictl | Processes |
| `pid_to_pod` | Map container PIDs to pod name/namespace via crictl | Processes |
| `ip_addr` | `ip -br addr` | Network |
| `dmesg_err` | `dmesg --level=err,crit,alert,emerg -T \| tail -50` | Logs |
| `journal_err` | `journalctl --no-pager -p err -n 50` | Logs |
| `failed_units` | `systemctl list-units --failed --no-pager` | Services |
| `kubelet_status` | `systemctl status kubelet --no-pager -l` | Services |
| `containerd_status` | `systemctl status containerd --no-pager -l` | Services |
| `ntp_status` | `timedatectl status` | Time |

## Environment Requirements

- `NETBOX_API_TOKEN` — for kubeconfig retrieval from NetBox (caas_sec role); not needed with `--kubeconfig`
- **kubectl** — installed locally for node discovery and kubectl-debug method
- **VPN** — must be connected to Telekom VPN (SSH method only)
- **SSH key** — must be loaded in ssh-agent (`ssh-add -l` to verify) (SSH method only)

## Exit Codes

- **0** — all nodes executed the command successfully
- **1** — one or more nodes failed (SSH error, timeout, or non-zero remote exit code)
- **2** — invalid command ID provided

## Diagnostic Reference

See `references/diagnostic-guide.md` for:
- **Symptom → command mapping** — which commands to run for each alert type
- **Output interpretation** — how to read disk, memory, RAID, dmesg output
- **Error handling** — what to do when SSH fails, VPN is down, or nodes are unreachable
