# Colors, Styles & Shapes Reference

Read this file when choosing colors for nodes/edges, picking shapes, or positioning edge labels.

## Color Palettes

### Status colors (for issue/task tracking)

| Status | Fill | Stroke | Usage |
|--------|------|--------|-------|
| Open/Active | `#DAE8FC` | `#6C8EBF` | Default state |
| Done/Closed | `#D5E8D4` | `#82B366` | Completed items |
| Blocked | `#F8CECC` | `#B85450` | Blocked/failed items |
| Critical/Warning | `#FFF2CC` | `#D6B656` | High priority |
| Incident/Alert | `#E1D5E7` | `#9673A6` | Incidents, alerts |
| Neutral/Group BG | `#F5F5F5` | `#666666` | Group containers |

### Architecture colors

| Component | Fill | Stroke | Usage |
|-----------|------|--------|-------|
| Frontend | `#DAE8FC` | `#6C8EBF` | UI, web apps |
| Backend/API | `#D5E8D4` | `#82B366` | Services, APIs |
| Database | `#FFE6CC` | `#D79B00` | Data stores |
| Infrastructure | `#F5F5F5` | `#666666` | Servers, networks |
| External | `#E1D5E7` | `#9673A6` | Third-party services |
| Security | `#F8CECC` | `#B85450` | Auth, firewalls |

These are available as `STATUS_COLORS` and `ARCH_COLORS` dicts in `drawio_utils.py`:

```python
from drawio_utils import STATUS_COLORS, ARCH_COLORS

fill, stroke = STATUS_COLORS["blocked"]   # ("#F8CECC", "#B85450")
fill, stroke = ARCH_COLORS["database"]    # ("#FFE6CC", "#D79B00")
```

## Shape Reference

### Common styles

- `rounded=1` — rounded corners
- `shadow=1` — drop shadow
- `fontStyle=1` — bold, `fontStyle=2` — italic, `fontStyle=3` — bold+italic
- `strokeWidth=2` — thicker border (use for emphasis)
- `dashed=1` — dashed border
- `opacity=50` — semi-transparent

### Common shapes

| Shape | Style snippet |
|-------|--------------|
| Rectangle | `rounded=0;` |
| Rounded rect | `rounded=1;` |
| Ellipse | `ellipse;` |
| Cylinder (DB) | `shape=cylinder3;` |
| Cloud | `shape=cloud;` |
| Diamond | `rhombus;` |
| Hexagon | `shape=hexagon;` |
| Document | `shape=document;` |

Use shapes via the `style_extra` parameter:

```python
db.add_node("Users DB", 100, 100, style_extra="shape=cylinder3;")
db.add_node("Decision", 100, 200, width=120, height=80, style_extra="rhombus;")
```

## Edge Styles

### Style options

- `edgeStyle=orthogonalEdgeStyle` — right-angle routing (best for most diagrams)
- `edgeStyle=elbowEdgeStyle` — single-elbow routing
- `curved=1` — smooth curves instead of sharp turns
- `entryX=0.5;entryY=0` — connect to top-center of target
- `exitX=0.5;exitY=1` — connect from bottom-center of source
- `startArrow=oval;startFill=1` — add arrowhead at start
- `endArrow=none` — remove end arrow

Use via the `style_extra` parameter:

```python
db.add_edge(n1, n2, style_extra="curved=1;endArrow=none;")
db.add_edge(n1, n3, style_extra="entryX=0.5;entryY=0;exitX=0.5;exitY=1;")
```

## Edge Label Positioning

For precise label placement on edges, create a separate label cell parented to the edge:

```python
import xml.etree.ElementTree as ET

# After creating edge with db.add_edge():
label_id = db._next_id()
c = ET.SubElement(db._root, "mxCell", id=label_id, value="HTTP",
    style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;"
          "fontSize=10;labelBackgroundColor=#FFFFFF;",
    vertex="1", connectable="0", parent=edge_id)
geo = ET.SubElement(c, "mxGeometry", relative="1")
geo.set("as", "geometry")
point = ET.SubElement(geo, "mxPoint", x="0", y="10")
point.set("as", "offset")
```
