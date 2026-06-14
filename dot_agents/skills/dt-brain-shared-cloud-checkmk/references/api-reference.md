# API Reference

## Permission Boundaries

The automation user has access to **monitoring (Livestatus)** endpoints but NOT to **configuration (WATO)** endpoints.

| Endpoint | Status | Description |
|----------|--------|-------------|
| `domain-types/host/collections/all` | ✅ Works | Host monitoring data (state, groups, labels, tags, service counts) |
| `domain-types/service/collections/all` | ✅ Works | Service monitoring data (state, check command, intervals, contacts) |
| `domain-types/downtime/collections/all` | ✅ Works | Active downtimes |
| `domain-types/host_config/collections/all` | ❌ 401 | Host WATO configuration (folder, attributes) |
| `domain-types/ruleset/collections/all` | ❌ 401 | Ruleset listing (requires 'Rulesets' permission) |
| `domain-types/rule/collections/all` | ❌ 401 | Rule listing (requires 'Rulesets' permission) |

To unlock configuration endpoints, ask the CheckMK admin to grant the 'Rulesets' and 'Hosts' WATO permissions to the automation user.

## Livestatus Host Columns

Available via `domain-types/host/collections/all`:

| Column | Description |
|--------|-------------|
| `name` | Hostname |
| `address` | IP address |
| `state` | 0=UP, 1=DOWN, 2=UNREACHABLE |
| `groups` | Host groups (e.g., `["caas-bm"]`) |
| `labels` | Host labels (e.g., `{"cmk/site": "hc_czprgc1"}`) |
| `tags` | Host tags (agent type, criticality, site, unit_type, etc.) |
| `num_services` | Total service count |
| `num_services_ok/warn/crit/unknown` | Service count by state |
| `check_command` | Host check command |
| `plugin_output` | Last check output |
| `contact_groups` | Notification contact groups |
| `last_state_change` | Unix timestamp of last state change |

## Livestatus Service Columns

Available via `domain-types/service/collections/all`:

| Column | Description |
|--------|-------------|
| `host_name` | Parent hostname |
| `description` | Service name |
| `state` | 0=OK, 1=WARN, 2=CRIT, 3=UNKNOWN |
| `check_command` | Check plugin (e.g., `check_mk-ipmi_sensors`) |
| `check_interval` | Check frequency in minutes |
| `retry_interval` | Retry frequency on non-OK state |
| `max_check_attempts` | Attempts before hard state |
| `check_period` | Time period for checks (e.g., `24X7`) |
| `contact_groups` | Notification contact groups |
| `plugin_output` | Last check output text |
| `perf_data` | Performance data metrics |
| `last_check` | Unix timestamp of last check |
| `next_check` | Unix timestamp of next scheduled check |
| `last_state_change` | Unix timestamp of last state change |
| `acknowledged` | 0/1 whether problem is acknowledged |
| `scheduled_downtime_depth` | >0 if in scheduled downtime |
| `notes` | Service notes |
| `notes_url` | Link to external documentation |
