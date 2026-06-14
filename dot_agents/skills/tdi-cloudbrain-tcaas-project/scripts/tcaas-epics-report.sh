#!/usr/bin/env bash
# TCAAS Epics Report Generator
# Generates a markdown (and optionally PDF) report for TCAAS epics
# filtered by labels, showing assigned/unassigned task breakdowns.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
REPO_ROOT="$(cd "$CLAUDE_DIR/.." && pwd)"
PDF_SCRIPT="$CLAUDE_DIR/skills/telekom-pdf/scripts/generate-pdf.py"
PYTHON_PATH="$REPO_ROOT/.venv/bin/python"

# Defaults
LABELS="Create_Operate_Management_Clusters,Create_Migrate_Workload_Clusters"
OUTPUT_DIR="reports"
GENERATE_PDF=false
INCLUDE_CLOSED=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --labels)
            LABELS="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --pdf)
            GENERATE_PDF=true
            shift
            ;;
        --include-closed)
            INCLUDE_CLOSED=true
            shift
            ;;
        --help|-h)
            echo "Usage: $(basename "$0") [OPTIONS]"
            echo ""
            echo "Generate TCAAS epics status report."
            echo ""
            echo "Options:"
            echo "  --labels <l1,l2>     Labels to filter epics (default: Create_Operate_Management_Clusters,Create_Migrate_Workload_Clusters)"
            echo "  --output-dir <dir>   Output directory (default: reports/)"
            echo "  --pdf                Also generate PDF with Telekom branding"
            echo "  --include-closed     Include Closed/Done issues"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Error: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate token
if [[ -z "${JIRA_API_TOKEN:-}" ]]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set." >&2
    echo "Set it with: export JIRA_API_TOKEN='your-token'" >&2
    exit 1
fi

# Validate python
if [[ ! -x "$PYTHON_PATH" ]]; then
    PYTHON_PATH="$(command -v python3 2>/dev/null || true)"
    if [[ -z "$PYTHON_PATH" ]]; then
        echo "Error: Python 3 not found." >&2
        exit 1
    fi
fi

# Resolve output dir relative to project root
if [[ "$OUTPUT_DIR" != /* ]]; then
    OUTPUT_DIR="$REPO_ROOT/$OUTPUT_DIR"
fi
mkdir -p "$OUTPUT_DIR"

MD_OUTPUT="$OUTPUT_DIR/tcaas-epics-report.md"
PDF_OUTPUT="$OUTPUT_DIR/tcaas-epics-report.pdf"

echo "Generating TCAAS Epics Report..."
echo "  Labels: $LABELS"
echo "  Include closed: $INCLUDE_CLOSED"

# Run Python to fetch data and generate report
"$PYTHON_PATH" << 'PYTHON_SCRIPT' - "$JIRA_API_TOKEN" "$LABELS" "$INCLUDE_CLOSED" "$MD_OUTPUT"
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from collections import defaultdict

JIRA_TOKEN = sys.argv[1]
LABELS = sys.argv[2].split(",")
INCLUDE_CLOSED = sys.argv[3].lower() == "true"
MD_OUTPUT = sys.argv[4]

BASE_URL = "https://jira.telekom.de"
HEADERS = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Content-Type": "application/json"
}

CLOSED_STATUSES = {"Closed", "Done"}


def jira_get(url):
    """Make a GET request to Jira API."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  Warning: HTTP {e.code} for {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Warning: {e} for {url}", file=sys.stderr)
        return None


def fetch_epics(labels, include_closed):
    """Fetch epics matching the given labels."""
    label_conditions = " OR ".join(f'labels = "{l}"' for l in labels)
    jql = f"project = TCAAS AND issuetype = Epic AND ({label_conditions})"
    if not include_closed:
        jql += " AND status not in (Closed, Done)"
    jql += " ORDER BY labels ASC, status ASC"

    encoded_jql = urllib.parse.quote(jql, safe="")
    url = f"{BASE_URL}/rest/api/2/search?jql={encoded_jql}&maxResults=100&fields=summary,labels,status,assignee"
    data = jira_get(url)
    if not data:
        return []
    return data.get("issues", [])


def fetch_epic_children(epic_key, include_closed):
    """Fetch child issues of an epic via the Agile API."""
    url = f"{BASE_URL}/rest/agile/1.0/epic/{epic_key}/issue?maxResults=100&fields=summary,status,assignee,issuetype"
    data = jira_get(url)
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
        "\u2014": "-",  # em dash
        "\u2013": "-",  # en dash
        "\u00fc": "ue", # u umlaut
        "\u00e4": "ae", # a umlaut
        "\u00f6": "oe", # o umlaut
        "\u00dc": "Ue", # U umlaut
        "\u00c4": "Ae", # A umlaut
        "\u00d6": "Oe", # O umlaut
        "\u00df": "ss", # eszett
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


# --- Fetch data ---
print("  Fetching epics...")
raw_epics = fetch_epics(LABELS, INCLUDE_CLOSED)
print(f"  Found {len(raw_epics)} epics")

# Organize epics by label
epics_by_label = defaultdict(list)
epic_info = {}  # key -> {summary, status, owner, labels}
all_children = {}  # epic_key -> [child issues]

for epic in raw_epics:
    key = epic["key"]
    fields = epic["fields"]
    summary = fields.get("summary", "").strip()
    status = fields.get("status", {}).get("name", "Unknown")
    owner = get_assignee_name(fields)
    labels = fields.get("labels", [])

    epic_info[key] = {
        "summary": summary,
        "status": status,
        "owner": owner,
        "labels": labels
    }

    for label in LABELS:
        if label in labels:
            epics_by_label[label].append(key)

print("  Fetching child issues per epic...")
for key in epic_info:
    children = fetch_epic_children(key, INCLUDE_CLOSED)
    all_children[key] = children
    print(f"    {key}: {len(children)} children")

# --- Classify tasks ---
assigned_by_person = defaultdict(list)  # person -> [(task_key, type, status, epic_key, summary)]
unassigned_by_epic = defaultdict(list)  # epic_key -> [(task_key, type, status, summary)]
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

# Sort persons by task count descending
sorted_persons = sorted(assigned_by_person.keys(), key=lambda p: len(assigned_by_person[p]), reverse=True)

total_assigned = sum(len(v) for v in assigned_by_person.values())
total_unassigned = sum(len(v) for v in unassigned_by_epic.values())
total_tasks = total_assigned + total_unassigned

# --- Generate markdown ---
today = datetime.now().strftime("%Y-%m-%d")
lines = []

lines.append("# TCAAS Epics Report - Create & Operate Management / Workload Clusters")
lines.append("")
lines.append(f"**Generated:** {today}")
lines.append("")
lines.append("This report covers non-closed epics under the labels " +
             ", ".join(f"`{l}`" for l in LABELS) +
             ", their child issues grouped by assignee, and all unassigned tasks.")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Epic Overview")
lines.append("")

for label in LABELS:
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

# --- Write markdown ---
md_content = "\n".join(lines)

with open(MD_OUTPUT, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"  Markdown report written to: {MD_OUTPUT}")

# Also write a PDF-safe version (sanitized for non-ASCII)
pdf_safe_path = MD_OUTPUT.replace(".md", ".pdf-safe.md")
with open(pdf_safe_path, "w", encoding="utf-8") as f:
    f.write(sanitize_for_pdf(md_content))

print(f"  PDF-safe markdown written to: {pdf_safe_path}")
PYTHON_SCRIPT

echo "  Markdown report: $MD_OUTPUT"

# Generate PDF if requested
if [[ "$GENERATE_PDF" == "true" ]]; then
    PDF_SAFE_MD="${MD_OUTPUT%.md}.pdf-safe.md"
    if [[ -f "$PDF_SCRIPT" ]]; then
        echo "  Generating PDF..."
        "$PYTHON_PATH" "$PDF_SCRIPT" --markdown "$PDF_SAFE_MD" --title "TCAAS Epics Report" --output "$PDF_OUTPUT"
        echo "  PDF report: $PDF_OUTPUT"
        # Clean up temp file
        rm -f "$PDF_SAFE_MD"
    else
        echo "  Warning: PDF script not found at $PDF_SCRIPT" >&2
        echo "  Skipping PDF generation." >&2
    fi
else
    # Clean up temp file if not generating PDF
    rm -f "${MD_OUTPUT%.md}.pdf-safe.md"
fi

echo "Done."
