# GitLab API v4 Reference

Base URL: `https://gitlab.devops.telekom.de/api/v4`

## Authentication

All requests require a Personal Access Token:

```
PRIVATE-TOKEN: <your-token>
```

## Key Endpoints

### Groups

**List group merge requests:**
```
GET /groups/:id/merge_requests
```
Parameters:
- `state` — opened, closed, merged, all
- `assignee_username` — filter by assignee
- `author_username` — filter by author
- `labels` — comma-separated label names
- `target_branch` — filter by target branch
- `include_subgroups` — true/false (include MRs from subgroup projects)
- `per_page` — results per page (max 100)
- `page` — page number

**Get group details:**
```
GET /groups/:id
```
`:id` can be the group path (URL-encoded): `cit%2Ft-caas`

### Projects

**Get project:**
```
GET /projects/:id
```
`:id` can be the project path (URL-encoded): `cit%2Ft-caas%2Fmy-repo`

### Merge Requests

**List project merge requests:**
```
GET /projects/:id/merge_requests
```

**Get single merge request:**
```
GET /projects/:id/merge_requests/:merge_request_iid
```

**Get MR approvals:**
```
GET /projects/:id/merge_requests/:merge_request_iid/approvals
```
Response:
- `approved` — boolean
- `approved_by` — list of users who approved

**Get MR changes (diff):**
```
GET /projects/:id/merge_requests/:merge_request_iid/changes
```

**List MR notes (comments):**
```
GET /projects/:id/merge_requests/:merge_request_iid/notes
```

**List MR pipelines:**
```
GET /projects/:id/merge_requests/:merge_request_iid/pipelines
```

**List jobs in a pipeline:**
```
GET /projects/:id/pipelines/:pipeline_id/jobs
```
Parameters:
- `per_page` — results per page (max 100)

**Get job trace/log:**
```
GET /projects/:id/jobs/:job_id/trace
```
Returns raw log content as text.

python-gitlab equivalents:
```python
# Get pipelines for an MR
mr = project.mergerequests.get(mr_iid)
pipelines = mr.pipelines.list(per_page=20)  # newest first

# Get jobs for a pipeline
pipeline = project.pipelines.get(pipeline_id)
jobs = pipeline.jobs.list(per_page=100, all=True)

# Get job log
job = project.jobs.get(job_id)
trace = job.trace()  # returns bytes, decode with .decode("utf-8", errors="replace")
```

### Repository Files

**List repository tree (files/directories):**
```
GET /projects/:id/repository/tree
```
Parameters:
- `path` — directory path (default: root)
- `ref` — branch, tag, or commit SHA (default: default branch)
- `recursive` — true/false (list files recursively)
- `per_page` — results per page (max 100)

**Get file from repository:**
```
GET /projects/:id/repository/files/:file_path
```
Parameters:
- `ref` — branch, tag, or commit SHA (required)

Response includes: `file_name`, `file_path`, `size`, `encoding`, `content` (base64), `content_sha256`

**Get raw file content:**
```
GET /projects/:id/repository/files/:file_path/raw
```
Parameters:
- `ref` — branch, tag, or commit SHA (default: default branch)

Returns raw file content directly.

### Search

**Search in project:**
```
GET /projects/:id/search
```
Parameters:
- `scope` — `blobs` (code), `commits`, `issues`, `merge_requests`, etc.
- `search` — search query
- `ref` — branch/tag to search in (for blobs scope)

**Search in group:**
```
GET /groups/:id/search
```
Same parameters as project search.

## python-gitlab Library

The scripts use the `python-gitlab` library which wraps these endpoints:

```python
import gitlab

gl = gitlab.Gitlab(url, private_token=token, ssl_verify=False)
gl.auth()

# Groups
group = gl.groups.get("cit/t-caas")
mrs = group.mergerequests.list(state="opened", include_subgroups=True)

# Projects
project = gl.projects.get("cit/t-caas/my-repo")
mr = project.mergerequests.get(42)

# MR details
mr.title, mr.state, mr.author, mr.assignees, mr.reviewers
mr.source_branch, mr.target_branch, mr.labels, mr.milestone
mr.pipeline, mr.web_url, mr.user_notes_count

# Approvals
approvals = mr.approvals.get()
approvals.approved, approvals.approved_by

# Repository tree
items = project.repository_tree(path="src", ref="main", recursive=False)
# Returns: [{"id": "...", "name": "file.py", "type": "blob", "path": "src/file.py", "mode": "100644"}, ...]

# File content
f = project.files.get(file_path="README.md", ref="main")
f.decode()  # Returns decoded content as bytes

# Raw file content
content = project.files.raw(file_path="README.md", ref="main")

# Search code in project
results = project.search(scope="blobs", search="def main")
# Returns: [{"basename": "main", "data": "...", "path": "src/main.py", "filename": "main.py", "ref": "main", "startline": 10}, ...]

# Search code in group
results = group.search(scope="blobs", search="class Handler")
```

## Rate Limits

GitLab enforces rate limits per user/token. Default is typically 300 requests per minute. The `--limit` flag in scripts helps avoid excessive API calls.
