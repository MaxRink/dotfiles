#!/usr/bin/env python3
"""
Generate a PDF deployment status report from CID epics and issues.

Usage:
    cid-deployment-report.py [options]

Options:
    --state STATE     Epic state filter: opened (default), closed, all
    --labels LABELS   Filter epics by comma-separated labels
    --output PATH     Output PDF path (default: deployment-report-YYYY-MM-DD.pdf)
    --title TITLE     Report title (default: "TDI Cloud Delivery Status Report")
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_gitlab_client, get_cid_group, print_error
from utils.output import format_date
from utils.validators import validate_state

# Import fpdf2 for PDF generation
try:
    from fpdf import FPDF
except ImportError:
    print("Error: fpdf2 not installed. Install with: pip install fpdf2", file=sys.stderr)
    sys.exit(1)


# Telekom brand colors
MAGENTA = (226, 0, 116)  # #e20074
DARK_GRAY = (51, 51, 51)  # #333333
LIGHT_GRAY = (245, 245, 245)  # #f5f5f5
WHITE = (255, 255, 255)


class TelekomPDF(FPDF):
    """Custom PDF class with Telekom branding."""

    def __init__(self, title="Document", template="documentation"):
        super().__init__()
        self.doc_title = title
        self.template = template
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)
        # Register a Unicode font so non-ASCII characters render correctly
        font_dir = "/System/Library/Fonts/Supplemental/"
        self.add_font("Arial", "", font_dir + "Arial.ttf")
        self.add_font("Arial", "B", font_dir + "Arial Bold.ttf")
        self.add_font("Arial", "I", font_dir + "Arial Italic.ttf")
        self.add_font("Arial", "BI", font_dir + "Arial Bold Italic.ttf")

    def header(self):
        """Page header with magenta accent."""
        self.set_fill_color(*MAGENTA)
        self.rect(0, 0, 210, 3, 'F')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*DARK_GRAY)
        self.set_y(8)
        self.cell(0, 10, self.doc_title, align='L')
        self.set_font('Arial', '', 9)
        self.set_xy(-50, 8)
        self.cell(30, 10, datetime.now().strftime("%Y-%m-%d"), align='R')
        self.ln(15)

    def footer(self):
        """Page footer with page numbers."""
        self.set_y(-15)
        self.set_font('Arial', '', 9)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_title_page(self, title, subtitle=None):
        """Add a styled title page."""
        self.add_page()
        self.set_fill_color(*MAGENTA)
        self.rect(0, 60, 210, 50, 'F')
        self.set_font('Arial', 'B', 28)
        self.set_text_color(*WHITE)
        self.set_y(75)
        self.multi_cell(0, 12, title, align='C')
        if subtitle:
            self.set_font('Arial', '', 14)
            self.set_y(95)
            self.cell(0, 10, subtitle, align='C')
        self.set_y(130)
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 10, 'Deployment Status Report', align='C')
        self.set_y(145)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, datetime.now().strftime("%B %d, %Y"), align='C')
        self.set_text_color(*DARK_GRAY)

    def add_heading(self, text, level=1):
        """Add a heading with appropriate styling."""
        self.ln(5)
        if self.get_y() + 30 > self.h - self.b_margin:
            self.add_page()
        if level == 1:
            self.set_font('Arial', 'B', 18)
            self.set_text_color(*MAGENTA)
            self.multi_cell(0, 10, text)
            self.set_fill_color(*MAGENTA)
            self.rect(20, self.get_y(), 170, 0.5, 'F')
            self.ln(5)
        elif level == 2:
            self.set_font('Arial', 'B', 14)
            self.set_text_color(*MAGENTA)
            self.multi_cell(0, 8, text)
            self.ln(2)
        else:
            self.set_font('Arial', 'B', 12)
            self.set_text_color(*DARK_GRAY)
            self.multi_cell(0, 7, text)
            self.ln(2)
        self.set_text_color(*DARK_GRAY)

    def add_paragraph(self, text):
        """Add a paragraph of text."""
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def add_table(self, headers, rows):
        """Add a simple table."""
        if not rows:
            return
        table_width = 170
        col_count = len(headers)
        col_width = table_width / col_count

        # Header
        self.set_fill_color(*MAGENTA)
        self.set_text_color(*WHITE)
        self.set_font('Arial', 'B', 9)
        for header in headers:
            self.cell(col_width, 7, str(header)[:20], border=1, fill=True, align='C')
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
                self.cell(col_width, 6, str(cell)[:25], border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)

    def add_horizontal_rule(self):
        """Add a horizontal rule."""
        self.ln(3)
        self.set_fill_color(*LIGHT_GRAY)
        self.rect(20, self.get_y(), 170, 0.5, 'F')
        self.ln(6)


def fetch_epics_with_issues(state="opened", labels=None, limit=50):
    """
    Fetch epics and their linked issues.

    Args:
        state: Epic state filter
        labels: Comma-separated labels
        limit: Maximum epics to fetch

    Returns:
        list: List of dicts with epic and issues data
    """
    gl = get_gitlab_client()
    group = get_cid_group(gl)

    params = {
        "include_descendant_groups": True,
        "per_page": min(limit, 100),
    }

    if state != "all":
        params["state"] = state

    if labels:
        params["labels"] = labels

    try:
        epics = group.epics.list(**params)

        results = []
        for epic in epics[:limit]:
            # Fetch issues for this epic
            try:
                issues = list(epic.issues.list(per_page=100))
            except Exception:
                issues = []

            results.append({
                "epic": epic,
                "issues": issues,
            })

        return results

    except Exception as e:
        print_error(f"Failed to fetch epics: {e}")
        sys.exit(1)


def calculate_progress(issues):
    """Calculate progress from issues."""
    if not issues:
        return {"total": 0, "closed": 0, "open": 0, "percent": 0}

    total = len(issues)
    closed = sum(1 for i in issues if i.state == "closed")
    open_count = total - closed
    percent = round((closed / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "closed": closed,
        "open": open_count,
        "percent": percent,
    }


def generate_markdown_report(epics_data, title):
    """
    Generate markdown content for the report.

    Args:
        epics_data: List of epic/issues dicts
        title: Report title

    Returns:
        str: Markdown content
    """
    lines = []

    # Executive Summary
    lines.append("# Executive Summary")
    lines.append("")

    total_epics = len(epics_data)
    total_issues = sum(len(e["issues"]) for e in epics_data)
    total_closed = sum(
        sum(1 for i in e["issues"] if i.state == "closed")
        for e in epics_data
    )
    overall_progress = round((total_closed / total_issues) * 100) if total_issues > 0 else 0

    lines.append(f"This report covers **{total_epics} epics** with a total of **{total_issues} issues**.")
    lines.append(f"Overall completion: **{overall_progress}%** ({total_closed}/{total_issues} issues closed).")
    lines.append("")
    lines.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Summary Table
    lines.append("## Epics Overview")
    lines.append("")
    lines.append("| Epic | State | Progress | Start | Due |")
    lines.append("|------|-------|----------|-------|-----|")

    for data in epics_data:
        epic = data["epic"]
        progress = calculate_progress(data["issues"])
        title_short = epic.title[:40] + "..." if len(epic.title) > 40 else epic.title
        progress_str = f"{progress['percent']}% ({progress['closed']}/{progress['total']})"
        start = format_date(getattr(epic, "start_date", None)) or "-"
        due = format_date(getattr(epic, "due_date", None)) or "-"

        lines.append(f"| {title_short} | {epic.state} | {progress_str} | {start} | {due} |")

    lines.append("")

    # Detailed Epic Sections
    lines.append("# Epic Details")
    lines.append("")

    for data in epics_data:
        epic = data["epic"]
        issues = data["issues"]
        progress = calculate_progress(issues)

        # Epic header
        lines.append(f"## {epic.title}")
        lines.append("")

        # Epic metadata
        lines.append(f"**State:** {epic.state}")
        lines.append(f"**Progress:** {progress['percent']}% ({progress['closed']}/{progress['total']} issues)")

        start = format_date(getattr(epic, "start_date", None))
        due = format_date(getattr(epic, "due_date", None))
        if start or due:
            lines.append(f"**Timeline:** {start or 'TBD'} → {due or 'TBD'}")

        epic_labels = getattr(epic, "labels", [])
        if epic_labels:
            lines.append(f"**Labels:** {', '.join(epic_labels)}")

        lines.append("")

        # Epic description (truncated)
        description = getattr(epic, "description", None)
        if description:
            desc_lines = description.split("\n")[:5]  # First 5 lines
            desc_text = "\n".join(desc_lines)
            if len(description.split("\n")) > 5:
                desc_text += "\n..."
            lines.append(desc_text)
            lines.append("")

        # Issues table
        if issues:
            lines.append("### Issues")
            lines.append("")
            lines.append("| IID | Title | State | Assignee | Due |")
            lines.append("|-----|-------|-------|----------|-----|")

            for issue in issues[:20]:  # Limit to 20 issues per epic
                title_short = issue.title[:35] + "..." if len(issue.title) > 35 else issue.title

                assignees = getattr(issue, "assignees", [])
                assignee = assignees[0].get("username", "-") if assignees else "-"

                due = format_date(getattr(issue, "due_date", None)) or "-"

                lines.append(f"| {issue.iid} | {title_short} | {issue.state} | {assignee} | {due} |")

            if len(issues) > 20:
                lines.append(f"| ... | *{len(issues) - 20} more issues* | | | |")

            lines.append("")
        else:
            lines.append("*No issues linked to this epic.*")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate deployment status PDF report")
    parser.add_argument("--state", default="opened", help="Epic state filter: opened, closed, all")
    parser.add_argument("--labels", help="Filter epics by comma-separated labels")
    parser.add_argument("--output", help="Output PDF path")
    parser.add_argument("--title", default="TDI Cloud Delivery Status Report", help="Report title")
    parser.add_argument("--limit", type=int, default=50, help="Maximum epics to include")

    args = parser.parse_args()

    # Validate inputs
    state = validate_state(args.state)

    # Default output path
    if not args.output:
        date_str = datetime.now().strftime("%Y-%m-%d")
        args.output = f"deployment-report-{date_str}.pdf"

    print(f"Fetching epics from cit-iaas/cid (state={state})...")

    # Fetch data
    epics_data = fetch_epics_with_issues(
        state=state,
        labels=args.labels,
        limit=args.limit,
    )

    if not epics_data:
        print("No epics found matching the criteria.")
        sys.exit(0)

    print(f"Found {len(epics_data)} epics. Generating report...")

    # Generate PDF directly
    try:
        pdf = TelekomPDF(title=args.title, template="documentation")
        pdf.add_title_page(args.title)
        pdf.add_page()

        # Executive Summary
        pdf.add_heading("Executive Summary", 1)
        total_epics = len(epics_data)
        total_issues = sum(len(e["issues"]) for e in epics_data)
        total_closed = sum(
            sum(1 for i in e["issues"] if i.state == "closed")
            for e in epics_data
        )
        overall_progress = round((total_closed / total_issues) * 100) if total_issues > 0 else 0

        pdf.add_paragraph(
            f"This report covers {total_epics} epics with a total of {total_issues} issues. "
            f"Overall completion: {overall_progress}% ({total_closed}/{total_issues} issues closed). "
            f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        # Epics Overview Table
        pdf.add_heading("Epics Overview", 2)
        headers = ["Epic", "State", "Progress", "Start", "Due"]
        rows = []
        for data in epics_data:
            epic = data["epic"]
            progress = calculate_progress(data["issues"])
            title_short = epic.title[:25] + "..." if len(epic.title) > 25 else epic.title
            progress_str = f"{progress['percent']}%"
            start = format_date(getattr(epic, "start_date", None)) or "-"
            due = format_date(getattr(epic, "due_date", None)) or "-"
            rows.append([title_short, epic.state, progress_str, start, due])
        pdf.add_table(headers, rows)

        # Detailed sections for each epic
        pdf.add_heading("Epic Details", 1)
        for data in epics_data:
            epic = data["epic"]
            issues = data["issues"]
            progress = calculate_progress(issues)

            pdf.add_heading(epic.title[:60], 2)

            meta = f"State: {epic.state} | Progress: {progress['percent']}% ({progress['closed']}/{progress['total']} issues)"
            start = format_date(getattr(epic, "start_date", None))
            due = format_date(getattr(epic, "due_date", None))
            if start or due:
                meta += f" | Timeline: {start or 'TBD'} - {due or 'TBD'}"
            pdf.add_paragraph(meta)

            epic_labels = getattr(epic, "labels", [])
            if epic_labels:
                pdf.add_paragraph(f"Labels: {', '.join(epic_labels[:5])}")

            # Issues table for this epic
            if issues:
                pdf.add_heading("Issues", 3)
                issue_headers = ["IID", "Title", "State", "Assignee"]
                issue_rows = []
                for issue in issues[:10]:
                    title_short = issue.title[:20] + "..." if len(issue.title) > 20 else issue.title
                    assignees = getattr(issue, "assignees", [])
                    assignee = assignees[0].get("username", "-")[:15] if assignees else "-"
                    issue_rows.append([issue.iid, title_short, issue.state, assignee])
                pdf.add_table(issue_headers, issue_rows)
                if len(issues) > 10:
                    pdf.add_paragraph(f"... and {len(issues) - 10} more issues")
            else:
                pdf.add_paragraph("No issues linked to this epic.")

            pdf.add_horizontal_rule()

        # Ensure output directory exists
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        pdf.output(args.output)
        print(f"Report generated: {args.output}")
    except Exception as e:
        print_error(f"Failed to generate PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
