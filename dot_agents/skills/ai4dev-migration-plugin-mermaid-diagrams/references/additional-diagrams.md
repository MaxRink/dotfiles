# Additional Diagram Types

Reference for pie charts, mindmaps, timelines, sankey diagrams, block diagrams, packet diagrams, kanban boards, and XY charts.

> **NEVER use literal `\n`** — use `<br>` for multi-line labels.

## Contents

- [Pie Chart](#pie-chart)
- [Mindmap](#mindmap)
- [Timeline](#timeline)
- [XY Chart](#xy-chart)
- [Block Diagram](#block-diagram)
- [Sankey Diagram](#sankey-diagram)
- [Packet Diagram](#packet-diagram)
- [Kanban Board](#kanban-board)

---

## Pie Chart

**Declaration:** `pie`

```mermaid
pie showData title "Technology Distribution"
    "Java" : 35
    "JavaScript" : 25
    "Python" : 20
    "Go" : 12
    "Other" : 8
```

- `showData` — renders numeric values next to legend (optional)
- `title` — optional, must be in quotes
- Values must be positive numbers > 0
- Slices render clockwise in source order

**Config:**

```yaml
---
config:
  pie:
    textPosition: 0.75
---
```

`textPosition`: `0.0` (center) to `1.0` (outer edge), default `0.75`

---

## Mindmap

**Declaration:** `mindmap`

Hierarchy is defined by indentation level:

```mermaid
mindmap
    root((Migration Strategy))
        Analysis
            Code inventory
            Dependency mapping
            Risk assessment
        Planning
            Architecture design
            Timeline
            Resource allocation
        Execution
            Wave 1
            Wave 2
            Wave 3
        Validation
            Testing
            Performance
            Security audit
```

### Node Shapes

```mermaid
mindmap
    root
        Square[Square]
        Rounded(Rounded)
        Circle((Circle))
        Bang)Bang(
        Cloud)Cloud(
        Hexagon{{Hexagon}}
```

**Markdown in labels:** `**bold**`, `*italic*` supported.

**Config:**

```yaml
---
config:
  layout: tidy-tree
---
```

---

## Timeline

**Declaration:** `timeline`

```mermaid
timeline
    title Application Evolution
    section 2020
        Jan : Monolith deployed
            : Initial team of 5
        Jun : First microservice extracted
    section 2022
        Mar : Kubernetes adoption
            : Service mesh added
        Sep : Event-driven architecture
    section 2024
        Jan : Cloud-native migration
        Jun : Multi-region deployment
```

- Multiple events per time period: add indented lines with `:`
- `section` groups time periods visually
- Free-form strings for time periods (not limited to dates)

### Direction (v11.14.0+)

```mermaid
timeline LR
    title Left to Right
    2020 : Event A
    2022 : Event B
```

Directions: `LR` (default), `TD`

---

## XY Chart

**Declaration:** `xychart` or `xychart horizontal`

```mermaid
xychart
    title "Monthly Revenue"
    x-axis "Month" [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Revenue ($K)" 0 --> 500
    bar [120, 200, 180, 350, 280, 420]
    line [100, 210, 170, 330, 290, 400]
```

- Both `bar` and `line` series can coexist
- Multiple series of each type allowed
- Axes are optional (auto-range from data)

### Numeric X-Axis

```mermaid
xychart
    title "Performance"
    x-axis 0 --> 100
    y-axis 0 --> 1000
    line [100, 300, 500, 700, 900]
```

### Data Labels (v11.14.0+)

```yaml
---
config:
  xyChart:
    showDataLabel: true
    showDataLabelOutsideBar: true
---
```

---

## Block Diagram

**Declaration:** `block`

Manual-layout diagrams with full positioning control:

```mermaid
block
    columns 3

    a["Frontend"]
    b["API Gateway"]
    c["Auth Service"]

    space
    d["Business Logic"]
    space

    e["Database"]
    f["Cache"]
    g["Message Queue"]

    a --> b
    b --> c
    b --> d
    d --> e
    d --> f
    d --> g
```

### Key Features

- `columns N` — set column count for auto-wrap
- `space` / `space:N` — empty cells for layout gaps
- Composite blocks: `parent[ child1 child2 ]`
- Shape support: `round`, `stadium`, `cylindrical`, `circle`, `rhombus`, `hexagon`, `parallelogram`, `trapezoid`, `double-circle`

---

## Sankey Diagram

**Declaration:** `sankey` (experimental)

CSV format with 3 columns — source, target, value:

```mermaid
sankey
    Source Code,Analysis,500
    Source Code,Dependencies,300
    Analysis,Risk Assessment,200
    Analysis,Complexity Score,300
    Dependencies,Direct,200
    Dependencies,Transitive,100
    Risk Assessment,High Risk,80
    Risk Assessment,Low Risk,120
```

**CSV rules:**

- Empty lines allowed for visual separation
- Commas in names: `"Node, Name",Target,50`
- Escaped quotes: `"Node ""Quoted""",Target,50`

**Config:**

```yaml
---
config:
  sankey:
    linkColor: gradient
    nodeAlignment: justify
---
```

`linkColor`: `source`, `target`, `gradient`, `#hexcode`
`nodeAlignment`: `justify`, `center`, `left`, `right`

---

## Packet Diagram

**Declaration:** `packet`

### Range Syntax

Ranges must be contiguous — each row continues from where the previous ended:

```mermaid
packet
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    100-105: "Reserved"
    106-111: "Flags"
    112-127: "Window Size"
```

### Bit-Count Syntax (v11.7.0+)

Auto-increments position:

```mermaid
packet
    +16: "Source Port"
    +16: "Destination Port"
    +32: "Sequence Number"
    +32: "Acknowledgment Number"
    +4: "Offset"
    +6: "Reserved"
    +6: "Flags"
    +16: "Window"
```

Both syntaxes can be mixed. Config: `bitsperrow`, `bitwidth`, `rowheight`, `showbits`

---

## Kanban Board

**Declaration:** `kanban`

```mermaid
kanban
    todo[Todo]
        task1[Analyze dependencies]
        task2[Map API contracts]
    progress[In Progress]
        task3[Migrate auth service]
    review[Review]
        task4[Database schema migration]
    done[Done]
        task5[Infrastructure setup]
```

Metadata support (`@{ assigned, ticket, priority }`) requires Mermaid v11.4.0+ and proper indentation matching the task node. Check your renderer version before using metadata.

### Metadata Keys

| Key | Values |
|-----|--------|
| `assigned` | Free text (name) |
| `ticket` | Free text (ticket ID) |
| `priority` | `Very High`, `High`, `Low`, `Very Low` |

### Ticket Links

```yaml
---
config:
  kanban:
    ticketBaseUrl: 'https://jira.example.com/browse/#TICKET#'
---
```

`#TICKET#` is replaced with the `ticket` metadata value.

**Important:** Proper indentation is mandatory; all IDs must be unique.

---

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Choose the right chart** — Match visualization to data type
3. **Keep data readable** — Limit pie slices to ~7, bar items to ~12
4. **Use sections** — Group timeline events and gantt tasks logically
5. **Label axes** — Always label XY chart axes with units
