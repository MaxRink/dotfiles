# Telekom Jira Custom Field Mappings

This document provides complete documentation of the custom fields used in the Telekom Jira instance.

## Date Fields

### Target Start Date
- **Field ID**: `customfield_21920`
- **Script Flag**: `--target-start`
- **Type**: Date
- **Format**: `YYYY-MM-DD` (e.g., `2025-02-01`)
- **Description**: The planned start date for work on this issue
- **API Usage**:
  ```json
  {
    "fields": {
      "customfield_21920": "2025-02-01"
    }
  }
  ```

### Target End Date
- **Field ID**: `customfield_21921`
- **Script Flag**: `--target-end`
- **Type**: Date
- **Format**: `YYYY-MM-DD` (e.g., `2025-02-28`)
- **Description**: The planned completion date for this issue
- **API Usage**:
  ```json
  {
    "fields": {
      "customfield_21921": "2025-02-28"
    }
  }
  ```

## Epic Fields

### Epic Link
- **Field ID**: `customfield_17615`
- **Script Flag**: `--epic`
- **Type**: String (HTML format in responses)
- **Description**: Links an issue to a parent Epic
- **Response Format**: HTML with title attribute: `<a title='Epic Name' href='...'>EPIC-123</a>`
- **API Usage** (when setting):
  ```json
  {
    "fields": {
      "customfield_17615": "TCAAS-100"
    }
  }
  ```
- **Parsing Epic Name from Response**:
  ```python
  import re
  epic_html = fields.get('customfield_17615', '')
  match = re.search(r"title='([^']+)'", epic_html)
  epic_name = match.group(1) if match else None
  ```

### Epic Status
- **Field ID**: `customfield_10014`
- **Type**: Select
- **Values**: "undefiniert" (undefined), "In Progress", "Done"
- **Description**: Indicates the completion status of an Epic

## Sprint Field

### Sprint
- **Field ID**: `customfield_12810`
- **Type**: Array of Sprint objects
- **Description**: Contains sprint assignment data
- **Response Format**: Complex array with sprint details
- **Note**: Read-only in most cases; sprint assignment is typically done through Jira's sprint board

## Standard Fields Reference

These standard fields are also commonly used:

| Field | API Name | Type | Example |
|-------|----------|------|---------|
| Summary | `summary` | String | "Implement feature X" |
| Description | `description` | String | "Detailed description..." |
| Issue Type | `issuetype` | Object | `{"name": "Task"}` |
| Status | `status` | Object | `{"name": "In Progress"}` (read-only) |
| Priority | `priority` | Object | `{"name": "High"}` |
| Assignee | `assignee` | Object | `{"name": "username"}` |
| Reporter | `reporter` | Object | `{"name": "username"}` (read-only) |
| Labels | `labels` | Array | `["label1", "label2"]` |
| Fix Versions | `fixVersions` | Array | `[{"name": "25.12"}]` |
| Due Date | `duedate` | Date | "2025-03-15" |
| Created | `created` | DateTime | (read-only) |
| Updated | `updated` | DateTime | (read-only) |

## Issue Type Mapping

| Issue Type | Description |
|------------|-------------|
| Task | General work item |
| Bug | Defect to be fixed |
| Story | User story for features |
| Epic | Large initiative containing multiple stories/tasks |
| Sub-task | Child task under a parent issue |
| Improvement | Enhancement to existing functionality |
| New Feature | Brand new functionality |
| Support | Support request |

## Complete Create Issue Example

```json
{
  "fields": {
    "project": {"key": "TCAAS"},
    "issuetype": {"name": "Task"},
    "summary": "Implement user authentication",
    "description": "Add OAuth2 authentication to the API",
    "labels": ["tdi-caas-convergence", "security"],
    "assignee": {"name": "javier.esteve-sole"},
    "priority": {"name": "High"},
    "customfield_21920": "2025-02-01",
    "customfield_21921": "2025-02-15",
    "fixVersions": [{"name": "25.12"}],
    "customfield_17615": "TCAAS-100"
  }
}
```

## Complete Update Issue Example

```json
{
  "fields": {
    "summary": "Updated summary",
    "customfield_21920": "2025-02-10"
  },
  "update": {
    "labels": [
      {"add": "new-label"},
      {"remove": "old-label"}
    ]
  }
}
```
