#!/usr/bin/env python3
"""Search for Jira users by name or email fragment, optionally scoped to a project."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import ssl

ALLOWED_PROJECTS = {"CAASPROD", "TCAAS", "ONB"}

def make_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def jira_get(url, token):
    ctx = make_ctx()
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())

def search_global(query, max_results, token):
    base_url = "https://jira.telekom.de"
    params = urllib.parse.urlencode({"username": query, "maxResults": max_results})
    return jira_get(f"{base_url}/rest/api/2/user/search?{params}", token)

def search_in_project(query, project, token):
    """Collect unique assignees from the project, filtered by query fragment."""
    base_url = "https://jira.telekom.de"
    q = query.lower()
    seen = {}
    start = 0
    page_size = 100

    while True:
        jql = urllib.parse.quote(f"project = {project} AND assignee is not EMPTY")
        fields = "assignee"
        params = f"jql={jql}&fields={fields}&maxResults={page_size}&startAt={start}"
        data = jira_get(f"{base_url}/rest/api/2/search?{params}", token)
        issues = data.get("issues", [])
        if not issues:
            break
        for issue in issues:
            assignee = issue["fields"].get("assignee")
            if assignee and assignee.get("name") not in seen:
                name = assignee.get("name", "")
                display = assignee.get("displayName", "")
                if q in name.lower() or q in display.lower():
                    seen[name] = display
        start += len(issues)
        if start >= data.get("total", 0):
            break

    return [{"name": k, "displayName": v} for k, v in sorted(seen.items(), key=lambda x: x[1])]

def main():
    parser = argparse.ArgumentParser(description="Search Jira users by name or email")
    parser.add_argument("query", help="Name or email fragment to search for")
    parser.add_argument("--project", help=f"Scope to project assignees ({', '.join(sorted(ALLOWED_PROJECTS))})")
    parser.add_argument("--max", type=int, default=10, help="Max results for global search (default: 10)")
    args = parser.parse_args()

    token = os.environ.get("JIRA_API_TOKEN") or os.environ.get("JIRA_TOKEN")
    if not token:
        print("ERROR: JIRA_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    if args.project:
        project = args.project.upper()
        if project not in ALLOWED_PROJECTS:
            print(f"ERROR: project must be one of {sorted(ALLOWED_PROJECTS)}", file=sys.stderr)
            sys.exit(1)
        print(f"Searching assignees in {project} matching '{args.query}'...\n")
        users = search_in_project(args.query, project, token)
    else:
        users = search_global(args.query, args.max, token)

    if not users:
        print(f"No users found for '{args.query}'")
        return

    print(f"{'Username (email)':<45} {'Display Name'}")
    print("-" * 75)
    for u in users:
        print(f"{u['name']:<45} {u['displayName']}")

if __name__ == "__main__":
    main()
