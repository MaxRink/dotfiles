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

## Additional Resources

- Official NetBox Documentation: https://docs.netbox.dev/
- pynetbox Documentation: https://pynetbox.readthedocs.io/
