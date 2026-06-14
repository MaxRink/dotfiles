---
name: schiff-k8s-agent-alert-hunting
description: Fetch and triage all active alerts from Alertmanager, build a prioritized list with actionable suggestions, and optionally silence alerts. Use when doing alert reviews, on-call handovers, or proactive alert triage sessions.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/alert-hunting by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Alert Hunting

Structured workflow for triaging all firing alerts, prioritizing them, suggesting next steps, and documenting findings in the knowledge base.

## When to use

- Start-of-shift / on-call handover — get a full picture of what is firing.
- Periodic alert review — clean up noise, identify patterns, act on real issues.
- After a change / upgrade — check if new alerts appeared.
- User says "alert hunting", "triage alerts", "what's firing", or similar.

## Inputs

- **Alertmanager filters** (optional) — label matchers to narrow scope, e.g. `severity=critical`, `cluster=ship-prod-1`.
- **Cluster context** (optional) — if alerts should be correlated with a specific cluster.

## Procedure

### Phase 1 — Fetch active, unsuppressed alerts only

By default, fetch **only active (non-silenced, non-inhibited) alerts** to keep the result set small and actionable. Suppressed alerts are noise for daily work.

```text
alertmanager_list_alerts(active=true, silenced=false, inhibited=false)
```

If the user provided additional filters, add them:

```text
alertmanager_list_alerts(active=true, silenced=false, inhibited=false, filter=["severity=critical", "cluster=ship-prod-1"])
```

If the user explicitly asks to include suppressed/silenced alerts, drop the `silenced=false` and `inhibited=false` flags.

### Phase 2 — Deduplicate and group

Group the raw alerts by:

1. **alertname** — collapse identical alert names firing for multiple targets.
2. **severity** — critical > warning > info.
3. **namespace / cluster** — group by blast radius.

For each unique alert group, record:

- Alert name
- Severity
- Number of instances firing
- Since when (earliest `startsAt`)
- Affected labels (cluster, namespace, pod, node, etc.)

### Phase 3 — Search KB for known patterns

For each unique alert group, search the knowledge base:

```text
kb_search_incidents(query="<alertname> <key symptom>", affected_component="<cluster/component>")
```

Note any matches — these alerts may have known root causes and resolutions.

### Phase 4 — Build prioritized alert table

Present a table sorted by priority (severity first, then age, then instance count):

| # | Severity | Alert | Count | Since | Affected | KB Match | Suggestion |
|---|----------|-------|-------|-------|----------|----------|------------|
| 1 | critical | ... | ... | ... | ... | Yes/No | ... |
| 2 | warning | ... | ... | ... | ... | Yes/No | ... |

Priority rules:

1. **critical** alerts always come first.
2. Within same severity, older alerts rank higher (longer unresolved = higher risk).
3. Within same severity+age, higher instance count ranks higher.
4. Alerts with no KB match rank higher (unknown = needs attention).

### Phase 5 — Actionable suggestions

For each alert group, provide a concrete suggestion:

- **KB match found**: Reference the past incident and suggest applying the known resolution. Quote the KB entry ID.
- **No KB match**: Suggest diagnostic steps based on the alert type using the Common Problem-Solving Playbook from AGENTS.md.
- **Noise / expected**: If the alert is clearly informational or expected (e.g. during a known maintenance window), suggest silencing.

### Phase 6 — Create KB entries (only for resolved incidents)

Do **NOT** create KB entries during the alert hunt itself. KB entries are only created when an incident has been fully investigated and a root cause + resolution are known. Use the `kb-workflow` skill for that.

Alert hunting is a triage activity — it identifies and prioritizes work, but does not produce resolutions.

### Phase 7 — Silence creation (on request)

Only create silences when the user explicitly asks.

#### Read author identity

Read the author identity from `~/.gitconfig`:

```bash
git config --global user.name
git config --global user.email
```

Use the result as the `author` parameter. Prefer `"Name <email>"` format. If only one is available, use that.

#### Create the silence

Call `alertmanager_create_silence`:

```text
alertmanager_create_silence(
  matchers=["alertname=<name>", "<additional matchers>"],
  author="<name from gitconfig> <email from gitconfig>",
  comment="<reason for silencing, reference alert hunt>",
  duration="<user-specified or default 1h>"
)
```

#### Document the silence

Update or create a KB entry for the alert noting the silence.

## Output format

Always end with a summary:

```text
Alert Hunting Summary
=====================
Total active alerts: <N>
Unique alert groups:  <N>
  Critical: <N>
  Warning:  <N>
  Info:     <N>

KB matches found:     <N> (known patterns)
Silences created:     <N>

Top action items:
1. <most urgent action>
2. <second most urgent>
3. <third most urgent>
```
