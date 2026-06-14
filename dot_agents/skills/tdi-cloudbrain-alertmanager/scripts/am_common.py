#!/usr/bin/env python3
"""
AlertManager Common Module
Shared utilities and API client for AlertManager scripts.
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Constants
DEFAULT_TIMEOUT = 30


class AlertManagerError(Exception):
    """Custom exception for AlertManager API errors."""
    pass


class AlertManagerClient:
    """AlertManager API client with basic authentication."""

    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True
    ):
        self.base_url = (url or os.environ.get("ALERTMANAGER_URL", "")).rstrip('/')
        self.username = username or os.environ.get("ALERTMANAGER_USER")
        self.password = password or os.environ.get("ALERTMANAGER_PASSWORD")

        # Default to not verifying SSL for corporate CAs (can be overridden with env var)
        verify_env = os.environ.get("ALERTMANAGER_VERIFY_SSL", "").lower()
        if verify_env in ("true", "1", "yes"):
            self.verify_ssl = True
        else:
            self.verify_ssl = False

        if not self.base_url:
            raise AlertManagerError(
                "ALERTMANAGER_URL environment variable is not set.\n"
                "Set it with: export ALERTMANAGER_URL='https://alertmanager.example.com'"
            )

        if not self.username or not self.password:
            raise AlertManagerError(
                "ALERTMANAGER_USER and ALERTMANAGER_PASSWORD environment variables are required.\n"
                "Set them with:\n"
                "  export ALERTMANAGER_USER='username'\n"
                "  export ALERTMANAGER_PASSWORD='password'"
            )

        self.auth = HTTPBasicAuth(self.username, self.password)

        # Suppress SSL warnings if verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Any:
        """Make an API request with error handling."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                auth=self.auth,
                params=params,
                json=json_data,
                timeout=timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            if response.text:
                return response.json()
            return None

        except requests.exceptions.ConnectionError as e:
            # Check if it's an SSL error
            if 'SSL' in str(e) or 'certificate' in str(e).lower():
                raise AlertManagerError(
                    f"SSL certificate verification failed.\n"
                    f"If using a corporate CA, set: export ALERTMANAGER_VERIFY_SSL=false"
                )
            raise AlertManagerError(
                f"Connection failed to {self.base_url}\n"
                "Check VPN connection and URL"
            )
        except requests.exceptions.Timeout:
            raise AlertManagerError(
                f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                message = error_data.get('error', str(e))
            except (json.JSONDecodeError, AttributeError):
                message = e.response.text or str(e)
            raise AlertManagerError(f"API error ({status_code}): {message}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json_data: Dict[str, Any]) -> Any:
        """Make a POST request."""
        return self._request("POST", endpoint, json_data=json_data)

    def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint)

    # Silence operations
    def list_silences(self, filter_expired: bool = False) -> List[Dict[str, Any]]:
        """List all silences."""
        silences = self.get("/api/v2/silences") or []

        if filter_expired:
            now = datetime.now(timezone.utc)
            silences = [
                s for s in silences
                if s.get('status', {}).get('state') != 'expired'
            ]

        return silences

    def create_silence(
        self,
        matchers: List[Dict[str, Any]],
        starts_at: str,
        ends_at: str,
        created_by: str,
        comment: str
    ) -> Dict[str, Any]:
        """Create a new silence."""
        payload = {
            "matchers": matchers,
            "startsAt": starts_at,
            "endsAt": ends_at,
            "createdBy": created_by,
            "comment": comment
        }
        return self.post("/api/v2/silences", payload)

    def delete_silence(self, silence_id: str) -> None:
        """Delete (expire) a silence."""
        self.delete(f"/api/v2/silence/{silence_id}")

    # Alert operations
    def list_alerts(
        self,
        active: bool = True,
        silenced: bool = False,
        inhibited: bool = False,
        filter_matchers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List alerts with optional filters."""
        params = {
            "active": str(active).lower(),
            "silenced": str(silenced).lower(),
            "inhibited": str(inhibited).lower()
        }

        if filter_matchers:
            params["filter"] = filter_matchers

        return self.get("/api/v2/alerts", params) or []


# Utility functions

def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration string into timedelta.
    Supports: 1h, 2d, 1w, 6M (months as 30 days)
    """
    match = re.match(r'^(\d+)([hdwM])$', duration_str)
    if not match:
        raise ValueError(
            f"Invalid duration format: {duration_str}\n"
            "Use format like: 1h, 2d, 1w, 6M"
        )

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'w':
        return timedelta(weeks=value)
    elif unit == 'M':
        return timedelta(days=value * 30)  # Approximate months

    raise ValueError(f"Unknown duration unit: {unit}")


def parse_matcher(matcher_str: str) -> Dict[str, Any]:
    """
    Parse a matcher string into AlertManager matcher format.
    Supports: name=value, name!=value, name=~regex, name!~regex
    """
    # Try regex match (=~ or !~)
    match = re.match(r'^([^=!~]+)(=~|!~)(.+)$', matcher_str)
    if match:
        return {
            "name": match.group(1).strip(),
            "value": match.group(3).strip(),
            "isRegex": True,
            "isEqual": match.group(2) == "=~"
        }

    # Try equality match (= or !=)
    match = re.match(r'^([^=!]+)(!=|=)(.+)$', matcher_str)
    if match:
        return {
            "name": match.group(1).strip(),
            "value": match.group(3).strip(),
            "isRegex": False,
            "isEqual": match.group(2) == "="
        }

    raise ValueError(
        f"Invalid matcher format: {matcher_str}\n"
        "Use format like: alertname=MyAlert, cluster!=prod, name=~regex.*"
    )


def format_datetime(dt_str: str) -> str:
    """Format an ISO datetime string for display."""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except (ValueError, AttributeError):
        return dt_str[:19].replace('T', ' ')


def format_matchers(matchers: List[Dict[str, Any]]) -> str:
    """Format matchers list for display."""
    parts = []
    for m in matchers:
        name = m.get('name', '')
        value = m.get('value', '')
        is_regex = m.get('isRegex', False)
        is_equal = m.get('isEqual', True)

        if is_regex:
            op = '=~' if is_equal else '!~'
        else:
            op = '=' if is_equal else '!='

        parts.append(f"{name}{op}{value}")

    return ', '.join(parts)


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def to_iso8601(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string."""
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def output_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def error_exit(message: str, code: int = 1) -> None:
    """Print error message and exit."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)
