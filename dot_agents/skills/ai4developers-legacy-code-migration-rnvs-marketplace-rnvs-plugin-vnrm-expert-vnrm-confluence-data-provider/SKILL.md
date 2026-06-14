---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-confluence-data-provider
description: Retrieves VNRM architecture documentation and component specifications from DHVOICE Confluence space using Telecontext MCP. Use when analyzing VNRM architecture, researching component designs, investigating inventory relationships, or when users ask about VNRM system documentation, microservice specifications, or telecommunications architecture patterns.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-confluence-data-provider by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM Confluence Data Provider

Retrieves targeted VNRM architecture documentation and component specifications from DHVOICE Confluence space using Telecontext MCP tools.

## VNRM Components

**Core Components**: SPE, PRT, COM, COR, NUM, PORT
**Architecture Areas**: APIs, BOM, Inventory, Order Management, Runtime, Requirements

For complete component descriptions and search patterns, see [FILTERS.md](references/FILTERS.md).

## Quick Start

Search DHVOICE space for VNRM architecture information:

**Step 1: Search for relevant pages**
```
mcp__Telecontext__search_tools -> "confluence search"
mcp__Telecontext__call_readonly_tool -> confluence_search
```

**Step 2: Get detailed page content**
```
mcp__Telecontext__call_readonly_tool -> confluence_get_page
```

## Successful Search Examples

### Example 1: Finding inventory relationships
**Query**: "VNRM architecture DHVOICE inventory"
**Tool call**:
```json
{
  "tool_name": "confluence_search",
  "tool_parameters": {"query": "VNRM architecture DHVOICE inventory"}
}
```
**Expected result**: Pages about inventory relationships, including page ID 3236856371

### Example 2: Getting specific page content
**Page ID found**: 3236856371
**Tool call**:
```json
{
  "tool_name": "confluence_get_page",
  "tool_parameters": {"page_id": "3236856371"}
}
```
**Result**: Full page content with inventory relationship tables and diagrams

### Example 3: Finding component architecture
**Query**: "VNRM NUM architecture component"
**Tool call**:
```json
{
  "tool_name": "confluence_search",
  "tool_parameters": {"query": "NUM NUMBERMANAGEMENT VNRM architecture"}
}
```

## Advanced Usage

**Get page children**: See [ADVANCED.md](references/ADVANCED.md) for child page navigation
**Search filters**: See [FILTERS.md](references/FILTERS.md) for component-specific search patterns
**Troubleshooting**: See [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for error handling

## Tool Workflow

1. **Search first**: Use `confluence_search` to find relevant pages
2. **Get page details**: Use `confluence_get_page` with page_id from search results
3. **Navigate children**: Use `confluence_get_page_children` if needed
4. **Always include page URLs** in responses for reference
