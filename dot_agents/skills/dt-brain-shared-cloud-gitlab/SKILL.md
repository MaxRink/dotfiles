---
name: dt-brain-shared-cloud-gitlab
description: This skill should be used when the user mentions "GitLab", "merge request", "MR", "merge requests", "gitlab MRs", asks to "list MRs", "get MR details", "check merge requests", "review MRs", "list issues", "search issues", "list files", "repo files", "repository files", "get file", "file content", "code search", "search code", "browse repository", "epic", "epics", "list epics", "epic details", "epic issues", "issue details", "issue comments", "labels", "list labels", or needs to access merge request, epic, issue, or repository information from the Deutsche Telekom GitLab instance.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-gitlab by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# GitLab Integration

This skill provides tools to interact with the Deutsche Telekom GitLab instance for merge requests, epics, issues, labels, and repository operations.

## Instance Details

- **Base URL**: `https://gitlab.devops.telekom.de/`
- **API Version**: v4
- **Authentication**: Personal Access Token via `GITLAB_API_TOKEN`
- **VPN Required**: Yes - API access only works when connected to Telekom VPN
- **SSL Verification**: Disabled (internal certificate)

## IMPORTANT: Allowed Groups

Operations are **restricted** to these groups only (including subgroups):

| Group Path | Description |
|------------|-------------|
| `cit/t-caas` | CIT T-CaaS group |
| `tdi-caas` | TDI CaaS group |
| `cit-iaas/cid` | CIT IaaS Cloud Infrastructure Delivery group |

All scripts validate the group/project path and will refuse operations on groups/projects outside this list.

## Authentication Setup

Set the environment variable before using any GitLab operations:

```bash
export GITLAB_API_TOKEN="your-personal-access-token"
```

To get a PAT:
1. Log in to GitLab at https://gitlab.devops.telekom.de/
2. Go to User Settings > Access Tokens
3. Create a token with `read_api` scope

## Operations

### List Merge Requests

List merge requests from a group (includes subgroups):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group <group-path> [options]
```

Options:
- `--group GROUP` (required) - Group path (e.g., `cit/t-caas`, `tdi-caas`)
- `--state STATE` - Filter by state: `opened` (default), `closed`, `merged`, `all`
- `--assignee USERNAME` - Filter by assignee username
- `--author USERNAME` - Filter by author username
- `--labels LABELS` - Filter by comma-separated labels
- `--target-branch BRANCH` - Filter by target branch
- `--updated-after DATE` - Only MRs updated after this date (ISO format, e.g. `2026-01-01`)
- `--created-after DATE` - Only MRs created after this date (ISO format, e.g. `2026-01-01`)
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 50)

Examples:
```bash
# List open MRs in cit/t-caas group
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas

# Filter by author with date range
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --author john.doe --updated-after 2026-01-01

# List merged MRs as JSON
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group tdi-caas --state merged --format json --limit 10
```

Output shows: IID, Project, Title, Author, Assignee, State, Target Branch, Created

JSON output also includes: `merged_at` (date the MR was merged, if applicable)

### Get Merge Request Details

Get detailed information about a specific merge request:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py <project-path> <mr-iid> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit/t-caas/my-repo`)
- `mr_iid` (positional) - Merge request number

Options:
- `--format FORMAT` - Output format: `detailed` (default), `json`

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py cit/t-caas/my-repo 42
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py cit/t-caas/my-repo 42 --format json
```

Output includes: Title, state, draft status, branches, merge status, author, assignees, reviewers, approvals, pipeline, labels, milestone, dates, description, web URL

## Epic Operations

### List Epics

List epics from a group (includes subgroups):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-epics.py <group-path> [options]
```

Arguments:
- `group` (positional) - Group path (e.g., `cit-iaas/cid`, `cit/t-caas`)

Options:
- `--state STATE` - Filter by state: `opened` (default), `closed`, `all`
- `--labels LABELS` - Filter by comma-separated labels
- `--author USERNAME` - Filter by author username
- `--search TEXT` - Search in title and description
- `--updated-after DATE` - Only epics updated after this date (ISO format)
- `--created-after DATE` - Only epics created after this date (ISO format)
- `--sort-by FIELD` - Sort results by: `due_date`, `created_at`, `updated_at`, `title`
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 50)

Examples:
```bash
# List open epics
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-epics.py cit-iaas/cid

# Filter by labels, sorted by due date
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-epics.py cit-iaas/cid --labels "A - CaaS_squad" --sort-by due_date

# Search with JSON output
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-epics.py cit-iaas/cid --search "Budapest" --format json --limit 100
```

Output shows: IID, Title, State, Start Date, Due Date, Labels

### Get Epic Details

Get detailed information about a specific epic:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-epic.py <group-path> <epic-iid> [options]
```

Arguments:
- `group` (positional) - Group path (e.g., `cit-iaas/cid`)
- `epic_iid` (positional) - Epic IID number

Options:
- `--format FORMAT` - Output format: `detailed` (default), `json`

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-epic.py cit-iaas/cid 42
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-epic.py cit-iaas/cid 42 --format json
```

Output includes: Title, state, confidentiality, hierarchy info (parent/children), dates, author, labels, issues count, description, web URL

### List Epic Issues

List all issues linked to an epic:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-epic-issues.py <group-path> <epic-iid> [options]
```

Arguments:
- `group` (positional) - Group path (e.g., `cit-iaas/cid`)
- `epic_iid` (positional) - Epic IID number

Options:
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 100)

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-epic-issues.py cit-iaas/cid 922
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-epic-issues.py cit-iaas/cid 922 --format json
```

Output shows: IID, Project, Title, State, Assignee, Labels, Due Date

## Issue Operations

### List Issues

List issues from a group (includes subgroups):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-issues.py <group-path> [options]
```

Arguments:
- `group` (positional) - Group path (e.g., `cit-iaas/cid`, `cit/t-caas`)

Options:
- `--state STATE` - Filter by state: `opened` (default), `closed`, `all`
- `--labels LABELS` - Filter by comma-separated labels
- `--assignee NAME` - Filter by assignee (supports partial name search with interactive selection)
- `--author USERNAME` - Filter by author username
- `--search TEXT` - Search in title and description
- `--updated-after DATE` - Only issues updated after this date (ISO format)
- `--created-after DATE` - Only issues created after this date (ISO format)
- `--sort-by FIELD` - Sort results by: `due_date`, `created_at`, `updated_at`, `title`
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 50)

Examples:
```bash
# List open issues with label filter
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-issues.py cit-iaas/cid --labels "A - CaaS_squad"

# Filter by assignee (fuzzy name search)
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-issues.py cit-iaas/cid --assignee "Angel" --sort-by due_date

# Search with JSON output
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-issues.py cit/t-caas --search "migration" --format json --limit 100
```

**Assignee Filter**: The `--assignee` option searches group members by partial name (e.g., "Angel" matches "Angel Vivas-Vivas"). If multiple matches are found, prompts for interactive selection.

Output shows: IID, Project, Title, State, Assignee, Due Date

### Get Issue Details

Get detailed information about a specific issue:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue.py <project-path> <issue-iid> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit-iaas/cid/caas-devops`)
- `issue_iid` (positional) - Issue IID number

Options:
- `--format FORMAT` - Output format: `detailed` (default), `json`

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue.py cit-iaas/cid/caas-devops 124
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue.py cit-iaas/cid/caas-devops 124 --format json
```

Output includes: Title, state, author, assignees, labels, milestone, due date, dates, comments count, description, web URL

### Get Issue Comments

List comments/notes on an issue:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue-comments.py <project-path> <issue-iid> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit-iaas/cid/caas-devops`)
- `issue_iid` (positional) - Issue IID number

Options:
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum comments (default: 50)
- `--sort ORDER` - Sort order: `asc` (default, oldest first), `desc`
- `--include-system` - Include system notes (title/label/date changes)

Examples:
```bash
# User comments only
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue-comments.py cit-iaas/cid/caas-devops 124

# Include system notes, newest first
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-issue-comments.py cit-iaas/cid/caas-devops 124 --include-system --sort desc
```

Output shows: Author, Date, Comment body

## Label Operations

### List Labels

List labels in a group to discover label conventions:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-labels.py <group-path> [options]
```

Arguments:
- `group` (positional) - Group path (e.g., `cit-iaas/cid`)

Options:
- `--search TEXT` - Filter labels by name
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 100)

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-labels.py cit-iaas/cid
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-labels.py cit-iaas/cid --search "status"
```

Output shows: Name, Color, Description

## Pipeline Operations

### Inspect MR Pipelines

Inspect pipelines for an MR. **Automatically focuses on the latest failed pipeline**, shows all jobs and the logs of failed jobs to help diagnose issues:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py <project-path> <mr-iid> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit/t-caas/my-repo`)
- `mr_iid` (positional) - Merge request IID number

Options:
- `--pipeline-id ID` - Inspect a specific pipeline by ID (default: auto-selects latest failed, or latest if none failed)
- `--list-only` - Only list pipelines, skip job/log inspection
- `--no-logs` - Show jobs but skip log output for failed jobs
- `--log-lines N` - Number of log lines to show per failed job (default: 80)
- `--format FORMAT` - Output format: `table` (default), `json`

Examples:
```bash
# Inspect the latest failed pipeline and show failed job logs (most common use case)
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py cit/t-caas/my-repo 42

# Just list all pipelines without inspecting jobs
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py cit/t-caas/my-repo 42 --list-only

# Inspect a specific pipeline
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py cit/t-caas/my-repo 42 --pipeline-id 12345

# Show jobs only, no logs
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py cit/t-caas/my-repo 42 --no-logs

# More log context for complex failures
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr-pipelines.py cit/t-caas/my-repo 42 --log-lines 150
```

Output:
1. **Pipelines list** — all pipelines for the MR with status, ref, SHA, date
2. **Jobs table** — all jobs in the selected pipeline: stage, name, status, duration
3. **Failed job logs** — last N lines of log for each failed job (auto-shown unless `--no-logs`)

## Repository File Operations

### List Files/Directories

List files and directories in a repository (like `ls`):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py <project-path> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit/t-caas/my-repo`)

Options:
- `--path PATH` - Directory path within the repository (default: root)
- `--ref REF` - Branch, tag, or commit SHA (default: default branch)
- `--recursive` - List files recursively
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 100)

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo --path src/ --ref develop --recursive
```

Output shows: Type (📁 dir / 📄 file), Name, Path

### Get File Content

Read file content from a repository (like `cat`):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py <project-path> --path <file-path> [options]
```

Arguments:
- `project` (positional) - Full project path (e.g., `cit/t-caas/my-repo`)
- `--path PATH` (required) - File path within the repository

Options:
- `--ref REF` - Branch, tag, or commit SHA (default: default branch)
- `--format FORMAT` - Output format: `raw` (default), `json`

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path README.md
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path src/main.py --ref develop
```

Notes:
- Binary files (images, archives, etc.) show metadata only, not content
- Files larger than 1MB show metadata only

### Search Code

Search for patterns in repository code (like `grep`):

```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --query <search-term> [--project <path> | --group <path>] [options]
```

Options:
- `--project PROJECT` - Project path to search in (e.g., `cit/t-caas/my-repo`)
- `--group GROUP` - Group path to search across all projects (e.g., `cit/t-caas`)
- `--query QUERY` (required) - Search query/pattern
- `--ref REF` - Branch, tag, or commit SHA (only for project search)
- `--format FORMAT` - Output format: `table` (default), `json`
- `--limit N` - Maximum results (default: 50)

Note: Either `--project` or `--group` must be specified, but not both.

Examples:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --project cit/t-caas/my-repo --query "def main"
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --group cit/t-caas --query "class Handler" --limit 20
```

Output shows: File path, Line number, Match preview

## Tips & Reporting

- **Most MRs have no assignee** — use `--author` instead of `--assignee` when filtering by person
- **`merged_at` in JSON** — useful for tracking when MRs were completed
- **Date filtering** — use `--updated-after`/`--created-after` to narrow to time windows
- **PDF reports** — fetch MRs as JSON, process into markdown, then use cloud-pdf skill
- **Two tokens available**: `GITLAB_API_TOKEN` (read_api scope) is required for all read operations. `GITLAB_API_TOKEN_RW` (api scope) is optional — only needed when performing write operations (posting comments, resolving threads, triggering bot reviews).
- **MR comments/notes via API**: The skill scripts only support read operations. For write operations (posting comments, replying to threads, resolving discussions), use the GitLab API directly with `GITLAB_API_TOKEN_RW`.
- **StabilityBot**: Most projects use StabilityBot for automatic code review. It runs automatically when an MR is created. You can also trigger a manual review by posting `/stabilitybot review` as an MR comment. Bot comments are resolvable discussion threads.

## Direct API Operations (Write)

For operations not covered by the skill scripts, use the GitLab API directly with `GITLAB_API_TOKEN_RW`.

### Post a Comment on an MR

```python
import requests, urllib.parse, os
token = os.environ['GITLAB_API_TOKEN_RW']
base = 'https://gitlab.devops.telekom.de/api/v4'
project = urllib.parse.quote('cit/t-caas/my-repo', safe='')

r = requests.post(
    f'{base}/projects/{project}/merge_requests/{mr_iid}/notes',
    headers={'PRIVATE-TOKEN': token},
    verify=False,
    json={'body': 'Your comment here'}
)
```

### List Discussion Threads on an MR

```python
r = requests.get(
    f'{base}/projects/{project}/merge_requests/{mr_iid}/discussions',
    headers={'PRIVATE-TOKEN': token},
    verify=False,
    params={'per_page': 100}
)
# Each discussion has: id, notes[], notes[0].resolvable, notes[0].resolved
```

### Reply to a Discussion Thread and Resolve It

```python
discussion_id = 'd18d007de537...'

# Reply
requests.post(
    f'{base}/projects/{project}/merge_requests/{mr_iid}/discussions/{discussion_id}/notes',
    headers={'PRIVATE-TOKEN': token},
    verify=False,
    json={'body': 'Fixed in commit abc123'}
)

# Resolve the thread
requests.put(
    f'{base}/projects/{project}/merge_requests/{mr_iid}/discussions/{discussion_id}',
    headers={'PRIVATE-TOKEN': token},
    verify=False,
    json={'resolved': True}
)
```

### Trigger StabilityBot Review

Post `/stabilitybot review` as an MR comment (requires write token):

```python
requests.post(
    f'{base}/projects/{project}/merge_requests/{mr_iid}/notes',
    headers={'PRIVATE-TOKEN': token},
    verify=False,
    json={'body': '/stabilitybot review'}
)
```

### Important Notes for API Operations

- **Cannot edit other users' notes** — editing bot comments returns 403; post a reply instead
- **Discussion threads** have a `discussion_id` (string hash), different from `note_id` (integer)
- **Resolvable threads** are code review comments; regular MR comments are not resolvable
- **SSL verification disabled** (`verify=False`) required for internal certificate
- **URL-encode project path** — `cit/t-caas/t-co` → `cit%2Ft-caas%2Ft-co`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `GITLAB_API_TOKEN not set` | Missing environment variable | `export GITLAB_API_TOKEN="your-token"` |
| `Group 'x' is not allowed` | Group not in allowed list | Use `cit/t-caas` or `tdi-caas` |
| `Project 'x' is not in an allowed group` | Project outside allowed groups | Ensure project is under an allowed group |
| `Failed to initialize GitLab client` | Not on VPN or bad token | Connect to VPN, check token |
| `Failed to get group` | Group path incorrect | Verify group path on GitLab |
| `File 'x' not found in project` | File path incorrect or doesn't exist | Verify file path exists |
| `File too large` | File exceeds 1MB limit | Use git clone for large files |

## Security Notes

1. **Token Storage**: Never commit `GITLAB_API_TOKEN` to version control
2. **VPN Required**: Operations only work when connected to Telekom VPN
3. **Read-Only by Default**: Skill scripts use read-only API calls (`read_api` scope). Write operations require `GITLAB_API_TOKEN_RW` (`api` scope)
4. **Group Restriction**: Scripts enforce group allowlist to prevent unauthorized access
5. **SSL Verification**: Disabled for internal certificate - only use on trusted networks

## Additional Resources

- [references/api-reference.md](references/api-reference.md) — GitLab API v4 endpoints and python-gitlab library usage. Consult when debugging API calls or making raw requests.
