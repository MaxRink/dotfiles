#!/usr/bin/env python3
"""
PlantUML Validation Wrapper Script

This script serves as a PostToolUse hook for validating PlantUML files
after they are written by Claude Code.

Usage:
    python validate.py <file_path>

    If no file path is provided, validates the most recently modified .puml file
    in the current directory.

Exit Codes:
    0 - Validation passed
    1 - Validation failed with errors

This script can be used as a hook command in Claude Code plugin skills:

hooks:
  PostToolUse:
    - matcher: "Write"
      pattern: "*.puml"
      hooks:
        - type: command
          command: "python /path/to/validate.py"
"""

import sys
import os
import glob
from pathlib import Path

# Import from the main generator script
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from plantuml_generator import PlantUMLValidator, validate_with_plantuml_cli


def find_most_recent_puml(directory: str = ".") -> str | None:
    """Find the most recently modified .puml file in the directory"""
    puml_files = glob.glob(os.path.join(directory, "**/*.puml"), recursive=True)
    if not puml_files:
        return None
    return max(puml_files, key=os.path.getmtime)


def validate_file(file_path: str) -> bool:
    """
    Validate a PlantUML file and print results

    Args:
        file_path: Path to the .puml file

    Returns:
        True if validation passed, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        return False

    print(f"Validating PlantUML file: {file_path}")
    print("-" * 60)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read file: {e}", file=sys.stderr)
        return False

    # Tier 1: Regex-based validation
    validator = PlantUMLValidator()
    result = validator.validate(content)

    if result.errors:
        print("TIER 1 ERRORS (Regex validation):")
        for error in result.errors:
            print(f"  - {error}")
        print()

    if result.warnings:
        print("TIER 1 WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")
        print()

    if not result.valid:
        print("FAILED: Tier 1 validation found errors")
        return False

    print("PASSED: Tier 1 validation (regex-based)")

    # Tier 2: PlantUML CLI validation (if available)
    cli_valid, cli_error = validate_with_plantuml_cli(file_path)

    if cli_error:
        if "not installed" in cli_error.lower() or "unavailable" in cli_error.lower():
            print(f"INFO: Tier 2 validation skipped - {cli_error}")
        else:
            print(f"TIER 2 ERROR: {cli_error}")
            return False
    else:
        print("PASSED: Tier 2 validation (PlantUML CLI)")

    print("-" * 60)
    print(f"SUCCESS: {file_path} is valid PlantUML")
    return True


def main():
    """Main entry point"""
    # Get file path from argument or find most recent
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Try to find most recent .puml file
        file_path = find_most_recent_puml()
        if not file_path:
            print("ERROR: No .puml files found and no file path provided", file=sys.stderr)
            print("Usage: python validate.py <file_path>")
            sys.exit(1)

    # Run validation
    if validate_file(file_path):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
