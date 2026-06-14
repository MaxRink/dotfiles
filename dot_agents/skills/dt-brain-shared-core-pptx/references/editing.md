# Editing Presentations

## Contents

- [TDI Slide Master Template](#tdi-slide-master-template)
- [Template-Based Workflow](#template-based-workflow)
- [Scripts](#scripts) — unpack, add_slide, batch_slides, shapes, clean, pack, thumbnail
- [Slide Operations](#slide-operations) — reorder, delete, add
- [Editing Content](#editing-content) — formatting rules, subagent delegation
- [Common Pitfalls](#common-pitfalls) — template adaptation, multi-item content, smart quotes, card sizing, content density, spacing
- [Slide File ↔ Presentation Order](#slide-file--presentation-order)
- [Building Tables in XML](#building-tables-in-xml)
- [XML Shape Helpers](#xml-shape-helpers) — slide wrapper, placeholders, text box, rounded rect, badges, bullets
- [TDI Layout Background Reference](#tdi-layout-background-reference)

---

## TDI Slide Master Template

When the user chooses the TDI template, use the TDI Slide Master:

```bash
# Light (default)
python scripts/office/unpack.py templates/tdi-slide-master.potx unpacked/

# Dark (only when user requests)
python scripts/office/unpack.py templates/tdi-slide-master-dark.potx unpacked/
```

Then follow the template-based workflow below. When packing, output as `.pptx` and pass the `.potx` as `--original`:

```bash
python scripts/office/pack.py unpacked/ output.pptx --original templates/tdi-slide-master.potx
```

### Title Slides with Default Image

TDI title layouts (slideLayout1–4 light, slideLayout1–2 dark) have a picture placeholder on the right side. **Always use `--title-image` when creating title slides** to populate it with the bundled cloud image:

```bash
# Single title slide
python scripts/add_slide.py unpacked/ slideLayout1.xml \
    --title-image templates/title-image.jpeg

# Batch: title + content slides
python scripts/batch_slides.py unpacked/ slideLayout1.xml slideLayout9.xml \
    --title-image templates/title-image.jpeg --update-presentation
```

The flag auto-detects title layouts (those with both `ctrTitle` and `pic` placeholders) and is silently ignored for other layouts.

**Unified magenta title**: When `--title-image` is used, the script forces a magenta (`E20074`) background and uses the light template's diagonal clip geometry on the slide. This ensures **both light and dark templates produce identical-looking title slides** — magenta left side with cloud image on the right. Content slides retain their template-specific styling.

To use a **custom image** instead of the default, pass its path:
```bash
python scripts/add_slide.py unpacked/ slideLayout1.xml \
    --title-image /path/to/custom-photo.jpeg
```

---

## Template-Based Workflow

When using an existing presentation as a template:

1. **Analyze existing slides**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   Review `thumbnails.jpg` to see layouts, and markitdown output to see placeholder text.

2. **Plan slide mapping**: For each content section, choose a template slide.

   ⚠️ **USE VARIED LAYOUTS** — monotonous presentations are a common failure mode. Don't default to basic title + bullet slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

   **Avoid:** Repeating the same text-heavy layout for every slide.

   Match content type to layout style (e.g., key points → bullet slide, team info → multi-column, testimonials → quote slide).

3. **Unpack**: `python scripts/office/unpack.py template.pptx unpacked/`

4. **Build presentation** (do this yourself, not with subagents):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (`add_slide.py`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 5**

5. **Edit content**: Update text in each `slide{N}.xml`.
   **Use subagents here if available** — slides are separate XML files, so subagents can edit in parallel.

6. **Clean**: `python scripts/clean.py unpacked/`

7. **Pack**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

8. **Cleanup**: Remove the `unpacked/` directory after packing — it's a build artifact and should not be committed.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `unpack.py` | Extract and pretty-print PPTX |
| `add_slide.py` | Duplicate slide or create from layout |
| `batch_slides.py` | Create multiple slides from layouts in one pass |
| `shapes.py` | Importable XML shape builders + TDI constants |
| `clean.py` | Remove orphaned files |
| `pack.py` | Repack with validation |
| `thumbnail.py` | Create visual grid of slides |

### unpack.py

```bash
python scripts/office/unpack.py input.pptx unpacked/
```

Extracts PPTX, pretty-prints XML, escapes smart quotes.

### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
python scripts/add_slide.py unpacked/ slideLayout1.xml --title-image templates/title-image.jpeg
# Title slide with default cloud image in pic placeholder
```

Prints `<p:sldId>` to add to `<p:sldIdLst>` at desired position.

The `--title-image` flag populates the picture placeholder on title layouts (those with both `ctrTitle` and `pic` placeholders). It is silently ignored for non-title layouts.

### batch_slides.py

```bash
# Create 3 slides from layouts in one pass
python scripts/batch_slides.py unpacked/ slideLayout7.xml slideLayout7.xml slideLayout3.xml
# Prints sldId entries for each created slide

# Auto-update presentation.xml sldIdLst
python scripts/batch_slides.py unpacked/ slideLayout7.xml slideLayout3.xml --update-presentation

# Title slide with default image + content slides
python scripts/batch_slides.py unpacked/ slideLayout1.xml slideLayout9.xml slideLayout9.xml \
    --title-image templates/title-image.jpeg --update-presentation
```

Creates multiple slides at once, updating `Content_Types` and rels. Much faster than calling `add_slide.py` in a loop.

The `--title-image` flag works the same as in `add_slide.py` — only title layouts get the image.

### shapes.py

Importable Python library for building slide XML. Use in custom build scripts:

```python
import sys; sys.path.insert(0, ".claude/skills/core-pptx/scripts")
from shapes import slide_xml, title_ph, rounded_rect, text_box, badge, TDI_CONTENT_BOTTOM

# Build a slide with shapes
xml = slide_xml([
    title_ph(2, "My Title"),
    rounded_rect(10, x=500000, y=2000000, cx=5000000, cy=3000000,
                 fill="0A1E40", border="1B3A5C", lines=[
        ("Header", {"b": True, "sz": "1900", "c": "A4DEEE"}),
        ("Bullet 1", {"sz": "1500", "bullet": True}),
    ]),
])
```

Key constants: `TDI_WIDTH`, `TDI_HEIGHT`, `TDI_CONTENT_TOP`, `TDI_CONTENT_BOTTOM` (safe zone above footer), `TDI_MARGIN_LEFT`.

Two-column constants: `TDI_COL2_LEFT_W`, `TDI_COL2_GAP`, `TDI_COL2_RIGHT_X`, `TDI_COL2_RIGHT_W` — pre-calculated for balanced 2-column card layouts with 0.71" gap.

Helpers: `estimate_content_height()`, `fit_font_size()` for adaptive sizing.

Table builder: `table()` — generates `<a:tbl>` inside a `<p:graphicFrame>` with alternating row colors and dark-theme defaults.

### clean.py

```bash
python scripts/clean.py unpacked/
```

Removes slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

### pack.py

```bash
python scripts/office/pack.py unpacked/ output.pptx --original input.pptx
```

Validates, repairs, condenses XML, re-encodes smart quotes.

### thumbnail.py

```bash
python scripts/thumbnail.py input.pptx [output_prefix] [--cols N]
```

Creates `thumbnails.jpg` with slide filenames as labels. Default 3 columns, max 12 per grid.

**Use for template analysis only** (choosing layouts). For visual QA, use `soffice` + `pdftoppm` to create full-resolution individual slide images—see SKILL.md.

---

## Slide Operations

Slide order is in `ppt/presentation.xml` → `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then run `clean.py`.

**Add**: Use `add_slide.py`. Never manually copy slide files—the script handles notes references, Content_Types.xml, and relationship IDs that manual copying misses.

---

## Editing Content

**Subagents:** If available, use them here (after completing step 4). Each slide is a separate XML file, so subagents can edit in parallel. In your prompt to subagents, include:
- The slide file path(s) to edit
- **"Use the Edit tool for all changes"**
- The formatting rules and common pitfalls below

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content—text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where, yielding better reliability.

### Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes:
  - Slide titles
  - Section headers within a slide
  - Inline labels like (e.g.: "Status:", "Description:") at the start of a line
- **Never use unicode bullets (•)**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

---

## Common Pitfalls

### Template Adaptation

When source content has fewer items than the template:
- **Remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- Check for orphaned visuals after clearing text content
- Run visual QA to catch mismatched counts

When replacing text with different length content:
- **Shorter replacements**: Usually safe
- **Longer replacements**: May overflow or wrap unexpectedly
- Test with visual QA after text changes
- Consider truncating or splitting content to fit the template's design constraints

**Template slots ≠ Source items**: If template has 4 team members but source has 3 users, delete the 4th member's entire group (image + text boxes), not just the text.

### Multi-Item Content

If source has multiple items (numbered lists, multiple sections), create separate `<a:p>` elements for each — **never concatenate into one string**.

**❌ WRONG** — all items in one paragraph:
```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**✅ CORRECT** — separate paragraphs with bold headers:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing. Use `b="1"` on headers.

### Smart Quotes

Handled automatically by unpack/pack. But the Edit tool converts smart quotes to ASCII.

**When adding new text with quotes, use XML entities:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name | Unicode | XML Entity |
|-----------|------|---------|------------|
| `“` | Left double quote | U+201C | `&#x201C;` |
| `”` | Right double quote | U+201D | `&#x201D;` |
| `‘` | Left single quote | U+2018 | `&#x2018;` |
| `’` | Right single quote | U+2019 | `&#x2019;` |

### Other

- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **NEVER use `xml.etree.ElementTree` to modify slide XML** — ET rewrites namespace prefixes (e.g., `p:sld` → `ns0:sld`), which corrupts the file and makes it unopenable. Use string replacement, `defusedxml.minidom`, or the Edit tool instead. ET is safe for *reading* attributes but never for *writing* back.

### Card Sizing

When building card grids (rounded rects with title + bullets), size cards to content — don't use fixed large heights that leave empty space.

| Bullets per card | Recommended height (EMU) | Notes |
|------------------|--------------------------|-------|
| 1–2 | ~1,400,000 | Compact info cards |
| 3–4 | ~1,700,000 | Most common case |
| 5–6 | ~2,000,000 | Dense content |
| 7+ | Use `estimate_content_height()` | Or split into multiple cards |

For two-column layouts, use the constants from `shapes.py`: `TDI_COL2_LEFT_W`, `TDI_COL2_GAP`, `TDI_COL2_RIGHT_X`, `TDI_COL2_RIGHT_W`. These give balanced columns with a 0.71" gap — tight enough to look connected, wide enough to be clearly separate.

### Content Density and Slide Merging

**Avoid sparse slides.** A slide with only 3 short bullet points or a single quote looks empty and wastes the audience's attention. Before finalizing structure:

- **Merge thin slides**: If two consecutive slides each have 3–4 short items, combine them into one (e.g., a 2×2 card grid or two-column layout).
- **Remove low-value slides**: Risk analysis tables or detailed matrices from a written document don't always need their own slide — consider folding key points into an adjacent slide as a callout box.
- **Standalone quote slides are risky**: A quote without context often confuses the audience. Prefer embedding quotes as highlighted callout boxes inside a content slide (e.g., inside a Technical Justification or Proposal slide).

**Rule of thumb:** Every slide should feel "full enough" — not cramped, but not sparse. If a slide has more than 40% empty space below the content, either enlarge the content (bigger fonts, more spacing) or merge it with an adjacent slide.

### Spacing with `spc_after`

The `spc_after` property (in hundredths of a point) controls vertical spacing between paragraphs. Use it to create visual rhythm:

| Context | `spc_after` value | Effect |
|---------|-------------------|--------|
| Default | `300` | Tight, compact lists |
| Comfortable bullets | `500–700` | Good breathing room between items |
| Generous bullets | `700–800` | Spacious, works with larger cards |
| After section headers | `600–800` | Clear separation between header and content |
| Between topic groups | `800–1000` | Visually separates distinct topics within one card |
| Between label + description | `200` | Keeps label and its description visually paired |

**Pattern for topic groups** (label + description with separation between topics):
```python
lines = [
    ("Topic Header:", {"b": True, "sz": "1400", "spc_after": 200}),     # label
    ("Description text here", {"sz": "1300", "spc_after": 800}),         # description + gap
    ("Next Topic:", {"b": True, "sz": "1400", "spc_after": 200}),        # next label
    ("Next description", {"sz": "1300"}),                                 # last item, no trailing space
]
```

---

## Slide File ↔ Presentation Order

**Slide file numbers don't match presentation order** when using templates. The template's sample slides occupy early file numbers, and `add_slide.py` creates new files with the next available number. Slide ordering is controlled by `<p:sldIdLst>` in `ppt/presentation.xml`, not by file names.

To map presentation order to file names:

```python
import xml.etree.ElementTree as ET

# 1. Read sldIdLst for rId order
tree = ET.parse('ppt/presentation.xml')
ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
rids = [s.get(f'{{{ns["r"]}}}id') for s in tree.findall('.//p:sldIdLst/p:sldId', ns)]

# 2. Map rIds to filenames from rels
rels = ET.parse('ppt/_rels/presentation.xml.rels')
rid_map = {r.get('Id'): r.get('Target') for r in rels.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship') if '/slide' in r.get('Target', '') and 'slideM' not in r.get('Target', '') and 'slideL' not in r.get('Target', '')}

# 3. Print mapping
for i, rid in enumerate(rids):
    print(f"Presentation slide {i+1} → {rid_map.get(rid, '?')}")
```

**Always check this mapping** when editing slides by number. "Fix slide 3" means finding the *third entry* in `sldIdLst`, which might be `slide6.xml` or `slide17.xml`.

---

## Building Tables in XML

**Always use real `<a:tbl>` table elements** — never fake tables with monospaced text in shapes. Real tables produce properly aligned columns, cell borders, and header styling that markitdown can extract as markdown tables.

### Table Structure

A table lives inside a `<p:graphicFrame>`:

```xml
<p:graphicFrame>
  <p:nvGraphicFramePr>
    <p:cNvPr id="50" name="Table 50"/>
    <p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr>
    <p:nvPr/>
  </p:nvGraphicFramePr>
  <p:xfrm>
    <a:off x="479000" y="1500000"/>     <!-- position -->
    <a:ext cx="11000000" cy="600000"/>  <!-- size -->
  </p:xfrm>
  <a:graphic>
    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">
      <a:tbl>
        <a:tblPr/>
        <a:tblGrid>
          <a:gridCol w="2800000"/>  <!-- column widths in EMU -->
          <a:gridCol w="3200000"/>
          <a:gridCol w="5000000"/>
        </a:tblGrid>
        <!-- header row -->
        <a:tr h="0">
          <!-- cells here -->
        </a:tr>
        <!-- data rows -->
        <a:tr h="0">
          <!-- cells here -->
        </a:tr>
      </a:tbl>
    </a:graphicData>
  </a:graphic>
</p:graphicFrame>
```

### Cell Structure

Each cell (`<a:tc>`) has text body + properties:

```xml
<a:tc>
  <a:txBody><a:bodyPr/><a:lstStyle/>
    <a:p><a:pPr indent="0" marL="0"><a:buNone/></a:pPr>
      <a:r><a:rPr lang="en-US" sz="1000" b="1" dirty="0">
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
      </a:rPr><a:t>Header Text</a:t></a:r>
    </a:p>
  </a:txBody>
  <a:tcPr marL="72000" marR="72000" marT="36000" marB="36000">
    <a:lnL w="6350"><a:solidFill><a:srgbClr val="1B3A5C"/></a:solidFill></a:lnL>
    <a:lnR w="6350"><a:solidFill><a:srgbClr val="1B3A5C"/></a:solidFill></a:lnR>
    <a:lnT w="6350"><a:solidFill><a:srgbClr val="1B3A5C"/></a:solidFill></a:lnT>
    <a:lnB w="6350"><a:solidFill><a:srgbClr val="1B3A5C"/></a:solidFill></a:lnB>
    <a:solidFill><a:srgbClr val="0D9488"/></a:solidFill>  <!-- cell background -->
  </a:tcPr>
</a:tc>
```

### Python Helper Function

Use this pattern to generate tables programmatically:

```python
def make_table(id, x, y, cx, cy, col_widths, headers, rows,
               header_bg="0D9488", row_bg_1="0A1E40", row_bg_2="122E55",
               border="1B3A5C", text_color="FFFFFF"):
    """Build a graphicFrame with <a:tbl>.

    Args:
        id: unique shape ID
        x, y, cx, cy: position and size in EMU
        col_widths: list of column widths in EMU (must sum ≈ cx)
        headers: list of header strings
        rows: list of lists of cell strings
        header_bg: header row fill color
        row_bg_1, row_bg_2: alternating data row colors
        border: cell border color
        text_color: text color
    """
    grid = "".join(f'<a:gridCol w="{w}"/>' for w in col_widths)

    def cell_xml(text, bold=False, bg_color="000000"):
        b_attr = ' b="1"' if bold else ''
        return f'''<a:tc>
  <a:txBody><a:bodyPr/><a:lstStyle/>
    <a:p><a:pPr indent="0" marL="0"><a:buNone/></a:pPr>
      <a:r><a:rPr lang="en-US" sz="1000"{b_attr} dirty="0">
        <a:solidFill><a:srgbClr val="{text_color}"/></a:solidFill>
      </a:rPr><a:t>{text}</a:t></a:r>
    </a:p>
  </a:txBody>
  <a:tcPr marL="72000" marR="72000" marT="36000" marB="36000">
    <a:lnL w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnL>
    <a:lnR w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnR>
    <a:lnT w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnT>
    <a:lnB w="6350"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:lnB>
    <a:solidFill><a:srgbClr val="{bg_color}"/></a:solidFill>
  </a:tcPr>
</a:tc>'''

    header_cells = "".join(cell_xml(h, bold=True, bg_color=header_bg) for h in headers)
    data_rows = ""
    for i, row in enumerate(rows):
        bg = row_bg_1 if i % 2 == 0 else row_bg_2
        row_cells = "".join(cell_xml(val, bg_color=bg) for val in row)
        data_rows += f'<a:tr h="0">{row_cells}</a:tr>\n'

    return f'''<p:graphicFrame>
  <p:nvGraphicFramePr>
    <p:cNvPr id="{id}" name="Table {id}"/>
    <p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr>
    <p:nvPr/>
  </p:nvGraphicFramePr>
  <p:xfrm>
    <a:off x="{x}" y="{y}"/>
    <a:ext cx="{cx}" cy="{cy}"/>
  </p:xfrm>
  <a:graphic>
    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">
      <a:tbl>
        <a:tblPr/>
        <a:tblGrid>{grid}</a:tblGrid>
        <a:tr h="0">{header_cells}</a:tr>
        {data_rows}
      </a:tbl>
    </a:graphicData>
  </a:graphic>
</p:graphicFrame>'''
```

### Key Rules

- **Column widths** must be in EMU (1 inch = 914400 EMU). Sum of `gridCol` widths should roughly equal `cx`.
- **Row height** `h="0"` lets the row auto-size to content.
- **Cell margins** (`marL`, `marR`, `marT`, `marB`) are in EMU. 72000 horizontal / 36000 vertical gives comfortable padding.
- **Border width** `w="6350"` ≈ 0.5pt. Use `<a:noFill/>` instead of `<a:solidFill>` for invisible borders.
- **Header rows** should use bold text + a distinct fill color (e.g., teal `0D9488`).
- **Alternating row colors** improve readability — use two shades with sufficient contrast (e.g., `0A1E40` / `122E55` for dark themes). Avoid pairs like `0A1E40` / `0F2850` which are too similar.

> **Tip:** The `table()` function in `shapes.py` handles all of this with sensible defaults. Use it instead of building table XML manually.

---

## XML Shape Helpers

When building slides programmatically with Python, use these helper patterns for common shape types. These write directly to slide XML files in the unpacked directory.

### Slide Wrapper

```python
def slide_xml(shapes):
    """Wrap shapes in a complete slide XML document."""
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
        <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{shapes}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''
```

### Title Placeholder

```python
def title_ph(id, text):
    """Title placeholder — inherits position/style from layout."""
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="{id}" name="Title"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr><p:ph type="title"/></p:nvPr>
  </p:nvSpPr>
  <p:spPr/>
  <p:txBody><a:bodyPr/><a:lstStyle/>
    <a:p><a:r><a:rPr lang="en-US" dirty="0"/><a:t>{text}</a:t></a:r></a:p>
  </p:txBody>
</p:sp>'''
```

### Text Box

```python
def tb(id, x, y, cx, cy, lines):
    """Free-form text box. Lines can be strings or (text, props) tuples.

    Props dict keys: b (bool), sz (str like "1200"), c (hex color), a (align: "l"/"ctr"/"r")
    """
    # ... build <a:p> elements from lines ...
```

### Rounded Rectangle

```python
def rr(id, x, y, cx, cy, fill, lines, rad="8000"):
    """Colored rounded rect with centered text. Good for tags, badges, flow nodes."""
    # ... roundRect preset geometry with solidFill ...
```

### Content Box

```python
def rect_box(id, x, y, cx, cy, fill, lines):
    """Rectangular content box with left-aligned text. Good for code blocks, details."""
    # ... roundRect with small radius (5000), top-anchored text ...
```

### Line format for text helpers

All text helpers accept `lines` as a list where each item is either:
- A plain string → white text, default size
- A tuple `(text, props)` → custom formatting via props dict

```python
lines = [
    ("Section Title", {"b": True, "sz": "1400", "c": "A4DEEE"}),  # bold, 14pt, light blue
    ("Description text here", {"sz": "1000", "c": "FFFFFF"}),      # 10pt, white
    ("Muted note", {"sz": "900", "c": "A3A3A3"}),                  # 9pt, gray
]
```

### Adding Bullet Lists

When content should be a bulleted list (not just plain lines), use `<a:buChar>` with hanging indent in the paragraph properties. **Never use unicode bullet characters (•) in the text itself.**

```xml
<!-- Bulleted paragraph with hanging indent -->
<a:p>
  <a:pPr marL="342900" indent="-342900">
    <a:spcAft><a:spcPts val="400"/></a:spcAft>
    <a:buSzPct val="100000"/>
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:rPr lang="en-US" sz="1200" dirty="0">
      <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    </a:rPr>
    <a:t>Bullet item text here</a:t>
  </a:r>
</a:p>
```

Key attributes:
- `marL="342900"` — left margin (≈0.375"), creates space for bullet
- `indent="-342900"` — negative indent pulls bullet back into margin (hanging indent)
- `<a:spcAft><a:spcPts val="400"/>` — space after paragraph (4pt)
- `<a:buSzPct val="100000"/>` — bullet size 100% of text size
- `<a:buChar char="•"/>` — bullet character

In Python helpers, add a `bullet` flag to the props dict:

```python
def bullet_ppr(props):
    """Generate paragraph properties with optional bullet."""
    a = props.get("a", "l")
    if props.get("bullet"):
        return f'''<a:pPr algn="{a}" marL="342900" indent="-342900">
          <a:spcAft><a:spcPts val="400"/></a:spcAft>
          <a:buSzPct val="100000"/><a:buChar char="\u2022"/>
        </a:pPr>'''
    return f'<a:pPr algn="{a}"/>'

# Usage in lines:
lines = [
    ("Header text", {"b": True, "sz": "1300", "c": "FFFFFF"}),
    ("First bullet point", {"sz": "1000", "c": "FFFFFF", "bullet": True}),
    ("Second bullet point", {"sz": "1000", "c": "FFFFFF", "bullet": True}),
    ("Third bullet point", {"sz": "1000", "c": "FFFFFF", "bullet": True}),
]
```

**Rule:** If the original presentation uses bullets for a list, always use `<a:buChar>` in the recreation. Plain text lines without bullets look flat and lose the visual hierarchy.

### EMU Reference

All positions and sizes are in English Metric Units (EMU):

| Measurement | EMU |
|-------------|-----|
| 1 inch | 914400 |
| 1 cm | 360000 |
| 1 pt (font) | 12700 |
| Standard slide width (16:9) | 9144000 (10") |
| Standard slide height (16:9) | 5143500 (5.625") |
| **TDI template width** | **12192000 (13.33")** |
| **TDI template height** | **6858000 (7.50")** |

Font sizes in `sz` attribute use hundredths of a point: `sz="1200"` = 12pt, `sz="1000"` = 10pt.

**⚠️ TDI templates are 1.33× larger** than standard 16:9 slides. When creating content for TDI templates, multiply standard font sizes by 1.33 (e.g., 10pt body → `sz="1300"`, not `sz="1000"`). See SKILL.md "TDI Theme Details" for the full conversion table.

---

## TDI Layout Background Reference

**⚠️ Most TDI content layouts have WHITE backgrounds.** Only title and divider layouts use the magenta (Telekom) background. Always check the background before choosing text colors.

### Light Template

| Layout | Name | Background | `showMasterSp` | Notes |
|--------|------|------------|-----------------|-------|
| slideLayout1 | Title long 01 | Magenta (`tx2`) | `0` (hidden) | Right 57% is image placeholder (x=5,297,864→edge). Content must stay left of x≈4,815,000. Has own T logo at y=5,733,256. |
| slideLayout5 | Divider 01 | Magenta (`tx2`) | `0` (hidden) | Right 40% has white geometric overlay. **NOT for full-width content.** Section divider only. |
| slideLayout10 | Only title | **White** (inherited) | default (shown) | Master elements shown: T logo (y=6,327,628), TDI cloud logo (x=10,228,840, y=6,024,445), footer (y=6,459,822). |
| Other layouts | Various | **White** (inherited) | default (shown) | Same as slideLayout10 unless they override background. |

### Dark Template

| Layout | Name | Background | `showMasterSp` | Notes |
|--------|------|------------|-----------------|-------|
| slideLayout1 | Title long 01 | Gradient (`002060` → `tx1`) | `0` (hidden) | Full-slide pic placeholder with different geometry than light. **Use `--title-image`** to get consistent magenta title look. |
| slideLayout2 | Title long 02 | Gradient (`002060` → `tx1`) | `0` (hidden) | Same as slideLayout1, alternate style. |
| slideLayout3 | Divider 02 | Dark blue | `0` (hidden) | Section divider. |
| slideLayout6 | One content | **Dark blue** (inherited) | default (shown) | Master elements shown: T logo, white cloud icon (`Grafik 7`), footer. |
| Other layouts | Various | **Dark blue** (inherited) | default (shown) | Same as slideLayout6 unless they override background. |

**⚠️ Dark template slide master has decorative elements** that appear on ALL content slides: a radial gradient background (lighter in the bottom-right corner) and a white cloud icon (`Grafik 7`, `image2.png`) in the bottom-right. These are part of the template design — not a bug or image leak.

**⚠️ Dark title slides with `--title-image`**: The script overrides the background to magenta, but the dark template's title/subtitle text colors may inherit dark-on-dark styling. Always set explicit white text on ctrTitle and subTitle placeholders:
```xml
<a:rPr lang="en-US" dirty="0">
  <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
</a:rPr>
```

### Text Color Rules

- **White background layouts (slideLayout10, etc.):**
  - Use `000000` (black) or `333333` (dark gray) for `text_box` section headers
  - Use `E20074` (magenta) for decorative arrows (→) and accent text
  - `A3A3A3` (gray) is acceptable for subtle labels/footnotes
  - ❌ **NEVER use `FFFFFF` (white) in `text_box` or other no-fill shapes** — invisible on white

- **Magenta background layouts (slideLayout1, slideLayout5):**
  - `FFFFFF` (white) is correct for text
  - `A3A3A3` (gray) works for subtle text

- **Inside filled shapes** (`rounded_rect`, `badge`, table cells):
  - `FFFFFF` is always safe — the shape's own fill provides contrast

### Title Slide Constraints (slideLayout1)

The title layout reserves the right side for an image placeholder. All custom content must stay within the left safe zone:

```
Left safe zone:
  x: 479,376 → 4,815,000  (width: ~4,336,000 = 4.7")
  y: 4,300,000 → 5,700,000 (height: ~1,400,000 = 1.5")
     ↑ below subtitle        ↑ above T logo
```

When placing badges on the title slide, use a grid layout (e.g., 3 columns × 3 rows) within this zone. Badge width ≈ 1,360,000 with 100,000 gaps fits 3 columns exactly.

### Title Slide Author/Footer Line

For author, date, or attribution text on the title slide, place a text box in the **bottom-left footer area** — below the subtitle and T logo, aligned with the slide footer zone. This position works for **both light and dark templates**.

```
Author line position (light & dark):
  x: 533,400
  y: 6,458,000
  cx: 4,200,000   cy: 400,000
```

Use italic, white, small text (`sz="1100"`, `i="1"`, color `FFFFFF`). Example: `"Author Name | Role | Month Year"`.

**⚠️ Do NOT place the author line between the title and subtitle** — it breaks visual hierarchy. Always at the bottom.
