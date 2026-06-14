# Phase 2 Dependency Visualization - Reference Examples

This directory contains example PlantUML diagrams demonstrating the three diagram types created in Phase 2.

## Example Files

### 1. example-NBM-dependencies.puml
**Module & Technology Dependency Diagram** (High-Level)

**Purpose**: Stakeholder communication and architecture overview

**Shows**:
- 3 logical modules (RNB, TNB, Validation)
- 3 programming languages (PL/SQL, C++, TCL) with file counts
- 3 external systems (BNetzA Gateway, CRM-T, Number Block Registry)
- Module-to-module dependencies
- Module-to-language connections
- Module-to-external-system integrations

**Key Features**:
- Notes with business context (KCODE values, purpose)
- File counts per language per module
- Clear separation of RNVS modules vs external systems

**When to Use**:
- Present to non-technical stakeholders
- Architecture documentation
- Migration planning discussions

---

### 2. example-NBM-dependencies_detailed.puml
**Detailed Component Diagram** (File-Level)

**Purpose**: Developer reference and migration planning

**Shows**:
- 12 individual code files (5 PL/SQL, 4 C++, 3 TCL)
- File-to-file dependencies with relationship details
- Color coding by relevance (green = high ≥70, yellow = medium 40-69)
- Cross-language invocations (C++ → PL/SQL, TCL → PL/SQL)
- External system integration points

**Key Features**:
- Packages group files by programming language
- Stereotypes indicate file type (<<Package Body>>, <<Manager>>, <<Script>>)
- Legend explains color coding and relationship types
- Notes highlight core components with line counts and relevance scores
- Dotted arrows show cross-language invocations

**When to Use**:
- Developer onboarding (understand codebase structure)
- Code review (identify high-coupling areas)
- Migration planning (identify which files to migrate together)
- Dependency impact analysis (what breaks if we change file X?)

**Complexity**: 12 components (under 20 threshold, single diagram appropriate)

---

### 3. example-NBM-dependencies_detailed_rnb.puml
**Split Detailed Diagram** (Single Module Focus)

**Purpose**: Detailed view of one module when total components >20

**Shows**:
- RNB module only (6 files: 2 PL/SQL, 2 C++, 2 TCL)
- Intra-module dependencies (within RNB)
- Inter-module dependencies (RNB to TNB, Validation, Common)
- External module dependencies shown as <<Cloud>> package
- External system integrations (BNetzA, CRM-T, Database)

**Key Features**:
- Focused view prevents diagram clutter
- External module dependencies clearly distinguished (<<Cloud>> stereotype)
- Legend references other split diagrams (dependencies_detailed_tnb.puml, dependencies_detailed_validation.puml)
- All RNB components in green (high relevance)

**When to Use**:
- Total components exceed 20 (diagram would be cluttered)
- Deep-dive into specific module
- Module-specific code review or migration planning
- Isolate one module's dependencies for analysis

**Splitting Strategy**:
- Create one diagram per module
- Show intra-module dependencies in full detail
- Show inter-module dependencies as external references
- Each split diagram references related diagrams in legend

---

## Choosing Between Diagram Types

| Scenario | Recommended Diagram |
|----------|---------------------|
| Present to business stakeholders | dependencies.puml (module-level) |
| Present to architects | dependencies.puml (module-level) |
| Developer onboarding | dependencies_detailed.puml (file-level) |
| Code review session | dependencies_detailed.puml (file-level) |
| ≤20 total components | dependencies_detailed.puml (single diagram) |
| >20 total components | dependencies_detailed_${module}.puml (split diagrams) |
| Deep-dive one module | dependencies_detailed_${module}.puml (split) |
| Migration impact analysis | Both (module-level + detailed) |

---

## Diagram Conventions

### Package Grouping
- **"RNVS NBM Modules"**: Logical business modules
- **"Programming Languages"**: Technology layers (PL/SQL, C++, TCL, Java, Shell)
- **"PL/SQL Components"**: All PL/SQL files grouped together
- **"C++ Components"**: All C++ files grouped together
- **"External Module Dependencies"**: Dependencies on other modules (when split)

### Icons and Stereotypes
- `cloud "External Systems"`: Third-party or external systems (BNetzA, CRM-T)
- `database "Data Storage"`: Database systems
- `<<Package Body>>`: PL/SQL package body
- `<<Package Spec>>`: PL/SQL package specification
- `<<Manager>>`: C++ manager class
- `<<Header>>`: C++ header file
- `<<Script>>`: TCL/Shell script
- `<<Utility>>`: Utility library
- `<<Component>>`: General component class
- `<<Cloud>>`: External module dependency (in split diagrams)

### Arrow Types
- `-->`: Direct dependency (includes, calls, executes)
- `..>`: Cross-language invocation (C++ to PL/SQL bridge, TCL SqlStoPro)
- `-down->`: Layout hint (force arrow downward)
- `-right->`: Layout hint (force arrow rightward)

### Color Scheme
- **#LightGreen**: High relevance (score ≥ 70)
- **#LightYellow**: Medium relevance (score 40-69)
- **#LightGray**: Low relevance (score 1-39) - rarely shown
- **No color**: External systems, databases (neutral)

### Notes
- **Right of component**: Business context, KCODE values, purpose
- **Bottom of component**: Technical details, line counts, scores
- **Standalone notes**: General explanations, legends, references

---

## Validation

All example diagrams have been validated:
- ✅ **Syntax**: PlantUML syntax is valid (no errors)
- ✅ **Renderability**: Successfully renders to SVG/PNG
- ✅ **Source Accuracy**: All components and dependencies derived from Phase 1 example data
- ✅ **Visual Clarity**: Appropriate component count, clear grouping, readable layout

To validate these diagrams yourself:
```bash
# Syntax check (Level 1: regex validation built into Phase 2 workflow)

# Renderability check (Level 2: requires PlantUML CLI)
java -jar plantuml.jar -tsvg example-NBM-dependencies.puml
java -jar plantuml.jar -tsvg example-NBM-dependencies_detailed.puml
java -jar plantuml.jar -tsvg example-NBM-dependencies_detailed_rnb.puml
```

---

## Customization Examples

### Change Color Scheme from Relevance to Language
Replace relevance-based colors with language-based colors:

```plantuml
' Instead of:
RNB_BODY #LightGreen  ' High relevance
TNB_BODY #LightYellow  ' Medium relevance

' Use:
RNB_BODY #LightBlue    ' PL/SQL
RNB_MGR #Orange        ' C++
KCODE_TCL #LightGreen  ' TCL
```

### Add Sequence Numbers to Dependencies
Show execution order:

```plantuml
KCODE_TCL --> RNB_UTILS : 1. load utilities
KCODE_TCL --> RNB_BODY : 2. call p_rnb.process_kcode
RNB_BODY --> TNB_BODY : 3. validate operator
RNB_BODY --> DB : 4. update T_RNB
```

### Add Deployment Information
Show where components run:

```plantuml
node "Application Server" {
  [RnvsRnbManager.cpp]
  [kcode_processor.tcl]
}

node "Database Server" {
  [pack_body_rnb.sql]
  [pack_body_tnb.sql]
}
```

### Add Component Metrics
Show complexity or size:

```plantuml
[pack_body_rnb.sql] as RNB_BODY <<Package Body>>
note right of RNB_BODY
  Lines: 2,847
  Procedures: 23
  Functions: 12
  Cyclomatic Complexity: 156
end note
```

---

## See Also

- **Phase 1 Examples**: `../../01-code-analysis-workflow/references/` - Source data for these diagrams
- **PlantUML Syntax Skill**: `../../../foundation/plantuml-syntax/` - Full PlantUML reference
- **Phase 2 Workflow Skill**: `../SKILL.md` - Complete Phase 2 workflow documentation
