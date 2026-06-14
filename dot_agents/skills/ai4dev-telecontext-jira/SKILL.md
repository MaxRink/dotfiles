---
name: ai4dev-telecontext-jira
description: >-
  Interact with Jira via Telecontext. Use when the user wants to work with Jira issues,
  sprints, boards, epics, worklogs, or project management on DT-IT's Jira instance.
  Supports search (JQL), issue CRUD, sprint management, and agile boards.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/jira by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Jira Operations via Telecontext

Interact with DT-IT's Jira instance through Telecontext MCP tools.

The user's query is: "$ARGUMENTS"

## Available Tools

### Search & Read
- `jira_search` - Search issues using JQL. Key param: `jql` (required).
  JQL examples: `"status = 'In Progress' AND project = PROJ"`, `"assignee = currentUser()"`, `"updated >= -7d"`
- `jira_search_fields` - Find field names by keyword (useful for custom fields).
- `jira_get_issue` - Get issue details. Requires `issue_key` (e.g., "PROJ-123").
- `jira_get_project_issues` - Get all issues for a project. Requires `project_key`.
- `jira_get_user_profile` - Get user info by email/username.
- `jira_get_transitions` - Get available status transitions for an issue.
- `jira_get_worklog` - Get worklog entries for an issue.
- `jira_get_link_types` - List available issue link types.
- `jira_get_all_projects` - List all accessible projects.
- `jira_get_project_versions` - Get fix versions for a project.
- `jira_batch_get_changelogs` - Get changelogs for multiple issues.
- `jira_jira_get_issue_dates` - Get issue dates.
- `jira_jira_get_issue_sla` - Calculate SLA metrics (cycle time, lead time, time in status, resolution time, first response time). Requires `issue_key`.

### Agile / Sprints
- `jira_get_agile_boards` - Find boards by name/project/type.
- `jira_get_board_issues` - Get board issues filtered by JQL.
- `jira_get_sprints_from_board` - List sprints (filter by state: active/future/closed).
- `jira_get_sprint_issues` - Get issues in a sprint.

### Create & Modify
- `jira_create_issue` - Create issue. Requires `project_key`, `summary`, `issue_type`.
  Never assume project_key - always ask the user.
- `jira_batch_create_issues` - Batch create issues (JSON array).
- `jira_update_issue` - Update issue fields/attachments.
- `jira_delete_issue` - Delete an issue.
- `jira_add_comment` / `jira_edit_comment` - Manage comments (Markdown format).
- `jira_add_worklog` - Log time (e.g., "1h 30m", "1d").
- `jira_transition_issue` - Change issue status. Get transitions first with `jira_get_transitions`.
- `jira_link_to_epic` - Link issue to epic.
- `jira_create_issue_link` - Link two issues (Blocks, Relates to, etc.).
- `jira_create_remote_issue_link` - Add web/Confluence links to issues.
- `jira_remove_issue_link` - Remove a link.

### Sprint Management
- `jira_create_sprint` - Create sprint for a board.
- `jira_update_sprint` - Update sprint (name, state, dates, goal).

### Versions
- `jira_create_version` - Create fix version in a project.
- `jira_batch_create_versions` - Batch create versions.

## Auth

Requires **Personal Access Token** for Jira (NOT API Token). Configure in Teleconsole > Authorization Services.
If you get auth errors, verify you used the correct token type, then revoke and reconnect.
