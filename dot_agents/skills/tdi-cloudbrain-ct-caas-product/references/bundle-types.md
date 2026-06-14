# CT-CaaS Bundle Types Reference

## Bundle Types

| Type | Directory | Description |
|------|-----------|-------------|
| **netbox** | `bundles/netbox/` | Baremetal Kubernetes clusters (T-CaaS Netbox) |
| **openstack** | `bundles/openstack/` | OpenStack-based clusters (management and workload) |
| bm4x | `bundles/bm4x/` | BM4X baremetal clusters |
| docker | `bundles/docker/` | Docker-based clusters |
| vsphere | `bundles/vsphere/` | VMware vSphere clusters |
| adopted | `bundles/adopted/` | Adopted/imported clusters |

## Repository Structure

```
tcaas/bundles/
├── bundles/                          # Bundle manifest definitions
│   ├── netbox/
│   │   └── netbox-workload-34.0.19.yaml
│   └── openstack/
│       ├── openstack-management-33.6.6.yaml
│       └── openstack-workload-33.4.21.yaml
├── functiondefinitions/              # Component function definitions
│   ├── calico/
│   │   └── calico-0.4.8.yaml
│   ├── coredns/
│   │   └── coredns-0.3.1.yaml
│   └── ... (63+ function categories)
├── computeprofiles/                  # Compute profile configurations
├── networkprofiles/                  # Network profile configurations
├── storageprofiles/                  # Storage profile configurations
├── bootstrapconfigs/                 # Bootstrap configurations
├── images/                           # Kubernetes image versions by version
└── image-registries/                 # Image registry configurations
```

## Bundle File Structure

```yaml
apiVersion: t-caas.telekom.com/v1alpha1
kind: Bundle
metadata:
  name: netbox-workload-34.0.19
  namespace: t-caas-operator-system
spec:
  k8sVersion: v1.34.1
  functions:
    - ref:
        name: coredns-0.3.1      # Combined name-version format
    - ref:
        name: calico-0.4.8
    - ref:
        name: cert-manager-0.2.5
```

**Key Characteristics:**
- API Version: `t-caas.telekom.com/v1alpha1`
- Kind: `Bundle`
- Functions use combined `name-version` format (e.g., `coredns-0.3.1`)
- Uses `k8sVersion` field (not `kubernetesVersion`)
- No `actions` section (unlike TDI-CaaS)

## FunctionDefinition File Structure

### Helm-based Release

```yaml
apiVersion: t-caas.telekom.com/v1alpha1
kind: FunctionDefinition
metadata:
  name: coredns-0.3.1
  namespace: t-caas-operator-system
spec:
  dependencies:
    provides:
      - dns
    requires:
      - prerequisites
      - cni
  releases:
    - name: coredns
      helm:
        name: coredns
        version: v1.43.1
        namespace: kube-system
        releaseName: coredns
        provider:
          flux:
            repo:
              endpoint:
                url: "oci://..."
        values: |-
          # Helm values (templated)
```

### Kustomize-based Release

```yaml
apiVersion: t-caas.telekom.com/v1alpha1
kind: FunctionDefinition
metadata:
  name: calico-0.4.8
  namespace: t-caas-operator-system
spec:
  dependencies:
    provides:
      - cni
    requires:
      - prerequisites
  releases:
    - name: cni
      kustomize:
        path: ./
        images:
          - name: docker.io/calico/node
            newName: ...
        provider:
          flux:
            repo:
              oci:
                reference: 3.30.3-r.0    # Version here
```

## Key Differences from TDI-CaaS

| Aspect | TDI-CaaS | CT-CaaS |
|--------|----------|---------|
| API Version | `caas.pan-net.eu/v1alpha1` | `t-caas.telekom.com/v1alpha1` |
| Product Kind | `CaasProduct` | `Bundle` |
| Function Kind | `CaasFunction` | `FunctionDefinition` |
| Products Folder | `products/` | `bundles/` |
| Functions Folder | `functions/` | `functiondefinitions/` |
| K8s Version Field | `kubernetesVersion` | `k8sVersion` |
| Functions Format | `name: X` + `version: Y` | `ref.name: X-Y` (combined) |
| Helm Source | `spec.source[]` | `spec.releases[].helm` |
| Kustomize | Not used | `spec.releases[].kustomize` |
| Actions | Yes (`spec.actions`) | No |

## Version Numbering

- **Bundle versions** follow semantic versioning: `MAJOR.MINOR.PATCH` (e.g., 34.0.19)
- **Function versions** are independent (e.g., calico-0.4.8, coredns-0.3.1)
- **Kubernetes version** is specified in `spec.k8sVersion` (e.g., v1.34.1)

## Common Components

### Netbox (Baremetal) Bundle
- calico, whereabouts, multus-cni, sriov-cni, ovs-cni
- metallb-standalone, ceph-csi, cert-manager
- ingress-nginx-controller, prometheus, fluent-bit, goldpinger
- kyverno, metrics-server, coredns, kube-proxy

### OpenStack Bundle
- calico, cert-manager, ingress-nginx-controller
- openstack-cloud-controller-manager, cinder-csi-plugin
- prometheus, fluent-bit, goldpinger
- kyverno, metrics-server, coredns
