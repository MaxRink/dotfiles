"""Telekom Wiki (Confluence) utility modules."""

from .config import WIKI_URL, ALLOWED_SPACES
from .client import get_confluence_client, ConfluenceClientError
from .validators import validate_space, validate_page_in_allowed_space
from .output import (
    format_pages_table,
    format_page_detail,
    format_page_tree,
    format_json,
    confluence_to_markdown,
    print_error,
    print_success,
)

__all__ = [
    "WIKI_URL",
    "ALLOWED_SPACES",
    "get_confluence_client",
    "ConfluenceClientError",
    "validate_space",
    "validate_page_in_allowed_space",
    "format_pages_table",
    "format_page_detail",
    "format_page_tree",
    "format_json",
    "confluence_to_markdown",
    "print_error",
    "print_success",
]
