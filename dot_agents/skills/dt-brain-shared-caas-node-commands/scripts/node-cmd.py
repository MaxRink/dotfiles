#!/usr/bin/env python3
"""
Run diagnostic commands on CaaS cluster nodes via SSH or kubectl debug.

Fetches a read-only kubeconfig from NetBox (caas_sec role), discovers nodes
via kubectl, and executes allowed commands on all (or filtered) nodes in parallel.

Two execution methods are supported:
  - ssh (default): SSH ProxyJump through the API server to reach nodes.
  - kubectl-debug: Uses 'kubectl debug node' with chroot as a fallback when
    SSH is unavailable (no VPN, no bastion, or no SSH key).

Usage:
    node-cmd.py <cluster-name> <command-id> [options]
    node-cmd.py --list-commands
"""

import argparse
import atexit
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

# Resolve path to netbox-get-secret.py relative to this script
SKILL_DIR = Path(__file__).resolve().parent.parent
NETBOX_SECRET_SCRIPT = (
    SKILL_DIR.parent / "cloud-netbox" / "scripts" / "netbox-get-secret.py"
)
PYTHON = SKILL_DIR.parent.parent.parent / ".venv" / "bin" / "python"

SSH_USER = "ubuntu"
SSH_JOBS = 10
SSH_TIMEOUT = 120
KUBECTL_DEBUG_IMAGE = "busybox:1.36"
KUBECTL_DEBUG_NAMESPACE = "default"

ALLOWED_COMMANDS: dict[str, str] = {
    # System basics
    "uptime": "uptime",
    "hostname": "cat /etc/hostname",
    "uname": "uname -a",
    # Disk
    "df_root": "df -h /",
    "df_all": "df -h",
    "disk_io": "iostat -xz 1 3",
    "mdstat": "cat /proc/mdstat",
    # Memory
    "free": "free -h",
    "mem_huge": "grep -i huge /proc/meminfo",
    # Processes
    "top_cpu": "ps aux --sort=-%cpu | head -15",
    "top_mem": "ps aux --sort=-%mem | head -15",
    # Zombie diagnostics
    "zombie_parents": (
        "total=$(ps -eo stat | awk '/^Z/{c++} END{print c+0}'); "
        "echo \"Total zombies: $total\" && "
        "echo '--- Top parent processes ---' && "
        "ps -eo ppid,pid,stat,comm | awk '$3 ~ /^Z/ {ppid[$1]++} "
        "END {for (p in ppid) print ppid[p], p}' | sort -rn | head -10 | "
        "while read cnt p; do printf '%6d zombies <- PID %-8s (%s)\\n' $cnt $p "
        "\"$(cat /proc/$p/comm 2>/dev/null || echo EXITED)\"; done && "
        "echo '--- Sample zombie processes (oldest first, top 20) ---' && "
        "ps -eo pid,ppid,stat,etimes,comm | awk '$3 ~ /^Z/' | sort -k4 -rn | head -20"
    ),
    "zombie_pods": (
        "ps -eo ppid,stat | awk '$2 ~ /^Z/ {print $1}' | sort -u | "
        "while read ppid; do "
        "cid=$(awk -F/ '{for(i=1;i<=NF;i++) if($i ~ /^[a-f0-9]{64}/) print $i}' "
        "/proc/$ppid/cgroup 2>/dev/null | tail -1); "
        "[ -z \"$cid\" ] && continue; "
        "cnt=$(ps -eo ppid,stat | awk -v p=$ppid '$1==p && $2 ~ /^Z/' | wc -l); "
        "sudo crictl inspect $cid 2>/dev/null | "
        "awk -F'\"' '/kubernetes.pod.namespace/{ns=$4} /kubernetes.pod.name/{pod=$4} "
        "/kubernetes.container.name/{cname=$4} "
        "END {printf \"ZOMBIES=%d  NS=%s  POD=%s  CONTAINER=%s\\n\", "
        "'\"$cnt\"', ns, pod, cname}'; done | sort -t= -k2 -rn"
    ),
    # PID to pod mapping (looks up the pod for a specific host PID via its cgroup)
    "pid_to_pod": (
        "echo 'Usage: check output for PID-to-pod mapping of all running containers' && "
        "sudo crictl ps -q 2>/dev/null | head -50 | while read cid; do "
        "pid=$(sudo crictl inspect --output json $cid 2>/dev/null | "
        "grep -m1 '\"pid\"' | grep -oP '\\d+'); "
        "[ -z \"$pid\" ] && continue; "
        "sudo crictl inspect $cid 2>/dev/null | "
        "awk -F'\"' '/kubernetes.pod.namespace/{ns=$4} /kubernetes.pod.name/{pod=$4} "
        "/kubernetes.container.name/{cname=$4} "
        "END {printf \"PID=%-8s  NS=%-20s  POD=%s  CONTAINER=%s\\n\", "
        "'\"$pid\"', ns, pod, cname}'; done | sort -t= -k3"
    ),
    # Network
    "ip_addr": "ip -br addr",
    # Logs & errors
    "dmesg_err": "dmesg --level=err,crit,alert,emerg -T | tail -50",
    "journal_err": "journalctl --no-pager -p err -n 50",
    # Systemd services
    "failed_units": "systemctl list-units --failed --no-pager",
    "kubelet_status": "systemctl status kubelet --no-pager -l",
    "containerd_status": "systemctl status containerd --no-pager -l",
    # Time
    "ntp_status": "timedatectl status",
}

# Temp kubeconfig path for cleanup
_temp_kubeconfig: str | None = None


def _cleanup_temp_kubeconfig():
    if _temp_kubeconfig and os.path.exists(_temp_kubeconfig):
        os.unlink(_temp_kubeconfig)


atexit.register(_cleanup_temp_kubeconfig)


def extract_bastion(kubeconfig_path: str) -> str | None:
    """Extract the API server hostname from a kubeconfig to use as SSH bastion."""
    try:
        with open(kubeconfig_path, "r") as f:
            for line in f:
                match = re.search(r"server:\s*(https?://\S+)", line)
                if match:
                    parsed = urlparse(match.group(1))
                    return parsed.hostname
    except OSError as e:
        print(f"[ERROR] Cannot read kubeconfig: {e}", file=sys.stderr)
    return None


def print_allowed_commands():
    """Print allowed command IDs and their commands."""
    print("Allowed commands:\n")
    max_id = max(len(k) for k in ALLOWED_COMMANDS)
    for cmd_id in sorted(ALLOWED_COMMANDS):
        print(f"  {cmd_id:<{max_id}}  →  {ALLOWED_COMMANDS[cmd_id]}")


def fetch_kubeconfig(cluster_name: str) -> str:
    """Fetch caas_sec kubeconfig from NetBox and save to temp file."""
    global _temp_kubeconfig

    if not NETBOX_SECRET_SCRIPT.exists():
        print(
            f"[ERROR] NetBox secret script not found: {NETBOX_SECRET_SCRIPT}",
            file=sys.stderr,
        )
        sys.exit(1)

    python_bin = str(PYTHON) if PYTHON.exists() else sys.executable

    cmd = [
        python_bin,
        str(NETBOX_SECRET_SCRIPT),
        cluster_name,
        "--role", "caas_sec",
        "--format", "plain",
    ]

    print(f"[*] Fetching caas_sec kubeconfig for '{cluster_name}' from NetBox...")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        print("[ERROR] Timed out fetching kubeconfig from NetBox", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"[ERROR] Failed to fetch kubeconfig:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    kubeconfig_content = result.stdout.strip()
    if not kubeconfig_content:
        print("[ERROR] Empty kubeconfig returned from NetBox", file=sys.stderr)
        sys.exit(1)

    fd, path = tempfile.mkstemp(prefix="node-cmd-kc-", suffix=".yaml")
    with os.fdopen(fd, "w") as f:
        f.write(kubeconfig_content)
    os.chmod(path, 0o600)

    _temp_kubeconfig = path
    print(f"[*] Kubeconfig saved to temp file")
    return path


def get_cluster_nodes(kubeconfig_path: str) -> list[dict]:
    """Discover cluster nodes via kubectl get nodes -owide."""
    cmd = [
        "kubectl", "--kubeconfig", kubeconfig_path,
        "get", "nodes", "-owide", "--no-headers",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("[ERROR] kubectl get nodes timed out", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("[ERROR] kubectl not found. Install kubectl first.", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"[ERROR] kubectl get nodes failed:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    nodes = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[5] != "<none>":
            nodes.append({"name": parts[0], "ip": parts[5]})

    if not nodes:
        print("[WARN] No nodes found in the cluster.", file=sys.stderr)
        sys.exit(0)

    return nodes


def filter_nodes(nodes: list[dict], pattern: str) -> list[dict]:
    """Filter nodes by name pattern (substring or regex)."""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        # Fall back to substring match
        return [n for n in nodes if pattern.lower() in n["name"].lower()]

    return [n for n in nodes if regex.search(n["name"])]


def ssh_exec(ip: str, remote_cmd: str, user: str, timeout: int,
             bastion: str | None = None) -> dict:
    """Execute a command on a remote node via SSH, optionally through a bastion."""
    ssh_opt_pairs = [
        ("StrictHostKeyChecking", "no"),
        ("UserKnownHostsFile", "/dev/null"),
        ("BatchMode", "yes"),
        ("ConnectTimeout", "10"),
        ("LogLevel", "ERROR"),
    ]
    ssh_opts = [arg for k, v in ssh_opt_pairs for arg in ("-o", f"{k}={v}")]
    ssh_opts_str = " ".join(f"-o {k}={v}" for k, v in ssh_opt_pairs)

    if bastion:
        # Nested SSH: agent-forward to bastion, then SSH to node
        # Quote remote_cmd so pipes/metacharacters survive both shell hops
        inner_ssh = (
            f"ssh {ssh_opts_str} {user}@{ip} -- {shlex.quote(remote_cmd)}"
        )
        cmd = ["ssh", "-A"] + ssh_opts + [f"{user}@{bastion}", "--", inner_ssh]
    else:
        cmd = ["ssh"] + ssh_opts + [f"{user}@{ip}", "--", remote_cmd]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "ip": ip,
            "stdout": result.stdout.replace("\r", ""),
            "stderr": result.stderr.replace("\r", ""),
            "rc": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ip": ip,
            "stdout": "",
            "stderr": f"[TIMEOUT] SSH timed out after {timeout}s",
            "rc": -1,
        }
    except OSError as e:
        return {
            "ip": ip,
            "stdout": "",
            "stderr": f"[EXCEPTION] {e}",
            "rc": -1,
        }


def kubectl_debug_exec(
    node_name: str,
    remote_cmd: str,
    kubeconfig_path: str,
    timeout: int,
    image: str = KUBECTL_DEBUG_IMAGE,
) -> dict:
    """Execute a command on a node via 'kubectl debug node' + chroot /host."""
    cmd = [
        "kubectl", "--kubeconfig", kubeconfig_path,
        "debug", f"node/{node_name}",
        "-it", "--quiet",
        f"--image={image}",
        "--", "chroot", "/host", "sh", "-c", remote_cmd,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "node": node_name,
            "stdout": result.stdout.replace("\r", ""),
            "stderr": result.stderr.replace("\r", ""),
            "rc": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "node": node_name,
            "stdout": "",
            "stderr": f"[TIMEOUT] kubectl debug timed out after {timeout}s",
            "rc": -1,
        }
    except OSError as e:
        return {
            "node": node_name,
            "stdout": "",
            "stderr": f"[EXCEPTION] {e}",
            "rc": -1,
        }


def cleanup_debug_pods(kubeconfig_path: str):
    """Remove leftover node-debugger pods created by kubectl debug."""
    try:
        result = subprocess.run(
            [
                "kubectl", "--kubeconfig", kubeconfig_path,
                "get", "pods", "--all-namespaces",
                "--no-headers", "-o",
                "custom-columns=NS:.metadata.namespace,NAME:.metadata.name",
            ],
            capture_output=True, text=True, timeout=30,
        )
        pods_to_delete: list[tuple[str, str]] = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) == 2 and "node-debugger-" in parts[1]:
                pods_to_delete.append((parts[0], parts[1]))

        for ns, pod in pods_to_delete:
            subprocess.run(
                [
                    "kubectl", "--kubeconfig", kubeconfig_path,
                    "delete", "pod", pod, "-n", ns,
                    "--force", "--grace-period=0",
                ],
                capture_output=True, text=True, timeout=30,
            )

        if pods_to_delete:
            print(f"[*] Cleaned up {len(pods_to_delete)} debug pod(s)")
    except Exception as e:
        print(f"[WARN] Debug pod cleanup failed: {e}", file=sys.stderr)


def print_results_text(nodes: list[dict], results: dict[str, dict]):
    """Print results in human-readable text format."""
    sep = "=" * 80

    for node in nodes:
        ip = node["ip"]
        name = node["name"]
        res = results.get(ip, {})

        print(sep)
        print(f"  Node: {name}  |  IP: {ip}  |  RC: {res.get('rc', '?')}")
        print(sep)

        stdout = res.get("stdout", "").rstrip()
        stderr = res.get("stderr", "").rstrip()

        if stdout:
            print(stdout)
        if stderr:
            print(f"[STDERR] {stderr}", file=sys.stderr)
        if not stdout and not stderr:
            print("  (no output)")

        print()


def print_results_json(
    nodes: list[dict], results: dict[str, dict], cluster: str, command_id: str
):
    """Print results in JSON format."""
    output = {
        "cluster": cluster,
        "command": command_id,
        "command_expanded": ALLOWED_COMMANDS.get(command_id, command_id),
        "node_count": len(nodes),
        "results": [],
    }

    for node in nodes:
        ip = node["ip"]
        res = results.get(ip, {})
        output["results"].append({
            "name": node["name"],
            "ip": ip,
            "rc": res.get("rc", -1),
            "stdout": res.get("stdout", "").rstrip(),
            "stderr": res.get("stderr", "").rstrip(),
        })

    failed = sum(1 for r in output["results"] if r["rc"] != 0)
    output["summary"] = {
        "total": len(nodes),
        "succeeded": len(nodes) - failed,
        "failed": failed,
    }

    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Run diagnostic commands on CaaS cluster nodes via SSH.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s my-cluster uptime\n"
            "  %(prog)s my-cluster df_root --node worker\n"
            "  %(prog)s my-cluster kubelet_status --format json\n"
            "  %(prog)s --list-commands"
        ),
    )
    parser.add_argument(
        "cluster_name", nargs="?",
        help="Cluster name (as registered in NetBox)",
    )
    parser.add_argument(
        "command_id", nargs="?",
        help="Command ID to run (use --list-commands to see available IDs)",
    )
    parser.add_argument(
        "--list-commands", action="store_true",
        help="List allowed command IDs and exit",
    )
    parser.add_argument(
        "--kubeconfig", metavar="PATH",
        help="Path to a local kubeconfig file (skips NetBox fetch)",
    )
    parser.add_argument(
        "--method", choices=["ssh", "kubectl-debug"], default="ssh",
        help="Execution method: ssh (default) or kubectl-debug (fallback)",
    )
    parser.add_argument(
        "--node", metavar="PATTERN",
        help="Filter nodes by name (substring or regex)",
    )
    parser.add_argument(
        "-u", "--user", default=SSH_USER,
        help=f"SSH user (default: {SSH_USER})",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=SSH_JOBS,
        help=f"Max parallel SSH connections (default: {SSH_JOBS})",
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=SSH_TIMEOUT,
        help=f"SSH timeout per connection in seconds (default: {SSH_TIMEOUT})",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.list_commands:
        print_allowed_commands()
        sys.exit(0)

    if not args.cluster_name:
        parser.error("cluster_name is required (use --list-commands to list commands)")
    if not args.command_id:
        parser.error("command_id is required (use --list-commands to list commands)")

    if args.command_id not in ALLOWED_COMMANDS:
        print(f"[ERROR] Unknown command ID: '{args.command_id}'", file=sys.stderr)
        print(f"[ERROR] Use --list-commands to see available IDs", file=sys.stderr)
        sys.exit(2)

    resolved_cmd = ALLOWED_COMMANDS[args.command_id]

    # 1. Get kubeconfig: use local file or fetch from NetBox
    if args.kubeconfig:
        kubeconfig = args.kubeconfig
        if not os.path.isfile(kubeconfig):
            print(f"[ERROR] Kubeconfig not found: {kubeconfig}", file=sys.stderr)
            sys.exit(1)
        print(f"[*] Using local kubeconfig: {kubeconfig}")
    else:
        kubeconfig = fetch_kubeconfig(args.cluster_name)

    # 2. Extract bastion (API server) for SSH ProxyJump (only needed for ssh method)
    bastion = None
    if args.method == "ssh":
        bastion = extract_bastion(kubeconfig)
        if bastion:
            print(f"[*] Bastion (API server): {bastion}")
        else:
            print("[WARN] Could not extract bastion from kubeconfig, trying direct SSH",
                  file=sys.stderr)

    # 3. Discover nodes
    print(f"[*] Discovering cluster nodes...")
    nodes = get_cluster_nodes(kubeconfig)

    if args.node:
        nodes = filter_nodes(nodes, args.node)
        if not nodes:
            print(f"[WARN] No nodes match pattern '{args.node}'", file=sys.stderr)
            sys.exit(0)

    print(f"[*] Found {len(nodes)} target(s):")
    for n in nodes:
        print(f"    {n['name']}  →  {n['ip']}")
    print()

    # 4. Run commands in parallel
    method_label = "kubectl debug" if args.method == "kubectl-debug" else "SSH"
    print(f"[*] Running '{args.command_id}' via {method_label} on {len(nodes)} node(s)...\n")

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        if args.method == "kubectl-debug":
            futures = {
                pool.submit(
                    kubectl_debug_exec, n["name"], resolved_cmd,
                    kubeconfig, args.timeout,
                ): n
                for n in nodes
            }
        else:
            futures = {
                pool.submit(
                    ssh_exec, n["ip"], resolved_cmd, args.user, args.timeout, bastion,
                ): n
                for n in nodes
            }
        for future in as_completed(futures):
            res = future.result()
            node_info = futures[future]
            results[node_info["ip"]] = res

    # 5. Print results
    if args.format == "json":
        print_results_json(nodes, results, args.cluster_name, args.command_id)
    else:
        print_results_text(nodes, results)

    # 6. Summary
    failed = sum(1 for r in results.values() if r["rc"] != 0)
    total = len(nodes)
    print(f"[*] Completed: {total - failed}/{total} succeeded, {failed}/{total} failed.")

    # 7. Clean up debug pods if kubectl-debug method was used
    if args.method == "kubectl-debug":
        cleanup_debug_pods(kubeconfig)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
