# Redfish Standard API Reference

Redfish is a DMTF standard for server management APIs. All major vendors (Lenovo, HPE, Dell) implement Redfish with vendor-specific extensions.

## Base Concepts

### Authentication
```bash
# Session-based (recommended)
POST /redfish/v1/SessionService/Sessions
Content-Type: application/json
{"UserName": "admin", "Password": "password"}

# Response includes X-Auth-Token header for subsequent requests

# Basic Auth (simpler, less secure)
curl -u admin:password https://bmc-ip/redfish/v1/Systems
```

### Common HTTP Methods
| Method | Usage |
|--------|-------|
| GET | Read resource |
| POST | Create resource or perform action |
| PATCH | Update resource (partial) |
| PUT | Replace resource (full) |
| DELETE | Remove resource |

## Core Endpoints

### Service Root
```
GET /redfish/v1/
```
Returns available services and API version.

### Systems Collection
```
GET /redfish/v1/Systems
GET /redfish/v1/Systems/1
```
Server system information, power state, boot settings.

### Chassis Collection
```
GET /redfish/v1/Chassis
GET /redfish/v1/Chassis/1
```
Physical chassis information, sensors, power supplies.

### Managers Collection (BMC)
```
GET /redfish/v1/Managers
GET /redfish/v1/Managers/1
```
BMC information, network config, firmware version.

### Update Service
```
GET /redfish/v1/UpdateService
POST /redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate
```
Firmware update operations.

## Common Operations

### Get Power State
```
GET /redfish/v1/Systems/1
# Response: {"PowerState": "On"} or {"PowerState": "Off"}
```

### Power Control
```
POST /redfish/v1/Systems/1/Actions/ComputerSystem.Reset
Content-Type: application/json
{"ResetType": "On"}           # Power on
{"ResetType": "ForceOff"}     # Force power off
{"ResetType": "GracefulShutdown"}
{"ResetType": "ForceRestart"}
```

### Get BMC Firmware Version
```
GET /redfish/v1/Managers/1
# Response includes "FirmwareVersion" field
```

### Get BIOS/UEFI Version
```
GET /redfish/v1/Systems/1
# Response includes "BiosVersion" field
```

### Get Thermal Sensors
```
GET /redfish/v1/Chassis/1/Thermal
# Response includes Temperatures array with sensor readings
```

### Get Network Adapters
```
GET /redfish/v1/Systems/1/NetworkInterfaces
GET /redfish/v1/Chassis/1/NetworkAdapters
```

## Firmware Update (SimpleUpdate)

```bash
POST /redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate
Content-Type: application/json
{
  "ImageURI": "https://server/firmware.bin",
  "TransferProtocol": "HTTPS",
  "Targets": ["/redfish/v1/Managers/1"]
}
```

## OData Query Parameters

```
?$select=PowerState,Status     # Select specific fields
?$expand=Members               # Expand collections inline
?$filter=Status/Health eq 'OK' # Filter results
```

## Error Handling

Redfish returns standard HTTP codes:
- 200/201: Success
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Server error

Error response format:
```json
{
  "error": {
    "code": "Base.1.0.GeneralError",
    "message": "A general error has occurred."
  }
}
```

## Python Example (using redfish library)

```python
import redfish

# Connect
client = redfish.redfish_client(
    base_url="https://bmc-ip",
    username="admin",
    password="password"
)
client.login()

# Get system info
response = client.get("/redfish/v1/Systems/1")
print(f"Power: {response.dict['PowerState']}")
print(f"BIOS: {response.dict['BiosVersion']}")

# Get BMC info
response = client.get("/redfish/v1/Managers/1")
print(f"BMC: {response.dict['FirmwareVersion']}")

client.logout()
```

## Useful Resources

- DMTF Redfish Specification: https://www.dmtf.org/standards/redfish
- Redfish Schema Bundle: https://redfish.dmtf.org/schemas/
- Python Redfish Library: https://github.com/DMTF/python-redfish-library
