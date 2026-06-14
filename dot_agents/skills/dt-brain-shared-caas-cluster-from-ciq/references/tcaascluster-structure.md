# TCaasCluster YAML Structure Reference

The TCaasCluster CR is the primary definition for a converged workload cluster.
Below is the field-by-field mapping showing where each value typically comes from.

## Top-level metadata

```yaml
apiVersion: t-caas.telekom.com/v1alpha1
kind: TCaasCluster
metadata:
  annotations: {}
  labels:
    caas-operator/dry-run: 'false'        # Start with 'true' for new clusters
    caas-operator/maintenance: 'false'
  name: <cluster-name>                     # e.g. czbrnc1-5gc-prod
  namespace: c-<cluster-name>              # Always prefixed with "c-"
```

**Source**: Cluster name from user input. Namespace is derived.

## spec.environment & spec.location

```yaml
spec:
  environment: production                  # production | staging | development
  location: hc-<site-code>                # hc- (Housekeeper Cloud), ic- (Infra Cloud), cl- (Central Lab)
```

**Source**: Site code from CiQ overview. Prefix convention:
- `hc-` = Housekeeper Cloud (NatCo hardware, production)
- `ic-` = Infrastructure Cloud (TDI hardware, legacy/lab)
- `cl-` = Central Lab (bare metal lab)

## spec.config

```yaml
  config:
    ref:
      name: tdi-0.2.1                     # Config version — from template cluster
      namespace: t-caas-operator-system
    overrides:
      bundle:
        functions:
          calico:
            ipipEnabled: false             # Usually false for bare metal
          coredns:
            extraZones:                    # DNS zones from CiQ Network Config
              - name: <domain>:53
                nameservers: [<ip1>, <ip2>]
          sriov-network-device-plugin:
            config:
              resourceList: [...]          # FROM CiQ: SRIOV_Hugepage sheet
          flux-workload:                   # FROM template
          tenant-resources:                # FROM template, path adjusted for new cluster
          thirdparty-resources:            # FROM template
```

## spec.dns

```yaml
  dns:
    providerRef:
      apiGroup: dns.t-caas.telekom.com
      kind: PowerdnsDNSProvider
      name: prod
    zone: <cluster-name>.caas.in.pan-net.eu
```

**Source**: Template. Zone derived from cluster name.

## spec.tenant

```yaml
  tenant:
    ref:
      name: tmcz                           # NatCo tenant name
      namespace: t-caas-operator-system
```

**Source**: Template (same NatCo = same tenant).

## spec.bundle

```yaml
  bundle:
    provider: flux
    ref:
      namespace: t-caas-operator-system
      name: netbox-workload-33.2.17        # Bundle version — from template
```

**Source**: Template cluster. Use latest version from same NatCo.

## spec.networkProfile

```yaml
  networkProfile:
    ref:
      name: default-0.3.0
      namespace: t-caas-operator-system
    inputs:
      networkSupplier: cisco               # cisco | juniper — from template/user
      serviceSubnet: 100.81.0.0/17         # FROM template or user (TODO if unknown)
      dthSubnet: 10.235.97.128/26          # FROM user input
      dthVLANId: 1043                      # FROM user or TODO
      oamSubnet: 10.247.142.0/26           # FROM CiQ: IP Subnet sheet, OAM row
      oamVLANId: 152                       # FROM user or TODO
      podSubnet: 192.168.0.0/16            # Usually standard
```

## spec.compute

```yaml
  compute:
    image:
      selector:                            # FROM template — OS and software versions
        operatingSystem:
          architecture: amd64
          distribution: Ubuntu
          variant: generic
          version: '24.04'
        software:
          containerd: v2.1.4
          flavour: tcaas-ofed
        tCaaSVersion: build-update-to-1.33.7-...
    controlPlane:
      replicas: 3                          # Always 3 for production
      computeProfile:
        inputs:
          Flavor: Profile7.1               # FROM template
      networkProfile:
        machineType: ens1                  # FROM template
      bootstrapConfig:
        ref:
          name: netbox-control-plane-0.3.1
        labels: {}
        taints: []
        apiServer:
          extraSANs:
            - <K8S_API_VIP>               # FROM CiQ: IP Subnet, "OAM K8 access API" row
```

## spec.compute.workerGroups

```yaml
    workerGroups:
      - replicas: 21                       # FROM CiQ: SRIOV_POD_Distribution count
        name: workergroup1-upf-vlb         # Naming from CiQ worker layout
        computeProfile:
          inputs:
            Hugepages1G: 240               # FROM CiQ: SRIOV_Hugepage / Platform_pre-requisites
            HugepageDefaultSize: 1G
            CPUPinning: 'true'             # FROM CiQ: Platform_pre-requisites
            CPUPinningKubelet: 8
            ExtraGrubParameters: ...       # FROM CiQ: Platform_pre-requisites
            ExtraSysctlParameters: |       # FROM CiQ: Platform_pre-requisites (sysctl rows)
              net.core.message_burst = 256
              ...
            ExtraLimits: |-                # FROM CiQ: Platform_pre-requisites
              ...
            CqeCompression: 1              # FROM template (NIC tuning)
            FlexParserProfileEnable: 3     # FROM template (NIC tuning)
            Flavor: Profile26.6ai.1        # FROM template (hardware profile)
            ServerPool: <cluster-name>     # Derived from cluster name
        networkProfile:
          machineType: ens2                # FROM template
        bootstrapConfig:
          ref:
            name: netbox-worker-0.1.2
          labels:                          # FROM CiQ: SRIOV_POD_Distribution
            isupf: 'yes'
            isvlb: 'yes'
            mavenir_core: 'true'
          taints: []
```

## spec.storage

```yaml
  storage:
    pools:
      - name: <cluster-name>
        profile:
          inputs:
            encryptionSecretName: ceph-<cluster-name>-encryption
            standard: 'true'
            rwxMonitorOnePort: '6789'
            rwxMonitorOneIPAddress: 0.0.0.0    # TODO: Ceph monitor IP
            ...
            rwxPoolName: cephfs.<cluster-name>-rwx.data
            fsName: <cluster-name>-rwx
            rwxAuthSecretName: ceph-<cluster-name>-rwx
            rwoMonitorOnePort: '3300'
            rwoMonitorOneIPAddress: 0.0.0.0    # TODO: Ceph monitor IP
            ...
            rwoPoolName: <cluster-name>
            rwoAuthSecretName: ceph-<cluster-name>-rwo
            rwoClusterID: 00000000-...         # TODO: Ceph cluster ID
            rwxClusterID: 00000000-...         # TODO: Ceph cluster ID
          ref:
            name: ceph-rwo-rwx-0.3.0
            namespace: t-caas-operator-system
```

**Source**: Structure from template. Pool/secret names derived from cluster name.
Ceph monitor IPs and cluster IDs are always TODO — populated during deployment.

## SRIOV resourceList Entry Pattern

Each SRIOV resource follows this pattern:

```yaml
- deviceType: netDevice
  excludeTopology: false
  resourceName: mellanox_mlx5_dpdk_<side>_<interface>_<numa>
  resourcePrefix: mellanox.com
  selectors:
    - isRdma: true
      devices:
        - 101e                              # ConnectX-6 Dx device ID
      drivers:
        - mlx5_core
      pfNames:
        - <pf_name>#<vf_index>             # e.g. ens3f0np0#0 (numa0 left)
      needVhostNet: false
```

### PF Name to NUMA/Side Mapping (typical)
| PF Name | Side | NUMA |
|---------|------|------|
| ens3f0np0 | left | numa0 |
| ens3f1np1 | right | numa0 |
| ens6f0np0 | left | numa1 |
| ens6f1np1 | right | numa1 |

VF index (`#N`) increments per interface on the same PF.
