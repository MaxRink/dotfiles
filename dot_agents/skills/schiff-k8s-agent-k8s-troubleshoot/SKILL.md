---
name: schiff-k8s-agent-k8s-troubleshoot
description: Diagnose common Kubernetes workload and node problems using a symptom-based playbook. Use when pods are unhealthy, nodes are NotReady, services are unreachable, or deployments are stuck.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/k8s-troubleshoot by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Kubernetes Troubleshooting Playbook

Use this skill when diagnosing workload or node problems on a Kubernetes cluster. Start from the observed symptom and follow the recommended first steps.

## Symptom lookup

| Symptom | First steps |
|---|---|
| Pod `CrashLoopBackOff` | `kubectl logs <pod> -n <ns> --previous --tail=200`, check exit code via `kubectl describe pod` |
| Pod `Pending` | Check node resources (`kubectl describe node`), PVC binding (`kubectl get pvc -n <ns>`), tolerations, node selectors, affinity rules |
| Pod `ImagePullBackOff` | Verify image name/tag, check imagePullSecrets exist and are valid, test registry connectivity |
| Pod `OOMKilled` | Check resource limits/requests (`kubectl describe pod`), review recent memory metrics via Prometheus/Grafana |
| Pod `Init:Error` / `Init:CrashLoopBackOff` | Check init container logs: `kubectl logs <pod> -n <ns> -c <init-container> --previous` |
| Service unreachable | Verify endpoints exist (`kubectl get endpoints <svc> -n <ns>`), check selector labels match pod labels, review NetworkPolicy |
| Deployment not rolling out | `kubectl rollout status deployment/<name> -n <ns>`, check ReplicaSet events, look for quota or scheduling issues |
| Node `NotReady` | `kubectl describe node <node>`, check kubelet status, containerd/CRI status, disk/memory pressure conditions |
| RBAC denied | `kubectl auth can-i <verb> <resource> -n <ns> --as=<user>`, check RoleBinding/ClusterRoleBinding |
| PVC stuck `Pending` | Check StorageClass exists, PV availability, CSI driver health |
| Helm release `failed` | `helm history <release> -n <ns>`, `helm get values <release> -n <ns>`, check HelmRelease events if using Flux |

## Diagnostic flow

1. **Gather context**: `kubectl get events -n <ns> --sort-by='.lastTimestamp'` to see recent cluster events.
2. **Inspect the resource**: `kubectl describe <resource> <name> -n <ns>` for conditions, events, and status.
3. **Check logs**: `kubectl logs <pod> -n <ns> --tail=200` (add `--previous` for crashed containers).
4. **Check resource pressure**: `kubectl top pods -n <ns>`, `kubectl top nodes`.
5. **Check dependencies**: ConfigMaps, Secrets, PVCs, Services that the workload depends on.
6. **Search KB**: Use `kb_search_incidents` to find similar past incidents before deep-diving.

## Known recurring patterns

| Pattern | Root cause | Fix |
|---|---|---|
| ImagePullBackOff blocking PDB | Artifactory `401 Unauthorized` on `artifactory.devops.telekom.de` — credentials expired/rotated | Rotate imagePullSecret in affected namespace |
| Single-replica PDB deadlock | `replicas=1` + `minAvailable=1` — replacement pod can't be scheduled before old one is evicted | Temporarily scale to 2 replicas, or patch PDB to `minAvailable=0` during drain |
| Dual PDB conflict | Legacy PDB selectors are a subset of newer Helm-managed pod labels — pods match both simultaneously | Delete the legacy PDB; eviction API only supports one PDB per pod |
| CrashLoopBackOff blocking PDB | Application misconfiguration (e.g. invalid S3/object-store credentials) keeps replacement pod unhealthy | Fix the underlying app config (secret/credentials); pod recovers and PDB allows disruption |

## After resolution

Once root cause and fix are identified, store the incident in the knowledge base using the `kb-workflow` skill.
