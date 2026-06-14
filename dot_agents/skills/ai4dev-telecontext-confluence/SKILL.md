---
name: ai4dev-telecontext-confluence
description: >-
  Interact with Confluence via Telecontext. Use when the user wants to search, read,
  create, or update Confluence wiki pages, comments, labels, or find users on DT-IT's
  Confluence instance. Supports CQL search, page CRUD, and content management.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/confluence by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Confluence Operations via Telecontext

Interact with DT-IT's Confluence instance through Telecontext MCP tools.

The user's query is: "$ARGUMENTS"

## Available Tools

### Search & Read
- `confluence_search` - Search using simple text or CQL. Key param: `query`.
  CQL examples: `'type=page AND space=DEV'`, `'title~"Meeting Notes"'`, `'label=documentation'`, `'siteSearch ~ "concept"'`
  Personal spaces: `'space="~username"'` (must quote ~username)
- `confluence_get_page` - Get page content by ID, or by title + space_key.
  Set `convert_to_markdown: true` (default) for readable output, `false` for raw HTML (reveals macros but uses more tokens).
- `confluence_get_page_children` - List child pages/folders of a parent page.
- `confluence_get_comments` - Get comments on a page.
- `confluence_get_labels` - Get labels on a page.
- `confluence_confluence_get_page_views` - Get page view stats (Cloud only).
- `confluence_search_user` - Find users via CQL: `'user.fullname ~ "First Last"'`

### Create & Modify
- `confluence_create_page` - Create page. Requires `space_key`, `title`, `content`.
  Content formats: `markdown` (default), `wiki`, or `storage`.
  Optional: `parent_id`, `emoji` for page icon.
- `confluence_update_page` - Update page. Requires `page_id`, `title`, `content`.
  Supports `is_minor_edit`, `version_comment`.
- `confluence_delete_page` - Delete page by ID.
- `confluence_add_comment` - Add comment (Markdown format).
- `confluence_add_label` - Add label to a page.

## Page ID

The page ID is the numeric part from the URL:
`https://example.atlassian.net/wiki/spaces/TEAM/pages/123456789/Page+Title` → ID is `123456789`

## Auth

Requires **API Token** for Confluence (NOT Personal Access Token). Configure in Teleconsole > Authorization Services.
If you get auth errors, verify you used the correct token type.
