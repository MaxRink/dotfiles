#!/usr/bin/env python3
"""
PagerDuty Common Module
Shared utilities and API client for PagerDuty scripts.
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Constants
PD_API_URL = "https://api.eu.pagerduty.com"
PD_WEB_URL = "https://dt-tdi.eu.pagerduty.com"
TCAAS_TEAM_ID = os.environ.get("TCAAS_TEAM_ID", "P5TDGFM")
DEFAULT_TIMEOUT = 30


class PagerDutyError(Exception):
    """Custom exception for PagerDuty API errors."""
    pass


class PagerDutyClient:
    """PagerDuty API client with authentication and common methods."""

    def __init__(self, token: Optional[str] = None, team_id: Optional[str] = None):
        self.token = token or os.environ.get("PAGERDUTY_TOKEN")
        self.team_id = team_id or TCAAS_TEAM_ID
        self.base_url = PD_API_URL
        self.web_url = PD_WEB_URL

        if not self.token:
            raise PagerDutyError(
                "PAGERDUTY_TOKEN environment variable is not set\n"
                "Set it with: export PAGERDUTY_TOKEN='your-token'"
            )

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Token token={self.token}",
            "Content-Type": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Make an API request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise PagerDutyError(
                "Connection failed - check VPN connection and network"
            )
        except requests.exceptions.Timeout:
            raise PagerDutyError(
                f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                message = error_data.get('error', {}).get('message', str(e))
            except (json.JSONDecodeError, AttributeError):
                message = str(e)
            raise PagerDutyError(f"API error ({status_code}): {message}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params)

    def get_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        result_key: str = "items",
        max_results: int = 1000,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch paginated results from an endpoint."""
        params = params or {}
        params["limit"] = limit
        params["offset"] = 0

        all_results = []

        while len(all_results) < max_results:
            data = self.get(endpoint, params)
            results = data.get(result_key, [])
            all_results.extend(results)

            if not data.get("more", False):
                break

            params["offset"] += limit
            total = data.get("total")
            if total:
                print(
                    f"\r  Fetching {result_key}... {len(all_results)}/{total}",
                    end="", file=sys.stderr, flush=True
                )
            else:
                print(
                    f"\r  Fetching {result_key}... {len(all_results)}",
                    end="", file=sys.stderr, flush=True
                )

        if params["offset"] > 0:
            print(file=sys.stderr)  # newline after progress

        return all_results[:max_results]

    # Convenience methods for common endpoints
    def get_incidents(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """Fetch incidents with optional filters."""
        params = {"team_ids[]": self.team_id}

        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if statuses:
            params["statuses[]"] = statuses

        return self.get_paginated(
            "incidents",
            params,
            result_key="incidents",
            max_results=max_results
        )

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        """Fetch a single incident by ID."""
        data = self.get(f"incidents/{incident_id}")
        return data.get("incident", {})

    def get_oncalls(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch on-call schedules."""
        params = {"team_ids[]": self.team_id}

        if since:
            params["since"] = since
        if until:
            params["until"] = until

        data = self.get("oncalls", params)
        return data.get("oncalls", [])

    def get_services(self) -> List[Dict[str, Any]]:
        """Fetch services for the team."""
        params = {"team_ids[]": self.team_id}
        data = self.get("services", params)
        return data.get("services", [])

    def search_teams(self, query: str) -> List[Dict[str, Any]]:
        """Search for teams by name."""
        params = {"query": query}
        data = self.get("teams", params)
        return data.get("teams", [])

    def incident_url(self, incident_id: str) -> str:
        """Get the web URL for an incident."""
        return f"{self.web_url}/incidents/{incident_id}"


# Utility functions

def parse_cluster_from_title(title: str) -> Optional[Dict[str, str]]:
    """
    Parse cluster information from incident title.

    Supported formats:
    1. Standard: [site | cluster] AlertName description
    2. Convergence: CONVERGENCE [T: type | L: location | C: cluster] A: AlertName description

    Returns: {'site': 'site', 'cluster': 'cluster', 'alert_name': 'alert', 'description': 'desc'}
    """
    # Format 1: Standard AlertManager format
    # [site | cluster] AlertName description
    match = re.match(r'\[([^\|]+)\s*\|\s*([^\]]+)\]\s*(\S+)\s*(.*)', title)
    if match:
        return {
            'site': match.group(1).strip(),
            'cluster': match.group(2).strip(),
            'alert_name': match.group(3).strip(),
            'description': match.group(4).strip()
        }

    # Format 2: Convergence format
    # CONVERGENCE [T: type | L: location | C: cluster] A: AlertName description
    match = re.match(r'CONVERGENCE\s*\[T:\s*([^\|]+)\|\s*L:\s*([^\|]+)\|\s*C:\s*([^\]]+)\]\s*A:\s*(\S+)\s*(.*)', title)
    if match:
        return {
            'site': match.group(2).strip(),  # L: location as site
            'cluster': match.group(3).strip(),  # C: cluster
            'alert_name': match.group(4).strip(),  # A: AlertName
            'description': match.group(5).strip()
        }

    # Fallback - try simpler format (standard without alert name)
    match = re.match(r'\[([^\|]+)\s*\|\s*([^\]]+)\]', title)
    if match:
        return {
            'site': match.group(1).strip(),
            'cluster': match.group(2).strip(),
            'alert_name': '',
            'description': ''
        }
    return None


def extract_country_from_site(site: str) -> str:
    """Extract country code from site name (e.g., hc-czbrnc1-baremetal -> CZ)."""
    match = re.search(r'hc-([a-z]{2})', site.lower())
    if match:
        return match.group(1).upper()
    return 'Unknown'


def parse_date(date_str: str, end_of_day: bool = False) -> str:
    """
    Parse a date string and return ISO 8601 format.
    If only date provided (YYYY-MM-DD), adds time component.
    """
    if not date_str:
        return ""

    if 'T' in date_str:
        return date_str

    if end_of_day:
        return f"{date_str}T23:59:59Z"
    return f"{date_str}T00:00:00Z"


def format_datetime(dt_str: str, include_time: bool = True) -> str:
    """Format an ISO datetime string for display, converted to local timezone."""
    if not dt_str:
        return "N/A"

    utc_dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    local_dt = utc_dt.astimezone()

    if include_time:
        return local_dt.strftime('%Y-%m-%d %H:%M')
    return local_dt.strftime('%Y-%m-%d')


def get_date_range(
    since: Optional[str] = None,
    until: Optional[str] = None,
    days_ago: int = 1,
    hours_ago: Optional[int] = None
) -> Tuple[str, str]:
    """
    Calculate date range for API queries.
    Returns (since, until) as ISO 8601 strings.
    """
    now = datetime.now(timezone.utc)

    if until:
        # User-provided date: treat as exclusive end (T00:00:00Z), not end-of-day.
        # e.g. --until 2026-02-24 means "up to start of Feb 24" (i.e. Feb 23 only)
        until_dt = parse_date(until, end_of_day=False)
    else:
        until_dt = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    if since:
        since_dt = since
    elif hours_ago is not None:
        since_dt = (now - timedelta(hours=hours_ago)).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        since_dt = (now - timedelta(days=days_ago)).strftime('%Y-%m-%dT00:00:00Z')

    return (parse_date(since_dt), until_dt)


def output_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def error_exit(message: str, code: int = 1) -> None:
    """Print error message and exit."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


# Status icons for display
STATUS_ICONS = {
    'triggered': '[!]',
    'acknowledged': '[~]',
    'resolved': '[+]'
}

STATUS_LABELS = {
    'triggered': 'TRIGGERED',
    'acknowledged': 'ACKNOWLEDGED',
    'resolved': 'RESOLVED'
}
