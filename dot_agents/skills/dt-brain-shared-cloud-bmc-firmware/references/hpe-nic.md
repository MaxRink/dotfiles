# HPE NIC Firmware Reference

HPE Gen11 servers ship with Mellanox ConnectX-6 Lx NICs. Their firmware is
distributed by HPE (OEM-validated) in the same Linux SDR repository as iLO
and System ROM firmware — **no NVIDIA account required**.

## NIC Models per Server

| HPE Server | NIC Part Number | NIC Description |
|---|---|---|
| DL380 Gen11 | MCX631102AS-ADA | ConnectX-6 Lx 25GbE Dual-port SFP28 PCIe 4.0 |
| DL320 Gen11 | MCX631102AS-ADA | ConnectX-6 Lx 25GbE Dual-port SFP28 PCIe 4.0 |
| DL360 Gen11 | MCX631102AS-ADA | ConnectX-6 Lx 25GbE Dual-port SFP28 PCIe 4.0 |
| DL365 Gen11 | MCX631102AS-ADA | ConnectX-6 Lx 25GbE Dual-port SFP28 PCIe 4.0 |
| DL325 Gen11 | MCX631102AS-ADA | ConnectX-6 Lx 25GbE Dual-port SFP28 PCIe 4.0 |
| DL20 Gen10  | — | No Mellanox NIC |
| DL360 Gen10 | — | No Mellanox NIC |
| DL380 Gen10 | — | No Mellanox NIC |

## Firmware File Naming Convention

```
{VV}_{XX}_{YYYY}-{PART_NUMBER}_{Rev}.pldm.fwpkg
```

Examples:
- `26_43_1014-MCX631102AS-ADA_Ax.pldm.fwpkg` → version **26.43.1014**
- `26_44_1036-MCX631102AS-ADA_Ax.pldm.fwpkg` → version **26.44.1036**

## Download Source

HPE Linux SDR Gen11 repository (no login required):
```
https://downloads.linux.hpe.com/SDR/repo/fwpp-gen11/current/
```

List all MCX631102AS-ADA files:
```bash
curl -s https://downloads.linux.hpe.com/SDR/repo/fwpp-gen11/current/ \
  | grep -o '"[^"]*MCX631102AS-ADA[^"]*\.fwpkg"' | tr -d '"' | sort -V | uniq
```

## Compatibility Matrix

NIC firmware compatibility must be verified against NVIDIA's official docs before use.
Different firmware versions are needed for **legacy** (MLNX_OFED) vs **doca** (DOCA-HOST) drivers.

### Checking Compatibility

URL format:
```
https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VERSION_NO_DOTS}/firmware+compatible+products
```

Example for version 26.43.1014:
```
https://docs.nvidia.com/networking/display/connectx6lxfirmwarev26431014/firmware+compatible+products
```

### Known Compatibility (HPE OEM versions)

| HPE Firmware | Certified MLNX_OFED | Certified DOCA-HOST | Recommended for |
|---|---|---|---|
| **26.39.1002** | `23.10-0.5.5.0` | — | legacy / ubuntu22 (k8s ≤1.32) |
| **26.43.1014** | `24.10-0.7.0.0` | — | legacy / ubuntu24 (k8s 1.31-1.32, best effort para 24.10-2.1.8.0) |
| **26.44.1036** | — | `2.9.1` | doca / ubuntu24 (k8s 1.33+, DOCA 2.9.x) |
| **26.45.1020** | — | `3.0.0`, `2.10.0` | doca / ubuntu24 con DOCA 3.x |
| **26.46.3048** | — | `3.1.0`, `3.0.0` | doca / ubuntu24 con DOCA 3.1.x |

> **Note**: DOCA-HOST 2.9.x uses `2.9.1` as the certified version in firmware docs.
> Versions 2.9.2 and 2.9.3 are patch releases and use the same firmware (`26.44.1036`).

### Driver Type Mapping

| `driver_type` in firmwares.json | Driver stack | OS | Target |
|---|---|---|---|
| `legacy` | MLNX_OFED | ubuntu22 | Classic OFED driver |
| `doca` | DOCA-HOST | ubuntu24 | NVIDIA DOCA platform |

## firmwares.json Entry Structure

```json
"mellanox": [
  {
    "file": "26_43_1014-MCX631102AS-ADA_Ax.pldm.fwpkg",
    "version": "26.43.1014",
    "driver_type": "legacy",
    "os": "ubuntu22"
  },
  {
    "file": "26_44_1036-MCX631102AS-ADA_Ax.pldm.fwpkg",
    "version": "26.44.1036",
    "driver_type": "doca",
    "os": "ubuntu24"
  }
]
```

## Automated Discovery

Use the `hpe-firmware-versions.py` script with `--nic` to automate the
compatibility check:

```bash
.venv/bin/python .claude/skills/cloud-bmc-firmware/scripts/hpe-firmware-versions.py \
    --model DL380-Gen11 \
    --nic \
    --target-mlnx-ofed 24.10-0.7.0.0 \
    --target-doca 2.9.1 \
    --download --download-dir ~/Downloads/firmwares
```

This will:
1. Fetch all MCX631102AS-ADA firmware versions from HPE SDR
2. Check NVIDIA docs for each version's MLNX_OFED / DOCA-HOST compatibility
3. Select the highest certified version for each driver type
4. Optionally download the matching files
