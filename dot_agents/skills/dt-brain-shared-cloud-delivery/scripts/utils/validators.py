"""
Input validation utilities for TDI Cloud Delivery skill.
"""

import sys
from .config import ALLOWED_GROUPS


def validate_group_path(group_path):
    """
    Validate that a group path is in the allowed list.

    Args:
        group_path: The group path to validate

    Returns:
        bool: True if valid

    Exits with error if invalid.
    """
    # Normalize path (remove leading/trailing slashes)
    normalized = group_path.strip("/").lower()

    for allowed in ALLOWED_GROUPS:
        allowed_normalized = allowed.strip("/").lower()
        # Check exact match or subgroup
        if normalized == allowed_normalized or normalized.startswith(allowed_normalized + "/"):
            return True

    print(f"Error: Group '{group_path}' is not in the allowed list.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Allowed groups:", file=sys.stderr)
    for allowed in ALLOWED_GROUPS:
        print(f"  - {allowed}", file=sys.stderr)
    sys.exit(1)


def validate_positive_int(value, name="value"):
    """
    Validate that a value is a positive integer.

    Args:
        value: The value to validate
        name: Name for error messages

    Returns:
        int: The validated integer

    Exits with error if invalid.
    """
    try:
        int_val = int(value)
        if int_val <= 0:
            raise ValueError()
        return int_val
    except (ValueError, TypeError):
        print(f"Error: {name} must be a positive integer, got '{value}'", file=sys.stderr)
        sys.exit(1)


def validate_state(state):
    """
    Validate epic/issue state parameter.

    Args:
        state: The state to validate

    Returns:
        str: The validated state

    Exits with error if invalid.
    """
    valid_states = ["opened", "closed", "all"]
    if state.lower() not in valid_states:
        print(f"Error: Invalid state '{state}'", file=sys.stderr)
        print(f"Valid states: {', '.join(valid_states)}", file=sys.stderr)
        sys.exit(1)
    return state.lower()
