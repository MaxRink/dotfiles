---
name: dt-brain-shared-cloud-nvidia-firmware
description: This skill should be used when the user mentions "NVIDIA", "firmware", "ConnectX", "adapter firmware", "DOCA", "MLNX_OFED", "network adapter", asks to "check firmware", "firmware compatibility", "firmware versions", or needs to query NVIDIA ConnectX adapter firmware information and compatibility matrices.
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-nvidia-firmware by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# NVIDIA Adapter Firmware Query

This skill provides tools to query NVIDIA ConnectX adapter firmware information, including available firmware versions and their software compatibility matrices.

## Supported Adapters

Currently supports:
- **ConnectX-6 Lx**: High-performance 25/50GbE Ethernet adapters

Can be extended to support other ConnectX series (ConnectX-8, ConnectX-7, ConnectX-6 Dx, etc.)

## Information Available

### Firmware Releases
- LTS (Long-Term Support) releases
- GA (General Availability) releases
- Previous releases with version history

### Compatibility Information
For each firmware version, you can query:
- **DOCA-HOST**: Compatible versions
- **MLNX_OFED**: Compatible driver versions
- **MLNX_EN**: Compatible versions
- **WinOF-2**: Windows driver compatibility
- **MFT** (Mellanox Firmware Tools): Compatible tool versions
- **FlexBoot/UEFI**: Pre-boot driver versions
- **Supported Devices**: Hardware part numbers and descriptions

## Operations

All scripts are Python-based and use web scraping to extract information from NVIDIA documentation:

```bash
.venv/bin/python ${SKILL_DIR}/scripts/<script>.py [arguments]
```

### List Available Firmware Versions

List all available firmware versions for ConnectX-6 Lx:

```bash
# List all versions (LTS + GA)
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-list-firmware.py --adapter connectx-6-lx

# List only LTS versions
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-list-firmware.py --adapter connectx-6-lx --lts-only

# Output as JSON
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-list-firmware.py --adapter connectx-6-lx --format json
```

Options:
- `--adapter`: Adapter model (default: `connectx-6-lx`)
- `--lts-only`: Show only LTS releases
- `--format`: Output format: `text` (default) or `json`

### Get Firmware Compatibility Information

Get detailed compatibility information for a specific firmware version:

```bash
# Get compatibility for specific version
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-firmware-compat.py --version 26.43.3608

# Include supported devices list
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-firmware-compat.py --version 26.43.3608 --include-devices

# Output as JSON
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-firmware-compat.py --version 26.43.3608 --format json
```

Options:
- `--version`: Firmware version (required)
- `--adapter`: Adapter model (default: `connectx-6-lx`)
- `--include-devices`: Include supported hardware devices list
- `--format`: Output format: `text` (default) or `json`

### Search Firmware by Software Version

Find compatible firmware versions for a specific software version:

```bash
# Find firmware compatible with DOCA-HOST version
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-search-firmware.py --software doca --version 2.9.3

# Find firmware compatible with MLNX_OFED version
.venv/bin/python ${SKILL_DIR}/scripts/nvidia-search-firmware.py --software mlnx_ofed --version 24.10-3.2.5.0
```

Options:
- `--software`: Software type: `doca`, `mlnx_ofed`, `mlnx_en`, `winof2`, `mft`
- `--version`: Software version to search for
- `--adapter`: Adapter model (default: `connectx-6-lx`)
- `--format`: Output format: `text` (default) or `json`

## Data Sources

- **Base URL**: `https://docs.nvidia.com/networking/software/adapter-firmware/`
- **Adapter Index**: Lists all available firmware versions with links to release notes
- **Release Notes**: Each firmware version has detailed compatibility tables

## Implementation Notes

The scripts use:
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- Standard library for data processing

No API key required - data is scraped from public NVIDIA documentation.

## Example Use Cases

1. **Check latest LTS firmware for ConnectX-6 Lx**:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/nvidia-list-firmware.py --adapter connectx-6-lx --lts-only
   ```

2. **Get compatibility matrix for specific firmware**:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/nvidia-firmware-compat.py --version 26.43.3608
   ```

   Output example:
   ```
   Firmware: 26.43.3608 (ConnectX-6 Lx)

   Compatible Software:
   - DOCA-HOST: 2.9.3 / 2.9.2
   - MLNX_OFED: 24.10-3.2.5.0 / 24.10-1.1.4.0 / 24.10-0.7.0.0
   - WinOF-2: 24.10.50010 / 24.7.50000 / 24.4.50000
   - MFT: 4.30.1-1210 / 4.30.1-113 / 4.30.1-8
   - FlexBoot: 3.7.500
   - UEFI: 14.37.13
   ```

3. **Find firmware compatible with your current driver**:
   ```bash
   .venv/bin/python ${SKILL_DIR}/scripts/nvidia-search-firmware.py --software mlnx_ofed --version 24.10-1.1.4.0
   ```

## Future Enhancements

- Support for additional ConnectX adapter families
- Caching mechanism for faster queries
- Comparison between firmware versions
- Download links for firmware packages
- Change log extraction
- Known issues tracking
