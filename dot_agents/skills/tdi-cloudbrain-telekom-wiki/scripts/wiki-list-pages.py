#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) List Pages Script
Usage: wiki-list-pages.py [--space SPACE] [--limit N] [--start N] [--format table|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_confluence_client,
    ConfluenceClientError,
    validate_space,
    format_pages_table,
    format_json,
    print_error,
)
from utils.config import ALLOWED_SPACES, DEFAULT_SPACE, DEFAULT_LIMIT
from utils.client import handle_confluence_error


def list_pages(confluence, space: str, limit: int = DEFAULT_LIMIT, start: int = 0):
    """
    List pages in a space.

    Args:
        confluence: Confluence client instance
        space: Space key
        limit: Maximum results to return
        start: Start index for pagination

    Returns:
        tuple: (pages list, size, has_more)
    """
    try:
        results = confluence.get_all_pages_from_space(
            space,
            start=start,
            limit=limit,
            expand='version,ancestors'
        )

        # The library returns a list directly
        pages = results if isinstance(results, list) else results.get('results', [])
        size = len(pages)
        has_more = size >= limit  # Approximation - library doesn't expose total

        return pages, size, has_more

    except Exception as e:
        handle_confluence_error(e, "list pages")


def main():
    parser = argparse.ArgumentParser(
        description='List pages in a Confluence space',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s
  %(prog)s --space TCAAS --limit 50
  %(prog)s --start 25 --limit 25   # Second page
  %(prog)s --format json

Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--space', default=DEFAULT_SPACE,
                        help=f'Space key (default: {DEFAULT_SPACE})')
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT,
                        help=f'Maximum results (default: {DEFAULT_LIMIT})')
    parser.add_argument('--start', type=int, default=0,
                        help='Start index for pagination (default: 0)')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    try:
        # Validate space
        space = validate_space(args.space)

        # Initialize client
        confluence = get_confluence_client()

        # List pages
        pages, size, has_more = list_pages(confluence, space, args.limit, args.start)

        # Format output
        if args.format == 'json':
            print(format_json({
                'space': space,
                'start': args.start,
                'size': size,
                'results': pages
            }))
        else:
            print(f"Pages in space {space} (showing {args.start + 1}-{args.start + size})")
            if has_more:
                print(f"  More pages available. Use --start {args.start + args.limit} for next page.")
            print()

            if not pages:
                print("No pages found in this space.")
            else:
                for page in pages:
                    page_id = page.get('id', 'N/A')
                    title = page.get('title', 'No title')
                    version = page.get('version', {}).get('number', '?')

                    ancestors = page.get('ancestors', [])
                    parent = ancestors[-1].get('title', '(root)') if ancestors else '(root)'

                    # Truncate long titles
                    if len(title) > 50:
                        title = title[:47] + '...'
                    if len(parent) > 30:
                        parent = parent[:27] + '...'

                    print(f"[{page_id}] {title}")
                    print(f"  Version: {version} | Parent: {parent}")
                    print()

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
