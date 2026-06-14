---
name: tdi-cloudbrain-tdi-caas-report
user-invocable: true
description: This skill should be used when the user mentions "tdi-caas report", "team report", "bi-weekly report", "2-week report", "caas team status", "sprint report", or needs to generate a combined Jira + GitLab status report for the TDI CaaS team.
---

<!-- Imported from tdi-caas/tools/tdi-cloudbrain/skills/tdi-caas-report by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TDI CaaS Team Review

Generate bi-weekly team reports combining Jira (CAASPROD) and GitLab (tdi-caas) data.

## Requirements

- `JIRA_API_TOKEN` and `GITLAB_API_TOKEN` environment variables
- VPN connection to Telekom network
- `telekom-pdf` skill for PDF generation (optional)

## Usage

```bash
# Basic report (markdown only)
.venv/bin/python ${SKILL_DIR}/scripts/generate-report.py

# With PDF output (landscape orientation)
.venv/bin/python ${SKILL_DIR}/scripts/generate-report.py --pdf

# Custom time period (default: 14 days)
.venv/bin/python ${SKILL_DIR}/scripts/generate-report.py --days 7

# Custom output directory
.venv/bin/python ${SKILL_DIR}/scripts/generate-report.py --output-dir /tmp/reports
```

## Report Structure

1. **Summary** - Counts by category at the top
2. **Jira sections** (Completed, In Progress, Refined) each with subsections:
   - On-Call
   - Development
   - Upgrades
   - Operations
   - Other
3. **GitLab - Merged MRs** - Grouped by project
4. **Top Contributors** - GitLab and Jira contributors at the end

## Categorization Logic

| Category | Detection |
|----------|-----------|
| On-Call | Summary contains "on-call" |
| Development | Label `tdi-caas-development` |
| Upgrades | Label `tdi-caas-cluster-upgrade` or summary contains "upgrade" |
| Operations | Label `tdi-caas-operations` |
| Other | No match |

## Output

Reports saved to output directory as:
- `tdi-caas-report-YYYY-MM-DD.md`
- `tdi-caas-report-YYYY-MM-DD.pdf` (landscape, if `--pdf`)
