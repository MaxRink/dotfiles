"""Jira API client wrapper with connection management and error handling."""

import os
import sys
from typing import Optional

import urllib3

from .config import JIRA_URL, ENV_TOKEN

# Suppress SSL warnings for internal certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JiraClientError(Exception):
    """Custom exception for Jira client errors."""
    pass


def get_jira_client():
    """
    Initialize and return a Jira API client.

    Returns:
        Jira: Configured Jira client instance

    Raises:
        JiraClientError: If token is missing or connection fails
    """
    token = os.environ.get(ENV_TOKEN)
    if not token:
        raise JiraClientError(
            f"Error: {ENV_TOKEN} environment variable is not set\n"
            f"Set it with: export {ENV_TOKEN}='your-personal-access-token'"
        )

    try:
        from atlassian import Jira

        # atlassian-python-api uses token_auth for Bearer token authentication
        jira = Jira(
            url=JIRA_URL,
            token=token,
            verify_ssl=False,
        )

        return jira

    except ImportError:
        raise JiraClientError(
            "Error: atlassian-python-api library not installed\n"
            "Install with: pip install atlassian-python-api"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
            raise JiraClientError(
                f"Error: Failed to connect to Jira at {JIRA_URL}\n"
                "Make sure you are connected to Telekom VPN"
            )
        raise JiraClientError(f"Error: Failed to initialize Jira client: {e}")


def make_agile_request(jira, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """
    Make a request to the Jira Agile API.

    The atlassian-python-api library doesn't expose all Agile endpoints,
    so we use the underlying session for direct requests.

    Args:
        jira: Jira client instance
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path (e.g., /rest/agile/1.0/epic/KEY/issue)
        data: Optional JSON data for POST/PUT requests

    Returns:
        dict: JSON response data

    Raises:
        JiraClientError: If request fails
    """
    import requests

    url = f"{JIRA_URL}{endpoint}"
    token = os.environ.get(ENV_TOKEN)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, verify=False)
        else:
            raise JiraClientError(f"Unsupported HTTP method: {method}")

        if response.status_code == 404:
            raise JiraClientError("Resource not found (HTTP 404)")
        elif response.status_code == 401:
            raise JiraClientError("Authentication failed (HTTP 401). Check your API token.")
        elif response.status_code == 403:
            raise JiraClientError("Access forbidden (HTTP 403). Check your permissions.")
        elif response.status_code not in (200, 201, 204):
            raise JiraClientError(f"API request failed (HTTP {response.status_code}): {response.text}")

        if response.status_code == 204:
            return {}
        return response.json()

    except requests.exceptions.ConnectionError:
        raise JiraClientError(
            f"Error: Failed to connect to {url}\n"
            "Make sure you are connected to Telekom VPN"
        )
    except requests.exceptions.Timeout:
        raise JiraClientError("Error: Request timed out. Try again.")
