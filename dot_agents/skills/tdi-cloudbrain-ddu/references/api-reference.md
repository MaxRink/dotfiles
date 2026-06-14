# DDU API Reference

## Overview

The DDU API provides endpoints for checking Kubernetes cluster status, retrieving cluster information, and accessing cluster secrets.

## Base URL

```
https://ddu.caas.in.pan-net.eu
```

## Authentication

All API requests require an API token passed via the `X-API-TOKEN` header:

```bash
-H "X-API-TOKEN: ${DDU_API_TOKEN}"
```

## VPN Requirement

API access only works when connected to Telekom VPN.

## Endpoints

### Check Cluster Status

Check the health status of a specific Kubernetes cluster.

```
GET /api/v1/cluster/check?name={cluster-name}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Name of the cluster to check |

**Example:**
```bash
curl -s -X GET "https://ddu.caas.in.pan-net.eu/api/v1/cluster/check?name=hrzagt5-skynet-dev" \
    -H "X-API-TOKEN: ${DDU_API_TOKEN}" \
    -H "Accept: application/json"
```

### Get Cluster Secrets

Retrieve passwords and secrets for a specific Kubernetes cluster.

```
GET /api/v1/cluster/secrets?name={cluster-name}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Name of the cluster |

**Response Fields:**

| Field | Description |
|-------|-------------|
| `GRAFANA_ADMIN_PASSWORD` | Admin password for Grafana dashboard |
| `PROMETHEUS_PASSWORD` | Password for Prometheus access |
| `AUTOMATION_KUBECONFIG` | Kubeconfig YAML for automation/CI pipelines |
| `CUSTOMER_KUBECONFIG` | Kubeconfig YAML for customer access |
| `OIDC_KUBECONFIG` | Kubeconfig YAML with OIDC authentication |
| `OPENRC` | OpenStack RC file contents (only populated for clusters running on OpenStack VMs, empty for baremetal clusters) |
| `CLUSTER_NAME` | Name of the cluster |
| `PARENT` | Parent management cluster name |

**Example:**
```bash
curl -s -X GET "https://ddu.caas.in.pan-net.eu/api/v1/cluster/secrets?name=hrzagt5-skynet-dev" \
    -H "X-API-TOKEN: ${DDU_API_TOKEN}" \
    -H "Accept: application/json"
```

**Security Note:** This endpoint returns sensitive credentials. Handle the response with care and never log or expose secrets.

### Get Cluster Report

Get a detailed report for a specific Kubernetes cluster.

```
GET /api/v1/cluster/report?name={cluster-name}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Name of the cluster |

**Example:**
```bash
curl -s -X GET "https://ddu.caas.in.pan-net.eu/api/v1/cluster/report?name=hrzagt5-skynet-dev" \
    -H "X-API-TOKEN: ${DDU_API_TOKEN}" \
    -H "Accept: application/json"
```

### Get All Clusters Report

Get a report for all Kubernetes clusters.

```
GET /api/v1/cluster/report
```

**Parameters:** None

**Example:**
```bash
curl -s -X GET "https://ddu.caas.in.pan-net.eu/api/v1/cluster/report" \
    -H "X-API-TOKEN: ${DDU_API_TOKEN}" \
    -H "Accept: application/json"
```

## Error Responses

### 401 Unauthorized

Missing or invalid API token.

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API token"
}
```

### 404 Not Found

Cluster not found.

```json
{
  "error": "Not Found",
  "message": "Cluster 'cluster-name' not found"
}
```

### 500 Internal Server Error

Server-side error.

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 404 | Not Found - Cluster not found |
| 500 | Internal Server Error |

## Rate Limiting

The API may apply rate limiting. If you receive HTTP 429, implement exponential backoff.

## Troubleshooting

### Connection Refused / Timeout

- Ensure you are connected to Telekom VPN
- Verify the API URL is correct
- Check if the service is available

### 401 Unauthorized

- Verify `DDU_API_TOKEN` is set correctly
- Ensure the token has not expired
- Request a new token if needed

### 404 Not Found

- Verify the cluster name is correct
- Check available clusters using the all-clusters report endpoint
