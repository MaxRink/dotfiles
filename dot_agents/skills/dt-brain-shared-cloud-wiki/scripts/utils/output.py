"""Output formatting utilities for Telekom Wiki (Confluence) integration."""

import json
import re
import html
import sys
from typing import List, Dict, Any, Optional

from .config import WIKI_URL


# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def supports_color() -> bool:
    """Check if terminal supports color output."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    prefix = colorize("Error:", Colors.RED + Colors.BOLD)
    if message.lower().startswith("error:"):
        message = message[6:].strip()
    print(f"{prefix} {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print a success message."""
    prefix = colorize("✓", Colors.GREEN)
    print(f"{prefix} {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    prefix = colorize("Warning:", Colors.YELLOW + Colors.BOLD)
    print(f"{prefix} {message}", file=sys.stderr)


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON."""
    return json.dumps(data, indent=indent, default=str)


def get_page_url(page_id: str) -> str:
    """Get the URL for a page."""
    return f"{WIKI_URL}/pages/viewpage.action?pageId={page_id}"


def format_pages_table(pages: List[Dict[str, Any]], title: str = "Pages",
                       total: Optional[int] = None, cql: Optional[str] = None) -> str:
    """
    Format a list of pages as a readable table.

    Args:
        pages: List of page dictionaries from Confluence API
        title: Title for the output
        total: Total number of results (for pagination info)
        cql: CQL query used (for display)

    Returns:
        str: Formatted table string
    """
    if total is None:
        total = len(pages)

    lines = []
    lines.append(f"Found {total} pages (showing {len(pages)})")

    if cql:
        lines.append(f"CQL: {cql}")

    lines.append("")

    if not pages:
        lines.append("No pages found matching the query.")
        return '\n'.join(lines)

    for page in pages:
        # Handle CQL search results which wrap page data in 'content'
        if 'content' in page:
            content = page['content']
            page_id = content.get('id', 'N/A')
            # Use content title (without highlighting) if available
            title_text = content.get('title', page.get('title', 'No title'))
            space_key = content.get('space', {}).get('key', 'Unknown')
            # Space might be in _expandable
            if space_key == 'Unknown' and '_expandable' in content:
                space_path = content['_expandable'].get('space', '')
                if '/space/' in space_path:
                    space_key = space_path.split('/space/')[-1]
            version = content.get('version', {}).get('number', '?')
            ancestors = content.get('ancestors', [])
        else:
            page_id = page.get('id', 'N/A')
            title_text = page.get('title', 'No title')
            space_key = page.get('space', {}).get('key', 'Unknown')
            version = page.get('version', {}).get('number', '?')
            ancestors = page.get('ancestors', [])

        parent = ancestors[-1].get('title', '-') if ancestors else '-'

        # Remove CQL highlight markers from title
        title_text = title_text.replace('@@@hl@@@', '').replace('@@@endhl@@@', '')

        # Truncate long titles
        if len(title_text) > 60:
            title_text = title_text[:57] + '...'
        if len(parent) > 30:
            parent = parent[:27] + '...'

        page_id_colored = colorize(f"[{page_id}]", Colors.CYAN)

        lines.append(f"{page_id_colored} {title_text}")
        lines.append(f"  Space: {space_key} | Version: {version} | Parent: {parent}")
        lines.append(f"  URL: {get_page_url(page_id)}")
        lines.append("")

    return '\n'.join(lines)


def format_page_detail(page: Dict[str, Any], format_type: str = "markdown") -> str:
    """
    Format a single page with full details.

    Args:
        page: Page dictionary from Confluence API
        format_type: Output format - 'markdown', 'confluence', or 'json'

    Returns:
        str: Formatted page content
    """
    if format_type == "json":
        return format_json(page)

    page_id = page.get('id', 'Unknown')
    title = page.get('title', 'Unknown')
    version = page.get('version', {}).get('number', 'Unknown')
    space = page.get('space', {}).get('key', 'Unknown')
    body_content = page.get('body', {}).get('storage', {}).get('value', '')

    ancestors = page.get('ancestors', [])
    parent = ancestors[-1].get('title', 'None') if ancestors else 'None'

    lines = []

    if format_type == "confluence":
        # Raw Confluence storage format
        lines.append(colorize(f"=== {title} ===", Colors.BOLD + Colors.CYAN))
        lines.append(f"ID:       {page_id}")
        lines.append(f"Space:    {space}")
        lines.append(f"Version:  {version}")
        lines.append(f"Parent:   {parent}")
        lines.append(f"URL:      {get_page_url(page_id)}")
        lines.append("")
        lines.append("Content (Confluence Storage Format):")
        lines.append("-" * 40)
        lines.append(body_content)
    else:
        # Markdown format (default)
        lines.append(colorize(f"# {title}", Colors.BOLD))
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| ID | {page_id} |")
        lines.append(f"| Space | {space} |")
        lines.append(f"| Version | {version} |")
        lines.append(f"| Parent | {parent} |")
        lines.append(f"| URL | {get_page_url(page_id)} |")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(confluence_to_markdown(body_content))

    return '\n'.join(lines)


def format_page_tree(pages: List[Dict[str, Any]], parent_title: str, parent_id: str) -> str:
    """
    Format pages as a tree structure.

    Args:
        pages: List of page dictionaries with optional '_indent' field
        parent_title: Title of the parent page
        parent_id: ID of the parent page

    Returns:
        str: Tree-formatted string
    """
    lines = []
    lines.append(colorize(f"{parent_title} [{parent_id}]", Colors.BOLD + Colors.CYAN))

    for i, page in enumerate(pages):
        indent = page.get('_indent', '')
        title = page.get('title', 'Unknown')
        page_id = page.get('id', 'N/A')

        # Use appropriate tree character
        is_last = (i == len(pages) - 1) and not indent
        prefix = '└──' if is_last else '├──'

        lines.append(f"{indent}{prefix} {title} [{page_id}]")

    return '\n'.join(lines)


def _preprocess_confluence_macros(content: str) -> str:
    """
    Pre-process Confluence storage format macros into standard HTML
    before passing to markdownify.
    """
    # Code blocks: extract language and body
    def _replace_code_block(m):
        inner = m.group(1)
        lang_match = re.search(
            r'<ac:parameter\s+ac:name="language">(.*?)</ac:parameter>',
            inner, re.DOTALL
        )
        lang = lang_match.group(1).strip() if lang_match else ''
        body_match = re.search(
            r'<ac:plain-text-body><!\[CDATA\[(.*?)\]\]></ac:plain-text-body>',
            inner, re.DOTALL
        )
        body = body_match.group(1) if body_match else ''
        return f'<pre><code class="language-{lang}">{html.escape(body)}</code></pre>'

    content = re.sub(
        r'<ac:structured-macro[^>]*ac:name="code"[^>]*>(.*?)</ac:structured-macro>',
        _replace_code_block, content, flags=re.DOTALL
    )

    # Info/note/tip/warning panels → blockquotes with emoji prefix
    panel_icons = {'info': 'ℹ️', 'note': '📝', 'tip': '💡', 'warning': '⚠️'}
    for panel_type, icon in panel_icons.items():
        def _replace_panel(m, _icon=icon, _type=panel_type):
            inner = m.group(1)
            title_match = re.search(
                r'<ac:parameter\s+ac:name="title">(.*?)</ac:parameter>',
                inner, re.DOTALL
            )
            title = title_match.group(1).strip() if title_match else _type.capitalize()
            body_match = re.search(
                r'<ac:rich-text-body>(.*?)</ac:rich-text-body>',
                inner, re.DOTALL
            )
            body = body_match.group(1) if body_match else ''
            return f'<blockquote><p><strong>{_icon} {title}</strong></p>{body}</blockquote>'

        content = re.sub(
            rf'<ac:structured-macro[^>]*ac:name="{panel_type}"[^>]*>(.*?)</ac:structured-macro>',
            _replace_panel, content, flags=re.DOTALL
        )

    # Expand macro → details/summary
    def _replace_expand(m):
        inner = m.group(1)
        title_match = re.search(
            r'<ac:parameter\s+ac:name="title">(.*?)</ac:parameter>',
            inner, re.DOTALL
        )
        title = title_match.group(1).strip() if title_match else 'Details'
        body_match = re.search(
            r'<ac:rich-text-body>(.*?)</ac:rich-text-body>',
            inner, re.DOTALL
        )
        body = body_match.group(1) if body_match else ''
        return f'<details><summary>{title}</summary>{body}</details>'

    content = re.sub(
        r'<ac:structured-macro[^>]*ac:name="expand"[^>]*>(.*?)</ac:structured-macro>',
        _replace_expand, content, flags=re.DOTALL
    )

    # Status macro → badge text
    content = re.sub(
        r'<ac:structured-macro[^>]*ac:name="status"[^>]*>.*?'
        r'<ac:parameter\s+ac:name="title">(.*?)</ac:parameter>.*?</ac:structured-macro>',
        r' `[\1]` ', content, flags=re.DOTALL
    )

    # Confluence images (attached files)
    content = re.sub(
        r'<ac:image[^>]*>.*?<ri:attachment\s+ri:filename="([^"]+)"[^/]*/?>.*?</ac:image>',
        r'<img src="\1" alt="\1" />', content, flags=re.DOTALL
    )
    # Self-closing variant
    content = re.sub(
        r'<ac:image[^>]*>\s*<ri:attachment\s+ri:filename="([^"]+)"[^/]*/>\s*</ac:image>',
        r'<img src="\1" alt="\1" />', content, flags=re.DOTALL
    )

    # Confluence links to other pages
    content = re.sub(
        r'<ac:link>.*?<ri:page\s+ri:content-title="([^"]+)"[^/]*/?>.*?'
        r'(?:<ac:plain-text-link-body><!\[CDATA\[(.*?)\]\]></ac:plain-text-link-body>)?.*?</ac:link>',
        lambda m: f'<a href="#">{m.group(2) or m.group(1)}</a>',
        content, flags=re.DOTALL
    )

    # Remove TOC, children, and other non-content macros
    for macro_name in ['toc', 'children', 'table-filter', 'scroll-pagebreak',
                       'multiexcerpt', 'multiexcerpt-include', 'anchor']:
        content = re.sub(
            rf'<ac:structured-macro[^>]*ac:name="{macro_name}"[^>]*>.*?</ac:structured-macro>',
            '', content, flags=re.DOTALL
        )
        # Self-closing variant
        content = re.sub(
            rf'<ac:structured-macro[^>]*ac:name="{macro_name}"[^>]*/>\s*',
            '', content, flags=re.DOTALL
        )

    # Remove layout wrappers (keep inner content)
    for tag in ['ac:layout', 'ac:layout-section', 'ac:layout-cell']:
        content = re.sub(rf'</?{re.escape(tag)}[^>]*>', '', content)

    # Remove any remaining ac:parameter tags
    content = re.sub(r'<ac:parameter[^>]*>.*?</ac:parameter>', '', content, flags=re.DOTALL)

    # Remove remaining ac: and ri: tags but keep their text content
    content = re.sub(r'</?ac:[^>]+>', '', content)
    content = re.sub(r'</?ri:[^>]+>', '', content)

    return content


def confluence_to_markdown(content: str) -> str:
    """
    Convert Confluence storage format to Markdown.

    Pre-processes Confluence-specific macros, then uses markdownify
    for accurate HTML-to-Markdown conversion with proper table,
    heading, and list handling.

    Args:
        content: Confluence storage format content

    Returns:
        str: Markdown formatted content
    """
    if not content:
        return ''

    from markdownify import markdownify as md_convert

    # Pre-process Confluence macros into standard HTML
    content = _preprocess_confluence_macros(content)

    # Convert HTML to Markdown using markdownify
    result = md_convert(
        content,
        heading_style='ATX',
        bullets='-',
        strip=['colgroup', 'col', 'tbody', 'thead'],
    )

    # Clean up excessive whitespace
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.strip()

    return result
