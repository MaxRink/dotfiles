---
name: dt-brain-shared-caas-monitoring
description: Look up, analyze, and propose changes to CaaS Prometheus alert rules and AlertManager configuration (inhibit rules, routing, receivers). Use when the user mentions "prometheus rules", "alert rules", "alertmanager config", "inhibit rules", "alert tuning", "flapping analysis", "monitoring config", "alert routing", "alert receivers", "repeat_interval", "group_interval", asks about alert definitions, Prometheus expressions, alert severity, or needs to investigate why alerts are flapping.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-monitoring by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Monitoring Configuration

Analyze and propose changes to CaaS Prometheus alert rules and AlertManager configuration. Complements the `caas-alertmanager` skill (runtime API) and `cloud-pagerduty` skill (incidents).

## Source Repositories

### Prometheus Alert Rules
- **Repo**: `tdi-caas/helm-charts/prometheus-rules`
- **Format**: Helm-templated ConfigMaps containing Prometheus rule groups
- **Key fields per rule**: `alert` (name), `expr` (PromQL), `for` (duration), `severity` (label)
- **Always search the full repo** — alerts exist in both upstream `kube-prometheus-stack-*.yaml` and custom `caas-*.yaml` / `rules-*.yaml` files
- **File inventory**: See [references/alert-rules-catalog.md](references/alert-rules-catalog.md) when you need to know which file contains a specific alert type

### AlertManager Configuration
- **Repo**: `tdi-caas/caas-bundles`
- **Path**: `functions/caas-alertmanager/caas-alertmanager-*.yaml` (use latest version)
- **Format**: CaasFunction YAML with AlertManager config nested inside `spec.source[name=alertmanager].valuesData` → `config:`
- **Key sections**: `inhibit_rules`, `route` (with `routes`), `receivers`, `global`

## Workflows

### 1. Look Up an Alert Rule

Find the definition (expr, for, severity) of a specific alert:

```bash
# Step 1: Search for the alert name across the prometheus-rules repo
source .env && .venv/bin/python .claude/skills/cloud-gitlab/scripts/gitlab-search-code.py \
  --project tdi-caas/helm-charts/prometheus-rules --query "ALERT_NAME" --limit 10

# Step 2: Fetch the file containing the alert
source .env && .venv/bin/python .claude/skills/cloud-gitlab/scripts/gitlab-get-file.py \
  tdi-caas/helm-charts/prometheus-rules --path "templates/FILENAME.yaml"
```

Parse the output to extract the rule block: `alert`, `expr`, `for`, `labels.severity`, `annotations`.

### 2. Check Inhibit Rules

Retrieve AlertManager config and inspect which alerts suppress others:

```bash
# Get the latest alertmanager function definition
source .env && .venv/bin/python .claude/skills/cloud-gitlab/scripts/gitlab-search-code.py \
  --project tdi-caas/caas-bundles --query "inhibit_rules" --limit 5

# Fetch the full config (use the latest version file found)
source .env && .venv/bin/python .claude/skills/cloud-gitlab/scripts/gitlab-get-file.py \
  tdi-caas/caas-bundles --path "functions/caas-alertmanager/caas-alertmanager-VERSION.yaml"
```

**Inhibit rule structure:** `source_matchers` (firing alert) suppress `target_matchers` (suppressed alert) when `equal` labels match.

**⚠️ Label mismatch gotcha:** AlertManager treats a missing label as `""`. If an `equal` field references a label that one of the alerts doesn't carry (e.g. `interface`), the match will **never fire** for that alert. You cannot extend an existing inhibit rule to cover an additional alert if that alert is missing one of the `equal` labels — add a separate rule with the appropriate `equal` set instead.

### 3. Check Alert Routing

In the same AlertManager config, inspect the `route` and `routes` section:
- `route.group_by`: labels used to group alerts (default: `['alertname', 'cluster', 'tenant']`)
- `route.group_wait`: time to buffer before sending first notification (default: `30s`)
- `route.group_interval`: time between notifications for new alerts in a group (default: `5m`)
- `route.repeat_interval`: time before re-sending for an unchanged alert (default: `12h`)
- `routes[]`: ordered list of sub-routes with matchers → receiver mapping

**Key receivers:**
| Receiver | Purpose |
|----------|---------|
| `OpenNMS2_PROD` | Production SNMP/event forwarding |
| `PagerDuty_EU_T_CaaS` | T-CaaS team paging |
| `null` | Sink (Watchdog, etc.) |

**Environment routing:**
- `environment !~ "development|t-caas-dev"` → alerts from dev clusters are NOT sent to PagerDuty/OpenNMS

### 4. Flapping Analysis

When an alert keeps firing and resolving repeatedly:

```bash
# Step 1: Get incident timing from PagerDuty
source .env && .venv/bin/python .claude/skills/cloud-pagerduty/scripts/pd-incidents.py \
  --since "DATE" --until "DATE" --cluster "CLUSTER" --format json

# Step 2: Analyze timing in Python (pipe JSON output)
# Calculate: alert duration (created→resolved), gap between alerts, frequency
```

**Cross-reference with rule config:**
- If alert duration ≈ `for` value → pod/target recovers just after threshold, then fails again
- If gap between alerts < `for` value → target briefly recovers between failures
- `repeat_interval` does NOT prevent re-firing — resolve→fire cycles create NEW alert instances

**Root cause patterns:**
| Pattern | Likely Cause |
|---------|-------------|
| Duration = `for` exactly, short gaps | CrashLoopBackOff with increasing backoff |
| Duration >> `for`, regular gaps | Periodic resource pressure (OOM, eviction) |
| Irregular timing | External dependency failures |

### 5. Proposing Changes

When suggesting monitoring config changes, consider:

**Adjusting `for` duration (Prometheus rule):**
- Increase `for` to require longer sustained failure before alerting
- Trade-off: reduces noise but delays detection of real outages
- Guideline: set `for` > typical recovery gap to eliminate flapping

**Adding inhibit rules (AlertManager config):**
- Use when one alert makes another redundant (e.g., `KubePodCrashLooping` already implies `TargetDown`)
- Always specify `equal` labels to scope inhibition (at minimum: `cluster`)
- Test with `source_matchers` and `target_matchers` (newer syntax, preferred)

**Tuning routing:**
- `group_wait` increase → fewer initial notifications but slower first alert
- `repeat_interval` only applies to alerts that stay firing continuously
- Route matchers filter by `alertname`, `severity`, `environment`

**Always note:** resolve→fire flapping bypasses `repeat_interval`. Only `for` duration or fixing the root cause stops this pattern.
