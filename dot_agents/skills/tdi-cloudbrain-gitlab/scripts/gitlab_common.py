#!/usr/bin/env python3
"""
GitLab Common Module - Shared utilities for GitLab skill scripts
"""

import os
import sys

try:
    import gitlab
except ImportError:
    print("Error: python-gitlab library not installed", file=sys.stderr)
    print("Install with: pip install python-gitlab", file=sys.stderr)
    sys.exit(1)

# Add core lib to path for cloudbrain_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib'))
from cloudbrain_config import get_config_list

# Allowed group prefixes (configurable via cloudbrain.yaml or GITLAB_GROUPS env var)
ALLOWED_GROUPS = get_config_list("gitlab", "groups",
                                 default=["cit/t-caas", "tdi-caas"],
                                 env_var="GITLAB_GROUPS")

GITLAB_URL = "https://gitlab.devops.telekom.de"


def get_gitlab_client():
    """Initialize GitLab API client"""
    token = os.environ.get("GITLAB_API_TOKEN")
    if not token:
        print("Error: GITLAB_API_TOKEN environment variable is not set", file=sys.stderr)
        print("Set it with: export GITLAB_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)

    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        gl = gitlab.Gitlab(GITLAB_URL, private_token=token, ssl_verify=False)
        gl.auth()
        return gl
    except Exception as e:
        print(f"Error: Failed to initialize GitLab client: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


def validate_group(group_path: str) -> bool:
    """Check if group path is in the allowed list (including subgroups)"""
    normalized = group_path.strip("/").lower()
    for allowed in ALLOWED_GROUPS:
        if normalized == allowed.lower() or normalized.startswith(allowed.lower() + "/"):
            return True
    return False


def validate_project(project_path: str) -> bool:
    """Check if project path belongs to an allowed group"""
    normalized = project_path.strip("/").lower()
    for allowed in ALLOWED_GROUPS:
        if normalized.startswith(allowed.lower() + "/"):
            return True
    return False
