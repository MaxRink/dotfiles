---
name: ai4dev-telecontext-raccoon
description: >-
  Query Raccoon/VictoriaMetrics monitoring data via Telecontext. Use when the user asks
  about API metrics, traffic, error rates, latency, bandwidth, service health, monitoring,
  PromQL queries, or Raccoon/TARDIS infrastructure metrics. Supports instant and range queries.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/raccoon by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Raccoon - API Monitoring & Metrics

Query Raccoon/VictoriaMetrics monitoring data for TARDIS infrastructure.

The user's query is: "$ARGUMENTS"

## Tools

### Query Tools
- `raccoon_instant_query` - Single point-in-time or aggregated totals. Use for: counts, totals, percentages, distributions, breakdowns, current values.
- `raccoon_range_query` - Time-series data over a range. Use for: trends, charts, patterns over time, "is traffic increasing?".

### Discovery Tools
- `raccoon_list_metrics` - List available metric names. Always start here if unsure what metrics exist.
- `raccoon_list_labels` - List available label names (dimensions): route, consumer, method, code, direction, service.
- `raccoon_list_label_values` - Get actual values for a label (e.g., all route names). Requires `label` param.
- `raccoon_mcp_server_status_overview` - Check server and VictoriaMetrics connectivity.

## Choosing instant vs range query

| User asks for... | Use |
|---|---|
| "total errors by status code" | `raccoon_instant_query` |
| "how many 404s yesterday?" | `raccoon_instant_query` |
| "current error rate" | `raccoon_instant_query` |
| "show traffic over time" | `raccoon_range_query` |
| "is traffic increasing?" | `raccoon_range_query` |
| "chart requests per hour" | `raccoon_range_query` |

## Key Metrics

- `mg_kong_eni_http_status_by_code_consumer_method_route:increase1m` - HTTP request counts
- `mg_kong_eni_bandwidth_by_consumer_route_direction:increase1m` - Bandwidth
- `mg_kong_eni_latency_*:increase1m` - Response time histograms
- `mg_kong_upstream_target_health_state_unhealthy_by_upstream` - Service health
- `mg_horizon_*:rate1m` - Horizon event system metrics

## Critical Rules

1. **NEVER use `rate()` with `:increase1m` or `:rate1m` metrics** - they are pre-aggregated. Using rate() causes double-aggregation and wrong results.
2. **For totals**: `sum(sum_over_time(metric:increase1m[1d:1m])) by (label)`
3. **Exclude gateway traffic**: Always add `consumer!~"gateway"` for real user data.
4. **Use 1m step** with `:increase1m` metrics for accurate data. Larger steps cause data loss (10m step = 90% data loss).
5. **Timestamps**: Always use RFC3339 format `"YYYY-MM-DDTHH:MM:SSZ"`, never Unix timestamps.
6. **Never use both `@` timestamp in query AND `time` parameter** - pick one.

## Environments

`playground` (default), `sit`, `cit2`, `cit4`, `preprod`, `prod`, `bond`, `av`, `rv`, `frv`

## Workflow

```
raccoon_list_metrics → discover available metrics
    ↓
raccoon_list_label_values(label="route") → find exact route names
    ↓
raccoon_instant_query / raccoon_range_query → execute PromQL query
```

## Debugging Zero Results

Zero results may be correct (no errors = good service). Only debug if you expect data:
1. Check date isn't in the future
2. Verify route name exactly (case-sensitive)
3. Try broader query first, then add filters
4. Don't loop endlessly - zero may be the right answer
