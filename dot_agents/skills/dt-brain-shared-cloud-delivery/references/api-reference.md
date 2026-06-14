# GitLab Epics API Reference

Base URL: `https://gitlab.devops.telekom.de/api/v4`

## Authentication

All requests require a Personal Access Token:

```
PRIVATE-TOKEN: <your-token>
```

## Epics Endpoints

### List Group Epics

```
GET /groups/:id/epics
```

Parameters:
- `state` — opened, closed, all (default: all)
- `labels` — comma-separated label names
- `with_labels_details` — true/false (include label details)
- `author_id` — filter by author user ID
- `author_username` — filter by author username
- `search` — search in title and description
- `created_after` — return epics created after date (ISO 8601)
- `created_before` — return epics created before date
- `updated_after` — return epics updated after date (ISO 8601)
- `updated_before` — return epics updated before date
- `include_ancestor_groups` — include epics from ancestor groups
- `include_descendant_groups` — include epics from descendant groups (subgroups)
- `order_by` — created_at, updated_at, title (default: created_at)
- `sort` — asc, desc (default: desc)
- `per_page` — results per page (max 100)
- `page` — page number

Response fields:
```json
{
  "id": 1,
  "iid": 1,
  "group_id": 123,
  "title": "Epic Title",
  "description": "Epic description...",
  "state": "opened",
  "confidential": false,
  "author": {"id": 1, "username": "user", "name": "User Name"},
  "start_date": "2026-01-01",
  "start_date_is_fixed": true,
  "due_date": "2026-06-30",
  "due_date_is_fixed": true,
  "labels": ["label1", "label2"],
  "upvotes": 0,
  "downvotes": 0,
  "created_at": "2026-01-01T00:00:00.000Z",
  "updated_at": "2026-01-15T00:00:00.000Z",
  "closed_at": null,
  "web_url": "https://gitlab.devops.telekom.de/groups/cit-iaas/cid/-/epics/1"
}
```

### Get Single Epic

```
GET /groups/:id/epics/:epic_iid
```

Returns the same fields as list, plus:
- Full description
- `_links` with related resources

### List Epic Issues

```
GET /groups/:id/epics/:epic_iid/issues
```

Parameters:
- `per_page` — results per page (max 100)
- `page` — page number

Response fields:
```json
{
  "id": 1,
  "iid": 1,
  "project_id": 123,
  "title": "Issue Title",
  "description": "Issue description...",
  "state": "opened",
  "assignees": [{"id": 1, "username": "user", "name": "User Name"}],
  "labels": ["label1"],
  "milestone": {"id": 1, "title": "v1.0"},
  "due_date": "2026-03-15",
  "web_url": "https://gitlab.devops.telekom.de/cit-iaas/cid/project/-/issues/1"
}
```

## Labels Endpoints

### List Group Labels

```
GET /groups/:id/labels
```

Parameters:
- `with_counts` — true/false (include issue/MR counts)
- `include_ancestor_groups` — true/false (include labels from parent groups)
- `include_descendant_groups` — true/false (include labels from subgroups)
- `search` — filter labels by name
- `per_page` — results per page (max 100)
- `page` — page number

Response fields:
```json
{
  "id": 1,
  "name": "status::in-progress",
  "color": "#428BCA",
  "text_color": "#FFFFFF",
  "description": "Work is in progress",
  "description_html": "<p>Work is in progress</p>",
  "open_issues_count": 5,
  "closed_issues_count": 2,
  "open_merge_requests_count": 1,
  "subscribed": false
}
```

## python-gitlab Library

The scripts use the `python-gitlab` library which wraps these endpoints:

```python
import gitlab

gl = gitlab.Gitlab(url, private_token=token, ssl_verify=False)
gl.auth()

# Get group
group = gl.groups.get("cit-iaas/cid")

# List epics
epics = group.epics.list(
    state="opened",
    include_descendant_groups=True,
    per_page=50
)

# Get single epic
epic = group.epics.get(42)
epic.title, epic.state, epic.description
epic.start_date, epic.due_date
epic.labels, epic.author
epic.web_url

# List epic issues
issues = epic.issues.list(per_page=100)
for issue in issues:
    issue.title, issue.state, issue.assignees
    issue.labels, issue.due_date, issue.web_url

# List labels
labels = group.labels.list(
    include_ancestor_groups=True,
    include_descendant_groups=True,
    per_page=100
)
for label in labels:
    label.name, label.color, label.description
```

## Common Patterns

### Pagination

All list endpoints support pagination:

```python
# Get all results with automatic pagination
all_epics = group.epics.list(
    state="opened",
    include_descendant_groups=True,
    get_all=True  # python-gitlab handles pagination
)

# Or manual pagination
epics = group.epics.list(per_page=100, page=1)
```

### Date Filtering

Use ISO 8601 format for date filters:

```python
from datetime import datetime, timedelta

# Epics updated in last 30 days
cutoff = (datetime.now() - timedelta(days=30)).isoformat()
epics = group.epics.list(updated_after=cutoff)
```

### Label Filtering

Filter by labels (comma-separated for AND logic):

```python
# Epics with both labels
epics = group.epics.list(labels="status::in-progress,priority::high")

# Note: No OR logic via API, filter client-side if needed
```

## Error Handling

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized - invalid/missing token |
| 403 | Forbidden - insufficient permissions |
| 404 | Not Found - invalid group/epic |
| 429 | Too Many Requests - rate limited |
