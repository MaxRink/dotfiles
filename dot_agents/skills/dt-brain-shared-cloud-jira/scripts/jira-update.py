#!/usr/bin/env python3
"""
Telekom Jira Update Issue Script
Usage: jira-update.py ISSUE-KEY [options]
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
from utils.client import make_agile_request
from utils.config import JIRA_URL, CUSTOM_FIELDS
from utils.validators import validate_labels, validate_date


def update_issue(jira, issue_key: str, summary: str = None,
                 description: str = None, assignee: str = None,
                 target_start: str = None, target_end: str = None,
                 add_labels: list = None, remove_labels: list = None) -> bool:
    """
    Update a Jira issue.

    Args:
        jira: Jira client instance
        issue_key: Issue key
        summary: New summary
        description: New description
        assignee: New assignee username
        target_start: New target start date
        target_end: New target end date
        add_labels: Labels to add
        remove_labels: Labels to remove

    Returns:
        bool: True if successful
    """
    fields = {}
    update = {}

    if summary:
        fields['summary'] = summary

    if description:
        fields['description'] = description

    if assignee:
        fields['assignee'] = {'name': assignee}

    if target_start:
        fields[CUSTOM_FIELDS['target_start']] = target_start

    if target_end:
        fields[CUSTOM_FIELDS['target_end']] = target_end

    # Handle label add/remove operations
    if add_labels or remove_labels:
        label_ops = []
        if add_labels:
            for label in add_labels:
                label_ops.append({'add': label})
        if remove_labels:
            for label in remove_labels:
                label_ops.append({'remove': label})
        update['labels'] = label_ops

    # Skip if nothing to update (epic-only update handled separately)
    if not fields and not update:
        return True

    try:
        # Build the update payload
        payload = {}
        if fields:
            payload['fields'] = fields
        if update:
            payload['update'] = update

        if update:
            # Use direct PUT request since update_issue_field wraps
            # everything under {"fields": ...} which breaks the "update" key
            base_url = jira.resource_url("issue")
            jira.put(f"{base_url}/{issue_key}", data=payload)
        elif fields:
            jira.update_issue_field(issue_key, fields)
        return True

    except Exception as e:
        raise JiraClientError(f"Failed to update issue: {e}")


def link_to_epic(jira, issue_key: str, epic_key: str) -> bool:
    """
    Link an issue to an epic using the Agile API.

    Args:
        jira: Jira client instance
        issue_key: Issue key to link
        epic_key: Epic key to link to

    Returns:
        bool: True if successful
    """
    try:
        endpoint = f"/rest/agile/1.0/epic/{epic_key}/issue"
        data = {"issues": [issue_key]}
        make_agile_request(jira, "POST", endpoint, data)
        return True
    except Exception as e:
        raise JiraClientError(f"Failed to link to epic {epic_key}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Update a Jira issue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TCAAS-123 --summary "Updated title"
  %(prog)s TCAAS-123 --add-labels "urgent,reviewed"
  %(prog)s CAASPROD-456 --assignee john.doe@t-systems.com --target-start 2026-02-01
  %(prog)s TCAAS-123 --epic TCAAS-100
        """
    )

    parser.add_argument('issue_key', help='Issue key (e.g., TCAAS-123)')
    parser.add_argument('--summary', help='New summary/title')
    parser.add_argument('--description', help='New description')
    parser.add_argument('--add-labels', help='Labels to add (comma-separated)')
    parser.add_argument('--remove-labels', help='Labels to remove (comma-separated)')
    parser.add_argument('--assignee', help='New assignee username (email)')
    parser.add_argument('--target-start', help='Target start date (YYYY-MM-DD)')
    parser.add_argument('--target-end', help='Target end date (YYYY-MM-DD)')
    parser.add_argument('--epic', help='Epic key to link to')

    args = parser.parse_args()

    # Check if any update was requested
    has_update = any([
        args.summary, args.description, args.add_labels, args.remove_labels,
        args.assignee, args.target_start, args.target_end, args.epic
    ])

    if not has_update:
        print_error("No updates specified. Use --help to see available options.")
        sys.exit(1)

    try:
        # Validate issue key
        issue_key = validate_issue_key(args.issue_key)

        # Parse and validate optional fields
        add_labels = validate_labels(args.add_labels) if args.add_labels else None
        remove_labels = validate_labels(args.remove_labels) if args.remove_labels else None

        if args.target_start:
            validate_date(args.target_start, 'target-start')

        if args.target_end:
            validate_date(args.target_end, 'target-end')

        # Initialize client
        jira = get_jira_client()

        # Update issue fields
        update_issue(
            jira,
            issue_key=issue_key,
            summary=args.summary,
            description=args.description,
            assignee=args.assignee,
            target_start=args.target_start,
            target_end=args.target_end,
            add_labels=add_labels,
            remove_labels=remove_labels,
        )

        # Link to epic if specified
        epic_msg = ""
        if args.epic:
            link_to_epic(jira, issue_key, args.epic)
            epic_msg = f"\n  Epic: {args.epic}"

        print_success(f"Issue {issue_key} updated successfully!")
        print(f"  URL: {JIRA_URL}/browse/{issue_key}{epic_msg}")

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
