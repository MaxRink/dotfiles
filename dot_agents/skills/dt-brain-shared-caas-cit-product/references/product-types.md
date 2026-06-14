# CaaS Product Types Reference

This document describes the different CaaS product types and folder structure in the `caas-bundles` repository.

## Table of Contents

- [Product Types](#product-types)
- [Repository Structure](#repository-structure)
- [Product File Structure](#product-file-structure)
- [ComponentConfig File Structure](#componentconfig-file-structure)
- [Key ComponentConfig Sections](#key-componentconfig-sections)
- [ExtraParams Templating](#extraparams-templating)
- [Function File Structure](#function-file-structure)
- [Function File Discovery](#function-file-discovery)
- [Version Numbering](#version-numbering)
- [Actions and Stages](#actions-and-stages)

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
  componentConfig: <component-config-name>  # e.g., baremetal-3.0.19
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

## ComponentConfig File Structure

ComponentConfigs define cluster-level Kubernetes configuration (kube-apiserver, kubelet, etcd, kubeadm, etc.).
They are stored in `componentconfig/` and referenced by products via the `spec.componentConfig` field.

```
caas-bundles/
├── componentconfig/
│   ├── baremetal-3.0.19.yaml
│   ├── baremetal-2.5.10.yaml
│   └── ...
```

Each componentConfig is a `CaasComponentConfig` resource:

```yaml
apiVersion: caas.pan-net.eu/v1alpha1
kind: CaasComponentConfig
metadata:
  namespace: caas-operator-system
  name: baremetal-3.0.19
spec:
  name: baremetal
  version: 3.0.19
  enabledFeatures:
    - RoleAndWorkerGroupNodeLabels
    - JSONSerializedTemplatesHash
    - ...
  bareMetal:
    ramdiskCommands: [...]           # Shell scripts run during provisioning
    kubeadmConfigTemplate:
      files:                         # Files placed on nodes (e.g., kubelet drop-ins)
        - path: /var/lib/kubelet/kubelet.conf.d/09-caas-kubelet.conf
          content: ...
      clusterConfiguration:
        apiServer:
          extraArgs:                 # kube-apiserver flags
            audit-log-path: /var/log/kubernetes/audit.log
            audit-policy-file: /etc/kubernetes/audit-policy/apiserver-audit-policy.yaml
            ...
          extraVolumes:              # Additional volume mounts for apiserver pod
            - name: audit-log
              hostPath: /var/log/kubernetes/
              mountPath: /var/log/kubernetes/
        controllerManager:
          extraArgs:
            profiling: "false"
        scheduler:
          extraArgs:
            profiling: "false"
        etcd:
          local: {}
        networking:
          podSubnet: '{{ dig "podSubnet" "" .ClusterSpec.ExtraParams }}'
          serviceSubnet: '{{ dig "serviceSubnet" "" .ClusterSpec.ExtraParams }}'
      initConfiguration:
        nodeRegistration:
          kubeletExtraArgs:          # kubelet flags for control plane nodes
            authorization-mode: Webhook
            cgroup-driver: systemd
            ...
      joinConfiguration:
        nodeRegistration:
          kubeletExtraArgs:          # kubelet flags for worker nodes
            ...
```

### Key ComponentConfig Sections

| Section | Path | Description |
|---------|------|-------------|
| **apiServer extraArgs** | `clusterConfiguration.apiServer.extraArgs` | kube-apiserver flags (admission plugins, audit, etc.) |
| **apiServer extraVolumes** | `clusterConfiguration.apiServer.extraVolumes` | Volume mounts for apiserver pod |
| **kubelet extraArgs** | `initConfiguration/joinConfiguration.nodeRegistration.kubeletExtraArgs` | kubelet flags |
| **kubelet drop-in** | `files[].path=/var/lib/kubelet/kubelet.conf.d/09-caas-kubelet.conf` | KubeletConfiguration drop-in, supports `kubeletDropIn` ExtraParams |
| **controller-manager** | `clusterConfiguration.controllerManager.extraArgs` | Controller manager flags |
| **scheduler** | `clusterConfiguration.scheduler.extraArgs` | Scheduler flags |
| **etcd** | `clusterConfiguration.etcd` | etcd configuration |
| **enabledFeatures** | `spec.enabledFeatures` | CaaS operator feature flags |
| **ramdiskCommands** | `spec.bareMetal.ramdiskCommands` | Shell scripts for node provisioning |

### ExtraParams Templating

ComponentConfigs use Go templates with `ExtraParams` for per-cluster customization:

```yaml
# Template syntax examples:
{{ dig "component_config" "kubelet" "reservation" false .ClusterSpec.ExtraParams }}
{{ dig "apiserver" "dnsPolicy" "ClusterFirst" .ClusterSpec.ExtraParams }}
{{ dig "podSubnet" "" .ClusterSpec.ExtraParams }}
```

This allows cluster-specific values without modifying the componentConfig itself.

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
