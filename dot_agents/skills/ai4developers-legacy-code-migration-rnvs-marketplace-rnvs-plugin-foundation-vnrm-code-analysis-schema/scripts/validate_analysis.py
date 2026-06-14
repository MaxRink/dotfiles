#!/usr/bin/env python3
"""
VNRM Microservice Analysis JSON Validator

Validates VNRM microservice analysis.json against the vnrm-code-analysis-schema JSON Schema.

Usage:
    python3 validate_analysis.py /path/to/analysis.json
    python3 validate_analysis.py /path/to/analysis.json --verbose
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

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


def validate_vnrm_business_logic(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate VNRM-specific business logic and data integrity."""
    errors = []
    warnings = []

    # Validate service_name format (kebab-case)
    service_name = data.get("service_name", "")
    if service_name and not service_name.replace("-", "").replace("_", "").isalnum():
        errors.append(f"service_name '{service_name}' should be in kebab-case")

    # Validate vnrm_submodule is valid
    valid_submodules = ["COM", "NUM", "PRT", "COR", "SPE", "NTW"]
    submodule = data.get("vnrm_submodule", "")
    if submodule and submodule not in valid_submodules:
        errors.append(
            f"vnrm_submodule '{submodule}' must be one of {valid_submodules}"
        )

    # Validate API endpoints have proper versioning
    for api in data.get("api_contracts", []):
        endpoint = api.get("endpoint", "")
        if endpoint and not endpoint.startswith("/api/v"):
            warnings.append(
                f"API endpoint '{endpoint}' should follow /api/vN/ pattern"
            )

    # Validate state machine transitions reference valid states
    for state_machine in data.get("database_schema", {}).get("state_machines", []):
        entity = state_machine.get("entity", "unknown")
        valid_states = set(state_machine.get("states", []))

        for transition in state_machine.get("transitions", []):
            from_state = transition.get("from")
            to_state = transition.get("to")

            if from_state and from_state != "ANY" and from_state not in valid_states:
                errors.append(
                    f"State machine '{entity}': transition 'from' state '{from_state}' "
                    f"not in valid states {valid_states}"
                )

            if to_state and to_state not in valid_states:
                errors.append(
                    f"State machine '{entity}': transition 'to' state '{to_state}' "
                    f"not in valid states {valid_states}"
                )

    # Validate integration patterns have required fields based on type
    for integration in data.get("integration_patterns", []):
        int_type = integration.get("type")
        protocol = integration.get("protocol")

        # Service dependencies should have circuit breaker and timeout
        if int_type == "service_dependency":
            if "circuit_breaker" not in integration:
                warnings.append(
                    f"Service dependency '{integration.get('target_service')}' "
                    f"should specify circuit_breaker"
                )
            if "timeout" not in integration:
                warnings.append(
                    f"Service dependency '{integration.get('target_service')}' "
                    f"should specify timeout"
                )

    return errors, warnings


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

    # Validate VNRM business logic
    print("\nValidating VNRM business logic...")
    logic_errors, logic_warnings = validate_vnrm_business_logic(analysis_data)

    if logic_errors:
        print(f"\n❌ Business logic validation FAILED with {len(logic_errors)} error(s):\n")
        for i, error in enumerate(logic_errors, 1):
            print(f"{i}. {error}")
        print()
        return False
    else:
        print("✓ Business logic validation passed")

    if logic_warnings:
        print(f"\n⚠️  Found {len(logic_warnings)} warning(s):")
        for i, warning in enumerate(logic_warnings, 1):
            print(f"{i}. {warning}")
        print()

    # Success
    print("\n✅ All validations passed!")
    print(f"\nAnalysis summary:")
    print(f"  Service: {analysis_data.get('service_name')}")
    print(f"  VNRM Submodule: {analysis_data.get('vnrm_submodule')}")
    print(f"  Analysis timestamp: {analysis_data.get('analysis_timestamp')}")

    # Technology stack
    tech_stack = analysis_data.get('technology_stack', {})
    if tech_stack:
        print(f"\nTechnology stack:")
        print(f"  Spring Boot: {tech_stack.get('spring_boot_version')}")
        print(f"  Java: {tech_stack.get('java_version')}")
        print(f"  Database: {tech_stack.get('database')}")
        print(f"  Messaging: {tech_stack.get('messaging', 'N/A')}")

    # API and data
    print(f"\nAPI and Data:")
    print(f"  API endpoints: {len(analysis_data.get('api_contracts', []))}")

    db_schema = analysis_data.get('database_schema', {})
    print(f"  Database tables: {len(db_schema.get('tables', []))}")
    print(f"  State machines: {len(db_schema.get('state_machines', []))}")

    # Integrations
    print(f"  Integration patterns: {len(analysis_data.get('integration_patterns', []))}")

    # Operational
    operational = analysis_data.get('operational_metrics', {})
    if operational:
        print(f"\nOperational metrics:")
        print(f"  Service level: {operational.get('service_level')}")
        print(f"  Availability target: {operational.get('availability_target')}")
        print(f"  Response time target: {operational.get('response_time_target')}")

    # Compliance
    compliance = analysis_data.get('compliance_requirements', [])
    if compliance:
        print(f"\nCompliance:")
        compliance_types = [c.get('type') for c in compliance]
        print(f"  Requirements: {', '.join(compliance_types)}")

    # Enhancement opportunities
    enhancements = analysis_data.get('enhancement_opportunities', {})
    if enhancements:
        total_enhancements = sum(len(v) for v in enhancements.values() if isinstance(v, list))
        print(f"\nEnhancement opportunities: {total_enhancements}")
        for category, items in enhancements.items():
            if isinstance(items, list):
                print(f"  {category.capitalize()}: {len(items)}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 validate_analysis.py <analysis.json> [--verbose]")
        print("\nExample:")
        print("  python3 validate_analysis.py results/num-service/phase11/analysis.json")
        print("  python3 validate_analysis.py ../references/vnrm-example.json --verbose")
        sys.exit(1)

    analysis_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Find schema file relative to this script
    script_dir = Path(__file__).parent
    schema_file = script_dir.parent / "references" / "vnrm-schema.json"

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
