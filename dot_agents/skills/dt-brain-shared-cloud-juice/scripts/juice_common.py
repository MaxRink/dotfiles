#!/usr/bin/env python3
"""
JUICE Common Module
Shared utilities for JUICE API scripts — authentication, request helpers, output formatting.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


JUICE_ENVS = {
    "prod": "https://prod.juice.in.pan-net.eu",
    "stage": "https://stage.juice.in.pan-net.eu",
}

# Module-level token cache: keyed by (env, juice_group)
_token_cache: dict[tuple[str, str], str] = {}


def get_credentials() -> tuple[str, str]:
    """Get JUICE username and password from environment variables."""
    username = os.environ.get("JUICE_USERNAME")
    password = os.environ.get("JUICE_PASSWORD")
    if not username or not password:
        print(
            "Error: JUICE_USERNAME and JUICE_PASSWORD environment variables must be set",
            file=sys.stderr,
        )
        sys.exit(1)
    return username, password


def get_default_group() -> Optional[str]:
    """Get default JUICE group from JUICE_GROUP env var."""
    return os.environ.get("JUICE_GROUP")


def get_verify() -> str | bool:
    """Get SSL verification setting.

    If JUICE_CACERT is set, returns the expanded path to the CA certificate file.
    Otherwise returns False (insecure, with warnings suppressed).
    """
    cacert = os.environ.get("JUICE_CACERT")
    if cacert:
        cert_path = Path(cacert).expanduser()
        if not cert_path.exists():
            print(f"Error: CA certificate not found: {cert_path}", file=sys.stderr)
            sys.exit(1)
        return str(cert_path)
    return False


def get_base_url(env: str = "prod") -> str:
    """Get JUICE base URL for the given environment."""
    url = JUICE_ENVS.get(env)
    if not url:
        print(
            f"Error: Unknown JUICE environment '{env}'. Use: {', '.join(JUICE_ENVS)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return url


def get_token(juice_group: str, env: str = "prod") -> str:
    """Authenticate and get a scoped JWT Bearer token.

    Uses HTTP Basic auth against /v2/auth/local/token/{juice_group}.
    Tokens are cached per (env, juice_group) for the process lifetime.
    """
    cache_key = (env, juice_group)
    if cache_key in _token_cache:
        return _token_cache[cache_key]

    username, password = get_credentials()
    base_url = get_base_url(env)
    url = f"{base_url}/v2/auth/local/token/{juice_group}"

    verify = get_verify()
    try:
        resp = requests.post(url, auth=(username, password), verify=verify, timeout=30)
    except requests.ConnectionError:
        print(
            f"Error: Cannot connect to JUICE at {base_url}. Is VPN connected?",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request to JUICE timed out", file=sys.stderr)
        sys.exit(1)

    if resp.status_code == 401:
        print(
            "Error: Authentication failed — check JUICE_USERNAME and JUICE_PASSWORD",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code == 404:
        print(f"Error: JUICE group '{juice_group}' not found", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(
            f"Error: Token request failed (HTTP {resp.status_code}): {resp.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = resp.json()
    token = data.get("data", {}).get("access_token")
    if not token:
        print("Error: No access_token in response", file=sys.stderr)
        sys.exit(1)

    _token_cache[cache_key] = token
    return token


def juice_request(
    method: str,
    path: str,
    juice_group: str,
    env: str = "prod",
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
    timeout: int = 60,
) -> Any:
    """Make an authenticated request to a JUICE API endpoint.

    Automatically handles token acquisition and Bearer auth.
    Returns the parsed JSON response body.
    """
    token = get_token(juice_group, env)
    base_url = get_base_url(env)
    url = f"{base_url}{path}"
    headers = {"Authorization": f"Bearer {token}"}

    verify = get_verify()
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_body,
            verify=verify,
            timeout=timeout,
        )
    except requests.ConnectionError:
        print(
            f"Error: Cannot connect to JUICE at {base_url}. Is VPN connected?",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request timed out: {method} {path}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code == 401:
        # Token might have expired — clear cache and retry once
        cache_key = (env, juice_group)
        _token_cache.pop(cache_key, None)
        token = get_token(juice_group, env)
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_body,
            verify=verify,
            timeout=timeout,
        )

    if resp.status_code == 401:
        print(f"Error: Unauthorized for {method} {path}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 404:
        print(f"Error: Not found: {method} {path}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 500:
        detail = ""
        try:
            detail = resp.json().get("error_message", resp.text)
        except Exception:
            detail = resp.text
        print(
            f"Error: Server error for {method} {path} — the cloud endpoint may be temporarily unreachable.\n"
            f"  Detail: {detail}",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code >= 400:
        print(
            f"Error: {method} {path} returned HTTP {resp.status_code}: {resp.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    if resp.status_code == 204:
        return None
    return resp.json()


def print_table(headers: list[str], rows: list[list[str]], min_width: int = 4) -> None:
    """Print a formatted ASCII table."""
    if not rows:
        print("(no results)")
        return

    col_widths = [max(min_width, len(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "  ".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_line)
    print(separator)
    for row in rows:
        line = "  ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(line)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def resolve_juice_group(args_group: Optional[str]) -> str:
    """Resolve juice-group from CLI arg or JUICE_GROUP env var."""
    group = args_group or get_default_group()
    if not group:
        print(
            "Error: --juice-group is required (or set JUICE_GROUP env var)",
            file=sys.stderr,
        )
        sys.exit(1)
    return group


def add_common_args(parser) -> None:
    """Add common CLI arguments (--juice-group, --env, --format) to an argparse parser."""
    parser.add_argument(
        "--juice-group",
        default=None,
        help="JUICE group name for auth scope (default: JUICE_GROUP env var)",
    )
    parser.add_argument(
        "--env",
        default="prod",
        choices=list(JUICE_ENVS.keys()),
        help="JUICE environment (default: prod)",
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        help="Output format (default: table)",
    )
