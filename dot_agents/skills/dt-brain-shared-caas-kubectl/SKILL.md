---
name: dt-brain-shared-caas-kubectl
description: Run read-only kubectl commands against CaaS Kubernetes clusters for troubleshooting. Fetches kubeconfig from NetBox automatically. Use when the user mentions "kubectl", "run kubectl", "check pods", "check nodes", "pod status", "node status", "pod logs", "describe pod", "get pods", "get nodes", "top nodes", "top pods", "cluster resources", "read-only kubectl", or needs to run kubectl commands for investigation without making any changes.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/caas-kubectl by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CaaS Read-Only Kubectl

Run read-only kubectl commands against CaaS clusters. Kubeconfig is fetched from NetBox automatically and cleaned up after use.

## ⚠️ READ-ONLY ONLY

This skill enforces a strict allowlist. Only these kubectl subcommands are permitted:

`get`, `describe`, `top`, `logs`, `explain`, `api-resources`, `api-versions`, `cluster-info`, `version`, `events`, `auth can-i`, `auth whoami`

**All mutating commands are blocked** — no apply, create, delete, edit, patch, exec, etc.

## Permissions by Role

The default `caas_sec` role is read-only but has **limited scope**:

| Operation | `caas_sec` (default) | `caas_admin` |
|-----------|---------------------|--------------|
| `get pods`, `get nodes`, `get events` | ✅ | ✅ |
| `describe pod/node` | ✅ | ✅ |
| `top nodes`, `top pods` | ✅ | ✅ |
| **`logs`** (any namespace) | ❌ Forbidden | ✅ |

### Pod Logs Alternative

Since `caas_sec` cannot read pod logs, use **OpenSearch** for `kube-system` pod logs:

```bash
# Get logs for a specific pod (use .keyword for hyphenated names)
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name.keyword:<pod-name-prefix>*'

# Get error logs for etcd pods
source .env && .venv/bin/python .claude/skills/cloud-opensearch/scripts/opensearch-search.py \
  --cluster <cluster> --from 1h \
  --query 'kubernetes.pod_name.keyword:etcd*' --level error
```

**⚠️ OpenSearch limitation:** Only `kube-system` namespace logs are indexed.

## Usage

```bash
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py <cluster-name> <kubectl-args...>
```

### Examples

```bash
# Pod status
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster get pods -A
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster get pods -n kube-system -o wide

# Node status
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster get nodes -o wide
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster describe node <node-name>

# Resource usage
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster top nodes
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster top pods -A --sort-by=memory

# Pod details and logs
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster describe pod <pod> -n <ns>
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster logs <pod> -n <ns> --tail=100
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster logs <pod> -n <ns> --previous --tail=100

# Events
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster get events -A --sort-by='.lastTimestamp'

# Events
source .env && .venv/bin/python .claude/skills/caas-kubectl/scripts/kubectl_ro.py mycluster get events -A --sort-by='.lastTimestamp'
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--role` | `caas_sec` | NetBox secret role: caas_sec, caas_admin, caas_oidc, caas_clab, caas_customer |
| `--kubeconfig` | (none) | Use existing kubeconfig file instead of fetching from NetBox |

## Troubleshooting Runbooks

For step-by-step troubleshooting guides for common alerts (TargetDown, OOMKilled, Node NotReady, etcd, DNS, etc.), see `references/troubleshooting-runbooks.md`.

## Tips

- The `caas_sec` role is read-only by design — use it for all investigations
- **`caas_sec` cannot read pod logs** — use OpenSearch for `kube-system` pod logs instead (see Pod Logs Alternative above)
- Run multiple commands by calling the script multiple times — each invocation fetches and cleans up the kubeconfig independently
- Combine with DDU check (`caas-ddu` skill) for a complete cluster health picture
