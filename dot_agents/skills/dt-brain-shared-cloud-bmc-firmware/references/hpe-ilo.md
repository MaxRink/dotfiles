# HPE iLO API Reference

HPE Integrated Lights-Out (iLO) is HPE's BMC for ProLiant servers. It implements Redfish with HPE-specific extensions (Oem.Hpe namespace).

## Table of Contents

- [iLO Generations](#ilo-generations)
- [Supported Server Models](#supported-server-models)
- [Firmware Naming Convention](#firmware-naming-convention)
- [HPE-Specific Endpoints](#hpe-specific-endpoints)
- [Service Pack for ProLiant (SPP)](#service-pack-for-proliant-spp)
- [Quirks and Known Issues](#quirks-and-known-issues)
- [Python Example](#python-example)
- [HPE Tools](#hpe-tools)
- [Useful Debug Endpoints](#useful-debug-endpoints)
- [Firmware Download Sources](#firmware-download-sources)

## iLO Generations

| Generation | Servers | Current Version |
|------------|---------|-----------------|
| iLO 5 | Gen10, Gen10 Plus | 3.x |
| iLO 6 | Gen11 | 1.x |
| iLO 7 | Gen12 | 1.x |

## Supported Server Models

- ProLiant DL360/DL380 (Gen10, Gen10 Plus, Gen11)
- ProLiant DL560/DL580
- ProLiant ML350
- Synergy compute modules

## Firmware Naming Convention

### iLO Firmware
```
ilo5_<version>.bin
ilo6_<version>.bin
```
Examples: `ilo5_318.bin` (version 3.18), `ilo6_174.bin` (version 1.74)

### System ROM (BIOS)
```
U<CODE>_<VERSION>_<MM>_<DD>_<YYYY>.fwpkg
```
Each server model has a unique U-code identifier:

| Model | U-code | Example |
|-------|--------|---------|
| DL380 Gen11 | U54 | `U54_2.72_11_27_2025.fwpkg` |
| DL320 Gen11 | U63 | `U63_2.72_11_27_2025.fwpkg` |
| DL360 Gen11 | U58 | `U58_2.72_11_27_2025.fwpkg` |
| DL365 Gen11 | U59 | `U59_2.72_11_27_2025.fwpkg` |
| DL325 Gen11 | U62 | `U62_2.72_11_27_2025.fwpkg` |
| DL20 Gen10  | U43 | `U43_3.72_01_09_2026.fwpkg` |
| DL360 Gen10 | U32 | `U32_x.xx_...fwpkg` |
| DL380 Gen10 | U30 | `U30_x.xx_...fwpkg` |

## HPE-Specific Endpoints

### Get iLO Firmware Version
```
GET /redfish/v1/Managers/1
```
Response includes:
```json
{
  "FirmwareVersion": "iLO 5 v3.18",
  "Oem": {
    "Hpe": {
      "Firmware": {
        "Current": {
          "VersionString": "iLO 5 v3.18"
        }
      }
    }
  }
}
```

### Get System ROM (BIOS) Version
```
GET /redfish/v1/Systems/1
```
Response includes:
```json
{
  "BiosVersion": "U32 v2.76 (03/08/2024)",
  "Oem": {
    "Hpe": {
      "Bios": {
        "Current": {
          "VersionString": "U32 v2.76 (03/08/2024)"
        }
      }
    }
  }
}
```

### Firmware Update via iLO Repository

HPE uses a component-based update system:

1. Upload firmware to iLO repository:
```
POST /redfish/v1/UpdateService/ComponentRepository
Content-Type: application/octet-stream
<binary firmware data>
```

2. Create update task:
```
POST /redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate
Content-Type: application/json
{
  "ImageURI": "https://server/ilo5_318.bin"
}
```

### iLO Reset (Apply Updates)
```
POST /redfish/v1/Managers/1/Actions/Manager.Reset
Content-Type: application/json
{"ResetType": "GracefulRestart"}
```

### Check Update Status
```
GET /redfish/v1/UpdateService/UpdateTaskQueue
```

### BIOS Settings (HPE Extension)
```
GET /redfish/v1/Systems/1/bios/settings
PATCH /redfish/v1/Systems/1/bios/settings
```

Example - Modify BIOS setting:
```json
{
  "Attributes": {
    "WorkloadProfile": "Virtualization-MaxPerformance"
  }
}
```

### Power Control
```
POST /redfish/v1/Systems/1/Actions/ComputerSystem.Reset
Content-Type: application/json
{"ResetType": "On"}
{"ResetType": "ForceOff"}
{"ResetType": "PushPowerButton"}
{"ResetType": "GracefulShutdown"}
```

### HPE SmartStorage (RAID)
```
GET /redfish/v1/Systems/1/SmartStorage
GET /redfish/v1/Systems/1/SmartStorage/ArrayControllers
```

## Service Pack for ProLiant (SPP)

HPE bundles firmware updates into SPP releases:
- Format: `YYYY.MM.0` (e.g., `2024.03.0`)
- Contains tested combinations of iLO, BIOS, and device firmware
- Download: https://support.hpe.com/spp

SPP includes:
- iLO firmware
- System ROM
- Power Management Controller
- Innovation Engine
- Server Platform Services (SPS)
- Network adapter firmware
- Storage controller firmware

## Quirks and Known Issues

### 1. iLO License Requirements
Some features require iLO Advanced license:
- Remote console
- Virtual media
- Federation management

Basic Redfish API access works without license.

### 2. Firmware Flash on Next Reset
HPE stages firmware updates and applies them on next iLO reset:
```json
{
  "Oem": {
    "Hpe": {
      "FlashOnReset": true
    }
  }
}
```

### 3. BIOS Update Requires Server Reboot
System ROM updates are staged and applied when the server reboots (not iLO reset).

### 4. Session Management
iLO has limited concurrent sessions (typically 6-10). Always logout:
```
DELETE /redfish/v1/SessionService/Sessions/<session-id>
```

### 5. Certificate Handling
iLO uses self-signed certificates. Handle in Python:
```python
import urllib3
urllib3.disable_warnings()
# requests: verify=False
# redfish library: default_prefix="/redfish/v1", verify_ssl=False
```

### 6. Different Behavior Between iLO 5 and iLO 6
- iLO 6 has additional security features
- Some endpoints moved or renamed
- Check API version compatibility

## Python Example

```python
import redfish

# Connect to iLO
client = redfish.redfish_client(
    base_url="https://ilo-ip",
    username="admin",
    password="password",
    default_prefix="/redfish/v1"
)
client.login(auth="session")

# Get iLO version
response = client.get("/redfish/v1/Managers/1")
print(f"iLO: {response.dict['FirmwareVersion']}")

# Get BIOS version
response = client.get("/redfish/v1/Systems/1")
print(f"BIOS: {response.dict['BiosVersion']}")

# Get power state
print(f"Power: {response.dict['PowerState']}")

client.logout()
```

## HPE Tools

### iLOrest
Command-line tool for iLO management:
```bash
# Login
ilorest login <ilo-ip> -u admin -p password

# Get firmware info
ilorest get FirmwareVersion --selector Manager.

# Logout
ilorest logout
```

### HPE OneView
Enterprise management platform with REST API for managing multiple servers.

## Useful Debug Endpoints

```
GET /redfish/v1/Managers/1/LogServices/IEL/Entries  # Integrated Event Log
GET /redfish/v1/Systems/1/LogServices/IML/Entries   # Integrated Management Log
GET /redfish/v1/Chassis/1/Thermal                   # Temperatures
GET /redfish/v1/Chassis/1/Power                     # Power consumption
GET /redfish/v1/Systems/1/Memory                    # Memory details
GET /redfish/v1/Systems/1/Processors                # CPU details
```

## Firmware Download Sources

### HPE Linux SDR Repository (Recommended — no login required)
- Gen11: `https://downloads.linux.hpe.com/SDR/repo/fwpp-gen11/current/`
- Gen10: `https://downloads.linux.hpe.com/SDR/repo/fwpp-gen10/current/`

Files can be downloaded directly with curl or the `--download` flag of the script.

### HPE Support Center (Alternative — may require HPE Passport account)
- HPE Support Center: https://support.hpe.com
- SPP Download: https://support.hpe.com/spp
- Driver/Firmware search by product

**Note**: The SDR repository contains individual `.fwpkg` files and is always up to date.
