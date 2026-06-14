#!/usr/bin/env python3
"""
Telekom Jira Transition Issue Script
Usage: jira-transition.py ISSUE-KEY "Status Name"
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_jira_client,
    JiraClientError,
    validate_issue_key,
    print_error,
    print_success,
)
from utils.config import JIRA_URL
from utils.output import format_transitions


def get_available_transitions(jira, issue_key: str) -> list:
    """
    Get available transitions for an issue.

    Args:
        jira: Jira client instance
        issue_key: Issue key

    Returns:
        list: Available transitions
    """
    try:
        transitions = jira.get_issue_transitions(issue_key)
        # Handle both dict and list responses
        if isinstance(transitions, dict):
            return transitions.get('transitions', [])
        elif isinstance(transitions, list):
            return transitions
        return []
    except Exception as e:
        if "404" in str(e):
            raise JiraClientError(
                f"Issue '{issue_key}' not found or you don't have permission to view it."
            )
        raise JiraClientError(f"Failed to get transitions: {e}")


def find_transition_id(transitions: list, target_status: str) -> str:
    """
    Find the transition ID for a target status.

    Args:
        transitions: List of available transitions
        target_status: Target status name

    Returns:
        str: Transition ID

    Raises:
        JiraClientError: If transition not found
    """
    target_lower = target_status.lower()

    for t in transitions:
        name = t.get('name', '').lower()
        to_status = t.get('to', {})
        # Handle both dict and string formats for 'to'
        if isinstance(to_status, dict):
            to_status_name = to_status.get('name', '').lower()
        else:
            to_status_name = str(to_status).lower() if to_status else ''

        if name == target_lower or to_status_name == target_lower:
            return t.get('id')

    # Not found
    raise JiraClientError(
        f"Transition to '{target_status}' is not available.\n"
        f"{format_transitions(transitions)}"
    )


def transition_issue(jira, issue_key: str, transition_id) -> bool:
    """
    Transition an issue to a new status using the REST API directly.

    The atlassian-python-api issue_transition() method is broken — it calls
    set_issue_status() which passes the status name instead of the numeric
    transition ID, causing a '... must be an integer' error from the API.

    Args:
        jira: Jira client instance
        issue_key: Issue key
        transition_id: Transition ID (int or str)

    Returns:
        bool: True if successful
    """
    try:
        data = {"transition": {"id": int(transition_id)}}
        url = f"rest/api/2/issue/{issue_key}/transitions"
        jira.post(url, data=data)
        return True
    except Exception as e:
        raise JiraClientError(f"Failed to transition issue: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Transition a Jira issue to a new status',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TCAAS-123 "In Progress"
  %(prog)s CAASPROD-456 "Done"
  %(prog)s TCAAS-123 "In Review"

Common statuses: To Do, In Progress, In Review, Done, Closed
        """
    )

    parser.add_argument('issue_key', help='Issue key (e.g., TCAAS-123)')
    parser.add_argument('status', nargs='?', default=None,
                        help='Target status name')
    parser.add_argument('--list', action='store_true',
                        help='List available transitions without executing')

    args = parser.parse_args()

    # Validate arguments
    if not args.list and not args.status:
        print_error("Target status is required (or use --list to see available transitions)")
        sys.exit(1)

    try:
        # Validate issue key
        issue_key = validate_issue_key(args.issue_key)

        # Initialize client
        jira = get_jira_client()

        # Get available transitions
        transitions = get_available_transitions(jira, issue_key)

        # If --list flag, just show transitions
        if args.list:
            print(f"Transitions available for {issue_key}:")
            print(format_transitions(transitions))
            sys.exit(0)

        # Find and execute transition
        transition_id = find_transition_id(transitions, args.status)
        transition_issue(jira, issue_key, transition_id)

        print_success(f"Issue {issue_key} transitioned to '{args.status}'")
        print(f"  URL: {JIRA_URL}/browse/{issue_key}")

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
