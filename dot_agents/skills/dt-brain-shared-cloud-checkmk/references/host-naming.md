# Host Naming Convention

Hostnames follow a structured pattern that encodes deployment type, site, and role.

## CaaS Bare-Metal (caas-bm)

```
{type}-{site}-CAAS-BM-{cluster}-{role}-IMM-{serial}
```

- Example: `hc-czprgc1-CAAS-BM-czprgc1-5gc-prod-IMM-J7022553`
- `hc` = Housekeeper Cloud, `ic` = Infrastructure Cloud, `cl` = Central Lab
- `czprgc1` = Czech Republic, Prague, DC1
- `5gc-prod` = 5G Core production cluster
- `IMM-J7022553` = Lenovo IMM (Integrated Management Module) serial

## IaaS/OpenStack (openstack-infra)

```
{type}-{site}-{role}-{number}
```

- Example: `hc-hrspif1-nova-compute-dedicated-43`
- Roles: `infra`, `nova-compute-shared`, `nova-compute-dedicated`, `ceph-osd`

## Site Codes

| Code | Location |
|------|----------|
| `czprgc1` | 🇨🇿 Prague |
| `hrzagt5/6` | 🇭🇷 Zagreb |
| `hrspif1` | 🇭🇷 Split |
| `hrrijf1` | 🇭🇷 Rijeka |
| `mkskof2` | 🇲🇰 Skopje |
| `mkstuf2` | 🇲🇰 Štip |
| `atsalf1` | 🇦🇹 Salzburg |
| `atvief1` | 🇦🇹 Vienna |
| `atgraf1` | 🇦🇹 Graz |
| `defraf2` | 🇩🇪 Frankfurt |
| `debamf3` | 🇩🇪 Bamberg |
| `plwarc2` | 🇵🇱 Warsaw |
| `mebjef1` | 🇲🇪 Bijelo Polje |
| `hubudt1` | 🇭🇺 Budapest |
