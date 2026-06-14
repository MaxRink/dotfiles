---
name: tcaas-agent-troubleshooter-caas-alertmanager
description: This skill should be used when the user mentions "AlertManager", "silence", "silences", "create silence", "delete silence", "mute alert", "suppress alert", "active alerts", or needs to manage alert silences in the CaaS AlertManager.
---

<!-- Imported from tdi-caas/tools/tcaas-agent-troubleshooter/skills/caas-alertmanager by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# AlertManager Integration

This skill provides tools to interact with the CaaS AlertManager API for managing silences and viewing alerts.

## Instance Details

- **API Base URL**: Configured via `ALERTMANAGER_URL` environment variable
- **API Version**: v2
- **Authentication**: Basic Auth (username/password)
- **VPN Required**: Yes - API access only works when connected to Telekom VPN

## Authentication Setup

Set the following environment variables before using any AlertManager operations:

```bash
export ALERTMANAGER_URL="https://alertmanager.caas-support-hrvart3.caas.in.pan-net.eu"
export ALERTMANAGER_USER="your-username"
export ALERTMANAGER_PASSWORD="your-password"
```

**Note:** SSL verification is disabled by default for compatibility with corporate/internal CAs. To enable it, set `ALERTMANAGER_VERIFY_SSL=true`.

## Operations

### Create Silence

Create a new silence to suppress alerts:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=AlertName" \
  --duration "6h" \
  --comment "Reason for silence" \
  --author "Your Name"
```

Options:
- `--matcher, -m` - Matcher in format `name=value` (required, can be repeated)
  - Equality: `alertname=NodeDown`
  - Inequality: `cluster!=prod`
  - Regex match: `alertname=~Node.*`
  - Regex not match: `alertname!~Test.*`
- `--duration, -d` - Duration (e.g., `1h`, `2d`, `1w`, `6M`)
- `--ends, -e` - End date (YYYY-MM-DD or ISO 8601) - alternative to duration
- `--comment, -c` - Comment/reason for the silence (required)
- `--author, -a` - Author name (required)
- `--json` - Output result as JSON

**Duration formats:**
- `1h` - 1 hour
- `2d` - 2 days
- `1w` - 1 week
- `6M` - 6 months (approximate, 30 days per month)

Examples:
```bash
# Silence for 6 hours
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=NodeNetworkReceiveErrorsCritical" \
  --duration 6h \
  --comment "CAASPROD-4150: Investigating network errors" \
  --author "Xavi Esteve"

# Silence until specific date (6 months)
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=NodeNetworkReceiveErrorsCritical" \
  --ends "2026-08-03" \
  --comment "CAASPROD-4150: Long-term silence for known issue" \
  --author "Xavi Esteve"

# Silence with multiple matchers
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=TargetDown" \
  --matcher "cluster=hrzagt6-sepp-titan-clab" \
  --duration 2d \
  --comment "Planned maintenance" \
  --author "Xavi Esteve"

# Silence using regex matcher
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=~Node.*" \
  --duration 1h \
  --comment "Testing node alerts" \
  --author "Xavi Esteve"
```

### List Silences

List active and optionally expired silences:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py
```

Options:
- `--all, -a` - Include expired silences
- `--json` - Output as JSON

Examples:
```bash
# List active silences
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py

# Include expired silences
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py --all

# JSON output for scripting
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py --json
```

### Delete Silence

Delete (expire) an existing silence:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-delete.py <silence-id>
```

The silence ID can be found using `am-silence-list.py`.

Examples:
```bash
# Delete a silence by ID
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-delete.py abc123def456
```

### List Alerts

List active alerts with optional filtering:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py
```

Options:
- `--filter, -f` - Filter in format `name=value` (can be repeated)
- `--silenced, -s` - Include silenced alerts
- `--inhibited, -i` - Include inhibited alerts
- `--summary` - Show summary grouped by alert name
- `--json` - Output as JSON

Examples:
```bash
# List all active alerts
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py

# Filter by alert name
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --filter alertname=NodeNetworkReceiveErrorsCritical

# Show summary by alert type
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --summary

# Include silenced alerts
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --silenced

# JSON output
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --json
```

## Common Use Cases

### Silence an Alert for Investigation
```bash
# 1. Check current alerts
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --summary

# 2. Create silence for the problematic alert
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "alertname=NodeNetworkReceiveErrorsCritical" \
  --duration 4h \
  --comment "CAASPROD-4150: Investigating root cause" \
  --author "Your Name"

# 3. Verify silence was created
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py
```

### Silence for Planned Maintenance
```bash
# Silence all alerts for a specific cluster during maintenance window
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-create.py \
  --matcher "cluster=my-cluster-name" \
  --ends "2026-02-04T06:00:00Z" \
  --comment "Planned maintenance window" \
  --author "Your Name"
```

### Remove Silence After Issue Resolution
```bash
# 1. Find the silence ID
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-list.py

# 2. Delete the silence
.venv/bin/python ${SKILL_DIR}/scripts/am-silence-delete.py <silence-id>
```

### Check Alert Status
```bash
# Quick summary of current alert situation
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --summary

# Check if specific alert is firing
.venv/bin/python ${SKILL_DIR}/scripts/am-alerts.py --filter alertname=KubePodNotReady
```

## Security Notes

1. **Credential Storage**: Never commit ALERTMANAGER_USER/PASSWORD to version control
2. **VPN Required**: API access requires Telekom VPN connection
3. **Audit Trail**: All silences include author and comment for accountability
4. **Always Reference Tickets**: Include Jira ticket numbers in silence comments
