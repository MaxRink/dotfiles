# CaaS Product Types Reference

This document describes the different CaaS product types and folder structure in the `caas-bundles` repository.

## Product Types

| Type | Directory | Description |
|------|-----------|-------------|
| **baremetal** | `products/baremetal/` | Baremetal Kubernetes cluster products |
| **caas** | `products/caas/` | Standard CaaS cluster products |
| **mgmt-cluster** | `products/mgmt-cluster/` | Management cluster products |
| **dtit** | `products/dtit/` | DTIT-specific products |
| **mom** | `products/mom/` | MOM (Management Operations Manager) products |
| **support** | `products/support/` | Support and utility products |

## Repository Structure

```
caas-bundles/
├── products/
│   ├── baremetal/
│   │   ├── baremetal-cluster-34.6.10.yaml
│   │   └── ...
│   ├── caas/
│   │   ├── caas-cluster-X.Y.Z.yaml
│   │   └── ...
│   ├── mgmt-cluster/
│   ├── dtit/
│   ├── mom/
│   └── support/
├── functions/
│   ├── calico/
│   │   ├── caas-calico-0.10.2.yaml
│   │   └── ...
│   ├── coredns/
│   │   ├── coredns-1.24.14.yaml
│   │   └── ...
│   └── ...
└── actions/
    ├── customer-kubeconfig/
    ├── clearview-register/
    └── ...
```

## Product File Structure

Each product file is a YAML file with the following structure:

```yaml
apiVersion: caas.pan-net.eu/v1alpha1
kind: CaasProduct
metadata:
  namespace: caas-operator-system
  name: <product-name>
spec:
  version: X.Y.Z
  kubernetesVersion: vX.Y.Z
  componentConfig: <component-config-name>
  productType: <product-type>
  production: true|false
  deploymentStrategy: makeBeforeBreak|...
  functions:
    - name: <function-name>
      version: X.Y.Z
    ...
  actions:
    - name: <action-name>
      version: X.Y.Z
      stages: [pre-build, post-build, pre-upgrade, post-upgrade, delete]
    ...
```

## Function File Structure

Functions define Helm chart deployments:

```yaml
apiVersion: caas.pan-net.eu/v1alpha1
kind: CaasFunction
metadata:
  namespace: caas-operator-system
  name: <function-name>-<version>
spec:
  name: <function-name>
  version: X.Y.Z
  provides:
    - <capability>
  requires:
    - <dependency>
  source:
    - name: <helm-chart-name>
      version: X.Y.Z
      namespace: <target-namespace>
      repoURL: <helm-repository-url>
      valuesData: |
        # Helm values template
```

## Function File Discovery

Functions may be in different directories than their name suggests:

| Function Name | Directory |
|--------------|-----------|
| `caas-calico` | `functions/calico/` |
| `coredns` | `functions/coredns/` |
| `caas-monitoring` | `functions/caas-monitoring/` |

The scripts handle this by searching for function files recursively.

## Version Numbering

Products follow semantic versioning with three components:
- **Major**: Kubernetes version alignment (e.g., 34 for k8s 1.34)
- **Minor**: Feature release
- **Patch**: Bug fixes and updates

Example: `baremetal-cluster-34.6.10`
- Kubernetes 1.34
- Feature release 6
- Patch 10

## Actions and Stages

Actions run at specific lifecycle stages:

| Stage | When Executed |
|-------|---------------|
| `pre-build` | Before cluster creation |
| `post-build` | After cluster creation |
| `pre-upgrade` | Before cluster upgrade |
| `post-upgrade` | After cluster upgrade |
| `delete` | During cluster deletion |
