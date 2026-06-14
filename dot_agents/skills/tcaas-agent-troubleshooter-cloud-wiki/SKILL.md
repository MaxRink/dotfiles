---
name: tcaas-agent-troubleshooter-cloud-wiki
description: This skill should be used when the user mentions "Confluence", "Wiki", "Telekom Wiki", "DT Wiki", "wiki.telekom.de", "CITTEST", "TCAAS", asks to "search wiki", "read page", "get page", "create page", "update page", "find documentation", or needs to access documentation in the Deutsche Telekom Confluence wiki.
---

<!-- Imported from tdi-caas/tools/tcaas-agent-troubleshooter/skills/cloud-wiki by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Telekom Wiki (Confluence) Integration

This skill provides tools to interact with the Deutsche Telekom Confluence wiki instance.

## Instance Details

- **Base URL**: `https://wiki.telekom.de`
- **API Base**: `https://wiki.telekom.de/rest/api`
- **Authentication**: Bearer Token (Personal Access Token)
- **VPN Required**: Yes - API access only works when connected to Telekom VPN

## IMPORTANT: Allowed Spaces

Operations are **restricted** to these spaces only:

| Space Key | Description |
|-----------|-------------|
| CITTEST | CIT Test/Documentation space |
| TCAAS | T-CaaS project space |
| CITOH | IaaS HandBook/KB |
| ckbsh | CaaS Knowledge Base (shared) |

All scripts validate the space and will refuse operations on other spaces.
Scripts that target a single space accept a `--space` parameter (defaults to CITTEST).

## Authentication Setup

The Telekom Wiki uses **Basic Auth** with username and API token. Set both environment variables:

```bash
export CONFLUENCE_USER="your.email@t-systems.com"
export CONFLUENCE_TOKEN="your-personal-access-token"
```

To get a PAT:
1. Go to https://wiki.telekom.de
2. Click your profile icon → Settings
3. Go to Personal Access Tokens
4. Create a new token with appropriate permissions

**Important:** Both `CONFLUENCE_USER` (your email) and `CONFLUENCE_TOKEN` are required.

## Operations

All scripts are Python-based and should be run with the project venv:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/<script>.py [arguments]
```

### Get Page

Retrieve a page by ID or title:

```bash
# By ID
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-page.py --id 12345

# By title
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-page.py --title "E2E CIT Infrastructure Architecture"

# Output as JSON
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-page.py --id 12345 --format json

# Output raw Confluence storage format
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-page.py --id 12345 --format confluence
```

Options:
- `--id ID` - Page ID
- `--title TITLE` - Page title (searches in specified space)
- `--space SPACE` - Space key for title search (default: CITTEST)
- `--format` - Output format: `markdown` (default), `confluence`, `json`
- `--expand` - Confluence expand fields (default: body.storage,version,space,ancestors)

### Search Pages

Search for pages using CQL (Confluence Query Language):

```bash
# Full-text search
.venv/bin/python ${SKILL_DIR}/scripts/wiki-search.py --query "text ~ 'kubernetes'"

# Search in titles
.venv/bin/python ${SKILL_DIR}/scripts/wiki-search.py --query "title ~ 'architecture'"

# Search by label
.venv/bin/python ${SKILL_DIR}/scripts/wiki-search.py --query "label = 'documentation'"

# Recently modified
.venv/bin/python ${SKILL_DIR}/scripts/wiki-search.py --query "lastModified > now('-7d')"

# With limit and JSON output
.venv/bin/python ${SKILL_DIR}/scripts/wiki-search.py --query "text ~ 'api'" --limit 50 --format json
```

Options:
- `--query, -q` - CQL search query (required)
- `--space` - Space key to search in (default: all allowed spaces)
- `--limit` - Maximum results (default: 25)
- `--format` - Output format: `table` (default), `json`

The query is automatically scoped to allowed spaces. Use `--space SPACE` to restrict to a single space.

### List Pages

List all pages in a space (use `--space` to specify):

```bash
# List first 25 pages
.venv/bin/python ${SKILL_DIR}/scripts/wiki-list-pages.py

# List more pages
.venv/bin/python ${SKILL_DIR}/scripts/wiki-list-pages.py --limit 50

# Pagination
.venv/bin/python ${SKILL_DIR}/scripts/wiki-list-pages.py --start 25 --limit 25

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/wiki-list-pages.py --format json
```

Options:
- `--space` - Space key (default: CITTEST)
- `--limit` - Maximum results (default: 25)
- `--start` - Start index for pagination (default: 0)
- `--format` - Output format: `table` (default), `json`

### Create Page

Create a new page:

```bash
# Simple page
.venv/bin/python ${SKILL_DIR}/scripts/wiki-create-page.py \
  --title "My New Page" \
  --content "<p>Hello World</p>"

# Child page
.venv/bin/python ${SKILL_DIR}/scripts/wiki-create-page.py \
  --title "Child Page" \
  --parent-id 12345 \
  --content "<p>This is a child page</p>"

# From file
.venv/bin/python ${SKILL_DIR}/scripts/wiki-create-page.py \
  --title "Page from File" \
  --content-file page-content.html
```

Options:
- `--title TITLE` - Page title (required)
- `--space SPACE` - Space key (default: CITTEST). Allowed: CITTEST, TCAAS, CITOH, CKBSH
- `--parent-id ID` - Parent page ID (creates as child)
- `--content TEXT` - Page content in Confluence storage format
- `--content-file FILE` - Read content from file
- `--content-format` - Content format: `storage` (default), `wiki`

### Update Page

Update an existing page (auto-increments version):

```bash
# Update content
.venv/bin/python ${SKILL_DIR}/scripts/wiki-update-page.py \
  --id 12345 \
  --content "<p>Updated content</p>"

# Update title
.venv/bin/python ${SKILL_DIR}/scripts/wiki-update-page.py \
  --id 12345 \
  --title "New Page Title"

# Update from file
.venv/bin/python ${SKILL_DIR}/scripts/wiki-update-page.py \
  --id 12345 \
  --content-file updated-content.html
```

Options:
- `--id ID` - Page ID (required)
- `--title TITLE` - New page title
- `--content TEXT` - New content
- `--content-file FILE` - Read content from file

### Get Child Pages

Get children of a page:

```bash
# Direct children
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-children.py --parent-id 12345

# With depth
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-children.py --parent-id 12345 --depth 2

# Tree format
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-children.py --parent-id 12345 --format tree

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/wiki-get-children.py --parent-id 12345 --format json
```

Options:
- `--parent-id ID` - Parent page ID (required)
- `--depth N` - Depth of children (default: 1, max: 10)
- `--limit N` - Max children per level (default: 100)
- `--format` - Output format: `table` (default), `tree`, `json`

## CQL Quick Reference

Common CQL patterns for searching:

```cql
# Full-text search
text ~ 'search term'

# Title search
title ~ 'page title'

# By label
label = 'label-name'

# By creator
creator = 'username'

# Recently modified (last 7 days)
lastModified > now('-7d')

# Under specific parent
ancestor = 12345

# Combine conditions
text ~ 'kubernetes' AND lastModified > '2024-01-01'
```

See [api-reference.md](references/api-reference.md) for full CQL documentation.

## Content Format

Pages use Confluence storage format (XHTML-based):

```html
<!-- Paragraph -->
<p>Text content</p>

<!-- Headings -->
<h1>Heading 1</h1>
<h2>Heading 2</h2>

<!-- List -->
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<!-- Code block -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">bash</ac:parameter>
  <ac:plain-text-body><![CDATA[
echo "Hello World"
  ]]></ac:plain-text-body>
</ac:structured-macro>

<!-- Link -->
<a href="https://example.com">Link text</a>

<!-- Bold/Italic -->
<strong>Bold</strong>
<em>Italic</em>
```

## Error Handling

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| CONFLUENCE_TOKEN not set | Missing environment variable | `export CONFLUENCE_TOKEN="your-token"` |
| HTTP 401 | Invalid or expired token | Generate new PAT |
| HTTP 403 | No permission | Check space permissions |
| HTTP 404 | Page not found | Verify page ID/title |
| HTTP 409 | Version conflict | Retry (script auto-increments version) |
| Connection refused | Not on VPN | Connect to Telekom VPN |

## Security Notes

1. **Token Storage**: Never commit CONFLUENCE_TOKEN to version control
2. **Space Restriction**: Scripts enforce allowed spaces only (CITTEST, TCAAS, CITOH, CKBSH)
3. **Audit**: All API calls use your personal token - actions are attributed to you
4. **VPN**: Only works when connected to Telekom VPN
5. **No Delete**: Delete operation is not exposed to prevent accidental data loss

## Output Formats

### Markdown (default for get-page)
Human-readable format with basic Confluence-to-Markdown conversion.

### Confluence (storage format)
Raw XHTML storage format as stored in Confluence.

### JSON
Raw API response for programmatic processing.

### Table (default for list/search)
Formatted table with key information.

### Tree (for get-children)
Hierarchical tree view of page structure.

## References

| File | When to Read |
|------|-------------|
| `references/api-reference.md` | Full CQL documentation and Confluence API details |
| `references/sre-handbook.md` | SRE Handbook page IDs (CKBSH space) — use when creating or navigating SRE handbook pages |
