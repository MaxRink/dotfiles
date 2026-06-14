---
name: dt-brain-shared-core-pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/core-pptx by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PPTX Skill

## Template Choice

When creating a new presentation and no template is provided by the user, **ask the user** whether they want:
1. **TDI Telekom template** — branded slides with Telekom fonts, colors, and layouts
2. **Custom design** — creative slides built from scratch with PptxGenJS

Do **not** assume either option. Always ask before starting.

| Variant | File | When to use |
|---------|------|-------------|
| **Light** (default) | `templates/tdi-slide-master.potx` | Always, unless user requests dark |
| **Dark** | `templates/tdi-slide-master-dark.potx` | Only when user explicitly requests dark theme |

### Using TDI Templates

TDI templates are `.potx` files — use them with the **editing workflow** (see [editing.md](references/editing.md)):

```bash
python scripts/office/unpack.py templates/tdi-slide-master.potx unpacked/
# Then: duplicate layouts, edit content, clean, pack as .pptx
```

### Available Layouts (Light Template)

| Layout | Name | Use for |
|--------|------|---------|
| slideLayout1 | Title long 01 | Title slide with large photo (long title). Use `--title-image` |
| slideLayout2 | Title long 02 | Alt title slide with large photo. Use `--title-image` |
| slideLayout3 | Title short 01 | Title slide (short title). Use `--title-image` |
| slideLayout4 | Title short 02 | Alt title slide (short title). Use `--title-image` |
| slideLayout5 | Divider 01 | Section divider |
| slideLayout6 | Divider 02 | Alt section divider |
| slideLayout7 | Divider 03 | Alt section divider |
| slideLayout8 | Agenda | Agenda slide |
| slideLayout9 | One content | Standard content (title + body) |
| slideLayout10 | Only title | Title only, free-form content below |
| slideLayout11 | Empty | Blank slide with footer |
| slideLayout12 | Two contents | Two-column content |
| slideLayout13 | Three contents | Three-column content |
| slideLayout14 | Four contents | Four-column content |
| slideLayout15 | Two contents with highlight | Two columns, one highlighted |
| slideLayout16 | Content with highlight | Single content with highlight area |
| slideLayout17 | Quote | Quote slide with photo |
| slideLayout18 | Content with picture | Text + picture side by side |
| slideLayout19 | Picture with content | Picture + text side by side |
| slideLayout20 | Picture (fullscale) | Full-bleed photo |
| slideLayout21 | Picture with frame | Framed photo |

### Available Layouts (Dark Template)

| Layout | Name | Use for |
|--------|------|---------|
| slideLayout1 | Title long 01 | Title slide (long title) — placeholders: ctrTitle, subTitle idx=1. Use `--title-image` |
| slideLayout2 | Title long 02 | Alt title slide. Use `--title-image` |
| slideLayout3 | Divider 02 | Section divider — placeholders: title, subTitle idx=1 |
| slideLayout4 | Divider 03 | Alt section divider — placeholders: title, subTitle idx=1 |
| slideLayout5 | Agenda | Agenda slide |
| slideLayout6 | One content | Standard content (title + body) — placeholders: title, body idx=12 |
| slideLayout7 | Only title | Title only, free-form content below — placeholder: title |
| slideLayout8 | Empty | Blank slide with footer |
| slideLayout9 | Two contents | Two-column content — placeholders: title, body idx=12, body idx=13 |
| slideLayout10 | Three contents | Three-column content |
| slideLayout11 | Four contents | Four-column content |
| slideLayout12 | Two contents with highlight | Two columns, one highlighted |
| slideLayout13 | Content with highlight | Single content with highlight area |
| slideLayout14 | Quote | Quote slide with photo |
| slideLayout15 | Content with picture | Text + picture side by side |
| slideLayout16 | Picture with content | Picture + text side by side |
| slideLayout17 | Picture (fullscale) | Full-bleed photo |
| slideLayout18 | Picture with frame | Framed photo |
| slideLayout19 | Empty no footer | Blank, no footer |

⚠️ **Light vs Dark layout numbering differs.** The dark template has fewer layouts and different numbering. Always check the table above — don't assume `slideLayout9` means the same thing in both templates.

### TDI Theme Details

**⚠️ Larger Canvas — Adjust Font Sizes**

Both TDI templates use **13.33" × 7.50"** (12192000 × 6858000 EMU), which is 1.33× larger than the standard 16:9 slide (10" × 5.625"). Text at the same point size appears ~25% smaller on TDI slides compared to standard presentations. **Always scale font sizes up by 1.33×** when porting content or matching visual density:

| Visual equivalent | Standard slide `sz=` | TDI template `sz=` |
|-------------------|----------------------|---------------------|
| Body text (10pt) | `1000` | `1300` |
| Body text (12pt) | `1200` | `1600` |
| Subheading (14pt) | `1400` | `1900` |
| Subheading (16pt) | `1600` | `2100` |
| Section header (20pt) | `2000` | `2700` |
| Section header (24pt) | `2400` | `3200` |
| Slide title (36pt) | `3600` | `4800` |

Shape positions and sizes must also use the larger coordinate space. The full slide area is 12192000 × 6858000 EMU (not 9144000 × 5143500).

**Light template:**
- **Fonts**: TeleNeo Office ExtraBold (headings), TeleNeo Office (body)
- **Colors**: Telekom magenta (`E20074`), teal (`32B9AF`), light blue (`A4DEEE`), blue (`00A8E6`)
- **Format**: 16:9 (12192000 × 6858000 EMU = 13.33" × 7.50")

**Dark template:**
- **Fonts**: Same as light
- **Background**: `002060` (dark blue)
- **Text**: `FFFFFF` (white primary), `A3A3A3` (gray secondary), `A4DEEE` (light blue for labels)
- **Accents**: `E20074` (magenta), `0D9488` (teal), `00A8E6` (blue), `6E648C` (purple)
- **Content boxes**: `0A1E40` (dark), `0F2850` (slightly lighter alternate)
- **Borders**: `1B3A5C` (subtle blue)
- **Format**: 16:9 (12192000 × 6858000 EMU)

### TDI Template Safe Zones

Content must stay within the body placeholder boundaries. Footer elements are inherited from the slide master and cannot be repositioned per-slide.

| Element | Y position (EMU) | Notes |
|---------|-------------------|-------|
| Title placeholder | 405,000 | Top of title area |
| Content body start | 1,485,024 | From slideLayout6 "One content" |
| **Content body end** | **6,324,600** | Bottom of body placeholder |
| T logo | 6,324,558 | Slide master, overlaps body edge |
| Footer text | 6,453,000 | Slide master |
| Slide number | 6,457,875 | Slide master |

**Safe bottom for custom shapes: y ≤ 6,200,000** (leaves margin above logo).

These values are available as constants in `scripts/shapes.py`: `TDI_CONTENT_TOP`, `TDI_CONTENT_BOTTOM`, etc.

### Adaptive Content Sizing

When building slides with variable-length content (e.g., 3–8 bullet points):

- **Calculate box height from content**: `cy = header_height + (line_count × line_height) + padding`
- **Typical line heights**: sz=1500 → ~280,000 EMU/line, sz=1300 → ~240,000 EMU/line
- **Scale fonts up when space allows**: if content uses < 60% of available space, increase font size one tier
- **Never set fixed large boxes for variable content** — it creates dead space and risks footer overlap
- Use `estimate_content_height()` and `fit_font_size()` from `scripts/shapes.py` for calculations

---

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Create with TDI template | Unpack TDI template → edit → pack. Read [editing.md](references/editing.md) |
| Create with custom design | Build from scratch with PptxGenJS. Read [pptxgenjs.md](references/pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](references/editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](references/pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

## Design Ideas

**Read [design.md](references/design.md) for full details** — color palettes, typography, layout options, and common mistakes.

Key principles:
- **Don't create boring slides** — every slide needs a visual element (image, chart, icon, or shape)
- **Pick a bold color palette** that matches the topic — don't default to generic blue
- **Vary layouts** across slides — don't repeat the same text-heavy layout
- **Use font size hierarchy** — bold title at one size, body smaller, muted text even smaller
- **Use real tables** (`<a:tbl>`), never monospaced text in shapes
- **Use proper bullets** (`<a:buChar>`), never unicode bullet characters

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
