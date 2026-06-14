---
type: Reference
title: T-CaaS Platform Knowledge Sources
description: Curated source categories used to analyze the T-CaaS platform for PSA SoC answers.
tags: [tcaas, evidence, architecture, soc]
timestamp: 2026-06-14T00:00:00Z
---

# Primary Sources

| Source | Use |
|---|---|
| `cit/t-caas` GitLab repositories | Platform functions, operators, software bundles, CI, GCP dev environment, runtime workload, and upstream mirrors. |
| `schiff/platform/clusters` GitLab repositories | Implementation cluster configuration, management clusters, marcel-1, Mondoo analysis exports, and runtime manifests. |
| T-CaaS Confluence Fact Sheet | Project purpose, roles, private-cloud framing, high-level architecture, operational boundaries, and platform facts. |
| T-CaaS Confluence Knowledge Base | Operational docs, platform architecture, limitations, release notes, tenant docs, and cluster creation guidance. |
| marcel-1 live collection | Runtime verification for server, Kubernetes, host, network, IAM, container, and hardening questions. |
| Mondoo console and exports | Policy and finding cross-reference for hardening, CIS-style checks, host posture, and Kubernetes controls. |
| Public GitHub upstreams | Upstream provenance where a row specifically needs component origin or project behavior. Prefer internal mirrors for portal evidence when available. |

# Component Coverage

Treat these as explicit platform component classes during SoC analysis:

* Kubernetes management and workload clusters.
* BM4X, Redfish, machine plans, vSphere, OpenStack, GCP dev environment, and private cloud infrastructure.
* NetworkBinding, DNS/Infoblox, SR-IOV, Multus, Coil, FRR, 6WIND vSR/HBR, Calico, NetworkPolicy, MetalLB, kube-vip, and ingress controllers.
* ObjectStorageProfile/S3, Ceph, NetApp, Cinder, CSI drivers, Velero, etcd, PostgreSQL, MongoDB, VictoriaMetrics, Grafana storage, and related backup/lifecycle paths.
* Auth operator, Keycloak/IDP, tenant kubeconfig, breakglass, RBAC, GitLab CI, GitOps/Flux, image sync, and secret generation paths.
* Harmonized platform logging based on logging-operator, Fluent Bit, Fluentd, EventTailer, HostTailer, platform/tenant Logging resources, and backend routing.
* AI use in development and CI review/grading workflows.

# Rules

1. Every applicable row needs a component-aware answer, not only a generic platform answer.
2. `NA` is acceptable only with a concrete scope reason.
3. For real server and cluster configuration, verify marcel-1 or the implementation repo before marking a row ready.
4. For Mondoo-backed statements, distinguish policy presence from actual pass/fail evidence.
5. For DTT and NatCo, use architecture evidence now; generate row-level answers only after PSA exposes SoCs.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
[2] [T-CaaS Knowledge Base](https://wiki.telekom.de/spaces/TCAAS/pages/2544994733/Knowledge+Base)
[3] [Telekom GitHub organization](https://github.com/telekom/)
