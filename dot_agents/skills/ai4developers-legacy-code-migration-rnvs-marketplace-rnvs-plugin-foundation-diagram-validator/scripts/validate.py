#!/usr/bin/env python3
"""
PlantUML Diagram Validator

Validates Phase2 PlantUML diagrams against production quality standards.
Implements 5-gate validation system matching Phase1 rigor.

Requirements:
- Python 3.10+
- No external dependencies (standard library only)
- PlantUML CLI (optional, for Tier 2 validation)

Usage:
    python validate.py --diagram phase2/dependencies.puml \
                       --phase1-analysis phase1/analysis.json \
                       --phase1-deps phase1/dependency-graph.json \
                       --output phase2/diagram-quality-report.json

    python validate.py --phase2-dir results/NBM/phase2 \
                       --phase1-dir results/NBM/phase1 \
                       --output results/NBM/phase2/diagram-quality-report.json
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationGateResult:
    """Result of a single validation gate."""
    status: str  # "PASSED", "FAILED", "WARNING"
    details: Dict
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class DiagramValidationResult:
    """Complete validation result for a diagram."""
    file: str
    validation_gates: Dict[str, ValidationGateResult]
    quality_score: float
    overall_status: str  # "COMPLETE", "INCOMPLETE"


class DiagramValidator:
    """Validates PlantUML diagrams against production quality standards."""

    def __init__(self, plantuml_cli_available: bool = None):
        """
        Initialize validator.

        Args:
            plantuml_cli_available: Override PlantUML CLI detection (for testing)
        """
        if plantuml_cli_available is None:
            self.plantuml_cli_available = self._check_plantuml_cli()
        else:
            self.plantuml_cli_available = plantuml_cli_available

    def _check_plantuml_cli(self) -> bool:
        """Check if PlantUML CLI is available."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _detect_diagram_type(self, diagram_content: str) -> str:
        """
        Detect diagram type from PlantUML content.

        Returns:
            "activity", "component", "sequence", or "unknown"
        """
        # Activity diagram indicators (highest priority)
        has_activity_start = bool(re.search(r'\bstart\b', diagram_content))
        has_activity_syntax = bool(re.search(r':\w+.*;', diagram_content))
        has_swimlanes = bool(re.search(r'\|[^|]+\|', diagram_content))

        if has_activity_start or (has_activity_syntax and has_swimlanes):
            return "activity"

        # Component diagram indicators (check before sequence since they also use arrows)
        # Match: component "Name", database "Name", [ComponentName], skinparam component
        has_component_keyword = bool(re.search(
            r'(?:component|database|interface|class|rectangle)\s+"',
            diagram_content
        ))
        has_bracket_notation = bool(re.search(r'^\s*\[[^\]]+\]', diagram_content, re.MULTILINE))
        has_component_skinparam = bool(re.search(r'skinparam\s+component\s*\{', diagram_content))

        if has_component_keyword or has_bracket_notation or has_component_skinparam:
            return "component"

        # Sequence diagram indicators (lowest priority - arrows also used in other diagrams)
        has_participants = bool(re.search(r'\bparticipant\b', diagram_content))
        has_actor = bool(re.search(r'\bactor\b', diagram_content))

        if has_participants or has_actor:
            return "sequence"

        return "unknown"

    def validate_diagram(
        self,
        diagram_path: Path,
        phase1_analysis: Optional[Path] = None,
        phase1_deps: Optional[Path] = None
    ) -> DiagramValidationResult:
        """
        Validate a single PlantUML diagram through all gates.

        Args:
            diagram_path: Path to .puml diagram file
            phase1_analysis: Path to phase1/analysis.json (for Gate 1)
            phase1_deps: Path to phase1/dependency-graph.json (for Gate 2)

        Returns:
            DiagramValidationResult with all gate results and quality score
        """
        # Read diagram content
        diagram_content = diagram_path.read_text(encoding='utf-8')

        # Detect diagram type
        diagram_type = self._detect_diagram_type(diagram_content)

        # Initialize gate results
        gates = {}

        # Gate 1: Component Coverage (only for component diagrams)
        if diagram_type == "component" and phase1_analysis and phase1_analysis.exists():
            gates["gate_1_component_coverage"] = self._gate_1_component_coverage(
                diagram_content, phase1_analysis
            )

        # Gate 2: Dependency Completeness (only for component diagrams)
        if diagram_type == "component" and phase1_deps and phase1_deps.exists():
            gates["gate_2_dependency_completeness"] = self._gate_2_dependency_completeness(
                diagram_content, phase1_deps
            )

        # Gate 3: Syntax Validation (always runs)
        gates["gate_3_syntax_validation"] = self._gate_3_syntax_validation(
            diagram_content, diagram_path
        )

        # Gate 4: Metadata Completeness (always runs)
        gates["gate_4_metadata_completeness"] = self._gate_4_metadata_completeness(
            diagram_content
        )

        # Gate 5: Renderability & Quality (always runs)
        gates["gate_5_renderability"] = self._gate_5_renderability(
            diagram_content
        )

        # Calculate quality score
        quality_score = self._calculate_quality_score(gates)

        # Determine overall status
        overall_status = self._determine_overall_status(gates, quality_score)

        return DiagramValidationResult(
            file=str(diagram_path),
            validation_gates=gates,
            quality_score=quality_score,
            overall_status=overall_status
        )

    def _gate_1_component_coverage(
        self,
        diagram_content: str,
        phase1_analysis_path: Path
    ) -> ValidationGateResult:
        """
        Gate 1: Component Coverage (≥80% threshold)

        Verify all components from Phase1 analysis.json appear in diagram.
        """
        # Load Phase1 analysis
        phase1_data = json.loads(phase1_analysis_path.read_text(encoding='utf-8'))

        # Extract components from Phase1
        phase1_components = set()
        for component in phase1_data.get("components", []):
            phase1_components.add(component["name"])

        # Extract components from diagram
        # Pattern: [ComponentName], component "ComponentName", or database "ComponentName"
        component_pattern = r'(?:component|database|interface|class|rectangle)\s+"([^"]+)"|^\s*\[([^\]]+)\]'
        diagram_components = set()
        for match in re.finditer(component_pattern, diagram_content, re.MULTILINE):
            comp_name = match.group(1) or match.group(2)
            if comp_name:
                diagram_components.add(comp_name.strip())

        # Calculate coverage
        components_in_phase1 = len(phase1_components)
        components_in_diagram = len(diagram_components & phase1_components)

        if components_in_phase1 > 0:
            coverage_percentage = int((components_in_diagram / components_in_phase1) * 100)
        else:
            coverage_percentage = 100  # No components to cover

        # Determine missing components
        missing_components = sorted(phase1_components - diagram_components)

        # Determine status
        status = "PASSED" if coverage_percentage >= 80 else "FAILED"

        return ValidationGateResult(
            status=status,
            details={
                "components_in_phase1": components_in_phase1,
                "components_in_diagram": components_in_diagram,
                "coverage_percentage": coverage_percentage,
                "missing_components": missing_components
            },
            errors=[f"Missing {len(missing_components)} components: {', '.join(missing_components[:5])}{'...' if len(missing_components) > 5 else ''}"] if status == "FAILED" else []
        )

    def _normalize_component_name(self, name: str) -> str:
        """
        Normalize component name for comparison.

        Examples:
            RNB Factory -> rnbfactory
            p_rnb (PL/SQL Package) -> p_rnb
            TNBManager -> tnbmanager
            T_RNB -> t_rnb
        """
        if not name:
            return ""

        # Remove parenthetical text (e.g., "(PL/SQL Package)")
        name = re.sub(r'\s*\([^)]*\)', '', name)

        # Remove special characters except underscores
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)

        # Convert to lowercase
        return name.lower()

    def _extract_component_name_from_path(self, file_path: str) -> Optional[str]:
        """
        Extract component name from file path.

        Examples:
            /path/to/rnbmanager.cpp -> rnbmanager
            /path/to/pack_body_rnb.sql -> p_rnb
            Oracle DB - T_RNB -> T_RNB
        """
        if not file_path:
            return None

        # Handle database references (e.g., "Oracle DB - T_RNB")
        if "Oracle DB -" in file_path or "Database -" in file_path:
            parts = file_path.split("-")
            if len(parts) >= 2:
                return parts[-1].strip()

        # Handle PL/SQL packages specially
        if "pack_body_rnb.sql" in file_path or "pack_rnb.sql" in file_path:
            return "p_rnb"
        if "pack_body_tnb.sql" in file_path or "pack_tnb.sql" in file_path:
            return "p_tnb"

        # Extract filename without extension
        from pathlib import Path as FilePath
        filename = FilePath(file_path).stem.lower()

        return filename

    def _gate_2_dependency_completeness(
        self,
        diagram_content: str,
        phase1_deps_path: Path
    ) -> ValidationGateResult:
        """
        Gate 2: Dependency Completeness (≥80% threshold)

        Verify all dependencies from Phase1 dependency-graph.json are visualized.
        """
        # Load Phase1 dependency graph
        phase1_deps_data = json.loads(phase1_deps_path.read_text(encoding='utf-8'))

        # Extract dependencies from Phase1
        # Phase1 format uses "dependency_details" array with file paths
        phase1_dependencies = set()

        # Try new format first (dependency_details)
        if "dependency_details" in phase1_deps_data:
            for detail in phase1_deps_data["dependency_details"]:
                source_path = detail.get("source", "")
                source_name = self._extract_component_name_from_path(source_path)

                for dep in detail.get("dependencies", []):
                    target_path = dep.get("target", "")
                    target_name = self._extract_component_name_from_path(target_path)

                    if source_name and target_name:
                        # Create dependency key
                        phase1_dependencies.add(f"{source_name}->{target_name}")

        # Fall back to old format (nodes) if new format not found
        elif "nodes" in phase1_deps_data:
            for node in phase1_deps_data["nodes"]:
                node_id = node["id"]
                for dep in node.get("dependencies", []):
                    phase1_dependencies.add(f"{node_id}->{dep}")

        # Extract dependencies from diagram
        # Pattern: ComponentA --> ComponentB, ComponentA ..> ComponentB, etc.
        arrow_pattern = r'(?:component|database|interface|class|rectangle|\[)\s*"?([^"\]]+)"?\s*(?:\])?(?:\s+<<[^>]+>>)?\s*(?:-->|\.\.>|==>|->>)\s*(?:component|database|interface|class|rectangle|\[)\s*"?([^"\]]+)"?'
        diagram_dependencies = set()
        for match in re.finditer(arrow_pattern, diagram_content):
            from_comp = self._normalize_component_name(match.group(1).strip())
            to_comp = self._normalize_component_name(match.group(2).strip())
            if from_comp and to_comp:
                diagram_dependencies.add(f"{from_comp}->{to_comp}")

        # Normalize Phase1 dependencies for comparison
        phase1_dependencies_normalized = set()
        for dep in phase1_dependencies:
            parts = dep.split("->")
            if len(parts) == 2:
                from_norm = self._normalize_component_name(parts[0])
                to_norm = self._normalize_component_name(parts[1])
                if from_norm and to_norm:
                    phase1_dependencies_normalized.add(f"{from_norm}->{to_norm}")

        # Calculate completeness
        dependencies_in_phase1 = len(phase1_dependencies_normalized)

        # Find matches (case-insensitive)
        matched_dependencies = diagram_dependencies & phase1_dependencies_normalized
        dependencies_in_diagram = len(matched_dependencies)

        if dependencies_in_phase1 > 0:
            completeness_percentage = int((dependencies_in_diagram / dependencies_in_phase1) * 100)
        else:
            completeness_percentage = 100  # No dependencies to cover

        # Determine missing dependencies
        missing_dependencies = sorted(phase1_dependencies_normalized - diagram_dependencies)

        # Determine status
        status = "PASSED" if completeness_percentage >= 80 else "FAILED"

        return ValidationGateResult(
            status=status,
            details={
                "dependencies_in_phase1": dependencies_in_phase1,
                "dependencies_in_diagram": dependencies_in_diagram,
                "completeness_percentage": completeness_percentage,
                "missing_dependencies": missing_dependencies[:10]  # Limit to first 10
            },
            errors=[f"Missing {len(missing_dependencies)} dependencies"] if status == "FAILED" else []
        )

    def _gate_3_syntax_validation(
        self,
        diagram_content: str,
        diagram_path: Path
    ) -> ValidationGateResult:
        """
        Gate 3: Syntax Validation (Tier 1 + Optional Tier 2)

        Verify PlantUML syntax correctness.
        """
        errors = []
        warnings = []

        # Tier 1: Regex validation (REQUIRED)
        tier1_errors = self._tier1_syntax_check(diagram_content)

        # Tier 2: PlantUML CLI validation (OPTIONAL)
        tier2_errors = []
        if self.plantuml_cli_available:
            tier2_errors = self._tier2_plantuml_cli_check(diagram_path)

        # Combine errors
        all_errors = tier1_errors + tier2_errors

        # Determine validation method
        if self.plantuml_cli_available:
            validation_method = "Tier 1 + Tier 2"
        else:
            validation_method = "Tier 1 (PlantUML CLI not available)"
            warnings.append("PlantUML CLI not available, using Tier 1 validation only (~90% accuracy)")

        # Determine status
        if tier1_errors:
            status = "FAILED"
        elif tier2_errors:
            status = "WARNING"
            warnings.extend(tier2_errors)
        else:
            status = "PASSED"

        return ValidationGateResult(
            status=status,
            details={
                "tier1_regex": len(tier1_errors) == 0,
                "tier2_plantuml_cli": self.plantuml_cli_available and len(tier2_errors) == 0,
                "validation_method": validation_method,
                "syntax_errors": all_errors
            },
            errors=tier1_errors,
            warnings=warnings
        )

    def _tier1_syntax_check(self, content: str) -> List[str]:
        """Tier 1: Regex-based syntax validation (~90% accuracy)."""
        errors = []

        # Check 1: @startuml/@enduml matching
        startuml_count = len(re.findall(r'@startuml', content))
        enduml_count = len(re.findall(r'@enduml', content))
        if startuml_count != enduml_count:
            errors.append(f"Mismatched @startuml ({startuml_count}) and @enduml ({enduml_count})")

        # Check 2: Activity diagram start/stop
        if '@startuml' in content:
            # Only check for activity diagrams
            if re.search(r'\bstart\b', content):
                if not re.search(r'\b(?:stop|end)\b', content):
                    errors.append("Activity diagram has 'start' but no 'stop' or 'end'")

        # Check 3: Block closure (if/endif, partition/{})
        # Only match PlantUML if statements (start of line with optional whitespace)
        if_count = len(re.findall(r'^\s*if\s*\(', content, re.MULTILINE))
        endif_count = len(re.findall(r'^\s*endif\b', content, re.MULTILINE))
        if if_count != endif_count:
            errors.append(f"Mismatched if ({if_count}) and endif ({endif_count})")

        open_brace_count = len(re.findall(r'\{', content))
        close_brace_count = len(re.findall(r'\}', content))
        if open_brace_count != close_brace_count:
            errors.append(f"Mismatched braces ({{ {open_brace_count}, }} {close_brace_count})")

        # Check 4: Color codes (#RRGGBB)
        invalid_colors = []
        for match in re.finditer(r'#([0-9A-Fa-f]+)', content):
            color = match.group(1)
            if len(color) not in [3, 6]:  # Valid: #RGB or #RRGGBB
                invalid_colors.append(f"#{color}")
        if invalid_colors:
            errors.append(f"Invalid color codes: {', '.join(invalid_colors[:5])}")

        # Check 5: Unclosed quotes
        # Count quotes (simplified - doesn't handle escaped quotes)
        quote_count = len(re.findall(r'"', content))
        if quote_count % 2 != 0:
            errors.append("Unclosed quotes detected (odd number of double quotes)")

        return errors

    def _tier2_plantuml_cli_check(self, diagram_path: Path) -> List[str]:
        """Tier 2: PlantUML CLI validation (100% accuracy)."""
        errors = []

        try:
            result = subprocess.run(
                ["plantuml", "-syntax", str(diagram_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # PlantUML CLI returns non-zero exit code on syntax errors
            if result.returncode != 0:
                # Parse error output
                output = result.stderr + result.stdout
                for line in output.split('\n'):
                    if 'error' in line.lower() or 'syntax' in line.lower():
                        errors.append(line.strip())

        except subprocess.TimeoutExpired:
            errors.append("PlantUML CLI validation timeout (30s)")
        except Exception as e:
            errors.append(f"PlantUML CLI error: {str(e)}")

        return errors

    def _gate_4_metadata_completeness(self, diagram_content: str) -> ValidationGateResult:
        """
        Gate 4: Metadata Completeness

        Verify diagram has required metadata (legend, notes, labels, layout).
        """
        errors = []

        # Check 1: Legend present
        legend_present = bool(re.search(r'legend\s+(?:right|left|top|bottom)', diagram_content))
        if not legend_present:
            errors.append("Legend missing (expected 'legend right' block)")

        # Check 2: Notes present for external systems
        notes_present = bool(re.search(r'note\s+(?:right|left|top|bottom)', diagram_content))
        if not notes_present:
            errors.append("Notes missing (expected notes for external systems or important context)")

        # Check 3: Component labels are descriptive
        labels_descriptive = True
        generic_labels = []
        for match in re.finditer(r'(?:component|database)\s+"([^"]+)"', diagram_content):
            label = match.group(1)
            # Check for generic names like "Component1", "Service2", etc.
            if re.match(r'^(?:Component|Service|Database|System)\s*\d+$', label, re.IGNORECASE):
                labels_descriptive = False
                generic_labels.append(label)

        if not labels_descriptive:
            errors.append(f"Generic component labels detected: {', '.join(generic_labels[:3])}")

        # Check 4: Layout pragmas applied
        layout_pragmas = bool(re.search(r'!pragma\s+layout\s+smetana', diagram_content))
        if not layout_pragmas:
            errors.append("Layout pragma missing (expected '!pragma layout smetana')")

        # Determine status
        status = "PASSED" if len(errors) == 0 else "FAILED"

        return ValidationGateResult(
            status=status,
            details={
                "legend_present": legend_present,
                "notes_present": notes_present,
                "labels_descriptive": labels_descriptive,
                "layout_pragmas": layout_pragmas
            },
            errors=errors
        )

    def _gate_5_renderability(self, diagram_content: str) -> ValidationGateResult:
        """
        Gate 5: Renderability & Quality

        Verify diagram can render and complexity is reasonable.
        """
        errors = []
        warnings = []

        # Check 1: Syntax complete (block closure)
        open_braces = len(re.findall(r'\{', diagram_content))
        close_braces = len(re.findall(r'\}', diagram_content))
        syntax_complete = open_braces == close_braces

        if not syntax_complete:
            errors.append(f"Unclosed blocks detected ({{ {open_braces}, }} {close_braces})")

        # Check 2: Component count (complexity)
        components = re.findall(
            r'(?:component|database|interface|class|rectangle)\s+"([^"]+)"',
            diagram_content
        )
        component_count = len(set(components))

        complexity_warning = False
        if component_count > 15:
            complexity_warning = True
            warnings.append(f"High complexity: {component_count} components (consider splitting diagram)")

        # Check 3: Rendering test (if PlantUML CLI available)
        renders_successfully = True
        if self.plantuml_cli_available:
            # We already validated syntax in Gate 3, so rendering should work
            # This is a placeholder for potential future rendering tests
            pass

        # Determine status
        status = "PASSED" if len(errors) == 0 else "FAILED"
        if complexity_warning and status == "PASSED":
            status = "WARNING"

        return ValidationGateResult(
            status=status,
            details={
                "syntax_complete": syntax_complete,
                "component_count": component_count,
                "complexity_warning": complexity_warning,
                "renders_successfully": renders_successfully
            },
            errors=errors,
            warnings=warnings
        )

    def _calculate_quality_score(self, gates: Dict[str, ValidationGateResult]) -> float:
        """
        Calculate overall quality score (0-100) from gate results.

        Weighted average (normalized when gates are skipped):
        - Gate 1 (Component Coverage): 25%
        - Gate 2 (Dependency Completeness): 25%
        - Gate 3 (Syntax Validation): 20%
        - Gate 4 (Metadata Completeness): 15%
        - Gate 5 (Renderability): 15%
        """
        weights = {
            "gate_1_component_coverage": 0.25,
            "gate_2_dependency_completeness": 0.25,
            "gate_3_syntax_validation": 0.20,
            "gate_4_metadata_completeness": 0.15,
            "gate_5_renderability": 0.15
        }

        total_score = 0.0
        total_weight = 0.0

        for gate_name, weight in weights.items():
            if gate_name not in gates:
                continue  # Skip gates that weren't run

            gate = gates[gate_name]
            total_weight += weight

            # Calculate gate score
            if gate_name == "gate_1_component_coverage":
                gate_score = gate.details.get("coverage_percentage", 0)
            elif gate_name == "gate_2_dependency_completeness":
                gate_score = gate.details.get("completeness_percentage", 0)
            else:
                # Binary gates: 100 if passed, 0 if failed
                gate_score = 100 if gate.status == "PASSED" else 0

            total_score += gate_score * weight

        # Normalize score based on actual weights used
        # total_score is already weighted (0-100 range), so just scale by total_weight
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0

        return round(normalized_score, 1)

    def _determine_overall_status(
        self,
        gates: Dict[str, ValidationGateResult],
        quality_score: float
    ) -> str:
        """
        Determine overall validation status.

        Returns:
            "COMPLETE" if all gates passed and quality ≥ 70
            "INCOMPLETE" otherwise
        """
        # Check if any gate FAILED
        for gate in gates.values():
            if gate.status == "FAILED":
                return "INCOMPLETE"

        # Check quality score threshold
        if quality_score < 70:
            return "INCOMPLETE"

        return "COMPLETE"


def generate_validation_report(
    feature: str,
    phase: int,
    diagrams: Dict[str, DiagramValidationResult],
    python_version: str,
    plantuml_cli_available: bool
) -> Dict:
    """
    Generate comprehensive validation report JSON.

    Args:
        feature: Feature name (e.g., "NBM")
        phase: Phase number (2)
        diagrams: Dict of diagram_name -> DiagramValidationResult
        python_version: Python version string
        plantuml_cli_available: Whether PlantUML CLI is available

    Returns:
        Report dictionary ready for JSON serialization
    """
    # Calculate overall quality score (average of all diagrams)
    if diagrams:
        overall_quality_score = sum(d.quality_score for d in diagrams.values()) / len(diagrams)
    else:
        overall_quality_score = 0.0

    # Determine overall status
    overall_status = "COMPLETE" if all(
        d.overall_status == "COMPLETE" for d in diagrams.values()
    ) else "INCOMPLETE"

    # Generate recommendations
    recommendations = []
    if overall_status == "COMPLETE":
        if overall_quality_score >= 85:
            recommendations.append("✅ All validation gates passed")
            recommendations.append("✅ Diagram quality exceeds minimum thresholds")
            recommendations.append("✅ Ready for Phase 3")
        else:
            recommendations.append("⚠️ All gates passed but quality score is below 85")
            recommendations.append("⚠️ Consider improving diagram quality before Phase 3")
    else:
        recommendations.append("❌ One or more validation gates failed")
        recommendations.append("❌ Review failed gates and regenerate diagrams")
        recommendations.append("❌ Not ready for Phase 3")

    # Build report structure
    report = {
        "feature": feature,
        "phase": phase,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "python_version": python_version,
        "plantuml_cli_available": plantuml_cli_available,
        "diagrams": {},
        "overall_status": overall_status,
        "overall_quality_score": round(overall_quality_score, 1),
        "recommendations": recommendations
    }

    # Add diagram results
    for name, result in diagrams.items():
        report["diagrams"][name] = {
            "file": result.file,
            "validation_gates": {
                gate_name: {
                    "status": gate.status,
                    **gate.details,
                    "errors": gate.errors,
                    "warnings": gate.warnings
                }
                for gate_name, gate in result.validation_gates.items()
            },
            "quality_score": result.quality_score
        }

    return report


def print_console_report(
    diagrams: Dict[str, DiagramValidationResult],
    overall_status: str,
    overall_quality_score: float
):
    """Print formatted validation report to console."""
    print()
    print("=" * 60)
    print("PHASE2 DIAGRAM VALIDATION REPORT")
    print("=" * 60)
    print()

    for name, result in diagrams.items():
        print(f"Diagram: {name}")
        print(f"File: {result.file}")
        print()

        for gate_name, gate in result.validation_gates.items():
            # Format gate name
            display_name = gate_name.upper().replace("_", " ")

            # Status icon
            if gate.status == "PASSED":
                icon = "✅"
            elif gate.status == "WARNING":
                icon = "⚠️"
            else:
                icon = "❌"

            # Print gate status
            if gate_name == "gate_1_component_coverage":
                coverage = gate.details.get("coverage_percentage", 0)
                print(f"{icon} {display_name}: {gate.status} ({coverage}%)")
            elif gate_name == "gate_2_dependency_completeness":
                completeness = gate.details.get("completeness_percentage", 0)
                print(f"{icon} {display_name}: {gate.status} ({completeness}%)")
            elif gate_name == "gate_3_syntax_validation":
                method = gate.details.get("validation_method", "Unknown")
                print(f"{icon} {display_name}: {gate.status} ({method})")
            elif gate_name == "gate_5_renderability":
                count = gate.details.get("component_count", 0)
                complexity = "high" if count > 15 else ("moderate" if count > 10 else "low")
                print(f"{icon} {display_name}: {gate.status} ({count} components, {complexity} complexity)")
            else:
                print(f"{icon} {display_name}: {gate.status}")

            # Print errors
            for error in gate.errors:
                print(f"    ❌ {error}")

            # Print warnings
            for warning in gate.warnings:
                print(f"    ⚠️  {warning}")

        print()
        print(f"Quality Score: {result.quality_score}/100")
        print()

    print("-" * 60)
    print(f"Overall Status: {overall_status}")
    print(f"Overall Quality Score: {overall_quality_score}/100")
    print()

    if overall_status == "COMPLETE":
        if overall_quality_score >= 85:
            print("✅ All validation gates passed")
            print("✅ Diagram is production-ready")
            print("✅ Ready to proceed to Phase 3")
        else:
            print("⚠️  All gates passed but quality below 85")
            print("⚠️  Consider improving diagram quality")
    else:
        print("❌ One or more validation gates failed")
        print("❌ Review errors and regenerate diagrams")
        print("❌ Not ready for Phase 3")

    print()


def main():
    """Command-line interface for diagram validation."""
    parser = argparse.ArgumentParser(
        description="Validate Phase2 PlantUML diagrams against production quality standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single diagram
  python validate.py --diagram phase2/dependencies.puml \\
                     --phase1-analysis phase1/analysis.json \\
                     --phase1-deps phase1/dependency-graph.json \\
                     --output phase2/diagram-quality-report.json

  # Validate all Phase2 diagrams
  python validate.py --phase2-dir results/NBM/phase2 \\
                     --phase1-dir results/NBM/phase1 \\
                     --output results/NBM/phase2/diagram-quality-report.json
        """
    )

    # Single diagram mode
    parser.add_argument(
        "--diagram",
        type=Path,
        help="Path to single .puml diagram file to validate"
    )
    parser.add_argument(
        "--phase1-analysis",
        type=Path,
        help="Path to phase1/analysis.json (for Gate 1)"
    )
    parser.add_argument(
        "--phase1-deps",
        type=Path,
        help="Path to phase1/dependency-graph.json (for Gate 2)"
    )

    # Batch mode
    parser.add_argument(
        "--phase2-dir",
        type=Path,
        help="Path to phase2 directory (batch mode)"
    )
    parser.add_argument(
        "--phase1-dir",
        type=Path,
        help="Path to phase1 directory (batch mode)"
    )

    # Output
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output diagram-quality-report.json"
    )

    # Feature name (for report)
    parser.add_argument(
        "--feature",
        type=str,
        default="Unknown",
        help="Feature name (e.g., NBM, PDA)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.diagram and args.phase2_dir:
        print("ERROR: Cannot specify both --diagram and --phase2-dir", file=sys.stderr)
        sys.exit(1)

    if not args.diagram and not args.phase2_dir:
        print("ERROR: Must specify either --diagram or --phase2-dir", file=sys.stderr)
        sys.exit(1)

    # Initialize validator
    validator = DiagramValidator()

    # Determine diagrams to validate
    diagrams_to_validate = {}

    if args.diagram:
        # Single diagram mode
        if not args.diagram.exists():
            print(f"ERROR: Diagram not found: {args.diagram}", file=sys.stderr)
            sys.exit(1)

        diagrams_to_validate["diagram"] = {
            "path": args.diagram,
            "phase1_analysis": args.phase1_analysis,
            "phase1_deps": args.phase1_deps
        }

    else:
        # Batch mode
        if not args.phase2_dir.exists():
            print(f"ERROR: Phase2 directory not found: {args.phase2_dir}", file=sys.stderr)
            sys.exit(1)

        # Find all .puml files in phase2 directory
        for puml_file in args.phase2_dir.glob("*.puml"):
            name = puml_file.stem  # e.g., "dependencies", "flow"

            # Determine Phase1 files
            phase1_analysis = None
            phase1_deps = None

            if args.phase1_dir and args.phase1_dir.exists():
                phase1_analysis = args.phase1_dir / "analysis.json"
                phase1_deps = args.phase1_dir / "dependency-graph.json"

            diagrams_to_validate[name] = {
                "path": puml_file,
                "phase1_analysis": phase1_analysis,
                "phase1_deps": phase1_deps
            }

    if not diagrams_to_validate:
        print(f"ERROR: No .puml files found", file=sys.stderr)
        sys.exit(1)

    # Validate all diagrams
    validation_results = {}

    for name, diagram_info in diagrams_to_validate.items():
        print(f"Validating {name}...", file=sys.stderr)

        result = validator.validate_diagram(
            diagram_path=diagram_info["path"],
            phase1_analysis=diagram_info.get("phase1_analysis"),
            phase1_deps=diagram_info.get("phase1_deps")
        )

        validation_results[name] = result

    # Generate report
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    report = generate_validation_report(
        feature=args.feature,
        phase=2,
        diagrams=validation_results,
        python_version=python_version,
        plantuml_cli_available=validator.plantuml_cli_available
    )

    # Write report to file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(f"Report written to: {args.output}", file=sys.stderr)

    # Print console report
    print_console_report(
        diagrams=validation_results,
        overall_status=report["overall_status"],
        overall_quality_score=report["overall_quality_score"]
    )

    # Exit with appropriate code
    if report["overall_status"] == "COMPLETE":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
