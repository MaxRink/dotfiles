---
name: schiff-k8s-agent-find-mgnt-cluster
description: Find the management (CAPI) cluster that owns a given tenant cluster by reading the SchiffCluster YAML from the cluster-components GitLab repo and extracting `spec.internal.managementCluster`.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/find-mgnt-cluster by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Find management cluster for a tenant cluster

Use this skill whenever you need to determine which CAPI management cluster is responsible for a tenant cluster — e.g. before running `kubectl` against CAPI CRDs (`Cluster`, `MachineDeployment`, `KubeadmControlPlane`) or `clusterctl describe`.

## Inputs

You need the tenant cluster's short name in the form:

```text
<cluster>.<environment>.<location>
```

Examples:

- `bulk-1.tstsa1.bn`
- `cas-1.tst.bmbg10`
- `schiff-canary-1.tmdc.b`
- `a4-4.reftmdc.n`

### Resolving from an alert label

Alertmanager/Prometheus use the full FQDN in the `cluster` label:

```text
cluster="a4-4.reftmdc.n.schiff.telekom.de"
```

Strip the `.schiff.telekom.de` suffix to get the short name:

```text
a4-4.reftmdc.n.schiff.telekom.de  →  a4-4.reftmdc.n
```

The short name maps directly to the GitLab file path and the kubeconfig context name.

If the user gives only a cluster base name (`a4-4`), ask for environment + location, or list candidates with `gitlab_get_repository_tree`.

## Source of truth

Repository: `schiff/platform/infrastructure/cluster-components` (project id `15328`).

File path pattern:

```text
locations/<location>/<environment>/<cluster>/SchiffCluster_<cluster>.<environment>.<location>.yaml
```

Relevant field:

```yaml
spec:
  internal:
    managementCluster: <mgmt-cluster-name>   # e.g. schiff-controlplane-reftmdc.reftmdc.bn
```

The value is itself a fully-qualified cluster name (`<cluster>.<environment>.<location>`) that matches a kubeconfig context.

## Procedure

1. Compose the file path from the tenant name:

   For tenant `bulk-1.tstsa1.bn` → path `locations/bn/tstsa1/bulk-1/SchiffCluster_bulk-1.tstsa1.bn.yaml`.

2. Fetch the file via the GitLab MCP tool:

   ```text
   gitlab_get_file_contents(
     project_id="schiff%2Fplatform%2Finfrastructure%2Fcluster-components",
     file_path="locations/<loc>/<env>/<cluster>/SchiffCluster_<cluster>.<env>.<loc>.yaml"
   )
   ```

3. Parse the YAML and read `spec.internal.managementCluster`. Report it to the user.

4. Note the CAPI namespace for the tenant on the management cluster. It follows the pattern:

   ```text
   <provider>-<environment><location>
   ```

   Examples:
   - `a4-4.reftmdc.n` with provider `vsphere` → namespace `vsphere-reftmdc-n`
   - `bulk-1.tstsa1.bn` with provider `metal3` → namespace `metal3-tstsa1-bn`

   The provider is available in `spec.provider.name` of the SchiffCluster YAML.
   Use this namespace when querying CAPI resources: `kubectl get cluster <cluster-short-name> -n <namespace>`.

5. (Optional) Switch kubectl context to the management cluster:

   ```bash
   kubectl config use-context <managementCluster>
   # if the context is missing:
   schiff login <managementCluster>
   ```

## Fallbacks

- **Direct path fetch fails (404)**: the directory layout may have changed or the input is malformed.
  - List the location directory: `gitlab_get_repository_tree(path="locations/<location>/<environment>")` and confirm the cluster folder name.
  - If location/environment are unknown, search the full tree: `gitlab_get_repository_tree(path="locations", recursive=true)` and grep for the cluster name.

- **Tenant fqdn unknown, only a tenant name is known**: use `gitlab_get_repository_tree` with `recursive=true` on `locations/` and filter client-side for `SchiffCluster_<cluster>.*.yaml`.

- **Need management cluster for many tenants at once**: prefer fetching and grepping `clusters.yaml` at the repo root — it aggregates tenant→mgmt mappings and avoids per-file lookups. Note: `clusters.yaml` can be large (>700 KB); use the explore agent with Grep to extract `managementCluster:` lines if needed.

## Example

User asks: "Which management cluster owns `cas-1.tst.bmbg10`?"

1. Path: `locations/bmbg10/tst/cas-1/SchiffCluster_cas-1.tst.bmbg10.yaml`
2. Fetch via `gitlab_get_file_contents`.
3. Read `spec.internal.managementCluster` → `schiff-mgmt-1.tmdc.b`.
4. Read `spec.provider.name` → `vsphere` → namespace on mgmt cluster: `vsphere-tstbmbg10`.
5. Answer: "`cas-1.tst.bmbg10` is managed by `schiff-mgmt-1.tmdc.b` in namespace `vsphere-tstbmbg10`. To switch context: `kubectl config use-context schiff-mgmt-1.tmdc.b`."

User reports alert with `cluster="a4-4.reftmdc.n.schiff.telekom.de"`:

1. Strip suffix → short name: `a4-4.reftmdc.n`
2. Path: `locations/n/reftmdc/a4-4/SchiffCluster_a4-4.reftmdc.n.yaml`
3. Read `spec.internal.managementCluster` → `schiff-cp-1.reftmdc.n`.
4. Read `spec.provider.name` → `vsphere` → namespace: `vsphere-reftmdc-n`.
5. Switch context: `kubectl config use-context schiff-cp-1.reftmdc.n`
6. Query: `kubectl get cluster a4-4 -n vsphere-reftmdc-n`

## Safety

- This skill is read-only — only fetches files from GitLab, does not mutate anything.
- Always verify the context switch with `kubectl config current-context` before issuing further `kubectl` commands against the management cluster.
