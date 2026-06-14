"""Input validation utilities for Telekom Wiki (Confluence) integration."""

from typing import Dict, Any

from .config import ALLOWED_SPACES, DEFAULT_SPACE


def validate_space(space: str) -> str:
    """
    Validate and normalize a space key.

    Args:
        space: Space key to validate

    Returns:
        str: Normalized space key (uppercase)

    Raises:
        ValueError: If space is not in allowed list
    """
    space_upper = space.upper()

    if space_upper not in ALLOWED_SPACES:
        raise ValueError(
            f"Space '{space}' is not allowed.\n"
            f"Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}"
        )

    return space_upper


def validate_page_in_allowed_space(page_data: Dict[str, Any]) -> str:
    """
    Validate that a page belongs to an allowed space.

    Args:
        page_data: Page data dictionary from Confluence API

    Returns:
        str: Space key of the page

    Raises:
        ValueError: If page belongs to disallowed space
    """
    space_key = page_data.get('space', {}).get('key', '')

    if not space_key:
        raise ValueError("Could not determine page space from API response")

    if space_key.upper() not in ALLOWED_SPACES:
        raise ValueError(
            f"Page belongs to space '{space_key}', which is not allowed.\n"
            f"Allowed spaces: {', '.join(sorted(ALLOWED_SPACES))}"
        )

    return space_key


def get_default_space() -> str:
    """Get the default space key."""
    return DEFAULT_SPACE


def build_space_filter(space: str = None) -> str:
    """
    Build a CQL space filter clause.

    Args:
        space: Optional specific space key

    Returns:
        str: CQL space filter clause
    """
    if space:
        validated_space = validate_space(space)
        return f"space = {validated_space}"
    else:
        # Search across all allowed spaces
        spaces_list = ', '.join(sorted(ALLOWED_SPACES))
        return f"space in ({spaces_list})"
