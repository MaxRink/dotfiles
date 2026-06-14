# External Helm Repos Investigation

## Problem Summary

The `caas-image-versions.sh` script reports incorrect image tags for **prometheus** and **grafana** components:

| Component | Script Reports | Actually Running | Issue |
|-----------|---------------|------------------|-------|
| Grafana | `v1.1.1` (hardcoded) | `grafana:11.3.1` | Wrong tag picked up |
| Prometheus | `v1.1.1` (hardcoded) | `prometheus:v3.1.0` | Wrong tag picked up |

## Root Cause (RESOLVED)

### Initial Hypothesis (Incorrect)

The initial assumption was that prometheus and grafana used external repositories:
- `prometheus-community-helm-virtual`
- `grafana-helm-virtual`

### Actual Root Cause (Correct)

After checking `mom-factory-adopted/settings.tpl.yaml`, we discovered that **ALL helm repos point to the same repository**:

```yaml
# From mom-factory-adopted/settings.tpl.yaml
registry_helm_repoURL: https://artifactory.devops.telekom.de/artifactory/tdi-caas-helm-virtual
registry_helm_repoURL_grafana: https://artifactory.devops.telekom.de/artifactory/tdi-caas-helm-virtual
registry_helm_repoURL_prometheus_community: https://artifactory.devops.telekom.de/artifactory/tdi-caas-helm-virtual
# ... all other repos also point to the same URL
```

The charts ARE in the main index. The actual issues were:

### Issue 1: Version Pattern Matching (Primary)

The `lookup_appversion()` function used **exact version matching**:

```awk
# Old code - exact match only
if ($0 == ver) {
    found_version=1
}
```

But function files use version patterns with `.x` suffix:
- Function: `version: 27.3.x`
- Index: `version: 27.3.0`, `27.3.1`, etc.
- Comparison: `"27.3.x" == "27.3.0"` → **FALSE** (lookup fails)

### Issue 2: Fallback Hardcoded Tag Extraction (Secondary)

When index lookup failed, `extract_hardcoded_tags()` picked up `tag: v1.1.1` from `sriov-network-metrics-exporter` and incorrectly applied it to ALL charts in the function.

## Solution Implemented

Modified `lookup_appversion()` to support version patterns with `.x` suffix:

```bash
# Check if version has .x pattern suffix (e.g., "27.3.x")
local use_prefix_match="0"
local version_prefix=""
if [[ "$chart_version" == *".x" ]]; then
    use_prefix_match="1"
    version_prefix="${chart_version%.x}."  # "27.3.x" -> "27.3."
fi

# In AWK: use prefix match when pattern detected
if (prefix_match == "1") {
    if (index($0, ver_prefix) == 1) {
        found_version=1
    }
}
```

This allows `27.3.x` to match any version starting with `27.3.` (e.g., `27.3.0`, `27.3.1`, etc.).

## Files Modified

- `scripts/caas-image-versions.sh` - Added version pattern matching support

## Testing

After fix, verify with:
```bash
# Should show actual appVersion from index (not v1.1.1)
ARTIFACTORY_TOKEN="..." ./scripts/caas-image-versions.sh baremetal-cluster-34.6.10 | grep -E "(prometheus|grafana)"

# Expected: prometheus:v3.x.x, grafana:11.x.x (or similar based on chart appVersion)
```

## Reference: Actual Versions Running (from cluster hrzagt5-skynet-dev)

```
grafana/grafana:11.3.1
prometheus/prometheus:v3.1.0
prometheus-operator/prometheus-config-reloader:v0.79.2
prometheus/node-exporter:v1.8.2
kube-state-metrics/kube-state-metrics:v2.14.0
```

## Lessons Learned

1. Always verify template variable resolutions in settings files before assuming repos are external
2. Version patterns with wildcards (`.x`) need special handling in lookup logic
3. The `mom-factory-adopted` project contains the canonical registry configuration
