# OPA Security Policies Reference

CaaS clusters enforce security policies via OPA (Open Policy Agent) admission controller.

## Source Location

- **Source template**: `tdi-caas/caas-bundles-source` → `functions/opa/opa-configuration-0.1.x.yaml`
- **Released versions**: `tdi-caas/caas-bundles` → `functions/opa/opa-configuration-<version>.yaml`
- **Deployed as**: ConfigMap `opa-caas-restrictions` in `kube-system` namespace

The policy is deployed by the CaaS operator to every cluster. There is **no per-cluster exception mechanism** — the same policy applies everywhere.

## Policy Rules

| Rule | Description |
|------|-------------|
| No privileged containers | `securityContext.privileged = true` denied |
| No hostPath volumes | Only `/var/log` and `/var/lib/containerd/io.containerd.grpc.v1.cri/containers` allowed (readOnly only) |
| No hostPID / hostIPC / hostNetwork | CIS Benchmark compliance |
| No allowPrivilegeEscalation | CIS Benchmark compliance |
| No dangerous capabilities | `NET_RAW`, `NET_ADMIN`, `IPC_LOCK` denied |
| No CaaS object modification | Objects with label `caasprotected=true` in `kube-system` are protected |
| No node deletion | Customers cannot delete nodes |
| No CaaS ServiceMonitor scraping | Label `monitoring=caas` denied |
| PriorityClass limit | Value must be ≤ 999999999 |

## Bypass / Exemption Mechanisms

The `is_not_whitelisted()` function controls who is exempt:

1. **Whitelisted service accounts** — hardcoded set of `kube-system` SAs (controllers, CaaS components like prometheus, calico, cert-manager, etc.)
2. **OIDC group** — members of `oidc:s_nfvi_caas` (CaaS team) bypass all rules
3. **Node users** — `system:node:*` pattern bypassed
4. **Customer SA pattern** — `system:serviceaccount:kube-system:caas-.*-customer` exempt from hostPath rules only
5. **Whitelisted namespaces** — currently empty (`{}`) — could be used for per-namespace exemptions but isn't used today

## hostPath Volume Rules (Detail)

The hostPath rules use **exact string matching**, not prefix matching:

- `/var/log` → allowed if mounted **readOnly**
- `/var/lib/containerd/io.containerd.grpc.v1.cri/containers` → allowed if mounted **readOnly**
- Any other path (e.g. `/var/log/pods`, `/etc`, `/tmp`) → **denied**

**Important**: Subpaths like `/var/log/pods` are NOT covered by the `/var/log` exception. The workaround is to mount `/var/log` (readOnly) and access subpaths from within the container.

The rules check both `spec.volumes` and `spec.template.spec.volumes` (covering both Pods and Deployments/DaemonSets).

## Common Customer Policy Violations

| Error Message | Cause | Workaround |
|---------------|-------|------------|
| "Path '/var/log/pods' not allowed as hostPath volume" | Only exact `/var/log` is allowed, not subpaths | Mount `/var/log` (readOnly) instead |
| "Do not admit privileged containers" | `securityContext.privileged: true` | Remove privileged flag, use specific capabilities |
| "Do not admit containers with allowPrivilegeEscalation" | `allowPrivilegeEscalation: true` | Set to `false` |
| "Do not admit containers with dangerous capabilities" | Adding `NET_RAW`, `NET_ADMIN`, or `IPC_LOCK` | Remove the capability or request CaaS team exception |
| "Do not admit containers wishing to share the host network namespace" | `hostNetwork: true` | Request CaaS team exception |

## How to Add Exceptions

1. **Temporary (PoC/testing)**: Edit the `opa-caas-restrictions` ConfigMap directly on the cluster. ⚠️ Will be overwritten on next CaaS operator reconciliation.
2. **Permanent**: Create a new version of `opa-configuration` in `tdi-caas/caas-bundles-source` via merge request.
3. **Jira**: Use project **CAASPROD** for OPA rule change requests.
