---
name: tdi-cloudbrain-telekom-pdf
user-invocable: true
description: This skill should be used when the user mentions "PDF", "create PDF", "generate PDF", "make PDF", "convert to PDF", "PDF from markdown", "report as PDF", "export PDF", asks to create a document, generate a report PDF, or needs to convert markdown files to styled PDF documents with Telekom branding.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/telekom-pdf by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PDF Generation Skill

## Description

This skill generates professional PDF documents with consistent Telekom styling:
- Magenta (#e20074) branded headers
- Professional typography
- Code blocks with syntax highlighting
- Tables with styled headers
- Page numbers and document headers

## Available Operations

### 1. Convert Markdown to PDF
Convert an existing markdown file to a styled PDF.

```bash
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --markdown <file.md> --output <output.pdf>
```

### 2. Generate PDF from Content
Create a PDF directly from title and content.

```bash
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --title "Document Title" --content "## Section\n- Point 1\n- Point 2"
```

### 3. Use Templates
Generate PDFs using predefined templates.

```bash
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --title "Title" --template <template-type>
```

**Available templates:**
- `documentation` - Technical documentation (default)
- `howto` - Step-by-step guides
- `release-notes` - Release notes format
- `architecture` - Architecture documentation

## Usage Examples

```bash
# Convert markdown file to PDF
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --markdown docs/guide.md --output docs/guide.pdf

# Generate PDF with template
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --title "Kubernetes RBAC Guide" --template howto --output docs/rbac-guide.pdf

# Quick PDF from inline content
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --title "Meeting Notes" --content "## Attendees\n- Alice\n- Bob\n\n## Topics\n- Project status\n- Next steps"

# Show help
.venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --help
```

## Output

- Default output directory: `docs/`
- Default filename: `<title-slugified>.pdf`
- Override with `--output <path>`

## Dependencies

- Python 3.x
- fpdf2 library (installed in project .venv)

## Known Limitations

- **Title from filename**: When using `--markdown`, the title is derived from the filename. Always pass `--title` explicitly for a clean document title and header.

## Instructions for Claude

When the user wants to create a PDF:

1. **Determine the source**:
   - If they have a markdown file, use `--markdown`
   - If they want to generate content, use `--title` and optionally `--content` or `--template`

2. **Choose appropriate template** if generating:
   - `howto` for step-by-step procedures
   - `documentation` for general technical docs
   - `release-notes` for version releases
   - `architecture` for system design docs

3. **Run the script** - always pass `--title` when using `--markdown`:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/generate-pdf.py --markdown file.md --title "Clean Title" --output out.pdf
   ```

4. **Report the output path** to the user.
