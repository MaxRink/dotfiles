---
name: dt-brain-shared-caas-team-planning
description: >-
  This skill should be used when the user mentions "team planning", "who is on holiday",
  "who is on vacation", "team availability", "vacation planning", "holidays", "bank holidays",
  "who is off", "who is available", "on-duty", "on duty", "team schedule", "planning sheet",
  or needs to check CaaS team member availability, holidays, or on-duty assignments for a
  specific date or date range.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-team-planning by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Team Planning

Check CaaS team availability by combining the Google Sheets vacation planner with PagerDuty on-call schedules.

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| Google Sheets | Vacations, bank holidays | Public sheet (no auth) |
| PagerDuty | On-call and on-duty schedules (1st & 2nd level) | `PAGERDUTY_TOKEN` env var |

### Google Sheet

- **URL**: `https://docs.google.com/spreadsheets/d/163-0QlHpRuQmixYJ8uZOjdpNaFEyvNHhck-SkAGOTZc`
- **Sheet name**: Year number (e.g., `2026`)
- **Format**: Columns = days of year (DD/MM), rows = team members
- **Legend**: `V` = Vacation, `V (0,5)` = Half Day, `BT` = Business Trip, country codes = Bank Holiday

## Requirements

- `PAGERDUTY_TOKEN` environment variable (for on-call data)
- VPN connection to Telekom network (for PagerDuty)
- Internet access (for Google Sheets)

## Usage

```bash
# Check team availability for a specific date
source .env && .venv/bin/python ${SKILL_DIR}/scripts/team-availability.py --date 2026-04-09

# Check availability for today
source .env && .venv/bin/python ${SKILL_DIR}/scripts/team-availability.py --today

# Check a date range
source .env && .venv/bin/python ${SKILL_DIR}/scripts/team-availability.py --from 2026-04-07 --to 2026-04-11

# Skip PagerDuty (only show vacation/holiday data)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/team-availability.py --date 2026-04-09 --no-oncall

# JSON output
source .env && .venv/bin/python ${SKILL_DIR}/scripts/team-availability.py --date 2026-04-09 --json
```

## Output

The script shows a combined view:
1. **Bank Holidays** active on the date (per country)
2. **On Holiday / Away** — team members on vacation or business trip
3. **On-Call** — PagerDuty 1st and 2nd level on-call assignments (authoritative source for on-call and on-duty)
4. **Available** — team members with no holiday markers

> **Note:** The on-duty field from the Google Sheet is intentionally ignored — PagerDuty is the single source of truth for on-call and on-duty assignments.
