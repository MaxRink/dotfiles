# CiQ Sheet Guide by Vendor

CiQ (Configuration Input Questionnaire) files are Excel workbooks provided by NF vendors
describing their cluster requirements. Sheet names and structures vary by vendor.

## Mavenir CiQ Sheets

Mavenir CiQ files typically have 30-40 sheets. Key sheets for cluster definition:

| Sheet Pattern | Contains | Maps To |
|---------------|----------|---------|
| `Overview` | Site name, NatCo, revision history | Cluster naming, location |
| `Platform_pre-requisites` | Worker count, AZs, K8s version, hugepages, CPU pinning, sysctl, GRUB params, storage classes (RWO/RWX), SCTP, BIOS, ulimits | `compute.workerGroups[].computeProfile.inputs` |
| `SRIOV_Hugepage*` | SRIOV VF queue counts, hugepage memory per NF, SRIOV resource names (mellanox_mlx5_dpdk_*) with left/right and numa0/numa1 | `config.overrides.bundle.functions.sriov-network-device-plugin` |
| `SRIOV_POD_Distribution*` | Worker-to-NF mapping, worker labels (isupf, isme, isepdg, isvlb), AZ distribution | `compute.workerGroups` (replicas, labels) |
| `IP Subnet 5GC` | All network interfaces: OAM, N1-N6, S1U, S2bU, X3, IPFIX, SBA, DNS, etc. with subnets, VLANs, GWs, ranges, access type (SRIOV/MACVLAN/LB) | `networkProfile.inputs`, CoreDNS zones |
| `CNF_Networks` | Network attachment definitions | Network profile validation |
| `CIT_cloud_servers_distribution` | Rack layout, server counts, cluster sizing | Worker group replica counts |
| `Network Config` | NF FQDNs (nrf01.brn.*.3gppnetwork.org), PLMN, slices, AMF info | CoreDNS extra zones |
| `vBOM-5GC*` | Bill of materials: NF pods, vCores, RAM, storage per microservice | Capacity planning (informational) |
| `Worker Static Routes` | Static routes for workers | Network profile customization |

### Mavenir Worker Group Patterns
Mavenir typically requires 3 worker groups:
- **workergroup1-upf-vlb**: UPF + VLB workloads (labels: `isupf=yes`, `isvlb=yes`, `mavenir_core=true`)
- **workergroup2-isme**: ME/iSME workloads (labels: `isme=yes`, `mavenir_core=true`)
- **workergroup3-epdg**: ePDG workloads (labels: `isepdg=yes`, `mavenir_core=true`)

### Mavenir SRIOV Resource Naming
Pattern: `mellanox_mlx5_dpdk_{side}_{interface}_{numa}`
- Side: `left` (port 0) or `right` (port 1)
- Interface: `n3`, `s1u`, `s2bu`, `n4u`, `n6`, `x3`, `ipfix`, `trust`, `untrust`, `vlbtrust`, `vlbuntrust`, `syslog`, `swu`, `epdgs2bu`, `epdgvlb`, `s5_sgw_u`, etc.
- NUMA: `numa0` or `numa1`

## Nokia CiQ Sheets

Nokia CiQ files (SDVoice, IMS, etc.) tend to be more compact:

| Sheet Pattern | Contains | Maps To |
|---------------|----------|---------|
| `Cluster Info` / `Overview` | Site, cluster sizing | Cluster naming |
| `Server Configuration` | Hardware profiles, CPU, memory | Compute profiles |
| `Network Configuration` | VLANs, subnets, bonding | Network profile inputs |
| `SRIOV Configuration` | VF counts, PF names | SRIOV device plugin config |
| `Storage` | Ceph/storage requirements | Storage pools |

### Nokia Worker Group Patterns
Nokia clusters may have different groupings:
- Worker groups often named by function (e.g., `sdv-workers`, `media-workers`)
- Labels vary by product line

## Ericsson CiQ Sheets

Ericsson (ECCD/CCD-based) CiQ files:

| Sheet Pattern | Contains | Maps To |
|---------------|----------|---------|
| `Deployment Info` | Cluster parameters | Cluster config |
| `Network Design` | Network interfaces, VLANs | Network profile |
| `Compute Design` | Server specs, roles | Compute/worker groups |
| `SRIOV` | VF configuration | SRIOV config |

> **Note**: When encountering an unknown vendor CiQ format, explore all sheets and look for
> patterns matching the TCaasCluster fields. The key data points are always the same
> (workers, networks, SRIOV, storage) — just organized differently.
