---
name: dt-brain-shared-cloud-checkmk
description: Query active monitoring problems, scheduled downtimes, and host/service check configuration from the CaaS central CheckMK instance. Use when the user mentions "CheckMK", "Checkmk", "check_mk", "monitoring problems", "host problems", "service problems", "monitoring alerts", "CheckMK alerts", "CheckMK downtimes", "scheduled downtime", "check configuration", "alert configuration", "host config", "service config", or needs to investigate monitoring state across CaaS, IaaS, STaaS, or network infrastructure.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-checkmk by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CheckMK Integration

- **Web URL**: `https://central-checkmk.infra-mon.in.pan-net.eu/cmkcentralprod/`
- **Authentication**: Via environment variables in `.env` (`CHECKMK_URL`, `CHECKMK_SITE`, `CHECKMK_USER`, `CHECKMK_PASSWORD`)
- **VPN Required**: Yes. All operations are read-only.

## Operations

All scripts support `--help` for full options and `--json` for machine-readable output.

### List Active Problems

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-alerts.py [options]
```

Key options: `--group GROUP`, `--host PATTERN`, `--service PATTERN`, `--state CRIT,WARN`, `--no-ack`, `--no-downtime`, `--summary`, `--by-site`, `--by-host`, `--links`

```bash
# CaaS critical problems, unhandled only
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-alerts.py --group caas --state CRIT --no-downtime --no-ack

# IaaS summary
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-alerts.py --group iaas --summary

# Site-level breakdown
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-alerts.py --group caas --state CRIT --by-site
```

### List Downtimes

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-downtimes.py [options]
```

Key options: `--host HOST`, `--group GROUP`, `--author AUTHOR`

### View Host & Service Configuration

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-config.py [options]
```

Key options: `--host HOSTNAME`, `--services`, `--service PATTERN`, `--search-hosts PATTERN`, `--group GROUP`

```bash
# Host details (address, groups, tags, labels, service summary)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-config.py --host <hostname>

# Service check configuration (command, intervals, contacts)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-config.py --host <hostname> --service "IPMI"

# Search hosts by name
source .env && .venv/bin/python ${SKILL_DIR}/scripts/cmk-config.py --search-hosts czprgc1 --group caas
```

### Host Groups

| Group | Alias | Description |
|-------|-------|-------------|
| `caas-bm` | `caas` | CaaS bare-metal servers |
| `openstack-infra` | `iaas`, `openstack` | IaaS / OpenStack infrastructure |
| `staas` | `storage` | Storage as a Service |
| `server-hw` | `hw` | Server hardware (IMM/ILO) |
| `network` | `net` | Network devices (switches, routers) |
| `pdu` | | Power Distribution Units |
| `check_mk` | | CheckMK monitoring infrastructure |

## Investigation Workflow

Typical drill-down sequence:

1. **Overview** — `cmk-alerts.py --group caas --state CRIT --by-site`
2. **Drill into site** — `cmk-alerts.py --group caas --host ic-mkskof2 --by-host`
3. **Check downtimes** — `cmk-downtimes.py --host <hostname>`
4. **Unhandled problems** — `cmk-alerts.py --host <hostname> --no-downtime --no-ack --links`
5. **Host config** — `cmk-config.py --host <hostname>`
6. **Service config** — `cmk-config.py --host <hostname> --service "IPMI"`

## References

- **Host naming & site codes**: See [references/host-naming.md](references/host-naming.md) for decoding hostnames and site code lookup table
- **API reference & Livestatus columns**: See [references/api-reference.md](references/api-reference.md) for available API endpoints, permission boundaries, and queryable columns
