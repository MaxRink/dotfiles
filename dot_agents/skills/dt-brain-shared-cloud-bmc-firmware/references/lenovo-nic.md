# Lenovo ThinkSystem NIC Firmware Reference

## Overview

Lenovo ThinkSystem servers use Mellanox ConnectX NICs. Firmware distribution and
naming conventions differ by server generation.

## NIC Generations in CaaS Fleet

| Generation | Platform  | Models               | File Format | Version Naming  |
|------------|-----------|----------------------|-------------|-----------------|
| V3         | Eagle Stream | SR650 V3, SR630 V3 | `.uxz` (inside `.zip`) | `xx.XX.XXXX` → `26.XX.XXXX` |
| V2         | Whitley   | SR650 V2, SR630 V2   | `.bin`      | DOCA/OFED label in filename |
| V1         | Purley    | SR650                | N/A         | No Mellanox NIC confirmed |

## File Naming Conventions

### V3 (Eagle Stream) — `.uxz` format

Lenovo distributes as `.zip`; the `.uxz` inside is the actual firmware file.
The `xx` prefix in the filename maps to `26` (ConnectX-6 Lx family):

```
mlnx-lnvgy_fw_nic_cx-xx.47.1026-ja0ib-06c2_anyos_comp.zip
  → mlnx-lnvgy_fw_nic_cx-xx.47.1026-ja0ib-06c2_anyos_comp.uxz (inside)
  → NIC firmware version: 26.47.1026
```

The direct `.uxz` URL can be derived by replacing `.zip` with `.uxz` in the
download URL.

### V2 (Whitley) — `.bin` format

Lenovo distributes Linux firmware packages as `.bin`. The DOCA or OFED version
is embedded in the filename (not the NIC firmware version number):

```
mlnx-lnvgy_fw_nic_cx-doca-3.1.0-2_linux_x86-64.bin    ← DOCA-certified
mlnx-lnvgy_fw_nic_cx-24.04-0.6.6.0-0_linux_x86-64.bin ← OFED-certified
```

> **Note**: The NIC firmware version (e.g. `26.41.1000`) is NOT in the V2
> filename. It must be looked up in the release notes or NVIDIA compat docs.

## NVIDIA Compatibility Check

Only possible for **V3 models** where the NIC firmware version is numeric.

URL format:
```
https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VERSION_NO_DOTS}/firmware+compatible+products
# e.g. 26.47.1026 → connectx6lxfirmwarev26471026
```

## Available NIC Firmware for CaaS Models (Current)

### SR650 V3 / SR630 V3

| Version   | Date     | DOCA Certified | OFED Certified | Notes |
|-----------|----------|----------------|----------------|-------|
| 26.47.1026 | Jan 2026 | 3.2.0 / 3.1.0 | —              | Latest |
| 26.43.2026 | Feb 2025 | —              | —              | No compat page |

> ⚠️ No version certified for DOCA 2.9.x (production target). Accept as best-effort.

### SR650 V2 / SR630 V2

| Filename label | Date     | Notes |
|----------------|----------|-------|
| `doca-3.1.0-2` | Nov 2025 | Latest |
| `doca-3.0.0-2` | ~2024    | Previous |

> ⚠️ DOCA 2.9.x is not available. Latest (`doca-3.1.0`) is best-effort.

## Lenovo API Endpoint

Discovery is done via the Lenovo support API (no browser/Selenium needed):

```
GET https://datacentersupport.lenovo.com/us/en/api/v4/downloads/drivers
    ?productId=servers%2Fthinksystem%2F{model_url}%2F{type_code}

Required header: Referer: https://datacentersupport.lenovo.com/us/en/products/servers/thinksystem/{model_url}/{type_code}/downloads/driver-list/
```

Filter items where `Title` contains `"mellanox"` and `"Firmware"`.

### Product IDs

| Model   | url_name | type_code |
|---------|----------|-----------|
| SR650V3 | sr650v3  | 7d76      |
| SR630V3 | sr630v3  | 7d72      |
| SR650V2 | sr650v2  | 7z73      |
| SR630V2 | sr630v2  | 7z71      |
| SR250V2 | sr250v2  | 7d7q      |
| SR650   | sr650    | 7x06      |

## Production Driver Targets (caas-image-builder)

| K8s     | Ubuntu | Driver              |
|---------|--------|---------------------|
| 1.31-1.32 | 22.04 | OFED 23.10-0.5.5.0 |
| 1.31-1.32 | 24.04 | OFED 24.10-2.1.8.0 |
| 1.33    | 24.04  | DOCA 2.9.2          |
| 1.34-1.35 | 24.04 | DOCA 2.9.3         |
