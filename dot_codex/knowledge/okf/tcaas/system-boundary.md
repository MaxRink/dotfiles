---
type: Reference
title: System Boundary
description: T-CaaS scope boundaries used when deciding SoC applicability.
tags: [tcaas, scope, private-cloud, dtt, natco]
timestamp: 2026-06-14T00:00:00Z
---

# Boundary

| Scope | Treatment |
|---|---|
| T-CaaS Core | Current captured and answerable PSA corpus. Covers the converged, NatCo-independent managed Kubernetes/private-cloud baseline. |
| DTT | No separate SoC rows currently exposed. Keep architectural differences and answer later when PSA exposes rows. |
| NatCo | No separate SoC manifest currently available. Keep tenant/CNF/runtime architecture differences and answer later when PSA exposes rows. |
| Private cloud | Applicable. T-CaaS is a private cloud / telco cloud managed Kubernetes platform. |
| GCP | Not the production runtime baseline, but truthfully answer where development, CI, runner, WIF, private GKE, or landing-zone controls apply. |
| AI/ML | Applicable to development and CI review tooling. Runtime tenant AI/ML model operation is usually out of T-CaaS Core scope. |
| Tenant applications | Usually outside Core except where T-CaaS provides shared platform controls. |
| Underlying infrastructure | Split responsibility with BM4X, TDI data centers, GCP landing zone, storage, network, or tenant owners must be stated explicitly. |

# Answering Rule

Classify every requirement before choosing `SOC`, `SOPC`, `SONC`, or `NA`. `NA` is valid only with a concrete boundary reason. Split responsibility generally maps to `SOPC` unless complete delegated fulfillment is documented.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
