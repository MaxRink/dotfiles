---
name: tdi-cloudbrain-gitlab
user-invocable: true
description: This skill should be used when the user mentions "GitLab", "merge request", "MR", "merge requests", "gitlab MRs", asks to "list MRs", "get MR details", "check merge requests", "review MRs", "list files", "repo files", "repository files", "get file", "file content", "code search", "search code", "browse repository", or needs to access merge request information or repository files from the Deutsche Telekom GitLab instance.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/gitlab by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# GitLab Integration

This skill provides tools to interact with the Deutsche Telekom GitLab instance for merge request operations.

## Table of Contents

- [Instance Details](#instance-details)
- [Allowed Groups](#important-allowed-groups)
- [Authentication Setup](#authentication-setup)
- [Operations](#operations)
  - [List Merge Requests](#list-merge-requests)
  - [Get Merge Request Details](#get-merge-request-details)
- [Repository File Operations](#repository-file-operations)
  - [List Files/Directories](#list-filesdirectories)
  - [Get File Content](#get-file-content)
  - [Search Code](#search-code)
- [Reporting Examples](#reporting-examples)
- [Error Handling](#error-handling)
- [Session Learnings](#session-learnings)
- [Security Notes](#security-notes)

## Instance Details

- **Base URL**: `https://gitlab.devops.telekom.de/`
- **API Version**: v4
- **Authentication**: Personal Access Token via `GITLAB_API_TOKEN`
- **VPN Required**: Yes - API access only works when connected to Telekom VPN
- **SSL Verification**: Disabled (internal certificate)

## IMPORTANT: Allowed Groups

Operations are restricted to the configured groups (including subgroups).
Default values (used when no config is set) are shown below.

| Group Path | Description |
|------------|-------------|
| `cit/t-caas` | CIT T-CaaS group (default) |
| `tdi-caas` | TDI CaaS group (default) |

All scripts validate the group/project path and will refuse operations on groups/projects outside this list.

## Configuration

This skill reads team-specific settings from `cloudbrain.yaml` (via `CLOUDBRAIN_CONFIG` env var).

| Setting | Env Variable | Config Key | Default |
|---------|-------------|------------|---------|
| Allowed groups | `GITLAB_GROUPS` | `gitlab.groups` | `cit/t-caas, tdi-caas` |

Priority: Environment variable → `cloudbrain.yaml` → built-in default.

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

# List merged MRs
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --state merged

# Filter by author
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --author john.doe

# Filter by assignee and target branch
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group tdi-caas --assignee jane.smith --target-branch main

# List with labels filter
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --labels "bug,urgent"

# Limit results and get JSON
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --limit 10 --format json
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
# Get MR details
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py cit/t-caas/my-repo 42

# Get JSON output
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py cit/t-caas/my-repo 42 --format json

# Get MR from subgroup project
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-mr.py cit/t-caas/sub/project 15
```

Output includes:
- Title, state, draft status
- Source and target branches, merge status
- Author, assignees, reviewers
- Approvals (approved status, approved by)
- Pipeline status and URL
- Labels, milestone
- Dates (created, updated, merged, closed)
- Comments count, upvotes/downvotes
- Description
- Web URL

## Session Learnings

- **Most MRs have no assignee**: The `assignee` field is empty for most merge requests. Use `--author` instead of `--assignee` when filtering by person.
- **`merged_at` available in JSON**: The JSON output includes a `merged_at` date field for merged MRs, useful for reporting on when work was completed.
- **Date filtering**: Use `--updated-after` and `--created-after` to narrow results to a specific time window (e.g. monthly reports).

## Reporting Examples

### Monthly MR report (JSON for processing)
```bash
# Get all merged MRs updated in January 2026
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --state merged --updated-after 2026-01-01 --limit 200 --format json
```

### Filter by author
```bash
# Get a specific author's merged MRs
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --state merged --author john.doe --updated-after 2026-01-01 --format json
```

### Pipe to telekom-pdf skill
To generate a PDF report from MR data, first fetch MRs as JSON, process them into a markdown file, then use the telekom-pdf skill:
```bash
# 1. Fetch MR data
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-mrs.py --group cit/t-caas --state merged --updated-after 2026-01-01 --limit 200 --format json > /tmp/mrs.json

# 2. Process into markdown (with Claude or jq), then generate PDF
${PDF_SKILL_DIR}/scripts/generate-pdf.py --markdown /tmp/report.md --title "Monthly MR Report" --output docs/mr-report.pdf
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `GITLAB_API_TOKEN not set` | Missing environment variable | `export GITLAB_API_TOKEN="your-token"` |
| `Group 'x' is not allowed` | Group not in allowed list | Use `cit/t-caas` or `tdi-caas` |
| `Project 'x' is not in an allowed group` | Project outside allowed groups | Ensure project is under an allowed group |
| `Failed to initialize GitLab client` | Not on VPN or bad token | Connect to VPN, check token |
| `Failed to get group` | Group path incorrect | Verify group path on GitLab |
| `File 'x' not found in project` | File path incorrect or doesn't exist | Verify file path exists |
| `Path 'x' not found in project` | Directory path incorrect | Verify directory path |
| `File too large` | File exceeds 1MB limit | Use git clone for large files |

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
# List root directory
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo

# List specific directory
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo --path src/

# List with specific branch
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo --path src/ --ref develop

# Recursive listing
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo --recursive --path src/

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-list-files.py cit/t-caas/my-repo --format json
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
# Get file from default branch
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path README.md

# Get file from specific branch
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path src/main.py --ref develop

# Get file from specific commit
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path config.yaml --ref abc123def

# Get with metadata (JSON)
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-get-file.py cit/t-caas/my-repo --path src/main.py --format json
```

Notes:
- Binary files (images, archives, etc.) show metadata only, not content
- Files larger than 1MB show metadata only
- JSON format includes: file_name, file_path, size, ref, encoding, content_sha256, last_commit_id, content

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
# Search in a specific project
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --project cit/t-caas/my-repo --query "def main"

# Search across a group (all projects)
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --group cit/t-caas --query "class Handler"

# Search in specific branch
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --project cit/t-caas/my-repo --query "TODO" --ref develop

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --project cit/t-caas/my-repo --query "import os" --format json

# Limit results
.venv/bin/python ${SKILL_DIR}/scripts/gitlab-search-code.py --group tdi-caas --query "kubernetes" --limit 20
```

Output shows: File path, Line number, Match preview

## Security Notes

1. **Token Storage**: Never commit `GITLAB_API_TOKEN` to version control
2. **VPN Required**: Operations only work when connected to Telekom VPN
3. **Read-Only**: All operations use read-only API calls (`read_api` scope)
4. **Group Restriction**: Scripts enforce group allowlist to prevent unauthorized access
5. **SSL Verification**: Disabled for internal certificate - only use on trusted networks
