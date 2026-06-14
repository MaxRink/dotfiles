---
name: dt-brain-shared-cloud-bmc-firmware
description: This skill should be used when the user mentions "BMC", "iLO", "XCC", "XClarity", "UEFI", "BIOS firmware", "server firmware", "Lenovo firmware", "HPE firmware", "Dell iDRAC", "Redfish API", asks to "check firmware versions", "latest firmware", "firmware compatibility", "firmware update", "BMC API", or needs to query server BMC/UEFI firmware versions and Redfish API documentation for Lenovo, HPE, or Dell servers.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-bmc-firmware by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# BMC Firmware & Redfish API Reference

This skill provides two core capabilities:

1. **API Documentation**: Redfish API reference for Lenovo XCC, HPE iLO, and Dell iDRAC
2. **Firmware Discovery**: Find latest BMC/UEFI firmware versions from vendor sources

## Supported Vendors

| Vendor | BMC Type | API Docs | Firmware Discovery |
|--------|----------|----------|-------------------|
| Lenovo | XClarity Controller (XCC) | Yes | Yes |
| HPE | iLO 5/6/7 | Yes | Yes |
| Dell | iDRAC 9 | Partial | Planned |

## Server Models in CaaS Infrastructure

Based on DCIM inventory (cf_server_usage=CaaS-BM):

### Lenovo ThinkSystem (~88% of fleet)
| Model | Count | Generation | XCC Version Range |
|-------|-------|------------|-------------------|
| SR650 v2 | 505 | Whitley | 2.x - 4.x |
| SR250 v2 | 190 | Whitley | 2.x - 4.x |
| SR650 v3 | 137 | Eagle Stream | 4.x |
| SR650 | 25 | Purley | 1.x - 2.x |
| SR630 v3 | 17 | Eagle Stream | 4.x |
| SR250 v3 | 3 | Eagle Stream | 4.x |
| SR630 v2 | 3 | Whitley | 2.x - 4.x |

### HPE ProLiant (~12% of fleet)
| Model | Count | Generation | iLO Version |
|-------|-------|------------|-------------|
| DL380 Gen11 | 99 | Gen11 | iLO 6 |
| DL320 Gen11 | 12 | Gen11 | iLO 6 |
| DL20 Gen10 | 9 | Gen10 | iLO 5 |

## Mellanox Driver Versions in Production (CIT CaaS)

The authoritative source for which OFED/DOCA driver versions are deployed in CaaS clusters is:

```
caas-image-builder/.gitlab-ci.yml  →  .matrix.parallel.matrix  →  MELLANOX_SW field
```

GitLab: `https://gitlab.devops.telekom.de/tdi-caas/caas-image-builder`

The driver type depends on **Kubernetes version**:
- **K8s < 1.33** → `legacy` → MLNX_OFED drivers
- **K8s ≥ 1.33** → `doca` → DOCA-HOST drivers

Use the helper script to extract the current versions:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/parse_ci_drivers.py
# Output example:
# mlnx_ofed: 24.10-2.1.8.0  (highest OFED version across all K8s/Ubuntu combinations)
# doca:      2.9.3           (highest DOCA version across all K8s/Ubuntu combinations)
```

The firmware scripts use this automatically when `--nic` is specified (no manual `--target-*` needed):

```bash
# Auto-reads OFED + DOCA from caas-image-builder CI config
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3 --nic
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --model DL380-Gen11 --nic

# Explicit CI config path (if not in default location)
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --model DL380-Gen11 \
    --nic --ci-config /path/to/caas-image-builder/.gitlab-ci.yml
```

> **Note**: Whenever DOCA or OFED versions change in `caas-image-builder`, the NIC firmware
> compatibility check will automatically pick up the new targets on the next script run.

## Firmware Version Discovery

### Automated Script (Recommended)

Uses the **Lenovo support JSON API** directly — no browser or Selenium required.

```bash
# List supported models (with platform and NIC generation)
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --list-models

# Query specific model
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3

# Query multiple models
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3 --model SR630V2

# Query all CaaS models
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --all

# JSON output for parsing
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --all --format json

# Include NIC firmware with NVIDIA compatibility check (V3 models only)
# OFED/DOCA targets are auto-read from caas-image-builder CI config:
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3 --nic

# Override targets explicitly if needed:
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3 \
    --nic --target-mlnx-ofed 24.10-2.1.8.0 --target-doca 2.9.3

# Download all firmware files (including NIC)
.venv/bin/python ${SKILL_DIR}/scripts/lenovo-firmware-versions.py --model SR650V3 \
    --nic --target-doca 2.9.3 \
    --download --download-dir ~/Downloads/firmwares
```

**Supported models**: SR650V3, SR630V3, SR650V2, SR630V2, SR250V2, SR650

### NIC Firmware (Lenovo — Mellanox ConnectX)

NIC firmware format and naming differ by generation:

| Generation | Format | Version in filename | NVIDIA compat check |
|------------|--------|---------------------|---------------------|
| V3 (Eagle Stream) | `.uxz` inside `.zip` | `xx.47.1026` → `26.47.1026` | ✅ Full |
| V2 (Whitley) | `.bin` | `doca-3.1.0-2` or `24.04-0.6.6.0-0` | ❌ Not possible |

> See [references/lenovo-nic.md](references/lenovo-nic.md) for full NIC firmware details.

### Model API Notes

All generations use the same JSON API endpoint. The Referer header is required — the API returns "deny access" without it. No Selenium or browser is needed.

### HPE ProLiant Firmware Script

The script queries the **HPE Linux SDR repository** directly — no browser, no login required.
Source: `https://downloads.linux.hpe.com/SDR/repo/fwpp-gen{10,11}/current/`

```bash
# List supported HPE models (with iLO gen, ROM U-code and NIC part)
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --list-models

# Query specific model
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --model DL380-Gen11

# Query all CaaS HPE models
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --all

# JSON output (includes filenames for firmwares.json)
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --all --format json

# Query iLO + SystemROM + NIC firmware with compatibility check
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --model DL380-Gen11 \
    --nic --target-mlnx-ofed 24.10-0.7.0.0 --target-doca 2.9.1

# Query and download all firmware files (including NIC)
.venv/bin/python ${SKILL_DIR}/scripts/hpe-firmware-versions.py --model DL380-Gen11 \
    --nic --target-mlnx-ofed 24.10-0.7.0.0 --target-doca 2.9.1 \
    --download --download-dir ~/Downloads/firmwares
```

**Supported HPE models**: DL380-Gen11, DL320-Gen11, DL360-Gen11, DL365-Gen11, DL325-Gen11, DL20-Gen10, DL360-Gen10, DL380-Gen10

### NIC Firmware (HPE Gen11 — Mellanox ConnectX-6 Lx)

HPE Gen11 servers include a **Mellanox MCX631102AS-ADA** (ConnectX-6 Lx). The firmware is
distributed by HPE in the same SDR repo as iLO/SystemROM, in `.pldm.fwpkg` format.

**Key rule**: NIC firmware must be cross-referenced with NVIDIA docs to ensure compatibility
with the driver version deployed. The driver type is determined by **Kubernetes version**:
- `legacy` — MLNX_OFED drivers, used for **K8s < 1.33**
- `doca` — DOCA-HOST drivers, used for **K8s ≥ 1.33**

Compatibility check URL:
```
https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VERSION_NO_DOTS}/firmware+compatible+products
# e.g. version 26.43.1014 → connectx6lxfirmwarev26431014
```

| HPE Firmware | MLNX_OFED certified | DOCA-HOST certified | Use for |
|---|---|---|---|
| 26_39_1002 | 23.10-0.5.5.0 | — | legacy (k8s ≤1.32, OFED 23.10) |
| 26_43_1014 | 24.10-0.7.0.0 | — | legacy (k8s ≤1.32, OFED 24.10) |
| 26_44_1036 | — | 2.9.1 | doca (k8s ≥1.33, DOCA 2.9.x) |
| 26_45_1020 | — | 3.0.0 / 2.10.0 | doca (k8s ≥1.33, DOCA 3.x) |
| 26_46_3048 | — | 3.1.0 / 3.0.0 | doca (k8s ≥1.33, latest) |

> See [references/hpe-nic.md](references/hpe-nic.md) for full NIC firmware details.

### System ROM U-code Mapping (HPE)

Each HPE server model has a unique System ROM identifier (U-code). The firmware filename format is:
`U<CODE>_<VERSION>_<MM>_<DD>_<YYYY>.fwpkg`

| Model | U-code | iLO Gen | Repo |
|-------|--------|---------|------|
| DL380 Gen11 | U54 | iLO 6 | fwpp-gen11 |
| DL320 Gen11 | U63 | iLO 6 | fwpp-gen11 |
| DL360 Gen11 | U58 | iLO 6 | fwpp-gen11 |
| DL365 Gen11 | U59 | iLO 6 | fwpp-gen11 |
| DL325 Gen11 | U62 | iLO 6 | fwpp-gen11 |
| DL20 Gen10  | U43 | iLO 5 | fwpp-gen10 |
| DL360 Gen10 | U32 | iLO 5 | fwpp-gen10 |
| DL380 Gen10 | U30 | iLO 5 | fwpp-gen10 |

> **Note**: iLO firmware is shared across all models of the same generation.
> If two profiles use the same model (e.g. DL380 Gen11), the iLO file only needs to be downloaded once.

### Manual WebSearch (Fallback)

If the script doesn't work, use WebSearch with specific queries.

### Lenovo ThinkSystem Servers

Search pattern:
```
Lenovo ThinkSystem <MODEL> firmware XCC UEFI latest download site:datacentersupport.lenovo.com
```

Example for SR630 V3:
```
Lenovo ThinkSystem SR630 V3 firmware XCC UEFI latest download site:datacentersupport.lenovo.com
```

**Key information to extract:**
- XCC (BMC) version: e.g., `4.15`
- UEFI version: e.g., `5.11`
- Release date
- Download URL from datacentersupport.lenovo.com

### HPE ProLiant Servers

Search pattern:
```
HPE ProLiant <MODEL> firmware iLO BIOS SPP latest site:support.hpe.com
```

Example for DL360 Gen10 Plus:
```
HPE ProLiant DL360 Gen10 Plus firmware iLO6 BIOS latest site:support.hpe.com
```

**Key information to extract:**
- iLO version: e.g., `3.18` (iLO 5), `1.74` (iLO 6)
- System ROM (BIOS) version: e.g., `U32`
- SPP version if applicable
- Release date

### Dell PowerEdge Servers (Future)

Search pattern:
```
Dell PowerEdge <MODEL> firmware iDRAC BIOS latest site:dell.com/support
```

## Comparing with Current Versions

When the user has a `firmwares.json` file (typically at `https://<proxy>/firmwares/firmwares.json`), compare discovered versions with current versions:

1. Search for latest versions using the patterns above
2. Parse the user's current versions from their firmwares.json
3. Report differences:
   ```
   Server: SR630 V3 (Profile7.1)
   Component    Current    Latest    Status
   XCC (BMC)    4.14       4.15      UPDATE AVAILABLE
   UEFI         5.10       5.11      UPDATE AVAILABLE
   ```

## API Documentation

For Redfish API development and scripting, see the reference files:

- **Redfish Standard**: See [references/redfish-standard.md](references/redfish-standard.md) for DMTF Redfish basics
- **Lenovo XCC**: See [references/lenovo-xcc.md](references/lenovo-xcc.md) for Lenovo-specific endpoints
- **HPE iLO**: See [references/hpe-ilo.md](references/hpe-ilo.md) for HPE-specific endpoints

## Common Firmware Update Sequence

When updating multiple firmware components, follow this order:

1. **BMC first** (XCC/iLO) - Can be updated with server ON
2. **UEFI/BIOS second** - Requires server OFF for Lenovo, varies for HPE
3. **NIC firmware last** - Requires server ON, then reboot

## Useful URLs

### Lenovo
- Firmware downloads: `https://datacentersupport.lenovo.com/us/en/products/servers/thinksystem/<model>/downloads`
- XCC REST API docs: `https://pubs.lenovo.com/xcc-restapi/`
- Best practices: `https://lenovopress.lenovo.com/lp1991`

### HPE
- SPP Home: `https://support.hpe.com/docs/display/public/a00sppdocen_US/spp/`
- iLO 5 API: `https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/`
- iLO 6 API: `https://hewlettpackard.github.io/ilo-rest-api-docs/ilo6/`
- Developer Portal: `https://developer.hpe.com/platform/ilo-restful-api/home/`

### Dell (Future)
- iDRAC API: `https://developer.dell.com/apis/2978/versions/6.xx/docs/0Background.md`

## Example Use Cases

1. **Check latest firmware for a server model**:
   - User: "What's the latest XCC version for SR630 V3?"
   - Action: WebSearch for Lenovo SR630 V3 firmware, extract XCC version

2. **Compare with current deployment**:
   - User: "Is my Profile7.1 firmware up to date?"
   - Action: Search latest versions, compare with user's firmwares.json

3. **API development help**:
   - User: "How do I get power status via Redfish on Lenovo?"
   - Action: Read lenovo-xcc.md reference, provide endpoint and example

4. **Update sequence guidance**:
   - User: "I need to update BMC and UEFI on a Lenovo server"
   - Action: Explain the correct order and power state requirements
