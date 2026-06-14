# CaaS Image Builder

How CaaS node images (OS + containerd + runc + kubelet etc.) are built, and how component versions flow from upstream defaults to what runs on nodes.

## Repositories

| Repo | GitLab Project ID | Purpose |
|------|-------------------|---------|
| `tdi-caas/caas-image-builder` | 179067 | TDI CaaS node images (baremetal clusters) |
| `cit/t-caas/image-building/t-caas-image-builder` | 352459 | CT-CaaS (Converged) node images |

Both repos wrap the upstream [kubernetes-sigs/image-builder](https://github.com/kubernetes-sigs/image-builder) and add their own ansible group_vars to override component versions.

## Architecture

```
tdi-caas/caas-image-builder
├── build_image.sh                    # Entry point — maps K8s version → upstream image-builder tag
├── ansible/inventories/production/group_vars/
│   ├── all.yaml                      # Defaults for all K8s versions
│   ├── 1.35.yaml                     # Overrides for K8s 1.35
│   ├── 1.34.yaml                     # Overrides for K8s 1.34
│   └── ...
└── (clones kubernetes-sigs/image-builder at the mapped tag)
```

### Version mapping (build_image.sh)

| K8s Version | Upstream image-builder Tag | Notes |
|-------------|---------------------------|-------|
| ≤ 1.34 | v0.1.41 | Uses `cri-containerd-cni` bundle (includes runc) |
| 1.35 | v0.1.48 | Uses standalone containerd tarball + separate runc download |

## Containerd + runc Packaging

### Before v0.1.48 (K8s ≤ 1.34)

The `cri-containerd-cni` tarball bundles containerd + runc + CNI plugins in a single archive:

```
cri-containerd-cni-{version}-linux-amd64.tar.gz  →  includes runc binary
```

No separate runc version variable is needed — runc comes from the containerd release.

### From v0.1.48 (K8s 1.35+)

The standalone containerd tarball does **NOT** include runc:

```
containerd-{version}-linux-amd64.tar.gz  →  containerd only, no runc
```

runc is downloaded separately by the ansible role `containerd/tasks/main.yml` using:

```yaml
# upstream defaults in images/capi/ansible/roles/containerd/defaults/main.yml
runc_version: "X.Y.Z"
containerd_runc_url: "https://github.com/opencontainers/runc/releases/download/v{{ runc_version }}/runc.{{ arch }}"
```

**This means `runc_version` must be explicitly set in the CaaS group_vars** — otherwise it inherits whatever the upstream image-builder tag hardcodes as a default.

## Variable Override Chain

Ansible variable precedence (lowest → highest):

```
upstream image-builder defaults/main.yml     ← lowest priority
  ↓
caas-image-builder all.yaml                  ← CaaS defaults for all versions
  ↓
caas-image-builder {version}.yaml            ← CaaS per-K8s-version overrides (highest)
```

### Key variables to check/override

| Variable | Where to set | Description |
|----------|-------------|-------------|
| `containerd_version` | `{version}.yaml` | Containerd release version |
| `containerd_url` | `{version}.yaml` | Tarball URL (standalone vs cri-bundle) |
| `runc_version` | `{version}.yaml` or `all.yaml` | runc release version (**critical for standalone tarball**) |
| `runc_sha256` | `{version}.yaml` or `all.yaml` | Checksum for runc binary |
| `kubernetes_semver` | `{version}.yaml` | Kubernetes version to install |

### Upstream defaults gotcha

The upstream `kubernetes-sigs/image-builder` sets `runc_version` in **two places**:

1. `images/capi/packer/config/containerd.json` — used by packer variable injection
2. `images/capi/ansible/roles/containerd/defaults/main.yml` — used as ansible defaults

CaaS bypasses packer and uses ansible group_vars directly, so **only the ansible defaults matter**. If these two files have different runc versions, CaaS gets the ansible default, NOT the packer one.

## CT-CaaS vs TDI-CaaS Comparison

| Setting | TDI-CaaS (`caas-image-builder`) | CT-CaaS (`t-caas-image-builder`) |
|---------|--------------------------------|----------------------------------|
| containerd (K8s 1.35) | 1.7.30 (standalone tarball) | 2.2.1 (standalone tarball) |
| runc_version set? | ❌ Not set (inherits upstream default) | ✅ 1.4.0 in `all.yaml` |
| runc_sha256 set? | ❌ Not set | ✅ Explicitly set |

CT-CaaS is the reference for how to do it right — always explicitly set `runc_version`, `runc_url`, and `runc_sha256`.

## Known Issues

### /dev/net/tun not available in pods (runc 1.2.0–1.2.3)

**Symptoms:** Pods that need `/dev/net/tun` (VPN, tunneling, Mavenir VLB) fail after K8s upgrade.

**Root cause:** runc v1.2.0 ([PR #3468](https://github.com/opencontainers/runc/pull/3468)) removed `/dev/net/tun` from the default container device allow-list. Fixed in runc v1.2.4 ([PR #4555](https://github.com/opencontainers/runc/pull/4555)) and all 1.3.x+.

**Affected versions:** runc 1.2.0, 1.2.1, 1.2.2, 1.2.3

**Fix:** Set `runc_version` to ≥ 1.2.4 (recommended: match what containerd bundles, e.g., 1.3.4 for containerd 1.7.30).

**Interim workaround for deployed clusters:** Replace runc binary on worker nodes:
```bash
curl -Lo /usr/local/sbin/runc https://github.com/opencontainers/runc/releases/download/v1.3.4/runc.amd64
chmod 755 /usr/local/sbin/runc
systemctl restart containerd
```

**References:**
- Jira: VLBFE-3220, VLBFE-2929
- [runc v1.2.4 release notes](https://github.com/opencontainers/runc/releases/tag/v1.2.4)
- [containerd issue #11078](https://github.com/containerd/containerd/issues/11078)

## Troubleshooting Tips

### Check runc version on a node
```bash
runc --version
```

### Check which containerd tarball type was used
```bash
# If runc is at /usr/local/sbin/runc → installed separately (standalone tarball)
# If runc is at /usr/bin/runc → likely from cri-containerd-cni bundle
which runc
```

### Check containerd version
```bash
containerd --version
```

### Verify /dev/net/tun in a pod
```bash
kubectl exec <pod> -- cat /dev/net/tun 2>&1
# Expected output if working: "cat: /dev/net/tun: File descriptor in bad state" (exit 1)
# If missing: "cat: /dev/net/tun: No such file or directory"
```
