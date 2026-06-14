---
name: dt-brain-shared-slack
description: This skill should be used when the user mentions "Slack", "slack channel", "channel summary", "slack search", "slack messages", "what happened in channel", "daily summary", "channel activity", "slack incidents", "slack history", asks about "what was discussed", "channel report", "search slack", "find in slack", "slack profile", "slack research", "slack analysis", "summary of person", "research about person", "tell me about person from slack", "analysis of person", "who is person", or needs to search, summarize, or browse Slack conversations, do person/user profile research, or investigate incident discussions.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/slack by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Slack Integration

Read and search Slack workspace messages for the T-CaaS team.

- **Auth**: `SLACK_BOT_TOKEN` (bot token) + `SLACK_BOT_USER_TOKEN` (user token for search)
- **VPN Required**: No (Slack API is public)
- **Read-Only**: All operations are read-only

## Setup — Getting Your Tokens

The Slack app **caas_ai_scout** is already installed in the TDI workspace. No new app creation needed.

### Bot Token (shared, same for everyone)

The bot token (`SLACK_BOT_TOKEN`) is tied to the app, not to any personal account. Get it from:

1. Go to **https://api.slack.com/apps** → select **caas_ai_scout**
2. Go to **OAuth & Permissions**
3. Copy **Bot User OAuth Token** (`xoxb-...`)

Or ask a team member who already has it.

### User Token (personal, each user generates their own)

The user token (`SLACK_BOT_USER_TOKEN`) is personal — it runs searches with your permissions and identity.

1. Go to **https://api.slack.com/apps** → select **caas_ai_scout**
2. Go to **OAuth & Permissions**
3. Click **Reinstall to Workspace** (this generates a new user token for *your* account)
4. Authorize when prompted
5. Copy **User OAuth Token** (`xoxp-...`)

> ⚠️ **Reinstalling** replaces the existing user token. Coordinate with the team so you don't invalidate someone else's token. Alternatively, each team member can be added as a **collaborator** on the app (Settings → Collaborators) to manage their own OAuth independently.

### Add to `.env`

```bash
export SLACK_BOT_TOKEN=xoxb-...          # shared, same for all users
export SLACK_BOT_USER_TOKEN=xoxp-...     # personal, each user has their own
```

> **Note**: The user token is optional. Without it, `slack-search.py` and search-based features of `slack-incidents.py` won't work, but all other scripts function normally with just the bot token.

### Required Bot Token Scopes (reference)

Already configured on the app: `channels:read`, `channels:history`, `groups:read`, `groups:history`, `users:read`, `channels:join`

### Required User Token Scopes (reference)

Already configured on the app: `search:read`

## Script Selection — Decision Tree

| User Request | Script | Key Flags |
|---|---|---|
| "list channels", "what channels" | `slack-channels.py` | `--filter`, `--sort` |
| "show messages from channel X" | `slack-history.py` | `--channel X --from 24h` |
| "what happened in #channel today" | `slack-summary.py` | `--channel X --from 24h` |
| "summarize all channels" | `slack-summary.py` | `--all` |
| "search slack for X" | `slack-search.py` | `--query X` |
| "find incident discussion" | `slack-incidents.py` | `--cluster`, `--alert`, `--since` |
| "incident summary from slack" | `slack-incidents.py` | `--summary` |
| "tell me about person X", "research X", "summary of X" | `slack-search.py` | See **User Profile Analysis** workflow below |

### Key Distinctions

- **slack-history.py** = raw message output, chronological, good for reading conversations
- **slack-summary.py** = aggregated stats (contributors, threads, links, reactions), good for "what happened"
- **slack-search.py** = workspace-wide keyword search using Slack search syntax
- **slack-incidents.py** = specialized for incident hunting (PD links, alert names, cluster names)

## User Profile Analysis

When the user asks for a **summary**, **research**, **analysis**, or **profile** of a person from Slack (e.g. "do slack research about John Doe", "tell me about Jane Smith from slack", "make a summary of user X"), perform a comprehensive multi-step analysis using `slack-search.py`.

### Trigger Words

Any of: `summary of`, `research about`, `analysis of`, `profile of`, `tell me about`, `who is`, `what does X do`, `make same for` (referencing a prior person profile).

### Step-by-Step Methodology

#### Step 1: Find the Username

Try multiple Slack username patterns until one returns results:

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:firstname.lastname" --limit 3
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:f.lastname" --limit 3
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:lastname" --limit 3
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:nickname" --limit 3
```

The first line of output shows total message count ("Found N results"). Record the working username and total count.

#### Step 2: Count Messages Per Channel

Iterate through all known team channels to build a channel presence table:

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:USERNAME in:CHANNEL" --limit 1
```

**Channels to check** (in order of importance):

Primary engineering: `caas-h4ck0rz`, `caas_team`, `caas`, `t-caas-team`
Operations: `onb-and-caas`, `caas-soc`, `caas-clab`, `monitoring-caas`, `caas-alerts`, `caas-incidents`
Convergence: `clab-tcaas-converged`, `convergence-caas`
Specialized: `nwi-caas`, `caas-code-review`, `caas-portal`, `caas-networking`
Other: `general`, `soc-sec`, `paas_dns_devops`, `sec_caas_idp_auth`, `tmcz-sk-deliveries`

Record counts for channels with >0 messages. Run checks in parallel for efficiency.

#### Step 3: Deep-Dive Content (Top Channels)

For each channel with significant message count (top 3-5), fetch actual messages across multiple time periods:

```bash
# Recent messages
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:USERNAME in:CHANNEL" --limit 20 --page 1
# Mid-history
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:USERNAME in:CHANNEL" --limit 20 --page 50
# Earliest messages (ascending sort)
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:USERNAME in:CHANNEL" --limit 20 --page 1 --sort timestamp --sort-dir asc
```

Read message content to understand: what topics they discuss, what they work on, their communication style, who they interact with.

#### Step 4: Topic-Specific Searches

Based on patterns discovered in Step 3, run targeted searches to map expertise areas:

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "from:USERNAME keyword1 keyword2" --limit 10
```

**Common topic searches to try** (adapt based on what Step 3 reveals):

- Technical: `T-CO operator CaasCluster`, `convergence converged`, `baremetal BMC`, `network calico metallb BGP`, `sriov mellanox firmware`, `dualstack ipv6`, `upgrade reroll`, `product release bundle`, `image-builder`
- Process: `jira ticket backlog`, `volunteer assign task`, `on-call oncall pagerduty`, `HPSM change maintenance`, `lessons learned`
- NatCo: `MT HT OTE CZSK`, `PCF Nokia SDM`
- Role: `chapter lead scrum master`, `review approve`

#### Step 5: Compile the Profile

Produce a structured summary with these sections:

```markdown
# 🔍 Full Name (slack.username / @display) — Slack Profile Summary

## Identity
- Slack username, display name, total messages, activity span, team, location (if discoverable)

## Channel Presence
| Channel | Messages | Role |
|---------|----------|------|
(sorted by message count descending)

## 🎯 Role: **Discovered Role Title**
Narrative description of what they do, based on evidence from messages.

### Numbered subsections for each area of expertise/responsibility
(with specific examples, cluster names, tools, code references from messages)

## 🎨 Working Style
Numbered list of personality traits and communication patterns with quote examples.

## 👥 Key Collaborators
List of people they interact with most (name, Slack ID, relationship context).

## 📊 Summary
2-3 sentence executive summary of who this person is and their significance to the team.
```

### Tips & Patterns

- **Pagination limit**: Slack API caps at ~100 pages. For users with >2000 msgs in a channel, use ascending sort to see earliest messages.
- **Username discovery**: Greek names often use `a.zakopoulos` pattern. Slovak/Czech names try `firstname.lastname` first. Employee IDs like `i752954` are also valid usernames.
- **Deactivated users**: Still searchable. Note deactivation prominently in the profile.
- **DM channels**: Messages in `mpdm-*` or `U*` channels indicate private/group conversations — still useful for understanding working relationships.
- **Parallel execution**: Run channel counts and independent searches in parallel to speed up the process.
- **Minimum viable profile**: Even 3 channels + 2 topic searches can produce a useful profile. Scale depth to user's needs.

## Operations

### slack-channels.py — List & Filter Channels

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-channels.py [options]
```

Options: `--filter PATTERN` (regex), `--sort {name,members,activity}`, `--private`, `--limit N`, `--json`

### slack-history.py — Fetch Channel Messages

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-history.py --channel CHANNEL [options]
```

Options: `--from` (default: 24h), `--to`, `--limit N`, `--threads` (expand replies), `--verbose`, `--json`

### slack-summary.py — Channel Activity Summary

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-summary.py --channel CHANNEL [options]
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-summary.py --all [--filter PATTERN]
```

Options: `--from` (default: 24h), `--to`, `--top N`, `--all`, `--filter PATTERN`, `--json`

Output includes: message count, unique users, threads, top contributors, peak hours, reactions, links shared.

### slack-search.py — Search Messages

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-search.py --query "QUERY" [options]
```

Options: `--sort {score,timestamp}`, `--sort-dir {asc,desc}`, `--limit N`, `--page N`, `--json`

Supports Slack search syntax: `in:channel`, `from:user`, `has:link`, `before:YYYY-MM-DD`, `after:YYYY-MM-DD`.

### slack-incidents.py — Incident-Focused Search

```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-incidents.py [options]
```

Options: `--cluster NAME`, `--alert NAME`, `--since` (default: 24h), `--channel`, `--keyword`, `--limit N`, `--summary`, `--json`

Detects: PagerDuty links, `[site | cluster] AlertName` patterns, cluster name mentions, incident keywords.

## Channel Directory

Known channels and their purpose. Use this to pick the right channel for queries.

> **Performance tip**: For private channels, use the channel **ID** (from the table below) instead of the name when calling scripts. This avoids slow workspace-wide pagination. Example:
> ```bash
> .venv/bin/python ${SKILL_DIR}/scripts/slack-history.py --channel G01C1FHV6RH --from 24h
> ```

| Channel | ID | Type | Messages | Purpose |
|---|---|---|---|---|
| `caas` | | Public | ~24k | **Customer-facing CaaS channel**. On-call rotation updates (topic auto-updated), customer support requests, namespace whitelisting, OPA exceptions, cluster issues. CaaS wiki & Jira service desk links pinned. |
| `caas-h4ck0rz` | `G01C1FHV6RH` | Private | ~42k | **Core CaaS engineering team**. Day-to-day technical work: cluster configs, alertmanager silences, federation configs, convergence clusters, PagerDuty alert triage, compute profiles, NTP configs, GitLab bundle reviews, test infrastructure, dt-brain skill development. Highest signal for technical decisions. |
| `caas_team` | `GCU626DJM` | Private | ~43k | **CaaS team coordination**. Daily standups, meeting links (Teams), AHC reminders, artifactory access, DDU tool status, licensing issues, sprint ceremonies, social/fun sharing. Team-wide announcements. |
| `caas-clab` | `C04J4E96NMB` | Private | — | **CaaS Central Lab**. Lab cluster operations and testing. |
| `caas-code-review` | `C07G5873NGG` | Private | — | **CaaS code reviews**. Code review discussions and GitLab MR notifications. |
| `caas-soc` | | Private | ~8k | **CaaS ↔ SOC collaboration**. Incident management between CaaS and Service Operations Center: hardware incidents (Lenovo SHS), server power-offs, node maintenance, IPMI issues, portal team routing, P4 investigations, host filtering from alerts. |
| `caas_ops` | | Public | ~516k | **Automated alerts/notifications**. PagerDuty alert feed, AlertManager notifications. Extremely high volume, almost entirely bot-generated. Useful for searching specific alert patterns over time. |
| `cloud_platforms-lt` | | Private | ~291 | **Cloud Platforms leadership team**. Strategic decisions: managed vs. franchise models, IaaS instances, BM4X strategy, NatCo relationships, INaaS+ positioning, AI/skills tooling adoption, procurement coordination. Low volume, high signal. |
| `onb-and-caas` | | Private | ~12k | **Onboarding team ↔ CaaS**. Cluster onboarding operations: kubeconfig updates, DCIM registration, OpenStack network setup (provider nets, VLANs, trunks), IDP role mappings, breakglass access, MetalLB/LoadBalancer config, machine operator updates. |
| `t-caas-team` | | Private | ~8k | **T-CaaS product team**. Product-level coordination: image epics (TCAAS Jira), environment naming, daily huddle reminders, review sessions, sprint planning, certification prep, code version updates. |
| `tdi_businessnews` | | Public | ~316 | **TDI-wide business news**. Major announcements: first bare metal delivery, new customer wins, UC Slice integration, weekly TI reports (CW reports), inflight project updates, Starque growth. |
| `tdi_communication` | | Public | ~1.5k | **TDI-wide communication**. AHC recordings & slides, TDI Classroom sessions (DevOps, Cloud Technology), open source contribution initiatives, organizational announcements. |
| `tmpl-escalation-temporary-channel` | | Private | ~318 | **T-Mobile PL escalation**. TMPL/Nokia/TDI steerco decisions, customer migration timelines, hardware procurement (Magenta/Buyin), pipeline/code adaptations for PL infrastructure, local deb repo discussions. |
| `planning_workshop_barcelona` | | Private | ~322 | **Workshop coordination**. Barcelona planning workshop logistics, presentation sharing, architecture summaries (linked from GitLab). Time-limited/event-specific. |

### Channel Selection Guide

| You want to know about... | Check these channels |
|---|---|
| A specific cluster issue / alert | `caas-h4ck0rz`, `caas_ops`, `caas-soc` |
| Customer request / support | `caas`, `onb-and-caas` |
| What the team discussed today | `caas_team`, `caas-h4ck0rz` |
| Strategic / management decisions | `cloud_platforms-lt`, `tmpl-escalation-temporary-channel` |
| Product releases / versions | `t-caas-team`, `tdi_businessnews` |
| Hardware / datacenter incidents | `caas-soc` |
| Onboarding / new cluster setup | `onb-and-caas` |
| TDI organization-wide news | `tdi_communication`, `tdi_businessnews` |
| PagerDuty alert history | `caas_ops` |

## Cross-Skill Integration

### PagerDuty → Slack (Incident Context)

Enrich PagerDuty incidents with Slack discussion context:

```bash
# 1. Get PD incident details
source .env && .venv/bin/python .claude/skills/pagerduty/scripts/pd-incident-get.py INCIDENT_ID

# 2. Search Slack for related discussion
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-incidents.py --cluster CLUSTER --since 2d
```

### Slack → Jira (Action Items)

After summarizing a channel, use telekom-jira skill to create tickets for action items identified in the discussion.

### Slack + OpenSearch (Full Investigation)

Complete incident investigation combining team discussion + infrastructure logs:

```bash
# 1. Find incident discussion in Slack
source .env && .venv/bin/python ${SKILL_DIR}/scripts/slack-incidents.py --cluster CLUSTER

# 2. Pull infrastructure logs from OpenSearch
source .env && .venv/bin/python .claude/skills/opensearch/scripts/opensearch-search.py --cluster CLUSTER --from 1h --level error
```

### Slack → PDF/PPTX (Reporting)

Generate reports from Slack data using telekom-pdf or pptx skills — daily summaries, incident post-mortems, weekly digests.

### Slack → KB Article

Turn troubleshooting threads into knowledge base articles using the kb-article-writer skill.
