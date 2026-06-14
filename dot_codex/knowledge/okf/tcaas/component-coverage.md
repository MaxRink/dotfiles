---
type: Reference
title: Component Coverage
description: Component families that must be covered when answering T-CaaS Core SoC rows.
tags: [tcaas, components, coverage, soc]
timestamp: 2026-06-14T00:00:00Z
---

# Current Coverage Summary

The current Core audit covers `991` captured rows with zero local-path hygiene issues and zero durable-reference issues. Coverage means the component is represented in answer rows and evidence references; it does not mean every component is fully compliant.

# Required Component Families

| Family | Notes |
|---|---|
| Core/private-cloud baseline | Treat private cloud rows as applicable unless explicitly out of scope. |
| Kubernetes and lifecycle | Kubernetes, Cluster API, T-CaaS Operator, Flux, GitOps, and operator-based reconciliation. |
| Bare-metal and infrastructure | BM4X, CAPRF/Redfish, vSphere/CAPV, OpenStack, GCP development environment. |
| Networking | Calico, Multus, SR-IOV, NetworkBinding, DNS/Infoblox, kube-vip, MetalLB, ingress, 6WIND vSR/HBR, FRR reference fabric, network operators, IPAM/VLAN/BGP. |
| Storage and data | NetApp/Trident, Ceph, Cinder, vSphere CSI, ObjectStorageProfile/S3/StorageGRID, Velero, etcd, PostgreSQL, MongoDB, VictoriaMetrics, Grafana storage. |
| IAM and access | Keycloak/OIDC, ZAM/IDP groups, Auth Operator, Kubernetes RBAC, tenant kubeconfig, breakglass, SSH/debug paths. |
| Security and compliance | Kyverno, Mondoo, policy reporter, SOPS/age, cert-manager, supply-chain and image-sync paths. |
| Observability and logging | Prometheus, platform logging, logging-operator, Fluent Bit, Fluentd, EventTailer, HostTailer, CDI/SOCT/TDI backend forwarding. |
| CI and AI | GitLab CI/CD, AI MR summary/review, release notes, upstream mirrors, package/image provenance. |
| DTT and NatCo | Architecture-difference records only until separate PSA rows exist. |

# Persistent Blockers

Keep conservative statements where evidence is not durable:

* Router/switch packet-plane, device-local AAA, SNMP, firmware, and physical fabric controls.
* Storage backend appliance controls, root mapping, retention, replication, MFA, and overload controls.
* Backup/restore schedules, restore tests, and tenant-data coverage.
* Web/application-specific cookie, CSRF, XSS, upload, redirect, and reauthentication behavior.
* Formal access-review cadence, release approval workflow, DPA/privacy process evidence, and AI governance specifics.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
[2] [T-CaaS Knowledge Base](https://wiki.telekom.de/spaces/TCAAS/pages/2544994733/Knowledge+Base)
