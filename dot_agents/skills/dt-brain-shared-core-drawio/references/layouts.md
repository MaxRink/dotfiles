# Layouts & Large Diagrams

Read this file when deciding which layout to use, implementing specific layout patterns, or generating diagrams with many nodes (>50).

## Layout Decision Framework

| Diagram Type | Best Layout | Reason |
|--------------|-------------|--------|
| **Dependency graph** | Grid with edges | Shows relationships clearly |
| **Org chart** | Hierarchical top-down | Clear reporting structure |
| **Pipeline/workflow** | Left-to-right flow | Follows reading direction |
| **Category grouping** | Two-column grouped | Maximizes vertical space |
| **Simple list** | Top-down flow | Vertical reading is natural |
| **Network topology** | Grid with edges | Shows connections between nodes |

## Layout Patterns

### Grid layout (for tables, matrices)

```python
cols = 3
for i, item in enumerate(items):
    row, col = i // cols, i % cols
    x = start_x + col * (node_w + gap_x)
    y = start_y + row * (node_h + gap_y)
    db.add_node(item["label"], x, y)
```

### Two-column grouped layout (for categorized items)

```python
col_ys = [40, 40]  # track Y position per column
for gi, (group_name, items) in enumerate(groups.items()):
    col = gi % 2
    gx = col * 700 + 40
    gy = col_ys[col]
    # Create group
    group_h = len(items) * 80 + 60
    gid = db.add_group(group_name, gx, gy, 650, group_h)
    # Add items inside group
    for i, item in enumerate(items):
        db.add_node(item["label"], gx + 20, gy + 40 + i * 80, parent=gid)
    col_ys[col] = gy + group_h + 30
```

### Hierarchical top-down layout (for trees)

```python
node_positions = {}

def layout_tree(node, x, y, level_height=120, sibling_gap=200):
    """Position node and recursively position children below."""
    node_positions[node.id] = (x, y)
    if not node.children:
        return x + node_w + sibling_gap
    child_x = x
    for child in node.children:
        child_x = layout_tree(child, child_x, y + level_height)
    # Center parent above children span
    first_x = node_positions[node.children[0].id][0]
    last_x = node_positions[node.children[-1].id][0]
    node_positions[node.id] = ((first_x + last_x) // 2, y)
    return child_x
```

### Top-down flow (for pipelines, sequences)

```python
for i, item in enumerate(items):
    x = center_x - node_w // 2
    y = start_y + i * (node_h + gap_y)
    db.add_node(item["label"], x, y)
```

### Left-to-right flow (for data pipelines)

```python
for i, item in enumerate(items):
    x = start_x + i * (node_w + gap_x)
    y = center_y - node_h // 2
    db.add_node(item["label"], x, y)
```

## Complete Example: Dependency Graph

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from drawio_utils import DiagramBuilder, STATUS_COLORS

def create_dependency_diagram(items, dependencies, output_path):
    """
    items: list of dicts with keys: id, label, status (open|closed|blocked)
    dependencies: list of (source_id, target_id) tuples
    """
    db = DiagramBuilder("Dependencies", page_width=1400)
    node_ids = {}

    # Create nodes in a 3-column grid
    for i, item in enumerate(items):
        row, col = i // 3, i % 3
        x, y = 80 + col * 320, 80 + row * 100
        fill, stroke = STATUS_COLORS.get(item["status"], STATUS_COLORS["open"])
        nid = db.add_node(item["label"], x, y, width=280, fill=fill, stroke=stroke)
        node_ids[item["id"]] = nid

    # Create dependency edges
    for src, tgt in dependencies:
        if src in node_ids and tgt in node_ids:
            db.add_edge(node_ids[src], node_ids[tgt], dashed=True)

    db.write(output_path)
```

## Large Diagram Guidelines (>50 nodes)

### Increase canvas size

```python
# For 100+ nodes, use larger page sizes
db = DiagramBuilder("Large Diagram", page_width=3200, page_height=2400)
```

### Use consistent spacing

```python
node_w, node_h = 280, 60
gap_x, gap_y = 80, 40  # increase gaps for breathing room

# Calculate total dimensions first
total_width = cols * (node_w + gap_x)
total_height = rows * (node_h + gap_y)
```

### Split large diagrams

**Rule of thumb**: If diagram has >50 nodes, split by logical grouping.

Instead of one huge diagram with 200 services, create separate files:
- `frontend-services.drawio` (30-50 nodes max)
- `backend-services.drawio`
- `data-layer.drawio`
- `infrastructure.drawio`

### Pre-calculate positions

```python
# ✅ Good: Calculate all positions first, then create XML
node_positions = {}
for i, item in enumerate(items):
    node_positions[item["id"]] = (x_calc(i), y_calc(i))

for item_id, (x, y) in node_positions.items():
    db.add_node(items[item_id]["label"], x, y)

# ❌ Bad: Complex layout logic interleaved with XML creation
```
