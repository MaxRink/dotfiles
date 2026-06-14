#!/usr/bin/env python3
"""
Telekom Jira Get Issue Script
Usage: jira-get.py ISSUE-KEY [--format table|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_jira_client,
    JiraClientError,
    validate_issue_key,
    format_issue_detail,
    format_json,
    print_error,
)


def get_issue(jira, issue_key: str) -> dict:
    """
    Get issue details by key.

    Args:
        jira: Jira client instance
        issue_key: Issue key (e.g., TCAAS-123)

    Returns:
        dict: Issue data
    """
    try:
        issue = jira.issue(issue_key)

        if not issue:
            raise JiraClientError(f"Issue '{issue_key}' not found")

        return issue

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            raise JiraClientError(
                f"Issue '{issue_key}' not found or you don't have permission to view it."
            )
        raise JiraClientError(f"Failed to get issue: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Get Jira issue details',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TCAAS-123
  %(prog)s CAASPROD-456 --format json
        """
    )

    parser.add_argument('issue_key', help='Issue key (e.g., TCAAS-123)')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    try:
        # Validate issue key
        issue_key = validate_issue_key(args.issue_key)

        # Initialize client
        jira = get_jira_client()

        # Get issue
        issue = get_issue(jira, issue_key)

        # Format output
        if args.format == 'json':
            print(format_json(issue))
        else:
            print(format_issue_detail(issue))

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
