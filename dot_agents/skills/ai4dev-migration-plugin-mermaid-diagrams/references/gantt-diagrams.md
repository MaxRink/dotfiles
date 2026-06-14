# Gantt Charts

Gantt charts visualize project timelines, task dependencies, and schedules. Ideal for migration planning, release schedules, and sprint planning.

> **NEVER use literal `\n`** — use `<br>` for multi-line labels.

## Contents

- [Basic Syntax](#basic-syntax)
- [Date Formats](#date-formats)
- [Task Syntax](#task-syntax)
- [Task Tags](#task-tags)
- [Dependencies](#dependencies)
- [Sections](#sections)
- [Axis Configuration](#axis-configuration)
- [Exclusions](#exclusions)
- [Milestones](#milestones)
- [Complete Example: Migration Plan](#complete-example-migration-plan)
- [Sprint Planning Example](#sprint-planning-example)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
        Task A :a1, 2024-01-01, 30d
        Task B :a2, after a1, 20d
```

## Date Formats

```mermaid
gantt
    dateFormat YYYY-MM-DD
```

Supported formats: `YYYY-MM-DD`, `DD-MM-YYYY`, `YYYY-MM-DDTHH:mm:ss` and other moment.js formats.

## Task Syntax

```text
Task name :taskId, startDate, duration
Task name :taskId, startDate, endDate
Task name :taskId, after otherId, duration
```

### Duration Units

- `ms` — milliseconds
- `s` — seconds
- `m` — minutes
- `h` — hours
- `d` — days
- `w` — weeks
- `M` — months
- `y` — years

## Task Tags

Tags must come first, before the task ID:

```mermaid
gantt
    dateFormat YYYY-MM-DD
    section Tasks
        Done task       :done, t1, 2024-01-01, 7d
        Active task     :active, t2, after t1, 5d
        Critical task   :crit, t3, after t2, 3d
        Critical active :crit, active, t4, after t3, 5d
        Future task     :t5, after t4, 10d
```

| Tag | Effect |
|-----|--------|
| `done` | Grayed out, completed |
| `active` | Highlighted as in-progress |
| `crit` | Red/critical path styling |
| `milestone` | Diamond marker, zero duration |

## Dependencies

### After (starts when dependency ends)

```mermaid
gantt
    dateFormat YYYY-MM-DD
    section Sequential
        Design    :des, 2024-01-01, 14d
        Develop   :dev, after des, 30d
        Test      :test, after dev, 14d
```

### Until (v10.9.0+) — task must finish by a deadline

```mermaid
gantt
    dateFormat YYYY-MM-DD
    section Deadline
        Feature   :f1, 2024-01-01, 30d
        Deadline  :milestone, m1, 2024-02-15, 0d
        Cleanup   :c1, after f1, until m1
```

## Sections

```mermaid
gantt
    title Multi-Phase Project
    dateFormat YYYY-MM-DD

    section Analysis
        Requirements  :a1, 2024-01-01, 14d
        Design        :a2, after a1, 7d

    section Development
        Backend       :d1, after a2, 30d
        Frontend      :d2, after a2, 25d

    section Testing
        Integration   :t1, after d1, 14d
        UAT           :t2, after t1, 7d
```

## Axis Configuration

```mermaid
gantt
    title Timeline
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m-%d
    tickInterval 1week
```

Axis format tokens: `%Y` (year), `%m` (month), `%d` (day), `%H` (hour), `%M` (minute)

Tick intervals: `1day`, `1week`, `1month`, `1year` (or multiples like `2week`)

## Exclusions

```mermaid
gantt
    dateFormat YYYY-MM-DD
    excludes weekends
    excludes 2024-12-25, 2024-12-26

    section Sprint
        Task A :2024-12-20, 10d
```

- `weekends` — excludes Saturday and Sunday
- Specific dates — comma-separated
- `weekend friday` — changes weekend to Friday/Saturday

## Milestones

```mermaid
gantt
    dateFormat YYYY-MM-DD
    section Releases
        Alpha release   :milestone, m1, 2024-03-01, 0d
        Beta release    :milestone, m2, 2024-04-15, 0d
        GA release      :milestone, m3, 2024-06-01, 0d
        Development     :active, dev, 2024-01-01, 2024-06-01
```

## Complete Example: Migration Plan

```mermaid
gantt
    title Legacy to Cloud Migration
    dateFormat YYYY-MM-DD
    excludes weekends

    section Discovery
        Inventory assessment    :done, inv, 2024-01-08, 10d
        Dependency mapping      :done, dep, after inv, 5d
        Risk analysis           :done, risk, after dep, 3d
        Migration strategy      :done, strat, after risk, 5d
        Strategy approval       :milestone, done, m1, after strat, 0d

    section Foundation
        Cloud infra setup       :active, infra, after m1, 15d
        CI/CD pipeline          :active, cicd, after m1, 10d
        Monitoring setup        :mon, after infra, 5d
        Security baseline       :sec, after infra, 7d
        Foundation complete     :milestone, m2, after sec, 0d

    section Migration Waves
        Wave 1 - Stateless svcs :crit, w1, after m2, 20d
        Wave 1 - Validation     :w1v, after w1, 5d
        Wave 2 - Stateful svcs  :crit, w2, after w1v, 25d
        Wave 2 - Validation     :w2v, after w2, 7d
        Wave 3 - Data layer     :crit, w3, after w2v, 30d
        Wave 3 - Validation     :w3v, after w3, 10d

    section Cutover
        Rehearsal               :reh, after w3v, 5d
        Production cutover      :crit, cut, after reh, 3d
        Go-live                 :milestone, crit, m3, after cut, 0d
        Hypercare               :hyp, after m3, 14d
```

## Sprint Planning Example

```mermaid
gantt
    title Sprint 24 - Jan 15 to Jan 26
    dateFormat YYYY-MM-DD
    excludes weekends

    section Backend
        API refactor        :crit, api, 2024-01-15, 4d
        Auth middleware      :auth, after api, 3d
        DB migration        :db, 2024-01-15, 2d

    section Frontend
        Dashboard redesign  :dash, 2024-01-15, 5d
        Form validation     :form, after dash, 3d

    section QA
        Test automation     :test, 2024-01-18, 4d
        Regression suite    :reg, after test, 3d

    section Milestones
        Code freeze         :milestone, m1, 2024-01-24, 0d
        Sprint review       :milestone, m2, 2024-01-26, 0d
```

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Use task IDs** — Enable dependencies with `after`
3. **Mark critical path** — Use `crit` tag for blocking tasks
4. **Use milestones** — Mark key decision points and deadlines
5. **Exclude non-work days** — `excludes weekends` for realistic timelines
6. **Group with sections** — Organize by phase, team, or workstream
7. **Show dependencies** — Use `after` to chain sequential tasks
8. **Keep readable** — Limit to ~30 tasks per chart; split larger plans
