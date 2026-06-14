#!/usr/bin/env python3
"""Validate a KB article against the Hybrid KCS Template structure."""

import re
import sys
import os


def validate_kb_article(filepath: str) -> dict:
    """Validate a KB article file and return results."""
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    with open(filepath, "r") as f:
        content = f.read()

    results = {"passed": [], "warnings": [], "errors": []}

    # Check YAML front matter
    if content.startswith("---"):
        fm_match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            for field in ["title", "type", "category", "tags", "audience", "created", "updated"]:
                if f"{field}:" in fm:
                    results["passed"].append(f"Front matter has '{field}' field")
                else:
                    results["errors"].append(f"Front matter missing required '{field}' field")
        else:
            results["errors"].append("YAML front matter started but not properly closed")
    else:
        results["errors"].append("Missing YAML front matter (---)")

    # Check required sections
    required_sections = {
        "troubleshooting": ["Environment", "Problem", "Cause", "Resolution"],
        "how-to": ["Prerequisites", "Steps", "Verification"],
        "default": ["Environment", "Problem", "Cause", "Resolution"],
    }

    # Detect article type from front matter
    type_match = re.search(r"type:\s*(\w+)", content)
    article_type = type_match.group(1) if type_match else "default"
    sections = required_sections.get(article_type, required_sections["default"])

    found_sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    found_names = [s.strip() for s in found_sections]

    for section in sections:
        if any(section.lower() in f.lower() for f in found_names):
            results["passed"].append(f"Required section '{section}' found")
        else:
            results["errors"].append(f"Missing required section: '{section}'")

    # Check title pattern (action verb + object)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        action_verbs = [
            "Fix", "Resolve", "Clear", "Troubleshoot", "Reset", "Unlock",
            "Restore", "Recover", "Configure", "Set Up", "Enable", "Disable",
            "Optimize", "Improve", "Tune", "Install", "Deploy", "Upgrade",
            "Migrate", "How to",
        ]
        if any(title.startswith(v) for v in action_verbs):
            results["passed"].append(f"Title starts with action verb: '{title}'")
        else:
            results["warnings"].append(
                f"Title '{title}' doesn't start with a standard action verb "
                f"({', '.join(action_verbs[:5])}...)"
            )
    else:
        results["errors"].append("No H1 title found")

    # Check for error codes in quotes
    if re.search(r'["\u201c].+?["\u201d]', content) or re.search(r"^>.*error", content, re.MULTILINE | re.IGNORECASE):
        results["passed"].append("Error messages quoted or in blockquotes")
    else:
        results["warnings"].append("No quoted error messages found — include exact error text in quotes")

    # Check for numbered steps in Resolution
    resolution_match = re.search(r"## Resolution\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if resolution_match:
        resolution = resolution_match.group(1)
        if re.search(r"^\d+\.", resolution, re.MULTILINE):
            results["passed"].append("Resolution uses numbered steps")
        else:
            results["warnings"].append("Resolution should use numbered steps")

        if "expected" in resolution.lower() or "verify" in resolution.lower():
            results["passed"].append("Resolution includes verification/expected outcomes")
        else:
            results["warnings"].append("Resolution should include expected outcomes after key steps")

    # Check code blocks have language specified
    # Count opening fences only: untyped are ``` at start of line (not closing fences)
    # We track open/close state to distinguish opening from closing fences
    lines = content.split("\n")
    untyped_blocks = []
    typed_blocks = []
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                # Opening fence
                lang = stripped[3:].strip()
                if lang:
                    typed_blocks.append(lang)
                else:
                    untyped_blocks.append(i + 1)
                in_code_block = True
            else:
                # Closing fence
                in_code_block = False
    if untyped_blocks:
        results["warnings"].append(
            f"{len(untyped_blocks)} code block(s) without language specification"
        )
    if typed_blocks:
        results["passed"].append(f"{len(typed_blocks)} code block(s) have language specified")

    # Check for implicit references
    implicit_count = len(re.findall(r"\b(it|this|that|these|those)\b", content, re.IGNORECASE))
    if implicit_count > 10:
        results["warnings"].append(
            f"High use of implicit references ({implicit_count} instances of it/this/that) — "
            "prefer specific nouns for AI retrieval"
        )

    return results


def print_results(results: dict):
    """Print validation results."""
    if "error" in results:
        print(f"❌ {results['error']}")
        return 1

    print("=" * 60)
    print("KB Article Validation Results")
    print("=" * 60)

    if results["passed"]:
        print(f"\n✅ PASSED ({len(results['passed'])})")
        for item in results["passed"]:
            print(f"   ✓ {item}")

    if results["warnings"]:
        print(f"\n⚠️  WARNINGS ({len(results['warnings'])})")
        for item in results["warnings"]:
            print(f"   ⚠ {item}")

    if results["errors"]:
        print(f"\n❌ ERRORS ({len(results['errors'])})")
        for item in results["errors"]:
            print(f"   ✗ {item}")

    print("\n" + "=" * 60)
    total = len(results["passed"]) + len(results["warnings"]) + len(results["errors"])
    print(f"Score: {len(results['passed'])}/{total} checks passed")

    if results["errors"]:
        print("Status: FAIL — fix errors before publishing")
        return 1
    elif results["warnings"]:
        print("Status: PASS with warnings — review warnings before publishing")
        return 0
    else:
        print("Status: PASS — article ready for publishing")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-kb-article.md>")
        sys.exit(1)

    results = validate_kb_article(sys.argv[1])
    exit_code = print_results(results)
    sys.exit(exit_code)
