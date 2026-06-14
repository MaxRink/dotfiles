# CaaS Baremetal Platform Capabilities Reference

Quick reference of T-CaaS baremetal platform capabilities for compliance mapping.
Always verify against the actual product version using `caas-componentconfig.py`.

## Operating System & Runtime

| Capability | Details |
|-----------|---------|
| OS | Ubuntu 22.04 LTS |
| Kernel | 5.15+ (ships with Ubuntu 22.04) |
| Container Runtime | containerd (OCI 1.0.0 compliant) |
| cgroups | v2 by default (v1 available via ExtraParam) |
| Systemd | cgroup driver = systemd |

## Kernel Configuration

### Modules loaded by default (`/etc/modules-load.d/9-caas.conf`)

br_netfilter, rbd, xt_u32, fou, ip6table_mangle, xt_bpf, ip_gre, nf_defrag_ipv4, xt_conntrack

Most iptables/netfilter modules (ip_tables, iptable_filter, iptable_mangle, ipt_REJECT, etc.) are auto-loaded by the kernel on demand.

Additional modules can be loaded via `extraModulesLoadOverride` ExtraParam.

### Sysctl parameters set by default

- `fs.inotify.max_user_instances=8192`
- `net.bridge.bridge-nf-call-iptables=1`
- `net.bridge.bridge-nf-call-ip6tables=1`

Additional sysctls can be set via `extraSysctlOverride` ExtraParam.

### File limits

- `nofile`: 65535
- `core`: unlimited

## Kubernetes

| Capability | Details |
|-----------|---------|
| kube-proxy mode | iptables (NOT IPVS) |
| Admission plugins | Default set (NO AlwaysPullImages) |
| Audit logging | Enabled |
| Profiling | Disabled (profiling=false) |
| RBAC | Enabled |
| API server encryption | Configurable (EncryptionConfiguration) |

### Kubelet

- cgroup-driver: systemd
- Container runtime: containerd
- PidsLimit: default unlimited, configurable via `kubeletDropIn`
- Additional kubelet config via `kubeletDropIn` ExtraParam

## Networking

| Component | Details |
|-----------|---------|
| CNI | Calico |
| Additional CNIs | Multus, SR-IOV, OVS-CNI, Whereabouts |
| Load Balancer | MetalLB (BGP mode) |
| Network Policies | Calico NetworkPolicy + GlobalNetworkPolicy |
| MTU | 9000 (jumbo frames, configurable) |
| IPv6 | Available via `ipv6_enabled` ExtraParam |
| Dual-stack | Supported |
| ECMP | Depends on DC gateway configuration |

## Storage

| Component | Details |
|-----------|---------|
| Block storage | Ceph RBD (via ceph-csi) |
| Filesystem storage | CephFS (via ceph-csi) |
| Storage classes | caas-block (RBD), caas-filesystem (CephFS) |
| Volume expansion | Supported |
| Snapshots | Supported (VolumeSnapshot) |
| Encryption at rest | Ceph-level (verify per deployment) |
| IOPS | Depends on Ceph cluster sizing |

## Security

| Capability | Details |
|-----------|---------|
| Admission control | OPA (NOT Pod Security Admission) |
| OPA policies | CPBRN2-15 (capabilities, host namespaces, etc.) |
| Key policy: CPBRN10 | Restricts Linux capabilities - vendors may need exceptions |
| CIS benchmarks | OpenSCAP hardening applied |
| Secret encryption | Configurable EncryptionConfiguration for etcd |
| Network policies | Supported via Calico |

## Monitoring & Logging

| Component | Details |
|-----------|---------|
| Metrics | Prometheus + custom ServiceMonitors |
| Dashboards | Grafana |
| Log collection | fluentbit (forwarded to central logging) |
| Alerting | Prometheus Alertmanager |
| Health checks | Goldpinger (node-to-node connectivity) |

## Platform Services

| Component | Details |
|-----------|---------|
| DNS | CoreDNS |
| Certificate management | cert-manager |
| Metrics API | metrics-server |
| Backup | Velero (S3-compatible backend) |
| Ingress | Customer-provisioned (not platform default) |

## High Availability & Topology

| Capability | Details |
|-----------|---------|
| Availability Zones | 3 AZs (topology.kubernetes.io/zone labels) |
| Control plane HA | 3 master nodes across AZs |
| etcd | 3-node cluster, co-located with masters |
| Pod anti-affinity | Supported via topology labels |
| Node affinity | Supported via standard Kubernetes labels |

## ExtraParams Override Mechanisms

These allow per-cluster customization without changing the product:

| ExtraParam | Purpose |
|-----------|---------|
| `extraSysctlOverride` | Add kernel sysctl parameters |
| `extraModulesLoadOverride` | Load additional kernel modules |
| `kubeletDropIn` | Override kubelet configuration (PidsLimit, etc.) |
| `hugepages` | Enable HugePages support |
| `crash_dumps.enabled` | Enable kernel crash dump collection |
| `ntp_servers` | Configure NTP/chrony servers |
| `ipv6_enabled` | Enable IPv6 support |
| `cgroups_v1` | Switch to cgroups v1 (if needed) |

## Common Vendor Requirement Gaps

These are areas where vendor requirements commonly don't align with defaults:

1. **vm.max_map_count**: Not set by default (needed for OpenSearch/Elasticsearch) → use `extraSysctlOverride`
2. **Descheduler**: Not deployed by default → evaluate if needed
3. **AlwaysPullImages**: Not enabled (by design for air-gapped environments)
4. **IPVS mode**: Not used (CaaS uses iptables mode)
5. **Linux capabilities**: OPA CPBRN10 restricts most capabilities → vendor may need exceptions
6. **Helm version**: Customer-side tool, not part of platform
7. **Ingress controller**: Customer-provisioned, not platform default
