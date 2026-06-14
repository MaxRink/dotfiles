# Prometheus Alert Rules — File Catalog

All files live in `tdi-caas/helm-charts/prometheus-rules/templates/`.

## Upstream kube-prometheus-stack rules (`kube-prometheus-stack-*.yaml`)

| File | Content |
|------|---------|
| `kube-prometheus-stack-alertmanager-rules.yaml` | AlertManager self-monitoring |
| `kube-prometheus-stack-config-reloaders.yaml` | Config reloader alerts |
| `kube-prometheus-stack-etcd.yaml` | etcd upstream alerts |
| `kube-prometheus-stack-general-rules.yaml` | General Prometheus rules |
| `kube-prometheus-stack-kube-apiserver-slos.yaml` | API server SLO alerts |
| `kube-prometheus-stack-kube-state-metrics.yaml` | kube-state-metrics upstream alerts |
| `kube-prometheus-stack-kubernetes-apps.yaml` | Pod/deployment/daemonset alerts (e.g. `NodeBondingDegraded`, `KubePodCrashLooping`) |
| `kube-prometheus-stack-kubernetes-resources.yaml` | CPU/memory resource alerts |
| `kube-prometheus-stack-kubernetes-storage.yaml` | PVC/storage alerts |
| `kube-prometheus-stack-kubernetes-system.yaml` | kubelet/kube-proxy alerts |
| `kube-prometheus-stack-node-exporter.yaml` | Node exporter upstream alerts |

## Custom CaaS rules (`caas-*.yaml` and `rules-*.yaml`)

| File | Content |
|------|---------|
| `caas-chronyc-sync-status.yaml` | NTP/chrony sync alerts (`NodeCustomChronySync`) |
| `caas-interfaces.rules.yaml` | `CaasCustomNodeExporterInterfacesDown` and related |
| `caas-kube-state-metrics.rules.yaml` | Custom kube-state-metrics rules |
| `caas-lldpctl-check-status.yaml` | LLDP neighbor check alerts |
| `caas-process-networkd.count.yaml` | systemd-networkd process alerts |
| `rules-argocd.yaml` | ArgoCD alerts |
| `rules-backup.yaml` | Backup alerts |
| `rules-black-exporter.yaml` | Blackbox exporter alerts |
| `rules-cpu-iowait.yaml` | CPU I/O wait alerts |
| `rules-cpu-steal.yaml` | CPU steal alerts |
| `rules-cpu-utilization.yaml` | CPU utilization alerts |
| `rules-etcd.yaml` | Custom etcd alerts |
| `rules-goldpinger.yaml` | Goldpinger connectivity alerts |
| `rules-kubeapi-cert.yaml` | Kube API certificate expiry alerts |
| `rules-loadbalancer-octavia.yaml` | Octavia load balancer alerts |
| `rules-metallb.yaml` | MetalLB alerts |
| `rules-monitoring-apps.yaml` | Monitoring stack self-alerts |
| `rules-network.yml` | `HostNetworkBondDegraded` and network bond alerts |
| `rules-openstack-collector.yaml` | OpenStack collector alerts |
| `rules-prometheus-slo.yaml` | Prometheus SLO alerts |
| `rules-systemd.yml` | systemd service alerts |
| `rules-watchdog-soc.yaml` | Watchdog/SOC alerts |
