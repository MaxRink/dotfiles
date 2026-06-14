# Lenovo XClarity Controller (XCC) API Reference

XCC is Lenovo's BMC for ThinkSystem servers. It implements Redfish with Lenovo-specific extensions.

## Supported Server Models

- ThinkSystem SR630/SR650 (V1, V2, V3)
- ThinkSystem SR670
- ThinkSystem SD530/SD650
- ThinkSystem SN550/SN850 (blades)

## XCC Firmware Naming Convention

XCC firmware files follow this pattern:
```
lnvgy_fw_xcc_<build>-<version>_anyos_noarch.uxz
```

Example: `lnvgy_fw_xcc_tgbt52f-4.14_anyos_noarch.uxz`
- `tgbt52f`: Build identifier
- `4.14`: Version number

## UEFI Firmware Naming Convention

```
lnvgy_fw_uefi_<build>-<version>_anyos_32-64.uxz
```

Example: `lnvgy_fw_uefi_tqe116c-5.10_anyos_32-64.uxz`

## Lenovo-Specific Endpoints

### Get XCC Firmware Version
```
GET /redfish/v1/Managers/1
```
Response includes:
```json
{
  "FirmwareVersion": "4.14 (TEI3xxx)",
  "Oem": {
    "Lenovo": {
      "FirmwareBuildTime": "2024-03-15T10:00:00Z"
    }
  }
}
```

### Get UEFI Version
```
GET /redfish/v1/Systems/1
```
Response includes:
```json
{
  "BiosVersion": "TQE116C 5.10"
}
```

### XCC Restart (Required After BMC Update)
```
POST /redfish/v1/Managers/1/Actions/Manager.Reset
Content-Type: application/json
{"ResetType": "GracefulRestart"}
```

**Important**: After XCC firmware update, you MUST restart the XCC and wait for it to come back online before proceeding.

### Firmware Update via SimpleUpdate
```
POST /redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate
Content-Type: application/json
{
  "ImageURI": "https://proxy-server/firmwares/lnvgy_fw_xcc_tgbt52f-4.14_anyos_noarch.uxz",
  "TransferProtocol": "HTTPS",
  "Targets": ["/redfish/v1/Managers/1"]
}
```

For UEFI:
```json
{
  "ImageURI": "https://proxy-server/firmwares/lnvgy_fw_uefi_tqe116c-5.10_anyos_32-64.uxz",
  "TransferProtocol": "HTTPS",
  "Targets": ["/redfish/v1/Systems/1/Bios"]
}
```

### Check Update Task Status
```
GET /redfish/v1/TaskService/Tasks/<task-id>
```

### BIOS Attributes (Lenovo Extension)
```
GET /redfish/v1/Systems/1/Bios
GET /redfish/v1/Systems/1/Bios/Settings
PATCH /redfish/v1/Systems/1/Bios/Settings
```

Example - Set BIOS attribute:
```json
{
  "Attributes": {
    "OperatingModes_ChooseOperatingMode": "Maximum Performance"
  }
}
```

### Get Network Adapter Firmware
```
GET /redfish/v1/Chassis/1/NetworkAdapters
GET /redfish/v1/Chassis/1/NetworkAdapters/<adapter-id>
```

Response includes Mellanox adapter firmware version in `Controllers[0].FirmwarePackageVersion`.

## Quirks and Known Issues

### 1. BMC Update Requires Restart
After uploading XCC firmware, you MUST call Manager.Reset to apply it. The BMC will be unreachable for ~5 minutes during restart.

### 2. UEFI Update Requires Server OFF
UEFI firmware can only be applied when the server is powered off. The update is staged when uploaded and applied on next boot.

### 3. Timeout Considerations
- XCC restart: Wait 5-7 minutes
- UEFI staging: Usually completes in 2-3 minutes
- Firmware download: Depends on file size and network speed

### 4. Certificate Validation
XCC uses self-signed certificates by default. Disable certificate verification in scripts:
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Use verify=False in requests
```

### 5. Session Limits
XCC has limited concurrent sessions. Always logout when done:
```
DELETE /redfish/v1/SessionService/Sessions/<session-id>
```

## Python Redfish Library (Lenovo)

Lenovo provides an extended Redfish library:
- Repository: https://github.com/lenovo/python-redfish-lenovo
- Contains 80+ example scripts for common operations
- Includes BIOS management, user management, firmware updates

## Hardware Profile Mapping

Different server generations may have different UEFI/XCC build identifiers:

| Model | Platform | XCC Build | UEFI Build |
|-------|----------|-----------|------------|
| SR630 V1 | Purley | CDI | IVE |
| SR630 V2 | Whitley | TEI | TQE |
| SR630 V3 | Eagle Stream | TGB | TQE |

## Useful Debug Endpoints

```
GET /redfish/v1/Managers/1/LogServices/ActiveLog/Entries  # BMC logs
GET /redfish/v1/Systems/1/LogServices/SEL/Entries        # System Event Log
GET /redfish/v1/Chassis/1/Thermal                        # Temperature sensors
GET /redfish/v1/Chassis/1/Power                          # Power readings
```
