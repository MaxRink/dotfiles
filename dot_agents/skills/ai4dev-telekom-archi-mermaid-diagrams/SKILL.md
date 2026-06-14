---
name: ai4dev-telekom-archi-mermaid-diagrams
description: >
  Create any type of Mermaid diagram — flowcharts, sequence diagrams, class diagrams, ER diagrams,
  C4 architecture diagrams, state diagrams, Gantt charts, git graphs, mindmaps, timelines, pie charts,
  quadrant charts, Sankey diagrams, block diagrams, architecture-beta diagrams, radar charts, kanban boards,
  XY charts, packet diagrams, and requirement diagrams. Use this skill whenever the user asks to create,
  fix, improve, or convert any Mermaid diagram. Trigger for any mention of "Mermaid", "diagram", "flowchart",
  "sequence diagram", "class diagram", "ER diagram", "C4 diagram", "state diagram", "Gantt chart", "mindmap",
  "timeline", or "draw me a...", "visualize this", "chart this".
  Also use when converting diagrams between formats, debugging Mermaid syntax errors, or styling diagrams.
argument-hint: "[diagram description or existing diagram to fix]"
allowed-tools: Read, Glob, Grep, mcp__mermaidchart__validate_and_render_mermaid_diagram
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telekom-archi/skills/mermaid-diagrams by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Mermaid Diagrams Skill

You create clear, correct, and visually effective Mermaid diagrams. Mermaid renders diagrams from text definitions — version-controllable, embeddable in Markdown, and no external tools needed.

## Diagram Selection Guide

| Need | Diagram | Syntax Keyword |
|------|---------|---------------|
| Process flow, decision logic | Flowchart | `graph TD` / `graph LR` |
| Service/API interactions | Sequence | `sequenceDiagram` |
| Domain model, class structure | Class | `classDiagram` |
| Database schema | ER | `erDiagram` |
| System landscape (C4 Level 1) | C4 Context | `C4Context` |
| System internals (C4 Level 2) | C4 Container | `C4Container` |
| Service internals (C4 Level 3) | C4 Component | `C4Component` |
| Deployment view (C4 Level 4) | C4 Deployment | `C4Deployment` |
| Infrastructure topology | Architecture | `architecture-beta` |
| Lifecycle, state machine | State | `stateDiagram-v2` |
| Project schedule | Gantt | `gantt` |
| Branch/merge history | Git Graph | `gitGraph` |
| Concept mapping | Mindmap | `mindmap` |
| Roadmap, chronology | Timeline | `timeline` |
| Proportions | Pie | `pie` |
| Prioritization matrix | Quadrant | `quadrantChart` |
| Data flow volumes | Sankey | `sankey-beta` |
| High-level blocks | Block | `block-beta` |
| User journey | Journey | `journey` |
| Line/bar charts | XY Chart | `xychart` |
| Multi-axis comparison | Radar | `radar-beta` |
| Task workflow board | Kanban | `kanban` |
| Network packet structure | Packet | `packet` |
| Requirements traceability | Requirement | `requirementDiagram` |

## Quality Rules

These apply to every diagram you create:

1. **Readable labels** — Full descriptive names, not abbreviations. "Order Service" not "OrdSvc".
2. **Meaningful connections** — Label edges with what flows or happens. "Sends order event" not just an arrow.
3. **Right size** — 7-20 elements per diagram. More than 20? Split into multiple diagrams.
4. **Consistent naming** — Same element = same name across diagrams. Don't rename between views.
5. **Direction matters** — Choose `TD` (top-down) for hierarchies, `LR` (left-right) for flows and timelines.
6. **Styling for emphasis** — Use color/style to highlight what matters, not to decorate. Max 3-4 colors.
7. **Correct syntax** — Always validate mentally. Common mistakes: missing quotes in labels with spaces, wrong arrow syntax, unclosed subgraphs.

## Quick Reference — Core Diagram Types

### Flowcharts

```mermaid
graph TD
  A[Start] --> B{Decision?}
  B -->|Yes| C[Action A]
  B -->|No| D[Action B]
  C --> E[End]
  D --> E
```

**Node shapes:** `[Rectangle]` `(Rounded)` `{Diamond}` `[(Database)]` `((Circle))` `[[Subroutine]]` `{{Hexagon}}` `>Asymmetric]`

**Edges:** `-->` solid arrow, `-.->` dotted, `==>` thick, `<-->` bidirectional, `-- text -->` labeled

**Subgraphs:**
```mermaid
graph LR
  subgraph Backend
    direction TB
    API --> DB[(Database)]
  end
  subgraph Frontend
    Web --> API
  end
```

### Sequence Diagrams

```mermaid
sequenceDiagram
  actor User
  participant API as API Gateway
  participant Svc as Service
  participant DB as Database

  User->>API: POST /orders
  activate API
  API->>Svc: createOrder()
  activate Svc
  Svc->>DB: INSERT
  DB-->>Svc: OK
  Svc-->>API: Order created
  deactivate Svc
  API-->>User: 201 Created
  deactivate API
```

**Arrows:** `->>` solid, `-->>` dashed, `-x` lost message, `-)` async
**Blocks:** `alt/else`, `opt`, `loop`, `par/and`, `critical/option`, `break`, `rect rgb(...)` highlight

**Activate/Deactivate Rules (critical for valid syntax):**
- `activate X` and `deactivate X` must be balanced — every activate needs exactly one deactivate
- **Never deactivate inside both branches of an `alt/else`** — this causes "inactivate an inactive participant" errors. Instead, deactivate BEFORE the `alt` or AFTER the `end`:
```text
  %% WRONG — deactivates RL twice (once per branch):
  alt Condition
    RL-->>GW: Response A
    deactivate RL
  else Other
    RL-->>GW: Response B
    deactivate RL        %% ERROR: RL already deactivated in alt branch
  end

  %% CORRECT — deactivate before branching:
  activate RL
  RL-->>GW: Response
  deactivate RL
  alt Condition
    GW-->>Client: Path A
  else Other
    GW-->>Client: Path B
  end
```
- Keep activations short — activate right before the call, deactivate right after the response
- Nested activations on the same participant are allowed (shows recursive/re-entrant calls)

### Class Diagrams

```mermaid
classDiagram
  class Order {
    <<aggregate root>>
    -UUID id
    -OrderStatus status
    -List~OrderLine~ lines
    +addLine(product, qty)
    +submit()
    +cancel()
  }
  class OrderLine {
    <<value object>>
    -Product product
    -int quantity
    +subtotal() Money
  }
  Order *-- OrderLine : contains
  Order --> OrderStatus : has
```

**Relationships:** `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association, `..>` dependency, `..|>` realization

### ER Diagrams

```mermaid
erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  LINE_ITEM }o--|| PRODUCT : references

  CUSTOMER {
    uuid id PK
    string email UK
    string name
  }
  ORDER {
    uuid id PK
    uuid customer_id FK
    enum status
    timestamp created_at
  }
```

**Cardinality:** `||` exactly one, `o|` zero or one, `|{` one or more, `o{` zero or more
**Line:** `--` identifying (solid), `..` non-identifying (dotted)

### State Diagrams

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Submitted : submit()
  Submitted --> InReview : assign_reviewer()
  InReview --> Approved : approve()
  InReview --> Rejected : reject()
  Approved --> [*]
  Rejected --> Draft : revise()
```

### Gantt Charts

```mermaid
gantt
  title Project Timeline
  dateFormat YYYY-MM-DD
  section Design
    Requirements    :a1, 2024-01-01, 14d
    Architecture    :a2, after a1, 10d
  section Development
    Backend         :b1, after a2, 30d
    Frontend        :b2, after a2, 25d
  section Testing
    Integration     :c1, after b1, 10d
    UAT             :c2, after c1, 7d
```

### Git Graphs

```mermaid
gitGraph
  commit id: "init"
  branch develop
  commit id: "feat-1"
  branch feature/auth
  commit id: "auth-impl"
  commit id: "auth-tests"
  checkout develop
  merge feature/auth
  checkout main
  merge develop tag: "v1.0"
```

### Mindmaps

```mermaid
mindmap
  root((Project))
    Frontend
      React
      TypeScript
      Tailwind
    Backend
      Node.js
      PostgreSQL
      Redis
    Infrastructure
      AWS
      Kubernetes
      Terraform
```

### Timeline

```mermaid
timeline
  title Release Plan
  section Q1
    January : Feature A launch
    March : Feature B beta
  section Q2
    April : Feature B GA
    June : Performance optimization
```

### Pie Charts

```mermaid
pie title Traffic Distribution
  "API Service" : 45
  "Web Frontend" : 30
  "Mobile App" : 20
  "Legacy" : 5
```

### Quadrant Charts

```mermaid
quadrantChart
  title Build vs Buy
  x-axis Low Complexity --> High Complexity
  y-axis Low Strategic Value --> High Strategic Value
  quadrant-1 Build in-house
  quadrant-2 Strategic partnership
  quadrant-3 Buy off-the-shelf
  quadrant-4 Evaluate carefully
  Auth System: [0.4, 0.8]
  CRM: [0.7, 0.3]
  Payment Gateway: [0.8, 0.6]
  Logging: [0.3, 0.2]
```

### Architecture-beta (Infrastructure)

```mermaid
architecture-beta
  group cloud(cloud)[Cloud]
  group app(server)[Application] in cloud

  service lb(internet)[Load Balancer] in cloud
  service api(server)[API Server] in app
  service db(database)[Database] in app
  service cache(database)[Cache] in app

  lb:R -- L:api
  api:R -- L:db
  api:B -- T:cache
```

**Icons:** `cloud`, `database`, `disk`, `server`, `internet`
**Directions:** `L` left, `R` right, `T` top, `B` bottom

**Architecture-beta Syntax Rules (critical — very strict parser):**
- **Labels in `[]` CANNOT contain special characters:** no dots (`.`), slashes (`/`), plus (`+`), colons (`:`), ampersands (`&`). Use plain text only.
  ```
  %% WRONG — parser chokes on dots, slashes, plus:
  group vpc(cloud)[VPC 10.0.0.0/16]
  service prom(server)[Prometheus + Grafana]
  service bss(server)[BSS/CRM Adapter]

  %% CORRECT — plain text labels:
  group vpc(cloud)[VPC] in cloud
  service prom(server)[Monitoring Stack] in mgmt
  service bss(server)[BSS Integration] in mgmt
  ```
- **Edges can ONLY connect services and junctions** — never groups. You cannot write `nat:B -- T:datanet` where `datanet` is a group.
- **Every service/junction must be declared before it appears in an edge.**
- **Edge format is strict:** `serviceA:DIRECTION -- DIRECTION:serviceB` with exactly one space around `--`.

### Sankey

```mermaid
sankey-beta
Source,Target,Value
Frontend,API Gateway,5000
API Gateway,Auth Service,5000
API Gateway,Order Service,3000
API Gateway,Catalog Service,2000
Order Service,Database,3000
Order Service,Cache,2500
```

### Journey (User Experience)

```mermaid
journey
  title User Checkout Flow
  section Browse
    Visit homepage: 5: User
    Search product: 4: User
    View details: 4: User
  section Purchase
    Add to cart: 5: User
    Enter payment: 2: User
    Confirm order: 4: User, System
  section Post-Purchase
    Receive confirmation: 5: System
    Track delivery: 3: User
```

## Styling and Theming

### Global Theme
```text
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#E20074', 'primaryTextColor': '#fff', 'lineColor': '#333'}}}%%
```

Available themes: `default`, `forest`, `dark`, `neutral`, `base` (customizable)

### Per-Node Styling (Flowcharts)
```text
style nodeId fill:#E20074,stroke:#333,stroke-width:2px,color:#fff
```

### CSS Classes
```text
classDef highlight fill:#E20074,stroke:#333,color:#fff
classDef external fill:#ddd,stroke:#999,color:#333
class ServiceA,ServiceB highlight
class ExternalAPI external
```

### Telekom Brand Colors
- Magenta: `#E20074` (primary)
- Dark: `#1A1A1A`
- Gray: `#EDEDED`
- White: `#FFFFFF`

## Common Syntax Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Diagram won't render | Missing diagram type keyword | Start with `graph TD`, `sequenceDiagram`, etc. |
| Label not showing | Spaces in unquoted label | Use `A["Label With Spaces"]` |
| Subgraph broken | Missing `end` keyword | Close every `subgraph` with `end` |
| Arrow not rendering | Wrong syntax for diagram type | Flowchart: `-->`, Sequence: `->>`, Class: `-->` |
| C4 element missing | Wrong function name | `System()` not `system()`, case-sensitive |
| Style not applied | Wrong node ID | Style ID must match the node alias exactly |

## Detailed Reference

Per-diagram-type reference files are in `references/`. Read only the ones you need:

- **[references/index.md](references/index.md)** — Full index of all 22 diagram types with links
- **[references/c4-diagrams.md](references/c4-diagrams.md)** — C4 Context, Container, Component, Deployment, Dynamic
- **[references/architecture-beta.md](references/architecture-beta.md)** — Infrastructure topology (strict syntax rules)
- **[references/flowchart.md](references/flowchart.md)** — Process flows, decision trees
- **[references/sequence-diagram.md](references/sequence-diagram.md)** — Service interactions, activate/deactivate rules
- **[references/class-diagram.md](references/class-diagram.md)** — Domain models, DDD
- **[references/er-diagram.md](references/er-diagram.md)** — Database schemas
- **[references/state-diagram.md](references/state-diagram.md)** — State machines
- **[references/quadrant-chart.md](references/quadrant-chart.md)** — Technology assessment (strict label rules)
- **[references/styling.md](references/styling.md)** — Themes, colors, CSS classes
