# Confluence REST API Quick Reference

This document provides a quick reference for the Confluence REST API used by the cloud-wiki skill.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Get Page by ID](#get-page-by-id)
  - [Search Pages (CQL)](#search-pages-cql)
  - [List Pages in Space](#list-pages-in-space)
  - [Create Page](#create-page)
  - [Update Page](#update-page)
  - [Get Child Pages](#get-child-pages)
  - [Delete Page](#delete-page)
- [CQL (Confluence Query Language)](#cql-confluence-query-language)
- [Storage Format](#storage-format)
- [Error Codes](#error-codes)
- [Rate Limits](#rate-limits)
- [Resources](#resources)

## Base URL

```
https://wiki.telekom.de/rest/api
```

## Authentication

All requests require Bearer token authentication:

```bash
curl -H "Authorization: Bearer ${CONFLUENCE_TOKEN}" \
     -H "Content-Type: application/json" \
     "${WIKI_URL}/rest/api/..."
```

## Endpoints

### Get Page by ID

```
GET /rest/api/content/{id}
```

Query parameters:
- `expand` - Comma-separated list of properties to expand
  - `body.storage` - Page content in storage format
  - `body.view` - Page content in view format
  - `version` - Version information
  - `space` - Space information
  - `ancestors` - Parent page hierarchy
  - `children.page` - Child pages
  - `history` - Edit history

Example:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     "${WIKI_URL}/rest/api/content/12345?expand=body.storage,version,space"
```

### Search Pages (CQL)

```
GET /rest/api/content/search
```

Query parameters:
- `cql` - Confluence Query Language query (URL encoded)
- `limit` - Maximum results (default: 25, max: 100)
- `start` - Pagination offset
- `expand` - Properties to expand

Example:
```bash
CQL="space = CITTEST AND text ~ 'kubernetes'"
curl -s -H "Authorization: Bearer $TOKEN" \
     "${WIKI_URL}/rest/api/content/search?cql=${CQL_ENCODED}&limit=25"
```

### List Pages in Space

```
GET /rest/api/content
```

Query parameters:
- `spaceKey` - Space key (required)
- `type` - Content type: `page`, `blogpost`, `comment`
- `limit` - Maximum results
- `start` - Pagination offset
- `expand` - Properties to expand

Example:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     "${WIKI_URL}/rest/api/content?spaceKey=CITTEST&type=page&limit=25"
```

### Create Page

```
POST /rest/api/content
```

Request body:
```json
{
  "type": "page",
  "title": "Page Title",
  "space": {
    "key": "CITTEST"
  },
  "ancestors": [
    {"id": "parentPageId"}
  ],
  "body": {
    "storage": {
      "value": "<p>Content in storage format</p>",
      "representation": "storage"
    }
  }
}
```

Example:
```bash
curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"type":"page","title":"New Page","space":{"key":"CITTEST"},"body":{"storage":{"value":"<p>Hello</p>","representation":"storage"}}}' \
     "${WIKI_URL}/rest/api/content"
```

### Update Page

```
PUT /rest/api/content/{id}
```

Request body (version number must be incremented):
```json
{
  "id": "12345",
  "type": "page",
  "title": "Updated Title",
  "space": {
    "key": "CITTEST"
  },
  "version": {
    "number": 2
  },
  "body": {
    "storage": {
      "value": "<p>Updated content</p>",
      "representation": "storage"
    }
  }
}
```

### Get Child Pages

```
GET /rest/api/content/{id}/child/page
```

Query parameters:
- `limit` - Maximum results
- `start` - Pagination offset
- `expand` - Properties to expand

Example:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     "${WIKI_URL}/rest/api/content/12345/child/page?limit=100&expand=version"
```

### Delete Page

```
DELETE /rest/api/content/{id}
```

Note: Not implemented in the skill to prevent accidental deletion.

## CQL (Confluence Query Language)

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `space = CITTEST` |
| `!=` | Not equals | `type != blogpost` |
| `~` | Contains (text search) | `text ~ 'kubernetes'` |
| `!~` | Does not contain | `title !~ 'draft'` |
| `>`, `<`, `>=`, `<=` | Comparison | `lastModified > '2024-01-01'` |
| `IN` | In list | `label IN ('doc', 'api')` |
| `NOT IN` | Not in list | `space NOT IN ('PRIVATE')` |

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| `space` | Space key | `space = CITTEST` |
| `type` | Content type | `type = page` |
| `title` | Page title | `title ~ 'architecture'` |
| `text` | Full-text content | `text ~ 'kubernetes'` |
| `label` | Page labels | `label = 'documentation'` |
| `creator` | Created by | `creator = 'username'` |
| `contributor` | Edited by | `contributor = 'username'` |
| `created` | Creation date | `created > '2024-01-01'` |
| `lastModified` | Last modified | `lastModified >= now('-7d')` |
| `ancestor` | Parent page ID | `ancestor = 12345` |
| `parent` | Direct parent | `parent = 12345` |

### Date Functions

- `now()` - Current time
- `now('-7d')` - 7 days ago
- `now('+1M')` - 1 month from now
- `startOfDay()` - Start of today
- `startOfWeek()` - Start of this week
- `startOfMonth()` - Start of this month
- `startOfYear()` - Start of this year

### Example Queries

```cql
# All pages in CITTEST space
space = CITTEST AND type = page

# Search for text
space = CITTEST AND text ~ 'kubernetes cluster'

# Recently modified pages
space = CITTEST AND lastModified > now('-7d')

# Pages with specific label
space = CITTEST AND label = 'architecture'

# Pages created by user
space = CITTEST AND creator = 'john.doe'

# Pages under specific parent
space = CITTEST AND ancestor = 12345

# Combine conditions
space = CITTEST AND type = page AND text ~ 'api' AND lastModified > '2024-01-01'
```

## Storage Format

Confluence uses XHTML-based storage format for page content.

### Common Elements

```html
<!-- Paragraph -->
<p>Text content</p>

<!-- Headings -->
<h1>Heading 1</h1>
<h2>Heading 2</h2>

<!-- Lists -->
<ul>
  <li>Unordered item</li>
</ul>
<ol>
  <li>Ordered item</li>
</ol>

<!-- Links -->
<a href="https://example.com">External link</a>
<ac:link><ri:page ri:content-title="Page Title"/></ac:link>

<!-- Bold/Italic -->
<strong>Bold</strong>
<em>Italic</em>

<!-- Code block -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">bash</ac:parameter>
  <ac:plain-text-body><![CDATA[
    echo "Hello World"
  ]]></ac:plain-text-body>
</ac:structured-macro>

<!-- Info panel -->
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>Info message</p>
  </ac:rich-text-body>
</ac:structured-macro>

<!-- Table -->
<table>
  <tbody>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
    <tr>
      <td>Cell 1</td>
      <td>Cell 2</td>
    </tr>
  </tbody>
</table>
```

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (no permission) |
| 404 | Not found |
| 409 | Conflict (version mismatch on update) |
| 500 | Server error |

## Rate Limits

The Telekom Confluence instance may have rate limits. If you encounter HTTP 429 errors, wait before retrying.

## Resources

- [Confluence REST API Documentation](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/)
- [CQL Reference](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)
- [Storage Format](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
