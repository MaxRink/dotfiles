"""
TDI Cloud Delivery - Utility Package

Shared utilities for CID GitLab operations.
"""

from .client import get_gitlab_client, get_cid_group
from .config import GITLAB_URL, ALLOWED_GROUPS, CID_GROUP_PATH
from .output import print_table, print_json, print_error
from .validators import validate_group_path
from .gitlab_users import search_group_members, find_user_by_name
from .assignee import get_assignee_username, get_assignee_name, filter_epics_by_assignee

__all__ = [
    "get_gitlab_client",
    "get_cid_group",
    "GITLAB_URL",
    "ALLOWED_GROUPS",
    "CID_GROUP_PATH",
    "print_table",
    "print_json",
    "print_error",
    "validate_group_path",
    "search_group_members",
    "find_user_by_name",
    "get_assignee_username",
    "get_assignee_name",
    "filter_epics_by_assignee",
]
