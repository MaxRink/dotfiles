#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Create Page Script
Usage: wiki-create-page.py --title "Title" [--parent-id ID] [--content "Content"] [--content-file FILE]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_confluence_client,
    ConfluenceClientError,
    validate_space,
    print_error,
    print_success,
)
from utils.config import ALLOWED_SPACES, DEFAULT_SPACE, WIKI_URL
from utils.client import handle_confluence_error
from utils.output import get_page_url


def create_page(confluence, space: str, title: str, content: str,
                parent_id: str = None, content_format: str = 'storage') -> dict:
    """
    Create a new Confluence page.

    Args:
        confluence: Confluence client instance
        space: Space key
        title: Page title
        content: Page content
        parent_id: Optional parent page ID
        content_format: Content format ('storage' or 'wiki')

    Returns:
        dict: Created page data
    """
    try:
        if parent_id:
            result = confluence.create_page(
                space=space,
                title=title,
                body=content,
                parent_id=parent_id,
                representation=content_format
            )
        else:
            result = confluence.create_page(
                space=space,
                title=title,
                body=content,
                representation=content_format
            )

        return result

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            raise ConfluenceClientError(
                f"A page with title '{title}' already exists in space {space}"
            )
        handle_confluence_error(e, "create page")


def main():
    parser = argparse.ArgumentParser(
        description='Create a new Confluence page',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --title "My New Page" --content "<p>Hello World</p>"
  %(prog)s --title "Child Page" --parent-id 12345 --content "<p>Content</p>"
  %(prog)s --title "Page from File" --content-file page-content.html
  %(prog)s --title "Wiki Page" --content "h1. Heading" --content-format wiki

Content Formats:
  storage - Confluence storage format (XHTML-like) - default
  wiki    - Confluence wiki markup

Storage Format Examples:
  <p>Paragraph text</p>
  <h1>Heading</h1>
  <ul><li>List item</li></ul>

Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--title', required=True,
                        help='Page title')
    parser.add_argument('--space', default=DEFAULT_SPACE,
                        help=f'Space key (default: {DEFAULT_SPACE})')
    parser.add_argument('--parent-id',
                        help='Parent page ID (creates as child page)')
    parser.add_argument('--content',
                        help='Page content')
    parser.add_argument('--content-file',
                        help='Read content from file')
    parser.add_argument('--content-format', choices=['storage', 'wiki'],
                        default='storage',
                        help='Content format (default: storage)')

    args = parser.parse_args()

    try:
        # Validate space
        space = validate_space(args.space)

        # Get content
        content = args.content
        if args.content_file:
            try:
                with open(args.content_file, 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                raise ConfluenceClientError(f"Content file not found: {args.content_file}")
            except IOError as e:
                raise ConfluenceClientError(f"Error reading content file: {e}")

        # Default content if none provided
        if not content:
            content = "<p>Page created by Claude Code.</p>"

        # Initialize client
        confluence = get_confluence_client()

        # Create page
        page = create_page(
            confluence,
            space=space,
            title=args.title,
            content=content,
            parent_id=args.parent_id,
            content_format=args.content_format
        )

        # Output result
        page_id = page.get('id', 'Unknown')
        title = page.get('title', args.title)
        space_key = page.get('space', {}).get('key', space)
        version = page.get('version', {}).get('number', 1)

        print_success("Page created successfully!")
        print()
        print(f"Title:   {title}")
        print(f"ID:      {page_id}")
        print(f"Space:   {space_key}")
        print(f"Version: {version}")
        print(f"URL:     {get_page_url(page_id)}")

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
