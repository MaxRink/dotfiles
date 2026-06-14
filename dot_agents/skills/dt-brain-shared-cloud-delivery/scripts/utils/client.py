"""
GitLab client utilities for TDI Cloud Delivery skill.
"""

import os
import sys

try:
    import gitlab
except ImportError:
    print("Error: python-gitlab not installed. Install with: pip install python-gitlab", file=sys.stderr)
    sys.exit(1)

from .config import GITLAB_URL, CID_GROUP_PATH


def get_gitlab_client():
    """
    Create and authenticate a GitLab client.

    Returns:
        gitlab.Gitlab: Authenticated GitLab client

    Exits with error if:
        - GITLAB_API_TOKEN is not set
        - Authentication fails (likely VPN issue)
    """
    token = os.environ.get("GITLAB_API_TOKEN")
    if not token:
        print("Error: GITLAB_API_TOKEN environment variable is not set", file=sys.stderr)
        print("", file=sys.stderr)
        print("To set it:", file=sys.stderr)
        print("  export GITLAB_API_TOKEN='your-personal-access-token'", file=sys.stderr)
        print("", file=sys.stderr)
        print("To get a PAT:", file=sys.stderr)
        print("  1. Log in to GitLab at https://gitlab.devops.telekom.de/", file=sys.stderr)
        print("  2. Go to User Settings > Access Tokens", file=sys.stderr)
        print("  3. Create a token with 'read_api' scope", file=sys.stderr)
        sys.exit(1)

    try:
        gl = gitlab.Gitlab(GITLAB_URL, private_token=token, ssl_verify=False)
        gl.auth()
        return gl
    except gitlab.exceptions.GitlabAuthenticationError as e:
        print(f"Error: GitLab authentication failed: {e}", file=sys.stderr)
        print("Check that your GITLAB_API_TOKEN is valid.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not connect to GitLab: {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Make sure you are connected to the Telekom VPN.", file=sys.stderr)
        sys.exit(1)


def get_cid_group(gl=None):
    """
    Get the CID group object.

    Args:
        gl: Optional GitLab client (will create one if not provided)

    Returns:
        gitlab.v4.objects.Group: The CID group object
    """
    if gl is None:
        gl = get_gitlab_client()

    try:
        return gl.groups.get(CID_GROUP_PATH)
    except gitlab.exceptions.GitlabGetError as e:
        print(f"Error: Could not access group '{CID_GROUP_PATH}': {e}", file=sys.stderr)
        print("Check that you have access to this group.", file=sys.stderr)
        sys.exit(1)
