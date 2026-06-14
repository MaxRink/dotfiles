"""
Epic assignee/delivery manager parsing utilities.

GitLab epics don't have a native assignee field. The CID team uses
a "Delivery manager: @username" pattern in epic descriptions.
"""

import re


def get_assignee_username(epic) -> str | None:
    """
    Extract assignee username from an epic.

    GitLab epics don't have a native assignee field, so we parse the
    description for the "Delivery manager: @username" pattern used by the team.

    Args:
        epic: GitLab epic object

    Returns:
        str: Username of the assignee/delivery manager, or None if not found
    """
    # First try native assignee field (future-proofing)
    assignee = getattr(epic, "assignee", None)
    if assignee:
        if isinstance(assignee, dict):
            return assignee.get("username")
        # If it's a user object
        return getattr(assignee, "username", None)

    # Try assignees array
    assignees = getattr(epic, "assignees", None)
    if assignees and len(assignees) > 0:
        first = assignees[0]
        if isinstance(first, dict):
            return first.get("username")
        return getattr(first, "username", None)

    # Parse description for "Delivery manager: @username" pattern
    description = getattr(epic, "description", "") or ""
    if description:
        # Match patterns like "**Delivery manager:** @username" or "Delivery manager: @username"
        match = re.search(r'[Dd]elivery\s*[Mm]anager.*?@([\w.-]+)', description)
        if match:
            return match.group(1)

    return None


def get_assignee_name(epic) -> str:
    """
    Extract assignee/delivery manager display name from an epic.

    Returns a formatted display name. Falls back to username formatting
    if only username is available.

    Args:
        epic: GitLab epic object

    Returns:
        str: Display name of the assignee, or "-" if not found
    """
    # First try native assignees field
    assignees = getattr(epic, "assignees", None)
    if assignees and len(assignees) > 0:
        first = assignees[0]
        if isinstance(first, dict):
            return first.get("name", first.get("username", "-"))
        return str(first)

    assignee = getattr(epic, "assignee", None)
    if assignee:
        if isinstance(assignee, dict):
            return assignee.get("name", assignee.get("username", "-"))
        return str(assignee)

    # Parse description for username
    username = get_assignee_username(epic)
    if username:
        # Convert "angel.vivas-vivas" to "Angel Vivas-Vivas"
        name_parts = username.replace('-', ' ').replace('.', ' ').split()
        return ' '.join(part.capitalize() for part in name_parts)

    return "-"


def filter_epics_by_assignee(epics: list, target_username: str) -> list:
    """
    Filter epics by assignee username.

    Args:
        epics: List of GitLab epic objects
        target_username: Username to filter by

    Returns:
        list: Filtered list of epics assigned to the target user
    """
    if not target_username:
        return epics

    filtered = []
    for epic in epics:
        assignee_username = get_assignee_username(epic)
        if assignee_username and assignee_username.lower() == target_username.lower():
            filtered.append(epic)

    return filtered
