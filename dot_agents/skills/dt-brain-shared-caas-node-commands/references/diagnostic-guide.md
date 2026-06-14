# Node Diagnostics Guide

## Symptom → Command Mapping

Use this table to pick the right command(s) based on the reported issue or alert.

| Symptom / Alert | Commands to Run | What to Look For |
|-----------------|-----------------|------------------|
| Node NotReady | `kubelet_status`, `failed_units`, `dmesg_err` | Kubelet crash loops, failed systemd units, kernel panics or hardware errors |
| Kubelet issues | `kubelet_status`, `journal_err`, `containerd_status` | Kubelet restart count, containerd socket errors, certificate expiry in journal |
| Disk pressure / DiskPressure | `df_root`, `df_all`, `disk_io` | Root filesystem >85% is warning, >95% is critical. High `await` in iostat indicates I/O bottleneck |
| OOMKilled pods / MemoryPressure | `free`, `top_mem`, `mem_huge` | Low available memory, large RSS consumers, hugepage misconfiguration eating memory |
| High CPU / load alerts | `top_cpu`, `uptime` | Load average exceeding CPU core count, runaway processes consuming >50% CPU |
| Zombie process alerts | `zombie_parents`, `zombie_pods` | Total zombie count, which parent processes are leaking, which pods own them |
| Identify pod for a host PID | `pid_to_pod` | Maps container PIDs to pod name and namespace |
| Network unreachable / packet loss | `ip_addr`, `dmesg_err` | Missing or DOWN interfaces, NIC driver errors, link flaps in dmesg |
| NTP / time drift alerts | `ntp_status` | "NTP synchronized: no" or large offset (>100ms can cause cert validation failures) |
| RAID degradation | `mdstat` | Arrays showing `[U_]` or `[_U]` instead of `[UU]` — means a disk has failed |
| General triage (unknown issue) | `uptime`, `failed_units`, `dmesg_err`, `journal_err` | Start broad: check uptime for recent reboots, failed services, kernel and system errors |

## Interpreting Output

### Disk (`df_root`, `df_all`)

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   45G  2.5G  95% /
```

- **>85% used**: Warning — investigate what's consuming space (logs, container images, etcd)
- **>95% used**: Critical — kubelet starts evicting pods, etcd may refuse writes
- Common culprits: `/var/log` (logs not rotated), `/var/lib/containerd` (unused images), `/var/lib/etcd` (large database)

### Memory (`free`)

```
              total        used        free      shared  buff/cache   available
Mem:           31Gi        12Gi       1.2Gi       256Mi        18Gi        18Gi
```

- Focus on **available** (not free) — buff/cache is reclaimable
- **available <5%** of total: memory pressure likely, OOM kills imminent
- **available <1Gi** on a control plane node: etcd and apiserver at risk

### Processes (`top_cpu`, `top_mem`)

- kube-apiserver, etcd, kubelet are expected high consumers
- Unknown processes consuming >20% CPU/MEM warrant investigation
- Multiple zombie processes (`Z` state) indicate a process leak

### Zombie Diagnostics (`zombie_parents`, `zombie_pods`)

- Use `zombie_parents` first to get total count and identify which parent processes are not reaping children
- Use `zombie_pods` to map zombie-spawning processes to Kubernetes pod/namespace (uses cgroup + crictl)

### PID to Pod Mapping (`pid_to_pod`)

- Maps running container PIDs to their Kubernetes pod name and namespace via crictl
- Useful for identifying which pod owns a high-CPU/high-MEM process spotted in `top_cpu`/`top_mem`

### RAID (`mdstat`)

```
md0 : active raid1 sda1[0] sdb1[1]
      999872 blocks [2/2] [UU]
```

- `[UU]` = healthy (all disks active)
- `[U_]` or `[_U]` = **degraded** — one disk has failed, needs replacement
- `[2/1]` = only 1 of 2 disks active — critical

### dmesg errors (`dmesg_err`)

Key patterns to watch for:
- `Out of memory: Kill process` — OOM killer activated
- `EXT4-fs error` or `XFS error` — filesystem corruption
- `Hardware Error` or `MCE` — hardware failure (CPU, memory)
- `link is not ready` or `carrier lost` — network link flap
- `I/O error, dev sd` — disk failure
- `EDAC MC` — ECC memory errors (correctable=warning, uncorrectable=critical)

### Journal errors (`journal_err`)

Key patterns:
- `kubelet.*failed` — kubelet operational issues
- `containerd.*error` — container runtime problems
- `oom-kill` — out of memory events
- `certificate.*expir` — TLS certificate issues

### Failed units (`failed_units`)

Any failed unit needs attention. Common ones:
- `kubelet.service` — critical, node will go NotReady
- `containerd.service` — critical, no containers can run
- `chrony.service` / `systemd-timesyncd` — NTP down, time drift risk

## Error Handling

### SSH connection fails

If SSH returns RC 255 or times out:
1. **VPN not connected** — most common cause. Verify VPN is active.
2. **SSH key not loaded** — run `ssh-add -l` to check, `ssh-add` to load.
3. **Bastion unreachable** — the API server hostname may not resolve. Check DNS / VPN.
4. **Node rebooting** — wait and retry; check if node is in `NotReady` state via kubectl.

### Kubeconfig fetch fails

- **NETBOX_API_TOKEN not set** — ensure `.env` is sourced
- **Cluster not found** — verify cluster name matches NetBox exactly (case-sensitive)
- **Wrong role** — the script uses `caas_sec` role; cluster may only have a different role

### Partial failures (some nodes succeed, some fail)

- Normal during rolling updates or node replacements
- Filter to failed nodes with `--node <name>` and retry
- If control plane nodes fail but workers succeed (or vice versa), check network segmentation
