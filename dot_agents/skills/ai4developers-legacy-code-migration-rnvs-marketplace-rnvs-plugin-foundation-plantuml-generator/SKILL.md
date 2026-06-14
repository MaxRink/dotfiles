---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-plantuml-generator
description: Generate and validate PlantUML diagrams (component, activity, sequence) for RNVS/VNRM architecture visualization. This skill should be used when creating system architecture diagrams, process flows, control flows, or interaction diagrams. Includes Python CLI tool (requires Python 3.10+) for diagram generation from JSON and syntax validation. Cross-platform compatible (Windows/Linux/macOS/WSL).
allowed-tools: Read, Bash
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/plantuml-generator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PlantUML Generator Skill

## Purpose
Generate syntactically correct PlantUML diagrams for RNVS legacy and VNRM target architectures. Supports component diagrams, activity diagrams, sequence diagrams, and custom styling with consistent color schemes.

## Requirements

### Python 3.10+ (REQUIRED)
- **Required for**: Diagram generation and validation
- **Version**: Python 3.10 or higher
- **Dependencies**: None (uses standard library only)
- **Cross-platform**: Automatic detection of `python` vs `python3` command

**Verification:**
```bash
# The run_generator.sh wrapper will auto-detect Python
bash scripts/run_generator.sh --help
```

**Installation if needed:**
- **Windows**: https://python.org/downloads (check "Add to PATH" during install)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt install python3` (Ubuntu/Debian) or `sudo yum install python3` (RHEL/CentOS)

### PlantUML CLI (OPTIONAL - for 100% validation accuracy)
- **Purpose**: Tier 2 validation (~10% improvement over Tier 1 regex)
- **Required for**: Maximum syntax validation accuracy (optional)
- **Requirement**: Java Runtime Environment

**Installation (optional):**
- **macOS**: `brew install plantuml`
- **Linux**: `sudo apt install plantuml`
- **Windows**: `choco install plantuml` or `scoop install plantuml`
- **Manual**: Download from https://plantuml.com/download

**Note**: Tier 1 regex validation (~90% accuracy) is sufficient for most diagram generation. PlantUML CLI is only needed for 100% validation accuracy.

## When to Use
- Creating architecture diagrams (component, deployment)
- Creating control flow diagrams (activity)
- Creating interaction diagrams (sequence)
- Applying consistent color schemes across diagrams
- Validating PlantUML syntax

## Diagram Types Supported

### 1. Component Diagram
Used for showing microservices, databases, external systems, and their dependencies.

**JSON Input Structure**:
```json
{
  "title": "Diagram Title",
  "components": [
    {"name": "Service Name", "type": "business", "description": "Optional description"},
    {"name": "Database Name", "type": "database", "description": "Optional description"},
    {"name": "External System", "type": "external"}
  ],
  "dependencies": [
    {"from": "Service Name", "to": "External System", "label": "API call"},
    {"from": "Service Name", "to": "Database Name", "label": "Read/Write"}
  ],
  "color_scheme": {
    "database": "#FFE6CC",
    "business": "#CCE5FF",
    "integration": "#D5E8D4",
    "presentation": "#F8CECC",
    "external": "#E1D5E7"
  }
}
```

**Component Types**: `business`, `database`, `integration`, `presentation`, `external`

### 2. Activity Diagram
Used for showing control flows, decision points, and process flows.

**JSON Input Structure**:
```json
{
  "title": "Diagram Title",
  "steps": [
    {"name": "Activity Name", "type": "business", "notes": "Additional context"}
  ],
  "decisions": [
    {
      "condition": "Decision?",
      "yes_path": "Success Path",
      "no_path": "Error Path"
    }
  ]
}
```

**Step Types**: `business`, `database`, `integration`

### 3. Activity Diagram with Swimlanes
Used for showing responsibilities across multiple services or actors.

**JSON Input Structure**:
```json
{
  "title": "Diagram Title",
  "use_swimlanes": true,
  "swimlanes": ["Service A", "Service B", "External System"],
  "steps": [
    {"name": "Action in Service A", "swimlane": "Service A"},
    {"name": "Action in Service B", "swimlane": "Service B"},
    {"name": "External Action", "swimlane": "External System"},
    {"name": "Final Action", "swimlane": "Service A"}
  ]
}
```

### 4. Sequence Diagram
Used for showing interactions between components over time.

**JSON Input Structure**:
```json
{
  "title": "Diagram Title",
  "participants": ["Client", "Service A", "Service B", "Database"],
  "interactions": [
    {"from": "Client", "to": "Service A", "message": "Request", "type": "normal"},
    {"from": "Service A", "to": "Service B", "message": "Call Service B", "type": "normal"},
    {"from": "Service B", "to": "Database", "message": "Query", "type": "normal"},
    {"from": "Database", "to": "Service B", "message": "Result", "type": "return"},
    {"from": "Service B", "to": "Service A", "message": "Response", "type": "return"},
    {"from": "Service A", "to": "Client", "message": "Final Response", "type": "return"}
  ]
}
```

**Interaction Types**: `normal` (sync), `return` (response), `async` (fire-and-forget)

## Color Scheme Guidelines

### Standard RNVS/VNRM Colors
- **Database Layer**: `#FFE6CC` (Orange) - Persistence, data storage
- **Business Logic**: `#CCE5FF` (Blue) - Core processing, rules
- **Integration Layer**: `#D5E8D4` (Green) - External APIs, message queues
- **Presentation Layer**: `#F8CECC` (Red) - UI, API Gateway
- **External Systems**: `#E1D5E7` (Purple) - Third-party systems

### Error Paths
- **Error Activities**: `#F8CECC` (Red background)
- **Warning States**: `#FFF4CC` (Yellow background)

## Layout Optimization

The generator includes automatic layout optimization for cleaner, more readable diagrams:

### Layout Directives
- **`!pragma layout smetana`**: Use the Smetana layout engine (best for hierarchical diagrams)
- **`skinparam linetype ortho`**: Use orthogonal lines (cleaner, professional connections)
- **`skinparam nodesep 100`**: Increase spacing between nodes (component diagrams)
- **`skinparam ranksep 100`**: Increase spacing between ranks (component diagrams)
- **`skinparam responseMessageBelowArrow true`**: Improve readability (sequence diagrams)

These directives are automatically added to all generated diagrams for optimal visual quality.

## Syntax Validation

### Two-Tier Validation System

The generator uses a two-tier validation approach for maximum accuracy:

**Tier 1: Built-in Regex Validation (Always Active)**
- Fast, offline, provides detailed line-by-line error messages
- Checks syntax rules, color codes, matching blocks, quotes/brackets
- Catches ~90% of common syntax errors

**Tier 2: PlantUML CLI Validation (Optional)**
- Uses official PlantUML parser for 100% accuracy
- Automatically enabled if PlantUML CLI is installed
- Installation:
  - macOS: `brew install plantuml`
  - Linux: `apt-get install plantuml`
  - Windows: `choco install plantuml` or `scoop install plantuml`
  - Manual: Download from https://plantuml.com/download

### Common Syntax Rules
1. **Start/End**: Activity diagrams must have `start` and `stop`
2. **Stereotypes**: Use `<<type>>` notation: `[Component] <<business>>`
3. **Notes**: Position with `note right/left/top/bottom`
4. **Arrows**:
   - Solid: `-->`
   - Dotted: `..>`
   - Bold: `==>`
   - Async: `->>`
5. **Escaping**: Use quotes for names with spaces: `[My Service]`
6. **Layout**: Use pragma directives for better auto-layout

### Validation Checklist
- [ ] All `@startuml` have matching `@enduml`
- [ ] All `if` have matching `endif`
- [ ] All `partition` have closing braces
- [ ] All stereotypes defined in skinparam
- [ ] Color codes are valid hex (#RRGGBB)
- [ ] No unclosed quotes or brackets
- [ ] Layout pragmas included for optimal rendering

## Functions

### generate_component_diagram(components, dependencies, color_scheme)
Generate a component diagram showing system architecture.

**Parameters**:
- `components`: List of {name, type, description}
- `dependencies`: List of {from, to, label}
- `color_scheme`: Dict of {type: color_hex}

**Returns**: PlantUML string

### generate_activity_diagram(steps, decisions, color_scheme)
Generate an activity diagram showing process flow.

**Parameters**:
- `steps`: List of {name, type, notes}
- `decisions`: List of {condition, yes_path, no_path}
- `color_scheme`: Dict of {type: color_hex}

**Returns**: PlantUML string

### generate_sequence_diagram(participants, interactions)
Generate a sequence diagram showing component interactions.

**Parameters**:
- `participants`: List of participant names
- `interactions`: List of {from, to, message, type}

**Returns**: PlantUML string

### validate_syntax(plantuml_string)
Validate PlantUML syntax for common errors.

**Parameters**:
- `plantuml_string`: PlantUML diagram code

**Returns**: {valid: bool, errors: []}

## Command-Line Tool

This Skill includes a Python CLI tool for generating diagrams from JSON and validating PlantUML syntax.

### Requirements
- Python 3.10+ (uses modern type hints and dataclasses)
- No external dependencies (standard library only)
- **Cross-platform**: Works on Windows, Linux, macOS, WSL

### Usage

**RECOMMENDED: Use cross-platform wrapper**:
```bash
# Component diagram (cross-platform, generic example)
bash scripts/run_generator.sh generate component \
  --input references/component-example-generic-ecommerce.json \
  --output architecture.puml

# Activity diagram with swimlanes (cross-platform, generic example)
bash scripts/run_generator.sh generate activity \
  --input references/activity-example-generic-registration.json \
  --output workflow.puml

# Sequence diagram (cross-platform, generic example)
bash scripts/run_generator.sh generate sequence \
  --input references/sequence-example-generic-order.json \
  --output interactions.puml

# Validate PlantUML syntax (cross-platform)
bash scripts/run_generator.sh validate --file architecture.puml
```

**Direct invocation (if you know your Python command)**:
```bash
# Use python3 (Linux/macOS) or python (Windows)
python3 scripts/plantuml_generator.py generate component --input data.json --output diagram.puml
# OR
python scripts/plantuml_generator.py generate component --input data.json --output diagram.puml
```

**Why use run_generator.sh?**
- Automatically detects `python` vs `python3` command
- Verifies Python version is 3.10+
- Works on all platforms (Windows Git Bash, Linux, macOS, WSL)
- Clear error messages if Python not installed or wrong version

### Example JSON Files

The `references/` directory contains sample JSON input files:

**Generic Examples (recommended for learning):**
- `component-example-generic-ecommerce.json` - E-Commerce Platform Architecture with order, payment, inventory services
- `activity-example-generic-registration.json` - User Registration Workflow with swimlanes (User, Frontend, Backend, Email Service)
- `sequence-example-generic-order.json` - Order Processing Sequence showing inventory and payment flow

These files demonstrate the expected JSON structure for each diagram type. Use them as templates for your own diagrams.

## Examples

See detailed examples in:

**Generic JSON Input Templates (recommended):**
- `references/component-example-generic-ecommerce.json` - E-Commerce component diagram
- `references/activity-example-generic-registration.json` - User registration activity diagram
- `references/sequence-example-generic-order.json` - Order processing sequence diagram

**RNVS-Specific JSON Input Templates:**
- `references/component-example.json` - PDA Import component diagram with microservices, databases, Message Bus
- `references/activity-example.json` - Number Porting activity diagram with swimlanes (TNB-A, BNetzA, TNB-B)
- `references/sequence-example.json` - PDA Import sequence diagram showing validation flow

**Usage Scenarios:**
- `references/examples.md` - Complete examples for Phases 2, 5, 6, 7 with PlantUML output

**Quick Start (Cross-Platform):**
```bash
# Generate component diagram (generic example)
bash scripts/run_generator.sh generate component \
  --input references/component-example-generic-ecommerce.json \
  --output diagram.puml

# Generate activity diagram (generic example)
bash scripts/run_generator.sh generate activity \
  --input references/activity-example-generic-registration.json \
  --output workflow.puml

# Generate sequence diagram (generic example)
bash scripts/run_generator.sh generate sequence \
  --input references/sequence-example-generic-order.json \
  --output interactions.puml
```

## Integration with Agents

Agents should generate diagrams by:

1. **Creating JSON input** with diagram structure
2. **Writing JSON to file** in feature directory
3. **Invoking CLI tool via cross-platform wrapper** using Bash command
4. **Saving generated .puml file** to results

**Example workflow:**
```python
# Step 1: Create diagram structure
diagram_data = {
    "title": "VNRM Architecture",
    "components": [
        {"name": "vnrm-validation-service", "type": "business", "description": "Validates input"},
        {"name": "validation-db", "type": "database", "description": "PostgreSQL"}
    ],
    "dependencies": [
        {"from": "vnrm-validation-service", "to": "validation-db", "label": "Read/Write"}
    ],
    "color_scheme": color_scheme
}

# Step 2: Write JSON to file
write_file("results/feature/phase6/architecture-input.json", json.dumps(diagram_data))

# Step 3: Generate diagram via cross-platform wrapper (RECOMMENDED)
bash_command = """
bash ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/plantuml-generator/scripts/run_generator.sh generate component \
  --input results/feature/phase6/architecture-input.json \
  --output results/feature/phase6/architecture.puml
"""

# Alternative: Direct Python invocation (if you know the command)
# bash_command = """
# python3 ${CLAUDE_PLUGIN_ROOT}/skills/validation-generation/plantuml-generator/scripts/plantuml_generator.py generate component \
#   --input results/feature/phase6/architecture-input.json \
#   --output results/feature/phase6/architecture.puml
# """

# Step 4: CLI tool handles validation and generation automatically
# The wrapper auto-detects Python and verifies version 3.10+
```

**Benefits of using run_generator.sh:**
- ✅ Cross-platform compatibility (Windows/Linux/macOS/WSL)
- ✅ Automatic Python command detection (python vs python3)
- ✅ Python version verification (3.10+)
- ✅ Clear error messages if Python missing or wrong version

## File Organization

- **SKILL.md** (this file) - Skill overview, usage, best practices
- **references/examples.md** - Complete Phase 2, 5, 6, 7 diagram generation workflows
- **references/*.json** - JSON input templates for each diagram type
- **scripts/plantuml_generator.py** - Python CLI tool for generation and validation

## Best Practices

### Diagram Generation
1. **Use JSON Schema**: Define diagram structure in JSON for version control and reusability
2. **Consistent Styling**: Always use the standard RNVS/VNRM color scheme
3. **Layout Optimization**: Leverage automatic layout pragmas (smetana, ortho lines)
4. **Incremental Building**: Build complex diagrams incrementally, validating at each step
5. **Template Reuse**: Create domain-specific templates for common architecture patterns

### Visual Design
1. **Clear Labels**: Use descriptive names for components and arrows (avoid abbreviations)
2. **Legend**: Always include legend for color meanings in multi-type diagrams
3. **Notes**: Add contextual notes to explain business logic or technical decisions
4. **Spacing**: Use adequate spacing (nodesep, ranksep) to avoid cluttered diagrams
5. **Arrow Types**: Choose appropriate arrow types (solid for sync, dotted for return, async for events)

### Validation Strategy
1. **Two-Tier Approach**: Use built-in validation first, then CLI validation for production
2. **Early Validation**: Validate during generation, not after completion
3. **Warning Review**: Review warnings even if syntax is valid (may indicate design issues)
4. **Test Rendering**: Always render diagrams visually before committing to repository

### File Management
1. **Descriptive Naming**: Use names like `phase2_dependencies.puml`, `vnrm_prt_architecture.puml`
2. **Version Control**: Store both JSON input and generated .puml files in git
3. **Documentation**: Keep diagram documentation adjacent to source (e.g., README.md)
4. **Automation**: Use CLI tool for batch generation in CI/CD pipelines

### Performance Tips
1. **Limit Complexity**: Keep diagrams focused (max 10-15 components per diagram)
2. **Split Large Systems**: Create multiple diagrams for different architectural views
3. **Avoid Deep Nesting**: Limit partition and swimlane nesting to 2-3 levels
4. **Cache Results**: Reuse validated diagrams rather than regenerating unnecessarily

## Error Handling

If PlantUML generation fails:
1. Check syntax with `validate_syntax()`
2. Review error messages for common issues
3. Simplify diagram and test incrementally
4. Verify all stereotypes are defined
5. Check for unclosed blocks or quotes

---

**Use this skill whenever you need to create PlantUML diagrams for RNVS/VNRM architecture visualization!**
