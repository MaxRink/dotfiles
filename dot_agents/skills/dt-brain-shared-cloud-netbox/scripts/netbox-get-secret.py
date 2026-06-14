#!/usr/bin/env python3
"""
NetBox Get Secret Script
Retrieves kubeconfigs and other secrets from the NetBox secrets plugin API.

Usage: netbox-get-secret.py <cluster-name-or-id> [options]
"""

import os
import sys
import json
import base64
import argparse
from typing import Any, Dict, List, Optional

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

from netbox_common import get_netbox_client, get_api_token, NETBOX_URL


SECRETS_API = f"{NETBOX_URL}api/plugins/secrets/secrets/"

VALID_ROLES = [
    "caas_admin",
    "caas_clab",
    "caas_oidc",
    "caas_sec",
    "caas_customer",
]


def resolve_cluster(nb, identifier: str, use_id: bool = False, use_name: bool = False) -> Any:
    """Resolve cluster name or ID to a cluster object"""
    if use_id or identifier.isdigit():
        try:
            cluster = nb.virtualization.clusters.get(int(identifier))
            if not cluster:
                print(f"Error: Cluster with ID {identifier} not found", file=sys.stderr)
                sys.exit(1)
            return cluster
        except Exception as e:
            print(f"Error: Failed to get cluster by ID: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            clusters = list(nb.virtualization.clusters.filter(name=identifier))
            if not clusters:
                print(f"Error: Cluster with name '{identifier}' not found", file=sys.stderr)
                sys.exit(1)
            if len(clusters) > 1:
                print(f"Warning: Multiple clusters found with name '{identifier}', using first one", file=sys.stderr)
            return clusters[0]
        except Exception as e:
            print(f"Error: Failed to get cluster by name: {e}", file=sys.stderr)
            sys.exit(1)


def get_secrets(token: str, cluster_id: int, role: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch secrets from the NetBox secrets plugin API"""
    headers = {"Authorization": f"Token {token}"}
    params: Optional[Dict[str, Any]] = {"assigned_object_id": cluster_id}
    if role:
        params["role"] = role

    all_secrets = []
    url = SECRETS_API

    try:
        while url:
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            all_secrets.extend(data.get("results", []))
            url = data.get("next")
            # Only pass params on the first request; "next" URL includes them
            params = None
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to NetBox API", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Error: Invalid or expired API token (HTTP 401)", file=sys.stderr)
        elif e.response.status_code == 403:
            print("Error: Insufficient permissions (HTTP 403)", file=sys.stderr)
        elif e.response.status_code == 404:
            print("Error: Secrets plugin not available (HTTP 404)", file=sys.stderr)
            print("The NetBox instance may not have the secrets plugin installed", file=sys.stderr)
        else:
            print(f"Error: HTTP {e.response.status_code}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to fetch secrets: {e}", file=sys.stderr)
        sys.exit(1)

    return all_secrets


def decode_plaintext(secret: Dict[str, Any]) -> Optional[str]:
    """Decode the base64-encoded plaintext from a secret"""
    plaintext = secret.get("plaintext")
    if not plaintext:
        return None
    try:
        return base64.b64decode(plaintext).decode("utf-8")
    except Exception:
        # May already be plain text, not base64
        return plaintext


def format_list(secrets: List[Dict[str, Any]], cluster_name: str):
    """List available secrets without showing plaintext"""
    print("=" * 80)
    print(f"Secrets for cluster: {cluster_name}")
    print("=" * 80)
    print()

    if not secrets:
        print("  No secrets found for this cluster")
        return

    print(f"  {'Name':<50} {'Role':<20}")
    print("  " + "-" * 70)
    for secret in secrets:
        name = secret.get("name", "-")
        role = secret.get("role", {})
        role_name = role.get("display", role.get("name", "-")) if isinstance(role, dict) else str(role)
        print(f"  {name:<50} {role_name:<20}")

    print()
    print(f"  Total: {len(secrets)} secret(s)")
    print()


def format_detailed(secrets: List[Dict[str, Any]], cluster_name: str):
    """Format secrets with full details"""
    print("=" * 80)
    print(f"Secrets for cluster: {cluster_name}")
    print("=" * 80)
    print()

    if not secrets:
        print("  No secrets found for this cluster")
        return

    for i, secret in enumerate(secrets):
        if i > 0:
            print("-" * 80)
            print()

        name = secret.get("name", "-")
        role = secret.get("role", {})
        role_name = role.get("display", role.get("name", "-")) if isinstance(role, dict) else str(role)
        role_slug = role.get("slug", "-") if isinstance(role, dict) else "-"
        secret_id = secret.get("id", "-")

        print(f"  Name:      {name}")
        print(f"  ID:        {secret_id}")
        print(f"  Role:      {role_name} ({role_slug})")
        print()

        decoded = decode_plaintext(secret)
        if decoded:
            print("  Content:")
            print("  " + "-" * 40)
            for line in decoded.splitlines():
                print(f"  {line}")
            print()
        else:
            print("  Content:   (no plaintext available)")
            print()

    print(f"  Total: {len(secrets)} secret(s)")
    print()


def format_json(secrets: List[Dict[str, Any]], cluster_name: str):
    """Format secrets as JSON"""
    output = []
    for secret in secrets:
        entry = {
            "id": secret.get("id"),
            "name": secret.get("name"),
            "role": secret.get("role", {}).get("slug") if isinstance(secret.get("role"), dict) else secret.get("role"),
            "role_display": secret.get("role", {}).get("display") if isinstance(secret.get("role"), dict) else None,
        }
        decoded = decode_plaintext(secret)
        if decoded:
            entry["plaintext_decoded"] = decoded
        output.append(entry)
    print(json.dumps({"cluster": cluster_name, "secrets": output, "count": len(output)}, indent=2))


def format_plain(secrets: List[Dict[str, Any]]):
    """Output raw decoded plaintext only (for piping)"""
    for secret in secrets:
        decoded = decode_plaintext(secret)
        if decoded:
            print(decoded)


def save_secret(secret: Dict[str, Any], cluster_name: str, path: Optional[str] = None):
    """Save a secret's decoded plaintext to a file"""
    decoded = decode_plaintext(secret)
    if not decoded:
        print(f"Warning: Secret '{secret.get('name')}' has no plaintext to save", file=sys.stderr)
        return None

    if path:
        filepath = path
    else:
        role = secret.get("role", {})
        role_slug = role.get("slug", "unknown") if isinstance(role, dict) else "unknown"
        filepath = f"{cluster_name}-{role_slug}-kubeconfig"

    with open(filepath, "w") as f:
        f.write(decoded)

    os.chmod(filepath, 0o600)
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Get secrets (kubeconfigs) from NetBox for a cluster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Secret Roles:
  caas_admin      Kubeconfig for CaaS admins (default)
  caas_clab       Kubeconfig for clab automation
  caas_oidc       Kubeconfig for OIDC users
  caas_sec        Kubeconfig for Security
  caas_customer   Kubeconfig for customers

Examples:
  # List all secrets for a cluster
  %(prog)s hudpxc1-5gc-prod --list

  # Get admin kubeconfig (default role)
  %(prog)s hudpxc1-5gc-prod

  # Get specific role kubeconfig
  %(prog)s hudpxc1-5gc-prod --role caas_oidc

  # Get raw kubeconfig for piping
  %(prog)s hudpxc1-5gc-prod --format plain > kubeconfig.yaml

  # Save kubeconfig to auto-named file
  %(prog)s hudpxc1-5gc-prod --save

  # Save kubeconfig to specific file
  %(prog)s hudpxc1-5gc-prod --save-to /tmp/kubeconfig.yaml

  # Get JSON output
  %(prog)s hudpxc1-5gc-prod --format json
        """,
    )

    parser.add_argument("cluster", help="Cluster name or ID")
    parser.add_argument(
        "--role",
        choices=VALID_ROLES,
        default="caas_admin",
        help="Secret role to retrieve (default: caas_admin)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_secrets",
        help="List available secrets for the cluster (no plaintext)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save kubeconfig to auto-named file (<cluster>-<role>-kubeconfig)",
    )
    parser.add_argument(
        "--save-to",
        metavar="PATH",
        help="Save kubeconfig to specific file path",
    )
    parser.add_argument(
        "--format",
        choices=["detailed", "json", "plain"],
        default="detailed",
        help="Output format (default: detailed)",
    )
    parser.add_argument(
        "--id",
        action="store_true",
        dest="use_id",
        help="Treat argument as cluster ID (faster)",
    )
    parser.add_argument(
        "--name",
        action="store_true",
        dest="use_name",
        help="Treat argument as cluster name",
    )

    args = parser.parse_args()

    # Initialize NetBox client and resolve cluster
    nb = get_netbox_client()
    cluster = resolve_cluster(nb, args.cluster, use_id=args.use_id, use_name=args.use_name)
    token = get_api_token()

    # List mode: show all secrets without role filter
    if args.list_secrets:
        secrets = get_secrets(token, cluster.id, role=None)
        format_list(secrets, cluster.name)
        return

    # Fetch secrets filtered by role
    secrets = get_secrets(token, cluster.id, role=args.role)

    if not secrets:
        print(f"No secrets found for cluster '{cluster.name}' with role '{args.role}'", file=sys.stderr)
        sys.exit(1)

    # Save mode
    if args.save or args.save_to:
        for secret in secrets:
            filepath = save_secret(secret, cluster.name, path=args.save_to)
            if filepath:
                print(f"Saved: {filepath}")
                print(f"  Secret: {secret.get('name')}")
                print(f"  Permissions: 600 (owner read/write only)")
        return

    # Output mode
    if args.format == "json":
        format_json(secrets, cluster.name)
    elif args.format == "plain":
        format_plain(secrets)
    else:
        format_detailed(secrets, cluster.name)


if __name__ == "__main__":
    main()
