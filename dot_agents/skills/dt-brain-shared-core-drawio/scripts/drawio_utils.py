"""Draw.io diagram generation utilities.

Provides helper functions to create valid .drawio XML files using
xml.etree.ElementTree. Never use string concatenation for XML generation.

Usage:
    from drawio_utils import DiagramBuilder, STATUS_COLORS, ARCH_COLORS

    db = DiagramBuilder("My Diagram")
    n1 = db.add_node("Service A", 100, 100)
    n2 = db.add_node("Service B", 400, 100, fill="#D5E8D4", stroke="#82B366")
    db.add_edge(n1, n2)
    db.add_group("Backend", 80, 60, 600, 200)
    db.write("output.drawio")
"""

import xml.etree.ElementTree as ET

# --- Color Constants ---

STATUS_COLORS = {
    "open":     ("#DAE8FC", "#6C8EBF"),
    "closed":   ("#D5E8D4", "#82B366"),
    "blocked":  ("#F8CECC", "#B85450"),
    "warning":  ("#FFF2CC", "#D6B656"),
    "incident": ("#E1D5E7", "#9673A6"),
    "neutral":  ("#F5F5F5", "#666666"),
}

ARCH_COLORS = {
    "frontend":       ("#DAE8FC", "#6C8EBF"),
    "backend":        ("#D5E8D4", "#82B366"),
    "database":       ("#FFE6CC", "#D79B00"),
    "infrastructure": ("#F5F5F5", "#666666"),
    "external":       ("#E1D5E7", "#9673A6"),
    "security":       ("#F8CECC", "#B85450"),
}


class DiagramBuilder:
    """Builder for .drawio diagram files.

    Args:
        name: Diagram tab name shown in draw.io.
        page_width: Canvas width in pixels (default 1600).
        page_height: Canvas height in pixels (default 900).
    """

    def __init__(self, name="Diagram", page_width=1600, page_height=900):
        self._cell_id = 1
        self._mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
        diagram = ET.SubElement(self._mxfile, "diagram", id="diagram-1", name=name)
        model = ET.SubElement(
            diagram, "mxGraphModel",
            dx="1422", dy="900", grid="1", gridSize="10", guides="1",
            tooltips="1", connect="1", arrows="1", fold="1", page="1",
            pageScale="1", pageWidth=str(page_width), pageHeight=str(page_height),
            math="0", shadow="1",
        )
        self._root = ET.SubElement(model, "root")
        ET.SubElement(self._root, "mxCell", id="0")
        ET.SubElement(self._root, "mxCell", id="1", parent="0")

    def _next_id(self):
        self._cell_id += 1
        return str(self._cell_id)

    def add_node(self, label, x, y, width=200, height=60,
                 fill="#DAE8FC", stroke="#6C8EBF", parent="1",
                 font_size=11, style_extra=""):
        """Add a rectangle node and return its ID.

        Args:
            label: Text displayed in the node.
            x, y: Position in pixels.
            width, height: Node dimensions.
            fill, stroke: Fill and border colors (hex).
            parent: Parent cell ID (use group ID for child nodes).
            font_size: Label font size.
            style_extra: Additional style properties to append.
        """
        nid = self._next_id()
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
            f"strokeColor={stroke};fontSize={font_size};shadow=1;"
            f"{style_extra}"
        )
        cell = ET.SubElement(
            self._root, "mxCell", id=nid, value=label,
            style=style, vertex="1", parent=parent,
        )
        geo = ET.SubElement(
            cell, "mxGeometry",
            x=str(x), y=str(y), width=str(width), height=str(height),
        )
        geo.set("as", "geometry")
        return nid

    def add_edge(self, source_id, target_id, label="",
                 stroke="#666666", width=1, dashed=False,
                 parent="1", style_extra=""):
        """Add a directed edge between two nodes and return its ID.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            label: Optional label on the edge.
            stroke: Edge color (hex).
            width: Stroke width.
            dashed: If True, draw dashed line.
            parent: Parent cell ID.
            style_extra: Additional style properties.
        """
        eid = self._next_id()
        dash_str = "dashed=1;" if dashed else ""
        label_bg = "labelBackgroundColor=#FFFFFF;" if label else ""
        style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor={stroke};"
            f"strokeWidth={width};{dash_str}endArrow=blockThin;endFill=1;"
            f"{label_bg}{style_extra}"
        )
        cell = ET.SubElement(
            self._root, "mxCell", id=eid, value=label,
            style=style, edge="1", parent=parent,
            source=source_id, target=target_id,
        )
        geo = ET.SubElement(cell, "mxGeometry", relative="1")
        geo.set("as", "geometry")
        return eid

    def add_group(self, label, x, y, width, height,
                  fill="#F5F5F5", stroke="#666666",
                  font_size=13, style_extra=""):
        """Add a group/container rectangle and return its ID.

        Child nodes should set parent=group_id OR overlap visually by position.

        Args:
            label: Group title (displayed at top).
            x, y: Position in pixels.
            width, height: Group dimensions.
            fill, stroke: Background and border colors.
            font_size: Title font size.
            style_extra: Additional style properties.
        """
        gid = self._next_id()
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
            f"strokeColor={stroke};dashed=1;verticalAlign=top;"
            f"fontStyle=1;fontSize={font_size};align=center;"
            f"spacingTop=5;arcSize=8;{style_extra}"
        )
        cell = ET.SubElement(
            self._root, "mxCell", id=gid, value=label,
            style=style, vertex="1", parent="1",
        )
        geo = ET.SubElement(
            cell, "mxGeometry",
            x=str(x), y=str(y), width=str(width), height=str(height),
        )
        geo.set("as", "geometry")
        return gid

    def write(self, output_path):
        """Write the diagram to a .drawio file and validate XML.

        Args:
            output_path: File path for the .drawio output.

        Raises:
            ET.ParseError: If the generated XML is malformed.
        """
        tree = ET.ElementTree(self._mxfile)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding="UTF-8", xml_declaration=True)
        ET.parse(output_path)  # validate
        return output_path
