"""
GitLab user search utilities for TDI Cloud Delivery skill.
"""

import sys
from .output import print_error


def search_group_members(group, search_term: str) -> list:
    """
    Search for users within a GitLab group by name or username.

    Args:
        group: GitLab group object
        search_term: Partial name or username to search for (case-insensitive)

    Returns:
        list: List of matching member dictionaries with 'username', 'name', 'id'
    """
    try:
        # GitLab API supports query parameter for member search
        members = group.members.list(query=search_term, get_all=True)

        # Convert to dict format for consistency
        results = []
        for member in members:
            results.append({
                'id': member.id,
                'username': member.username,
                'name': member.name,
            })

        return results

    except Exception as e:
        print_error(f"Failed to search group members: {e}")
        return []


def find_user_by_name(group, name: str, interactive: bool = True) -> str | None:
    """
    Find a GitLab username by searching for a partial name.

    Handles ambiguous matches by showing options to user (if interactive)
    or returning None. If no group members match, returns the input as-is
    if it looks like a username (contains '.' or '-').

    Args:
        group: GitLab group object
        name: Partial name or username to search for
        interactive: If True, prompt user when multiple matches found

    Returns:
        str: Username if found (or selected by user), or the input name if it looks like a username, None otherwise
    """
    members = search_group_members(group, name)

    if not members:
        # If no members found but input looks like a username (contains . or -), use it directly
        if '.' in name or '-' in name or '@' in name:
            # Strip @ if present
            username = name.lstrip('@')
            print(f"No group members found matching '{name}', using as direct username: @{username}", file=sys.stderr)
            return username

        print_error(f"No users found matching '{name}' in the CID group")
        return None

    if len(members) == 1:
        # Exact match or single result
        return members[0]['username']

    # Multiple matches - show options
    if interactive:
        print(f"\nMultiple users found matching '{name}':", file=sys.stderr)
        for i, member in enumerate(members, 1):
            print(f"  {i}. {member['name']} (@{member['username']})", file=sys.stderr)
        print(f"  {len(members) + 1}. Cancel", file=sys.stderr)

        try:
            choice = input("\nSelect a user (number): ").strip()
            idx = int(choice) - 1

            if 0 <= idx < len(members):
                return members[idx]['username']
            else:
                print_error("Selection cancelled")
                return None
        except (ValueError, KeyboardInterrupt):
            print_error("\nInvalid selection or cancelled")
            return None
    else:
        # Non-interactive - just show matches and return None
        print_error(f"Multiple users found matching '{name}'. Please be more specific:")
        for member in members:
            print(f"  - {member['name']} (@{member['username']})", file=sys.stderr)
        return None


def format_user_list(members: list) -> str:
    """
    Format a list of members for display.

    Args:
        members: List of member dicts with 'name' and 'username'

    Returns:
        str: Formatted string of users
    """
    if not members:
        return "No users"

    return ", ".join(f"{m['name']} (@{m['username']})" for m in members[:5])
