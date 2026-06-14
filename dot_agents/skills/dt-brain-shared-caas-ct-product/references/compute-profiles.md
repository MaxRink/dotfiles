# Compute Profiles

Compute profiles (`computeprofiles/` folder in the bundles repo) define node-level provisioning configuration via `NetboxComputeProfile` CRD. They are separate from function definitions and bundles.

Browse: https://gitlab.devops.telekom.de/cit/t-caas/software/bundles/-/tree/main/computeprofiles

## Available Profile Types

| File pattern | Used for |
|---|---|
| `netbox-*.yaml` | Standard netbox workload clusters |
| `bm4x-*.yaml` | BM4X clusters |
| `openstack-juice-*.yaml` | OpenStack clusters with Juice |
| `openstack-juiceless-*.yaml` | OpenStack clusters without Juice |
| `vsphere-mgmt-*.yaml` | vSphere management clusters |

To list current versions, fetch the repo tree via GitLab API:
```python
client.project.repository_tree(path='computeprofiles', ref='main', get_all=True)
```

## NTP Configuration (netbox profile)

NTP is configured via Chrony in post-provisioning commands. The `netbox` compute profile has an optional `ExtraNTPServers` input (type: string, required: false). If not set, falls back to TDI defaults:

```
pool 10.235.9.253 iburst
pool 10.235.9.254 iburst
```

Template logic in the profile:
```
{{- with .inputs.ExtraNTPServers }}
{{ . }}
{{- else }}
pool 10.235.9.253 iburst
pool 10.235.9.254 iburst
{{- end }}
```

To verify the current defaults, read the latest netbox profile directly:
```python
content = client._get_file_content('computeprofiles/netbox-<version>.yaml')
```
