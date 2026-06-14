#!/usr/bin/env python3
"""
Telekom Jira Epic Children Script
Usage: jira-epic-children.py EPIC-KEY [--max N] [--format table|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_jira_client,
    JiraClientError,
    validate_issue_key,
    format_issues_table,
    format_json,
    print_error,
)
from utils.client import make_agile_request


def get_epic_children(jira, epic_key: str, max_results: int = 50,
                      fields: str = None) -> tuple:
    """
    Get child issues of an epic using the Agile API.

    Args:
        jira: Jira client instance
        epic_key: Epic issue key
        max_results: Maximum results to return
        fields: Comma-separated fields to retrieve

    Returns:
        tuple: (issues list, total count)
    """
    if fields is None:
        fields = "summary,status,assignee,issuetype,labels,customfield_21920,customfield_21921"

    try:
        endpoint = f"/rest/agile/1.0/epic/{epic_key}/issue"
        params = f"?maxResults={max_results}&fields={fields}"

        result = make_agile_request(jira, "GET", endpoint + params)

        issues = result.get('issues', [])
        total = result.get('total', len(issues))

        return issues, total

    except JiraClientError as e:
        if "404" in str(e):
            raise JiraClientError(
                f"Epic '{epic_key}' not found or you don't have permission to view it."
            )
        raise


def main():
    parser = argparse.ArgumentParser(
        description='List child issues of a Jira Epic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TCAAS-100
  %(prog)s CAASPROD-500 --max 100
  %(prog)s TCAAS-100 --format json

Note: This uses the Agile API to get all children linked to the epic.
        """
    )

    parser.add_argument('epic_key', help='Epic issue key (e.g., TCAAS-100)')
    parser.add_argument('--max', type=int, default=50,
                        help='Maximum results (default: 50)')
    parser.add_argument('--fields',
                        help='Comma-separated list of fields to retrieve')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    try:
        # Validate epic key
        epic_key = validate_issue_key(args.epic_key)

        # Initialize client
        jira = get_jira_client()

        # Get children
        issues, total = get_epic_children(jira, epic_key, args.max, args.fields)

        # Format output
        if args.format == 'json':
            print(format_json({'epic': epic_key, 'total': total, 'issues': issues}))
        else:
            print(f"Epic {epic_key}: {total} child issues (showing {len(issues)})\n")
            if issues:
                print(format_issues_table(issues, total))
            else:
                print("No child issues found.")

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
