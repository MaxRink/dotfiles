# CT-CaaS Kyverno Policies Reference

## Architecture

Kyverno in CT-CaaS is deployed via the `kyverno` FunctionDefinition (`functiondefinitions/kyverno/`) in the bundles repo. It consists of three releases:

| Release | Chart | Description |
|---------|-------|-------------|
| `kyverno` | `kyverno/kyverno` | Kyverno policy engine |
| `policy-reporter` | `kyverno/policy-reporter` | Policy Reporter UI and monitoring |
| `platform-policies` | `t-caas/platform-policies` | The actual Kyverno policy rules |

## Repository Locations

| Component | Repository |
|-----------|------------|
| Kyverno FunctionDefinition | `cit/t-caas/software/bundles` → `functiondefinitions/kyverno/` |
| **Platform Policies (Kyverno rules)** | **`https://gitlab.devops.telekom.de/cit/t-caas/software/platform-policies`** |

The `platform-policies` repo contains the Helm chart with the actual `ClusterPolicy` and `Policy` resources that Kyverno enforces.

## Enforcement Levels

The `enforcementLevel` input controls policy behavior:

| Level | Description |
|-------|-------------|
| `full` | Policies are enforced — violations are blocked |
| `reduced` | Reduced enforcement — some policies only audit |
| `audit` | All policies only log violations (no blocking) |

### Default Enforcement Logic

- **BM4X / vSphere** in `prd` or `ref` environments → `full` (hardcoded)
- **BM4X / vSphere** in other environments → user input, defaults to `audit`
- **All other infrastructure types** → user input, defaults to `audit`

## Deployment Details

- **Namespace:** `t-caas-security`
- **Dependencies:** requires `dns`, `service-proxy`, `prerequisites`, `cni`, `multus-cni`
- **Provides:** `policy-engine`
- **Included in:** both Netbox (baremetal) and OpenStack bundles

## Allowed Container Registries

The platform policies enforce an allowlist of container registries:

- `harbor.das-schiff.telekom.de`
- `registry.k8s.io`
- `ghcr.io`, `gcr.io`, `docker.io`, `quay.io`
- `artifactory.devops.telekom.de`, `artifactory.yard.telekom.de`
- `gitlab.devops.telekom.de`, `gitlab.yard.telekom.de`
- Various `yard-ref`, `yard-tst`, `yard-bootstrap-*` registries
- `docker.elastic.co`

## Configuration Options

The FunctionDefinition exposes these inputs via its schema:

| Input | Type | Description |
|-------|------|-------------|
| `enforcementLevel` | string | `full`, `reduced`, or `audit` |
| `additionalAllowedFluxSources` | array of strings | Extra allowed Flux sources for platform-policies |
