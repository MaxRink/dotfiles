"""Create multiple slides from layouts in a single pass.

Usage:
    python batch_slides.py <unpacked_dir> <layout1.xml> [layout2.xml] ...

Examples:
    python batch_slides.py unpacked/ slideLayout7.xml slideLayout7.xml slideLayout3.xml
    # Creates slide4.xml, slide5.xml, slide6.xml in one call

    python batch_slides.py unpacked/ slideLayout1.xml slideLayout7.xml --count 5
    # Creates 1 from layout1 + 5 from layout7

    python batch_slides.py unpacked/ slideLayout1.xml slideLayout9.xml \
        --title-image templates/title-image.jpeg
    # Creates title slide with image + content slide

Output:
    Prints the <p:sldId> entries to add to <p:sldIdLst> in presentation.xml,
    and the slide filenames created.

    Also updates Content_Types.xml and presentation.xml.rels automatically.
    Does NOT update presentation.xml sldIdLst — paste the printed entries yourself
    or use --update-presentation to do it automatically.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

from add_slide import _is_title_layout, _add_title_image


def batch_create_slides(unpacked_dir, layouts, update_presentation=False,
                        title_image=None):
    """Create multiple slides from layouts in one pass.

    Args:
        unpacked_dir: Path to unpacked PPTX directory
        layouts: list of layout filenames (e.g., ["slideLayout7.xml", "slideLayout3.xml"])
        update_presentation: if True, replace sldIdLst in presentation.xml
        title_image: optional Path to image for title layout pic placeholders

    Returns:
        list of (slide_filename, sldId_xml) tuples
    """
    unpacked_dir = Path(unpacked_dir)
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    pres_xml_path = unpacked_dir / "ppt" / "presentation.xml"
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    ctypes_path = unpacked_dir / "[Content_Types].xml"

    # Read current state
    pres_content = pres_xml_path.read_text(encoding="utf-8")
    pres_rels = pres_rels_path.read_text(encoding="utf-8")
    ctypes = ctypes_path.read_text(encoding="utf-8")

    # Get max rId
    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', pres_rels)]
    next_rid = max(rids) + 1 if rids else 1

    # Get max slide id
    slide_ids = [int(m) for m in re.findall(r'<p:sldId[^>]*id="(\d+)"', pres_content)]
    next_slide_id = max(slide_ids) + 1 if slide_ids else 256

    # Get next slide number
    existing_nums = [int(m.group(1)) for f in slides_dir.glob("slide*.xml")
                     if (m := re.match(r"slide(\\d+)\\.xml", f.name))]
    if not existing_nums:
        existing_nums = [int(m.group(1)) for f in slides_dir.glob("slide*.xml")
                         if (m := re.match(r"slide(\d+)\.xml", f.name))]
    next_num = max(existing_nums) + 1 if existing_nums else 1

    rels_dir.mkdir(exist_ok=True)
    results = []

    for layout_file in layouts:
        # Validate layout exists
        layout_path = unpacked_dir / "ppt" / "slideLayouts" / layout_file
        if not layout_path.exists():
            print(f"Warning: {layout_path} not found, skipping", file=sys.stderr)
            continue

        sfile = f"slide{next_num}.xml"
        rid = f"rId{next_rid}"
        sid = next_slide_id

        # Create empty slide XML
        slide_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                     '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
                     ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
                     ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
                     '  <p:cSld><p:spTree>\n'
                     '    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'
                     '    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
                     '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n'
                     '  </p:spTree></p:cSld>\n'
                     '  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n'
                     '</p:sld>')
        (slides_dir / sfile).write_text(slide_xml, encoding="utf-8")

        # Create rels
        rels_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                    f'  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"'
                    f' Target="../slideLayouts/{layout_file}"/>\n'
                    '</Relationships>')
        (rels_dir / f"{sfile}.rels").write_text(rels_xml, encoding="utf-8")

        # Add title image if provided and layout is a title layout
        if title_image and _is_title_layout(layout_path):
            _add_title_image(unpacked_dir, sfile, title_image)

        # Update Content_Types
        override = (f'<Override PartName="/ppt/slides/{sfile}"'
                    f' ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        if f"/ppt/slides/{sfile}" not in ctypes:
            ctypes = ctypes.replace("</Types>", f"  {override}\n</Types>")

        # Update presentation.xml.rels
        new_rel = (f'<Relationship Id="{rid}"'
                   f' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"'
                   f' Target="slides/{sfile}"/>')
        if f"slides/{sfile}" not in pres_rels:
            pres_rels = pres_rels.replace("</Relationships>", f"  {new_rel}\n</Relationships>")

        sldid_xml = f'<p:sldId id="{sid}" r:id="{rid}"/>'
        results.append((sfile, sldid_xml))

        next_rid += 1
        next_slide_id += 1
        next_num += 1

    # Write updated files
    ctypes_path.write_text(ctypes, encoding="utf-8")
    pres_rels_path.write_text(pres_rels, encoding="utf-8")

    if update_presentation:
        # Replace sldIdLst with new entries
        new_list = "  <p:sldIdLst>\n"
        for _, sldid in results:
            new_list += f"    {sldid}\n"
        new_list += "  </p:sldIdLst>"
        pres_content = re.sub(
            r'<p:sldIdLst>.*?</p:sldIdLst>',
            new_list, pres_content, flags=re.DOTALL)
        pres_xml_path.write_text(pres_content, encoding="utf-8")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create multiple slides from layouts")
    parser.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    parser.add_argument("layouts", nargs="+", help="Layout filenames (e.g., slideLayout7.xml)")
    parser.add_argument("--update-presentation", action="store_true",
                        help="Replace sldIdLst in presentation.xml with new slides only")
    parser.add_argument("--title-image",
                        help="Image for the pic placeholder on title layouts. "
                             "Ignored for non-title layouts.")
    args = parser.parse_args()

    title_image = Path(args.title_image) if args.title_image else None
    if title_image and not title_image.exists():
        print(f"Error: {title_image} not found", file=sys.stderr)
        sys.exit(1)

    results = batch_create_slides(args.unpacked_dir, args.layouts,
                                  args.update_presentation, title_image)

    print(f"Created {len(results)} slides:")
    for sfile, sldid in results:
        print(f"  {sfile}: {sldid}")

    if not args.update_presentation:
        print("\nAdd to <p:sldIdLst> in presentation.xml:")
        for _, sldid in results:
            print(f"  {sldid}")
