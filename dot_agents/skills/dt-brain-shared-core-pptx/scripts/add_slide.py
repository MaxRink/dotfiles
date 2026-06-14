"""Add a new slide to an unpacked PPTX directory.

Usage: python add_slide.py <unpacked_dir> <source> [--title-image <path>]

The source can be:
  - A slide file (e.g., slide2.xml) - duplicates the slide
  - A layout file (e.g., slideLayout2.xml) - creates from layout

Options:
  --title-image <path>  Image to populate the pic placeholder on title layouts.
                        Title layouts are auto-detected (have both ctrTitle and
                        pic placeholders). If the layout is not a title layout,
                        the flag is silently ignored.

Examples:
    python add_slide.py unpacked/ slide2.xml
    # Duplicates slide2, creates slide5.xml

    python add_slide.py unpacked/ slideLayout2.xml
    # Creates slide5.xml from slideLayout2.xml

    python add_slide.py unpacked/ slideLayout1.xml --title-image templates/title-image.jpeg
    # Creates title slide with image in pic placeholder

To see available layouts: ls unpacked/ppt/slideLayouts/

Prints the <p:sldId> element to add to presentation.xml.
"""

import re
import shutil
import sys
from pathlib import Path


def _is_title_layout(layout_path: Path) -> bool:
    """Check if a layout has both ctrTitle and pic placeholders (= title layout)."""
    content = layout_path.read_text(encoding="utf-8")
    return 'type="ctrTitle"' in content and 'type="pic"' in content


def _get_next_media_name(media_dir: Path, ext: str) -> str:
    """Get the next available imageN.ext filename in the media directory."""
    existing = [int(m.group(1)) for f in media_dir.glob(f"image*{ext}")
                if (m := re.match(r"image(\d+)", f.stem))]
    next_num = max(existing) + 1 if existing else 1
    return f"image{next_num}{ext}"


def _add_title_image(unpacked_dir: Path, dest: str, image_path: Path) -> None:
    """Add an image to a title slide's pic placeholder.

    Copies the image to ppt/media/, adds an image rel, and injects <p:pic> XML.
    """
    media_dir = unpacked_dir / "ppt" / "media"
    media_dir.mkdir(exist_ok=True)

    ext = image_path.suffix.lower()
    media_name = _get_next_media_name(media_dir, ext)
    shutil.copy2(image_path, media_dir / media_name)

    # Add image relationship to slide rels
    rels_path = unpacked_dir / "ppt" / "slides" / "_rels" / f"{dest}.rels"
    rels_content = rels_path.read_text(encoding="utf-8")

    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels_content)]
    img_rid = f"rId{max(rids) + 1 if rids else 2}"

    mime_map = {".jpeg": "image/jpeg", ".jpg": "image/jpeg", ".png": "image/png"}
    content_type = mime_map.get(ext, "image/jpeg")

    new_rel = (f'<Relationship Id="{img_rid}"'
               f' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"'
               f' Target="../media/{media_name}"/>')
    rels_content = rels_content.replace("</Relationships>", f"  {new_rel}\n</Relationships>")
    rels_path.write_text(rels_content, encoding="utf-8")

    # Add content type if needed
    ctypes_path = unpacked_dir / "[Content_Types].xml"
    ctypes = ctypes_path.read_text(encoding="utf-8")
    ext_bare = ext.lstrip(".")
    if f'Extension="{ext_bare}"' not in ctypes:
        ctypes = ctypes.replace("</Types>",
                                f'  <Default Extension="{ext_bare}" ContentType="{content_type}"/>\n</Types>')
        ctypes_path.write_text(ctypes, encoding="utf-8")

    # Inject <p:pic> with explicit geometry from light template (diagonal clip)
    # Uses <p:pic> (not <p:sp>) so PowerPoint treats it as filled — no "Insert Picture" prompt
    # Uses fixed position/custGeom so both light and dark templates look identical
    pic_xml = (
        f'<p:pic>\n'
        f'  <p:nvPicPr>\n'
        f'    <p:cNvPr id="10" name="Title Image"/>\n'
        f'    <p:cNvPicPr><a:picLocks noGrp="1"/></p:cNvPicPr>\n'
        f'    <p:nvPr><p:ph type="pic" idx="10"/></p:nvPr>\n'
        f'  </p:nvPicPr>\n'
        f'  <p:blipFill>\n'
        f'    <a:blip r:embed="{img_rid}"/>\n'
        f'    <a:stretch><a:fillRect/></a:stretch>\n'
        f'  </p:blipFill>\n'
        f'  <p:spPr bwMode="gray">\n'
        f'    <a:xfrm>\n'
        f'      <a:off x="5297864" y="0"/>\n'
        f'      <a:ext cx="6894136" cy="6858000"/>\n'
        f'    </a:xfrm>\n'
        f'    <a:custGeom>\n'
        f'      <a:avLst/>\n'
        f'      <a:gdLst>\n'
        f'        <a:gd name="connsiteX0" fmla="*/ 6894136 w 6894136"/>\n'
        f'        <a:gd name="connsiteY0" fmla="*/ 0 h 6858000"/>\n'
        f'        <a:gd name="connsiteX1" fmla="*/ 6894136 w 6894136"/>\n'
        f'        <a:gd name="connsiteY1" fmla="*/ 6858000 h 6858000"/>\n'
        f'        <a:gd name="connsiteX2" fmla="*/ 0 w 6894136"/>\n'
        f'        <a:gd name="connsiteY2" fmla="*/ 6858000 h 6858000"/>\n'
        f'        <a:gd name="connsiteX3" fmla="*/ 1265474 w 6894136"/>\n'
        f'        <a:gd name="connsiteY3" fmla="*/ 197 h 6858000"/>\n'
        f'      </a:gdLst>\n'
        f'      <a:ahLst/>\n'
        f'      <a:cxnLst>\n'
        f'        <a:cxn ang="0"><a:pos x="connsiteX0" y="connsiteY0"/></a:cxn>\n'
        f'        <a:cxn ang="0"><a:pos x="connsiteX1" y="connsiteY1"/></a:cxn>\n'
        f'        <a:cxn ang="0"><a:pos x="connsiteX2" y="connsiteY2"/></a:cxn>\n'
        f'        <a:cxn ang="0"><a:pos x="connsiteX3" y="connsiteY3"/></a:cxn>\n'
        f'      </a:cxnLst>\n'
        f'      <a:rect l="l" t="t" r="r" b="b"/>\n'
        f'      <a:pathLst>\n'
        f'        <a:path w="6894136" h="6858000">\n'
        f'          <a:moveTo><a:pt x="6894136" y="0"/></a:moveTo>\n'
        f'          <a:lnTo><a:pt x="6894136" y="6858000"/></a:lnTo>\n'
        f'          <a:lnTo><a:pt x="0" y="6858000"/></a:lnTo>\n'
        f'          <a:lnTo><a:pt x="1265474" y="197"/></a:lnTo>\n'
        f'          <a:close/>\n'
        f'        </a:path>\n'
        f'      </a:pathLst>\n'
        f'    </a:custGeom>\n'
        f'  </p:spPr>\n'
        f'</p:pic>\n'
    )

    slide_path = unpacked_dir / "ppt" / "slides" / dest
    slide_content = slide_path.read_text(encoding="utf-8")
    slide_content = slide_content.replace("</p:grpSpPr>\n", f"</p:grpSpPr>\n{pic_xml}")
    # Handle compact XML (no newline after grpSpPr)
    if pic_xml not in slide_content:
        slide_content = slide_content.replace("</p:grpSpPr>", f"</p:grpSpPr>\n{pic_xml}")

    # Force magenta background so both light and dark templates look identical
    bg_xml = (
        '<p:bg>\n'
        '  <p:bgPr>\n'
        '    <a:solidFill><a:srgbClr val="E20074"/></a:solidFill>\n'
        '    <a:effectLst/>\n'
        '  </p:bgPr>\n'
        '</p:bg>\n'
    )
    slide_content = slide_content.replace("<p:spTree>", f"{bg_xml}<p:spTree>")

    slide_path.write_text(slide_content, encoding="utf-8")


def get_next_slide_number(slides_dir: Path) -> int:
    existing = [int(m.group(1)) for f in slides_dir.glob("slide*.xml")
                if (m := re.match(r"slide(\d+)\.xml", f.name))]
    return max(existing) + 1 if existing else 1


def create_slide_from_layout(unpacked_dir: Path, layout_file: str,
                             title_image: Path | None = None) -> None:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    layouts_dir = unpacked_dir / "ppt" / "slideLayouts"

    layout_path = layouts_dir / layout_file
    if not layout_path.exists():
        print(f"Error: {layout_path} not found", file=sys.stderr)
        sys.exit(1)

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    dest_slide = slides_dir / dest
    dest_rels = rels_dir / f"{dest}.rels"

    slide_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>'''
    dest_slide.write_text(slide_xml, encoding="utf-8")

    rels_dir.mkdir(exist_ok=True)
    rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout_file}"/>
</Relationships>'''
    dest_rels.write_text(rels_xml, encoding="utf-8")

    # Add title image if provided and layout is a title layout
    if title_image and _is_title_layout(layout_path):
        _add_title_image(unpacked_dir, dest, title_image)

    _add_to_content_types(unpacked_dir, dest)

    rid = _add_to_presentation_rels(unpacked_dir, dest)

    next_slide_id = _get_next_slide_id(unpacked_dir)

    print(f"Created {dest} from {layout_file}")
    print(f'Add to presentation.xml <p:sldIdLst>: <p:sldId id="{next_slide_id}" r:id="{rid}"/>')


def duplicate_slide(unpacked_dir: Path, source: str) -> None:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"

    source_slide = slides_dir / source

    if not source_slide.exists():
        print(f"Error: {source_slide} not found", file=sys.stderr)
        sys.exit(1)

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    dest_slide = slides_dir / dest

    source_rels = rels_dir / f"{source}.rels"
    dest_rels = rels_dir / f"{dest}.rels"

    shutil.copy2(source_slide, dest_slide)

    if source_rels.exists():
        shutil.copy2(source_rels, dest_rels)

        rels_content = dest_rels.read_text(encoding="utf-8")
        rels_content = re.sub(
            r'\s*<Relationship[^>]*Type="[^"]*notesSlide"[^>]*/>\s*',
            "\n",
            rels_content,
        )
        dest_rels.write_text(rels_content, encoding="utf-8")

    _add_to_content_types(unpacked_dir, dest)

    rid = _add_to_presentation_rels(unpacked_dir, dest)

    next_slide_id = _get_next_slide_id(unpacked_dir)

    print(f"Created {dest} from {source}")
    print(f'Add to presentation.xml <p:sldIdLst>: <p:sldId id="{next_slide_id}" r:id="{rid}"/>')


def _add_to_content_types(unpacked_dir: Path, dest: str) -> None:
    content_types_path = unpacked_dir / "[Content_Types].xml"
    content_types = content_types_path.read_text(encoding="utf-8")

    new_override = f'<Override PartName="/ppt/slides/{dest}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'

    if f"/ppt/slides/{dest}" not in content_types:
        content_types = content_types.replace("</Types>", f"  {new_override}\n</Types>")
        content_types_path.write_text(content_types, encoding="utf-8")


def _add_to_presentation_rels(unpacked_dir: Path, dest: str) -> str:
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    pres_rels = pres_rels_path.read_text(encoding="utf-8")

    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', pres_rels)]
    next_rid = max(rids) + 1 if rids else 1
    rid = f"rId{next_rid}"

    new_rel = f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{dest}"/>'

    if f"slides/{dest}" not in pres_rels:
        pres_rels = pres_rels.replace("</Relationships>", f"  {new_rel}\n</Relationships>")
        pres_rels_path.write_text(pres_rels, encoding="utf-8")

    return rid


def _get_next_slide_id(unpacked_dir: Path) -> int:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    pres_content = pres_path.read_text(encoding="utf-8")
    slide_ids = [int(m) for m in re.findall(r'<p:sldId[^>]*id="(\d+)"', pres_content)]
    return max(slide_ids) + 1 if slide_ids else 256


def parse_source(source: str) -> tuple[str, str | None]:
    if source.startswith("slideLayout") and source.endswith(".xml"):
        return ("layout", source)

    return ("slide", None)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Add a new slide to an unpacked PPTX directory.")
    parser.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    parser.add_argument("source", help="slide2.xml (duplicate) or slideLayout2.xml (from layout)")
    parser.add_argument("--title-image",
                        help="Image for the pic placeholder on title layouts. "
                             "Ignored if the layout is not a title layout.")
    args = parser.parse_args()

    unpacked_dir = Path(args.unpacked_dir)
    source = args.source
    title_image = Path(args.title_image) if args.title_image else None

    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    if title_image and not title_image.exists():
        print(f"Error: {title_image} not found", file=sys.stderr)
        sys.exit(1)

    source_type, layout_file = parse_source(source)

    if source_type == "layout" and layout_file is not None:
        create_slide_from_layout(unpacked_dir, layout_file, title_image)
    else:
        duplicate_slide(unpacked_dir, source)
