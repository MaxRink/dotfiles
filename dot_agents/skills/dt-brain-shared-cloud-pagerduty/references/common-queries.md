# Common PagerDuty Queries

## Quick Reference

### Check Current Status

```bash
# Active incidents (triggered or acknowledged)
${SKILL_DIR}/scripts/pd-incidents.py --status triggered,acknowledged

# Who is on call right now
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py
```

### Incident Queries

```bash
# Default: last 24 hours
${SKILL_DIR}/scripts/pd-incidents.py

# ALL active incidents (no time limit when filtering by triggered/acknowledged)
${SKILL_DIR}/scripts/pd-incidents.py --status triggered,acknowledged

# All incidents ever (use --all flag)
${SKILL_DIR}/scripts/pd-incidents.py --all

# Last 7 days
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22"

# Specific date range
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-01" --until "2026-01-31"

# Filter by cluster
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --cluster atgraf1-ndl-prod

# Filter by site
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --site atgraf1

# Get summary statistics
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --format summary

# Only high urgency (using summary)
${SKILL_DIR}/scripts/pd-incidents.py --since "2026-01-22" --format summary

# Get specific incident details
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py Q32G3MTCMP2QBZ

# Get incident as JSON for further processing
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-get.py Q32G3MTCMP2QBZ --json
```

### Incident Actions

```bash
# Add a note to an incident
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-note.py 107041 "Alert silenced in AlertManager"

# Add note with custom email
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-note.py Q1UFIV4RJQRWCS "Fixed issue" --from "user@example.com"

# Resolve an incident (without note)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-resolve.py 107041

# Resolve with explanation
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-resolve.py 107041 --note "Alert silenced for 2 years - cluster not maintained"

# Combined: add note then resolve
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-note.py 107041 "Created AlertManager silence ID: abc123. Cluster is old 1.23 version managed by IoT team."
.venv/bin/python ${SKILL_DIR}/scripts/pd-incident-resolve.py 107041 --note "Resolved after silencing"
```

### On-Call Queries

```bash
# All current on-call assignments
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py

# Filter by schedule name
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --schedule "First"

# Check on-call at a specific time
.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py --since "2025-01-27T08:00:00Z"

# View schedule for next 48 hours (use API directly)
curl -s -H "Authorization: Token token=${PAGERDUTY_TOKEN}" \
  "https://api.pagerduty.com/oncalls?team_ids[]=P5TDGFM&since=$(date -u +%Y-%m-%dT%H:%M:%SZ)&until=$(date -v+48H -u +%Y-%m-%dT%H:%M:%SZ)"
```

### Service Queries

```bash
# All T-CaaS services
.venv/bin/python ${SKILL_DIR}/scripts/pd-services.py

# Only active services
.venv/bin/python ${SKILL_DIR}/scripts/pd-services.py --status active

# Only disabled services
.venv/bin/python ${SKILL_DIR}/scripts/pd-services.py --status disabled
```

### Statistics and Reporting

```bash
# Last 24 hours summary (default)
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --format summary

# Last 7 days
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --format summary --since "$(date -v-7d +%Y-%m-%d)"

# Monthly report
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --format summary --since "2025-01-01" --until "2025-01-31"

# Quarterly report
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --format summary --since "2025-01-01" --until "2025-03-31"
```

### Team Discovery

```bash
# Find T-CaaS team ID (one-time setup)
.venv/bin/python ${SKILL_DIR}/scripts/pd-team-info.py "T-CaaS"

# Search for other teams
.venv/bin/python ${SKILL_DIR}/scripts/pd-team-info.py "TDI"
```

## Combining with Other Tools

### Export incidents to CSV

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "2025-01-01" --max 100 | \
  grep "^#" | \
  awk '{print $2, $3, $4}' > incidents.csv
```

### Count incidents per service

```bash
.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --since "$(date -v-7d +%Y-%m-%d)" | \
  grep "Service:" | \
  cut -d: -f2 | \
  sort | uniq -c | sort -rn
```

### Quick incident check in shell prompt

```bash
# Add to .zshrc or .bashrc
alias pd-active='.venv/bin/python ${SKILL_DIR}/scripts/pd-incidents.py --status "triggered,acknowledged"'
alias pd-oncall='.venv/bin/python ${SKILL_DIR}/scripts/pd-oncall.py'
```

## Environment Setup

Before running any script, ensure:

```bash
# Set API token (add to ~/.zshrc for persistence)
export PAGERDUTY_TOKEN="your-api-token"

# Team ID is hardcoded in scripts (P5TDGFM), but can be overridden:
export TCAAS_TEAM_ID="P5TDGFM"
```

## Troubleshooting

### "PAGERDUTY_TOKEN environment variable is not set"

```bash
source ~/.zshrc  # Reload shell config
echo $PAGERDUTY_TOKEN  # Verify it's set
```

### "API request failed with status 401"

Your API token is invalid or expired. Create a new one in PagerDuty.

### "API request failed with status 403"

Insufficient permissions. Ensure your token has read access.

### No incidents showing

- For active incidents, use `--status "triggered,acknowledged"` (no time limit applied)
- For historical queries, check the date range with `--since` and `--until`
- Use `--all` to remove any time filtering
- Verify `TCAAS_TEAM_ID` is set correctly (default: P5TDGFM)
