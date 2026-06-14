# Domain Knowledge

## NTP Configuration

NTP servers are configured via Chrony in the componentConfig post-provisioning scripts. In `baremetal-cluster` products, the default NTP servers are `10.235.9.253` and `10.235.9.254`.

These defaults are defined using a Go template in the componentConfig:
```
{{- range (dig "ntp_servers" (list "10.235.9.253" "10.235.9.254") .ClusterSpec.ExtraParams) }}
echo 'pool {{ . }} iburst' >> /etc/chrony/chrony.conf
{{- end }}
```

Per-cluster override is possible by setting `ntp_servers` in `ClusterSpec.ExtraParams`.

To check NTP config for a product:
```bash
source .env && .venv/bin/python ${SKILL_DIR}/scripts/caas-componentconfig.py <product-name> --raw | grep -i ntp -A 5 -B 5
```

## cert-manager & Certificate Issuers

CaaS deploys **cert-manager** as a standard function (e.g., `cert-manager` v0.2.23 → cert-manager v1.12.12).

**No ClusterIssuer is deployed.** The cert-manager Helm chart (`tdi-caas/helm-charts/cert-manager`) only contains:
- `templates/CRDs.yaml` — cert-manager CRD definitions
- `templates/config-map.yaml` — ConfigMap (`cert-manager-ca`) with Pan-Net root CA certificates, mounted into the cert-manager controller pod at `/etc/ssl/certs/cert-manager-ca.crt`

A separate function **`pannet-ca`** (e.g., v0.0.6) deploys a ConfigMap (`pan-net-ca`) with Pan-Net / DNSaaS / TMPL CA certificate bundles. This is **not** a ClusterIssuer — it's just CA trust anchors.

**Workloads must bring their own Issuer or ClusterIssuer** (e.g., self-signed, ACME/Let's Encrypt, or a CA issuer).

This is different from **CT-CaaS (converged)**, which has a `cert-manager-issuers` function definition prepared (with TelesecCA/ACME support) but not yet wired into any bundle. CT-CaaS does deploy Calico-specific certs via the `certs` function using a scoped self-signed Issuer.
