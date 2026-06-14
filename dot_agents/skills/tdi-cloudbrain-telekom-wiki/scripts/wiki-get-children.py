#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Get Child Pages Script
Usage: wiki-get-children.py --parent-id PAGE_ID [--depth N] [--format table|tree|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_confluence_client,
    ConfluenceClientError,
    validate_page_in_allowed_space,
    format_pages_table,
    format_page_tree,
    format_json,
    print_error,
)
from utils.config import ALLOWED_SPACES, MAX_DEPTH
from utils.client import handle_confluence_error
from utils.output import get_page_url


def get_parent_info(confluence, page_id: str) -> tuple:
    """
    Get parent page information and validate space.

    Args:
        confluence: Confluence client instance
        page_id: Parent page ID

    Returns:
        tuple: (space_key, title)
    """
    try:
        page = confluence.get_page_by_id(page_id, expand='space')

        if not page:
            raise ConfluenceClientError(f"Page '{page_id}' not found")

        space_key = validate_page_in_allowed_space(page)
        title = page.get('title', 'Unknown')

        return space_key, title

    except ValueError as e:
        raise ConfluenceClientError(str(e))
    except Exception as e:
        if "404" in str(e):
            raise ConfluenceClientError(
                f"Page '{page_id}' not found or you don't have permission to view it."
            )
        handle_confluence_error(e, "get parent page")


def get_children(confluence, page_id: str, limit: int = 100) -> list:
    """
    Get direct children of a page.

    Args:
        confluence: Confluence client instance
        page_id: Parent page ID
        limit: Maximum children to return

    Returns:
        list: Child pages
    """
    try:
        children = confluence.get_page_child_by_type(
            page_id,
            type='page',
            limit=limit,
            expand='version'
        )

        return children if isinstance(children, list) else []

    except Exception as e:
        handle_confluence_error(e, "get children")


def get_children_recursive(confluence, page_id: str, depth: int,
                           limit: int = 100, indent: str = '') -> list:
    """
    Get children recursively up to specified depth.

    Args:
        confluence: Confluence client instance
        page_id: Parent page ID
        depth: Remaining depth to traverse
        limit: Maximum children per level
        indent: Current indentation string

    Returns:
        list: All descendant pages with _indent field
    """
    if depth <= 0:
        return []

    all_pages = []
    children = get_children(confluence, page_id, limit)

    for child in children:
        child['_indent'] = indent
        all_pages.append(child)

        if depth > 1:
            grandchildren = get_children_recursive(
                confluence,
                child['id'],
                depth - 1,
                limit,
                indent + '  '
            )
            all_pages.extend(grandchildren)

    return all_pages


def main():
    parser = argparse.ArgumentParser(
        description='Get child pages of a Confluence page',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --parent-id 12345
  %(prog)s --parent-id 12345 --depth 2 --format tree
  %(prog)s --parent-id 12345 --format json

Output formats:
  table - Default tabular format
  tree  - Hierarchical tree view
  json  - Raw JSON data

Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--parent-id', required=True,
                        help='Parent page ID')
    parser.add_argument('--depth', type=int, default=1,
                        help=f'Depth of children to retrieve (default: 1, max: {MAX_DEPTH})')
    parser.add_argument('--limit', type=int, default=100,
                        help='Maximum children per level (default: 100)')
    parser.add_argument('--format', choices=['table', 'tree', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    # Cap depth at maximum
    depth = min(args.depth, MAX_DEPTH)

    try:
        # Initialize client
        confluence = get_confluence_client()

        # Validate parent page
        space_key, parent_title = get_parent_info(confluence, args.parent_id)

        # Get children
        if depth > 1:
            pages = get_children_recursive(confluence, args.parent_id, depth, args.limit)
        else:
            pages = get_children(confluence, args.parent_id, args.limit)
            # Add empty indent for consistency
            for page in pages:
                page['_indent'] = ''

        # Format output
        if args.format == 'json':
            # Remove _indent from JSON output
            for p in pages:
                p.pop('_indent', None)
            print(format_json({
                'parent_id': args.parent_id,
                'parent_title': parent_title,
                'depth': depth,
                'results': pages
            }))
        elif args.format == 'tree':
            print(format_page_tree(pages, parent_title, args.parent_id))
        else:
            # Table format
            print(f'Children of "{parent_title}" (ID: {args.parent_id})')
            print(f'Found {len(pages)} pages (depth: {depth})')
            print()

            if not pages:
                print("No child pages found.")
            else:
                for page in pages:
                    indent = page.get('_indent', '')
                    page_id = page.get('id', 'N/A')
                    title = page.get('title', 'No title')
                    version = page.get('version', {}).get('number', '?')

                    print(f"{indent}[{page_id}] {title} (v{version})")
                    print(f"{indent}  URL: {get_page_url(page_id)}")
                    print()

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
