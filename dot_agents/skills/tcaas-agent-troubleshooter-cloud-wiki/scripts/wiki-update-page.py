#!/usr/bin/env python3
"""
Telekom Wiki (Confluence) Update Page Script
Usage: wiki-update-page.py --id PAGE_ID [--title "Title"] [--content "Content"] [--content-file FILE]
"""

import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from utils import (
    get_confluence_client,
    ConfluenceClientError,
    validate_page_in_allowed_space,
    print_error,
    print_success,
)
from utils.config import ALLOWED_SPACES
from utils.client import handle_confluence_error
from utils.output import get_page_url


def get_page_info(confluence, page_id: str) -> tuple:
    """
    Get current page information for update.

    Args:
        confluence: Confluence client instance
        page_id: Page ID

    Returns:
        tuple: (space_key, current_version, current_title, current_content)
    """
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,version,space')

        if not page:
            raise ConfluenceClientError(f"Page '{page_id}' not found")

        # Validate space
        space_key = validate_page_in_allowed_space(page)

        version = page.get('version', {}).get('number', 0)
        title = page.get('title', '')
        content = page.get('body', {}).get('storage', {}).get('value', '')

        return space_key, version, title, content

    except ValueError as e:
        raise ConfluenceClientError(str(e))
    except Exception as e:
        if "404" in str(e):
            raise ConfluenceClientError(
                f"Page '{page_id}' not found or you don't have permission to view it."
            )
        handle_confluence_error(e, "get page")


def update_page(confluence, page_id: str, space_key: str, title: str,
                content: str, version: int) -> dict:
    """
    Update a Confluence page.

    Args:
        confluence: Confluence client instance
        page_id: Page ID
        space_key: Space key
        title: Page title
        content: Page content
        version: Current version number (will be incremented)

    Returns:
        dict: Updated page data
    """
    try:
        result = confluence.update_page(
            page_id=page_id,
            title=title,
            body=content,
            representation='storage'
        )

        return result

    except Exception as e:
        error_msg = str(e)
        if "409" in error_msg:
            raise ConfluenceClientError(
                "Version conflict. The page may have been modified by another user.\n"
                "Try fetching the latest version and retrying."
            )
        handle_confluence_error(e, "update page")


def main():
    parser = argparse.ArgumentParser(
        description='Update a Confluence page',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --id 12345 --content "<p>Updated content</p>"
  %(prog)s --id 12345 --title "New Page Title"
  %(prog)s --id 12345 --content-file updated-content.html

Note: The version number is automatically incremented.

Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}
        """
    )

    parser.add_argument('--id', required=True,
                        help='Page ID to update')
    parser.add_argument('--title',
                        help='New page title')
    parser.add_argument('--content',
                        help='New page content')
    parser.add_argument('--content-file',
                        help='Read content from file')

    args = parser.parse_args()

    # Check if any update was specified
    if not args.title and not args.content and not args.content_file:
        print_error("At least one of --title, --content, or --content-file is required")
        sys.exit(1)

    try:
        # Get content from file if specified
        new_content = args.content
        if args.content_file:
            try:
                with open(args.content_file, 'r') as f:
                    new_content = f.read()
            except FileNotFoundError:
                raise ConfluenceClientError(f"Content file not found: {args.content_file}")
            except IOError as e:
                raise ConfluenceClientError(f"Error reading content file: {e}")

        # Initialize client
        confluence = get_confluence_client()

        # Get current page info
        space_key, current_version, current_title, current_content = get_page_info(
            confluence, args.id
        )

        # Use current values if not updating
        title = args.title if args.title else current_title
        content = new_content if new_content else current_content

        # Update page
        page = update_page(
            confluence,
            page_id=args.id,
            space_key=space_key,
            title=title,
            content=content,
            version=current_version
        )

        # Output result
        page_id = page.get('id', args.id)
        new_title = page.get('title', title)
        space = page.get('space', {}).get('key', space_key)
        new_version = page.get('version', {}).get('number', current_version + 1)

        print_success("Page updated successfully!")
        print()
        print(f"Title:   {new_title}")
        print(f"ID:      {page_id}")
        print(f"Space:   {space}")
        print(f"Version: {new_version} (was {current_version})")
        print(f"URL:     {get_page_url(page_id)}")

    except (ConfluenceClientError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()
