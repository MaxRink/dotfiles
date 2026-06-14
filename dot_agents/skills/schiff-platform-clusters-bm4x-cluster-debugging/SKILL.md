---
name: schiff-platform-clusters-bm4x-cluster-debugging
description: 'Debug BM4X bare-metal T-CaaS cluster bootstrap failures. USE WHEN: cluster bootstrap fails, control plane not initializing, nodes unreachable, FunctionInstances failing, kubeadm errors, kubelet not starting, CAPI machine stuck. Keywords: BM4X, bootstrap, control plane, kubeadm, kubelet, CAPI, Redfish, TCaasCluster, KubeadmControlPlane, FunctionInstance, cloud-init.'
---

<!-- Imported from schiff/platform/clusters/.github/skills/bm4x-cluster-debugging by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# BM4X Cluster Debugging

## Overview

BM4X clusters use bare-metal nodes managed via Redfish/iLO BMCs. Debugging requires checking multiple layers: management cluster controllers, CAPI state, BMC hardware, node OS, and Kubernetes bootstrap.

## Debugging Workflow

### 1. Get Cluster Status

```bash
./scripts/status.sh                    # Full status overview
./scripts/watch-cluster.sh 5           # Live polling every 5 seconds
```

Key things to check:
- `TCaasCluster` phase and conditions
- `KubeadmControlPlane` initialized/ready status, replica count
- `Machine` phases (Provisioning → Provisioned → Running)
- `RedfishMachine` state and hostRef
- `FunctionInstance` statuses (Deploying, Failed, WaitingForDependencies)

### 2. Check Controller Logs

```bash
./scripts/logs.sh tco                  # T-CO operator logs
./scripts/logs.sh capi                 # CAPI controller logs
./scripts/logs.sh kcp                  # KubeadmControlPlane controller
./scripts/logs.sh bootstrap            # Bootstrap controller
./scripts/logs.sh caprf                # CAPRF (Redfish provider) logs
./scripts/logs.sh all                  # All controllers
```

**What to look for:**
- `context deadline exceeded` → API endpoint unreachable
- `connection refused` → kubelet/apiserver not running
- `certificate` errors → PKI issues
- `not found` → missing resources (FDs, secrets, profiles)

### 3. Check Node Hardware

```bash
./scripts/bmc-power.sh status          # Is the server powered on?
# Via Redfish API:
# Check .PowerState, .Status.Health, .PostState
```

### 4. Check Node OS (Serial Console)

If the node is unreachable via SSH, use BMC serial console:

```bash
./scripts/bmc-console.sh               # Connect to serial console
# Or automated evidence collection:
./scripts/bmc-evidence.sh              # Gather all diagnostics
```

**Critical checks on the node:**
```bash
# Is kubelet running?
sudo systemctl status kubelet
sudo journalctl -u kubelet -n 100

# Did cloud-init complete?
cloud-init status --long
cat /var/log/cloud-init-output.log | tail -200

# Does bootstrap success marker exist?
ls -la /run/cluster-api/bootstrap-success.complete

# Container runtime
sudo crictl ps -a
sudo crictl pods

# Network state
ip addr show
ip route show
ip -6 route show
cat /etc/resolv.conf

# Static pod manifests (should contain kube-apiserver, etcd, etc.)
ls -la /etc/kubernetes/manifests/
```

### 5. Take Diagnostic Snapshots

Always snapshot before and after making changes:

```bash
./scripts/snapshot.sh "before-fix"     # Before
# ... apply fix ...
./scripts/snapshot.sh "after-fix"      # After
```

## Common Failure Patterns

### Control Plane Not Initializing

**Symptoms:**
- KCP `Initialized=False`, 0 ready replicas
- Machine is `Provisioned` but no `nodeRef`
- API endpoint unreachable: `context deadline exceeded`

**Root causes:**
1. **Node network misconfigured** — BGP not peering, VLAN not tagged, no IPv6 route
2. **kubeadm init failed** — check `journalctl -u kubelet` on node
3. **etcd won't start** — disk issues, timeout waiting for peers
4. **Cloud-init didn't complete** — check `/var/log/cloud-init-output.log`
5. **Bootstrap data not applied** — check `/run/cluster-api/`
6. **kube-vip-pull.service failing** — check `systemctl status kube-vip-pull.service` (blocks kubelet via `Requires=` dependency)
7. **kube-vip BGP crash** — IPv6 `--bgppeers` parsing fails; use env vars instead of CLI flags
8. **BGP peer address wrong** — `bgp_peers` points to network address `fd00:7:caa5::` instead of VSR gateway `fd00:7:caa5:1::` (see HBN architecture section)
9. **Management cluster routing** — CAPI/KCP pods on some mgmt worker nodes can't reach workload VIPs due to EVPN/VXLAN route propagation delays or asymmetric connectivity. Flux on another node may work fine. Try restarting CAPI pods to reschedule. The mgmt cluster is **vSphere-based** (no HBR) — SSH directly into mgmt worker nodes to test connectivity.

### Debugging from Management Cluster Nodes

The management cluster is vSphere-based (not BM4X), so nodes are regular VMs accessible via SSH — no BMC/VSP needed.

```bash
# Find which mgmt node the failing pod runs on
kubectl get pod -n capi-system -l control-plane=controller-manager -o wide
# SSH to that mgmt worker node and test direct connectivity to workload VIP
ssh <mgmt-worker-ip>
ping6 <workload-VIP>
curl -6sk https://[<workload-VIP>]:6443/healthz
# Compare with a node where Flux works
kubectl get pod -n t-caas-controllers -l app=kustomize-controller -o wide
```

### kube-vip BGP IPv6 Crash

**Symptoms:**
- kube-vip crashloops with: `"creating BGP server: you need to provide at least one peer"`
- Happens when `--bgppeers` flag contains IPv6 addresses like `[fd00:7:caa5:1::]`

**Root cause:** kube-vip v1.1.2 `--bgppeers` flag uses colon-delimited format (`address:as:password:multihop`) which conflicts with IPv6 colons in brackets.

**Fix:** Use environment variables instead of CLI flags for BGP config:
```yaml
env:
  - name: bgp_enable
    value: "true"
  - name: bgp_peers
    value: "[fd00:7:caa5:1::]:65169::false/mpbgp_nexthop=fixed"
  - name: bgp_as
    value: "65170"
  # ... etc
```

**Note:** The BGP peer (`fd00:7:caa5:1::`) is the **HBR/VSR (CRA — 6WIND Container Routing Agent)** running on the same physical host. It is NOT a ToR switch. See the HBN architecture section below.

### HBN / BGP Architecture (VSR/HBR/CRA)

BM4X nodes use **Host-Based Networking (HBN)** with a **VSR/HBR (Virtual Service Router / Host-Based Router)** — a 6WIND Container Routing Agent (CRA) running on the same bare-metal host:

- **`hbn` interface**: The node's primary network interface, provided by the VSR container
- **ULA addresses on hbn**:
  - `fd00:7:caa5::1/128` — the K8s node
  - `fd00:7:caa5:1::/128` — the VSR/HBR gateway (also the default route)
- **Default route**: `default via fd00:7:caa5:1:: dev hbn` — all traffic exits through the VSR
- **BGP peering**: kube-vip (AS 65170) peers with VSR (AS 65169). The VSR runs in **passive mode** — it waits for the node to initiate the BGP session at `fd00:7:caa5:1::` port 179
- **Route propagation**: VSR redistributes VIP routes into the EVPN/VXLAN fabric via BGP route reflectors

**Common mistake:** Using `fd00:7:caa5::` (the network/subnet address) as the BGP peer instead of `fd00:7:caa5:1::` (the VSR gateway). This causes BGP sessions to stay in ACTIVE state indefinitely because there's no host at `fd00:7:caa5::`.

**Debugging BGP on node:**
```bash
# Check kube-vip logs (log level 0 = most verbose)
echo PASSWORD | sudo -S cat /etc/kubernetes/manifests/kube-vip.yaml | grep -A1 bgp_peers
echo PASSWORD | sudo -S crictl logs $(echo PASSWORD | sudo -S crictl ps -q --name kube-vip) 2>&1 | tail -20

# Verify BGP session state (look for ESTABLISHED)
# States: IDLE → ACTIVE → OPENSENT → OPENCONFIRM → ESTABLISHED

# Test connectivity to VSR
ping6 -c3 fd00:7:caa5:1::   # Should succeed (VSR gateway)
ping6 -c3 fd00:7:caa5::     # Will FAIL (network address, no host)

# Check VIP assignment
ip addr show lo | grep -E '10\.|2a01'   # VIPs should be on loopback
```

### kube-vip-pull.service Failure (Blocks kubelet)

**Symptoms:**
- `[FAILED] Failed to start kube-vip-pull.service`
- `[DEPEND] Dependency failed for kubelet.service`
- kubelet never starts because of `Requires=kube-vip-pull.service`

**Root causes:**
1. **Missing `[Unit]` section** — `After=network-online.target` placed in `[Service]` section is silently ignored by systemd
2. **`ctr` without `--hosts-dir`** — `ctr images pull` doesn't use containerd's `/etc/containerd/certs.d/` registry mirrors by default, leading to DNS resolution failures (like `no such host`) even when DNS works otherwise
3. **Registry unreachable** — DNS/network not ready, or auth required
4. **Service starts before network** — without proper `[Unit]` ordering, ctr may run before DNS is available

**Fix on node:**
```bash
# Quick workaround: manually pull the image and start kubelet
echo PASSWORD | sudo -S ctr --namespace=k8s.io images pull --hosts-dir /etc/containerd/certs.d <image>
echo PASSWORD | sudo -S systemctl reset-failed kube-vip-pull.service
echo PASSWORD | sudo -S systemctl start kube-vip-pull.service
echo PASSWORD | sudo -S systemctl reset-failed kubelet
echo PASSWORD | sudo -S systemctl start kubelet
```

**Note:** When operating through serial console (VSP), use `echo PASSWORD | sudo -S cmd` pattern — heredocs and herestrings don't work through VSP.

**Permanent fix:** Ensure the systemd unit has proper sections:
```ini
[Unit]
Description=Pre-pull kube-vip container image
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=ctr --namespace=k8s.io images pull --hosts-dir /etc/containerd/certs.d <image>
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

### Kubelet Race Condition with kubeadm

**Symptoms:**
- kubelet crashloops, then gets rate-limited by systemd
- kubeadm's `systemctl start kubelet` fails because unit is in "failed" state
- `/var/log/cloud-init-output.log` shows kubeadm errors

**Root cause:** Cloud-init enables kubelet before kubeadm creates config. kubelet crashes, systemd rate-limits it, kubeadm can't restart it.

**Fix on node:**
```bash
sudo systemctl reset-failed kubelet
sudo systemctl start kubelet
```

### Cluster Deletion Stuck (FunctionInstance Finalizers)

**Symptoms:**
- TCaasCluster stuck in `Deleting` phase
- FunctionInstances all stuck in `Deleting` with finalizers
- Operator logs show template rendering errors (missing secrets)

**Root cause:** FI deletion reconciler tries to render deletion manifests using secrets that were never created (cluster never fully bootstrapped).

**Fix:** Clear finalizers on all stuck FIs:
```bash
for fi in $(kubectl get fi -n $CLUSTER_NS -o jsonpath='{.items[*].metadata.name}'); do
  kubectl patch fi "$fi" -n $CLUSTER_NS --type=merge -p '{"metadata":{"finalizers":[]}}'
done
```

### Missing FunctionDefinition

**Symptoms:**
- FunctionInstance in `Failed` state
- Error: `functiondefinitions.t-caas.telekom.com "xxx" not found`

**Fix:**
1. Check if the FD exists: `kubectl get fd -n t-caas-operator-system | grep <name>`
2. If missing, create it from the bundles repo or functions repo
3. Apply: `kubectl apply -f <fd-file>.yaml`
4. The bundle references FDs by name — ensure `metadata.name` matches exactly

### FunctionInstance WaitingForDependencies

**Symptoms:**
- Most FIs stuck in `WaitingForDependencies`

**Root cause:** Usually a cascade — one upstream function is failing, blocking everything downstream. Check `spec.dependencies.requires` on the failing FIs to find the root.

### Flux Source Not Ready

**Symptoms:**
- FunctionInstance has error about source not ready
- `OCIRepository` or `GitRepository` in failed state

**Fix:**
1. Check the source: `kubectl get ocirepository -A` or `gitrepository -A`
2. Look at conditions for auth/network errors
3. May need to fix registry credentials or source URL

## Management Cluster Resources

| Resource | Namespace | Short Name |
|----------|-----------|------------|
| TCaasCluster | cluster NS | `tcc` |
| Bundle | `t-caas-operator-system` | `bund` |
| FunctionDefinition | `t-caas-operator-system` | `fd` |
| FunctionInstance | cluster NS | `fi` |
| SharedConfig | `t-caas-operator-system` | `shc` |
| KubeadmControlPlane | cluster NS | `kcp` |
| Machine | cluster NS | - |
| RedfishMachine | cluster NS | - |
| RedfishHost | infra NS | - |
| ClusterNetwork | cluster NS | - |

## Useful kubectl Commands

```bash
# Quick FI status overview
kubectl get fi -n $CLUSTER_NS -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,MSG:.status.conditions[0].message'

# Check which FDs a bundle references
kubectl get bundle <name> -n t-caas-operator-system -o jsonpath='{.spec.functions[*].name}' | tr ' ' '\n'

# Get machine details
kubectl get machine -n $CLUSTER_NS -o wide

# Check CAPI cluster status
kubectl get cluster -n $CLUSTER_NS -o jsonpath='{.status.conditions}' | jq

# Get KCP conditions
kubectl get kcp -n $CLUSTER_NS -o jsonpath='{.items[0].status.conditions}' | jq

# Events sorted by time
kubectl get events -n $CLUSTER_NS --sort-by='.lastTimestamp' | tail -30
```

## Workflow: Fix and Iterate

```bash
# 1. Suspend Flux to prevent overwriting changes
./scripts/flux-suspend.sh suspend

# 2. Snapshot current state
./scripts/snapshot.sh "pre-fix-1"

# 3. Apply fix
kubectl apply -f path/to/fix.yaml

# 4. Restart operator to pick up changes
./scripts/restart-operator.sh

# 5. Watch progress
./scripts/watch-cluster.sh 5

# 6. Snapshot after fix
./scripts/snapshot.sh "post-fix-1"

# 7. When done, resume Flux
./scripts/flux-suspend.sh resume
```

**Important:** `kubectl apply/patch` changes will be overwritten by Flux if the resource is managed by a Flux Kustomization with `prune: true`. For permanent fixes, commit changes to the source Git repo and let Flux reconcile. Only use direct `kubectl` for emergency/temporary fixes while also preparing the proper Git-based fix.

## etcd Direct Access (Emergency Recovery)

When resources are stuck in states that can't be fixed via the Kubernetes API (e.g., stuck `Terminating` namespaces, resources with `deletionTimestamp` that can't be removed), use etcd directly.

### Setup

```bash
# Deploy an etcd helper pod with certs
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: etcd-helper
  namespace: kube-system
spec:
  containers:
  - name: etcd
    image: bitnami/etcd:3.5
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: etcd-certs
      mountPath: /certs
  volumes:
  - name: etcd-certs
    hostPath:
      path: /etc/kubernetes/pki/etcd
  nodeName: <control-plane-node>
EOF

# Port-forward
kubectl port-forward -n kube-system etcd-helper 2479:2379

# Copy certs locally
kubectl cp kube-system/etcd-helper:/certs/ca.crt /tmp/etcd-ca.crt
kubectl cp kube-system/etcd-helper:/certs/server.crt /tmp/etcd-server.crt
kubectl cp kube-system/etcd-helper:/certs/server.key /tmp/etcd-server.key

# Set alias
alias etcdctl='~/go/bin/etcdctl --endpoints=https://localhost:2479 \
  --cacert=/tmp/etcd-ca.crt --cert=/tmp/etcd-server.crt --key=/tmp/etcd-server.key'
```

### Install auger (protobuf decoder)

```bash
go install github.com/etcd-io/auger@latest
```

### Key Formats

| Resource Type | etcd Key Pattern |
|---------------|------------------|
| Core resources (Namespace, Pod, etc.) | `/registry/<resource>/<namespace>/<name>` or `/registry/<resource>/<name>` |
| CRDs (TCaasCluster, FI, etc.) | `/registry/<apigroup>/<resource>/<namespace>/<name>` |
| Namespaces | `/registry/namespaces/<name>` (no group prefix) |

### Common Operations

```bash
# Read a resource (core = protobuf, CRDs = JSON)
etcdctl get /registry/namespaces/<name> --print-value-only | auger decode

# Read a CRD resource (stored as JSON, no auger needed)
etcdctl get /registry/t-caas.telekom.com/tcaasclusters/<ns>/<name> --print-value-only | python3 -m json.tool

# Remove deletionTimestamp from a namespace (protobuf)
etcdctl get /registry/namespaces/<name> --print-value-only | \
  auger decode | \
  jq 'del(.metadata.deletionTimestamp, .metadata.deletionGracePeriodSeconds) | .spec.finalizers = []' | \
  auger encode | \
  etcdctl put /registry/namespaces/<name>

# Remove deletionTimestamp from a CRD resource (JSON)
etcdctl get /registry/t-caas.telekom.com/tcaasclusters/<ns>/<name> --print-value-only | \
  python3 -c "import sys,json; d=json.load(sys.stdin); d['metadata'].pop('deletionTimestamp',None); d['metadata'].pop('deletionGracePeriodSeconds',None); json.dump(d,sys.stdout)" | \
  etcdctl put /registry/t-caas.telekom.com/tcaasclusters/<ns>/<name>

# Remove a specific finalizer from a CRD resource
etcdctl get /registry/<group>/<resource>/<ns>/<name> --print-value-only | \
  python3 -c "import sys,json; d=json.load(sys.stdin); d['metadata']['finalizers']=[f for f in d['metadata'].get('finalizers',[]) if f != 'finalizer-to-remove']; json.dump(d,sys.stdout)" | \
  etcdctl put /registry/<group>/<resource>/<ns>/<name>

# List all keys for a resource type
etcdctl get /registry/t-caas.telekom.com/tcaasclusters/ --prefix --keys-only
```

### CRDs vs Core Resources Encoding

- **Core resources** (Namespace, Pod, Secret, ConfigMap): Stored as **protobuf** → use `auger decode` / `auger encode`
- **CRD resources** (TCaasCluster, FunctionInstance, Bundle, etc.): Stored as **JSON** → use `python3 -m json.tool` / `jq`
- To check encoding: `etcdctl get <key> --print-value-only | head -c4` — if starts with `k8s` it's protobuf; if `{` it's JSON

## Flux Prune Cascade Recovery

### The Danger

**CRITICAL:** The `management-cluster-resources-clusters-sync` Kustomization has `prune: true`. If the MCR FunctionInstance re-reconciles with different content, Flux prunes old resources (GitRepository, Kustomization) that no longer match. This triggers a cascade:

```
MCR FI re-reconciled → Flux prunes old GitRepo/Kustomization →
clusters-sync can't reconcile → operator detects unmanaged TCaasClusters →
sets deletionTimestamp → cluster starts deleting → FI finalizers kick in →
FI deletion needs context secrets → secrets already pruned → ALL FI deletions fail
```

**Note:** `t-caas-clusters-sync` has `prune: false` — safe.

### Recovery Steps

1. **Remove deletionTimestamp from TCaasCluster via etcd** (API won't allow it):
   ```bash
   etcdctl get /registry/t-caas.telekom.com/tcaasclusters/<ns>/<name> --print-value-only | \
     python3 -c "..." | etcdctl put ...
   ```

2. **Re-apply SOPS-encrypted secrets** (they're gone with the cascade):
   ```bash
   export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt
   sops -d <encrypted-secret.yaml> | kubectl apply -f -
   ```

3. **Copy critical secrets to `t-caas-controllers` namespace:**
   - `age-flux-management-sync-clusters` — SOPS decryption for clusters-sync
   - `gitlab-mcicd-cluster` — GitRepo auth

4. **Re-apply all management resources from clusters repo:**
   - SharedConfig, TCaasTenants, IDPProviders
   - GitRepositories, Kustomizations

5. **Force-reconcile Flux sources and kustomizations:**
   ```bash
   flux reconcile source git t-caas-clusters-sync -n t-caas-controllers
   flux reconcile kustomization t-caas-clusters-sync -n t-caas-controllers
   ```

### Critical Secrets for Recovery

| Secret | Namespace | Purpose |
|--------|-----------|---------|
| `mcicd-artifactory-cit-read-only` | `t-caas-operator-system` | Registry auth for prerequisites-management |
| `mcicd-artifactory-cit-read-only-image-pull-secret` | `t-caas-operator-system` | Image pull secret |
| `gitlab-mcicd-cluster` | `t-caas-controllers` | GitRepository auth for clusters repo |
| `age-flux-management-sync-clusters` | `t-caas-controllers` | SOPS decryption for clusters-sync |
| `cluster-context-bundle-<cluster>-<hash>` | `<cluster-ns>` | Operator template context for FIs |

## Namespace Stuck Terminating

When a namespace is stuck `Terminating` due to finalizers on child resources:

1. **Identify blocking resources:**
   ```bash
   kubectl api-resources --verbs=list --namespaced -o name | while read r; do
     kubectl get "$r" -n <ns> --no-headers 2>/dev/null
   done
   ```

2. **Strip finalizers from blocking resources:**
   ```bash
   kubectl patch <kind> <name> -n <ns> --type=merge -p '{"metadata":{"finalizers":[]}}'
   ```

3. **If API rejects (namespace in Terminating):** Use etcd directly to remove deletionTimestamp from the namespace, clean up resources, then re-delete.

4. **Common finalizer types that block namespace deletion:**
   - `fluxcd.io/finalizer` — Flux Kustomization (needs workload cluster access to prune)
   - `rolebinding.authorization.t-caas.telekom.com/finalizer` — auth-operator RoleBindings
   - `t-caas.telekom.com/*` — T-CO managed resources (FIs, etc.)
   - `kubernetes` — default namespace finalizer
