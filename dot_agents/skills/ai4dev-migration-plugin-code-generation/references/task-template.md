# Task Template — tasks.md

Use this template when generating `tasks.md` for a feature. Replace placeholders with actual values.

---

## Template

```markdown
# Code Generation Tasks — <feature-name>

> Generated: <ISO 8601 timestamp>
> Source: `.migration/<feature-name>/spec-specification/`
> Status: <In Progress | Completed | Halted>

## Progress Summary

| Metric     | Count |
|------------|-------|
| Total      | <N>   |
| Completed  | <N>   |
| Failed     | <N>   |
| Skipped    | <N>   |
| Remaining  | <N>   |

---

## Step 1 — Setup

> Status: <not-started | in-progress | completed | failed>

| Task | Title | Status | Dependencies | BR IDs |
|------|-------|--------|--------------|--------|
| T001 | <title> | <status-marker> <status> | — | — |
| T002 | <title> | <status-marker> <status> | T001 | — |

---

## Step 2 — Tests (TDD Red)

> Status: <not-started | in-progress | completed | failed>

| Task | Title | Status | Dependencies | BR IDs |
|------|-------|--------|--------------|--------|
| T003 | <title> | <status-marker> <status> | T001,T002 | BR001,BR002 |
| T004 | <title> | <status-marker> <status> | T001,T002 | BR003 |

---

## Step 3 — Core (TDD Green)

> Status: <not-started | in-progress | completed | failed>

| Task | Title | Status | Attempts | Dependencies | BR IDs |
|------|-------|--------|----------|--------------|--------|
| T005 | <title> | <status-marker> <status> | <N>/3 | T003 | BR001 |
| T006 | <title> | <status-marker> <status> | <N>/3 | T004 | BR003 |

### Failure Details (if any)

#### T00X — <title>
- **Attempt 1**: <failure summary>
- **Attempt 2**: <failure summary>
- **Attempt 3**: <failure summary>
- **Halted**: <reason>

---

## Step 4 — Integration

> Status: <not-started | in-progress | completed | failed>

| Task | Title | Status | Attempts | Dependencies | BR IDs |
|------|-------|--------|----------|--------------|--------|
| T007 | <title> | <status-marker> <status> | <N>/3 | T005,T006 | — |

---

## Step 5 — Polish

> Status: <not-started | in-progress | completed | failed>

| Task | Title | Status | Dependencies | BR IDs |
|------|-------|--------|--------------|--------|
| T008 | <title> | <status-marker> <status> | T007 | — |

---

## Generated Files

| File | Task | Purpose |
|------|------|---------|
| `src/<file>` | T005 | <description> |
| `tests/<file>` | T003 | <description> |
| `features/<file>.feature` | T004 | BDD scenario for <rule> |

---

## Next Steps

> Run `/validation <feature-name>` to validate the generated code against specifications.
```

## Status Marker Reference

| Status | Marker |
|--------|--------|
| not-started | [ ] |
| in-progress | [~] |
| passed | [PASS] |
| failed | [FAIL] |
| skipped | [SKIP] |

## Conventions

1. **Always update `tasks.md` after each task completes or fails** — this is the user-facing progress tracker.
2. **Step headers** include the step status — update when the first task starts and when the last task finishes.
3. **Failure Details section** only appears in steps that use the TDD retry loop (Core, Integration).
4. **Generated Files table** grows incrementally as tasks produce output.
5. **Progress Summary** at the top is recalculated after every task state change.
