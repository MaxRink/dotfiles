#!/usr/bin/env python3
"""
TCAAS Epics Report Generator
Generates a markdown (and optionally PDF) report for TCAAS epics
filtered by labels, showing assigned/unassigned task breakdowns.

Usage: tcaas-epics-report.py [--labels L1,L2] [--output-dir DIR] [--pdf] [--include-closed]
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime


BASE_URL = "https://jira.telekom.de"
CLOSED_STATUSES = {"Closed", "Done"}
DEFAULT_LABELS = "Create_Operate_Management_Clusters,Create_Migrate_Workload_Clusters"


def get_headers():
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not token:
        print("Error: JIRA_API_TOKEN environment variable is not set.", file=sys.stderr)
        print("Set it with: export JIRA_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def jira_get(url, headers):
    """Make a GET request to Jira API."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  Warning: HTTP {e.code} for {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Warning: {e} for {url}", file=sys.stderr)
        return None


def fetch_epics(labels, include_closed, headers):
    """Fetch epics matching the given labels."""
    label_conditions = " OR ".join(f'labels = "{l}"' for l in labels)
    jql = f"project = TCAAS AND issuetype = Epic AND ({label_conditions})"
    if not include_closed:
        jql += " AND status not in (Closed, Done)"
    jql += " ORDER BY labels ASC, status ASC"

    encoded_jql = urllib.parse.quote(jql, safe="")
    url = f"{BASE_URL}/rest/api/2/search?jql={encoded_jql}&maxResults=100&fields=summary,labels,status,assignee"
    data = jira_get(url, headers)
    if not data:
        return []
    return data.get("issues", [])


def fetch_epic_children(epic_key, include_closed, headers):
    """Fetch child issues of an epic via the Agile API."""
    url = f"{BASE_URL}/rest/agile/1.0/epic/{epic_key}/issue?maxResults=100&fields=summary,status,assignee,issuetype"
    data = jira_get(url, headers)
    if not data:
        return []
    issues = data.get("issues", [])
    if not include_closed:
        issues = [i for i in issues if i["fields"].get("status", {}).get("name", "") not in CLOSED_STATUSES]
    return issues


def get_assignee_name(fields):
    """Extract assignee display name."""
    assignee = fields.get("assignee")
    if assignee:
        return assignee.get("displayName", "Unassigned")
    return "Unassigned"


def sanitize_for_pdf(text):
    """Replace non-ASCII characters for PDF compatibility."""
    replacements = {
        "\u2014": "-",   # em dash
        "\u2013": "-",   # en dash
        "\u00fc": "ue",  # u umlaut
        "\u00e4": "ae",  # a umlaut
        "\u00f6": "oe",  # o umlaut
        "\u00dc": "Ue",  # U umlaut
        "\u00c4": "Ae",  # A umlaut
        "\u00d6": "Oe",  # O umlaut
        "\u00df": "ss",  # eszett
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


def generate_report(labels, include_closed, headers):
    """Fetch data from Jira and generate markdown report content."""
    print("  Fetching epics...")
    raw_epics = fetch_epics(labels, include_closed, headers)
    print(f"  Found {len(raw_epics)} epics")

    # Organize epics by label
    epics_by_label = defaultdict(list)
    epic_info = {}
    all_children = {}

    for epic in raw_epics:
        key = epic["key"]
        fields = epic["fields"]
        summary = fields.get("summary", "").strip()
        status = fields.get("status", {}).get("name", "Unknown")
        owner = get_assignee_name(fields)
        elabels = fields.get("labels", [])

        epic_info[key] = {
            "summary": summary,
            "status": status,
            "owner": owner,
            "labels": elabels,
        }

        for label in labels:
            if label in elabels:
                epics_by_label[label].append(key)

    print("  Fetching child issues per epic...")
    for key in epic_info:
        children = fetch_epic_children(key, include_closed, headers)
        all_children[key] = children
        print(f"    {key}: {len(children)} children")

    # Classify tasks
    assigned_by_person = defaultdict(list)
    unassigned_by_epic = defaultdict(list)
    empty_epics = []

    for epic_key, children in all_children.items():
        if not children:
            empty_epics.append(epic_key)
        for child in children:
            ckey = child["key"]
            cf = child["fields"]
            csummary = cf.get("summary", "").strip()
            cstatus = cf.get("status", {}).get("name", "Unknown")
            ctype = cf.get("issuetype", {}).get("name", "Task")
            cassignee = get_assignee_name(cf)

            if cassignee == "Unassigned":
                unassigned_by_epic[epic_key].append((ckey, ctype, cstatus, csummary))
            else:
                assigned_by_person[cassignee].append((ckey, ctype, cstatus, epic_key, csummary))

    sorted_persons = sorted(assigned_by_person.keys(), key=lambda p: len(assigned_by_person[p]), reverse=True)

    total_assigned = sum(len(v) for v in assigned_by_person.values())
    total_unassigned = sum(len(v) for v in unassigned_by_epic.values())
    total_tasks = total_assigned + total_unassigned

    # Generate markdown
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    lines.append("# TCAAS Epics Report - Create & Operate Management / Workload Clusters")
    lines.append("")
    lines.append(f"**Generated:** {today}")
    lines.append("")
    lines.append("This report covers non-closed epics under the labels " +
                 ", ".join(f"`{l}`" for l in labels) +
                 ", their child issues grouped by assignee, and all unassigned tasks.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Epic Overview")
    lines.append("")

    for label in labels:
        epic_keys = epics_by_label.get(label, [])
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Key | Status | Summary | Epic Owner |")
        lines.append("|-----|--------|---------|------------|")
        for ek in epic_keys:
            info = epic_info[ek]
            lines.append(f"| {ek} | {info['status']} | {info['summary']} | {info['owner']} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Assigned Tasks - By Person")
    lines.append("")

    for person in sorted_persons:
        tasks = assigned_by_person[person]
        lines.append(f"### {person} ({len(tasks)} task{'s' if len(tasks) != 1 else ''})")
        lines.append("")
        lines.append("| Key | Type | Status | Epic | Summary |")
        lines.append("|-----|------|--------|------|---------|")
        for ckey, ctype, cstatus, epic_key, csummary in tasks:
            einfo = epic_info.get(epic_key, {})
            epic_short = f"{epic_key} ({einfo.get('summary', '')[:30]} - {einfo.get('owner', '')})"
            lines.append(f"| {ckey} | {ctype} | {cstatus} | {epic_short} | {csummary} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## Unassigned Tasks ({total_unassigned} tasks)")
    lines.append("")

    for epic_key in epic_info:
        utasks = unassigned_by_epic.get(epic_key, [])
        if not utasks:
            continue
        einfo = epic_info[epic_key]
        lines.append(f"### {epic_key} - {einfo['summary']} ({einfo['owner']}) - {len(utasks)} task{'s' if len(utasks) != 1 else ''}")
        lines.append("")
        lines.append("| Key | Type | Status | Summary |")
        lines.append("|-----|------|--------|---------|")
        for ckey, ctype, cstatus, csummary in utasks:
            lines.append(f"| {ckey} | {ctype} | {cstatus} | {csummary} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total non-closed epics | {len(epic_info)} |")
    lines.append(f"| Total non-closed child tasks | {total_tasks} |")
    lines.append(f"| Assigned tasks | {total_assigned} |")
    pct = f"{total_unassigned / total_tasks * 100:.0f}%" if total_tasks > 0 else "0%"
    lines.append(f"| Unassigned tasks | {total_unassigned} ({pct}) |")
    lines.append(f"| Epics with zero child issues | {len(empty_epics)} ({', '.join(empty_epics) if empty_epics else 'none'}) |")
    lines.append("")

    if empty_epics:
        lines.append("### Epics with no child issues")
        lines.append("")
        lines.append("These epics have no tasks broken down yet:")
        lines.append("")
        for ek in empty_epics:
            einfo = epic_info[ek]
            lines.append(f"- **{ek}** - {einfo['summary']} ({einfo['owner']})")
        lines.append("")

    lines.append("### Workload distribution")
    lines.append("")
    lines.append("| Person | Assigned Tasks | Epics Involved |")
    lines.append("|--------|---------------|----------------|")
    for person in sorted_persons:
        tasks = assigned_by_person[person]
        epic_keys_involved = sorted(set(t[3] for t in tasks))
        lines.append(f"| {person} | {len(tasks)} | {', '.join(epic_keys_involved)} |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate TCAAS epics status report.")
    parser.add_argument("--labels", default=DEFAULT_LABELS,
                        help=f"Labels to filter epics (default: {DEFAULT_LABELS})")
    parser.add_argument("--output-dir", default="reports",
                        help="Output directory (default: reports/)")
    parser.add_argument("--pdf", action="store_true",
                        help="Also generate PDF with Telekom branding")
    parser.add_argument("--include-closed", action="store_true",
                        help="Include Closed/Done issues")
    args = parser.parse_args()

    headers = get_headers()
    labels = [l.strip() for l in args.labels.split(",")]

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    claude_dir = os.path.dirname(os.path.dirname(skill_dir))  # .claude
    repo_root = os.path.dirname(claude_dir)
    pdf_script = os.path.join(claude_dir, "skills", "telekom-pdf", "scripts", "generate-pdf.py")

    output_dir = args.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(repo_root, output_dir)
    os.makedirs(output_dir, exist_ok=True)

    md_output = os.path.join(output_dir, "tcaas-epics-report.md")
    pdf_output = os.path.join(output_dir, "tcaas-epics-report.pdf")

    print("Generating TCAAS Epics Report...")
    print(f"  Labels: {args.labels}")
    print(f"  Include closed: {args.include_closed}")

    md_content = generate_report(labels, args.include_closed, headers)

    with open(md_output, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Markdown report written to: {md_output}")

    # Handle PDF generation
    pdf_safe_path = md_output.replace(".md", ".pdf-safe.md")
    if args.pdf:
        with open(pdf_safe_path, "w", encoding="utf-8") as f:
            f.write(sanitize_for_pdf(md_content))

        if os.path.exists(pdf_script):
            print("  Generating PDF...")
            python_path = os.path.join(repo_root, ".venv", "bin", "python")
            if not os.path.isfile(python_path):
                python_path = sys.executable
            subprocess.run(
                [python_path, pdf_script, "--markdown", pdf_safe_path,
                 "--title", "TCAAS Epics Report", "--output", pdf_output],
                check=True,
            )
            print(f"  PDF report: {pdf_output}")
        else:
            print(f"  Warning: PDF script not found at {pdf_script}", file=sys.stderr)
            print("  Skipping PDF generation.", file=sys.stderr)

        # Clean up temp file
        if os.path.exists(pdf_safe_path):
            os.remove(pdf_safe_path)
    else:
        # Clean up any leftover temp file
        if os.path.exists(pdf_safe_path):
            os.remove(pdf_safe_path)

    print("Done.")


if __name__ == "__main__":
    main()
