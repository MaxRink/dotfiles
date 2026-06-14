---
name: dt-brain-shared-caas-ct-project
description: This skill should be used when the user mentions "tcaas report", "epics report", "tcaas epics", "project report", "workload report", "epic status", or needs to generate a status report for TCAAS project epics with assigned/unassigned task breakdowns.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-ct-project by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TCAAS Project Reporting

This skill generates status reports for TCAAS project epics, showing epic ownership, task assignments, and unassigned work.

## Dependencies

- **Jira API Token**: `JIRA_API_TOKEN` environment variable must be set
- **PDF generation**: Uses the `cloud-pdf` skill's `generate-pdf.py` for PDF output
- **VPN Required**: Yes - Jira API access only works when connected to Telekom VPN
- **Python 3.x with venv**: The script uses the project venv at `<repo-root>/.venv/bin/python`. The venv must have `fpdf2` installed (`pip install fpdf2`) for PDF generation to work. If the venv is not found, the script falls back to system `python3`.

## Operations

### Generate Epics Report

Generate a status report for TCAAS epics filtered by labels:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/tcaas-epics-report.py
```

This produces a markdown report at `reports/tcaas-epics-report.md`.

#### Options

- `--labels <label1,label2>` - Labels to filter epics (default: `Create_Operate_Management_Clusters,Create_Migrate_Workload_Clusters`)
- `--output-dir <dir>` - Output directory (default: `reports/`)
- `--pdf` - Also generate a PDF with Telekom branding
- `--include-closed` - Include Closed/Done issues (excluded by default)

#### Examples

```bash
# Default report (markdown only)
.venv/bin/python ${SKILL_DIR}/scripts/tcaas-epics-report.py

# Report with PDF
.venv/bin/python ${SKILL_DIR}/scripts/tcaas-epics-report.py --pdf

# Custom labels
.venv/bin/python ${SKILL_DIR}/scripts/tcaas-epics-report.py --labels "TDG-legacy,meec-affected"

# Include closed issues
.venv/bin/python ${SKILL_DIR}/scripts/tcaas-epics-report.py --include-closed --pdf
```

## Report Structure

The generated report includes:

1. **Epic Overview** - All matching epics grouped by label, with status and owner
2. **Assigned Tasks - By Person** - All non-closed child tasks grouped by assignee, showing which epic they belong to
3. **Unassigned Tasks** - All non-closed child tasks with no assignee, grouped by parent epic
4. **Summary** - Totals, percentages, empty epics, and workload distribution table

## Instructions for Claude

When the user asks for a TCAAS project report or epic status:

1. Run the report script with appropriate flags
2. If the user wants a PDF, add the `--pdf` flag
3. If the user specifies different labels, pass them via `--labels`
4. Present a summary of the output to the user
5. The script automatically uses the project venv at `<repo-root>/.venv/bin/python`. Ensure `fpdf2` is installed in the venv for PDF generation.
