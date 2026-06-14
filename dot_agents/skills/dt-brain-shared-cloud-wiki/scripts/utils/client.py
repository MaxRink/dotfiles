"""Confluence API client wrapper with connection management and error handling."""

import os
import sys
from typing import Optional

import urllib3

from .config import WIKI_URL, ENV_USER, ENV_TOKEN

# Suppress SSL warnings for internal certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConfluenceClientError(Exception):
    """Custom exception for Confluence client errors."""
    pass


def get_confluence_client():
    """
    Initialize and return a Confluence API client.

    Returns:
        Confluence: Configured Confluence client instance

    Raises:
        ConfluenceClientError: If credentials are missing or connection fails
    """
    user = os.environ.get(ENV_USER)
    token = os.environ.get(ENV_TOKEN)

    if not user:
        raise ConfluenceClientError(
            f"Error: {ENV_USER} environment variable is not set\n"
            f"Set it with: export {ENV_USER}='your.email@t-systems.com'"
        )

    if not token:
        raise ConfluenceClientError(
            f"Error: {ENV_TOKEN} environment variable is not set\n"
            f"Set it with: export {ENV_TOKEN}='your-personal-access-token'"
        )

    try:
        from atlassian import Confluence

        # Confluence uses basic auth with username:token
        confluence = Confluence(
            url=WIKI_URL,
            username=user,
            password=token,
            verify_ssl=False,
        )

        return confluence

    except ImportError:
        raise ConfluenceClientError(
            "Error: atlassian-python-api library not installed\n"
            "Install with: pip install atlassian-python-api"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
            raise ConfluenceClientError(
                f"Error: Failed to connect to Confluence at {WIKI_URL}\n"
                "Make sure you are connected to Telekom VPN"
            )
        raise ConfluenceClientError(f"Error: Failed to initialize Confluence client: {e}")


def handle_confluence_error(e: Exception, operation: str = "operation") -> None:
    """
    Handle Confluence API errors and raise appropriate exceptions.

    Args:
        e: The caught exception
        operation: Description of the operation for error message

    Raises:
        ConfluenceClientError: With appropriate error message
    """
    error_msg = str(e).lower()

    if "401" in str(e):
        raise ConfluenceClientError(
            "Authentication failed (HTTP 401). Check your credentials.\n"
            f"  {ENV_USER}: Your email address\n"
            f"  {ENV_TOKEN}: Your Personal Access Token"
        )
    elif "403" in str(e):
        raise ConfluenceClientError(
            f"Access forbidden (HTTP 403). Check your permissions for this {operation}."
        )
    elif "404" in str(e):
        raise ConfluenceClientError(
            f"Resource not found (HTTP 404). The page or space may not exist."
        )
    elif "409" in str(e):
        raise ConfluenceClientError(
            "Version conflict (HTTP 409). The page may have been modified by another user.\n"
            "Try fetching the latest version and retrying."
        )
    elif "connection" in error_msg or "refused" in error_msg:
        raise ConfluenceClientError(
            f"Error: Failed to connect to Confluence at {WIKI_URL}\n"
            "Make sure you are connected to Telekom VPN"
        )
    else:
        raise ConfluenceClientError(f"Error during {operation}: {e}")
