#!/usr/bin/env python3
"""
PlantUML Generator and Validator

This script provides functionality to generate and validate PlantUML diagrams
for RNVS/VNRM architecture visualization. Supports component, activity, and
sequence diagrams with consistent color schemes.

Usage:
    # Generate a component diagram
    python plantuml_generator.py generate component --input data.json --output diagram.puml

    # Generate an activity diagram
    python plantuml_generator.py generate activity --input data.json --output diagram.puml

    # Generate a sequence diagram
    python plantuml_generator.py generate sequence --input data.json --output diagram.puml

    # Validate a PlantUML file
    python plantuml_generator.py validate --file diagram.puml
"""

import argparse
import json
import re
import sys
import subprocess
import shutil
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# RNVS/VNRM Standard Color Scheme
DEFAULT_COLOR_SCHEME = {
    "database": "#FFE6CC",  # Orange - Persistence, data storage
    "business": "#CCE5FF",  # Blue - Core processing, rules
    "integration": "#D5E8D4",  # Green - External APIs, message queues
    "presentation": "#F8CECC",  # Red - UI, API Gateway
    "external": "#E1D5E7",  # Purple - Third-party systems
    "error": "#F8CECC",  # Red - Error paths
    "warning": "#FFF4CC",  # Yellow - Warning states
}


@dataclass
class ValidationResult:
    """Result of PlantUML syntax validation"""

    valid: bool
    errors: List[str]
    warnings: List[str]


def validate_with_plantuml_cli(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate PlantUML diagram using official PlantUML CLI (Tier 2 validation)

    Args:
        file_path: Path to the PlantUML file to validate

    Returns:
        Tuple of (is_valid, error_message)
        Returns (True, None) if valid or CLI not available
    """
    # Check if PlantUML CLI is installed
    if not shutil.which("plantuml"):
        return True, None  # Skip validation if CLI not installed

    try:
        # Run PlantUML syntax check
        result = subprocess.run(
            ["plantuml", "-syntax", file_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True, None
        else:
            # Extract error message from stderr
            error_msg = (
                result.stderr.strip() if result.stderr else "Unknown syntax error"
            )
            return False, f"PlantUML CLI validation failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return True, "PlantUML CLI validation timed out (skipped)"
    except Exception as e:
        return True, f"PlantUML CLI validation unavailable: {str(e)}"


class PlantUMLValidator:
    """Validates PlantUML diagram syntax"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, content: str) -> ValidationResult:
        """
        Validate PlantUML syntax

        Args:
            content: PlantUML diagram content

        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []

        lines = content.split("\n")

        # Check basic structure
        self._check_start_end_tags(content)
        self._check_unclosed_blocks(lines)
        self._check_color_codes(lines)
        self._check_quotes_brackets(lines)
        self._check_activity_diagram_rules(lines, content)
        self._check_sequence_diagram_rules(lines, content)
        self._check_stereotypes(lines)

        return ValidationResult(
            valid=len(self.errors) == 0, errors=self.errors, warnings=self.warnings
        )

    def _check_start_end_tags(self, content: str):
        """Check for matching @startuml and @enduml tags"""
        start_count = content.count("@startuml")
        end_count = content.count("@enduml")

        if start_count == 0:
            self.errors.append("Missing @startuml tag")
        if end_count == 0:
            self.errors.append("Missing @enduml tag")
        if start_count != end_count:
            self.errors.append(
                f"Mismatched @startuml ({start_count}) and @enduml ({end_count}) tags"
            )

    def _check_unclosed_blocks(self, lines: List[str]):
        """Check for unclosed if/endif, loop/endloop, etc."""
        stack = []
        block_pairs = {
            "if": "endif",
            "while": "endwhile",
            "repeat": "repeat while",
            "fork": "end fork",
        }

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Check for opening blocks
            for opener, closer in block_pairs.items():
                if re.match(rf"\b{opener}\b", line):
                    stack.append((opener, closer, i))

            # Check for closing blocks
            for opener, closer in block_pairs.items():
                if closer in line:
                    if not stack or stack[-1][0] != opener:
                        # Only warn if it's actually wrong, not for "end note" etc
                        if (
                            closer == "endif"
                            or closer == "endwhile"
                            or "repeat while" in line
                        ):
                            self.warnings.append(
                                f"Line {i}: Unexpected '{closer}' without matching '{opener}'"
                            )
                    elif stack:
                        stack.pop()

        # Check for unclosed blocks
        for opener, closer, line_num in stack:
            self.errors.append(
                f"Line {line_num}: Unclosed '{opener}' block (missing '{closer}')"
            )

    def _check_color_codes(self, lines: List[str]):
        """Check for valid hex color codes"""
        invalid_color_pattern = re.compile(
            r"#[0-9A-Fa-f]{1,2}(?![0-9A-Fa-f])|#[0-9A-Fa-f]{4,5}(?![0-9A-Fa-f])|#[0-9A-Fa-f]{7,}"
        )

        for i, line in enumerate(lines, 1):
            # Check for invalid color codes
            invalid_matches = invalid_color_pattern.findall(line)
            if invalid_matches:
                self.errors.append(
                    f"Line {i}: Invalid color code format. Use #RGB or #RRGGBB"
                )

    def _check_quotes_brackets(self, lines: List[str]):
        """Check for unclosed quotes and brackets"""
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("'"):
                continue

            # Check quotes
            quote_count = line.count('"')
            if quote_count % 2 != 0:
                self.warnings.append(f"Line {i}: Unclosed double quote")

            # Check brackets
            open_brackets = line.count("[")
            close_brackets = line.count("]")
            if open_brackets != close_brackets:
                self.warnings.append(f"Line {i}: Mismatched square brackets")

            # Check parentheses
            open_parens = line.count("(")
            close_parens = line.count(")")
            if open_parens != close_parens:
                self.warnings.append(f"Line {i}: Mismatched parentheses")

    def _check_activity_diagram_rules(self, lines: List[str], content: str):
        """Check activity diagram specific rules"""
        if ":" in content and ";" in content:  # Likely an activity diagram
            has_start = any("start" in line for line in lines)
            has_stop = any("stop" in line or "end" in line for line in lines)

            if not has_start:
                self.warnings.append("Activity diagram should have 'start'")
            if not has_stop:
                self.warnings.append("Activity diagram should have 'stop' or 'end'")

            # Check for activities without semicolons
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if (
                    line.startswith(":")
                    and not line.endswith(";")
                    and not line.endswith("}")
                ):
                    self.errors.append(f"Line {i}: Activity missing semicolon at end")

    def _check_sequence_diagram_rules(self, lines: List[str], content: str):
        """Check sequence diagram specific rules"""
        if "participant" in content or "->" in content:
            # Check for activation/deactivation pairing
            activation_count = content.count("activate ")
            deactivation_count = content.count("deactivate ")

            if activation_count != deactivation_count:
                self.warnings.append(
                    f"Mismatched activate ({activation_count}) and deactivate ({deactivation_count}) calls"
                )

    def _check_stereotypes(self, lines: List[str]):
        """Check that stereotypes are properly defined in skinparam"""
        used_stereotypes = set()
        defined_stereotypes = set()

        for line in lines:
            # Find used stereotypes: <<type>>
            used_matches = re.findall(r"<<(\w+)>>", line)
            used_stereotypes.update(used_matches)

            # Find defined stereotypes in skinparam
            if "BackgroundColor<<" in line:
                defined_matches = re.findall(r"BackgroundColor<<(\w+)>>", line)
                defined_stereotypes.update(defined_matches)

        # Check for undefined stereotypes
        undefined = used_stereotypes - defined_stereotypes
        if undefined:
            self.warnings.append(
                f"Stereotypes used but not defined in skinparam: {', '.join(undefined)}"
            )


class ComponentDiagramGenerator:
    """Generates PlantUML component diagrams"""

    def __init__(self, color_scheme: Dict[str, str] | None = None):
        self.color_scheme = (
            color_scheme if color_scheme is not None else DEFAULT_COLOR_SCHEME
        )

    def _escape_label(self, label: str) -> str:
        """
        Escape newline characters in labels to preserve them as literal \\n in PlantUML.

        PlantUML interprets actual newline characters as statement terminators, causing
        syntax errors. This method converts newline characters to the literal string \\n
        which PlantUML will render as a line break in the diagram.

        Args:
            label: The label text that may contain newline characters

        Returns:
            Label with newlines escaped as \\n
        """
        return label.replace('\n', '\\n')

    def generate(
        self,
        components: List[Dict],
        dependencies: List[Dict],
        title: str = "Component Diagram",
    ) -> str:
        """
        Generate a component diagram

        Args:
            components: List of {name, type, description}
            dependencies: List of {from, to, label}
            title: Diagram title

        Returns:
            PlantUML diagram string
        """
        lines = [
            "@startuml",
            "' Layout optimization",
            "!pragma layout smetana",
            "skinparam linetype ortho",
            "skinparam nodesep 100",
            "skinparam ranksep 100",
            "!theme plain",
            f"title {title}",
            "",
            "' Color scheme",
            "skinparam component {",
        ]

        # Add color definitions for used types
        used_types = {c["type"] for c in components}
        for type_name in sorted(used_types):
            if type_name in self.color_scheme:
                lines.append(
                    f"  BackgroundColor<<{type_name}>> {self.color_scheme[type_name]}"
                )

        lines.append("}")
        lines.append("")
        lines.append("' Components")

        # Add components
        for comp in components:
            name = comp["name"]
            comp_type = comp["type"]

            if comp_type == "database":
                lines.append(f'database "{name}" <<{comp_type}>>')
            else:
                lines.append(f"[{name}] <<{comp_type}>>")

            if "description" in comp and comp["description"]:
                lines.append(f"note right of [{name}]")
                lines.append(f"  {comp['description']}")
                lines.append("end note")

        lines.append("")
        lines.append("' Dependencies")

        # Add dependencies
        for dep in dependencies:
            from_comp = dep["from"]
            to_comp = dep["to"]
            label = dep.get("label", "")

            if label:
                # Escape newlines to prevent PlantUML syntax errors
                escaped_label = self._escape_label(label)
                lines.append(f"[{from_comp}] --> [{to_comp}] : {escaped_label}")
            else:
                lines.append(f"[{from_comp}] --> [{to_comp}]")

        # Add legend
        lines.append("")
        lines.append("legend right")
        for type_name in sorted(used_types):
            if type_name in self.color_scheme:
                color = self.color_scheme[type_name]
                label = type_name.replace("_", " ").title()
                lines.append(f"  |<back:{color}>   </back>| {label} |")
        lines.append("endlegend")

        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)


class ActivityDiagramGenerator:
    """Generates PlantUML activity diagrams"""

    def __init__(self, color_scheme: Dict[str, str] | None = None):
        self.color_scheme = (
            color_scheme if color_scheme is not None else DEFAULT_COLOR_SCHEME
        )

    def _escape_label(self, label: str) -> str:
        """
        Escape newline characters in labels to preserve them as literal \\n in PlantUML.

        Args:
            label: The label text that may contain newline characters

        Returns:
            Label with newlines escaped as \\n
        """
        return label.replace('\n', '\\n')

    def generate(
        self,
        steps: List[Dict],
        decisions: List[Dict] | None = None,
        title: str = "Activity Diagram",
        use_swimlanes: bool = False,
        swimlanes: List[str] | None = None,
    ) -> str:
        """
        Generate an activity diagram

        Args:
            steps: List of {name, type, notes?, swimlane?}
            decisions: List of {condition, yes_path, no_path}
            title: Diagram title
            use_swimlanes: Whether to use swimlanes
            swimlanes: List of swimlane names

        Returns:
            PlantUML diagram string
        """
        lines = [
            "@startuml",
            "' Layout optimization",
            "!pragma layout smetana",
            "!theme plain",
            f"title {title}",
            "",
        ]

        current_swimlane = None

        if use_swimlanes and swimlanes:
            lines.append(f"|{swimlanes[0]}|")
            current_swimlane = swimlanes[0]

        lines.append("start")
        lines.append("")

        # Add steps
        for step in steps:
            # Flexible field access - try different field names
            name = step.get("name") or step.get("activity") or step.get("step") or "Unknown Step"
            step_type = step.get("type", "business")
            notes = step.get("notes")
            swimlane = step.get("swimlane")

            # Switch swimlane if needed
            if use_swimlanes and swimlane and swimlane != current_swimlane:
                lines.append(f"|{swimlane}|")
                current_swimlane = swimlane

            # Escape newlines to prevent PlantUML syntax errors
            escaped_name = self._escape_label(name)

            # Add activity without stereotypes (stereotypes cause warnings in activity diagrams)
            lines.append(f":{escaped_name};")

            # Add notes if present
            if notes:
                lines.append("note right")
                lines.append(f"  {notes}")
                lines.append("end note")
            lines.append("")

        # Add decisions if provided
        if decisions:
            for decision in decisions:
                condition = decision.get("condition", "Decision")
                yes_path = decision.get("yes_path", "Continue")
                no_path = decision.get("no_path", "Alternative")

                # Escape newlines to prevent PlantUML syntax errors
                escaped_condition = self._escape_label(condition)
                escaped_yes_path = self._escape_label(yes_path)
                escaped_no_path = self._escape_label(no_path)

                lines.append(f"if ({escaped_condition}) then (yes)")
                lines.append(f"  :{escaped_yes_path};")
                lines.append("else (no)")
                lines.append(f"  :{escaped_no_path};")
                lines.append("endif")
                lines.append("")

        lines.append("stop")
        lines.append("@enduml")

        return "\n".join(lines)


class SequenceDiagramGenerator:
    """Generates PlantUML sequence diagrams"""

    def _escape_label(self, label: str) -> str:
        """
        Escape newline characters in labels to preserve them as literal \\n in PlantUML.

        Args:
            label: The label text that may contain newline characters

        Returns:
            Label with newlines escaped as \\n
        """
        return label.replace('\n', '\\n')

    def generate(
        self,
        participants: List[str],
        interactions: List[Dict],
        title: str = "Sequence Diagram",
    ) -> str:
        """
        Generate a sequence diagram

        Args:
            participants: List of participant names
            interactions: List of {from, to, message, type?}
            title: Diagram title

        Returns:
            PlantUML diagram string
        """
        lines = [
            "@startuml",
            "' Layout optimization",
            "!pragma layout smetana",
            "skinparam responseMessageBelowArrow true",
            "!theme plain",
            f"title {title}",
            "",
        ]

        # Add participants
        for participant in participants:
            lines.append(
                f'participant "{participant}" as {self._sanitize_alias(participant)}'
            )

        lines.append("")

        # Add interactions
        for interaction in interactions:
            from_participant = self._sanitize_alias(interaction["from"])
            to_participant = self._sanitize_alias(interaction["to"])
            message = interaction["message"]
            interaction_type = interaction.get("type", "normal")

            # Determine arrow type
            if interaction_type == "return":
                arrow = "-->"
            elif interaction_type == "async":
                arrow = "->>"
            else:
                arrow = "->"

            # Escape newlines to prevent PlantUML syntax errors
            escaped_message = self._escape_label(message)
            lines.append(f"{from_participant} {arrow} {to_participant}: {escaped_message}")

            # Add activation if specified
            if interaction.get("activate"):
                lines.append(f"activate {to_participant}")
            if interaction.get("deactivate"):
                lines.append(f"deactivate {to_participant}")

        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

    def _sanitize_alias(self, name: str) -> str:
        """Convert participant name to valid alias"""
        return name.replace(" ", "").replace("-", "_")


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="PlantUML Generator and Validator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate PlantUML diagram"
    )
    generate_parser.add_argument(
        "diagram_type",
        choices=["component", "activity", "sequence"],
        help="Type of diagram to generate",
    )
    generate_parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file with diagram data"
    )
    generate_parser.add_argument(
        "--output", "-o", required=True, help="Output PlantUML file"
    )
    generate_parser.add_argument("--title", "-t", default=None, help="Diagram title")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate PlantUML syntax")
    validate_parser.add_argument(
        "--file", "-f", required=True, help="PlantUML file to validate"
    )

    args = parser.parse_args()

    if args.command == "generate":
        generate_diagram(args)
    elif args.command == "validate":
        validate_diagram(args)
    else:
        parser.print_help()
        sys.exit(1)


def generate_diagram(args):
    """Generate a PlantUML diagram"""
    diagram = ""
    try:
        with open(args.input, "r") as f:
            data = json.load(f)

        title = args.title or data.get("title", f"{args.diagram_type.title()} Diagram")
        color_scheme = data.get("color_scheme", DEFAULT_COLOR_SCHEME)

        if args.diagram_type == "component":
            generator = ComponentDiagramGenerator(color_scheme)
            diagram = generator.generate(
                components=data["components"],
                dependencies=data["dependencies"],
                title=title,
            )
        elif args.diagram_type == "activity":
            generator = ActivityDiagramGenerator(color_scheme)
            diagram = generator.generate(
                steps=data["steps"],
                decisions=data.get("decisions", []),
                title=title,
                use_swimlanes=data.get("use_swimlanes", False),
                swimlanes=data.get("swimlanes", []),
            )
        elif args.diagram_type == "sequence":
            generator = SequenceDiagramGenerator()
            diagram = generator.generate(
                participants=data["participants"],
                interactions=data["interactions"],
                title=title,
            )
        else:
            print(f"ERROR: Unknown diagram type '{args.diagram_type}'", file=sys.stderr)
            sys.exit(1)

        # Tier 1: Built-in regex validation (fast, detailed)
        print("Running Tier 1 validation (regex-based)...")
        validator = PlantUMLValidator()
        result = validator.validate(diagram)

        if not result.valid:
            print("ERROR: Generated diagram has validation errors:", file=sys.stderr)
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        if result.warnings:
            print("WARNING: Tier 1 warnings:", file=sys.stderr)
            for warning in result.warnings:
                print(f"  - {warning}", file=sys.stderr)
        else:
            print("SUCCESS: Tier 1 validation passed")

        # Save diagram
        with open(args.output, "w") as f:
            f.write(diagram)

        # Tier 2: PlantUML CLI validation (optional, most accurate)
        if shutil.which("plantuml"):
            print("Running Tier 2 validation (PlantUML CLI)...")
            cli_valid, cli_error = validate_with_plantuml_cli(args.output)
            if not cli_valid:
                print(f"ERROR: {cli_error}", file=sys.stderr)
                sys.exit(1)
            else:
                print("SUCCESS: Tier 2 validation passed")
        else:
            print("INFO: Tier 2 validation skipped (PlantUML CLI not installed)")
            print("      Installation instructions:")
            print("      macOS:   brew install plantuml")
            print("      Linux:   apt-get install plantuml")
            print("      Windows: choco install plantuml  OR  scoop install plantuml")
            print("      Manual:  https://plantuml.com/download")

        print(f"\nSUCCESS: Generated {args.diagram_type} diagram: {args.output}")

    except FileNotFoundError:
        print(f"ERROR: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"ERROR: Missing required field in input data: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def validate_diagram(args):
    """Validate a PlantUML diagram"""
    try:
        with open(args.file, "r") as f:
            content = f.read()

        validator = PlantUMLValidator()
        result = validator.validate(content)

        if result.valid:
            print(f"SUCCESS: PlantUML syntax is valid: {args.file}")
            if result.warnings:
                print("\nWARNINGS:")
                for warning in result.warnings:
                    print(f"  - {warning}")
        else:
            print(f"ERROR: PlantUML syntax has errors: {args.file}", file=sys.stderr)
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

            if result.warnings:
                print("\nWarnings:")
                for warning in result.warnings:
                    print(f"  - {warning}")

            sys.exit(1)

    except FileNotFoundError:
        print(f"ERROR: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
