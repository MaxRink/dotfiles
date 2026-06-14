#!/usr/bin/env python3
"""
Batch label Jira issues from a JQL search.

Usage:
  jira-batch-label.py --jql 'project = CAASPROD AND ...' --add-labels tdi-caas-operations
  jira-batch-label.py --jql 'project = CAASPROD AND ...' --add-labels tdi-caas-development --dry-run
"""

import sys
import argparse

sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import get_jira_client, JiraClientError, print_error, print_success
from utils.config import JIRA_URL, ALLOWED_PROJECTS
from utils.validators import validate_labels


def search_issues(jira, jql: str, max_results: int = 200) -> list:
    """Search for issues and return list of dicts with key, summary, labels, type."""
    results = []
    start = 0
    while start < max_results:
        batch = jira.jql(jql, start=start, limit=min(50, max_results - start),
                         fields="summary,labels,issuetype")
        issues = batch.get("issues", [])
        if not issues:
            break
        for issue in issues:
            fields = issue["fields"]
            results.append({
                "key": issue["key"],
                "summary": fields.get("summary", ""),
                "labels": fields.get("labels", []),
                "type": fields.get("issuetype", {}).get("name", ""),
            })
        start += len(issues)
        if start >= batch.get("total", 0):
            break
    return results


def add_labels_to_issue(jira, issue_key: str, labels: list) -> bool:
    """Add labels to a single issue using the update API."""
    label_ops = [{"add": label} for label in labels]
    payload = {"update": {"labels": label_ops}}
    base_url = jira.resource_url("issue")
    jira.put(f"{base_url}/{issue_key}", data=payload)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Batch add labels to Jira issues matching a JQL query",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run: see which CAASPROD tasks are missing ops/dev labels
  %(prog)s --jql 'project = CAASPROD AND status in (Refined, "In Progress") AND type not in (Epic) AND (labels is EMPTY OR labels not in (tdi-caas-operations, tdi-caas-development))' --add-labels tdi-caas-operations --dry-run

  # Apply operations label to all matching issues
  %(prog)s --jql 'project = CAASPROD AND status = "In Progress" AND labels is EMPTY' --add-labels tdi-caas-operations

  # Apply multiple labels
  %(prog)s --jql 'project = CAASPROD AND key in (CAASPROD-100, CAASPROD-101)' --add-labels "tdi-caas-operations,urgent"
        """,
    )

    parser.add_argument("--jql", required=True, help="JQL query to find issues")
    parser.add_argument("--add-labels", required=True, help="Labels to add (comma-separated)")
    parser.add_argument("--max", type=int, default=200, help="Max issues to process (default: 200)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be changed without making changes")

    args = parser.parse_args()

    labels = validate_labels(args.add_labels)

    # Validate project scope in JQL
    jql_upper = args.jql.upper()
    has_allowed_project = any(p in jql_upper for p in ALLOWED_PROJECTS)
    if not has_allowed_project:
        print_error(f"JQL must target an allowed project: {', '.join(ALLOWED_PROJECTS)}")
        sys.exit(1)

    try:
        jira = get_jira_client()

        print(f"Searching: {args.jql}")
        issues = search_issues(jira, args.jql, args.max)

        if not issues:
            print("No matching issues found.")
            return

        print(f"Found {len(issues)} issue(s)\n")

        if args.dry_run:
            print("=== DRY RUN (no changes will be made) ===\n")

        success = 0
        failed = 0
        skipped = 0

        for issue in issues:
            existing = issue["labels"]
            new_labels = [l for l in labels if l not in existing]
            if not new_labels:
                print(f"  SKIP {issue['key']} [{issue['type']}] - already has: {', '.join(labels)}")
                skipped += 1
                continue

            if args.dry_run:
                print(f"  WOULD ADD {issue['key']} [{issue['type']}] {issue['summary'][:60]}")
                print(f"    Current labels: {', '.join(existing) or 'None'}")
                print(f"    Adding: {', '.join(new_labels)}")
                success += 1
            else:
                try:
                    add_labels_to_issue(jira, issue["key"], new_labels)
                    print(f"  ✓ {issue['key']} [{issue['type']}] +{', '.join(new_labels)}")
                    success += 1
                except Exception as e:
                    print(f"  ✗ {issue['key']} - {e}")
                    failed += 1

        print(f"\n{'Would update' if args.dry_run else 'Updated'}: {success} | "
              f"Failed: {failed} | Skipped: {skipped}")

        if args.dry_run and success > 0:
            print("\nRe-run without --dry-run to apply changes.")

    except (JiraClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
