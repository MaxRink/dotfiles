#!/usr/bin/env python3
"""
PDF Generation Script with Telekom Branding

Generates consistently styled PDF documents for technical documentation.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Ensure we can import fpdf2
try:
    from fpdf import FPDF
except ImportError:
    print("Error: fpdf2 not installed. Install with: pip install fpdf2", file=sys.stderr)
    sys.exit(1)


# Telekom brand colors
MAGENTA = (226, 0, 116)  # #e20074
DARK_GRAY = (51, 51, 51)  # #333333
LIGHT_GRAY = (245, 245, 245)  # #f5f5f5
CODE_BG = (240, 240, 240)  # #f0f0f0
WHITE = (255, 255, 255)


class TelekomPDF(FPDF):
    """Custom PDF class with Telekom branding."""

    def __init__(self, title="Document", template="documentation", orientation="portrait"):
        super().__init__(orientation=orientation[0].upper())  # 'P' or 'L'
        self.doc_title = title
        self.template = template
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)
        # Register a Unicode font so non-ASCII characters (ü, č, ö, etc.) render correctly
        font_dir = "/System/Library/Fonts/Supplemental/"
        self.add_font("Arial", "", font_dir + "Arial.ttf")
        self.add_font("Arial", "B", font_dir + "Arial Bold.ttf")
        self.add_font("Arial", "I", font_dir + "Arial Italic.ttf")
        self.add_font("Arial", "BI", font_dir + "Arial Bold Italic.ttf")

    def header(self):
        """Page header with magenta accent."""
        # Magenta line at top (full page width)
        self.set_fill_color(*MAGENTA)
        self.rect(0, 0, self.w, 3, 'F')

        # Title on header
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*DARK_GRAY)
        self.set_y(8)
        self.cell(0, 10, self.doc_title, align='L')

        # Date on right
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

        # Get page width for dynamic sizing
        page_w = self.w

        # Large magenta block (full width)
        self.set_fill_color(*MAGENTA)
        self.rect(0, 60, page_w, 50, 'F')

        # Title text (white on magenta)
        self.set_font('Arial', 'B', 28)
        self.set_text_color(*WHITE)
        self.set_y(75)
        self.multi_cell(0, 12, title, align='C')

        # Subtitle if provided
        if subtitle:
            self.set_font('Arial', '', 14)
            self.set_y(95)
            self.cell(0, 10, subtitle, align='C')

        # Template badge
        self.set_y(130)
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        template_labels = {
            'documentation': 'Technical Documentation',
            'howto': 'How-To Guide',
            'release-notes': 'Release Notes',
            'architecture': 'Architecture Document'
        }
        self.cell(0, 10, template_labels.get(self.template, 'Document'), align='C')

        # Date
        self.set_y(145)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, datetime.now().strftime("%B %d, %Y"), align='C')

        # Reset text color
        self.set_text_color(*DARK_GRAY)

    def add_heading(self, text, level=1):
        """Add a heading with appropriate styling."""
        self.ln(5)

        # Prevent orphan headings: ensure space for heading + some content
        min_space = 30  # mm for heading + at least some content
        if self.get_y() + min_space > self.h - self.b_margin:
            self.add_page()

        if level == 1:
            self.set_font('Arial', 'B', 18)
            self.set_text_color(*MAGENTA)
            self.multi_cell(0, 10, text)
            # Underline
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
        self.multi_cell(0, 6, text, markdown=True)
        self.ln(3)

    def add_bullet_list(self, items):
        """Add a bulleted list."""
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        for item in items:
            self.set_x(25)
            self.cell(5, 6, "\u2022")  # Bullet character
            self.multi_cell(0, 6, item, markdown=True)
        self.ln(3)

    def add_numbered_list(self, items):
        """Add a numbered list."""
        self.set_font('Arial', '', 11)
        self.set_text_color(*DARK_GRAY)
        for i, item in enumerate(items, 1):
            self.set_x(25)
            self.cell(8, 6, f"{i}.")
            self.multi_cell(0, 6, item, markdown=True)
        self.ln(3)

    def add_code_block(self, code):
        """Add a code block with background."""
        self.set_fill_color(*CODE_BG)
        self.set_font('Courier', '', 9)
        self.set_text_color(*DARK_GRAY)

        # Calculate height needed
        lines = code.split('\n')
        height = len(lines) * 5 + 6

        # Draw background
        y_start = self.get_y()
        self.rect(20, y_start, 170, height, 'F')

        # Add code text
        self.set_xy(23, y_start + 3)
        for line in lines:
            self.cell(0, 5, line[:100])  # Truncate long lines
            self.ln(5)
            self.set_x(23)

        self.ln(5)
        self.set_font('Arial', '', 11)

    def add_inline_code(self, text):
        """Format inline code within text."""
        # This is a simplified version - inline code handling
        return text

    def add_table(self, headers, rows):
        """Add a table with magenta header and text wrapping."""
        # Dynamic table width based on page orientation
        table_width = self.w - self.l_margin - self.r_margin
        col_widths = self._calc_col_widths(headers, rows, table_width)
        line_h = 6

        # Ensure space for header + at least one data row
        self.set_font('Arial', 'B', 10)
        header_h = max(8, self._calc_row_height(headers, col_widths, line_h))
        self.set_font('Arial', '', 10)
        first_row_h = self._calc_row_height(rows[0], col_widths, line_h) if rows else 0
        if self.get_y() + header_h + first_row_h > self.h - self.b_margin:
            self.add_page()

        # Header row
        self.set_fill_color(*MAGENTA)
        self.set_text_color(*WHITE)
        self.set_font('Arial', 'B', 10)
        row_h = max(8, self._calc_row_height(headers, col_widths, line_h))
        self._draw_table_row(headers, col_widths, row_h, line_h, fill=True, align='C')

        # Data rows
        self.set_text_color(*DARK_GRAY)
        self.set_font('Arial', '', 10)
        fill = False

        for row in rows:
            if fill:
                self.set_fill_color(*LIGHT_GRAY)
            else:
                self.set_fill_color(*WHITE)

            row_h = self._calc_row_height(row, col_widths, line_h)
            self._draw_table_row(row, col_widths, row_h, line_h, fill=True)
            fill = not fill

        self.ln(5)

    def _calc_col_widths(self, headers, rows, table_width):
        """Calculate column widths: compact columns get natural width, wide columns share the rest."""
        num_cols = len(headers)
        if num_cols == 0:
            return []

        self.set_font('Arial', '', 10)
        # Calculate natural width needed for single-line content
        natural = []
        for col_idx in range(num_cols):
            max_w = self.get_string_width(str(headers[col_idx]))
            for row in rows:
                if col_idx < len(row):
                    w = self.get_string_width(str(row[col_idx]))
                    max_w = max(max_w, w)
            natural.append(max_w + 4)  # padding

        total_natural = sum(natural)
        if total_natural <= table_width:
            # Everything fits on single lines
            scale = table_width / total_natural
            return [w * scale for w in natural]

        # Split into compact (fit on one line) vs wide (need wrapping)
        threshold = table_width * 0.25
        compact = [i for i, w in enumerate(natural) if w <= threshold]
        wide = [i for i, w in enumerate(natural) if w > threshold]

        if not wide or not compact:
            return [(w / total_natural) * table_width for w in natural]

        compact_total = sum(natural[i] for i in compact)
        remaining = table_width - compact_total
        if remaining <= 0:
            return [(w / total_natural) * table_width for w in natural]

        wide_total = sum(natural[i] for i in wide)
        widths = [0.0] * num_cols
        for i in compact:
            widths[i] = natural[i]
        for i in wide:
            widths[i] = (natural[i] / wide_total) * remaining

        return widths

    def _calc_row_height(self, cells, col_widths, line_h):
        """Calculate row height based on text wrapping."""
        max_lines = 1
        for i, cell_text in enumerate(cells):
            if i >= len(col_widths):
                break
            text = str(cell_text)
            cell_w = col_widths[i] - 2  # padding
            if cell_w <= 0:
                continue
            # Word-wrap line count
            lines = 1
            words = text.split()
            current_line = ""
            for word in words:
                test = current_line + (" " if current_line else "") + word
                if self.get_string_width(test) > cell_w and current_line:
                    lines += 1
                    current_line = word
                else:
                    current_line = test
            max_lines = max(max_lines, lines)
        return max_lines * line_h + 2  # vertical padding

    def _draw_table_row(self, cells, col_widths, row_h, line_h, fill=False, align='L'):
        """Draw a table row with multi-line cell support."""
        x_start = self.get_x()
        y_start = self.get_y()

        # Page break check
        if y_start + row_h > self.h - self.b_margin:
            self.add_page()
            y_start = self.get_y()
            x_start = self.get_x()

        # Disable auto page break so multi_cell doesn't split a row across pages
        self.set_auto_page_break(auto=False)

        x_offset = 0
        for i, cell_text in enumerate(cells):
            if i >= len(col_widths):
                break
            w = col_widths[i]
            x = x_start + x_offset

            # Draw cell rectangle (fill + border)
            self.rect(x, y_start, w, row_h, 'DF' if fill else 'D')

            # Write text inside cell
            self.set_xy(x + 1, y_start + 1)
            self.multi_cell(w - 2, line_h, str(cell_text), align=align)

            x_offset += w

        # Restore auto page break and move to next row
        self.set_auto_page_break(auto=True, margin=25)
        self.set_xy(x_start, y_start + row_h)

    def add_horizontal_rule(self):
        """Add a horizontal rule."""
        self.ln(3)
        self.set_fill_color(*LIGHT_GRAY)
        self.rect(20, self.get_y(), 170, 0.5, 'F')
        self.ln(6)


def parse_markdown(content):
    """Parse markdown content into structured elements."""
    elements = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headers
        if line.startswith('### '):
            elements.append(('h3', line[4:].strip()))
        elif line.startswith('## '):
            elements.append(('h2', line[3:].strip()))
        elif line.startswith('# '):
            elements.append(('h1', line[2:].strip()))

        # Code blocks
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            elements.append(('code', '\n'.join(code_lines)))

        # Horizontal rule
        elif line.strip() in ['---', '***', '___']:
            elements.append(('hr', None))

        # Bullet lists
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            items = [line.strip()[2:]]
            i += 1
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                items.append(lines[i].strip()[2:])
                i += 1
            elements.append(('bullets', items))
            i -= 1

        # Numbered lists
        elif re.match(r'^\d+\.\s', line.strip()):
            items = [re.sub(r'^\d+\.\s*', '', line.strip())]
            i += 1
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(re.sub(r'^\d+\.\s*', '', lines[i].strip()))
                i += 1
            elements.append(('numbered', items))
            i -= 1

        # Tables
        elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            headers = [cell.strip() for cell in line.split('|')[1:-1]]
            i += 2  # Skip header and separator
            rows = []
            while i < len(lines) and '|' in lines[i]:
                row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                rows.append(row)
                i += 1
            elements.append(('table', (headers, rows)))
            i -= 1

        # Regular paragraph
        elif line.strip():
            para_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('```') and not lines[i].startswith('-') and not lines[i].startswith('*') and not re.match(r'^\d+\.', lines[i]):
                para_lines.append(lines[i])
                i += 1
            elements.append(('paragraph', ' '.join(para_lines)))
            i -= 1

        i += 1

    return elements


def generate_pdf(title, content=None, markdown_file=None, template='documentation', output=None, orientation='portrait'):
    """Generate a PDF document."""

    # Create PDF
    pdf = TelekomPDF(title=title, template=template, orientation=orientation)

    # Add title page
    pdf.add_title_page(title)

    # Start content page
    pdf.add_page()

    # Get content
    if markdown_file:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif not content:
        # Use template content
        content = get_template_content(template, title)

    # Parse and render content
    elements = parse_markdown(content)

    for elem_type, elem_content in elements:
        if elem_type == 'h1':
            pdf.add_heading(elem_content, 1)
        elif elem_type == 'h2':
            pdf.add_heading(elem_content, 2)
        elif elem_type == 'h3':
            pdf.add_heading(elem_content, 3)
        elif elem_type == 'paragraph':
            pdf.add_paragraph(elem_content)
        elif elem_type == 'bullets':
            pdf.add_bullet_list(elem_content)
        elif elem_type == 'numbered':
            pdf.add_numbered_list(elem_content)
        elif elem_type == 'code':
            pdf.add_code_block(elem_content)
        elif elem_type == 'table':
            headers, rows = elem_content
            pdf.add_table(headers, rows)
        elif elem_type == 'hr':
            pdf.add_horizontal_rule()

    # Determine output path
    if not output:
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        output = f"docs/{slug}.pdf"

    # Ensure output directory exists
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # Save PDF
    pdf.output(output)
    print(f"PDF generated: {output}")
    return output


def get_template_content(template, title):
    """Get template content based on template type."""

    templates = {
        'documentation': f"""# {title}

## Overview

This document provides technical documentation for the system.

## Prerequisites

- Requirement 1
- Requirement 2
- Requirement 3

## Architecture

Describe the system architecture here.

## Configuration

### Basic Configuration

Add configuration details here.

```yaml
# Example configuration
key: value
```

## Usage

Describe how to use the system.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Error A | Fix A |
| Error B | Fix B |

## References

- Reference 1
- Reference 2
""",

        'howto': f"""# {title}

## Introduction

This guide explains how to accomplish a specific task.

## Prerequisites

Before you begin, ensure you have:

- Prerequisite 1
- Prerequisite 2
- Prerequisite 3

## Steps

### Step 1: First Action

Description of the first step.

```bash
# Example command
echo "Step 1"
```

### Step 2: Second Action

Description of the second step.

### Step 3: Third Action

Description of the third step.

## Verification

To verify the procedure completed successfully:

1. Check item 1
2. Check item 2
3. Check item 3

## Troubleshooting

If you encounter issues:

- **Problem A**: Solution A
- **Problem B**: Solution B

## Next Steps

- Follow-up task 1
- Follow-up task 2
""",

        'release-notes': f"""# {title}

## Release Information

| Field | Value |
|-------|-------|
| Version | X.Y.Z |
| Date | {datetime.now().strftime("%Y-%m-%d")} |
| Type | Feature Release |

## Highlights

Summary of the key changes in this release.

## New Features

- Feature 1: Description
- Feature 2: Description

## Improvements

- Improvement 1
- Improvement 2

## Bug Fixes

- Fixed issue with X
- Resolved problem in Y

## Breaking Changes

- Change 1 (migration guide below)

## Migration Guide

### From Version X.Y.Z

Steps to migrate:

1. Step 1
2. Step 2
3. Step 3

## Known Issues

- Issue 1: Workaround available
- Issue 2: Fix planned for next release

## Dependencies

| Component | Version |
|-----------|---------|
| Dep A | 1.0.0 |
| Dep B | 2.0.0 |
""",

        'architecture': f"""# {title}

## Executive Summary

High-level overview of the architecture.

## System Context

Description of how the system fits into the larger ecosystem.

## Architecture Overview

### High-Level Design

Describe the overall architecture.

### Components

| Component | Purpose |
|-----------|---------|
| Component A | Purpose A |
| Component B | Purpose B |
| Component C | Purpose C |

## Component Details

### Component A

Detailed description of Component A.

### Component B

Detailed description of Component B.

## Data Flow

Description of how data flows through the system.

## Security Considerations

- Security aspect 1
- Security aspect 2
- Security aspect 3

## Scalability

How the system scales to meet demand.

## Deployment Architecture

### Production Environment

```
[Diagram description]
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Tech A |
| Backend | Tech B |
| Database | Tech C |

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Decision 1 | Reason 1 | Date |
| Decision 2 | Reason 2 | Date |
"""
    }

    return templates.get(template, templates['documentation'])


def main():
    parser = argparse.ArgumentParser(
        description='Generate PDF documents with Telekom branding',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --markdown docs/guide.md --output docs/guide.pdf
  %(prog)s --title "K8s RBAC Guide" --template howto
  %(prog)s --title "Notes" --content "## Topics\\n- Item 1\\n- Item 2"
        """
    )

    parser.add_argument('--markdown', '-m', metavar='FILE',
                        help='Markdown file to convert')
    parser.add_argument('--title', '-t', metavar='TITLE',
                        help='Document title')
    parser.add_argument('--content', '-c', metavar='CONTENT',
                        help='Markdown content string')
    parser.add_argument('--template', choices=['documentation', 'howto', 'release-notes', 'architecture'],
                        default='documentation',
                        help='Template type (default: documentation)')
    parser.add_argument('--output', '-o', metavar='FILE',
                        help='Output PDF path (default: docs/<title>.pdf)')
    parser.add_argument('--landscape', '-l', action='store_true',
                        help='Use landscape orientation')

    args = parser.parse_args()

    # Validate arguments
    if not args.markdown and not args.title:
        parser.error('Either --markdown or --title is required')

    # Get title from markdown filename if not specified
    title = args.title
    if not title and args.markdown:
        title = Path(args.markdown).stem.replace('-', ' ').replace('_', ' ').title()

    # Handle escaped newlines in content
    content = args.content
    if content:
        content = content.replace('\\n', '\n')

    # Generate PDF
    try:
        output_path = generate_pdf(
            title=title,
            content=content,
            markdown_file=args.markdown,
            template=args.template,
            output=args.output,
            orientation='landscape' if args.landscape else 'portrait'
        )
        print(f"Successfully created: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
