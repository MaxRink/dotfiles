# cert-manager & Certificate Issuers in CT-CaaS

## Overview

CT-CaaS deploys **cert-manager** as a standard function (e.g., `cert-manager` v0.2.5 → cert-manager v1.18.2).

A `cert-manager-issuers` function definition exists in the bundles repo (`functiondefinitions/cert-manager-issuers/`) but is **not yet referenced by any current bundle** (neither `netbox-workload` nor `openstack-management` as of 35.0.4 / 33.6.18). The ClusterIssuers are prepared but not deployed out of the box.

The `certs` function (v0.1.1) deploys Calico-specific certificates only (calico-ca, calico-node, calico-typha, calico-goldmane, calico-whisker) using a self-signed Issuer scoped to Calico mTLS — not a general-purpose ClusterIssuer.

## ClusterIssuers (prepared, not yet deployed)

Defined in `cert-manager-issuers` FD (`cit/t-caas/software/kustomizations/cert-manager-issuers`):

| ClusterIssuer | Purpose |
|---|---|
| `t-caas-selfsigned` | Self-signed fallback, always deployed |
| `t-caas-issuer` | Primary issuer used by services (e.g., k8s-breakglass). Configurable provider |
| `t-caas-issuer-http01` | Optional HTTP-01 issuer for environments without DNS-01 |

## Issuer Strategy

The `t-caas-issuer` provider depends on the deployment configuration:

| Mode | Provider | When |
|------|----------|------|
| Self-signed (default) | `selfSigned: {}` | No `acme.server` configured |
| ACME + DNS-01 | **TelesecCA** via Infoblox WAPI webhook | `acme.server` + `infoblox.enabled=true` |
| ACME + HTTP-01 | ACME with ingress-based solver | `acme.server` set, no Infoblox |

### Production Example (TelesecCA + Infoblox DNS-01)

```yaml
issuerName: t-caas-issuer
acme:
  server: https://ca.2.telesec.de/acme/v2/directory
  email: platform-team@example.com
infoblox:
  enabled: true
  host: infoblox-bln.dcpf.telekom.de
  dnsView: default.TDCN
```

## Key FD Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `issuerName` | string | `t-caas-issuer` | Primary ClusterIssuer name |
| `acme.server` | string | — | ACME directory URL (enables ACME mode) |
| `acme.email` | string | — | ACME account email |
| `acme.privateKeySecretName` | string | `t-caas-acme-account-key` | ACME account key secret |
| `infoblox.enabled` | boolean | `false` | Deploy Infoblox WAPI webhook |
| `infoblox.host` | string | — | Infoblox WAPI hostname |
| `infoblox.dnsView` | string | `default.TDCN` | DNS view for records |
| `infoblox.credentialsSecretName` | string | `infoblox-credentials` | Secret with username/password |
| `httpSolver.enabled` | boolean | `false` | Enable HTTP-01 ClusterIssuer |

## Related Components

- **certbot** (`cit/t-caas/software/helm-charts/certbot`) — CronJob-based ACME client, separate from cert-manager issuers. Uses `certbotAcmeServer` config, deployed under the `prometheus` function.
- **cluster-certificates** (`cit/t-caas/software/kustomizations/cluster-certificates`) — Calico-specific CA/certs (calico-ca, calico-node, calico-typha), not related to the primary issuer.

## Comparison with Standard CaaS

| Feature | Standard CaaS | CT-CaaS |
|---------|--------------|---------|
| cert-manager deployed | ✅ | ✅ |
| ClusterIssuer deployed | ❌ | ❌ (FD exists but not in any bundle yet) |
| Calico mTLS certs | N/A | ✅ (`certs` function, self-signed Issuer) |
| ACME support | Not built-in | Prepared in `cert-manager-issuers` FD (TelesecCA + Infoblox DNS-01) |
| Workloads need own Issuer | Yes | Yes (until `cert-manager-issuers` is added to bundles) |
