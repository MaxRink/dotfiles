---
type: Reference
title: Runtime Verification
description: How marcel-1 and Mondoo evidence should be used for PSA SoC answers.
tags: [tcaas, marcel-1, mondoo, runtime, verification]
timestamp: 2026-06-14T00:00:00Z
---

# marcel-1

marcel-1 runtime checks are required for questions about actual server, Kubernetes, host, container, network, IAM, hardening, and runtime configuration. The collector writes compact, redacted summaries by default and should avoid raw dumps unless needed for temporary local debugging.

# Mondoo

Use Mondoo policy results as verification and provenance. Do not treat policy presence alone as fulfillment proof. If the policy result has open findings or degraded configuration, keep the related answer partial or negative.

# Durable Evidence Rule

Runtime observations can guide investigation, but final PSA references still need durable GitLab, GitHub, or Confluence URLs. If a runtime observation must be cited directly, first publish a sanitized, approved export in a durable location.

# Known Runtime Findings

The latest marcel-1 audit confirmed deployed logging-operator based platform logging, Trident/NetApp storage patterns, Calico policy patterns, and many platform components. It did not prove storage-array local controls, physical router/switch controls, full web-application controls, or Mondoo fulfillment where Mondoo credentials were degraded.

# Citations

[1] [T-CaaS Fact Sheet](https://wiki.telekom.de/spaces/TCAAS/pages/3079290239/Fact+sheet)
