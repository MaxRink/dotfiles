#!/usr/bin/env python3
"""Shared utilities for CheckMK skill scripts."""

import json
import os
import sys

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST_GROUP_ALIASES = {
    "caas": "caas-bm",
    "iaas": "openstack-infra",
    "openstack": "openstack-infra",
    "storage": "staas",
    "hw": "server-hw",
    "net": "network",
}

KNOWN_HOST_GROUPS = {
    "caas-bm": "CaaS bare-metal servers",
    "openstack-infra": "IaaS / OpenStack infrastructure",
    "staas": "Storage as a Service",
    "server-hw": "Server hardware (IMM/ILO)",
    "network": "Network devices (switches, routers)",
    "pdu": "Power Distribution Units",
    "check_mk": "CheckMK monitoring infrastructure",
}


def resolve_group(name):
    """Resolve a group name or alias to the actual host group name."""
    lower = name.lower()
    if lower in HOST_GROUP_ALIASES:
        return HOST_GROUP_ALIASES[lower]
    for g in KNOWN_HOST_GROUPS:
        if lower == g.lower():
            return g
    return name


class CheckMKClient:
    """Client for CheckMK REST API."""

    def __init__(self):
        self.base_url = os.environ.get("CHECKMK_URL")
        self.site = os.environ.get("CHECKMK_SITE")
        self.user = os.environ.get("CHECKMK_USER")
        self.password = os.environ.get("CHECKMK_PASSWORD")
        self.verify_ssl = os.environ.get("CHECKMK_VERIFY_SSL", "false").lower() == "true"

        missing = []
        for var in ["CHECKMK_URL", "CHECKMK_SITE", "CHECKMK_USER", "CHECKMK_PASSWORD"]:
            if not os.environ.get(var):
                missing.append(var)
        if missing:
            print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        self.api_url = f"{self.base_url.rstrip('/')}/{self.site}/check_mk/api/1.0"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.user} {self.password}",
            "Accept": "application/json",
        })
        self.session.verify = self.verify_ssl

    def _get(self, endpoint, params=None):
        """Make GET request to CheckMK API."""
        url = f"{self.api_url}/{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError:
            print(f"Error: HTTP {resp.status_code} - {resp.text[:200]}", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print(f"Error: Cannot connect to {self.base_url}. Check VPN connection.", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("Error: Request timed out.", file=sys.stderr)
            sys.exit(1)

    def host_url(self, hostname):
        """Build CheckMK host view URL."""
        return f"{self.base_url}/{self.site}/check_mk/view.py?view_name=host&host={hostname}"
