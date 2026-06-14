---
name: ai4dev-telecontext-tardis
description: >-
  Search and explore APIs on the TARDIS platform. Use when the user asks about
  TARDIS APIs, API catalog, API specifications, OpenAPI specs, or wants to find/explore
  APIs available on the TARDIS platform. Handles API search, details, and spec retrieval.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/tardis by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TARDIS API Explorer

Search and explore APIs on Deutsche Telekom's TARDIS platform.

The user's query is: "$ARGUMENTS"

## Tools

Three tools available, used in sequence:

### 1. `tardis_api_search` - Find APIs
Search by name or keyword. Returns up to 100 matching APIs with titles, descriptions, IDs, and available environments.

Tips:
- Use specific API names: "customer-service", "payment-api"
- Try abbreviations or partial names: "customer" matches "customer-service", "customer-data"

### 2. `get_tardis_api_details` - Get API details
Get comprehensive info about a specific API environment: base path, visibility, spec links, monitoring, team contacts.

- Use the `path` from search results: `[*].environments[*].url` field (must start with `/api/catalog`)
- Pick the right environment: prefer production > playground > any available
- Note: provided URLs may not be accessible from the user's network

### 3. `get_tardis_openapi_spec` - Get OpenAPI spec
Fetch the full OpenAPI specification (YAML/JSON).

- Use the `yamlLink` or `jsonLink` from `get_tardis_api_details` response
- Path must start with `/api/catalog/spec`
- Response may be large - consider saving to a file

## Workflow

```
tardis_api_search("payment") → find API
    ↓
get_tardis_api_details(path from results) → get details + spec links
    ↓
get_tardis_openapi_spec(yamlLink or jsonLink) → full OpenAPI spec
```

## Environment Priority

When no specific environment requested: production > playground > any available.
