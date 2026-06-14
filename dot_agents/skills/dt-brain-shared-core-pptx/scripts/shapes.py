"""Reusable XML shape builders for PowerPoint slides.

Provides functions to generate OOXML shape elements for use in unpacked PPTX slides.
All positions and sizes are in EMU (English Metric Units).

Usage:
    from shapes import slide_xml, title_ph, text_box, rounded_rect, bullet_list

    xml = slide_xml([
        title_ph(2, "My Title"),
        rounded_rect(10, x=479425, y=2150000, cx=7000000, cy=3000000,
                     fill="0A1E40", lines=[
            ("Header", {"b": True, "sz": "1900", "c": "A4DEEE"}),
            ("Bullet point", {"sz": "1500", "bullet": True}),
        ]),
    ])
"""

# ---------------------------------------------------------------------------
# TDI Template Constants
# ---------------------------------------------------------------------------

# Canvas dimensions (13.33" x 7.50" — 1.33x larger than standard 16:9)
TDI_WIDTH = 12192000
TDI_HEIGHT = 6858000

# Safe content zones (derived from slideLayout6 body placeholder + slide master footer)
TDI_TITLE_TOP = 405000        # Top of title placeholder
TDI_CONTENT_TOP = 1485024     # Top of body content area
TDI_CONTENT_BOTTOM = 5900000  # Safe bottom (above TDI cloud logo at y=6,024,445)
TDI_MARGIN_LEFT = 479425      # Standard left margin
TDI_MARGIN_RIGHT = 479425     # Standard right margin
TDI_CONTENT_WIDTH = TDI_WIDTH - TDI_MARGIN_LEFT - TDI_MARGIN_RIGHT  # 11,233,150

# Two-column layout constants (cards, side-by-side content)
TDI_COL2_GAP = 650000                                          # Gap between columns (~0.71")
TDI_COL2_LEFT_W = (TDI_CONTENT_WIDTH - TDI_COL2_GAP) // 2     # 5,291,575
TDI_COL2_RIGHT_X = TDI_MARGIN_LEFT + TDI_COL2_LEFT_W + TDI_COL2_GAP  # 6,420,575
TDI_COL2_RIGHT_W = TDI_COL2_LEFT_W                             # Same as left

# Title slide (slideLayout1) safe zones — right 57% is image placeholder
TDI_TITLE_SAFE_RIGHT = 4815000   # Max x for content on title slides
TDI_TITLE_BADGE_TOP = 4300000    # Safe y start below subtitle
TDI_TITLE_BADGE_BOTTOM = 5700000 # Safe y end above T logo

# Font scale factor: TDI templates need 1.33x standard font sizes
TDI_FONT_SCALE = 1.33

# Typical line heights per font size (EMU, approximate)
LINE_HEIGHTS = {
    "900":  170000,
    "1000": 190000,
    "1100": 210000,
    "1200": 230000,
    "1300": 250000,
    "1400": 270000,
    "1500": 290000,
    "1600": 310000,
    "1700": 330000,
    "1800": 350000,
    "1900": 370000,
    "2000": 390000,
}


# ---------------------------------------------------------------------------
# Adaptive Sizing Helpers
# ---------------------------------------------------------------------------

def estimate_content_height(lines, default_sz="1300", header_spacing=600, item_spacing=300):
    """Estimate total height of a text block in EMU.

    Args:
        lines: list of strings or (text, props) tuples
        default_sz: default font size if not specified in props
        header_spacing: extra space after header lines (spcAft in hundredths of pt)
        item_spacing: extra space after regular lines

    Returns:
        Estimated height in EMU
    """
    total = 0
    for line in lines:
        if isinstance(line, tuple):
            _, props = line
            sz = props.get("sz", default_sz)
            spacing = header_spacing if props.get("b") else item_spacing
        else:
            sz = default_sz
            spacing = item_spacing

        line_h = LINE_HEIGHTS.get(sz, 250000)
        spc_emu = int(spacing) * 12700 // 100  # hundredths of pt to EMU
        total += line_h + spc_emu

    return total


def fit_font_size(line_count, available_height, base_sz="1300", padding=300000):
    """Choose the largest font size that fits line_count lines in available_height.

    Args:
        line_count: number of content lines (excluding header)
        available_height: available EMU height for content
        base_sz: minimum font size to try
        padding: top + bottom padding in EMU

    Returns:
        Font size string (e.g., "1500")
    """
    usable = available_height - padding
    sizes = ["1900", "1700", "1500", "1400", "1300", "1200", "1100", "1000"]
    base_idx = sizes.index(base_sz) if base_sz in sizes else len(sizes) - 1

    for sz in sizes:
        if sizes.index(sz) > base_idx:
            continue
        line_h = LINE_HEIGHTS.get(sz, 250000)
        # Header takes ~1.5x line height, then N lines
        needed = int(line_h * 1.5) + (line_count * (line_h + 40000))
        if needed <= usable:
            return sz

    return base_sz  # fallback


# ---------------------------------------------------------------------------
# Paragraph Builders
# ---------------------------------------------------------------------------

def _para_xml(text, props=None):
    """Build a single <a:p> element.

    Args:
        text: the text string
        props: dict with optional keys:
            b (bool) - bold
            i (bool) - italic
            sz (str) - font size like "1300"
            c (str) - hex color like "FFFFFF"
            a (str) - alignment: "l", "ctr", "r"
            bullet (bool) - add bullet character
            bullet_char (str) - bullet char (default "•")
            font (str) - font family
            spc_after (int) - space after in hundredths of pt
    """
    props = props or {}
    align = props.get("a", "l")
    bold = ' b="1"' if props.get("b") else ""
    italic = ' i="1"' if props.get("i") else ""
    sz = f' sz="{props["sz"]}"' if "sz" in props else ""
    color = props.get("c", "FFFFFF")
    font = props.get("font", "TeleNeo Office")
    spc = props.get("spc_after", 300)

    # Paragraph properties
    if props.get("bullet"):
        char = props.get("bullet_char", "\u2022")
        ppr = (f'<a:pPr algn="{align}" marL="342900" indent="-342900">'
               f'<a:spcAft><a:spcPts val="{spc}"/></a:spcAft>'
               f'<a:buSzPct val="100000"/><a:buChar char="{char}"/>'
               f'</a:pPr>')
    else:
        spc_xml = f'<a:spcAft><a:spcPts val="{spc}"/></a:spcAft>' if spc else ""
        ppr = f'<a:pPr algn="{align}">{spc_xml}</a:pPr>'

    return (f'<a:p>{ppr}'
            f'<a:r><a:rPr lang="en-US"{sz}{bold}{italic} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/>'
            f'</a:rPr><a:t>{text}</a:t></a:r></a:p>')


def _build_paragraphs(lines):
    """Build paragraph XML from a list of lines.

    Each line is either:
        - A plain string (white text, default size)
        - A tuple (text, props_dict)
    """
    paras = []
    for line in lines:
        if isinstance(line, tuple):
            text, props = line
            paras.append(_para_xml(text, props))
        else:
            paras.append(_para_xml(line))
    return "\n".join(paras)


# ---------------------------------------------------------------------------
# Shape Builders
# ---------------------------------------------------------------------------

def slide_xml(shapes):
    """Wrap shape XML strings in a complete slide document.

    Args:
        shapes: list of XML strings (from shape builder functions)

    Returns:
        Complete slide XML string
    """
    joined = "\n".join(shapes)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
      <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {joined}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def title_ph(id, text, ph_type="title"):
    """Title placeholder — inherits position/style from layout.

    Args:
        id: unique shape ID
        text: title text
        ph_type: placeholder type ("title", "ctrTitle")
    """
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Title"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph type="{ph_type}"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:r><a:rPr lang="en-US" dirty="0"/>'
            f'<a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')


def subtitle_ph(id, text, idx="1", ph_type="subTitle"):
    """Subtitle placeholder — inherits position/style from layout."""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Subtitle"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph type="{ph_type}" idx="{idx}"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:r><a:rPr lang="en-US" dirty="0"/>'
            f'<a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')


def content_ph(id, lines, idx="1"):
    """Body content placeholder — inherits position/style from layout.

    Args:
        id: unique shape ID
        lines: list of strings or (text, props) tuples
        idx: placeholder index
    """
    paras = _build_paragraphs(lines)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Content"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph idx="{idx}"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            f'{paras}</p:txBody></p:sp>')


def text_box(id, x, y, cx, cy, lines, anchor="t"):
    """Free-form text box with no background.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        lines: list of strings or (text, props) tuples
        anchor: vertical anchor ("t", "ctr", "b")
    """
    paras = _build_paragraphs(lines)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="TextBox{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"/>'
            f'<a:lstStyle/>{paras}</p:txBody></p:sp>')


def rect(id, x, y, cx, cy, fill, border=None):
    """Simple colored rectangle (no text). Good for accent bars, dividers.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        fill: hex color string (e.g., "E20074")
        border: hex color for border, or None for no border
    """
    ln = f'<a:ln w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>' if border else '<a:ln><a:noFill/></a:ln>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Rect{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{ln}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>')


def rounded_rect(id, x, y, cx, cy, fill, lines, border="1B3A5C",
                 radius="3000", anchor="t",
                 padding=None):
    """Colored rounded rectangle with text content.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        fill: background hex color
        lines: list of strings or (text, props) tuples
        border: border hex color
        radius: corner radius (OOXML adj value, "3000" = small, "15000" = large)
        anchor: vertical text anchor ("t", "ctr", "b")
        padding: dict with lIns, tIns, rIns, bIns in EMU (defaults provided)
    """
    p = padding or {}
    l_ins = p.get("lIns", 180000)
    t_ins = p.get("tIns", 144000)
    r_ins = p.get("rIns", 144000)
    b_ins = p.get("bIns", 108000)

    paras = _build_paragraphs(lines)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="RRect{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst>'
            f'<a:gd name="adj" fmla="val {radius}"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            f'<a:ln w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>'
            f'</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{l_ins}" tIns="{t_ins}" '
            f'rIns="{r_ins}" bIns="{b_ins}" anchor="{anchor}"/>'
            f'<a:lstStyle/>{paras}</p:txBody></p:sp>')


def table(id, x, y, cx, cy, col_widths, headers, rows,
          header_bg="0D9488", row_bg_1="0A1E40", row_bg_2="122E55",
          border="1B3A5C", text_color="FFFFFF", header_sz="1200",
          cell_sz="1100", font="TeleNeo Office"):
    """Build a graphicFrame with <a:tbl>.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        col_widths: list of column widths in EMU (should sum ≈ cx)
        headers: list of header strings
        rows: list of lists of cell strings
        header_bg: header row fill color
        row_bg_1, row_bg_2: alternating data row colors
        border: cell border color
        text_color: text hex color
        header_sz: header font size
        cell_sz: data cell font size
        font: font family
    """
    grid = "".join(f'<a:gridCol w="{w}"/>' for w in col_widths)

    def _cell(text, bold=False, bg="000000", sz=None):
        sz = sz or cell_sz
        b = ' b="1"' if bold else ''
        return (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>'
                f'<a:p><a:pPr indent="0" marL="0"><a:buNone/></a:pPr>'
                f'<a:r><a:rPr lang="en-US" sz="{sz}"{b} dirty="0">'
                f'<a:solidFill><a:srgbClr val="{text_color}"/></a:solidFill>'
                f'<a:latin typeface="{font}"/>'
                f'</a:rPr><a:t>{text}</a:t></a:r></a:p></a:txBody>'
                f'<a:tcPr marL="72000" marR="72000" marT="36000" marB="36000">'
                f'<a:lnL w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnL>'
                f'<a:lnR w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnR>'
                f'<a:lnT w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnT>'
                f'<a:lnB w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnB>'
                f'<a:solidFill><a:srgbClr val="{bg}"/></a:solidFill>'
                f'</a:tcPr></a:tc>')

    hdr = "".join(_cell(h, bold=True, bg=header_bg, sz=header_sz) for h in headers)
    data = ""
    for i, row in enumerate(rows):
        bg = row_bg_1 if i % 2 == 0 else row_bg_2
        data += '<a:tr h="0">' + "".join(_cell(v, bg=bg) for v in row) + '</a:tr>\n'

    return (f'<p:graphicFrame><p:nvGraphicFramePr>'
            f'<p:cNvPr id="{id}" name="Table {id}"/>'
            f'<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr>'
            f'<p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f'<a:tbl><a:tblPr/><a:tblGrid>{grid}</a:tblGrid>'
            f'<a:tr h="0">{hdr}</a:tr>\n{data}</a:tbl>'
            f'</a:graphicData></a:graphic></p:graphicFrame>')


def badge(id, x, y, cx, cy, fill, text, text_color="FFFFFF", sz="1100"):
    """Small rounded badge/tag with centered text.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        fill: background hex color
        text: badge text
        text_color: text hex color
        sz: font size
    """
    return rounded_rect(id, x, y, cx, cy, fill,
                        lines=[(text, {"b": True, "sz": sz, "c": text_color, "a": "ctr",
                                       "font": "TeleNeo Office"})],
                        border=fill, radius="15000", anchor="ctr",
                        padding={"lIns": 36000, "tIns": 36000, "rIns": 36000, "bIns": 36000})
