#!/usr/bin/env python3
"""
Telekom Jira Search Script
Usage: jira-search.py "JQL query" [--max N] [--fields "field1,field2"] [--format table|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_jira_client,
    JiraClientError,
    validate_jql_projects,
    format_issues_table,
    format_json,
    print_error,
)
from utils.config import DEFAULT_SEARCH_FIELDS


def search_issues(jira, jql: str, max_results: int = 50, fields: list = None):
    """
    Search for issues using JQL.

    Args:
        jira: Jira client instance
        jql: JQL query string
        max_results: Maximum number of results to return
        fields: List of fields to retrieve

    Returns:
        tuple: (issues list, total count)
    """
    if fields is None:
        fields = DEFAULT_SEARCH_FIELDS

    try:
        # Use the Jira client's jql method
        results = jira.jql(jql, limit=max_results, fields=fields)

        issues = results.get('issues', [])
        total = results.get('total', len(issues))

        return issues, total

    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            raise JiraClientError(f"Invalid JQL query: {jql}\nError: {e}")
        raise JiraClientError(f"Search failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Search Jira issues using JQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 'project = TCAAS AND status not in (Closed, Done)'
  %(prog)s 'project = CAASPROD AND labels = tdi-caas-operations' --max 100
  %(prog)s 'project IN (CAASPROD, TCAAS) AND assignee = currentUser()' --format json

Note: Use single quotes and 'not in' instead of '!=' to avoid shell escaping issues.
        """
    )

    parser.add_argument('jql', help='JQL query string')
    parser.add_argument('--max', type=int, default=50,
                        help='Maximum results (default: 50)')
    parser.add_argument('--fields',
                        help='Comma-separated list of fields to retrieve')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    try:
        # Validate JQL only references allowed projects
        validate_jql_projects(args.jql)

        # Initialize client
        jira = get_jira_client()

        # Parse fields if provided
        fields = None
        if args.fields:
            fields = [f.strip() for f in args.fields.split(',')]

        # Search
        issues, total = search_issues(jira, args.jql, args.max, fields)

        # Format output
        if args.format == 'json':
            print(format_json({'total': total, 'issues': issues}))
        else:
            print(format_issues_table(issues, total))

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
