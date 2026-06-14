# Mermaid Diagrams for Architecture — Quick Reference

For full syntax details on any diagram type, see the per-diagram reference files in the `mermaid-diagrams` skill at `skills/mermaid-diagrams/references/`.

## Diagram Selection for Architecture

| Architecture Need | Diagram Type | Reference |
|------------------|-------------|-----------|
| System landscape (C4 L1) | `C4Context` | [c4-diagrams.md](../../mermaid-diagrams/references/c4-diagrams.md) |
| System internals (C4 L2) | `C4Container` | [c4-diagrams.md](../../mermaid-diagrams/references/c4-diagrams.md) |
| Service internals (C4 L3) | `C4Component` | [c4-diagrams.md](../../mermaid-diagrams/references/c4-diagrams.md) |
| Deployment view (C4 L4) | `C4Deployment` | [c4-diagrams.md](../../mermaid-diagrams/references/c4-diagrams.md) |
| Infrastructure topology | `architecture-beta` | [architecture-beta.md](../../mermaid-diagrams/references/architecture-beta.md) |
| Service interactions | `sequenceDiagram` | [sequence-diagram.md](../../mermaid-diagrams/references/sequence-diagram.md) |
| Process flow | `graph TD/LR` | [flowchart.md](../../mermaid-diagrams/references/flowchart.md) |
| Domain model | `classDiagram` | [class-diagram.md](../../mermaid-diagrams/references/class-diagram.md) |
| Database schema | `erDiagram` | [er-diagram.md](../../mermaid-diagrams/references/er-diagram.md) |
| State machine | `stateDiagram-v2` | [state-diagram.md](../../mermaid-diagrams/references/state-diagram.md) |
| Technology assessment | `quadrantChart` | [quadrant-chart.md](../../mermaid-diagrams/references/quadrant-chart.md) |
| Architecture roadmap | `timeline` | [timeline.md](../../mermaid-diagrams/references/timeline.md) |
| Capability mapping | `mindmap` | [mindmap.md](../../mermaid-diagrams/references/mindmap.md) |
| Data flow volumes | `sankey-beta` | [sankey.md](../../mermaid-diagrams/references/sankey.md) |
| High-level blocks | `block-beta` | [block-diagram.md](../../mermaid-diagrams/references/block-diagram.md) |
| Line/bar charts | `xychart` | [xy-chart.md](../../mermaid-diagrams/references/xy-chart.md) |
| Multi-axis comparison | `radar-beta` | [radar-chart.md](../../mermaid-diagrams/references/radar-chart.md) |
| Task workflow | `kanban` | [kanban.md](../../mermaid-diagrams/references/kanban.md) |
| Requirements traceability | `requirementDiagram` | [requirement-diagram.md](../../mermaid-diagrams/references/requirement-diagram.md) |
| Styling and theming | — | [styling.md](../../mermaid-diagrams/references/styling.md) |

## Critical Syntax Pitfalls

1. **Sequence diagrams:** Never `deactivate` inside both branches of `alt/else`. Use `+`/`-` shorthand on arrows instead.
2. **Quadrant charts:** Labels must be plain text — no em dashes, parentheses, or special Unicode.
3. **Architecture-beta:** Labels in `[]` must be plain text only — no dots, slashes, plus, colons, ampersands, parentheses.
4. **C4 elements:** Function names are case-sensitive — `System()` not `system()`.

## Architecture-Specific Patterns

### Recommended Diagram Sets

**Minimal set (most projects):**
1. C4 Context — system landscape
2. C4 Container — system decomposition
3. Sequence diagrams — key interaction flows

**Full architecture document:**
1. C4 Context — system landscape
2. C4 Container — system decomposition
3. C4 Component — key service internals
4. Sequence diagrams — critical flows
5. ER diagram — data model
6. Architecture-beta — infrastructure topology
7. Timeline — roadmap

### Quality Rules

- Stay under 20 elements per diagram (sweet spot: 7-15)
- Every element needs: name, type, technology, description
- Use action verbs for relationship labels with technology/protocol
- Prefer unidirectional arrows showing dependency direction
- Group related elements with boundaries/subgraphs
- Consistent naming across related diagrams
