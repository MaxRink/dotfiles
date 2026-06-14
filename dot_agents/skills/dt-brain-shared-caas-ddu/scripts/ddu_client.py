"""
DDU API Client Module

Shared client logic for DDU API operations.
"""
import os
import sys
import json
import ssl
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Any

# SSL context that skips verification for internal Telekom certificates
_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


class DDUClient:
    """Client for DDU API operations."""

    BASE_URL = "https://ddu.caas.in.pan-net.eu"

    def __init__(self, token: Optional[str] = None):
        """Initialize DDU client with API token."""
        self.token = token or os.environ.get("DDU_API_TOKEN")
        if not self.token:
            raise ValueError(
                "DDU_API_TOKEN environment variable is not set.\n"
                "Set it with: export DDU_API_TOKEN='your-token'"
            )

    def _request(self, endpoint: str, params: Optional[dict] = None) -> tuple[Any, int]:
        """Make API request and return (data, status_code)."""
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(
            url,
            headers={
                "X-API-TOKEN": self.token,
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, context=_SSL_CONTEXT, timeout=30) as response:
                body = response.read().decode("utf-8")
                # Try to parse as JSON, fall back to raw text
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    data = body
                return data, response.status
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = body
            return data, e.code
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Failed to connect to DDU API: {e.reason}\n"
                "Ensure you are connected to Telekom VPN."
            )

    def check_cluster(self, name: str) -> tuple[Any, int]:
        """Check cluster health status."""
        return self._request("/api/v1/cluster/check", {"name": name})

    def get_secrets(self, name: str) -> tuple[dict, int]:
        """Get cluster secrets."""
        return self._request("/api/v1/cluster/secrets", {"name": name})

    def get_report(self, name: str) -> tuple[dict, int]:
        """Get cluster report."""
        return self._request("/api/v1/cluster/report", {"name": name})

    def get_all_reports(self) -> tuple[Any, int]:
        """Get report for all clusters."""
        return self._request("/api/v1/cluster/report")


def print_error(message: str):
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def format_value(value: Any, indent: int = 0) -> str:
    """Format a value for display with indentation."""
    prefix = "  " * indent
    lines = []

    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                lines.append(format_value(v, indent + 1))
            else:
                lines.append(f"{prefix}{k}: {v}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                lines.append(format_value(item, indent))
                lines.append("")
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{value}")

    return "\n".join(lines)


def format_cluster(cluster: dict, indent: int = 0) -> str:
    """Format cluster info for display."""
    prefix = "  " * indent
    lines = []

    if isinstance(cluster, dict):
        name = cluster.get("name", cluster.get("cluster_name", "Unknown"))
        lines.append(f"{prefix}NAME: {name}")
        lines.append(f"{prefix}" + "-" * 40)

        for k, v in cluster.items():
            if k in ("name", "cluster_name"):
                continue
            key_upper = k.upper()
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}  {key_upper}:")
                lines.append(format_value(v, indent + 2))
            else:
                lines.append(f"{prefix}  {key_upper}: {v}")
        lines.append("")
    else:
        lines.append(f"{prefix}{cluster}")

    return "\n".join(lines)
