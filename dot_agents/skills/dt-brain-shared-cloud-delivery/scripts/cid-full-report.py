#!/usr/bin/env python3
"""
Generate a comprehensive report on all open epics from the CID group.

Creates both Markdown and PDF output files with statistics and analysis.
Supports filtering by squad labels (e.g., --squad "A - CDM_squad,A - CaaS_squad").
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_error
from utils.assignee import get_assignee_name
from utils.output import format_date
from utils.config import DEFAULT_SQUAD_LABEL, VALID_SQUAD_LABELS, get_squad_display_name

try:
    from fpdf import FPDF
except ImportError:
    print("Error: fpdf2 not installed. Install with: pip install fpdf2", file=sys.stderr)
    sys.exit(1)


# Telekom brand colors
MAGENTA = (226, 0, 116)
DARK_GRAY = (51, 51, 51)
LIGHT_GRAY = (245, 245, 245)
WHITE = (255, 255, 255)


class TelekomPDF(FPDF):
    """Custom PDF class with Telekom branding."""

    def __init__(self, title="Document", orientation="P"):
        """
        Initialize TelekomPDF with branding.

        Args:
            title: Document title for header
            orientation: 'P' for portrait, 'L' for landscape
        """
        super().__init__(orientation=orientation)
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)
        font_dir = "/System/Library/Fonts/Supplemental/"
        self.add_font("Arial", "", font_dir + "Arial.ttf")
        self.add_font("Arial", "B", font_dir + "Arial Bold.ttf")
        self.add_font("Arial", "I", font_dir + "Arial Italic.ttf")
        self.add_font("Arial", "BI", font_dir + "Arial Bold Italic.ttf")

    def header(self):
        self.set_fill_color(*MAGENTA)
        self.rect(0, 0, self.w, 3, 'F')  # Use self.w for dynamic page width
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*DARK_GRAY)
        self.set_y(8)
        self.cell(0, 10, self.doc_title, align='L')
        self.set_font('Arial', '', 9)
        self.set_xy(-50, 8)
        self.cell(30, 10, datetime.now().strftime("%Y-%m-%d"), align='R')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 9)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_title_page(self, title, subtitle=None):
        self.add_page()
        self.set_fill_color(*MAGENTA)
        self.rect(0, 60, self.w, 50, 'F')  # Use self.w for dynamic page width
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*WHITE)
        self.set_y(70)
        self.multi_cell(0, 12, title, align='C')
        if subtitle:
            self.set_font('Arial', '', 14)
            self.set_y(95)
            self.cell(0, 10, subtitle, align='C')
        self.set_y(130)
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 10, 'TDI Cloud Infrastructure Delivery', align='C')
        self.set_y(145)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, datetime.now().strftime("%B %d, %Y"), align='C')

    def add_heading(self, text, level=1):
        self.ln(5)
        if self.get_y() + 30 > self.h - self.b_margin:
            self.add_page()
        table_width = self.w - 40  # Dynamic width based on page orientation
        if level == 1:
            self.set_font('Arial', 'B', 16)
            self.set_text_color(*MAGENTA)
            self.multi_cell(0, 10, text)
            self.set_fill_color(*MAGENTA)
            self.rect(20, self.get_y(), table_width, 0.5, 'F')
            self.ln(5)
        elif level == 2:
            self.set_font('Arial', 'B', 13)
            self.set_text_color(*MAGENTA)
            self.multi_cell(0, 8, text)
            self.ln(2)
        else:
            self.set_font('Arial', 'B', 11)
            self.set_text_color(*DARK_GRAY)
            self.multi_cell(0, 7, text)
            self.ln(2)
        self.set_text_color(*DARK_GRAY)

    def add_paragraph(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 5, text)
        self.ln(3)

    def add_table(self, headers, rows, col_widths=None):
        if not rows:
            return
        table_width = self.w - 40  # Dynamic width based on page orientation
        if col_widths is None:
            col_widths = [table_width / len(headers)] * len(headers)

        # Header
        self.set_fill_color(*MAGENTA)
        self.set_text_color(*WHITE)
        self.set_font('Arial', 'B', 9)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, str(header)[:30], border=1, fill=True, align='C')
        self.ln()

        # Rows
        self.set_text_color(*DARK_GRAY)
        self.set_font('Arial', '', 9)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(*LIGHT_GRAY)
            else:
                self.set_fill_color(*WHITE)
            for i, cell in enumerate(row):
                max_chars = int(col_widths[i] / 1.8)  # Slightly more chars per width
                cell_text = str(cell)[:max_chars] if len(str(cell)) > max_chars else str(cell)
                self.cell(col_widths[i], 6, cell_text, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)


def discover_squad_labels():
    """
    Discover squad labels from GitLab by fetching all labels from the CID group.

    Returns:
        dict: Mapping of squad label to display name for labels matching 'A - *_squad'
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    discovered = {}
    try:
        labels = group.labels.list(per_page=100, get_all=True)
        for label in labels:
            name = label.name
            if name.startswith("A - ") and name.endswith("_squad"):
                # Generate display name from label
                display_name = name.replace("A - ", "").replace("_squad", " Squad").replace("_", " ")
                discovered[name] = display_name
    except Exception as e:
        print(f"Warning: Could not discover labels: {e}", file=sys.stderr)

    return discovered


def validate_squad_labels(squad_labels: list[str]) -> list[str]:
    """
    Validate squad labels against predefined list, falling back to auto-discovery.

    Args:
        squad_labels: List of squad labels to validate

    Returns:
        List of validated squad labels

    Raises:
        ValueError: If any label is not valid
    """
    validated = []
    unknown = []

    for label in squad_labels:
        label = label.strip()
        if label in VALID_SQUAD_LABELS:
            validated.append(label)
        else:
            unknown.append(label)

    # Try to validate unknown labels via discovery
    if unknown:
        discovered = discover_squad_labels()
        for label in unknown:
            if label in discovered:
                validated.append(label)
                # Add to runtime known labels
                VALID_SQUAD_LABELS[label] = discovered[label]
            else:
                raise ValueError(
                    f"Unknown squad label: '{label}'. "
                    f"Valid labels: {', '.join(sorted(VALID_SQUAD_LABELS.keys()))}"
                )

    return validated



# Assignee/delivery manager parsing moved to utils.assignee module
# This function is now imported and reused across scripts


def fetch_all_epics(squad_labels: list[str], limit=500):
    """
    Fetch all open epics from CID parent group only (no subgroups), filtered by squad labels.

    Args:
        squad_labels: List of squad labels to filter by (joined with comma for GitLab API)
        limit: Maximum number of epics to fetch

    Returns:
        List of epic objects
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    # GitLab API accepts comma-separated labels (AND logic)
    # For OR logic across squads, we need to fetch separately and merge
    # But for simplicity, if multiple squads, use the first one (most common use case)
    # For true multi-squad reports, we'd need multiple API calls

    all_epics = []
    seen_iids = set()

    for label in squad_labels:
        params = {
            "state": "opened",
            "include_descendant_groups": False,  # Parent group only
            "labels": label,
            "per_page": 100,
        }

        page = 1
        while len(all_epics) < limit:
            epics = group.epics.list(**params, page=page, get_all=False)
            if not epics:
                break
            for epic in epics:
                if epic.iid not in seen_iids:
                    all_epics.append(epic)
                    seen_iids.add(epic.iid)
            page += 1
            if len(epics) < 100:
                break

    return all_epics[:limit]


def build_hierarchy(epics):
    """Build epic hierarchy map and classify epics."""
    epic_map = {e.iid: e for e in epics}

    # Classify epics
    parent_iids = set()
    child_epics = []

    for e in epics:
        parent_iid = getattr(e, 'parent_iid', None)
        if parent_iid:
            child_epics.append(e)
            parent_iids.add(parent_iid)

    # Umbrella epics are those that have children (whether open or closed parent)
    umbrella_epics = [e for e in epics if e.iid in parent_iids]
    standalone_epics = [e for e in epics if e.iid not in parent_iids and not getattr(e, 'parent_iid', None)]

    # Build parent->children map
    children_by_parent = defaultdict(list)
    for e in epics:
        parent_iid = getattr(e, 'parent_iid', None)
        if parent_iid:
            children_by_parent[parent_iid].append(e)

    return {
        'epic_map': epic_map,
        'umbrella_epics': umbrella_epics,
        'child_epics': child_epics,
        'standalone_epics': standalone_epics,
        'children_by_parent': dict(children_by_parent),
        'parent_iids': parent_iids,
    }


def analyze_epics(epics):
    """Analyze epic data and return statistics."""
    # Build hierarchy first
    hierarchy = build_hierarchy(epics)

    stats = {
        "total": len(epics),
        "status": Counter(),
        "squads": Counter(),
        "priorities": Counter(),
        "environments": Counter(),
        "work_categories": Counter(),
        "with_due_date": 0,
        "overdue": [],
        "due_this_month": [],
        "no_labels": [],
        "no_squad": [],
        "epics_by_status": defaultdict(list),
        # Hierarchy data
        "hierarchy": hierarchy,
        "umbrella_count": len(hierarchy['umbrella_epics']),
        "child_count": len(hierarchy['child_epics']),
        "standalone_count": len(hierarchy['standalone_epics']),
    }

    today = datetime.now().strftime("%Y-%m-%d")
    end_of_month = "2026-02-28"

    for epic in epics:
        labels = getattr(epic, "labels", [])

        # Status
        status_found = False
        for label in labels:
            if "epic::" in label:
                stats["status"][label] += 1
                stats["epics_by_status"][label].append(epic)
                status_found = True
        if not status_found:
            stats["epics_by_status"]["No Status"].append(epic)

        # Squads
        squad_found = False
        for label in labels:
            if label.startswith("A - ") and "squad" in label.lower():
                stats["squads"][label] += 1
                squad_found = True
        if not squad_found:
            stats["no_squad"].append(epic)

        # Priorities
        for label in labels:
            if label.startswith("D - "):
                stats["priorities"][label] += 1

        # Environments
        for label in labels:
            if label.startswith("E - "):
                stats["environments"][label] += 1

        # Work categories
        for label in labels:
            if label.startswith("I - "):
                stats["work_categories"][label] += 1

        # No labels
        if not labels:
            stats["no_labels"].append(epic)

        # Due dates
        due_date = getattr(epic, "due_date", None)
        if due_date:
            stats["with_due_date"] += 1
            if due_date < today:
                stats["overdue"].append(epic)
            elif due_date <= end_of_month:
                stats["due_this_month"].append(epic)

    return stats


def generate_markdown_report(epics, stats, squad_labels: list[str]):
    """Generate markdown content for the report."""
    lines = []
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Generate title based on squads
    squad_names = [get_squad_display_name(label) for label in squad_labels]
    if len(squad_names) == 1:
        title = f"TDI Cloud Delivery - {squad_names[0]} Open Epics Report"
    else:
        title = f"TDI Cloud Delivery - Multi-Squad Open Epics Report"

    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Generated:** {today}")
    lines.append(f"**Source:** GitLab cit-iaas/cid group")
    lines.append(f"**Squads:** {', '.join(squad_names)}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"The CID group currently has **{stats['total']} open epics** tracking datacenter deployments and infrastructure work.")
    lines.append("")

    # Key Metrics
    lines.append("### Key Metrics")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Open Epics | {stats['total']} |")
    lines.append(f"| Epics with Due Dates | {stats['with_due_date']} |")
    lines.append(f"| Overdue Epics | {len(stats['overdue'])} |")
    lines.append(f"| Due This Month (Feb 2026) | {len(stats['due_this_month'])} |")
    lines.append(f"| Epics Without Squad Assignment | {len(stats['no_squad'])} |")
    lines.append(f"| Epics Without Any Labels | {len(stats['no_labels'])} |")
    lines.append(f"| **Umbrella Epics (with children)** | {stats['umbrella_count']} |")
    lines.append(f"| **Child Epics (under umbrella)** | {stats['child_count']} |")
    lines.append(f"| Standalone Epics | {stats['standalone_count']} |")
    lines.append("")

    # Status Distribution
    lines.append("## Epic Status Distribution")
    lines.append("")
    lines.append("| Status | Count | % |")
    lines.append("|--------|-------|---|")
    for status, count in sorted(stats["status"].items()):
        pct = round(count / stats["total"] * 100, 1)
        lines.append(f"| {status} | {count} | {pct}% |")
    no_status = len(stats["epics_by_status"].get("No Status", []))
    if no_status:
        pct = round(no_status / stats["total"] * 100, 1)
        lines.append(f"| (No Status Label) | {no_status} | {pct}% |")
    lines.append("")

    # Squad Workload
    lines.append("## Squad Workload")
    lines.append("")
    lines.append("| Squad | Epic Count |")
    lines.append("|-------|------------|")
    for squad, count in sorted(stats["squads"].items(), key=lambda x: -x[1]):
        lines.append(f"| {squad} | {count} |")
    lines.append(f"| (Unassigned) | {len(stats['no_squad'])} |")
    lines.append("")

    # Epic Hierarchy (Umbrella Epics)
    hierarchy = stats['hierarchy']
    if hierarchy['umbrella_epics']:
        lines.append("## 🏛️ Epic Hierarchy (Umbrella Epics)")
        lines.append("")

        # Sort umbrella epics by number of children
        umbrella_with_counts = []
        for ue in hierarchy['umbrella_epics']:
            children = hierarchy['children_by_parent'].get(ue.iid, [])
            umbrella_with_counts.append((ue, len(children)))
        umbrella_with_counts.sort(key=lambda x: -x[1])

        for umbrella, child_count in umbrella_with_counts:
            labels = getattr(umbrella, "labels", [])
            status = next((l.replace("B - epic::", "") for l in labels if "epic::" in l), "-")
            squad = next((l.replace("A - ", "") for l in labels if "squad" in l.lower()), "-")

            lines.append(f"### 📁 Epic {umbrella.iid}: {umbrella.title}")
            lines.append("")
            lines.append(f"- **Status:** {status}")
            lines.append(f"- **Squad:** {squad}")
            lines.append(f"- **Due Date:** {getattr(umbrella, 'due_date', '-') or '-'}")
            lines.append(f"- **Children:** {child_count} epic(s)")
            lines.append("")

            children = hierarchy['children_by_parent'].get(umbrella.iid, [])
            if children:
                lines.append("| Child IID | Title | Status | Due Date |")
                lines.append("|-----------|-------|--------|----------|")
                for child in sorted(children, key=lambda c: getattr(c, 'due_date', None) or '9999-99-99'):
                    c_labels = getattr(child, "labels", [])
                    c_status = next((l.replace("B - epic::", "") for l in c_labels if "epic::" in l), "-")
                    c_due = getattr(child, 'due_date', '-') or '-'
                    lines.append(f"| {child.iid} | {child.title} | {c_status} | {c_due} |")
                lines.append("")
        lines.append("")

    # Priority Distribution
    if stats["priorities"]:
        lines.append("## Priority Distribution")
        lines.append("")
        lines.append("| Priority | Count |")
        lines.append("|----------|-------|")
        for prio, count in sorted(stats["priorities"].items()):
            lines.append(f"| {prio} | {count} |")
        lines.append("")

    # Environment Distribution
    if stats["environments"]:
        lines.append("## Top Environments (by epic count)")
        lines.append("")
        lines.append("| Environment | Epic Count |")
        lines.append("|-------------|------------|")
        for env, count in sorted(stats["environments"].items(), key=lambda x: -x[1])[:20]:
            lines.append(f"| {env} | {count} |")
        lines.append("")

    # Work Categories
    if stats["work_categories"]:
        lines.append("## Work Categories")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, count in sorted(stats["work_categories"].items(), key=lambda x: -x[1]):
            lines.append(f"| {cat} | {count} |")
        lines.append("")

    # Overdue Epics
    if stats["overdue"]:
        lines.append("## ⚠️ Overdue Epics")
        lines.append("")
        lines.append("| IID | Title | Due Date | Squad | Assignee |")
        lines.append("|-----|-------|----------|-------|----------|")
        for epic in sorted(stats["overdue"], key=lambda e: getattr(e, "due_date", "")):
            labels = getattr(epic, "labels", [])
            squad = next((l for l in labels if "squad" in l.lower()), "-")
            assignee = get_assignee_name(epic)
            lines.append(f"| {epic.iid} | {epic.title} | {getattr(epic, 'due_date', '-')} | {squad} | {assignee} |")
        lines.append("")

    # Due This Month
    if stats["due_this_month"]:
        lines.append("## 📅 Due This Month (February 2026)")
        lines.append("")
        lines.append("| IID | Title | Due Date | Status | Assignee |")
        lines.append("|-----|-------|----------|--------|----------|")
        for epic in sorted(stats["due_this_month"], key=lambda e: getattr(e, "due_date", "")):
            labels = getattr(epic, "labels", [])
            status = next((l for l in labels if "epic::" in l), "-")
            assignee = get_assignee_name(epic)
            lines.append(f"| {epic.iid} | {epic.title} | {getattr(epic, 'due_date', '-')} | {status} | {assignee} |")
        lines.append("")

    # Epics In Progress
    doing_epics = stats["epics_by_status"].get("B - epic::Doing", [])
    if doing_epics:
        lines.append("## 🔄 Epics In Progress (Doing)")
        lines.append("")
        lines.append("| IID | Title | Squad | Due Date | Assignee |")
        lines.append("|-----|-------|-------|----------|----------|")
        for epic in doing_epics:
            labels = getattr(epic, "labels", [])
            squad = next((l.replace("A - ", "") for l in labels if "squad" in l.lower()), "-")
            due = getattr(epic, "due_date", "-") or "-"
            assignee = get_assignee_name(epic)
            lines.append(f"| {epic.iid} | {epic.title} | {squad} | {due} | {assignee} |")
        lines.append("")

    # Full Epic List (all open epics)
    lines.append("## 📋 All Open Epics")
    lines.append("")
    lines.append("| IID | Title | State | Due Date | Squad | Status | Assignee |")
    lines.append("|-----|-------|-------|----------|-------|--------|----------|")
    for epic in sorted(epics, key=lambda e: (getattr(e, "due_date", None) or "9999-99-99")):
        labels = getattr(epic, "labels", [])
        squad = next((l.replace("A - ", "") for l in labels if "squad" in l.lower()), "-")
        status = next((l.replace("B - epic::", "") for l in labels if "epic::" in l), "-")
        due = getattr(epic, "due_date", "-") or "-"
        assignee = get_assignee_name(epic)
        lines.append(f"| {epic.iid} | {epic.title} | {epic.state} | {due} | {squad} | {status} | {assignee} |")
    lines.append("")

    # Analysis Section
    lines.append("## Analysis & Observations")
    lines.append("")

    # Calculate insights
    total = stats["total"]
    doing_count = stats["status"].get("B - epic::Doing", 0)
    backlog_count = stats["status"].get("B - epic::Backlog", 0)
    refinement_count = stats["status"].get("B - epic::Refinement", 0)
    todo_count = stats["status"].get("B - epic::ToDo", 0)

    lines.append("### Status Flow Analysis")
    lines.append("")
    lines.append(f"- **Active Work:** {doing_count} epics ({round(doing_count/total*100, 1)}%) are currently in implementation")
    lines.append(f"- **Pipeline:** {todo_count + refinement_count} epics in pre-implementation stages (ToDo + Refinement)")
    lines.append(f"- **Backlog:** {backlog_count} epics waiting in backlog")
    lines.append("")

    lines.append("### Risk Indicators")
    lines.append("")
    overdue_pct = round(len(stats['overdue']) / total * 100, 1) if total > 0 else 0
    no_squad_pct = round(len(stats['no_squad']) / total * 100, 1) if total > 0 else 0

    if len(stats['overdue']) > 0:
        lines.append(f"- ⚠️ **{len(stats['overdue'])} overdue epics** ({overdue_pct}%) require immediate attention")
    if len(stats['no_squad']) > 10:
        lines.append(f"- ⚠️ **{len(stats['no_squad'])} epics without squad assignment** ({no_squad_pct}%) may lack ownership")
    if len(stats['no_labels']) > 0:
        lines.append(f"- ⚠️ **{len(stats['no_labels'])} epics have no labels** - tracking and filtering is limited")

    lines.append("")
    lines.append("### Squad Capacity")
    lines.append("")
    if stats["squads"]:
        top_squad = max(stats["squads"].items(), key=lambda x: x[1])
        lines.append(f"- **Highest workload:** {top_squad[0]} with {top_squad[1]} epics")
        avg_per_squad = round(sum(stats["squads"].values()) / len(stats["squads"]), 1)
        lines.append(f"- **Average per squad:** {avg_per_squad} epics")
    lines.append("")

    return "\n".join(lines)


def generate_pdf_report(epics, stats, output_path, title, squad_labels: list[str]):
    """Generate PDF report in landscape orientation for better table display."""
    # Use landscape orientation ('L') for wider tables
    pdf = TelekomPDF(title=title, orientation='L')
    pdf.add_title_page(title, f"{stats['total']} Open Epics")
    pdf.add_page()

    # Page width for landscape A4: 297mm, usable width with margins: ~257mm
    table_width = pdf.w - 40  # Dynamic based on orientation

    # Executive Summary
    pdf.add_heading("Executive Summary", 1)
    squad_names = [get_squad_display_name(label) for label in squad_labels]
    pdf.add_paragraph(
        f"This report covers {', '.join(squad_names)}. "
        f"Currently tracking {stats['total']} open epics for datacenter deployments "
        f"and infrastructure work as of {datetime.now().strftime('%Y-%m-%d')}."
    )

    # Key Metrics Table
    pdf.add_heading("Key Metrics", 2)
    metrics_rows = [
        ["Total Open Epics", str(stats['total'])],
        ["Epics with Due Dates", str(stats['with_due_date'])],
        ["Overdue Epics", str(len(stats['overdue']))],
        ["Due This Month", str(len(stats['due_this_month']))],
        ["Without Squad Assignment", str(len(stats['no_squad']))],
        ["Umbrella Epics", str(stats['umbrella_count'])],
        ["Child Epics", str(stats['child_count'])],
        ["Standalone Epics", str(stats['standalone_count'])],
    ]
    pdf.add_table(["Metric", "Count"], metrics_rows, [120, 80])

    # Status Distribution
    pdf.add_heading("Epic Status Distribution", 2)
    status_rows = []
    for status, count in sorted(stats["status"].items()):
        pct = f"{round(count / stats['total'] * 100, 1)}%"
        status_rows.append([status.replace("B - epic::", ""), str(count), pct])
    pdf.add_table(["Status", "Count", "%"], status_rows, [100, 50, 50])

    # Squad Workload
    pdf.add_heading("Squad Workload", 2)
    squad_rows = []
    for squad, count in sorted(stats["squads"].items(), key=lambda x: -x[1])[:10]:
        squad_rows.append([squad.replace("A - ", ""), str(count)])
    pdf.add_table(["Squad", "Epic Count"], squad_rows, [140, 60])

    # Epic Hierarchy
    hierarchy = stats['hierarchy']
    if hierarchy['umbrella_epics']:
        pdf.add_page()
        pdf.add_heading("Epic Hierarchy (Umbrella Epics)", 1)

        # Summary table of umbrella epics
        pdf.add_heading("Umbrella Epics Overview", 2)
        umbrella_rows = []
        umbrella_with_counts = []
        for ue in hierarchy['umbrella_epics']:
            children = hierarchy['children_by_parent'].get(ue.iid, [])
            umbrella_with_counts.append((ue, len(children)))
        umbrella_with_counts.sort(key=lambda x: -x[1])

        for umbrella, child_count in umbrella_with_counts:
            labels = getattr(umbrella, "labels", [])
            status = next((l.replace("B - epic::", "") for l in labels if "epic::" in l), "-")
            # Wider title field in landscape mode
            title = umbrella.title[:80] + "..." if len(umbrella.title) > 80 else umbrella.title
            umbrella_rows.append([str(umbrella.iid), title, str(child_count), status])
        pdf.add_table(["IID", "Umbrella Epic", "Children", "Status"], umbrella_rows, [20, 160, 25, 52])

    # Overdue Epics
    if stats["overdue"]:
        pdf.add_heading("Overdue Epics (Attention Required)", 2)
        overdue_rows = []
        for epic in sorted(stats["overdue"], key=lambda e: getattr(e, "due_date", "")):
            # Full title in landscape mode
            title = epic.title[:100] + "..." if len(epic.title) > 100 else epic.title
            assignee = get_assignee_name(epic)[:20]
            overdue_rows.append([str(epic.iid), title, getattr(epic, "due_date", "-"), assignee])
        pdf.add_table(["IID", "Title", "Due Date", "Assignee"], overdue_rows, [20, 160, 35, 42])

    # Due This Month
    if stats["due_this_month"]:
        pdf.add_heading("Due This Month (February 2026)", 2)
        due_rows = []
        for epic in sorted(stats["due_this_month"], key=lambda e: getattr(e, "due_date", "")):
            title = epic.title[:100] + "..." if len(epic.title) > 100 else epic.title
            assignee = get_assignee_name(epic)[:20]
            due_rows.append([str(epic.iid), title, getattr(epic, "due_date", "-"), assignee])
        pdf.add_table(["IID", "Title", "Due Date", "Assignee"], due_rows, [20, 160, 35, 42])

    # All Epics In Progress
    doing_epics = stats["epics_by_status"].get("B - epic::Doing", [])
    if doing_epics:
        pdf.add_page()
        pdf.add_heading("Epics In Progress (Doing)", 2)
        doing_rows = []
        for epic in doing_epics:
            labels = getattr(epic, "labels", [])
            squad = next((l.replace("A - ", "") for l in labels if "squad" in l.lower()), "-")
            title = epic.title[:90] + "..." if len(epic.title) > 90 else epic.title
            assignee = get_assignee_name(epic)[:20]
            doing_rows.append([str(epic.iid), title, squad[:18], assignee])
        pdf.add_table(["IID", "Title", "Squad", "Assignee"], doing_rows, [20, 150, 45, 42])

    # Full Epic List
    pdf.add_page()
    pdf.add_heading("Complete Epic List", 1)
    pdf.add_paragraph(f"All {len(epics)} open epics sorted by due date:")
    all_rows = []
    for epic in sorted(epics, key=lambda e: (getattr(e, "due_date", None) or "9999-99-99")):
        labels = getattr(epic, "labels", [])
        squad = next((l.replace("A - ", "")[:15] for l in labels if "squad" in l.lower()), "-")
        title = epic.title[:85] + "..." if len(epic.title) > 85 else epic.title
        due = getattr(epic, "due_date", "-") or "-"
        assignee = get_assignee_name(epic)[:20]
        all_rows.append([str(epic.iid), title, due, squad, assignee])
    pdf.add_table(["IID", "Title", "Due", "Squad", "Assignee"], all_rows, [18, 130, 30, 40, 39])

    # Analysis
    pdf.add_page()
    pdf.add_heading("Analysis & Recommendations", 1)

    total = stats["total"]
    doing_count = stats["status"].get("B - epic::Doing", 0)

    pdf.add_heading("Current Status", 2)
    pdf.add_paragraph(
        f"Of the {total} open epics, {doing_count} ({round(doing_count/total*100, 1)}%) are actively "
        f"in implementation. There are {len(stats['overdue'])} overdue epics that require immediate attention."
    )

    if len(stats['overdue']) > 5:
        pdf.add_heading("Risk: Overdue Deliveries", 3)
        pdf.add_paragraph(
            f"With {len(stats['overdue'])} overdue epics, there is a significant backlog of delayed work. "
            f"Recommend reviewing these epics to update timelines or reallocate resources."
        )

    if len(stats['no_squad']) > 10:
        pdf.add_heading("Risk: Unassigned Work", 3)
        pdf.add_paragraph(
            f"{len(stats['no_squad'])} epics lack squad assignment, representing "
            f"{round(len(stats['no_squad'])/total*100, 1)}% of all open work. "
            f"These should be assigned to ensure accountability."
        )

    # Save PDF
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)


def generate_output_filename(squad_labels: list[str], base_date: str) -> str:
    """
    Generate output filename based on squad labels.

    Args:
        squad_labels: List of squad labels
        base_date: Date string for the filename (YYYY-MM-DD)

    Returns:
        Filename without extension (e.g., "cid-cdm-caas-report-2026-02-03")
    """
    # Extract short squad names from labels
    short_names = []
    for label in squad_labels:
        # "A - CDM_squad" -> "cdm"
        name = label.replace("A - ", "").replace("_squad", "").lower()
        short_names.append(name)

    if len(short_names) == 1:
        return f"reports/cid-{short_names[0]}-report-{base_date}"
    elif len(short_names) <= 3:
        return f"reports/cid-{'-'.join(short_names)}-report-{base_date}"
    else:
        return f"reports/cid-multi-squad-report-{base_date}"


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive CID epics report")
    parser.add_argument(
        "--squad",
        default=DEFAULT_SQUAD_LABEL,
        help=f"Squad label(s) to filter by, comma-separated (default: {DEFAULT_SQUAD_LABEL}). "
             f"Example: --squad 'A - CDM_squad,A - CaaS_squad'"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (without extension). Auto-generated from squad names if not specified."
    )
    parser.add_argument("--title", default=None, help="Report title (auto-generated if not specified)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum epics to fetch")

    args = parser.parse_args()

    # Parse squad labels
    squad_labels = [s.strip() for s in args.squad.split(",")]

    # Validate squad labels
    try:
        squad_labels = validate_squad_labels(squad_labels)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate squad display names for output
    squad_names = [get_squad_display_name(label) for label in squad_labels]
    squad_display = ", ".join(squad_names)

    print(f"Fetching open epics for: {squad_display}")
    epics = fetch_all_epics(squad_labels, args.limit)
    print(f"Found {len(epics)} open epics.")

    print("Analyzing data...")
    stats = analyze_epics(epics)

    # Generate output path
    today = datetime.now().strftime("%Y-%m-%d")
    if args.output:
        output_base = args.output
    else:
        output_base = generate_output_filename(squad_labels, today)

    # Generate title
    if args.title:
        title = args.title
    elif len(squad_names) == 1:
        title = f"TDI Cloud Delivery - {squad_names[0]} Open Epics Report"
    else:
        title = f"TDI Cloud Delivery - Multi-Squad Open Epics Report"

    # Generate Markdown
    md_path = f"{output_base}.md"
    print(f"Generating Markdown report: {md_path}")
    md_content = generate_markdown_report(epics, stats, squad_labels)
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w") as f:
        f.write(md_content)

    # Generate PDF
    pdf_path = f"{output_base}.pdf"
    print(f"Generating PDF report: {pdf_path}")
    generate_pdf_report(epics, stats, pdf_path, title, squad_labels)

    print(f"\nReports generated:")
    print(f"  - {md_path}")
    print(f"  - {pdf_path}")

    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Squads: {squad_display}")
    print(f"Total open epics: {stats['total']}")
    print(f"Overdue: {len(stats['overdue'])}")
    print(f"Due this month: {len(stats['due_this_month'])}")
    print(f"Without squad: {len(stats['no_squad'])}")


if __name__ == "__main__":
    main()
