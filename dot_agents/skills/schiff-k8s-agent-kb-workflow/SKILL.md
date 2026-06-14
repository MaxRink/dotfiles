---
name: schiff-k8s-agent-kb-workflow
description: Search and store incidents in the mcp-kb knowledge base. Use at the start of every incident investigation (search) and after resolution (store).
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/kb-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Knowledge Base Workflow

All incident investigations must be integrated with the `mcp-kb` knowledge base. This skill defines when and how to search and store incidents.

## At the start of every investigation

Before diagnosing a new alert or incident, search the knowledge base for similar past incidents:

```text
kb_search_incidents(query="<alert name> <symptom>", affected_component="<cluster/component>")
```

Use the results to:

- Identify known root causes and skip redundant investigation steps.
- Apply proven resolutions directly when the pattern matches.
- Note any differences from past incidents before applying a fix.

## At the end of every resolved investigation

Once the root cause is identified and resolution is known, store the incident:

```text
kb_store_incident(
  title=           # short descriptive title, e.g. "MachineDeploymentStuck on a4-3-md-0: Dual PDB conflict"
  description=     # full symptoms: alert, stuck node, drain start time, blocking pods, PDB state
  affected_component= # "cluster/<name>, node/<name>, namespace/resource"
  alert_name=      # Prometheus/Alertmanager alert name
  environment=     # prod | preprod | av | playground
  severity=        # Critical | Major | Minor | Uncritical
  root_cause=      # detailed explanation of why the failure occurred
  resolution=      # concrete steps to fix it
  occurred_at=     # RFC3339 drain/failure start time from CAPI or logs
  tags=            # comma-separated: e.g. "node-drain,pdb,imagepullbackoff,artifactory"
  runbook_url=     # link to relevant runbook if available
)
```

Store even when the fix has not yet been applied — document the finding so future investigations benefit.

## When to search

- At the start of any incident or alert investigation
- When encountering an unfamiliar error pattern
- Before escalating — check if the team already solved this before

## When to store

- After identifying root cause of any incident (even if fix is not yet applied)
- After resolving an incident with a new or non-obvious fix
- When discovering a new failure pattern that may recur

## Tips

- Use specific alert names and component names in search queries for better matches.
- Include tags when storing to improve future search relevance.
- Reference runbook URLs when available.
- Use `kb_stats` to check overall KB health and coverage.
