#!/usr/bin/env python3
"""
TDI CaaS Team Report Generator

Generates a bi-weekly report combining:
- Jira CAASPROD: Completed, In Progress, and Refined issues
- GitLab tdi-caas: Merged merge requests grouped by project
"""

import argparse
import json
import os
import ssl
import subprocess
import sys
import urllib.request
import urllib.parse
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


# Configuration
JIRA_BASE_URL = "https://jira.telekom.de"
GITLAB_BASE_URL = "https://gitlab.devops.telekom.de"
GITLAB_GROUP = "tdi-caas"
JIRA_PROJECT = "CAASPROD"

# Key labels for categorization
CATEGORY_LABELS = {
    "tdi-caas-operations": "Ops",
    "tdi-caas-development": "Dev",
    "tdi-caas-cluster-upgrade": "Upgrade",
}


def get_ssl_context():
    """Create SSL context that doesn't verify certificates (internal network)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def jira_request(endpoint: str, token: str) -> dict:
    """Make a request to the Jira API."""
    url = f"{JIRA_BASE_URL}/rest/api/2/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, context=get_ssl_context()) as resp:
        return json.loads(resp.read().decode())


def jira_search(jql: str, token: str, max_results: int = 200) -> list:
    """Search Jira issues using JQL."""
    params = urllib.parse.urlencode({
        "jql": jql,
        "maxResults": max_results,
        "fields": "key,summary,issuetype,status,assignee,labels,created,updated"
    })
    result = jira_request(f"search?{params}", token)
    return result.get("issues", [])


def gitlab_request(endpoint: str, token: str) -> list:
    """Make a request to the GitLab API, handling pagination."""
    all_results = []
    page = 1
    per_page = 100

    while True:
        url = f"{GITLAB_BASE_URL}/api/v4/{endpoint}"
        separator = "&" if "?" in endpoint else "?"
        url = f"{url}{separator}page={page}&per_page={per_page}"

        req = urllib.request.Request(url)
        req.add_header("PRIVATE-TOKEN", token)

        with urllib.request.urlopen(req, context=get_ssl_context()) as resp:
            data = json.loads(resp.read().decode())
            if not data:
                break
            all_results.extend(data)
            if len(data) < per_page:
                break
            page += 1

    return all_results


def get_gitlab_group_id(token: str) -> int:
    """Get the GitLab group ID for tdi-caas."""
    url = f"{GITLAB_BASE_URL}/api/v4/groups/{urllib.parse.quote(GITLAB_GROUP, safe='')}"
    req = urllib.request.Request(url)
    req.add_header("PRIVATE-TOKEN", token)

    with urllib.request.urlopen(req, context=get_ssl_context()) as resp:
        data = json.loads(resp.read().decode())
        return data["id"]


def get_merged_mrs(token: str, since_date: str, group_id: int) -> list:
    """Get merged MRs from the GitLab group since a given date."""
    endpoint = f"groups/{group_id}/merge_requests?state=merged&updated_after={since_date}T00:00:00Z"
    return gitlab_request(endpoint, token)


def format_labels(labels: list, for_pdf: bool = False) -> str:
    """Format labels for display, highlighting category labels."""
    if not labels:
        return "-"

    formatted = []
    for label in labels:
        if label in CATEGORY_LABELS:
            # Use plain text for PDF compatibility
            formatted.append(CATEGORY_LABELS[label])
        elif not label.startswith("["):  # Skip date/week labels
            formatted.append(label)

    return ", ".join(formatted[:3]) if formatted else "-"


def get_issue_category(issue: dict) -> str:
    """Categorize issue by priority: On-Call → Development → Upgrades → Operations → Other."""
    summary = issue["fields"].get("summary", "").lower()
    labels = issue["fields"].get("labels", [])

    # 1. On-Call (check summary)
    if "on-call" in summary or "on call" in summary:
        return "On-Call"

    # 2. Development (check label) - before upgrade check!
    if "tdi-caas-development" in labels:
        return "Development"

    # 3. Upgrades (check label or summary)
    if "tdi-caas-cluster-upgrade" in labels or "upgrade" in summary:
        return "Upgrades"

    # 4. Operations (check label)
    if "tdi-caas-operations" in labels:
        return "Operations"

    # 5. Other
    return "Other"


def group_issues_by_category(issues: list) -> dict:
    """Group issues into categories."""
    groups = {
        "On-Call": [],
        "Upgrades": [],
        "Development": [],
        "Operations": [],
        "Other": []
    }

    for issue in issues:
        category = get_issue_category(issue)
        groups[category].append(issue)

    return groups


def categorize_labels(labels: list) -> dict:
    """Count issues by category label."""
    counts = {"Ops": 0, "Dev": 0, "Upgrade": 0, "Other": 0}

    found = False
    for label in labels:
        if label in CATEGORY_LABELS:
            counts[CATEGORY_LABELS[label]] += 1
            found = True

    if not found:
        counts["Other"] += 1

    return counts


def render_jira_section(lines: list, section_title: str, issues: list, empty_message: str):
    """Render a Jira section with subsections grouped by category."""
    lines.append(f"## {section_title}")
    lines.append("")

    if not issues:
        lines.append(f"*{empty_message}*")
        lines.append("")
        return

    # Group by category
    groups = group_issues_by_category(issues)
    category_order = ["On-Call", "Development", "Upgrades", "Operations", "Other"]

    for category in category_order:
        category_issues = groups[category]
        if not category_issues:
            continue

        lines.append(f"### {category}")
        lines.append("")
        lines.append("| Key | Type | Summary | Assignee |")
        lines.append("|-----|------|---------|----------|")

        for issue in category_issues:
            key = issue["key"]
            fields = issue["fields"]
            itype = fields["issuetype"]["name"]
            summary = fields["summary"][:70] + "..." if len(fields["summary"]) > 70 else fields["summary"]
            assignee = fields["assignee"]["displayName"] if fields.get("assignee") else "-"
            lines.append(f"| {key} | {itype} | {summary} | {assignee} |")

        lines.append("")


def generate_markdown_report(
    completed_issues: list,
    in_progress_issues: list,
    refined_issues: list,
    merged_mrs: list,
    start_date: str,
    end_date: str
) -> str:
    """Generate the markdown report."""
    lines = []

    # Filter out epics
    completed_issues = [i for i in completed_issues if i["fields"]["issuetype"]["name"] != "Epic"]
    in_progress_issues = [i for i in in_progress_issues if i["fields"]["issuetype"]["name"] != "Epic"]
    refined_issues = [i for i in refined_issues if i["fields"]["issuetype"]["name"] != "Epic"]

    # Header
    lines.append("# TDI CaaS Team Review")
    lines.append(f"\n**Period:** {start_date} to {end_date}")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Summary (at top)
    lines.append("## Summary")
    lines.append("")

    # Count by category for completed issues
    completed_groups = group_issues_by_category(completed_issues)
    cat_counts = {cat: len(issues) for cat, issues in completed_groups.items() if issues}
    cat_str = ", ".join(f"{k}: {v}" for k, v in cat_counts.items())

    lines.append(f"- **Completed issues:** {len(completed_issues)} ({cat_str})")
    lines.append(f"- **In progress:** {len(in_progress_issues)}")
    lines.append(f"- **Refined (ready):** {len(refined_issues)}")
    lines.append(f"- **Merge requests merged:** {len(merged_mrs)}")
    lines.append("")

    # Jira sections with subsections
    render_jira_section(lines, "Jira - Completed Work", completed_issues, "No issues completed in this period.")
    render_jira_section(lines, "Jira - In Progress", in_progress_issues, "No issues currently in progress.")
    render_jira_section(lines, "Jira - Refined (Ready for Work)", refined_issues, "No refined issues in backlog.")

    # GitLab - Merged MRs grouped by project
    lines.append("## Merged Code Changes (GitLab)")
    lines.append("")

    if merged_mrs:
        # Group by project
        by_project = {}
        for mr in merged_mrs:
            project = mr.get("references", {}).get("full", "").split("!")[0].rstrip()
            if not project:
                project = mr.get("web_url", "").split("/-/")[0].split(".de/")[-1]
            if project not in by_project:
                by_project[project] = []
            by_project[project].append(mr)

        # Sort projects by MR count
        for project in sorted(by_project.keys(), key=lambda p: -len(by_project[p])):
            mrs = by_project[project]
            lines.append(f"### {project} ({len(mrs)} MRs)")
            lines.append("")
            lines.append("| MR | Title | Author | Merged |")
            lines.append("|----|-------|--------|--------|")
            for mr in mrs:
                iid = mr["iid"]
                title = mr["title"][:50] + "..." if len(mr["title"]) > 50 else mr["title"]
                author = mr["author"]["username"] if mr.get("author") else "-"
                merged_at = mr.get("merged_at", "")[:10] if mr.get("merged_at") else "-"
                lines.append(f"| !{iid} | {title} | {author} | {merged_at} |")
            lines.append("")
    else:
        lines.append("*No merge requests merged in this period.*")
        lines.append("")

    # Top Contributors (at the end)
    lines.append("## Top Contributors")
    lines.append("")

    # GitLab contributors
    mr_authors = Counter(mr["author"]["username"] for mr in merged_mrs if mr.get("author"))
    lines.append("### GitLab (MRs merged)")
    lines.append("")
    for author, count in mr_authors.most_common(10):
        lines.append(f"- {author}: {count}")
    lines.append("")

    # Jira contributors (from completed issues)
    jira_assignees = Counter(
        issue["fields"]["assignee"]["displayName"]
        for issue in completed_issues
        if issue["fields"].get("assignee")
    )
    if jira_assignees:
        lines.append("### Jira (issues completed)")
        lines.append("")
        for assignee, count in jira_assignees.most_common(10):
            lines.append(f"- {assignee}: {count}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate TDI CaaS team report")
    parser.add_argument("--days", type=int, default=14, help="Number of days to include (default: 14)")
    parser.add_argument("--output-dir", default="reports", help="Output directory (default: reports)")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF with Telekom branding")
    args = parser.parse_args()

    # Check tokens
    jira_token = os.environ.get("JIRA_API_TOKEN")
    gitlab_token = os.environ.get("GITLAB_API_TOKEN")

    if not jira_token:
        print("Error: JIRA_API_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not gitlab_token:
        print("Error: GITLAB_API_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"Generating report for {start_str} to {end_str}...")

    # Fetch Jira data
    print("Fetching Jira data...")

    completed_jql = f'project = {JIRA_PROJECT} AND status changed to (Closed, Done) DURING (-{args.days}d, now())'
    completed_issues = jira_search(completed_jql, jira_token)
    print(f"  - Completed issues: {len(completed_issues)}")

    in_progress_jql = f'project = {JIRA_PROJECT} AND status = "In Progress"'
    in_progress_issues = jira_search(in_progress_jql, jira_token)
    print(f"  - In Progress issues: {len(in_progress_issues)}")

    refined_jql = f'project = {JIRA_PROJECT} AND status = "Refined"'
    refined_issues = jira_search(refined_jql, jira_token)
    print(f"  - Refined issues: {len(refined_issues)}")

    # Fetch GitLab data
    print("Fetching GitLab data...")
    group_id = get_gitlab_group_id(gitlab_token)
    merged_mrs = get_merged_mrs(gitlab_token, start_str, group_id)
    print(f"  - Merged MRs: {len(merged_mrs)}")

    # Generate report
    print("Generating report...")
    report = generate_markdown_report(
        completed_issues,
        in_progress_issues,
        refined_issues,
        merged_mrs,
        start_str,
        end_str
    )

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write markdown
    md_file = output_dir / f"tdi-caas-report-{end_str}.md"
    md_file.write_text(report)
    print(f"Markdown report: {md_file}")

    # Generate PDF if requested
    if args.pdf:
        print("Generating PDF...")
        script_dir = Path(__file__).parent.parent.parent
        pdf_script = script_dir / "telekom-pdf" / "scripts" / "generate-pdf.py"

        if pdf_script.exists():
            pdf_file = output_dir / f"tdi-caas-report-{end_str}.pdf"
            result = subprocess.run([
                sys.executable,
                str(pdf_script),
                "--markdown", str(md_file),
                "--title", "TDI CaaS Team Review",
                "--output", str(pdf_file),
                "--landscape"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"PDF report: {pdf_file}")
            else:
                print(f"Warning: PDF generation failed: {result.stderr}", file=sys.stderr)
        else:
            print(f"Warning: PDF script not found at {pdf_script}", file=sys.stderr)

    print("Done!")


if __name__ == "__main__":
    main()
