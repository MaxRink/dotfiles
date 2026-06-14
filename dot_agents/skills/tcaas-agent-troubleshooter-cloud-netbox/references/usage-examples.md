# Usage Examples & Cross-Skill Integration

## Common Use Cases

### Count Clusters by Group

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --format json | jq '. | group_by(.group) | map({group: .[0].group, count: length})'
```

### See Installed Functions and Versions

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py "my-cluster" --product | grep -A 50 "## Functions"
```

### Complete Cluster Topology Analysis

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-server-connections.py mkskof2-5gc-lab --cluster --format detailed
```

## Cross-Skill Integration

### NetBox + CaaS Product Details

Get cluster with complete product information:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py atgraf1-ndl-prod --product
```

This shows:
- Cluster infrastructure details from NetBox
- Kubernetes version and product type
- Complete list of installed functions with versions
- Lifecycle actions and deployment strategy

### NetBox + PagerDuty Incidents

Check if a cluster has recent incidents:

```bash
# Check incidents for a specific cluster (last 7 days)
.venv/bin/python ../../pagerduty/scripts/pd-incidents.py --since "2026-01-22" --cluster atgraf1-ndl-prod

# Check all incidents at a site
.venv/bin/python ../../pagerduty/scripts/pd-incidents.py --since "2026-01-22" --site atgraf1

# Get summary of incidents by cluster
.venv/bin/python ../../pagerduty/scripts/pd-incidents.py --since "2026-01-22" --format summary
```

### Example Workflow: Cluster Health Check

1. List clusters at a site:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site ATGRAD001
   ```

2. Get cluster details with product info:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/netbox-get-cluster.py atgraf1-ndl-prod --product
   ```

3. Check for recent incidents:
   ```bash
   .venv/bin/python ../../pagerduty/scripts/pd-incidents.py --cluster atgraf1-ndl-prod --since 2026-01-22
   ```

4. Result: Healthy cluster with v1.30.10, no incidents in 7 days ✅
