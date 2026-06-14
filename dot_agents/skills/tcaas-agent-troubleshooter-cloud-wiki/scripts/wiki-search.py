#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Search Script
Usage: wiki-search.py --query "CQL query" [--space SPACE] [--limit N] [--format table|json]
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
from utils.config import ALLOWED_SPACES, DEFAULT_SEARCH_LIMIT
from utils.validators import build_space_filter
from utils.client import handle_confluence_error


def search_pages(confluence, query: str, space: str = None, limit: int = DEFAULT_SEARCH_LIMIT):
    """
    Search for pages using CQL.

    Args:
        confluence: Confluence client instance
        query: CQL query string
        space: Optional space to restrict search
        limit: Maximum results to return

    Returns:
        tuple: (pages list, total count, full CQL)
    """
    # Build CQL with space restriction
    space_filter = build_space_filter(space)
    full_cql = f"{space_filter} AND type = page AND ({query})"

    try:
        results = confluence.cql(full_cql, limit=limit, expand='space,version,ancestors')

        pages = results.get('results', [])
        total = results.get('totalSize', len(pages))

        return pages, total, full_cql

    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            raise ConfluenceClientError(f"Invalid CQL query: {query}\nError: {e}")
        handle_confluence_error(e, "search")


def main():
    parser = argparse.ArgumentParser(
        description='Search Confluence pages using CQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --query "text ~ 'kubernetes'"
  %(prog)s --query "title ~ 'architecture'" --limit 10
  %(prog)s --query "label = 'documentation'" --space TCAAS
  %(prog)s --query "lastModified > now('-7d')" --format json

CQL Examples:
  text ~ 'search term'           Full-text search
  title ~ 'page title'           Search in titles
  label = 'label-name'           Pages with specific label
  creator = 'username'           Pages created by user
  lastModified > '2024-01-01'    Recently modified pages

Note: Queries are automatically scoped to allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--query', '-q', required=True,
                        help='CQL search query')
    parser.add_argument('--space',
                        help=f'Space key to search in (default: all allowed)')
    parser.add_argument('--limit', type=int, default=DEFAULT_SEARCH_LIMIT,
                        help=f'Maximum results (default: {DEFAULT_SEARCH_LIMIT})')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')

    args = parser.parse_args()

    try:
        # Validate space if provided
        if args.space:
            validate_space(args.space)

        # Initialize client
        confluence = get_confluence_client()

        # Search
        pages, total, full_cql = search_pages(confluence, args.query, args.space, args.limit)

        # Format output
        if args.format == 'json':
            print(format_json({'total': total, 'cql': full_cql, 'results': pages}))
        else:
            print(format_pages_table(pages, "Search Results", total, full_cql))

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
