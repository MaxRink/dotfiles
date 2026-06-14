#!/usr/bin/env python3
"""
Generate Confluence wiki page from vendor requirements and compliance analysis.

Usage:
  generate_wiki.py --requirements reqs.json --compliance compliance.json \
    --product-version baremetal-cluster-35.4.4 --customer "Magyar Telekom" \
    --output /tmp/wiki_content.html
"""

import argparse
import html
import json
import sys
from pathlib import Path


# Status categories and their colors
STATUS_CONFIG = {
    'Fulfilled':             {'color': 'rgb(223,240,216)', 'group': 'fulfilled'},
    'Supported':             {'color': 'rgb(223,240,216)', 'group': 'fulfilled'},
    'Fulfilled (customer provision)': {'color': 'rgb(223,240,216)', 'group': 'fulfilled'},
    'Supported (if needed)': {'color': 'rgb(223,240,216)', 'group': 'fulfilled'},
    'Partial':               {'color': 'rgb(252,248,227)', 'group': 'partial'},
    'Configurable':          {'color': 'rgb(252,248,227)', 'group': 'partial'},
    'Needs review':          {'color': 'rgb(252,248,227)', 'group': 'partial'},
    'Needs verification':    {'color': 'rgb(252,248,227)', 'group': 'partial'},
    'Depends on storage':    {'color': 'rgb(252,248,227)', 'group': 'partial'},
    'Not deployed':          {'color': 'rgb(242,222,222)', 'group': 'gap'},
    'Gap':                   {'color': 'rgb(242,222,222)', 'group': 'gap'},
    'N/A':                   {'color': 'rgb(217,237,247)', 'group': 'info'},
    'N/A for now':           {'color': 'rgb(217,237,247)', 'group': 'info'},
    'Info':                  {'color': 'rgb(217,237,247)', 'group': 'info'},
    'Customer responsibility': {'color': 'rgb(217,237,247)', 'group': 'info'},
}

WIKI_REFERENCES = [
    ('1499499273', 'CIT CaaS 1.0 Documentation'),
    ('1478511397', 'CaaS on Baremetal Components'),
    ('1382794879', 'CaaS on Baremetal Storage'),
    ('1377043242', 'CaaS on Baremetal Network Design'),
    ('1448911229', 'CaaS on Baremetal DC Requirements'),
    ('1486868707', 'CaaS on Baremetal Failure Domains'),
    ('1768078246', 'T-CaaS Cluster Policy (OPA)'),
    ('1960971820', 'T-CaaS OS Security'),
]


def esc(s):
    """Escape string for Confluence storage format, replacing non-ASCII."""
    if not s:
        return ''
    result = html.escape(str(s))
    result = result.replace('\n', '<br/>')
    # Replace common non-ASCII characters with ASCII equivalents
    replacements = {
        '\u2122': '(TM)',   # ™
        '\u2014': '-',      # —
        '\u2013': '-',      # –
        '\u2265': '&gt;=',  # ≥
        '\u2264': '&lt;=',  # ≤
        '\u2018': "'",      # '
        '\u2019': "'",      # '
        '\u201c': '"',      # "
        '\u201d': '"',      # "
        '\u2026': '...',    # …
        '\u00a0': ' ',      # non-breaking space
        '\u2705': '',       # ✅ (emoji - strip)
        '\u274c': '',       # ❌ (emoji - strip)
        '\u26a0': '',       # ⚠ (emoji - strip)
        '\ufe0f': '',       # variation selector (strip)
        '\u2139': '',       # ℹ (emoji - strip)
    }
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def get_status_color(status):
    """Get background color for a compliance status."""
    for key, config in STATUS_CONFIG.items():
        if key.lower() in status.lower():
            return config['color']
    return ''


def get_status_group(status):
    """Get group (fulfilled/partial/gap/info) for a status."""
    for key, config in STATUS_CONFIG.items():
        if key.lower() in status.lower():
            return config['group']
    return 'info'


def count_by_group(compliance_data):
    """Count requirements by status group."""
    counts = {'fulfilled': 0, 'partial': 0, 'gap': 0, 'info': 0}
    for rid, data in compliance_data.items():
        group = get_status_group(data.get('status', ''))
        counts[group] = counts.get(group, 0) + 1
    return counts


def generate_html(requirements, compliance_data, product_version, customer, k8s_version=None):
    """Generate Confluence storage format HTML."""
    total = len(requirements)
    counts = count_by_group(compliance_data)

    parts = []

    # Header
    parts.append(f'<h1>SDM Infrastructure Requirements Analysis - {esc(customer)}</h1>')
    parts.append(f'<p><strong>Product version:</strong> {esc(product_version)}'
                 + (f' (Kubernetes {esc(k8s_version)})' if k8s_version else '') + '</p>')
    parts.append('<p><strong>Date:</strong> {{DATE}}</p>')
    parts.append('<p><strong>Source:</strong> Ericsson SDM Infrastructure Requirements (CCDM)</p>')

    # Info box
    parts.append('<ac:structured-macro ac:name="info" ac:schema-version="1"><ac:rich-text-body>')
    parts.append('<p><strong>This page analyzes Ericsson SDM/CCDM infrastructure requirements '
                 'against T-CaaS baremetal platform capabilities.</strong></p>')
    parts.append('<p>Each requirement is mapped to CaaS configuration with references to '
                 'product code and wiki documentation.</p>')
    parts.append('</ac:rich-text-body></ac:structured-macro>')

    # Summary table
    parts.append('<h2>Summary</h2>')
    parts.append('<table><tbody>')
    pct = lambda n: f'{100*n//total}%' if total > 0 else '0%'
    parts.append(f'<tr><td style="background-color: rgb(223,240,216);"><strong>FULFILLED / SUPPORTED'
                 f'</strong></td><td>{counts["fulfilled"]} ({pct(counts["fulfilled"])})</td></tr>')
    parts.append(f'<tr><td style="background-color: rgb(252,248,227);"><strong>PARTIAL / CONFIGURABLE / '
                 f'NEEDS REVIEW</strong></td><td>{counts["partial"]} ({pct(counts["partial"])})</td></tr>')
    parts.append(f'<tr><td style="background-color: rgb(242,222,222);"><strong>GAP</strong></td>'
                 f'<td>{counts["gap"]} ({pct(counts["gap"])})</td></tr>')
    parts.append(f'<tr><td style="background-color: rgb(217,237,247);"><strong>N/A / INFO</strong></td>'
                 f'<td>{counts["info"]} ({pct(counts["info"])})</td></tr>')
    parts.append(f'<tr><td><strong>Total requirements</strong></td><td>{total}</td></tr>')
    parts.append('</tbody></table>')

    # Legend
    parts.append('<h3>Legend</h3>')
    parts.append('<table><tbody>')
    parts.append('<tr><td style="background-color: rgb(223,240,216);">FULFILLED</td>'
                 '<td>Requirement is met by CaaS platform</td></tr>')
    parts.append('<tr><td style="background-color: rgb(252,248,227);">PARTIAL / CONFIGURABLE</td>'
                 '<td>Partially met or can be configured via ExtraParams</td></tr>')
    parts.append('<tr><td style="background-color: rgb(242,222,222);">GAP</td>'
                 '<td>Not supported by CaaS platform</td></tr>')
    parts.append('<tr><td style="background-color: rgb(217,237,247);">N/A / INFO</td>'
                 '<td>Not applicable or informational</td></tr>')
    parts.append('</tbody></table>')

    # Action items - collect non-fulfilled items
    action_items = []
    for req in requirements:
        rid = str(req['id'])
        comp = compliance_data.get(rid, {})
        group = get_status_group(comp.get('status', ''))
        if group in ('partial', 'gap'):
            action_items.append((req['id'], comp.get('status', ''), comp.get('notes', '')))

    if action_items:
        parts.append('<h2>Action Items</h2>')
        parts.append('<ac:structured-macro ac:name="warning" ac:schema-version="1"><ac:rich-text-body>')
        parts.append('<p>The following items require attention:</p>')
        parts.append('<ol>')
        for rid, status, notes in action_items:
            note_short = notes[:150] + '...' if len(notes) > 150 else notes
            parts.append(f'<li><strong>Req #{rid} ({esc(status)}):</strong> {esc(note_short)}</li>')
        parts.append('</ol>')
        parts.append('</ac:rich-text-body></ac:structured-macro>')

    # Per-sheet tables
    sheets_seen = []
    for req in requirements:
        if req['sheet'] not in sheets_seen:
            sheets_seen.append(req['sheet'])

    for sheet_name in sheets_seen:
        sheet_reqs = [r for r in requirements if r['sheet'] == sheet_name]
        if not sheet_reqs:
            continue

        parts.append(f'<h2>{esc(sheet_name)}</h2>')
        parts.append('<table><tbody>')
        parts.append('<tr>')
        parts.append('<th style="width: 4.0%;">#</th>')
        parts.append('<th style="width: 12.0%;">Category</th>')
        parts.append('<th style="width: 30.0%;">Requirement</th>')
        parts.append('<th style="width: 10.0%;">Customer Comment</th>')
        parts.append('<th style="width: 10.0%;">T-CaaS Status</th>')
        parts.append('<th style="width: 15.0%;">Reference</th>')
        parts.append('<th style="width: 19.0%;">Notes</th>')
        parts.append('</tr>')

        for req in sheet_reqs:
            rid = str(req['id'])
            comp = compliance_data.get(rid, {})
            status = comp.get('status', '')
            reference = comp.get('reference', '')
            notes = comp.get('notes', '')

            color = get_status_color(status)
            status_td = (f'<td style="background-color: {color};">{esc(status)}</td>'
                         if color else f'<td>{esc(status)}</td>')

            # Build reference with wiki link if available
            ref_html = esc(reference)
            wiki_url = comp.get('wiki_url', '')
            wiki_title = comp.get('wiki_title', '')
            if wiki_url and wiki_title:
                ref_html += f' (<a href="{esc(wiki_url)}">{esc(wiki_title)}</a>)'

            parts.append('<tr>')
            parts.append(f'<td>{req["id"]}</td>')
            parts.append(f'<td>{esc(req.get("category", ""))}</td>')
            parts.append(f'<td>{esc(req.get("requirement_text", ""))}</td>')
            parts.append(f'<td>{esc(req.get("customer_comment", ""))}</td>')
            parts.append(status_td)
            parts.append(f'<td>{ref_html}</td>')
            parts.append(f'<td>{esc(notes)}</td>')
            parts.append('</tr>')

        parts.append('</tbody></table>')

    # References section
    parts.append('<h2>References</h2>')
    parts.append('<ul>')
    for pid, title in WIKI_REFERENCES:
        parts.append(f'<li><a href="https://wiki.telekom.de/pages/viewpage.action?pageId={pid}">'
                     f'{esc(title)}</a></li>')
    parts.append('</ul>')

    content = '\n'.join(parts)

    # Replace date placeholder
    from datetime import date
    content = content.replace('{{DATE}}', date.today().isoformat())

    return content


def main():
    parser = argparse.ArgumentParser(
        description='Generate Confluence wiki page from vendor requirements compliance analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --requirements reqs.json --compliance compliance.json \\
    --product-version baremetal-cluster-35.4.4 --customer "Magyar Telekom" \\
    --output /tmp/wiki_content.html

Compliance JSON format:
  {
    "1": {"status": "Fulfilled", "reference": "...", "notes": "...", "wiki_url": "...", "wiki_title": "..."},
    "2": {"status": "Partial", "reference": "...", "notes": "..."}
  }
        """
    )

    parser.add_argument('--requirements', '-r', required=True,
                        help='Path to requirements JSON (from parse_requirements.py)')
    parser.add_argument('--compliance', '-c', required=True,
                        help='Path to compliance analysis JSON')
    parser.add_argument('--product-version', '-p', required=True,
                        help='CaaS product version (e.g., baremetal-cluster-35.4.4)')
    parser.add_argument('--customer', required=True,
                        help='Customer/NatCo name (e.g., "Magyar Telekom")')
    parser.add_argument('--k8s-version', help='Kubernetes version (e.g., v1.35.0)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output HTML file path')

    args = parser.parse_args()

    # Load requirements
    with open(args.requirements) as f:
        requirements = json.load(f)

    # Load compliance data
    with open(args.compliance) as f:
        compliance_data = json.load(f)

    print(f"Requirements: {len(requirements)}", file=sys.stderr)
    print(f"Compliance entries: {len(compliance_data)}", file=sys.stderr)

    # Generate HTML
    content = generate_html(
        requirements,
        compliance_data,
        args.product_version,
        args.customer,
        args.k8s_version
    )

    # Verify ASCII-clean output
    non_ascii = [(i, ch) for i, ch in enumerate(content) if ord(ch) > 127]
    if non_ascii:
        print(f"Warning: {len(non_ascii)} non-ASCII characters found, cleaning...", file=sys.stderr)
        # Strip any remaining non-ASCII
        content = ''.join(ch if ord(ch) <= 127 else '?' for ch in content)

    # Write output
    Path(args.output).write_text(content, encoding='utf-8')
    print(f"Generated {len(content)} chars -> {args.output}", file=sys.stderr)

    # Print summary
    counts = count_by_group(compliance_data)
    total = len(requirements)
    print(f"Summary: Fulfilled={counts['fulfilled']}, Partial={counts['partial']}, "
          f"Gap={counts['gap']}, Info={counts['info']}, Total={total}", file=sys.stderr)


if __name__ == '__main__':
    main()
