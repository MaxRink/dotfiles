---
name: schiff-k8s-agent-mimir-quick-check
description: Quickly assess the health of a Grafana Mimir deployment using the classic gRPC ingest path (distributor → ingester). Covers rollout state, distributor write path (HTTP push errors, ingester push latency/failures), ingester & store-gateway health. Use when investigating Mimir push errors, agent send failures, slow ingestion, or right after a Mimir config/chart change.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/mimir-quick-check by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Mimir Quick Check (classic gRPC ingest)

Read-only skill. Diagnoses; does **not** remediate.

This skill assumes the Mimir deployment uses the **classic gRPC ingest path** (distributor pushes directly to ingesters via gRPC, ingesters write to local TSDB and ship blocks to object storage). There is **no Kafka** in this architecture.

## When to use

- Distributor reports HTTP 5xx on `/api/v1/push`.
- Source `prometheus-agent` / `prometheus` clients log `Failed to send batch, retrying`, `context canceled`, or `server returned HTTP status 500/503`.
- After deploying a Mimir HelmRelease change (config, image, chart) — verify the rolling update completes cleanly and ingest stays healthy.
- Generic "Mimir feels slow" or alerts on `cortex_request_duration_seconds` percentiles.

Do **not** use for query-path-only issues (use a query-focused investigation) or for non-Mimir Prometheus stacks.

## Inputs

- **Mimir cluster context** (required) — kubectl context where Mimir runs, e.g. `schiff-workload-1.az.f`.
- **Mimir namespace** (optional, default `observability-system`).
- Optional: a specific tenant id if a recent error log points at one.

## Procedure

Run phases in order. Stop early once root cause is clear.

### Phase 1 — Topology & rollout state

**Step 1.1** — List all Mimir workloads and rollout state:

```bash
MIMIR=<context>
NS=<namespace>
kubectl --context $MIMIR -n $NS get deploy -l app.kubernetes.io/instance=grafana-mimir
kubectl --context $MIMIR -n $NS get sts  -l app.kubernetes.io/instance=grafana-mimir
kubectl --context $MIMIR -n $NS get hr grafana-mimir -o jsonpath='{.status.history[0].chartVersion}{"\t"}{.metadata.generation}/{.status.observedGeneration}{"\n"}'
```

Look for:

- StatefulSets `READY` < `DESIRED` for `grafana-mimir-ingester` or `grafana-mimir-store-gateway` → rollout in progress.
- Deployments not at full replica count → rollout in progress.
- Pod ages: a mix of "11h" + "few minutes" on `ingester` / `store-gateway` confirms a rolling update orchestrated by `rollout-operator`.
- Newest pod ordinal is highest (StatefulSet rolls highest → lowest in `OrderedReady`).

**Step 1.2** — Identify the cause of an unexpected rollout. The Helm chart adds `checksum/config` annotations on every workload that mounts the Mimir ConfigMap, so any change to the ConfigMap triggers a rollout of **all** Mimir components:

```bash
kubectl --context $MIMIR -n $NS get sts grafana-mimir-ingester      -o jsonpath='{.spec.template.metadata.annotations.checksum/config}{"\n"}'
kubectl --context $MIMIR -n $NS get sts grafana-mimir-store-gateway -o jsonpath='{.spec.template.metadata.annotations.checksum/config}{"\n"}'
kubectl --context $MIMIR -n $NS get deploy grafana-mimir-distributor -o jsonpath='{.spec.template.metadata.annotations.checksum/config}{"\n"}'
```

If all match → all components are reconciling to the same config version.

### Phase 2 — Distributor write path

**Step 2.1** — Tail logs of one (newest) distributor pod:

```bash
DPOD=$(kubectl --context $MIMIR -n $NS get pod -l app.kubernetes.io/component=distributor \
  --sort-by=.metadata.creationTimestamp -o name | tail -1 | cut -d/ -f2)
kubectl --context $MIMIR -n $NS logs $DPOD -c distributor --tail=30
```

Recognise these patterns:

| Log fragment | Meaning |
|---|---|
| `failed pushing to ingester ...: context deadline exceeded` | Ingester slow or overloaded. If concentrated on a single ingester → that pod is unhealthy. |
| `failed pushing to ingester ...: connection refused` / `no such host` | Ingester pod down or just (re)starting; transient during rollout. |
| `at least 2 live replicas required, could only find 1` | Quorum lost on the ingester ring. Critical. |
| `duplicate sample for timestamp` | Source agent retried after partial accept; benign (HTTP 400, sample dropped). |
| `out of order sample` / `sample timestamp out of bounds` | Source clock skew or back-fill; benign per-sample (HTTP 400). |
| `per-user series limit ... exceeded` / `per-metric series limit ... exceeded` | Tenant hit cardinality limit; raise limits or fix source. |

**Step 2.2** — Snapshot HTTP push outcome counters (per pod):

```bash
kubectl --context $MIMIR -n $NS exec $DPOD -c distributor -- \
  wget -qO- http://localhost:8080/metrics 2>/dev/null \
  | grep '^cortex_request_duration_seconds_count{.*api_v1_push'
```

Sample output:

```text
cortex_request_duration_seconds_count{...status_code="200",...} 10660176
cortex_request_duration_seconds_count{...status_code="400",...} 550026
cortex_request_duration_seconds_count{...status_code="499",...} 670
cortex_request_duration_seconds_count{...status_code="500",...} 1840
```

Interpretation:

- `400` = per-sample rejections (duplicate/out-of-order/limit). High rate is **benign** for the platform but indicates source-side issues; investigate offending tenants if it grows.
- `499` = client cancellation; usually source-side timeout.
- `500` = real platform errors. Compute `500 / (200 + 500)`. Should be < 0.1% in steady state. Spikes during a rollout are expected.

**Step 2.3** — **Definitive check**: ingester push latency and failure delta over a fixed window. Cumulative counters since pod start are misleading for steady-state diagnosis; you must measure a delta. The relevant metric is `cortex_distributor_ingester_append_failures_total` and `cortex_distributor_ingester_appends_total`, plus the gRPC client latency histogram:

```bash
DPOD=<chosen distributor pod>
T0=$(kubectl --context $MIMIR -n $NS exec $DPOD -c distributor -- wget -qO- http://localhost:8080/metrics 2>/dev/null)
sleep 60
T1=$(kubectl --context $MIMIR -n $NS exec $DPOD -c distributor -- wget -qO- http://localhost:8080/metrics 2>/dev/null)

# Push outcomes
P200_0=$(echo "$T0" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="200"' | awk '{print $2}')
P200_1=$(echo "$T1" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="200"' | awk '{print $2}')
P500_0=$(echo "$T0" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="500"' | awk '{print $2}')
P500_1=$(echo "$T1" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="500"' | awk '{print $2}')
P400_0=$(echo "$T0" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="400"' | awk '{print $2}')
P400_1=$(echo "$T1" | grep '^cortex_request_duration_seconds_count{.*api_v1_push.*status_code="400"' | awk '{print $2}')
python3 -c "
d200=$P200_1-$P200_0; d500=$P500_1-$P500_0; d400=$P400_1-$P400_0
tot=d200+d500
print(f'push 60s: 200={d200:.0f}, 400={d400:.0f}, 500={d500:.0f}, 5xx_rate={(d500/tot*100 if tot>0 else 0):.3f}%')
"

# Ingester append latency (gRPC client to ingester)
S0=$(echo "$T0" | grep '^cortex_distributor_ingester_appends_total ' | awk '{print $2}')
S1=$(echo "$T1" | grep '^cortex_distributor_ingester_appends_total ' | awk '{print $2}')
F0=$(echo "$T0" | grep '^cortex_distributor_ingester_append_failures_total ' | awk '{print $2}')
F1=$(echo "$T1" | grep '^cortex_distributor_ingester_append_failures_total ' | awk '{print $2}')
python3 -c "
ds=${S1:-0}-${S0:-0}; df=${F1:-0}-${F0:-0}
tot=ds+df
print(f'ingester appends 60s: ok={ds:.0f} ({ds/60:.0f}/s), fail={df:.0f}, fail_rate={(df/tot*100 if tot>0 else 0):.3f}%')
"
```

Healthy reference (per distributor pod under steady production load):

- 5xx rate < 0.1%
- ingester append fail_rate < 0.1%
- p99 of `cortex_distributor_ingester_client_request_duration_seconds_bucket{operation="/cortex.Ingester/Push"}` < 100ms

If `5xx_rate > 1%` or `fail_rate > 1%` sustained → Phase 3.

**Step 2.4** — Inspect effective distributor config:

```bash
kubectl --context $MIMIR -n $NS exec $DPOD -c distributor -- \
  wget -qO- http://localhost:8080/config 2>/dev/null \
  | grep -A 5 -E 'distributor:|ingester_client:'
```

Key knobs: `distributor.remote_timeout` (gRPC push to ingester), `ingester_client.grpc_client_config.max_send_msg_size`, `distributor.max_recv_msg_size`.

### Phase 3 — Ingester health

When the distributor reports failed appends, identify which ingester(s) are slow or unhealthy.

**Step 3.1** — Per-ingester failure breakdown from the distributor:

```bash
kubectl --context $MIMIR -n $NS exec $DPOD -c distributor -- \
  wget -qO- http://localhost:8080/metrics 2>/dev/null \
  | grep '^cortex_distributor_ingester_append_failures_total{' | sort -k2 -t' ' -n -r | head -10
```

If failures concentrate on a single ingester (e.g. `grafana-mimir-ingester-29`) → focus there.

**Step 3.2** — Ingester pod state, resource usage, restarts:

```bash
kubectl --context $MIMIR -n $NS get pod -l app.kubernetes.io/component=ingester -o wide
kubectl --context $MIMIR -n $NS top pod -l app.kubernetes.io/component=ingester --sort-by=cpu | head -10
kubectl --context $MIMIR -n $NS top pod -l app.kubernetes.io/component=ingester --sort-by=memory | head -10
```

Red flags:

- `RESTARTS` > 0 in last hour → recent crash; `kubectl logs --previous`.
- Memory near `limits.memory` → OOM risk; ingesters keep an in-memory head block.
- Skewed CPU (one pod 5+ cores while others < 1) → hashing/tenant skew.

**Step 3.3** — Ingester ring state and recent errors. The ring is exposed via the distributor admin UI; the per-pod logs reveal slow appends and head-compaction issues:

```bash
IPOD=<problematic ingester pod, or any>
kubectl --context $MIMIR -n $NS logs $IPOD --tail=50 \
  | grep -E 'level=(error|warn)|slow|push|compact' | tail -20
```

Common patterns:

| Log fragment | Meaning |
|---|---|
| `slow ingester request` | This ingester is the bottleneck. Check CPU, GC, disk. |
| `failed to flush user` | Object storage write error. Phase 5. |
| `compaction failed` | Local disk full or corrupt; check PVC. |
| `out of order sample` (sampled) | Same as on distributor; benign. |

**Step 3.4** — Ingester ring membership and unhealthy instances. A common cause of distributor 5xx is an ingester that is `Unhealthy`/`LEAVING` in the ring but still being targeted:

```bash
kubectl --context $MIMIR -n $NS port-forward deploy/grafana-mimir-distributor 8080:8080 >/dev/null 2>&1 &
PF=$!
sleep 2
curl -s http://localhost:8080/ingester/ring | grep -E 'ACTIVE|LEAVING|UNHEALTHY|JOINING|PENDING' | sort | uniq -c
kill $PF 2>/dev/null
```

Healthy: all instances `ACTIVE`. Any `UNHEALTHY` for > 1 minute → check the corresponding pod.

### Phase 4 — Store-gateway

Only relevant for query path or if ingesters complain about block uploads. Ingest path itself does not depend on store-gateway.

**Step 4.1** — Store-gateway readiness during rollout:

```bash
kubectl --context $MIMIR -n $NS get pods -l app.kubernetes.io/component=store-gateway --sort-by=.metadata.creationTimestamp
```

Each new pod loads tenant blocks from object storage at startup (logs: `loaded new block`). Expect 1–3 min per pod.

**Step 4.2** — Check if any store-gateway is failing block sync:

```bash
SG=$(kubectl --context $MIMIR -n $NS get pod -l app.kubernetes.io/component=store-gateway -o name | head -1 | cut -d/ -f2)
kubectl --context $MIMIR -n $NS logs $SG --tail=30 | grep -E 'level=(error|warn)|sync|block' | tail -10
```

### Phase 5 — Object storage path (compactor & ingester ship)

If ingesters log `failed to flush user` or compactor falls behind, suspect S3-compatible object storage. Check the compactor:

```bash
CPOD=$(kubectl --context $MIMIR -n $NS get pod -l app.kubernetes.io/component=compactor -o name | head -1 | cut -d/ -f2)
kubectl --context $MIMIR -n $NS logs $CPOD --tail=30 | grep -E 'level=(error|warn)' | tail -10
kubectl --context $MIMIR -n $NS exec $CPOD -- wget -qO- http://localhost:8080/metrics 2>/dev/null \
  | grep -E '^(cortex_compactor_runs_failed_total|thanos_objstore_bucket_operation_failures_total)'
```

`thanos_objstore_bucket_operation_failures_total` increasing → object-store issue (credentials, network, throttling).

### Phase 6 — Source side (optional)

Only if Phases 2–5 are clean but agents still complain. Pick one source `prometheus-agent`:

```bash
APOD=$(kubectl --context <agent-ctx> -n observability-system get pod \
  -l app.kubernetes.io/name=prometheus-agent --no-headers | grep Running | head -1 | awk '{print $1}')
kubectl --context <agent-ctx> -n observability-system exec $APOD -c agent -- \
  wget -qO- http://localhost:9090/metrics 2>/dev/null \
  | grep -E '^prometheus_remote_storage_(highest_timestamp_in_seconds|queue_highest_sent_timestamp_seconds|samples_failed_total|shards_desired) '
```

`now() - queue_highest_sent_timestamp_seconds` is the end-to-end send lag. > 60s means the agent is behind.

## Outputs

Report a short summary:

1. **Rollout state**: components rolling / steady, expected duration if rolling.
2. **Distributor**: push 5xx rate (last 60s), ingester append fail rate.
3. **Ingester**: ring membership (any UNHEALTHY?), restarts, hot pods.
4. **Store-gateway / compactor**: sync errors, object-store failures.
5. **Suspected root cause** (if any) plus the single most relevant log line / metric value.

## References

- Mimir architecture (classic): `https://grafana.com/docs/mimir/latest/references/architecture/`
- Known patterns from past incidents in the `mcp-kb` knowledge base — query with `kb_search_incidents` using `affected_component=grafana-mimir`.
