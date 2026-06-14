#!/usr/bin/env python3
"""
Telekom Jira Create Issue Script
Usage: jira-create.py --project PROJECT --type TYPE --summary "Title" [options]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_jira_client,
    JiraClientError,
    validate_project,
    print_error,
    print_success,
)
from utils.client import make_agile_request
from utils.config import JIRA_URL, CUSTOM_FIELDS
from utils.validators import validate_labels, validate_date


def create_issue(jira, project: str, issue_type: str, summary: str,
                 description: str = None, labels: list = None,
                 assignee: str = None, target_start: str = None,
                 target_end: str = None, fix_version: str = None,
                 parent: str = None) -> str:
    """
    Create a new Jira issue.

    Args:
        jira: Jira client instance
        project: Project key
        issue_type: Issue type (Task, Bug, Story, Epic, Sub-task)
        summary: Issue title
        description: Issue description
        labels: List of labels
        assignee: Assignee username
        target_start: Target start date (YYYY-MM-DD)
        target_end: Target end date (YYYY-MM-DD)
        fix_version: Fix version name
        parent: Parent issue key (for sub-tasks)

    Returns:
        str: Created issue key
    """
    fields = {
        'project': {'key': project},
        'issuetype': {'name': issue_type},
        'summary': summary,
    }

    if description:
        fields['description'] = description

    if labels:
        fields['labels'] = labels

    if assignee:
        fields['assignee'] = {'name': assignee}

    if target_start:
        fields[CUSTOM_FIELDS['target_start']] = target_start

    if target_end:
        fields[CUSTOM_FIELDS['target_end']] = target_end

    if fix_version:
        fields['fixVersions'] = [{'name': fix_version}]

    # For Epics, set the Epic Name field (required)
    if issue_type.lower() == 'epic':
        fields[CUSTOM_FIELDS['epic_name']] = summary

    if parent:
        fields['parent'] = {'key': parent}

    try:
        result = jira.create_issue(fields=fields)

        if isinstance(result, dict):
            return result.get('key', '')
        return str(result)

    except Exception as e:
        error_msg = str(e)
        if "required" in error_msg.lower():
            raise JiraClientError(f"Missing required field: {e}")
        raise JiraClientError(f"Failed to create issue: {e}")


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
        description='Create a new Jira issue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project TCAAS --type Task --summary "Implement new feature"
  %(prog)s --project CAASPROD --type Bug --summary "Fix login issue" --labels "tdi-caas-operations"
  %(prog)s --project TCAAS --type Task --summary "Sprint task" --epic TCAAS-100 --assignee john.doe
        """
    )

    # Required arguments
    parser.add_argument('--project', required=True,
                        help='Project key (CAASPROD, TCAAS, or ONB)')
    parser.add_argument('--type', required=True,
                        help='Issue type (Task, Bug, Story, Epic, Sub-task)')
    parser.add_argument('--summary', required=True,
                        help='Issue title')

    # Optional arguments
    parser.add_argument('--description',
                        help='Issue description')
    parser.add_argument('--labels',
                        help='Comma-separated labels')
    parser.add_argument('--assignee',
                        help='Assignee username (email)')
    parser.add_argument('--target-start',
                        help='Target start date (YYYY-MM-DD)')
    parser.add_argument('--target-end',
                        help='Target end date (YYYY-MM-DD)')
    parser.add_argument('--fix-version',
                        help='Fix version name')
    parser.add_argument('--epic',
                        help='Epic key to link to')
    parser.add_argument('--parent',
                        help='Parent issue key (for sub-tasks)')

    args = parser.parse_args()

    try:
        # Validate project
        project = validate_project(args.project)

        # Parse and validate optional fields
        labels = validate_labels(args.labels) if args.labels else None

        if args.target_start:
            validate_date(args.target_start, 'target-start')

        if args.target_end:
            validate_date(args.target_end, 'target-end')

        # Initialize client
        jira = get_jira_client()

        # Create issue
        issue_key = create_issue(
            jira,
            project=project,
            issue_type=args.type,
            summary=args.summary,
            description=args.description,
            labels=labels,
            assignee=args.assignee,
            target_start=args.target_start,
            target_end=args.target_end,
            fix_version=args.fix_version,
            parent=args.parent,
        )

        # Link to epic if specified (requires separate API call)
        if args.epic and issue_key:
            try:
                link_to_epic(jira, issue_key, args.epic)
                epic_msg = f"\n  Epic: {args.epic}"
            except JiraClientError as e:
                print_success(f"Issue created: {issue_key}")
                print(f"  URL: {JIRA_URL}/browse/{issue_key}")
                print_error(f"Warning: {e}")
                sys.exit(0)
        else:
            epic_msg = ""

        print_success(f"Issue created: {issue_key}")
        print(f"  URL: {JIRA_URL}/browse/{issue_key}{epic_msg}")

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
