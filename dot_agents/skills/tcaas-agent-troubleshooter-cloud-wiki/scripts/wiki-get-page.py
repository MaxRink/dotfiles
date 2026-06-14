#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Get Page Script
Usage: wiki-get-page.py --id PAGE_ID | --title "Page Title" [--format markdown|confluence|json]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_confluence_client,
    ConfluenceClientError,
    validate_space,
    validate_page_in_allowed_space,
    format_page_detail,
    format_json,
    print_error,
)
from utils.config import ALLOWED_SPACES, DEFAULT_SPACE, DEFAULT_EXPAND
from utils.client import handle_confluence_error


def get_page_by_id(confluence, page_id: str, expand: str = DEFAULT_EXPAND) -> dict:
    """
    Get a page by its ID.

    Args:
        confluence: Confluence client instance
        page_id: Page ID
        expand: Confluence expand parameter

    Returns:
        dict: Page data
    """
    try:
        page = confluence.get_page_by_id(page_id, expand=expand)

        if not page:
            raise ConfluenceClientError(f"Page '{page_id}' not found")

        # Validate space
        validate_page_in_allowed_space(page)

        return page

    except ValueError as e:
        raise ConfluenceClientError(str(e))
    except Exception as e:
        if "404" in str(e):
            raise ConfluenceClientError(
                f"Page '{page_id}' not found or you don't have permission to view it."
            )
        handle_confluence_error(e, "page retrieval")


def get_page_by_title(confluence, title: str, space: str, expand: str = DEFAULT_EXPAND) -> dict:
    """
    Get a page by its title in a space.

    Args:
        confluence: Confluence client instance
        title: Page title
        space: Space key
        expand: Confluence expand parameter

    Returns:
        dict: Page data
    """
    try:
        page = confluence.get_page_by_title(space, title, expand=expand)

        if not page:
            raise ConfluenceClientError(
                f"Page with title '{title}' not found in space {space}"
            )

        return page

    except Exception as e:
        if isinstance(e, ConfluenceClientError):
            raise
        handle_confluence_error(e, "page retrieval")


def main():
    parser = argparse.ArgumentParser(
        description='Get a Confluence page by ID or title',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --id 12345
  %(prog)s --title "E2E CIT Infrastructure Architecture"
  %(prog)s --title "My Page" --space TCAAS
  %(prog)s --id 12345 --format json
  %(prog)s --id 12345 --format confluence

Output formats:
  markdown   - Converted to Markdown (default)
  confluence - Raw Confluence storage format (XHTML)
  json       - Raw API response

Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--id',
                        help='Page ID')
    parser.add_argument('--title',
                        help='Page title (searches in specified space)')
    parser.add_argument('--space', default=DEFAULT_SPACE,
                        help=f'Space key for title search (default: {DEFAULT_SPACE})')
    parser.add_argument('--format', choices=['markdown', 'confluence', 'json'],
                        default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--expand', default=DEFAULT_EXPAND,
                        help=f'Confluence expand fields (default: {DEFAULT_EXPAND})')

    args = parser.parse_args()

    # Validate input
    if not args.id and not args.title:
        print_error("Either --id or --title is required")
        parser.print_help()
        sys.exit(1)

    try:
        # Validate space if searching by title
        if args.title:
            validate_space(args.space)

        # Initialize client
        confluence = get_confluence_client()

        # Get page
        if args.id:
            page = get_page_by_id(confluence, args.id, args.expand)
        else:
            page = get_page_by_title(confluence, args.title, args.space, args.expand)

        # Format output
        if args.format == 'json':
            print(format_json(page))
        else:
            print(format_page_detail(page, args.format))

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
