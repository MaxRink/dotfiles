#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Export Script
Exports all pages under a given parent page as Markdown files, preserving the page hierarchy
as a directory structure. Optionally downloads all attachments and rewrites image references
to point to local files.

Usage:
  wiki-export-tree.py --parent-id PAGE_ID [--output-dir DIR] [--attachments]

Examples:
  # Export entire T-CaaS Convergence Wiki (text only)
  wiki-export-tree.py --parent-id 1959079430

  # Export with all attachments and images
  wiki-export-tree.py --parent-id 1959079430 --attachments

  # Export to a custom directory
  wiki-export-tree.py --parent-id 1959079430 --output-dir /tmp/wiki-export --attachments

  # Export just the Knowledge Base subtree
  wiki-export-tree.py --parent-id 2544994733 --attachments
"""

import os
import sys
import re
import time
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import get_confluence_client, ConfluenceClientError
from utils.output import confluence_to_markdown
from utils.config import DEFAULT_EXPAND, WIKI_URL


def sanitize_filename(title: str) -> str:
    """Convert a page title to a safe filename."""
    name = re.sub(r'[/\\:*?"<>|]', '-', title)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > 100:
        name = name[:100].rstrip(' -')
    return name


def get_children(confluence, parent_id: str) -> list:
    """Get all direct children of a page."""
    children = []
    start = 0
    limit = 100
    while True:
        try:
            result = confluence.get_page_child_by_type(
                parent_id, type='page', start=start, limit=limit,
                expand='version'
            )
        except Exception as e:
            print(f"  Warning: Could not get children of {parent_id}: {e}", file=sys.stderr)
            break
        if not result:
            break
        children.extend(result)
        if len(result) < limit:
            break
        start += limit
    return children


def download_attachments(confluence, page_id: str, target_dir: str) -> dict:
    """
    Download all attachments for a page and return a mapping of
    original filenames to local relative paths.

    Returns:
        dict: {original_filename: relative_path_from_page_md}
    """
    attachment_map = {}
    try:
        attachments = confluence.get_attachments_from_content(page_id, start=0, limit=200)
        results = attachments.get('results', [])
        if not results:
            return attachment_map

        attachments_dir = os.path.join(target_dir, "_attachments")
        os.makedirs(attachments_dir, exist_ok=True)

        for att in results:
            filename = att.get('title', '')
            download_link = att.get('_links', {}).get('download', '')
            if not filename or not download_link:
                continue

            safe_filename = sanitize_filename(filename)
            # Keep the original extension
            _, ext = os.path.splitext(filename)
            base, _ = os.path.splitext(safe_filename)
            safe_filename = base + ext

            local_path = os.path.join(attachments_dir, safe_filename)

            try:
                url = f"{WIKI_URL}/wiki{download_link}" if download_link.startswith('/') else download_link
                # Use the underlying requests session for direct download
                response = confluence._session.get(
                    f"{WIKI_URL}{download_link}",
                    stream=True
                )
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                attachment_map[filename] = f"_attachments/{safe_filename}"
            except Exception as e:
                print(f"    Warning: Could not download attachment '{filename}': {e}", file=sys.stderr)

    except Exception as e:
        print(f"    Warning: Could not list attachments for page {page_id}: {e}", file=sys.stderr)

    return attachment_map


def rewrite_image_refs(markdown_content: str, attachment_map: dict) -> str:
    """Rewrite image and link references to point to local attachment files."""
    if not attachment_map:
        return markdown_content

    result = markdown_content

    for original_name, local_path in attachment_map.items():
        # Replace markdown image references: ![alt](url_containing_filename)
        # Confluence images often appear as ![filename](wiki_url/download/attachments/...)
        result = re.sub(
            r'!\[([^\]]*)\]\([^)]*' + re.escape(original_name) + r'[^)]*\)',
            f'![\\1]({local_path})',
            result
        )
        # Also replace any remaining bare references to the attachment URL
        result = re.sub(
            r'\]\([^)]*' + re.escape(original_name) + r'[^)]*\)',
            f']({local_path})',
            result
        )

    return result


def get_page_content(confluence, page_id: str) -> tuple:
    """Fetch page content and return (title, body_html, metadata_header)."""
    try:
        page = confluence.get_page_by_id(page_id, expand=DEFAULT_EXPAND)
        title = page.get('title', 'Untitled')
        body_html = page.get('body', {}).get('storage', {}).get('value', '')

        page_url = f"https://wiki.telekom.de/pages/viewpage.action?pageId={page_id}"
        version = page.get('version', {}).get('number', '?')
        space = page.get('space', {}).get('key', '?')
        ancestors = page.get('ancestors', [])
        parent_title = ancestors[-1].get('title', 'None') if ancestors else 'None'

        header = f"# {title}\n\n"
        header += f"> **Page ID:** {page_id} | **Space:** {space} | **Version:** {version}  \n"
        header += f"> **Parent:** {parent_title}  \n"
        header += f"> **URL:** [{page_url}]({page_url})\n\n---\n\n"

        return title, body_html, header
    except Exception as e:
        print(f"  Warning: Could not fetch page {page_id}: {e}", file=sys.stderr)
        return None, None, None


def export_tree(confluence, page_id: str, parent_dir: str, depth: int = 0,
                counter: dict = None, with_attachments: bool = False):
    """Recursively export a page and all its children."""
    if counter is None:
        counter = {'done': 0, 'attachments': 0}

    indent = "  " * depth

    title, body_html, header = get_page_content(confluence, page_id)
    if title is None:
        return

    safe_name = sanitize_filename(title)
    children = get_children(confluence, page_id)

    if children:
        page_dir = os.path.join(parent_dir, safe_name)
        os.makedirs(page_dir, exist_ok=True)

        md = confluence_to_markdown(body_html)

        # Download attachments and rewrite references
        att_count = 0
        if with_attachments:
            attachment_map = download_attachments(confluence, page_id, page_dir)
            att_count = len(attachment_map)
            counter['attachments'] += att_count
            md = rewrite_image_refs(md, attachment_map)

        filepath = os.path.join(page_dir, "_index.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + md)

        counter['done'] += 1
        att_info = f" 📎{att_count}" if att_count else ""
        print(f"{indent}📁 [{counter['done']}] {title}{att_info}")

        for child in children:
            child_id = child.get('id')
            if child_id:
                export_tree(confluence, child_id, page_dir, depth + 1, counter, with_attachments)
                time.sleep(0.2)  # Rate limiting
    else:
        # Leaf page - determine the directory for attachments
        md = confluence_to_markdown(body_html)

        att_count = 0
        if with_attachments:
            # For leaf pages, create a directory if there are attachments
            attachment_map = download_attachments(confluence, page_id, parent_dir)
            att_count = len(attachment_map)
            counter['attachments'] += att_count
            if attachment_map:
                # Move attachments into a page-specific subfolder
                page_att_dir = os.path.join(parent_dir, f"_attachments_{safe_name}")
                generic_att_dir = os.path.join(parent_dir, "_attachments")
                if os.path.exists(generic_att_dir):
                    os.rename(generic_att_dir, page_att_dir)
                # Update paths in the map
                rewritten_map = {}
                for orig, path in attachment_map.items():
                    rewritten_map[orig] = path.replace("_attachments/", f"_attachments_{safe_name}/")
                md = rewrite_image_refs(md, rewritten_map)

        filepath = os.path.join(parent_dir, f"{safe_name}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + md)

        counter['done'] += 1
        att_info = f" 📎{att_count}" if att_count else ""
        print(f"{indent}📄 [{counter['done']}] {title}{att_info}")


def main():
    parser = argparse.ArgumentParser(
        description='Export a Confluence page tree as Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --parent-id 1959079430
  %(prog)s --parent-id 1959079430 --attachments
  %(prog)s --parent-id 1959079430 --output-dir /tmp/wiki-export --attachments
  %(prog)s --parent-id 2544994733 --output-dir ~/Desktop/kb-export
        """
    )

    parser.add_argument('--parent-id', required=True,
                        help='Root page ID to export from')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory (default: ~/Desktop/wiki-export-<parent-id>)')
    parser.add_argument('--attachments', action='store_true',
                        help='Also download attachments and images')

    args = parser.parse_args()

    output_dir = args.output_dir or os.path.expanduser(
        f"~/Desktop/wiki-export-{args.parent_id}"
    )

    att_label = " (with attachments)" if args.attachments else ""
    print(f"🚀 Exporting wiki tree (root page: {args.parent_id}){att_label}")
    print(f"📂 Output directory: {output_dir}\n")

    os.makedirs(output_dir, exist_ok=True)

    try:
        confluence = get_confluence_client()
    except ConfluenceClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    counter = {'done': 0, 'attachments': 0}
    export_tree(confluence, args.parent_id, output_dir, depth=0, counter=counter,
                with_attachments=args.attachments)

    summary = f"\n✅ Export complete! {counter['done']} pages exported to {output_dir}"
    if args.attachments:
        summary += f" ({counter['attachments']} attachments downloaded)"
    print(summary)


if __name__ == '__main__':
    main()
