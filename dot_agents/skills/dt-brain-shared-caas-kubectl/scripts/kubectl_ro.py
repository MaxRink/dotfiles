#!/usr/bin/env python3
"""
Read-only kubectl wrapper for CaaS cluster troubleshooting.
Fetches kubeconfig from NetBox and enforces read-only operations.

Usage:
  kubectl_ro.py <cluster-name> get pods -A
  kubectl_ro.py <cluster-name> describe pod <name> -n kube-system
  kubectl_ro.py <cluster-name> top nodes
  kubectl_ro.py <cluster-name> logs <pod> -n <ns> --tail=100
  kubectl_ro.py <cluster-name> --role caas_admin get nodes
  kubectl_ro.py <cluster-name> --kubeconfig /path/to/kubeconfig get pods
"""

import os
import sys
import subprocess
import tempfile
import argparse
import base64
from typing import List, Optional

# Reuse shared NetBox utilities from cloud-netbox skill
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
NETBOX_SCRIPTS = os.path.join(SKILL_DIR, "..", "..", "cloud-netbox", "scripts")
sys.path.insert(0, NETBOX_SCRIPTS)

from netbox_common import get_netbox_client, get_api_token, NETBOX_URL

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    sys.exit(1)

SECRETS_API = f"{NETBOX_URL}api/plugins/secrets/secrets/"

# --- Read-only allowlist ---
# Only these kubectl subcommands are permitted.
ALLOWED_SUBCOMMANDS = frozenset({
    "get",
    "describe",
    "top",
    "logs",
    "log",
    "explain",
    "api-resources",
    "api-versions",
    "cluster-info",
    "version",
    "events",
    "config",
    "auth",
    "wait",
})

# Block these flag prefixes (prefix match catches --dry-run=server, --raw=/api/...)
BLOCKED_FLAG_PREFIXES = (
    "--dry-run",
    "--raw",
)

# auth sub-subcommands: only "can-i" and "whoami" allowed
ALLOWED_AUTH_SUBCOMMANDS = frozenset({"can-i", "whoami"})

# config sub-subcommands: only read-only ones
ALLOWED_CONFIG_SUBCOMMANDS = frozenset({"view", "get-contexts", "current-context", "get-clusters", "get-users"})

VALID_ROLES = ["caas_admin", "caas_clab", "caas_oidc", "caas_sec", "caas_customer"]


def validate_readonly(kubectl_args: List[str]) -> None:
    """Validate that kubectl arguments are read-only operations only."""
    if not kubectl_args:
        print("Error: No kubectl arguments provided", file=sys.stderr)
        print("Usage: kubectl_ro.py <cluster> <kubectl-subcommand> [args...]", file=sys.stderr)
        sys.exit(1)

    subcommand = kubectl_args[0]

    if subcommand.startswith("-"):
        # Global flags like --version, --help are OK
        if subcommand in ("--version", "--help", "-h"):
            return
        print(f"Error: Unrecognized flag '{subcommand}' before subcommand", file=sys.stderr)
        sys.exit(1)

    if subcommand not in ALLOWED_SUBCOMMANDS:
        print(f"Error: '{subcommand}' is not a read-only command", file=sys.stderr)
        print(f"Allowed commands: {', '.join(sorted(ALLOWED_SUBCOMMANDS))}", file=sys.stderr)
        sys.exit(1)

    # Validate auth sub-subcommands
    if subcommand == "auth" and len(kubectl_args) > 1:
        sub_sub = kubectl_args[1]
        if sub_sub not in ALLOWED_AUTH_SUBCOMMANDS:
            print(f"Error: 'auth {sub_sub}' is not allowed (only: {', '.join(sorted(ALLOWED_AUTH_SUBCOMMANDS))})", file=sys.stderr)
            sys.exit(1)

    # Validate config sub-subcommands
    if subcommand == "config" and len(kubectl_args) > 1:
        sub_sub = kubectl_args[1]
        if sub_sub not in ALLOWED_CONFIG_SUBCOMMANDS:
            print(f"Error: 'config {sub_sub}' is not allowed (only: {', '.join(sorted(ALLOWED_CONFIG_SUBCOMMANDS))})", file=sys.stderr)
            sys.exit(1)

    # Check for blocked flags (prefix match)
    for arg in kubectl_args:
        for prefix in BLOCKED_FLAG_PREFIXES:
            if arg.startswith(prefix):
                print(f"Error: Flag '{arg}' is not allowed in read-only mode", file=sys.stderr)
                sys.exit(1)


def fetch_kubeconfig(cluster_name: str, role: str) -> str:
    """Fetch kubeconfig from NetBox using shared cloud-netbox utilities."""
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

    # Fetch secrets
    headers = {"Authorization": f"Token {token}"}
    params = {"assigned_object_id": cluster.id, "role": role}

    try:
        resp = requests.get(SECRETS_API, headers=headers, params=params, verify=False, timeout=30)
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
        print(f"Available roles: {', '.join(VALID_ROLES)}", file=sys.stderr)
        sys.exit(1)

    plaintext = secrets[0].get("plaintext")
    if not plaintext:
        print("Error: Secret has no plaintext content", file=sys.stderr)
        sys.exit(1)

    try:
        return base64.b64decode(plaintext).decode("utf-8")
    except Exception:
        return plaintext


def run_kubectl(kubeconfig_content: str, kubectl_args: List[str]) -> int:
    """Run kubectl with a temporary kubeconfig file. Returns exit code."""
    fd, tmppath = tempfile.mkstemp(prefix="kubectl-ro-", suffix=".kubeconfig")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(kubeconfig_content)
        os.chmod(tmppath, 0o600)

        env = os.environ.copy()
        env["KUBECONFIG"] = tmppath

        result = subprocess.run(
            ["kubectl"] + kubectl_args,
            env=env,
        )
        return result.returncode
    finally:
        try:
            os.unlink(tmppath)
        except OSError:
            pass


def main():
    # Split args: everything before first kubectl subcommand is ours
    # Pattern: kubectl_ro.py <cluster> [--role X] [--kubeconfig Y] <kubectl-args...>
    parser = argparse.ArgumentParser(
        description="Read-only kubectl wrapper for CaaS clusters",
        usage="%(prog)s <cluster> [options] <kubectl-subcommand> [kubectl-args...]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Allowed read-only commands:
  get, describe, top, logs, explain, api-resources, api-versions,
  cluster-info, version, events, auth can-i, auth whoami

Examples:
  %(prog)s mycluster get pods -A
  %(prog)s mycluster describe pod my-pod -n kube-system
  %(prog)s mycluster top nodes
  %(prog)s mycluster logs my-pod -n kube-system --tail=100
  %(prog)s mycluster get events -n kube-system --sort-by='.lastTimestamp'
  %(prog)s mycluster --role caas_admin get nodes -o wide
""",
    )
    parser.add_argument("cluster", help="Cluster name (as registered in NetBox)")
    parser.add_argument("--role", choices=VALID_ROLES, default="caas_sec",
                        help="NetBox secret role (default: caas_sec)")
    parser.add_argument("--kubeconfig", dest="kubeconfig_path",
                        help="Use existing kubeconfig file instead of fetching from NetBox")

    # Parse only known args; everything else is kubectl args
    args, kubectl_args = parser.parse_known_args()

    if not kubectl_args:
        parser.print_help()
        sys.exit(1)

    # Validate read-only
    validate_readonly(kubectl_args)

    # Get kubeconfig
    if args.kubeconfig_path:
        if not os.path.isfile(args.kubeconfig_path):
            print(f"Error: Kubeconfig file not found: {args.kubeconfig_path}", file=sys.stderr)
            sys.exit(1)
        with open(args.kubeconfig_path) as f:
            kubeconfig_content = f.read()
        print(f"Using kubeconfig: {args.kubeconfig_path}", file=sys.stderr)
    else:
        print(f"Fetching kubeconfig for '{args.cluster}' (role: {args.role}) from NetBox...", file=sys.stderr)
        kubeconfig_content = fetch_kubeconfig(args.cluster, args.role)
        print(f"Running: kubectl {' '.join(kubectl_args)}", file=sys.stderr)

    exit_code = run_kubectl(kubeconfig_content, kubectl_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
