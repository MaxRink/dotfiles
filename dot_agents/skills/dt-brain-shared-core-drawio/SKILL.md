---
name: dt-brain-shared-core-drawio
description: >
  Generate draw.io (.drawio) diagram files programmatically. Use this skill when asked to create
  architecture diagrams, dependency graphs, flowcharts, org charts, network diagrams, or any
  visual diagram that should be saved as a .drawio file. Handles proper XML escaping, layout,
  colors, grouping, and edge routing.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/core-drawio by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Draw.io File Generator

Generate valid `.drawio` XML files that open correctly in draw.io desktop, VS Code extension, and app.diagrams.net.

## Workflow

1. Choose a layout strategy (see `references/layouts.md` if unsure)
2. Write a Python script using `drawio_utils.py` to build the diagram
3. The script validates XML automatically on write

## Critical Rules

1. **Always use `xml.etree.ElementTree`** — never string concatenation or f-strings for XML
2. **IDs 0 and 1 are reserved** — the helper handles this automatically
3. **All `mxGeometry` elements need `.set("as", "geometry")`** — the helper handles this
4. **Use plain text in `value` attributes** — avoid embedded HTML tags
5. **Validate after writing** — `db.write()` does this automatically
6. **For >50 nodes**, consider splitting into multiple diagrams

## Using the Helper Script

Write a Python script with diagram logic, then run it through the wrapper:

```bash
.venv/bin/python .claude/skills/core-drawio/scripts/generate_drawio.py my_diagram.py
```

The wrapper pre-imports `DiagramBuilder`, `STATUS_COLORS`, `ARCH_COLORS`, and `ET` (ElementTree) — no import boilerplate needed in your script.

### Create a diagram

```python
db = DiagramBuilder("My Diagram")            # default 1600x900
db = DiagramBuilder("Large", 3200, 2400)     # custom canvas size
```

### Add nodes

```python
n1 = db.add_node("Service A", 100, 100)
n2 = db.add_node("Service B", 400, 100, fill="#D5E8D4", stroke="#82B366")
n3 = db.add_node("Database", 250, 250, width=160, height=80,
                  style_extra="shape=cylinder3;")

# Use color constants
fill, stroke = STATUS_COLORS["blocked"]
n4 = db.add_node("Failed Job", 100, 300, fill=fill, stroke=stroke)
```

### Add edges

```python
db.add_edge(n1, n2)                                    # solid default
db.add_edge(n1, n3, label="queries", dashed=True)      # dashed with label
db.add_edge(n2, n3, stroke="#B85450", width=2)          # custom color/width
```

### Add groups

```python
gid = db.add_group("Backend Services", 60, 60, 700, 300)
# Child nodes overlap visually by position
db.add_node("API", 80, 100)
db.add_node("Worker", 300, 100)
```

### Write and validate

```python
db.write("output.drawio")  # writes XML, validates, returns path
```

## Manually Building XML (Advanced)

When `drawio_utils.py` doesn't cover a specific need, build XML directly with `ElementTree`:

```python
import xml.etree.ElementTree as ET

mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
diagram = ET.SubElement(mxfile, "diagram", id="diagram-1", name="My Diagram")
model = ET.SubElement(diagram, "mxGraphModel",
    dx="1422", dy="900", grid="1", gridSize="10", guides="1", tooltips="1",
    connect="1", arrows="1", fold="1", page="1", pageScale="1",
    pageWidth="1600", pageHeight="900", math="0", shadow="1")
root_elem = ET.SubElement(model, "root")
ET.SubElement(root_elem, "mxCell", id="0")
ET.SubElement(root_elem, "mxCell", id="1", parent="0")

# Write with XML declaration
tree = ET.ElementTree(mxfile)
ET.indent(tree, space="  ")
tree.write("output.drawio", encoding="UTF-8", xml_declaration=True)
ET.parse("output.drawio")  # validate
```

**Important:** The `as` attribute must use `.set()` because `as` is a Python reserved word:
```python
geo.set("as", "geometry")
```

## References

- **Colors, shapes, edge styles**: See [references/colors-and-styles.md](references/colors-and-styles.md) for color palettes, shape snippets, and edge style options
- **Layouts & large diagrams**: See [references/layouts.md](references/layouts.md) for layout decision framework, layout code patterns, and guidelines for diagrams with >50 nodes
