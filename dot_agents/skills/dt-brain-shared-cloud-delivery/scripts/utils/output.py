"""
Output formatting utilities for TDI Cloud Delivery skill.
"""

import json
import sys


def print_error(message):
    """Print an error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_table(headers, rows, max_widths=None):
    """
    Print data as a formatted table.

    Args:
        headers: List of column headers
        rows: List of row data (each row is a list)
        max_widths: Optional dict of column index -> max width for truncation
    """
    if not rows:
        print("No results found.")
        return

    max_widths = max_widths or {}

    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                cell = str(row[i]) if row[i] is not None else ""
                max_width = max(max_width, len(cell))

        # Apply max width limit if specified
        if i in max_widths:
            max_width = min(max_width, max_widths[i])

        col_widths.append(max_width)

    # Build format string
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)

    # Print header
    print(fmt.format(*[str(h) for h in headers]))
    print(fmt.format(*["-" * w for w in col_widths]))

    # Print rows
    for row in rows:
        formatted_cells = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ""
            # Truncate if needed
            if i in max_widths and len(cell_str) > max_widths[i]:
                cell_str = cell_str[:max_widths[i] - 3] + "..."
            formatted_cells.append(cell_str)

        # Pad row if needed
        while len(formatted_cells) < len(headers):
            formatted_cells.append("")

        print(fmt.format(*formatted_cells))


def truncate(text, max_length):
    """Truncate text to max_length, adding ellipsis if needed."""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_date(date_str):
    """Format a date string for display (YYYY-MM-DD)."""
    if not date_str:
        return ""
    # Handle both date and datetime strings
    return date_str[:10] if date_str else ""


def format_labels(labels, max_length=40):
    """Format a list of labels for display."""
    if not labels:
        return ""
    label_str = ", ".join(labels)
    return truncate(label_str, max_length)
