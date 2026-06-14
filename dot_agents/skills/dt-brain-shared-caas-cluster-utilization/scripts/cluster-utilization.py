#!/usr/bin/env python3
"""
Cluster worker CPU utilization by QoS pool.

On CaaS baremetal clusters with static CPU Manager policy, worker CPUs are
split into two pools:
  - Exclusive pool (isolcpus): Guaranteed QoS pods with integer CPU requests
  - Shared pool (reservedSystemCPUs): system services + Burstable + BestEffort
    + Guaranteed pods with fractional CPU requests

Pool sizes are auto-detected from node capacity vs allocatable.

Usage:
  cluster-utilization.py <cluster-name>
  cluster-utilization.py <cluster-name> --role caas_admin
  cluster-utilization.py --kubeconfig /path/to/kubeconfig
  cluster-utilization.py --kubeconfig /path/to/kubeconfig --format json
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# NetBox integration (optional — only when cluster name is provided)
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETBOX_SCRIPTS = os.path.join(SCRIPT_DIR, "..", "..", "cloud-netbox", "scripts")
VALID_ROLES = ["caas_admin", "caas_clab", "caas_oidc", "caas_sec", "caas_customer"]

WORKER_GROUP_LABEL = "caas.in.pan-net.eu/worker-group"


def _load_netbox():
    """Lazy-load NetBox utilities."""
    sys.path.insert(0, NETBOX_SCRIPTS)
    try:
        from netbox_common import get_netbox_client, get_api_token, NETBOX_URL
        return get_netbox_client, get_api_token, NETBOX_URL
    except ImportError as e:
        print(f"Error: Cannot import NetBox utilities: {e}", file=sys.stderr)
        print("Make sure you run from the project root with the venv active.", file=sys.stderr)
        sys.exit(1)


def fetch_kubeconfig(cluster_name: str, role: str) -> str:
    """Fetch kubeconfig from NetBox secrets API."""
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        print("Error: requests library not installed", file=sys.stderr)
        sys.exit(1)

    get_netbox_client, get_api_token, NETBOX_URL = _load_netbox()
    nb = get_netbox_client()
    token = get_api_token()

    try:
        clusters = list(nb.virtualization.clusters.filter(name=cluster_name))
    except Exception as e:
        print(f"Error: Failed to query NetBox: {e}", file=sys.stderr)
        sys.exit(1)

    if not clusters:
        print(f"Error: Cluster '{cluster_name}' not found in NetBox", file=sys.stderr)
        sys.exit(1)

    cluster = clusters[0]
    secrets_url = f"{NETBOX_URL}api/plugins/secrets/secrets/"
    headers = {"Authorization": f"Token {token}"}
    params = {"assigned_object_id": cluster.id, "role": role}

    try:
        resp = requests.get(secrets_url, headers=headers, params=params, verify=False, timeout=30)
        resp.raise_for_status()
        secrets = resp.json().get("results", [])
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to NetBox API (check VPN)", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code} fetching secrets", file=sys.stderr)
        sys.exit(1)

    if not secrets:
        print(f"Error: No kubeconfig found for '{cluster_name}' with role '{role}'", file=sys.stderr)
        sys.exit(1)

    plaintext = secrets[0].get("plaintext")
    if not plaintext:
        print("Error: Secret has no plaintext content", file=sys.stderr)
        sys.exit(1)

    try:
        return base64.b64decode(plaintext).decode("utf-8")
    except Exception:
        return plaintext


# ---------------------------------------------------------------------------
# kubectl helpers
# ---------------------------------------------------------------------------

def run_kubectl_json(kubeconfig_path: str, args: List[str]) -> dict:
    """Run a read-only kubectl command and return parsed JSON."""
    cmd = ["kubectl", "--kubeconfig", kubeconfig_path] + args + ["-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running kubectl {' '.join(args)}:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def detect_cpu_manager_policy(kubeconfig_path: str, worker_node: str) -> str:
    """Detect cpuManagerPolicy from kubelet's /configz endpoint on a worker node."""
    cmd = ["kubectl", "--kubeconfig", kubeconfig_path, "get", "--raw",
           f"/api/v1/nodes/{worker_node}/proxy/configz"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return "unknown"
    try:
        data = json.loads(result.stdout)
        return data.get("kubeletconfig", {}).get("cpuManagerPolicy", "none")
    except (json.JSONDecodeError, KeyError):
        return "unknown"


# ---------------------------------------------------------------------------
# CPU parsing and classification
# ---------------------------------------------------------------------------

def parse_cpu(val: Any) -> float:
    """Convert CPU value ('100m', '4', '2.5') to float cores."""
    if val is None:
        return 0.0
    val = str(val)
    if val.endswith("m"):
        return float(val[:-1]) / 1000.0
    return float(val)


def has_integer_cpu(val: Any) -> bool:
    """Check if a CPU value is an integer number of cores."""
    if val is None:
        return False
    val = str(val)
    if val.endswith("m"):
        return float(val[:-1]) % 1000 == 0 and float(val[:-1]) >= 1000
    f = float(val)
    return f == int(f) and f >= 1


def is_exclusive_pod(pod: dict) -> bool:
    """True if this Guaranteed pod gets exclusive CPUs from the CPU Manager.

    Requirements: QoS=Guaranteed, every container has integer CPU request >= 1.
    """
    if pod["status"].get("qosClass") != "Guaranteed":
        return False
    for c in pod["spec"].get("containers", []):
        cpu_req = c.get("resources", {}).get("requests", {}).get("cpu")
        if not has_integer_cpu(cpu_req):
            return False
    return True


# ---------------------------------------------------------------------------
# Node / pod data extraction
# ---------------------------------------------------------------------------

def get_worker_nodes(nodes_json: dict, policy_map: Optional[Dict[str, str]] = None) -> List[dict]:
    """Filter to worker nodes and extract relevant fields."""
    if policy_map is None:
        policy_map = {}
    workers = []
    for node in nodes_json.get("items", []):
        labels = node["metadata"].get("labels", {})
        if "node-role.kubernetes.io/worker" not in labels:
            continue
        name = node["metadata"]["name"]
        capacity = int(node["status"]["capacity"].get("cpu", 0))
        allocatable_raw = node["status"]["allocatable"].get("cpu", "0")
        allocatable = int(parse_cpu(allocatable_raw))
        worker_group = labels.get(WORKER_GROUP_LABEL, "default")
        node_policy = policy_map.get(name, "static")
        has_static = node_policy == "static"
        # With static CPU Manager: allocatable = exclusive pool (isolcpus),
        # capacity - allocatable = shared pool (reservedSystemCPUs).
        # Without static: all CPUs are shared, no exclusive pool.
        has_pinning = has_static and allocatable < capacity
        workers.append({
            "name": name,
            "worker_group": worker_group,
            "cpu_capacity": capacity,
            "cpu_allocatable": allocatable,
            "cpu_policy": node_policy,
            "cpu_pinning": has_pinning,
            "cpu_exclusive": allocatable if has_pinning else 0,
            "cpu_shared": (capacity - allocatable) if has_pinning else capacity,
        })
    return sorted(workers, key=lambda w: (w["worker_group"], w["name"]))


def classify_pods(pods_json: dict, worker_names: set, pinning_map: Optional[Dict[str, bool]] = None) -> Dict[str, Dict[str, Any]]:
    """Classify running pods on workers into exclusive/shared CPU pools.

    Returns per-node dict with:
      exclusive_cpu: float (sum of CPU requests from exclusive pods)
      shared_cpu: float (sum of CPU requests from shared-pool pods)
      exclusive_pods: list of (namespace/name, cpu)
      shared_pods: list of (namespace/name, cpu)
      qos_breakdown: {Guaranteed: {count, cpu}, Burstable: ..., BestEffort: ...}
    """
    if pinning_map is None:
        pinning_map = {n: True for n in worker_names}
    result = {n: {
        "exclusive_cpu": 0.0,
        "shared_cpu": 0.0,
        "exclusive_pods": [],
        "shared_pods": [],
        "guaranteed_exclusive": {"count": 0, "cpu_req": 0.0},
        "guaranteed_shared": {"count": 0, "cpu_req": 0.0},
        "qos_breakdown": defaultdict(lambda: {"count": 0, "cpu_req": 0.0}),
    } for n in worker_names}

    for pod in pods_json.get("items", []):
        phase = pod["status"].get("phase", "")
        if phase not in ("Running", "Pending"):
            continue
        node = pod["spec"].get("nodeName", "")
        if node not in worker_names:
            continue

        qos = pod["status"].get("qosClass", "Unknown")
        total_cpu = sum(
            parse_cpu(c.get("resources", {}).get("requests", {}).get("cpu"))
            for c in pod["spec"].get("containers", [])
        )
        pod_id = f"{pod['metadata']['namespace']}/{pod['metadata']['name']}"

        result[node]["qos_breakdown"][qos]["count"] += 1
        result[node]["qos_breakdown"][qos]["cpu_req"] += total_cpu

        if is_exclusive_pod(pod) and pinning_map.get(node, False):
            result[node]["exclusive_cpu"] += total_cpu
            result[node]["exclusive_pods"].append((pod_id, total_cpu))
            result[node]["guaranteed_exclusive"]["count"] += 1
            result[node]["guaranteed_exclusive"]["cpu_req"] += total_cpu
        else:
            result[node]["shared_cpu"] += total_cpu
            result[node]["shared_pods"].append((pod_id, total_cpu))
            if qos == "Guaranteed":
                result[node]["guaranteed_shared"]["count"] += 1
                result[node]["guaranteed_shared"]["cpu_req"] += total_cpu

    return result


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def pct(used: float, total: float) -> str:
    if total == 0:
        return "  N/A"
    return f"{used / total * 100:5.1f}%"


def format_text(workers: List[dict], pod_data: Dict[str, Dict], cluster_name: str) -> str:
    """Produce human-readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  Cluster Worker CPU Utilization")
    lines.append("=" * 60)
    lines.append(f"  Cluster:          {cluster_name}")
    lines.append(f"  Workers:          {len(workers)}")
    policies = sorted(set(w["cpu_policy"] for w in workers))
    lines.append(f"  CPU Manager:      {', '.join(policies)}")
    lines.append(f"  Date:             {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Group by worker_group
    groups: Dict[str, List[dict]] = defaultdict(list)
    for w in workers:
        groups[w["worker_group"]].append(w)

    cluster_excl_used = 0.0
    cluster_excl_cap = 0
    cluster_shared_used = 0.0
    cluster_shared_cap = 0

    for gname in sorted(groups):
        gnodes = groups[gname]
        lines.append("")
        lines.append("-" * 60)
        cap = gnodes[0]["cpu_capacity"]
        excl = gnodes[0]["cpu_exclusive"]
        shared = gnodes[0]["cpu_shared"]
        has_pinning = gnodes[0]["cpu_pinning"]
        group_policy = gnodes[0]["cpu_policy"]
        lines.append(f"  Worker Group: {gname}  ({len(gnodes)} nodes, cpuManagerPolicy={group_policy})")
        if has_pinning:
            lines.append(f"  Per-node: {cap} CPU total = {excl} exclusive + {shared} shared")
        else:
            lines.append(f"  Per-node: {cap} CPU total (all shared)")
        lines.append("")

        if has_pinning:
            # Exclusive pool
            lines.append("  Exclusive Pool (Guaranteed pods with integer CPU):")
            g_excl_used = 0.0
            g_excl_cap = 0
            for w in gnodes:
                pd = pod_data[w["name"]]
                used = pd["exclusive_cpu"]
                total = w["cpu_exclusive"]
                g_excl_used += used
                g_excl_cap += total
                lines.append(f"    {w['name']}: {used:6.0f} / {total} CPUs  ({pct(used, total)})")
            lines.append(f"    {'Group total':>{len(gnodes[0]['name'])}}: {g_excl_used:6.0f} / {g_excl_cap} CPUs  ({pct(g_excl_used, g_excl_cap)})")
            cluster_excl_used += g_excl_used
            cluster_excl_cap += g_excl_cap
            lines.append("")

        # Shared / all pool
        pool_label = "  Shared Pool (reservedSystemCPUs):" if has_pinning else "  CPU Allocation:"
        lines.append(pool_label)
        g_shared_used = 0.0
        g_shared_cap = 0
        for w in gnodes:
            pd = pod_data[w["name"]]
            used = pd["shared_cpu"]
            total = w["cpu_shared"]
            g_shared_used += used
            g_shared_cap += total
            lines.append(f"    {w['name']}: {used:6.1f} / {total} CPUs  ({pct(used, total)})")
        lines.append(f"    {'Group total':>{len(gnodes[0]['name'])}}: {g_shared_used:6.1f} / {g_shared_cap} CPUs  ({pct(g_shared_used, g_shared_cap)})")
        cluster_shared_used += g_shared_used
        cluster_shared_cap += g_shared_cap

        lines.append("")

        # QoS breakdown
        lines.append("  QoS Breakdown (pod count / CPU requests):")
        for w in gnodes:
            pd = pod_data[w["name"]]
            parts = []
            guar = pd["qos_breakdown"]["Guaranteed"]
            if guar["count"] > 0:
                ge = pd["guaranteed_exclusive"]
                gs = pd["guaranteed_shared"]
                if ge["count"] > 0 and gs["count"] > 0:
                    parts.append(f"Guar={guar['count']}pods/{guar['cpu_req']:.1f}cpu "
                                 f"[excl:{ge['count']}pods/{ge['cpu_req']:.0f}cpu, "
                                 f"frac:{gs['count']}pods/{gs['cpu_req']:.1f}cpu]")
                elif ge["count"] > 0:
                    parts.append(f"Guar={guar['count']}pods/{guar['cpu_req']:.0f}cpu (all exclusive)")
                else:
                    parts.append(f"Guar={guar['count']}pods/{guar['cpu_req']:.1f}cpu (all fractional)")
            for qos in ["Burstable", "BestEffort"]:
                d = pd["qos_breakdown"][qos]
                if d["count"] > 0:
                    parts.append(f"{qos[:4]}={d['count']}pods/{d['cpu_req']:.1f}cpu")
            lines.append(f"    {w['name']}: {', '.join(parts)}")

    # Cluster summary
    total_cap = cluster_excl_cap + cluster_shared_cap
    total_used = cluster_excl_used + cluster_shared_used
    any_pinning = cluster_excl_cap > 0
    lines.append("")
    lines.append("=" * 60)
    lines.append("  Cluster Summary")
    lines.append("=" * 60)
    lines.append(f"  {'Pool':<25} {'Allocated':>12} {'Capacity':>10} {'Util':>8}")
    lines.append(f"  {'-'*25} {'-'*12} {'-'*10} {'-'*8}")
    if any_pinning:
        lines.append(f"  {'Exclusive (Guaranteed)':<25} {cluster_excl_used:>10.0f}  {cluster_excl_cap:>8}   {pct(cluster_excl_used, cluster_excl_cap)}")
        lines.append(f"  {'Shared (reserved)':<25} {cluster_shared_used:>10.1f}  {cluster_shared_cap:>8}   {pct(cluster_shared_used, cluster_shared_cap)}")
    else:
        lines.append(f"  {'All CPUs (no pinning)':<25} {cluster_shared_used:>10.1f}  {cluster_shared_cap:>8}   {pct(cluster_shared_used, cluster_shared_cap)}")
    lines.append(f"  {'Overall':<25} {total_used:>10.1f}  {total_cap:>8}   {pct(total_used, total_cap)}")
    lines.append("")

    return "\n".join(lines)


def format_json_output(workers: List[dict], pod_data: Dict[str, Dict], cluster_name: str) -> str:
    """Produce JSON report."""
    groups: Dict[str, List[dict]] = defaultdict(list)
    for w in workers:
        groups[w["worker_group"]].append(w)

    policies = sorted(set(w["cpu_policy"] for w in workers))
    result = {
        "cluster": cluster_name,
        "timestamp": datetime.now().isoformat(),
        "cpu_manager_policies": policies,
        "worker_count": len(workers),
        "worker_groups": {},
        "summary": {},
    }

    total_excl_used = 0.0
    total_excl_cap = 0
    total_shared_used = 0.0
    total_shared_cap = 0

    for gname in sorted(groups):
        gnodes = groups[gname]
        g_data = {
            "node_count": len(gnodes),
            "per_node_capacity": gnodes[0]["cpu_capacity"],
            "per_node_exclusive": gnodes[0]["cpu_exclusive"],
            "per_node_shared": gnodes[0]["cpu_shared"],
            "nodes": {},
        }
        g_excl_used = 0.0
        g_shared_used = 0.0

        for w in gnodes:
            pd = pod_data[w["name"]]
            g_excl_used += pd["exclusive_cpu"]
            g_shared_used += pd["shared_cpu"]
            g_data["nodes"][w["name"]] = {
                "exclusive_allocated": pd["exclusive_cpu"],
                "exclusive_capacity": w["cpu_exclusive"],
                "shared_allocated": round(pd["shared_cpu"], 2),
                "shared_capacity": w["cpu_shared"],
                "exclusive_pods": [{"pod": p, "cpu": c} for p, c in pd["exclusive_pods"]],
                "shared_pods": [{"pod": p, "cpu": round(c, 2)} for p, c in pd["shared_pods"]],
                "qos_breakdown": {
                    qos: {"count": d["count"], "cpu_requests": round(d["cpu_req"], 2)}
                    for qos, d in pd["qos_breakdown"].items() if d["count"] > 0
                },
            }

        g_data["exclusive_allocated"] = g_excl_used
        g_data["exclusive_capacity"] = sum(w["cpu_exclusive"] for w in gnodes)
        g_data["shared_allocated"] = round(g_shared_used, 2)
        g_data["shared_capacity"] = sum(w["cpu_shared"] for w in gnodes)
        result["worker_groups"][gname] = g_data

        total_excl_used += g_excl_used
        total_excl_cap += g_data["exclusive_capacity"]
        total_shared_used += g_shared_used
        total_shared_cap += g_data["shared_capacity"]

    result["summary"] = {
        "exclusive_allocated": total_excl_used,
        "exclusive_capacity": total_excl_cap,
        "exclusive_utilization_pct": round(total_excl_used / total_excl_cap * 100, 1) if total_excl_cap else 0,
        "shared_allocated": round(total_shared_used, 2),
        "shared_capacity": total_shared_cap,
        "shared_utilization_pct": round(total_shared_used / total_shared_cap * 100, 1) if total_shared_cap else 0,
        "overall_allocated": round(total_excl_used + total_shared_used, 2),
        "overall_capacity": total_excl_cap + total_shared_cap,
        "overall_utilization_pct": round(
            (total_excl_used + total_shared_used) / (total_excl_cap + total_shared_cap) * 100, 1
        ) if (total_excl_cap + total_shared_cap) else 0,
    }

    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def analyze_cluster(kubeconfig_path: str, cluster_name: str) -> dict:
    """Run utilization analysis on a cluster and return structured result.

    This is the importable entry point for batch/parallel usage.
    Returns the same dict structure as --format json output (parsed).
    """
    nodes_json = run_kubectl_json(kubeconfig_path, ["get", "nodes"])

    # Detect CPU manager policy per worker group
    policy_map = {}
    group_probed = {}
    for node in nodes_json.get("items", []):
        labels = node["metadata"].get("labels", {})
        if "node-role.kubernetes.io/worker" not in labels:
            continue
        wg = labels.get(WORKER_GROUP_LABEL, "default")
        name = node["metadata"]["name"]
        if wg not in group_probed:
            group_probed[wg] = detect_cpu_manager_policy(kubeconfig_path, name)
        policy_map[name] = group_probed[wg]

    pods_json = run_kubectl_json(kubeconfig_path, ["get", "pods", "-A"])

    workers = get_worker_nodes(nodes_json, policy_map)
    if not workers:
        raise RuntimeError(f"No worker nodes found in {cluster_name}")

    worker_names = {w["name"] for w in workers}
    pinning_map = {w["name"]: w["cpu_pinning"] for w in workers}
    pod_data = classify_pods(pods_json, worker_names, pinning_map)

    return json.loads(format_json_output(workers, pod_data, cluster_name))


def main():
    parser = argparse.ArgumentParser(
        description="Calculate worker CPU utilization by QoS pool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-cluster
  %(prog)s my-cluster --role caas_admin
  %(prog)s --kubeconfig /path/to/kubeconfig
  %(prog)s --kubeconfig /path/to/kubeconfig --format json
""",
    )
    parser.add_argument("cluster", nargs="?", help="Cluster name in NetBox")
    parser.add_argument("--kubeconfig", help="Path to kubeconfig file (bypasses NetBox)")
    parser.add_argument("--role", choices=VALID_ROLES, default="caas_sec",
                        help="NetBox secret role (default: caas_sec)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")

    args = parser.parse_args()

    if not args.cluster and not args.kubeconfig:
        parser.error("Provide either a cluster name or --kubeconfig path")

    # Resolve kubeconfig
    kubeconfig_path = None
    temp_kubeconfig = None
    cluster_display = args.cluster or os.path.basename(args.kubeconfig)

    try:
        if args.kubeconfig:
            if not os.path.isfile(args.kubeconfig):
                print(f"Error: Kubeconfig not found: {args.kubeconfig}", file=sys.stderr)
                sys.exit(1)
            kubeconfig_path = args.kubeconfig
            print(f"Using kubeconfig: {args.kubeconfig}", file=sys.stderr)
        else:
            print(f"Fetching kubeconfig for '{args.cluster}' (role: {args.role}) from NetBox...",
                  file=sys.stderr)
            content = fetch_kubeconfig(args.cluster, args.role)
            fd, temp_kubeconfig = tempfile.mkstemp(prefix="cluster-util-", suffix=".kubeconfig")
            with os.fdopen(fd, "w") as f:
                f.write(content)
            os.chmod(temp_kubeconfig, 0o600)
            kubeconfig_path = temp_kubeconfig
            print("Kubeconfig fetched.", file=sys.stderr)

        # Fetch data (read-only)
        print("Fetching nodes...", file=sys.stderr)
        nodes_json = run_kubectl_json(kubeconfig_path, ["get", "nodes"])

        # Detect CPU manager policy per worker group
        policy_map = {}
        group_probed = {}
        worker_count = 0
        for node in nodes_json.get("items", []):
            labels = node["metadata"].get("labels", {})
            if "node-role.kubernetes.io/worker" not in labels:
                continue
            worker_count += 1
            wg = labels.get(WORKER_GROUP_LABEL, "default")
            name = node["metadata"]["name"]
            if wg not in group_probed:
                policy = detect_cpu_manager_policy(kubeconfig_path, name)
                group_probed[wg] = policy
                print(f"  {wg}: cpuManagerPolicy={policy} (via {name})", file=sys.stderr)
            policy_map[name] = group_probed[wg]

        if worker_count > 0:
            print(f"Detected CPU Manager policy ({worker_count} workers, {len(group_probed)} groups)", file=sys.stderr)

        print("Fetching pods...", file=sys.stderr)
        pods_json = run_kubectl_json(kubeconfig_path, ["get", "pods", "-A"])

        # Process
        workers = get_worker_nodes(nodes_json, policy_map)
        if not workers:
            print("Error: No worker nodes found", file=sys.stderr)
            sys.exit(1)

        worker_names = {w["name"] for w in workers}
        pinning_map = {w["name"]: w["cpu_pinning"] for w in workers}
        pod_data = classify_pods(pods_json, worker_names, pinning_map)

        # Output
        if args.format == "json":
            print(format_json_output(workers, pod_data, cluster_display))
        else:
            print(format_text(workers, pod_data, cluster_display))

    finally:
        if temp_kubeconfig:
            try:
                os.unlink(temp_kubeconfig)
            except OSError:
                pass


if __name__ == "__main__":
    main()
