#!/usr/bin/env python3
"""
NetBox Common Module
Shared utilities for NetBox scripts.
"""

import os
import sys
from typing import Any

try:
    import pynetbox
except ImportError:
    print("Error: pynetbox library not installed", file=sys.stderr)
    print("Install with: pip install pynetbox", file=sys.stderr)
    sys.exit(1)

# Suppress SSL warnings once at module load
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


NETBOX_URL = "https://dcim.tools.in.pan-net.eu/"


def get_api_token() -> str:
    """Get NetBox API token from environment"""
    token = os.environ.get("NETBOX_API_TOKEN")
    if not token:
        print("Error: NETBOX_API_TOKEN environment variable is not set", file=sys.stderr)
        print("Set it with: export NETBOX_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)
    return token


def get_netbox_client() -> Any:
    """Initialize NetBox API client

    Returns a pynetbox API client configured for the Telekom NetBox instance.
    SSL verification is disabled due to internal certificate.

    Raises SystemExit if:
        - NETBOX_API_TOKEN environment variable is not set
        - Connection fails (usually means VPN is not connected)
    """
    token = get_api_token()

    try:
        nb = pynetbox.api(NETBOX_URL, token=token)
        # Disable SSL verification due to internal certificate
        nb.http_session.verify = False
        return nb
    except Exception as e:
        print(f"Error: Failed to initialize NetBox client: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


# Country to ISO code mapping for site filtering
COUNTRY_MAPPING = {
    'AT': 'AT',
    'AUSTRIA': 'AT',
    'SK': 'SK',
    'SLOVAKIA': 'SK',
    'DE': 'DE',
    'GERMANY': 'DE',
    'CZ': 'CZ',
    'CZECHIA': 'CZ',
    'CZECH REPUBLIC': 'CZ',
    'HU': 'HU',
    'HUNGARY': 'HU',
    'HR': 'HR',
    'CROATIA': 'HR',
    'PL': 'PL',
    'POLAND': 'PL',
    'MK': 'MK',
    'NORTH MACEDONIA': 'MK',
    'MACEDONIA': 'MK',
    'ME': 'ME',
    'MONTENEGRO': 'ME',
    'US': 'US',
    'USA': 'US',
    'UNITED STATES': 'US',
}


def get_country_code(site_input: str) -> str | None:
    """Convert country name or code to ISO code

    Args:
        site_input: Country name (e.g., "Slovakia") or code (e.g., "SK")

    Returns:
        ISO country code or None if not a recognized country
    """
    return COUNTRY_MAPPING.get(site_input.upper())
