---
name: schiff-k8s-agent-document-upgrade-wave
description: Systematically record every alert, issue, or incident related to a Kubernetes upgrade wave (bundle/k8s version rollout, node rolls, OS upgrades) in the `mcp-kb` knowledge base so future waves can be compared, reported on, and pattern-matched.
license: MIT
compatibility: opencode
metadata:
  audience: devops
  workflow: upgrade-wave-documentation
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/document-upgrade-wave by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Document K8s Upgrade Wave in KB

## Purpose

During a Kubernetes upgrade wave (k8s version bump, bundle rollout, node-image refresh, OS patching, CAPI machine roll), the fleet generates a long tail of related alerts and incidents. If each event is filed ad-hoc, situation-room reports have to be rebuilt from scratch every time and patterns across waves are lost.

**Rule:** every alert, issue, or incident that is *caused by* or *surfaced during* an upgrade wave MUST be stored in `mcp-kb` with a consistent schema. This skill defines that schema and the workflow.

## When to apply this skill

Trigger this workflow whenever any of the following is true:

- A Jira ticket exists for a rollout (e.g. `rollout k8s 1.34 ref`, `bundle 1.34.9`, `node roll prod`).
- An alert fires on a cluster whose `tcaas_bundle` label matches the version being rolled out.
- A node is being drained/cordoned as part of a CAPI `MachineDeployment` roll.
- A Flux `HelmRelease` / `Kustomization` fails reconciliation after a bundle bump.
- Symptoms match known upgrade-related patterns: `KubeDaemonSetRolloutStuck`, `MachineStuck`, `MachineDeploymentStuck`, `WorkerNodesUnavailable*`, `CPNodesUnavailable`, `KubeNodeNotReady` shortly after a roll.

If the event is clearly unrelated to the wave (e.g. app-level OOM on an already-upgraded cluster, expired Artifactory credentials, hardware defect), document it with a normal incident record — **not** under the wave tag.

## Identify the wave

Each wave must have a stable identifier used across all KB entries. Compose it as:

```text
wave/<env>/<component>-<version>
```

Examples:

- `wave/ref/k8s-1.34`
- `wave/prod/bundle-1.33.20`
- `wave/ref/node-roll-ubuntu-22.04.5`

Record this identifier in the `tags` field of every related KB entry (comma-separated with other tags). If a Jira rollout ticket exists (e.g. `SCHIFF-2755`), include it as a tag too: `jira-schiff-2755`.

## Workflow

### 1. Gather evidence before storing

For each alert or issue, collect:

- **Alert details** from `alertmanager_list_alerts` (alertname, cluster, namespace, startsAt, labels.tcaas_bundle, silencedBy).
- **Affected resource** from the cluster (`kubectl describe` on the stuck DaemonSet/Machine/HelmRelease/Node).
- **Upgrade linkage** — which step of the wave was running at `startsAt`? (bundle version being applied, machine being rolled, node being drained).
- **Blast radius** — how many pods/nodes/tenants impacted.

### 2. Store the record in mcp-kb

Call `kb_store_incident` with the fields below. Be strict about the schema so later searches and reports work.

```text
kb_store_incident(
  title=          # "[wave/<env>/<component>-<ver>] <symptom> on <cluster>"
                  # e.g. "[wave/ref/k8s-1.34] KubeDaemonSetRolloutStuck whereabouts on t5g-1.ref.ffm1"
  description=    # Full context:
                  # - Alert name(s) + fingerprint(s)
                  # - startsAt / endsAt (UTC, RFC3339)
                  # - Cluster FQDN, namespace, workload
                  # - tcaas_bundle before/after
                  # - What was running at the time (drain, HelmRelease upgrade, etc.)
                  # - Observed symptoms (pod status, event log excerpt)
  affected_component=  # "cluster/<fqdn>, <kind>/<name>"
                       # e.g. "cluster/t5g-1.ref.ffm1.schiff.telekom.de, daemonset/kube-system/whereabouts"
  alert_name=     # The Prometheus alertname (single most relevant one)
  environment=    # prod | preprod | av | playground | ref
  severity=       # Critical | Major | Minor | Uncritical
                  # Map from alert label `severity` (critical→Critical, major→Major, warning→Minor)
  root_cause=     # Technical root cause if known; otherwise "Under investigation — <wave-id>"
  resolution=     # Concrete fix applied; "Pending" if not yet resolved
  occurred_at=    # Alert startsAt
  resolved_at=    # Alert endsAt once cleared (omit if still firing)
  tags=           # MUST contain the wave id + jira ticket + symptom tags
                  # e.g. "wave/ref/k8s-1.34,jira-schiff-2755,daemonset-stuck,whereabouts,bm4x"
  runbook_url=    # Alert's runbook_url if provided
  reported_by=    # "alertmanager" | "<user>" | "situation-room"
)
```

### 3. Update the record as things evolve

- When the alert clears, store a follow-up with `resolved_at`, `resolution`, and the confirmed `root_cause`.
- If the same alert flaps on the same cluster during the same wave, append to the description of the existing record (search first via `kb_search_incidents` with the wave tag + alert name + cluster) instead of creating duplicates.
- When the root cause is identified, backfill all related records sharing the wave id so future searches converge on the same explanation.

### 4. Wave closure entry

When the wave is complete (all targeted clusters upgraded), store a summary record:

```text
kb_store_incident(
  title="[wave/<env>/<component>-<ver>] Wave closure summary"
  description=   # - Start / end dates
                 # - Clusters targeted + completed
                 # - Total related alerts captured (count by alertname)
                 # - Confirmed root causes
                 # - Mitigations applied
                 # - Carry-over issues to next wave
  affected_component="environment/<env>"
  alert_name="WaveClosure"
  environment=<env>
  severity=Uncritical
  root_cause="n/a — summary entry"
  resolution="Wave completed"
  occurred_at=<wave-start>
  resolved_at=<wave-end>
  tags="wave/<env>/<component>-<ver>,jira-<ticket>,wave-summary"
  reported_by="situation-room"
)
```

This single record becomes the anchor that links all individual incidents.

## Generating reports from the KB

When asked for a situation-room or wave report, do:

1. `kb_search_incidents(query="<wave-id>", tags="<wave-id>")` — pull all records for the wave.
2. Group by `alert_name` and `affected_component` → build the alert matrix.
3. Pull the wave closure record (if exists) for the executive summary.
4. Cross-reference with current `alertmanager_list_alerts` filtered by `tcaas_bundle` / `tcaas_platform_environment` to spot anything not yet captured — and capture it per §2.

This way every report starts from the KB, not from raw Alertmanager output.

## Do / Don't

**Do:**

- Tag every wave-related record with the same `wave/<env>/<component>-<ver>` identifier.
- Store even unresolved issues — mark `resolution="Pending"` and update later.
- Link the Jira rollout ticket via a tag.
- Map `severity` labels consistently (alertmanager `major` → KB `Major`, `critical` → `Critical`, `warning` → `Minor`).

**Don't:**

- Don't create one KB entry per alert instance if the alert is flapping on the same object — consolidate.
- Don't tag unrelated incidents with the wave id just because they happened in the same week. The wave tag is reserved for events *caused by or surfaced during* the upgrade.
- Don't skip the wave closure record — without it, retro analysis is painful.

## Example

Alert: `KubeDaemonSetRolloutStuck` on `t5g-1.ref.ffm1`, daemonset `kube-system/whereabouts`, startsAt `2026-04-24T04:59:22Z`, cluster bundle `1.34.9`, Jira `SCHIFF-2755`.

```text
kb_store_incident(
  title="[wave/ref/k8s-1.34] KubeDaemonSetRolloutStuck whereabouts on t5g-1.ref.ffm1",
  description="Alert KubeDaemonSetRolloutStuck fired at 2026-04-24T04:59:22Z after bundle bump to 1.34.9. DaemonSet kube-system/whereabouts has not progressed for >15min. Cluster was mid-roll (node t5g-1-ffm1-md-0-xxx drained at 04:54Z). Observed: 2/3 pods Running, 1 pod Pending with 'node(s) had untolerated taint'. Other DaemonSets on same node also stuck (schiff-fluentbit).",
  affected_component="cluster/t5g-1.ref.ffm1.schiff.telekom.de, daemonset/kube-system/whereabouts",
  alert_name="KubeDaemonSetRolloutStuck",
  environment="ref",
  severity="Major",
  root_cause="Under investigation — wave/ref/k8s-1.34",
  resolution="Pending",
  occurred_at="2026-04-24T04:59:22Z",
  tags="wave/ref/k8s-1.34,jira-schiff-2755,daemonset-stuck,whereabouts,bm4x,node-roll",
  reported_by="alertmanager"
)
```

Once resolved, a follow-up store adds `resolved_at`, `resolution`, and updates `root_cause`.
