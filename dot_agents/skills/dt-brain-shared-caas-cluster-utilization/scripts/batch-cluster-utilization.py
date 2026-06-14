#!/usr/bin/env python3
"""
Batch parallel cluster CPU utilization analysis.

Auto-discovers active baremetal CaaS clusters from NetBox and runs
utilization analysis in parallel, saving results to local files.

Usage:
  batch-cluster-utilization.py [options]

Output:
  reports/cluster-utilization/<timestamp>/
  ├── summary.json          # Combined results + aggregate stats
  ├── cluster-abc.json      # Per-cluster detail
  └── ...
"""

import argparse
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
NETBOX_SCRIPTS = os.path.join(SCRIPT_DIR, "..", "..", "cloud-netbox", "scripts")

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, NETBOX_SCRIPTS)

from netbox_common import get_netbox_client, get_api_token, NETBOX_URL, COUNTRY_MAPPING

VALID_ROLES = ["caas_admin", "caas_clab", "caas_oidc", "caas_sec", "caas_customer"]


# ---------------------------------------------------------------------------
# NetBox cluster discovery
# ---------------------------------------------------------------------------

def discover_baremetal_clusters(
    nb: Any,
    site: Optional[str] = None,
    status: str = "active",
) -> List[Dict[str, str]]:
    """Query NetBox for active baremetal CaaS clusters."""
    filters: Dict[str, Any] = {}

    # CaaS group
    groups = list(nb.virtualization.cluster_groups.filter(name="CaaS"))
    if not groups:
        print("Error: Cluster group 'CaaS' not found in NetBox", file=sys.stderr)
        sys.exit(1)
    filters["group_id"] = groups[0].id

    # Baremetal type
    types = list(nb.virtualization.cluster_types.filter(name="baremetal"))
    if not types:
        print("Error: Cluster type 'baremetal' not found in NetBox", file=sys.stderr)
        sys.exit(1)
    filters["type_id"] = types[0].id

    if status:
        filters["status"] = status

    # Optional site/country filter
    if site:
        site_upper = site.upper()
        country_code = COUNTRY_MAPPING.get(site_upper)
        if country_code:
            all_sites = nb.dcim.sites.all()
            country_sites = [s for s in all_sites if s.name and s.name.startswith(country_code)]
            if country_sites:
                filters["site_id"] = [s.id for s in country_sites]
            else:
                print(f"Warning: No sites found for country '{site}'", file=sys.stderr)
                return []
        else:
            sites = list(nb.dcim.sites.filter(name=site))
            if sites:
                filters["site_id"] = sites[0].id
            else:
                print(f"Warning: Site '{site}' not found", file=sys.stderr)
                return []

    clusters = nb.virtualization.clusters.filter(**filters)
    return [
        {
            "name": c.name,
            "site": c.site.name if c.site else "unknown",
            "id": c.id,
        }
        for c in clusters
    ]


# ---------------------------------------------------------------------------
# Per-cluster analysis (runs in thread)
# ---------------------------------------------------------------------------

def analyze_single_cluster(
    cluster_name: str,
    role: str,
    timeout: int,
) -> Dict[str, Any]:
    """Fetch kubeconfig and run utilization analysis for one cluster.

    Returns dict with 'status', 'data' or 'error', and 'duration_s'.
    """
    # Import from the sibling script (filename has hyphens, use importlib)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cluster_utilization",
        os.path.join(SCRIPT_DIR, "cluster-utilization.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fetch_kubeconfig = mod.fetch_kubeconfig
    analyze_cluster = mod.analyze_cluster

    start = time.monotonic()
    temp_kubeconfig = None

    try:
        content = fetch_kubeconfig(cluster_name, role)
        fd, temp_kubeconfig = tempfile.mkstemp(
            prefix=f"batch-util-{cluster_name}-", suffix=".kubeconfig"
        )
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.chmod(temp_kubeconfig, 0o600)

        result = analyze_cluster(temp_kubeconfig, cluster_name)
        duration = round(time.monotonic() - start, 1)
        return {"status": "ok", "data": result, "duration_s": duration}

    except SystemExit:
        duration = round(time.monotonic() - start, 1)
        return {"status": "error", "error": "Script exited (kubeconfig or kubectl failure)", "duration_s": duration}
    except Exception as e:
        duration = round(time.monotonic() - start, 1)
        return {"status": "error", "error": str(e), "duration_s": duration}
    finally:
        if temp_kubeconfig:
            try:
                os.unlink(temp_kubeconfig)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Aggregate stats
# ---------------------------------------------------------------------------

def compute_aggregate(results: Dict[str, Dict]) -> Dict[str, Any]:
    """Compute cross-cluster aggregate utilization stats."""
    total_workers = 0
    total_excl_cap = 0
    total_excl_alloc = 0.0
    total_shared_cap = 0
    total_shared_alloc = 0.0

    for name, entry in results.items():
        if entry["status"] != "ok":
            continue
        summary = entry["data"].get("summary", {})
        total_workers += entry["data"].get("worker_count", 0)
        total_excl_cap += summary.get("exclusive_capacity", 0)
        total_excl_alloc += summary.get("exclusive_allocated", 0)
        total_shared_cap += summary.get("shared_capacity", 0)
        total_shared_alloc += summary.get("shared_allocated", 0)

    overall_cap = total_excl_cap + total_shared_cap
    overall_alloc = total_excl_alloc + total_shared_alloc

    return {
        "total_workers": total_workers,
        "exclusive_capacity": total_excl_cap,
        "exclusive_allocated": round(total_excl_alloc, 2),
        "exclusive_utilization_pct": round(total_excl_alloc / total_excl_cap * 100, 1) if total_excl_cap else 0,
        "shared_capacity": total_shared_cap,
        "shared_allocated": round(total_shared_alloc, 2),
        "shared_utilization_pct": round(total_shared_alloc / total_shared_cap * 100, 1) if total_shared_cap else 0,
        "overall_capacity": overall_cap,
        "overall_allocated": round(overall_alloc, 2),
        "overall_utilization_pct": round(overall_alloc / overall_cap * 100, 1) if overall_cap else 0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Batch parallel cluster CPU utilization analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         # All active baremetal CaaS clusters
  %(prog)s --site SK               # Only Slovakia clusters
  %(prog)s --workers 10            # 10 parallel threads
  %(prog)s --timeout 180           # 3 min per-cluster timeout
  %(prog)s --output-dir /tmp/util  # Custom output directory
""",
    )
    parser.add_argument("--workers", type=int, default=5,
                        help="Max parallel cluster queries (default: 5)")
    parser.add_argument("--role", choices=VALID_ROLES, default="caas_sec",
                        help="NetBox secret role (default: caas_sec)")
    parser.add_argument("--site",
                        help="Filter clusters by site/country (e.g., SK, AT, HR)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Per-cluster timeout in seconds (default: 120)")
    parser.add_argument("--output-dir",
                        help="Override output directory (default: reports/cluster-utilization/<timestamp>)")

    args = parser.parse_args()

    # Discover clusters
    print("Connecting to NetBox...", file=sys.stderr)
    nb = get_netbox_client()

    print("Discovering active baremetal CaaS clusters...", file=sys.stderr)
    clusters = discover_baremetal_clusters(nb, site=args.site)

    if not clusters:
        print("No clusters found matching filters.", file=sys.stderr)
        sys.exit(1)

    cluster_names = sorted(c["name"] for c in clusters)
    print(f"Found {len(cluster_names)} clusters to analyze", file=sys.stderr)
    for name in cluster_names:
        print(f"  • {name}", file=sys.stderr)
    print(file=sys.stderr)

    # Prepare output directory
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(PROJECT_ROOT, "reports", "cluster-utilization", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Run in parallel
    results: Dict[str, Dict] = {}
    total = len(cluster_names)
    completed = 0
    ok_count = 0
    fail_count = 0
    start_time = time.monotonic()

    print(f"Starting analysis with {args.workers} workers...", file=sys.stderr)
    print(file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(analyze_single_cluster, name, args.role, args.timeout): name
            for name in cluster_names
        }

        for future in as_completed(futures):
            name = futures[future]
            completed += 1

            try:
                result = future.result(timeout=args.timeout)
            except Exception as e:
                result = {"status": "error", "error": str(e), "duration_s": 0}

            results[name] = result

            if result["status"] == "ok":
                ok_count += 1
                summary = result["data"].get("summary", {})
                util_pct = summary.get("overall_utilization_pct", "?")
                workers = result["data"].get("worker_count", "?")
                print(
                    f"  [{completed}/{total}] ✓ {name:<40} "
                    f"{workers} workers  {util_pct}% util  ({result['duration_s']}s)",
                    file=sys.stderr,
                )

                # Write individual cluster file
                cluster_file = os.path.join(output_dir, f"{name}.json")
                with open(cluster_file, "w") as f:
                    json.dump(result["data"], f, indent=2)
            else:
                fail_count += 1
                print(
                    f"  [{completed}/{total}] ✗ {name:<40} "
                    f"ERROR: {result.get('error', 'unknown')}  ({result['duration_s']}s)",
                    file=sys.stderr,
                )

    total_duration = round(time.monotonic() - start_time, 1)

    # Build combined summary
    aggregate = compute_aggregate(results)
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "total_clusters": total,
        "successful": ok_count,
        "failed": fail_count,
        "duration_s": total_duration,
        "workers_flag": args.workers,
        "role": args.role,
        "site_filter": args.site,
        "clusters": {
            name: {
                "status": r["status"],
                "duration_s": r["duration_s"],
                **({"summary": r["data"]["summary"]} if r["status"] == "ok" else {}),
                **({"worker_count": r["data"]["worker_count"]} if r["status"] == "ok" else {}),
                **({"error": r["error"]} if r["status"] == "error" else {}),
            }
            for name, r in sorted(results.items())
        },
        "aggregate": aggregate,
    }

    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)

    # Final report
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"  Batch Analysis Complete", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"  Clusters:    {ok_count} ok / {fail_count} failed / {total} total", file=sys.stderr)
    print(f"  Duration:    {total_duration}s", file=sys.stderr)
    print(f"  Workers:     {aggregate['total_workers']}", file=sys.stderr)
    print(f"  Exclusive:   {aggregate['exclusive_allocated']:.0f} / {aggregate['exclusive_capacity']} CPUs  "
          f"({aggregate['exclusive_utilization_pct']}%)", file=sys.stderr)
    print(f"  Shared:      {aggregate['shared_allocated']:.1f} / {aggregate['shared_capacity']} CPUs  "
          f"({aggregate['shared_utilization_pct']}%)", file=sys.stderr)
    print(f"  Overall:     {aggregate['overall_allocated']:.1f} / {aggregate['overall_capacity']} CPUs  "
          f"({aggregate['overall_utilization_pct']}%)", file=sys.stderr)
    print(f"  Output:      {output_dir}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Also print summary JSON to stdout for piping
    print(json.dumps(summary_data, indent=2))


if __name__ == "__main__":
    main()
