# PagerDuty API Reference

## API Endpoints Used

### Incidents
- `GET /incidents` - List incidents
- `GET /incidents/{id}` - Get incident details
- `GET /incidents/{id}/log_entries` - Get incident timeline

### On-Call
- `GET /oncalls` - List current on-call assignments
- `GET /schedules` - List schedules
- `GET /schedules/{id}/users` - Get users on a schedule

### Services
- `GET /services` - List services
- `GET /services/{id}` - Get service details

### Teams
- `GET /teams` - List teams
- `GET /teams/{id}` - Get team details

## Authentication

All API requests require a token header:

```bash
-H "Authorization: Token token=${PAGERDUTY_TOKEN}"
```

## Common Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| team_ids[] | array | Filter by team IDs |
| service_ids[] | array | Filter by service IDs |
| since | datetime | Start of date range (ISO 8601) |
| until | datetime | End of date range (ISO 8601) |
| statuses[] | array | Filter by status: triggered, acknowledged, resolved |
| urgencies[] | array | Filter by urgency: high, low |
| limit | integer | Max results per page (default 25, max 100) |
| offset | integer | Pagination offset |

## Response Pagination

PagerDuty uses offset-based pagination:

```json
{
  "incidents": [...],
  "limit": 25,
  "offset": 0,
  "total": 150,
  "more": true
}
```

When `more` is `true`, increment `offset` by `limit` to get the next page.

## Date/Time Format

All dates use ISO 8601 format: `2025-01-26T10:30:00Z`

For shell scripts:

```bash
# macOS
date -v-24H +%Y-%m-%dT%H:%M:%SZ      # 24 hours ago
date -v-7d +%Y-%m-%dT%H:%M:%SZ       # 7 days ago
date -v-30d +%Y-%m-%dT%H:%M:%SZ      # 30 days ago

# Linux
date -d "24 hours ago" --iso-8601=seconds
date -d "7 days ago" --iso-8601=seconds
date -d "30 days ago" --iso-8601=seconds
```

## Incident Status Values

| Status | Description |
|--------|-------------|
| triggered | Incident is active and unacknowledged |
| acknowledged | Someone has acknowledged but not resolved |
| resolved | Incident has been resolved |

## Urgency Values

| Urgency | Description |
|---------|-------------|
| high | High urgency - immediate notification |
| low | Low urgency - may be batched/delayed |

## Error Response Format

```json
{
  "error": {
    "message": "Error description",
    "code": 2001,
    "errors": ["Additional error details"]
  }
}
```

## Rate Limits

PagerDuty applies rate limiting. If you receive HTTP 429, implement exponential backoff.

## API Documentation Links

- [PagerDuty API Reference](https://developer.pagerduty.com/api-reference)
- [REST API Overview](https://developer.pagerduty.com/docs/ZG9jOjExMDI5NTUw-rest-api-overview)
- [List Incidents](https://developer.pagerduty.com/api-reference/9d0b4b12e36f9-list-incidents)
- [List On-Calls](https://developer.pagerduty.com/api-reference/e1ad560792567-list-users-on-call)
