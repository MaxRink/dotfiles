# Gantt Charts

For project schedules, timelines, and dependency tracking.

## Syntax

```mermaid
gantt
  title Project Timeline
  dateFormat YYYY-MM-DD
  axisFormat %b %d
  excludes weekends

  section Design
    Requirements    :done, a1, 2024-01-01, 14d
    Architecture    :active, a2, after a1, 10d
  section Development
    Backend         :b1, after a2, 30d
    Frontend        :b2, after a2, 25d
  section Testing
    Integration     :crit, c1, after b1, 10d
    UAT             :milestone, c2, after c1, 0d
```

**Tags:** `done`, `active`, `crit`, `milestone`
**Dependencies:** `after taskId`
**Duration:** `14d` (days), or explicit end date
**Excludes:** `weekends`, specific dates `YYYY-MM-DD`, weekday names
