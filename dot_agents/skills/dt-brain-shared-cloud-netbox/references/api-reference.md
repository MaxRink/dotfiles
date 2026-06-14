# NetBox API Reference

## Instance Information

- **Base URL**: `https://dcim.tools.in.pan-net.eu/`
- **API Root**: `https://dcim.tools.in.pan-net.eu/api/`
- **API Version**: 3.x
- **Documentation**: `https://dcim.tools.in.pan-net.eu/api/docs/`
- **Authentication**: Token-based via `Authorization: Token <token>` header

## Key API Endpoints

### Virtualization

| Endpoint | Description |
|----------|-------------|
| `/api/virtualization/clusters/` | List all clusters |
| `/api/virtualization/clusters/{id}/` | Get specific cluster |
| `/api/virtualization/cluster-groups/` | List cluster groups |
| `/api/virtualization/virtual-machines/` | List virtual machines |

### DCIM (Data Center Infrastructure Management)

| Endpoint | Description |
|----------|-------------|
| `/api/dcim/sites/` | List all sites/datacenters |
| `/api/dcim/devices/` | List all devices |
| `/api/dcim/interfaces/` | List interfaces |

## Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query | `?q=kubernetes` |
| `limit` | Limit results | `?limit=50` |
| `offset` | Pagination offset | `?offset=100` |
| `name` | Filter by exact name | `?name=my-cluster` |
| `group_id` | Filter by cluster group | `?group_id=5` |
| `site_id` | Filter by site | `?site_id=10` |
| `status` | Filter by status | `?status=active` |

## Status Values

### Cluster Status
- `active` - Cluster is operational
- `planned` - Cluster is being planned
- `staged` - Cluster is staged for deployment
- `decommissioning` - Cluster is being decommissioned
- `offline` - Cluster is offline

### VM Status
- `active` - VM is running
- `offline` - VM is powered off
- `staged` - VM is staged
- `failed` - VM has failed

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 401 | Unauthorized | Verify API token is correct |
| 403 | Forbidden | Check token permissions |
| 404 | Not Found | Verify object ID/name exists |
| 503 | Service Unavailable | Check VPN connection |

## Python Client (pynetbox)

The skill scripts use the `pynetbox` library. Key usage:

```python
import pynetbox

nb = pynetbox.api('https://dcim.tools.in.pan-net.eu/', token='your-token')

# List clusters
clusters = nb.virtualization.clusters.filter(group='caas')

# Get specific cluster
cluster = nb.virtualization.clusters.get(123)
```

## CaaS Baremetal (BM4X) Reference

### Terminology

- **"Profile"** or **"BM4X profile"** = the `hw_versions` custom field on a device in DCIM (e.g., `Profile6.6a`, `Profile26.6ai`). This is the primary identifier for hardware configurations.
- **"HW Model"** = the `device_type` field (e.g., `ThinkSystem SR650 v2`, `ProLiant DL380 Gen11`). Each BM4X profile maps to a specific HW model.
- Profiles ending in `_HP` (e.g., `Profile6.6a_HP`) are HP equivalents of the Lenovo profile with the same specs.

### Querying BM4X Devices

- CaaS baremetal clusters: filter by `group_id` (CaaS) and `type_id` (baremetal)
- Devices per cluster: `nb.dcim.devices.filter(cluster_id=<id>)`
- Filter by profile: `nb.dcim.devices.filter(cf_hw_versions='Profile6.6a')`
- Server devices are identified by `device_role` containing "Server", "Compute", or "Management" (use `d.device_role`, NOT `d.role`)

### Device Object Key Fields

| Field | Access | Description |
|-------|--------|-------------|
| `device_type` | `d.device_type` (dict with `model`, `manufacturer`) | Hardware model |
| `device_role` | `d.device_role` (dict with `name`) | Role (e.g., "BE Compute Server") |
| `site` | `d.site` (dict with `name`) | Site code (e.g., `HRZAGD001`) |
| `cluster` | `d.cluster` (dict with `name`) | Assigned cluster |
| `custom_fields.hw_versions` | `d.custom_fields['hw_versions']` | BM4X profile name |
| `custom_fields.server_usage` | `d.custom_fields['server_usage']` | Usage type (e.g., `CaaS-BM`) |
| `custom_fields.warranty_expires_at` | `d.custom_fields['warranty_expires_at']` | Warranty expiry |
| `serial` | `d.serial` | Serial number |
| `primary_ip` | `d.primary_ip` | Primary IP address |

### Profile Types

| Type | Profiles | Description |
|------|----------|-------------|
| **Control Plane** | Profile7.1, Profile7.1_HP, Profile27.1.1, Profile27.2i, Profile27.2i_HP | Master/control plane nodes (1 socket, low RAM) |
| **Worker** | Profile6.x, Profile26.x, Profile1.3, Profile21.x, Profile22.x, Profile28.x | Compute worker nodes (1-2 sockets, high RAM) |
| **EOL** | Be1.5, Li | Legacy profiles, no longer deployed |

### Wiki References for Profile Specs

- **Older profiles** (1.x–7.x): Wiki page ID `1442357349` ("HW profile details" in CITTEST space)
- **2024+ profiles** (21.x, 22.x, 26.x, 27.x): Wiki page ID `1435539872` ("CIT HW Catalog" in CITTEST space), table under "CaaS 2024" section at end of page
- **BOM/part numbers**: Wiki page ID `2042864768` ("BMAX Profiles" in ckbsh space)
- **NIC slot positions**: Wiki page ID `2747916741` ("HW profile / NIC positions" in ckbsh space)

## Additional Resources

- Official NetBox Documentation: https://docs.netbox.dev/
- pynetbox Documentation: https://pynetbox.readthedocs.io/
