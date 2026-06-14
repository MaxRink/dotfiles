---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-diagram-validator
description: Automated PlantUML diagram quality validation with 5-gate system matching Phase1 rigor. Use when validating Phase2 diagram outputs, checking diagram completeness, syntax correctness, metadata quality, and overall production-readiness. Implements blocking behavior - diagrams must pass all gates before Phase3.
allowed-tools: Read, Bash
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/diagram-validator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Diagram Validator Skill

## Purpose
Validate PlantUML diagrams against production quality standards with a 5-gate validation system that BLOCKS progression until all quality criteria are met. This skill brings Phase2 diagram generation to the same validation rigor as Phase1 code analysis.

## When to Use
- Validating Phase2 diagram outputs (dependencies.puml, flow.puml)
- Checking diagram completeness against Phase1 analysis.json
- Verifying syntax correctness (Tier 1 + Tier 2)
- Validating metadata quality (legend, notes, labels)
- Calculating diagram quality scores
- Generating validation reports (diagram-quality-report.json)
- **Generating dependency maps** (dependency_map.md for Phase3)

## Requirements

### Python 3.10+ (REQUIRED)
- Standard library only (no external dependencies)
- Cross-platform compatible (Windows/Linux/macOS/WSL)
- Auto-detected via run_validator.sh wrapper

### PlantUML CLI (OPTIONAL)
- Enables Tier 2 validation (100% syntax accuracy)
- Gracefully degrades to Tier 1 if missing

## Validation Gates (BLOCKING)

This skill implements a **5-gate validation system** modeled after Phase1's rigorous quality standards. ALL gates must PASS before Phase2 is considered complete.

### Gate 1: Component Coverage (≥80% threshold)

**Purpose**: Verify all components from Phase1 analysis.json appear in diagram

**Validation Logic**:
- Extract components from `phase1/analysis.json`
- Parse components from `phase2/dependencies.puml`
- Calculate coverage: `(components_in_diagram / components_in_phase1) × 100`
- **PASS** if coverage ≥ 80%
- **FAIL** if coverage < 80% → List missing components

**Output**:
```json
{
  "status": "PASSED",
  "components_in_phase1": 4,
  "components_in_diagram": 4,
  "coverage_percentage": 100,
  "missing_components": []
}
```

### Gate 2: Dependency Completeness (≥80% threshold)

**Purpose**: Verify all dependencies from Phase1 dependency-graph.json are visualized

**Validation Logic**:
- Extract dependencies from `phase1/dependency-graph.json`
- Parse arrows/relationships from `phase2/dependencies.puml`
- Calculate completeness: `(dependencies_in_diagram / dependencies_in_phase1) × 100`
- **PASS** if completeness ≥ 80%
- **FAIL** if completeness < 80% → List missing dependencies

**Output**:
```json
{
  "status": "PASSED",
  "dependencies_in_phase1": 287,
  "dependencies_in_diagram": 256,
  "completeness_percentage": 89,
  "missing_dependencies": ["RNBManager->Database"]
}
```

### Gate 3: Syntax Validation (Tier 1 + Optional Tier 2)

**Purpose**: Verify PlantUML syntax correctness

**Validation Logic**:
- **Tier 1** (REQUIRED): Regex validation (~90% accuracy)
  - Check @startuml/@enduml matching
  - Verify block closure (if/endif, partition/{})
  - Validate color codes (#RRGGBB)
  - Check for unclosed quotes/brackets
- **Tier 2** (OPTIONAL): PlantUML CLI validation (100% accuracy)
  - Run `plantuml -syntax diagram.puml` if CLI available
  - Gracefully skip if not installed

**Blocking Behavior**:
- **FAIL** if Tier 1 fails (syntax errors present)
- **WARN** if Tier 2 fails but Tier 1 passes (review warnings)

**Output**:
```json
{
  "status": "PASSED",
  "tier1_regex": true,
  "tier2_plantuml_cli": true,
  "validation_method": "Tier 1 + Tier 2",
  "syntax_errors": []
}
```

### Gate 4: Metadata Completeness

**Purpose**: Verify diagram has required metadata (legend, notes, labels, layout)

**Validation Checklist**:
- [ ] Legend present (`legend right` block exists)
- [ ] Notes present for external systems
- [ ] Component labels are descriptive (not "Component1", "Service2")
- [ ] Layout pragmas applied (`!pragma layout smetana`, `linetype ortho`)
- [ ] Color scheme documented in legend

**Blocking Behavior**:
- **PASS** if all checklist items ✓
- **FAIL** if any missing → List missing metadata

**Output**:
```json
{
  "status": "PASSED",
  "legend_present": true,
  "notes_present": true,
  "labels_descriptive": true,
  "layout_pragmas": true
}
```

### Gate 5: Renderability & Quality

**Purpose**: Verify diagram can render and complexity is reasonable

**Validation Logic**:
- Verify block closure (all `{` have matching `}`)
- Check diagram complexity (component count)
- Optional: Test rendering with PlantUML CLI if available

**Complexity Thresholds**:
- < 10 components: ✅ Simple, clear
- 10-15 components: ✅ Moderate, acceptable
- \> 15 components: ⚠️ High complexity, consider splitting

**Blocking Behavior**:
- **FAIL** if syntax incomplete (unclosed blocks)
- **WARN** if > 15 components (suggest splitting)

**Output**:
```json
{
  "status": "PASSED",
  "syntax_complete": true,
  "component_count": 4,
  "complexity_warning": false,
  "renders_successfully": true
}
```

## Validation Report Output

The validator generates a comprehensive `diagram-quality-report.json` file:

```json
{
  "feature": "NBM",
  "phase": 2,
  "timestamp": "2025-11-05T12:00:00Z",
  "python_version": "3.11.5",
  "plantuml_cli_available": true,
  "diagrams": {
    "dependencies": {
      "file": "phase2/dependencies.puml",
      "validation_gates": {
        "gate_1_component_coverage": { ... },
        "gate_2_dependency_completeness": { ... },
        "gate_3_syntax_validation": { ... },
        "gate_4_metadata_completeness": { ... },
        "gate_5_renderability": { ... }
      },
      "quality_score": 94
    },
    "flow": {
      "file": "phase2/flow.puml",
      "validation_gates": { ... },
      "quality_score": 88
    }
  },
  "overall_status": "COMPLETE",
  "overall_quality_score": 91,
  "recommendations": [
    "All validation gates passed",
    "Diagram quality exceeds minimum thresholds",
    "Ready for Phase 3"
  ]
}
```

## Quality Score Calculation

Weighted average of all gates:

| Gate | Weight | Calculation |
|------|--------|-------------|
| Gate 1: Component Coverage | 25% | coverage_percentage × 0.25 |
| Gate 2: Dependency Completeness | 25% | completeness_percentage × 0.25 |
| Gate 3: Syntax Validation | 20% | 100 if passed, 0 if failed × 0.20 |
| Gate 4: Metadata Completeness | 15% | 100 if passed, 0 if failed × 0.15 |
| Gate 5: Renderability | 15% | 100 if passed, 0 if failed × 0.15 |

**Overall Quality Score** = Sum of weighted gate scores

**Thresholds**:
- ≥ 85: ✅ Production-ready
- 70-84: ⚠️ Acceptable but needs improvement
- < 70: ❌ Not ready for Phase3

## Command-Line Tool

### Usage

**Validate a single diagram:**
```bash
bash scripts/run_validator.sh \
  --diagram phase2/dependencies.puml \
  --phase1-analysis phase1/analysis.json \
  --phase1-deps phase1/dependency-graph.json \
  --output phase2/diagram-quality-report.json
```

**Validate all Phase2 diagrams:**
```bash
bash scripts/run_validator.sh \
  --phase2-dir results/NBM/phase2 \
  --phase1-dir results/NBM/phase1 \
  --output results/NBM/phase2/diagram-quality-report.json
```

**Check validation status:**
```bash
# Exit code 0 = all gates passed
# Exit code 1 = one or more gates failed
bash scripts/run_validator.sh --diagram phase2/dependencies.puml ...
echo $?  # Check exit code
```

### Output

**Console Output**:
```
============================================================
PHASE2 DIAGRAM VALIDATION REPORT
============================================================

✅ GATE_1_COMPONENT_COVERAGE: PASSED (100%)
✅ GATE_2_DEPENDENCY_COMPLETENESS: PASSED (89%)
✅ GATE_3_SYNTAX_VALIDATION: PASSED (Tier 1 + Tier 2)
✅ GATE_4_METADATA_COMPLETENESS: PASSED
✅ GATE_5_RENDERABILITY: PASSED (4 components, low complexity)

Overall Status: COMPLETE
Quality Score: 94/100

✅ All validation gates passed
✅ Diagram is production-ready
✅ Ready to proceed to Phase 3
```

## Integration with Phase2 Command

The diagram-architect agent automatically invokes this validator at the end of Phase2:

```markdown
### PHASE E: Validation Gate Execution (BLOCKING)

1. Generate diagrams (dependencies.puml, flow.puml)
2. Invoke diagram-validator skill
3. Run all 5 validation gates
4. Generate diagram-quality-report.json
5. Calculate overall quality score
6. **BLOCK** if any gate FAILED
7. **PROCEED** only if all gates PASSED
```

## Blocking Behavior

**CRITICAL**: This validator implements **BLOCKING behavior** like Phase1:

- If **ALL gates PASS** → Phase2 COMPLETE → Proceed to Phase3
- If **ANY gate FAILS** → Phase2 INCOMPLETE → Re-generate diagrams → Re-validate
- Agent MUST iterate until all gates pass (no partial results allowed)

## Best Practices

### For Agents Using This Skill

1. **Always validate before declaring Phase2 complete**
2. **Review gate results** - understand why gates failed
3. **Iterate on failures** - re-generate diagrams, don't skip validation
4. **Include quality report** - save diagram-quality-report.json for auditing
5. **Check quality score** - aim for ≥ 85 (production-ready threshold)

### For Manual Validation

1. **Run after diagram generation** - validate immediately after creating .puml files
2. **Fix failures incrementally** - address one gate at a time
3. **Use Tier 2 when possible** - install PlantUML CLI for 100% syntax accuracy
4. **Review warnings** - even if gates pass, check for improvement suggestions

## Troubleshooting

### Gate 1 Fails (Component Coverage < 80%)

**Cause**: Some components from Phase1 analysis.json missing from diagram

**Solution**:
1. Check phase1/analysis.json for component list
2. Verify all components in dependencies.puml
3. Add missing components to diagram
4. Re-validate

### Gate 2 Fails (Dependency Completeness < 80%)

**Cause**: Some dependencies from Phase1 dependency-graph.json not visualized

**Solution**:
1. Check phase1/dependency-graph.json for dependency list
2. Add missing arrows to dependencies.puml
3. Verify arrow labels match dependency relationships
4. Re-validate

### Gate 3 Fails (Syntax Errors)

**Cause**: PlantUML syntax errors (unclosed blocks, invalid colors, etc.)

**Solution**:
1. Review syntax_errors in report
2. Fix errors (check line numbers if provided)
3. Re-validate with Tier 1
4. If available, use Tier 2 (PlantUML CLI) for precise error location

### Gate 4 Fails (Missing Metadata)

**Cause**: Legend, notes, or layout pragmas missing

**Solution**:
1. Add `legend right` block with color explanations
2. Add notes for external systems
3. Verify layout pragmas present (`!pragma layout smetana`)
4. Re-validate

### Gate 5 Fails (Syntax Incomplete)

**Cause**: Unclosed blocks (`{` without matching `}`)

**Solution**:
1. Review diagram structure
2. Verify all `if` have `endif`, all `{` have `}`
3. Fix block closures
4. Re-validate

## Dependency Map Generation

Phase3 requires a `dependency_map.md` file that provides a comprehensive mapping of components, dependencies, and database interactions. This skill includes a dependency map generator that creates this file from Phase1 analysis results.

### Purpose

The `dependency_map.md` file serves as:
- **Phase3 input**: Required for migration planning and VNRM design
- **Documentation**: Human-readable component and dependency reference
- **Dependency reference**: Quick lookup for component relationships
- **Database mapping**: Identifies all database interactions

### Usage

**Generate dependency map:**
```bash
bash scripts/run_dependency_map.sh \
  --phase1-analysis results/NBM/phase1/analysis.json \
  --phase1-deps results/NBM/phase1/dependency-graph.json \
  --output results/NBM/phase2/dependency_map.md \
  --feature NBM
```

**Example Output Structure:**
```markdown
# Dependency Map: NBM

## Component Overview
**Total Components**: 4

| Component | Type | Description |
|-----------|------|-------------|
| rnb-manager | Business | Manages RNB operations |
| rnb-database | Database | PostgreSQL database |

## Dependency Matrix
| Component | Depends On | Count |
|-----------|------------|-------|
| rnb-manager | rnb-database, message_bus | 2 |

## Database Interactions
| Component | Accesses Database(s) |
|-----------|----------------------|
| rnb-manager | rnb-database |

## Component Details
### rnb-manager
**Type**: Business
**Description**: Manages RNB operations
**Dependencies**: rnb-database, message_bus
**Database Access**: rnb-database
**Files** (15):
- `src/main/java/RNBManager.java`
- ... and 14 more files
```

### Integration with Phase2

The dependency map should be generated at the end of Phase2, alongside diagram validation:

1. Generate diagrams (dependencies.puml, flow.puml)
2. **Generate dependency_map.md** ← New step
3. Validate diagrams (all 5 gates)
4. Generate diagram-quality-report.json
5. Proceed to Phase3 if validation passes

## File Organization

```
diagram-validator/
├── SKILL.md (this file)
├── scripts/
│   ├── run_validator.sh (cross-platform wrapper for validation)
│   ├── validate.py (validation implementation)
│   ├── run_dependency_map.sh (cross-platform wrapper for dependency map)
│   └── generate_dependency_map.py (dependency map generator)
├── schemas/
│   └── diagram-quality-report.schema.json (JSON schema for reports)
└── references/
    └── validation-example.md (usage examples)
```

## See Also

- **plantuml-generator** skill - Generate diagrams before validating
- **diagram-quality-schema** skill - JSON schema for quality reports
- **Phase1 validation gates** - Inspiration for this validation system

---

**Use this skill to ensure Phase2 diagrams meet production quality standards before proceeding to Phase3!**
