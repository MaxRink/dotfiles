# Troubleshooting Guide

## Common Errors

### "Tool not found" Errors
**Problem**: `Error calling tool 'confluence_search'`
**Solution**:
1. First use `mcp__Telecontext__search_tools` to find exact tool name
2. Use fully qualified tool names: `mcp__Telecontext__call_readonly_tool`

**Correct approach**:
```json
// Step 1: Find tool
{
  "tool_name": "mcp__Telecontext__search_tools",
  "tool_parameters": {"toolNameQuery": "confluence search"}
}

// Step 2: Use tool
{
  "tool_name": "mcp__Telecontext__call_readonly_tool",
  "tool_parameters": {
    "tool_name": "confluence_search",
    "tool_parameters": {"query": "VNRM architecture"}
  }
}
```

### Parameter Validation Errors
**Problem**: `Parameter validation failed: parent_id: Required`
**Cause**: Missing required parameters or incorrect parameter names
**Solution**: Check parameter schema with `shouldIncludeDetails: true`

**Example - Getting page children**:
```json
// Wrong - missing parent_id
{
  "tool_name": "confluence_get_page_children",
  "tool_parameters": {"page_id": "123"}
}

// Correct - use parent_id
{
  "tool_name": "confluence_get_page_children",
  "tool_parameters": {"parent_id": "123"}
}
```

### Empty Search Results
**Problem**: Search returns no results
**Troubleshooting steps**:
1. **Broaden search terms**: Start with "VNRM" only
2. **Check space access**: Ensure DHVOICE space is accessible
3. **Try alternative terms**: Use both English and German terms
4. **Use known page IDs**: Fall back to documented page IDs

**Progressive search approach**:
```json
// Start broad
{"query": "VNRM"}

// Add context
{"query": "VNRM architecture"}

// Get specific
{"query": "VNRM architecture DHVOICE inventory"}
```

## Page Access Issues

### Page Not Found
**Problem**: Page ID exists in search but `confluence_get_page` fails
**Solution**: Try alternative access methods or check permissions

### Incomplete Content
**Problem**: Page loads but content seems truncated
**Solution**: Check for child pages or attachments

```json
{
  "tool_name": "confluence_get_page_children",
  "tool_parameters": {
    "parent_id": "page_id_here",
    "include_content": true
  }
}
```

## Best Practices for Reliability

### 1. Tool Discovery First
Always discover tools before using them:
```json
{
  "tool_name": "mcp__Telecontext__search_tools",
  "tool_parameters": {
    "toolNameQuery": "confluence",
    "shouldIncludeDetails": true
  }
}
```

### 2. Parameter Validation
Use the parameter schema from tool discovery to ensure correct calls.

### 3. Fallback Strategies
- If search fails, try alternative queries
- If page access fails, try getting child pages
- Keep known working page IDs for common queries

### 4. Error Context
Always include enough context in error reports:
- What query was used
- What page ID was accessed
- What parameters were provided

## Known Working Examples

Use these as templates for reliable calls:

### Architecture Overview
```json
{
  "tool_name": "confluence_search",
  "tool_parameters": {"query": "VNRM architecture"}
}
```

### Inventory Relationships
```json
{
  "tool_name": "confluence_get_page",
  "tool_parameters": {"page_id": "3236856371"}
}
```

### Component Details
```json
{
  "tool_name": "confluence_get_page_children",
  "tool_parameters": {
    "parent_id": "2069758700",
    "include_content": true
  }
}
```
