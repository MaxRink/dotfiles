---
name: schiff-platform-clusters-tcaas-function-image-mirroring
description: 'Fix image pull failures in T-CaaS FunctionDefinitions caused by CI image mirroring mismatches. USE WHEN: ImagePullBackOff on workload pods, image not found errors, definition.yaml newName mismatch, preserve-path strategy issues, CI tcaas-func-publish-definition job, image registry path debugging, SharedConfig 0.2.x mirror compatibility, mirrors.dockerIo removed, mirrors.ghcrIo removed, mirrors.registryK8sIo removed, ghcr.io no route to host, registry.k8s.io no route to host. Keywords: ImagePullBackOff, preserve-path, image mirror, newName, definition.yaml, CI pipeline, OCI, artifactory, cit-t-caas-oci, functions, registry.mirrors.functions.path, SharedConfig 0.2, dockerIo, ghcrIo, registryK8sIo, quayIo, no route to host.'
---

<!-- Imported from schiff/platform/clusters/.github/skills/tcaas-function-image-mirroring by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS Function Image Mirroring

## Overview

T-CaaS functions use CI to mirror container images from upstream registries into a per-function image namespace in Artifactory. The `definition.yaml` in each function repo maps original image names to mirrored paths using Go templates. Mismatches between what CI mirrors and what `definition.yaml` expects cause `ImagePullBackOff` on workload clusters.

## Image Mirroring Architecture

```
Source Image (upstream)
  → CI mirrors to → Artifactory per-function path
  → definition.yaml maps → original name → mirrored newName
  → T-CO renders templates → HelmRelease/Kustomization uses correct image
```

### CI Image Mirroring Job

The `tcaas-func-publish-definition` CI job in each function repo:
1. Reads images from `definition.yaml` (or related manifests)
2. Mirrors them to the function's image repository in Artifactory
3. Publishes the FunctionDefinition as an OCI artifact

**Key CI variable:**
```yaml
TCAAS_IMAGE_DESTINATION_REPOSITORY_STRATEGY: "preserve-path"
```

### Image Destination Strategies

| Strategy | Behavior | Destination Path |
|----------|----------|------------------|
| `preserve-path` | Keeps the full source path after registry hostname | `<imageRepo>/<full-source-path-after-hostname>` |
| `flatten` (default) | Uses only the image name | `<imageRepo>/<image-name>` |

### preserve-path Example

**Source image:** `artifactory.devops.telekom.de/cit-t-caas-oci/images/t-caas/minimal:0.1.5`

**Function imageRepository:** `artifactory.devops.telekom.de/cit-t-caas-oci/functions/cluster-secret-generation/images`

**Mirrored to (preserve-path):**
```
artifactory.devops.telekom.de/cit-t-caas-oci/functions/cluster-secret-generation/images/cit-t-caas-oci/images/t-caas/minimal:0.1.5
```

The path after the imageRepository base is the FULL source path starting from after the registry hostname:
- Registry: `artifactory.devops.telekom.de`
- Source path after hostname: `cit-t-caas-oci/images/t-caas/minimal`
- Result: `<imageRepo>/<source-path-after-hostname>`

## Common Mistake: Missing Path Prefix in newName

### Wrong (missing registry path prefix):
```yaml
images:
  - name: artifactory.devops.telekom.de/cit-t-caas-oci/images/t-caas/minimal
    newName: |-
      {{ $.config.sources.registry.endpoint.url }}/{{ $.config.sources.registry.mirrors.functions.path }}/cluster-secret-generation/images/t-caas/minimal
```

### Correct (includes full path after hostname):
```yaml
images:
  - name: artifactory.devops.telekom.de/cit-t-caas-oci/images/t-caas/minimal
    newName: |-
      {{ $.config.sources.registry.endpoint.url }}/{{ $.config.sources.registry.mirrors.functions.path }}/cluster-secret-generation/images/cit-t-caas-oci/images/t-caas/minimal
```

The key difference: with `preserve-path`, you must include the full path after the source registry hostname (`cit-t-caas-oci/images/t-caas/minimal`), not just the "logical" path (`t-caas/minimal`).

## CI Image Discovery Mechanism (tcaas-cli)

The `tcaas-func-publish-definition` CI job uses the `tcaas-cli` (`/tcaas build`) to render charts/kustomizations and discover images. The code lives in `software/cli/tcaas-cli/pkg/releases/artifacts/images.go`.

### How Images Are Discovered

For each rendered YAML document, the CLI applies a two-phase extraction:

1. **Structured PodSpec parsing** — if the document is a known K8s workload (Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job, CronJob), it extracts `container.image` from the PodSpec.
2. **Regex fallback** — for documents that are NOT known K8s workload types (e.g., CRDs), it scans lines matching:
   ```
   (?:image|IMAGE):\s*['"]?<image-ref>['"]?$
   ```

### Known Limitation: CRD-Specific Image Fields

The regex only matches exactly `image:` (lowercase) or `IMAGE:` (uppercase). **Mixed-case CRD fields are NOT discovered:**

| Field | Matched? | Example |
|-------|----------|---------|
| `image:` | ✅ Yes | Standard container image field |
| `IMAGE:` | ✅ Yes | Uppercase variant |
| `tridentImage:` | ❌ No | NetApp TridentOrchestrator CRD |
| `autosupportImage:` | ❌ No | NetApp TridentOrchestrator CRD |
| `acpImage:` | ❌ No | NetApp TridentOrchestrator CRD |
| `imageRegistry:` | ❌ No* | Matched by regex but value is a registry, not an image ref |

**Impact:** Charts that only deploy CRDs (like trident-operator which creates a TridentOrchestrator) will have their operator-managed images missed. The operator constructs image paths at runtime from CRD fields, and CI never mirrors them.

**Workaround:** Use `additionalImages` in the release build config to explicitly list these images:
```yaml
releases:
  - name: trident
    helm:
      build:
        repository: "oci://registry.example.com/charts"
        version: "26.02.0"
        additionalImages:
          - "netapp/trident:26.02.0"
          - "netapp/trident-autosupport:26.02"
```
Each entry is a standard image reference (`[registry/]repository:tag` or `[registry/]repository@digest`). Entries containing Go template expressions are skipped.

### Additional Discovery Features

- **Helm `imageExtractionValuesFile`** — merges extra values during rendering to satisfy `required` checks. Set in `spec.releases[].helm.build.imageExtractionValuesFile`.
- **Kustomize image field specs** — custom image paths declared via kustomize `configurations:` files. Only works for kustomize releases, not Helm.
- **Unreferenced kustomize components** — automatically enabled during extraction to discover additional images.
- **`syncImages: false`** — set in `spec.releases[].helm.build.syncImages` to skip image mirroring for a release.
- **Definition kustomize image overrides** — `tcaas` automatically extracts source images from `spec.releases[].kustomize.images[]` overrides. When an override redirects an upstream image to an internal registry with a different tag (e.g. `newTag: v4.1.4-PATCH.2`), the upstream source is discovered for mirroring. Entries containing Go template expressions (`{{ }}`) are skipped.
- **`additionalImages`** — explicit upstream image references in `spec.releases[].helm.build.additionalImages` (or kustomize equivalent). Use this for CRD-specific image fields (e.g. `tridentImage`, `autosupportImage`) that are not auto-discovered. Entries containing Go templates are skipped.
- **`excludeImages`** — glob patterns in `spec.releases[].helm.build.excludeImages` to skip mirroring of specific images. Supports `*` (single segment) and `**` (cross-segment). Example: `"docker.io/debug-*:*"` or `"**:latest"`.
- **`signatureRepository`** — set in `spec.releases[].helm.build.signatureRepository` when upstream projects store cosign signatures in a separate OCI repo (e.g. kyverno stores signatures in `ghcr.io/kyverno/signatures`). Equivalent to the `COSIGN_REPOSITORY` env var.

### Checking CI Publish Job Logs

```bash
cd functions/<component>/

# List recent pipelines
glab ci list --per-page=5

# Find the publish job ID for a specific pipeline
glab api projects/<url-encoded-project>/pipelines/<pipeline-id>/jobs \
  | python3 -c "import sys,json; jobs=json.load(sys.stdin); [print(f'{j[\"id\"]} {j[\"name\"]} {j[\"status\"]}') for j in jobs]"

# View the publish job logs
glab ci trace <job-id>
```

**Key log lines to look for:**
```
Image mirror destination strategy: preserve-path
Configured image mirror destination base: artifactory.devops.telekom.de/cit-t-caas-oci/functions/<name>/images
► Extracting images from Helm release <release-name>
    Found N image(s) in release <release-name>
    <source-registry>/<path>:<tag>
► Mirroring N image(s) from <release> to <destination>
  Mirroring <source> -> <destination>
✔   Mirrored <destination-path>
```

### preserve-path with Artifactory Source Images

**Critical edge case:** When the source image is ALREADY in Artifactory (e.g., `artifactory.devops.telekom.de/cit-t-caas-oci/images/t-caas/my-image:v1.0`), the `preserve-path` strategy preserves the FULL path after the registry hostname:

```
Source: artifactory.devops.telekom.de/cit-t-caas-oci/images/t-caas/my-image:v1.0
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      This entire path is preserved

Destination: .../functions/<func>/images/cit-t-caas-oci/images/t-caas/my-image:v1.0
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Common mistake:** The FD `newName` omits the `cit-t-caas-oci/images/` prefix:
```yaml
# WRONG — path doesn't match what CI mirrored:
newName: .../functions/capi/images/t-caas/cluster-api-provider-redfish

# CORRECT — includes full preserve-path prefix:
newName: .../functions/capi/images/cit-t-caas-oci/images/t-caas/cluster-api-provider-redfish
```

### Image Source Rewrite Map

CI rewrites public registries to trusted Artifactory mirrors before mirroring:

| Public Registry | Trusted Mirror |
|----------------|----------------|
| `docker.io` | `trusted.artifactory.devops.telekom.de/hub.docker.com` |
| `ghcr.io` | `trusted.artifactory.devops.telekom.de/ghcr.io.docker` |
| `registry.k8s.io` | `trusted.artifactory.devops.telekom.de/k8s.gcr.io` |
| `quay.io` | `trusted.artifactory.devops.telekom.de/quay.io` |
| `gcr.io` | `trusted.artifactory.devops.telekom.de/gcr.io` |
| `public.ecr.aws` | `trusted.artifactory.devops.telekom.de/public.ecr.aws-remote` |
| `mcr.microsoft.com` | `trusted.artifactory.devops.telekom.de/mcr.microsoft.com` |

After rewriting, the image is mirrored from the trusted cache to the function's image repository.

## Debugging Image Pull Failures

### 1. Identify the Failing Pod

```bash
export KUBECONFIG=~/marcel.k  # or appropriate workload kubeconfig
kubectl get pods -A | grep -i "pull\|err\|crash"
kubectl describe pod <pod> -n <ns> | grep -A5 "Events:"
```

### 2. Find the Expected Image Path

```bash
# From the pod spec:
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].image}'

# From the FunctionDefinition on mgmt cluster:
unset KUBECONFIG
kubectl -n t-caas-operator-system get fd <fd-name> -o yaml | grep -A5 "images:"
```

### 3. Check CI Pipeline Logs

```bash
cd functions/<component>/
glab ci list --per-page=3
glab ci trace <pipeline-id>  # Or view in browser
```

Look for lines like:
```
Image destination repository strategy: preserve-path
Mirroring <source> -> <destination>
```

### 4. Verify the Image Exists in Artifactory

```bash
# Check if image is actually present at the expected path
# Use skopeo or crane to inspect:
skopeo inspect docker://<full-image-path>:<tag>
crane manifest <full-image-path>:<tag>
```

### 5. Fix the definition.yaml

Edit `definition.yaml` in the function repo to correct the `newName`:
```bash
cd functions/<component>/
git checkout -b fix/image-mirror-path
# Fix the newName to match what CI actually mirrors
git add definition.yaml
git commit -m "fix: correct image mirror path for preserve-path strategy"
git push -u origin fix/image-mirror-path
git tag <next-rc-version>
git push origin <next-rc-version>
```

### Step 6: Make FD Available and Deploy

After CI publishes the new FD to `releases.git`, Flux `releases-sync` picks it up automatically — no ignore list changes needed.
```bash
# Force Flux reconcile:
flux reconcile source git releases-sync -n t-caas-operator-system

# In bundles repo: update Bundle CR to reference new FD name
# In clusters repo: update TCaasCluster bundle ref if needed
```

**NEVER copy FD yamls into `bundles/functiondefinitions/`** — `releases-sync` handles delivery automatically.

## definition.yaml Image Section Reference

### Kustomize images (used by Flux Kustomization):
```yaml
releases:
  - name: my-release
    kustomize:
      images:
        - name: <original-image-without-tag>
          newName: |-
            {{ $.config.sources.registry.endpoint.url }}/{{ $.config.sources.registry.mirrors.functions.path }}/<function-name>/images/<preserved-path>
          newTag: "1.2.3"
```

### Helm values (used by Flux HelmRelease):
```yaml
releases:
  - name: my-release
    helm:
      values: |-
        image:
          repository: "{{ .config.sources.registry.endpoint.url }}/{{ .config.sources.registry.mirrors.functions.path }}/<function-name>/images/<preserved-path>"
          tag: "1.2.3"
```

## Template Variables for Image Paths

| Variable | Typical Value |
|----------|---------------|
| `{{ .config.sources.registry.endpoint.url }}` | `artifactory.devops.telekom.de` |
| `{{ .config.sources.registry.mirrors.functions.path }}` | `cit-t-caas-oci/functions` |
| `{{ .config.sources.registry.imagePullSecretName }}` | `mcicd-artifactory-cit-read-only-image-pull-secret` |

Full mirrored image path pattern:
```
<endpoint.url>/<mirrors.functions.path>/<function-name>/images/<full-source-path-after-hostname>:<tag>
```

## postRenderers and Go Templates

**CRITICAL:** T-CO does NOT render Go templates inside `spec.releases[].helm.provider.flux.postRenderers`. Templates in postRenderers are passed through literally to Flux, which doesn't understand them.

### Wrong (Go templates in postRenderers — will fail):
```yaml
provider:
  flux:
    postRenderers:
      - kustomize:
          patches:
            - patch: |
                {{- if .config.sources.registry.imagePullSecretName }}
                - op: replace
                  path: /spec/imagePullSecrets
                  value: "{{ .config.sources.registry.imagePullSecretName }}"
                {{- end }}
              target:
                kind: TridentOrchestrator
                name: trident
```

### Correct (use Helm values instead):
```yaml
values: |-
  {{- if .config.sources.registry.imagePullSecretName }}
  imagePullSecrets:
    - name: "{{ .config.sources.registry.imagePullSecretName }}"
  {{- end }}
```

**Where T-CO renders templates:**
- ✅ `spec.releases[].helm.values`
- ✅ `spec.releases[].kustomize.images[].newName`
- ✅ `spec.releases[].kustomize.patches[].patch`
- ✅ `spec.releases[].kustomize.components`
- ❌ `spec.releases[].helm.provider.flux.postRenderers` (passed literally to Flux)

## imagePullSecrets

Functions that deploy pods need `imagePullSecrets` to pull from Artifactory.

### For Helm releases (in values):
```yaml
values: |-
  {{- if .config.sources.registry.imagePullSecretName }}
  imagePullSecrets:
    - name: "{{ .config.sources.registry.imagePullSecretName }}"
  {{- end }}
```

### For Kustomize releases (via patch):
```yaml
kustomize:
  patches:
    - target:
        kind: Deployment
      patch: |-
        - op: add
          path: /spec/template/spec/imagePullSecrets
          value:
            - name: {{ .config.sources.registry.imagePullSecretName }}
```

### Namespace Secret Availability

The imagePullSecret must exist in the namespace where pods run. The T-CO operator copies it from `t-caas-operator-system` to cluster namespaces. If pods can't pull:
```bash
# Check if secret exists in the cluster namespace
kubectl -n <cluster-ns> get secret mcicd-artifactory-cit-read-only-image-pull-secret

# If missing, copy it (emergency fix — Flux should handle this):
kubectl -n t-caas-operator-system get secret mcicd-artifactory-cit-read-only-image-pull-secret \
  -o json | jq '.metadata.namespace = "<target-ns>" | del(.metadata.uid,.metadata.resourceVersion,.metadata.creationTimestamp)' \
  | kubectl apply -f -
```

## SharedConfig 0.2.x Compatibility — Registry Mirror Changes

### What Changed in SharedConfig 0.2.x

SharedConfig 0.2.x **removed** all per-registry mirror keys that existed in 0.1.x. FunctionDefinitions that reference these keys will render as empty strings, causing pods to try pulling from the public internet (and failing with "no route to host").

| Mirror Key | 0.1.x | 0.2.x | Behaviour in 0.2.x |
|------------|-------|-------|---------------------|
| `.config.sources.registry.mirrors.functions` | ✅ | ✅ | Works — all images should use this |
| `.config.sources.registry.mirrors.dockerIo` | ✅ | ❌ removed | Renders as `<nil>` → image pulled from docker.io directly |
| `.config.sources.registry.mirrors.ghcrIo` | ✅ | ❌ removed | Renders as `<nil>` → image pulled from ghcr.io directly |
| `.config.sources.registry.mirrors.registryK8sIo` | ✅ | ❌ removed | Renders as `<nil>` → image pulled from registry.k8s.io directly |
| `.config.sources.registry.mirrors.quayIo` | ✅ | ❌ removed | Renders as `<nil>` → image pulled from quay.io directly |
| `.config.sources.registry.mirrors.gcrIo` | ✅ | ❌ removed | Renders as `<nil>` → image pulled from gcr.io directly |

**Symptom:** Pods show `ImagePullBackOff` with errors like:
```
failed to do request: Head "https://ghcr.io/...": dial tcp ...: connect: no route to host
```
or the image is fetched from docker.io/ghcr.io/registry.k8s.io but the workload cluster has no internet access.

### Audit Functions for 0.2.x Incompatibility

```bash
# Find all definition.yaml files using old mirror keys
grep -rl "mirrors\.dockerIo\|mirrors\.ghcrIo\|mirrors\.registryK8sIo\|mirrors\.quayIo\|mirrors\.gcrIo" \
  /path/to/functions/ --include="definition.yaml"

# Also find hardcoded registry hostnames with no mirror template at all
grep -rl '"ghcr\.io\|"registry\.k8s\.io\|"docker\.io\|"quay\.io' \
  /path/to/functions/ --include="definition.yaml"
```

### Fix Pattern for 0.2.x Compatibility

All images from any upstream registry must now go through the `mirrors.functions` path. CI mirrors them there via `preserve-path` strategy.

**Old pattern (0.1.x only — broken on 0.2.x):**
```yaml
image:
  registry: "{{ $.config.sources.registry.mirrors.ghcrIo.path }}"
  # OR
newName: |
  {{ $.config.sources.registry.endpoint.url }}/{{ $.config.sources.registry.mirrors.dockerIo.path }}/library/alpine
```

**New pattern (works on both 0.1.x and 0.2.x via `mirrors.functions`):**
```yaml
newName: |-
  {{ $.config.sources.registry.endpoint.url }}/{{ $.config.sources.registry.mirrors.functions.path }}/<function-name>/images/<full-source-path-after-hostname>
```

For **Helm `values`** where the old pattern set `registry: "{{ .mirrors.ghcrIo.path }}"`:
```yaml
values: |-
  image:
    registry: "{{ $.config.sources.registry.endpoint.url }}"
    repository: "{{ $.config.sources.registry.mirrors.functions.path }}/<func>/images/ghcr.io/<org>/<image>"
    tag: "v1.2.3"
```

**Key rule:** `registry.k8s.io/kube-proxy:v1.35.5` → CI mirrors to
`artifactory.../cit-t-caas-oci/functions/kube-proxy/images/kube-proxy:v1.35.5`
(registry hostname stripped, path preserved — so `registry.k8s.io/kube-proxy` becomes just `kube-proxy`).

### Functions Fixed for 0.2.x (reference)

These were audited and fixed with tags `*.dev.0` / `*.dev.4`:
- `kube-proxy` — was using hardcoded version mismatch; VERSION file updated to `1.35.5`
- `cert-manager` — mirror path corrected
- `coredns` — mirror path corrected
- `flux` — 7× image entries: `images/ghcr.io.docker/fluxcd/{component}` → `images/fluxcd/{component}`
- `metallb-controller` — mirror path corrected
- `metrics-server` — mirror path corrected
- `meta-cni-config` — was using `mirrors.dockerIo` for alpine; changed to `mirrors.functions`
- `flux-management` — was using `mirrors.ghcrIo`; changed to `mirrors.functions`
- `flux-workload` — was using `mirrors.ghcrIo`; changed to `mirrors.functions`
- `ingress-nginx-controller` (and metallb/kube-vip/openstack variants) — completely hardcoded `registry.k8s.io` with no mirror template; added `mirrors.functions` conditional template

### Still Needs Audit

Functions that likely have the same issue (pull from ghcr.io/registry.k8s.io directly):
- `whereabouts` — confirmed `ImagePullBackOff` on `ghcr.io/k8snetworkplumbingwg/whereabouts:v0.8.1`
- `kyverno` — confirmed `ImagePullBackOff` on `ghcr.io/kyverno/kyverno:v1.15.3`

Audit with:
```bash
# Find all functions pulling directly from public registries on workload cluster
KUBECONFIG=/tmp/workload-kubeconfig.yaml kubectl get pods -A -o yaml \
  | grep "image:" \
  | grep -v "artifactory.devops.telekom.de" \
  | grep -v "#" | sort -u
```
