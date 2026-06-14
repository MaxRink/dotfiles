#!/usr/bin/env python3
"""
Phase 1 Analysis JSON Validator

Validates analysis.json against the code-analysis-schema JSON Schema.

Usage:
    python3 validate_analysis.py /path/to/analysis.json
    python3 validate_analysis.py /path/to/analysis.json --verbose
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema library not installed")
    print("Install with: pip3 install jsonschema")
    sys.exit(1)


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}")
        print(f"  {e}")
        sys.exit(1)


def validate_referential_integrity(data: Dict[str, Any]) -> List[str]:
    """Validate referential integrity (e.g., function.component exists)."""
    errors = []

    # Build component name set
    component_names = {comp["name"] for comp in data.get("components", [])}

    # Validate function.component references
    for func in data.get("functions", []):
        if "component" in func:
            if func["component"] not in component_names:
                errors.append(
                    f"Function '{func['name']}' references non-existent "
                    f"component '{func['component']}'"
                )

    # Validate dependency.from and dependency.to references
    for dep in data.get("dependencies", []):
        if "from" in dep and dep["from"] not in component_names:
            errors.append(
                f"Dependency references non-existent component '{dep['from']}' (from)"
            )
        if "to" in dep and dep["to"] not in component_names:
            errors.append(
                f"Dependency references non-existent component '{dep['to']}' (to)"
            )

    # Validate database_entities.accessed_by references
    for entity in data.get("database_entities", []):
        for comp_name in entity.get("accessed_by", []):
            if comp_name not in component_names:
                errors.append(
                    f"Database entity '{entity['name']}' accessed_by references "
                    f"non-existent component '{comp_name}'"
                )

    # Validate external_integrations.used_by references
    for integration in data.get("external_integrations", []):
        for comp_name in integration.get("used_by", []):
            if comp_name not in component_names:
                errors.append(
                    f"External integration '{integration['system']}' used_by references "
                    f"non-existent component '{comp_name}'"
                )

    return errors


def validate_analysis(analysis_file: str, schema_file: str, verbose: bool = False) -> bool:
    """Validate analysis.json against schema."""

    # Load files
    print(f"Loading analysis file: {analysis_file}")
    analysis_data = load_json_file(analysis_file)

    print(f"Loading schema file: {schema_file}")
    schema_data = load_json_file(schema_file)

    # Validate against JSON Schema
    print("\nValidating against JSON Schema...")
    validator = Draft7Validator(schema_data)
    errors = list(validator.iter_errors(analysis_data))

    if errors:
        print(f"\n❌ Schema validation FAILED with {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error.message}")
            if verbose:
                print(f"   Path: {' -> '.join(str(p) for p in error.path)}")
                print(f"   Schema path: {' -> '.join(str(p) for p in error.schema_path)}")
            print()
        return False
    else:
        print("✓ JSON Schema validation passed")

    # Validate referential integrity
    print("\nValidating referential integrity...")
    ref_errors = validate_referential_integrity(analysis_data)

    if ref_errors:
        print(f"\n❌ Referential integrity FAILED with {len(ref_errors)} error(s):\n")
        for i, error in enumerate(ref_errors, 1):
            print(f"{i}. {error}")
        print()
        return False
    else:
        print("✓ Referential integrity validation passed")

    # Success
    print("\n✅ All validations passed!")
    print(f"\nAnalysis summary:")
    print(f"  Feature: {analysis_data.get('feature_name')}")
    print(f"  Components: {len(analysis_data.get('components', []))}")
    print(f"  Functions: {len(analysis_data.get('functions', []))}")
    print(f"  Dependencies: {len(analysis_data.get('dependencies', []))}")
    print(f"  Database entities: {len(analysis_data.get('database_entities', []))}")
    print(f"  External integrations: {len(analysis_data.get('external_integrations', []))}")
    print(f"  Translations: {len(analysis_data.get('translations', []))}")

    if 'migration_assessment' in analysis_data:
        ma = analysis_data['migration_assessment']
        print(f"\nMigration assessment:")
        print(f"  Complexity: {ma.get('overall_complexity')}")
        print(f"  Effort (days): {ma.get('estimated_effort_days')}")
        print(f"  Risk level: {ma.get('risk_level')}")
        print(f"  Priority: {ma.get('migration_priority')}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 validate_analysis.py <analysis.json> [--verbose]")
        print("\nExample:")
        print("  python3 validate_analysis.py results/pda-import/phase1/analysis.json")
        sys.exit(1)

    analysis_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Find schema file relative to this script
    script_dir = Path(__file__).parent
    schema_file = script_dir.parent / "references" / "schema.json"

    if not schema_file.exists():
        print(f"ERROR: Schema file not found: {schema_file}")
        sys.exit(1)

    # Validate
    success = validate_analysis(
        analysis_file=analysis_file,
        schema_file=str(schema_file),
        verbose=verbose
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
