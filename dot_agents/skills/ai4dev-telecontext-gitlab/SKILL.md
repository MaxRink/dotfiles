---
name: ai4dev-telecontext-gitlab
description: >-
  Interact with GitLab via Telecontext. Use when the user wants to work with GitLab
  projects, issues, merge requests, epics, branches, commits, pipelines, wikis, or groups
  on the DT-IT GitLab instance. Supports both read and write operations.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/gitlab by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# GitLab Operations via Telecontext

Interact with DT-IT's GitLab instance through Telecontext MCP tools.

The user's query is: "$ARGUMENTS"

## Available Tools

### Repository & Metadata
- `gitlab_get_metadata` - Get GitLab server version
- `gitlab_branch_list` - List branches (search, regex filter). Requires `projectId`.
- `gitlab_commit_list` - List commits (filter by date, author, path). Requires `projectId`.
- `gitlab_commit_get` - Get specific commit details. Requires `projectId`, `sha`.
- `gitlab_commit_compare` - Compare two commits/branches. Requires `projectId`, `from`, `to`.

### Pipelines & Jobs
- `gitlab_pipeline_list` - List pipelines with filters (status, ref, sha, username). Requires `projectId`.
- `gitlab_pipeline_get` - Get pipeline details. Requires `projectId`, `pipelineId`.
- `gitlab_pipeline_start` - Start a new pipeline. Requires `projectId`, `ref` (branch/tag). Optional: `variables` array.
- `gitlab_pipeline_retry` - Retry failed/canceled jobs in a pipeline. Requires `projectId`, `pipelineId`.
- `gitlab_pipeline_job_list` - List jobs in a project (filter by `pipelineId`, `scope`). Requires `projectId`.
- `gitlab_pipeline_job_get` - Get job details. Requires `projectId`, `jobId`.
- `gitlab_pipeline_job_retry` - Retry a specific job. Requires `projectId`, `jobId`.
- `gitlab_pipeline_job_log` - Get job trace/log output. Requires `projectId`, `jobId`.

### Issues
- `gitlab_issue_list` - List issues with filters. Requires `projectId`.
- `gitlab_issue_get` - Get issue details. Requires `projectId`, `issueIid`.
- `gitlab_issue_create` - Create issue. Requires `projectId`, `title`.
- `gitlab_issue_update` - Update issue. Requires `projectId`, `issueIid`.
- `gitlab_issue_comment_list` - List issue comments.
- `gitlab_issue_comment_create` - Add comment to issue.

### Merge Requests
- `gitlab_merge_request_list` - List MRs with filters. Requires `projectId`.
- `gitlab_merge_request_get` - Get MR details. Requires `projectId`, `mergeRequestIid`.
- `gitlab_merge_request_create` - Create MR. Requires `projectId`, `sourceBranch`, `targetBranch`, `title`.
- `gitlab_merge_request_update` - Update MR.
- `gitlab_merge_request_approve` / `_unapprove` - Approve/unapprove MR.
- `gitlab_merge_request_merge` - Merge MR.
- `gitlab_merge_request_discussion_list` / `_create` / `_note_add` / `_resolve` - MR discussions.

### Epics
- `gitlab_epic_list` / `_get` / `_create` / `_update` / `_delete` - Epic CRUD. Requires `groupId`.
- `gitlab_epic_issues` - List issues in an epic.
- `gitlab_epic_comment_list` / `_comment_create` - Epic comments.

### Groups
- `gitlab_group_list` / `_get` / `_subgroup_list` / `_project_list` - Group operations.

### Wiki
- `gitlab_wiki_list` - List wiki pages. Requires `projectId`.
- `gitlab_wiki_get` - Get wiki page content. Requires `projectId`, `slug`.
- `gitlab_wiki_create` - Create wiki page. Requires `projectId`, `title`, `content`.
- `gitlab_wiki_update` - Update wiki page. Requires `projectId`, `slug`.

## Key Parameters

- `projectId`: Can be numeric ID or URL-encoded path (e.g., `"group/subgroup/project"`)
- `groupId`: Can be numeric ID or URL-encoded path
- Pagination: Most list tools support `page` and `perPage` (max 100)

## Auth

Requires GitLab authentication via Telecontext. If you get auth errors, check your token in Teleconsole > Authorization Services.
