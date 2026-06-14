---
type: Reference
title: DTT And NatCo Architecture Differences
description: Current DTT and NatCo differences to keep for future PSA filings while no separate SoC rows exist.
tags: [tcaas, dtt, natco, architecture, deferred-soc]
timestamp: 2026-06-14T00:00:00Z
---

# Scope Decision

DTT and NatCo currently do not have separate PSA SoCs available for row-level capture and answering. Keep architectural differences documented now. When PSA later exposes DTT or NatCo rows, create separate captures, exports, answer sets, evidence reviews, gates, and portal filing runs.

# DTT Differences

| Area | Difference |
|---|---|
| Primary role | DTT-specific development and CI infrastructure, including GCP runner fleets, private GKE/Flux, proxy/egress, and CSA/FAST integration. |
| Evidence source | `cit/t-caas/gcp-dev-env`, especially DTT environment variables, Terraform/OpenTofu, GKE bootstrap, runner configuration, proxy configuration, and certificate/e2e proxy manifests. |
| Scope boundary | DTT evidence is not production runtime proof for every T-CaaS Core control. Use it where the SoC row asks about DTT, GCP, CI, runners, GKE bootstrap, or development infrastructure. |

# NatCo Differences

| Area | Difference |
|---|---|
| Primary role | Tenant, CNF, runtime workload, elevated-components, and deployment-group implementation evidence. |
| Evidence source | `cit/t-caas/runtime/workload`, `cit/t-caas/tdi/elevated-components-tdi`, and CNF template repositories. |
| Scope boundary | NatCo evidence supports tenant and CNF differences, but it is not a separate PSA answer corpus until a NatCo SoC manifest exists. |

# Future Filing Guidance

1. Do not copy T-CaaS Core answers blindly.
2. Reuse Core evidence only when control ownership and component scope are demonstrably shared.
3. Start DTT research from GCP dev-env and CI infrastructure.
4. Start NatCo research from tenant, runtime workload, CNF template, elevated-components, and owner evidence.
5. Keep all final references as GitLab, GitHub, or Confluence URLs.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
[2] [T-CaaS Knowledge Base](https://wiki.telekom.de/spaces/TCAAS/pages/2544994733/Knowledge+Base)
