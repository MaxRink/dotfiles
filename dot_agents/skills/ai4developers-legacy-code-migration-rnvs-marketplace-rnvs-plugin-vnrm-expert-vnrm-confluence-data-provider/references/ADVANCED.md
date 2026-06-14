# Advanced Usage Guide

## Tool Discovery

Always start by finding the exact tool name:
```json
{
  "tool_name": "mcp__Telecontext__search_tools",
  "tool_parameters": {
    "toolNameQuery": "confluence",
    "limit": 5,
    "shouldIncludeDetails": true
  }
}
```

## Page Navigation Workflow

### 1. Search for Pages
```json
{
  "tool_name": "confluence_search",
  "tool_parameters": {
    "query": "VNRM architecture DHVOICE inventory"
  }
}
```

### 2. Get Main Page Content
```json
{
  "tool_name": "confluence_get_page",
  "tool_parameters": {
    "page_id": "2069758700"
  }
}
```

### 3. Get Child Pages
```json
{
  "tool_name": "confluence_get_page_children",
  "tool_parameters": {
    "parent_id": "2069758700",
    "include_content": true,
    "limit": 50
  }
}
```

## Query Optimization

### Effective Queries
- "VNRM architecture DHVOICE inventory" - Finds inventory relationships
- "NUM NUMBERMANAGEMENT VNRM" - Finds number management components
- "PRT porting management VNRM" - Finds porting system info
- "VNRM business object model" - Finds BOM documentation

### Query Construction Tips
1. **Include space filter implicitly**: Add "DHVOICE" to queries
2. **Use both abbreviations and full names**: "NUM" and "Number Management"
3. **Combine architectural concepts**: "architecture", "design", "specification"
4. **Include German terms when relevant**: "Portierung", "Rufnummer"

## Data Extraction Patterns

### Page Content Analysis
1. **Read metadata first**: Check page title, space, version
2. **Extract attachments**: Look for diagrams and documentation
3. **Follow child pages**: Architecture often spans multiple pages
4. **Check for tables**: Inventory relationships often in tabular format

### Content Types to Look For
- **PlantUML diagrams**: Architecture visualizations
- **Tables**: Inventory relationships, use cases
- **Process flows**: Sequence diagrams, activity flows
- **Configuration examples**: API calls, data structures

## Performance Tips

1. **Use specific searches**: Avoid overly broad queries
2. **Limit results appropriately**: Don't request more than needed
3. **Cache page IDs**: Reuse known page IDs for follow-up requests
4. **Progressive loading**: Get overview first, then dive into details
