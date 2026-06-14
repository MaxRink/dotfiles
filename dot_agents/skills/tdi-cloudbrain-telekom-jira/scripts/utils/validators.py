"""Input validation utilities for Telekom Jira integration."""

import re
from typing import Set, Optional

from .config import ALLOWED_PROJECTS, PROJECT_ALIASES


def validate_project(project: str) -> str:
    """
    Validate and normalize a project key.

    Args:
        project: Project key or alias

    Returns:
        str: Normalized project key (uppercase)

    Raises:
        ValueError: If project is not in allowed list
    """
    # Check if it's an alias first
    project_lower = project.lower()
    if project_lower in PROJECT_ALIASES:
        project = PROJECT_ALIASES[project_lower]

    # Normalize to uppercase
    project_upper = project.upper()

    if project_upper not in ALLOWED_PROJECTS:
        raise ValueError(
            f"Project '{project}' is not allowed.\n"
            f"Allowed projects: {', '.join(sorted(ALLOWED_PROJECTS))}"
        )

    return project_upper


def validate_issue_key(issue_key: str) -> str:
    """
    Validate an issue key format and extract/validate the project.

    Args:
        issue_key: Jira issue key (e.g., TCAAS-123)

    Returns:
        str: Normalized issue key (uppercase)

    Raises:
        ValueError: If format is invalid or project not allowed
    """
    # Normalize to uppercase
    issue_key = issue_key.upper()

    # Validate format
    pattern = r'^([A-Z]+)-(\d+)$'
    match = re.match(pattern, issue_key)

    if not match:
        raise ValueError(
            f"Invalid issue key format: '{issue_key}'\n"
            "Expected format: PROJECT-123 (e.g., TCAAS-456)"
        )

    project = match.group(1)

    if project not in ALLOWED_PROJECTS:
        raise ValueError(
            f"Issue '{issue_key}' belongs to project '{project}' which is not allowed.\n"
            f"Allowed projects: {', '.join(sorted(ALLOWED_PROJECTS))}"
        )

    return issue_key


def validate_jql_projects(jql: str) -> None:
    """
    Validate that a JQL query only references allowed projects.

    This is a security check to prevent querying unauthorized projects.

    Args:
        jql: JQL query string

    Raises:
        ValueError: If JQL references disallowed projects
    """
    jql_lower = jql.lower()

    # Check for project = X pattern
    single_project_pattern = r'project\s*=\s*([A-Za-z0-9]+)'
    for match in re.finditer(single_project_pattern, jql, re.IGNORECASE):
        project = match.group(1).upper()
        if project not in ALLOWED_PROJECTS:
            raise ValueError(
                f"Project '{project}' in JQL is not allowed.\n"
                f"Allowed projects: {', '.join(sorted(ALLOWED_PROJECTS))}"
            )

    # Check for project in (X, Y, Z) pattern
    multi_project_pattern = r'project\s+in\s*\(([^)]+)\)'
    for match in re.finditer(multi_project_pattern, jql, re.IGNORECASE):
        projects_str = match.group(1)
        # Split by comma and clean up
        projects = [p.strip().strip('"\'').upper() for p in projects_str.split(',')]
        for project in projects:
            if project and project not in ALLOWED_PROJECTS:
                raise ValueError(
                    f"Project '{project}' in JQL is not allowed.\n"
                    f"Allowed projects: {', '.join(sorted(ALLOWED_PROJECTS))}"
                )


def validate_labels(labels: str) -> list:
    """
    Parse and validate a comma-separated labels string.

    Args:
        labels: Comma-separated labels

    Returns:
        list: List of label strings
    """
    if not labels:
        return []
    return [label.strip() for label in labels.split(',') if label.strip()]


def validate_date(date_str: str, field_name: str = "date") -> str:
    """
    Validate a date string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate
        field_name: Name of field for error message

    Returns:
        str: Validated date string

    Raises:
        ValueError: If date format is invalid
    """
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        raise ValueError(
            f"Invalid {field_name} format: '{date_str}'\n"
            "Expected format: YYYY-MM-DD (e.g., 2026-01-29)"
        )
    return date_str
