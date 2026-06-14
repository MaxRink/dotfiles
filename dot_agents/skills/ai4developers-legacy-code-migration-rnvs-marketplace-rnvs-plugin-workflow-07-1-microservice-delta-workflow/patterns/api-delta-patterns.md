# API Delta Design Patterns

**Purpose**: Design patterns for API endpoint changes in delta model (endpoints_to_add, endpoints_to_modify, endpoints_to_deprecate).

**Context**: Phase 7.1 captures ONLY changes to existing microservice APIs, not complete API specifications.

---

## Endpoints to Add

### Requirements

Every endpoint in `endpoints_to_add` MUST include:

1. **Path and Method**: RESTful resource paths with HTTP methods
2. **Description**: Clear explanation of endpoint purpose and behavior
3. **Request Schema**: Complete specification of all request parameters
4. **Response Schema**: All HTTP status codes with response bodies
5. **Business Rules**: Mapping to Phase 3 business rule identifiers (BR-XXX)
6. **RNVS Source Attribution**: Traceability to legacy code (maps_from field)
7. **Authentication**: Auth requirements and authorization rules

### OpenAPI 3.0 Specification Template

```json
{
  "path": "/resource/{id}/action",
  "method": "POST",
  "description": "Business purpose of this endpoint - what it does and why",
  "request": {
    "path_parameters": [
      {
        "name": "id",
        "type": "string",
        "format": "uuid",
        "required": true,
        "description": "Resource identifier"
      }
    ],
    "query_parameters": [
      {
        "name": "validate",
        "type": "boolean",
        "required": false,
        "default": true,
        "description": "Whether to validate business rules"
      }
    ],
    "body": {
      "type": "object",
      "required": ["field1", "field2"],
      "properties": {
        "field1": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "Field description"
        },
        "field2": {
          "type": "integer",
          "minimum": 0,
          "maximum": 999,
          "description": "Field description"
        }
      }
    }
  },
  "responses": {
    "200": {
      "description": "Success response",
      "schema": {
        "type": "object",
        "properties": {
          "result_id": {"type": "string", "format": "uuid"},
          "status": {"type": "string", "enum": ["SUCCESS", "PENDING"]},
          "created_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    "400": {
      "description": "Bad request - validation failed",
      "schema": {
        "type": "object",
        "properties": {
          "error_code": {"type": "string", "example": "BR-001-VIOLATION"},
          "error_message": {"type": "string"},
          "validation_errors": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "field": {"type": "string"},
                "message": {"type": "string"},
                "business_rule": {"type": "string", "example": "BR-001"}
              }
            }
          }
        }
      }
    },
    "401": {
      "description": "Unauthorized - authentication required",
      "schema": {"$ref": "#/components/schemas/ErrorResponse"}
    },
    "403": {
      "description": "Forbidden - insufficient permissions",
      "schema": {"$ref": "#/components/schemas/ErrorResponse"}
    },
    "404": {
      "description": "Resource not found",
      "schema": {"$ref": "#/components/schemas/ErrorResponse"}
    },
    "409": {
      "description": "Conflict - resource already exists or state conflict",
      "schema": {
        "type": "object",
        "properties": {
          "error_code": {"type": "string", "example": "DUPLICATE_RESOURCE"},
          "error_message": {"type": "string"},
          "existing_resource_id": {"type": "string", "format": "uuid"}
        }
      }
    },
    "500": {
      "description": "Internal server error",
      "schema": {"$ref": "#/components/schemas/ErrorResponse"}
    }
  },
  "business_rules_enforced": [
    "BR-001: Field1 must be unique within scope",
    "BR-023: Field2 must not exceed threshold"
  ],
  "authentication": {
    "required": true,
    "type": "Bearer JWT",
    "scopes": ["resource:write"]
  },
  "maps_from": {
    "rnvs_component": "NumberValidationService",
    "rnvs_function": "validateNumberRequest",
    "rnvs_file": "src/main/java/de/telekom/rnvs/validation/NumberValidationService.java:156"
  }
}
```

### Complete Example: Adding Portability Request Endpoint

```json
{
  "path": "/portability/requests",
  "method": "POST",
  "description": "Create a new number portability request. Validates donor/recipient carriers, checks number ownership, and initiates porting workflow.",
  "request": {
    "path_parameters": [],
    "query_parameters": [],
    "body": {
      "type": "object",
      "required": ["msisdn", "donor_carrier_id", "recipient_carrier_id", "desired_port_date"],
      "properties": {
        "msisdn": {
          "type": "string",
          "pattern": "^49[1-9][0-9]{9,10}$",
          "description": "Mobile number to port (E.164 format, Germany)"
        },
        "donor_carrier_id": {
          "type": "string",
          "format": "uuid",
          "description": "Carrier currently owning the number"
        },
        "recipient_carrier_id": {
          "type": "string",
          "format": "uuid",
          "description": "Carrier requesting the number"
        },
        "desired_port_date": {
          "type": "string",
          "format": "date",
          "description": "Requested porting date (must be at least 7 days in future)"
        },
        "customer_consent": {
          "type": "boolean",
          "default": true,
          "description": "Customer consent flag (required by regulation)"
        }
      }
    }
  },
  "responses": {
    "200": {
      "description": "Portability request created successfully",
      "schema": {
        "type": "object",
        "properties": {
          "request_id": {"type": "string", "format": "uuid"},
          "status": {"type": "string", "enum": ["PENDING_VALIDATION"]},
          "created_at": {"type": "string", "format": "date-time"},
          "estimated_completion": {"type": "string", "format": "date"}
        }
      }
    },
    "400": {
      "description": "Validation failed",
      "schema": {
        "type": "object",
        "properties": {
          "error_code": {"type": "string", "example": "BR-PORT-001"},
          "error_message": {"type": "string"},
          "validation_errors": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "field": {"type": "string", "example": "desired_port_date"},
                "message": {"type": "string", "example": "Port date must be at least 7 days in future"},
                "business_rule": {"type": "string", "example": "BR-PORT-003"}
              }
            }
          }
        }
      }
    },
    "401": {"description": "Unauthorized"},
    "403": {"description": "Forbidden - carrier not authorized for this operation"},
    "404": {"description": "Donor or recipient carrier not found"},
    "409": {
      "description": "Portability request already exists for this MSISDN",
      "schema": {
        "type": "object",
        "properties": {
          "error_code": {"type": "string", "example": "DUPLICATE_PORT_REQUEST"},
          "error_message": {"type": "string"},
          "existing_request_id": {"type": "string", "format": "uuid"}
        }
      }
    },
    "500": {"description": "Internal server error"}
  },
  "business_rules_enforced": [
    "BR-PORT-001: MSISDN must be valid German mobile number (E.164)",
    "BR-PORT-002: Donor and recipient carriers must be different",
    "BR-PORT-003: Desired port date must be at least 7 days in future",
    "BR-PORT-004: Customer consent required for portability request",
    "BR-PORT-005: MSISDN must not have active portability request"
  ],
  "authentication": {
    "required": true,
    "type": "Bearer JWT",
    "scopes": ["portability:write"]
  },
  "maps_from": {
    "rnvs_component": "PortierungsService",
    "rnvs_function": "erstellePortierungsantrag",
    "rnvs_file": "rnvs-legacy/src/de/telekom/rnvs/portierung/PortierungsService.java:234"
  }
}
```

---

## Endpoints to Modify

### Requirements

Every endpoint in `endpoints_to_modify` MUST include:

1. **Path and Method**: Identify the existing endpoint being modified
2. **Schema Changes**: Detailed description of what changed
3. **Breaking Change Rationale**: Why this change is necessary
4. **Migration Guidance**: How consumers should adapt

### Template

```json
{
  "path": "/existing/endpoint/{id}",
  "method": "GET",
  "schema_changes": {
    "description": "Detailed explanation of all changes",
    "request_changes": [
      "Added new optional query parameter 'include_metadata' (non-breaking)",
      "Deprecated query parameter 'legacy_format' (will be removed in v2.0)"
    ],
    "response_changes": [
      "Added new field 'metadata' to response object (non-breaking)",
      "Changed field 'status' from string to enum (BREAKING - type change)",
      "Removed field 'legacy_id' (BREAKING - field removal)"
    ]
  },
  "breaking_change_rationale": "Standardizing status field across all endpoints for consistency. Legacy string values were ambiguous.",
  "migration_guidance": {
    "consumer_actions": [
      "Update status parsing to handle enum values: ['ACTIVE', 'INACTIVE', 'PENDING']",
      "Replace usage of 'legacy_id' with 'id' field",
      "Optional: Use 'include_metadata' parameter for additional data"
    ],
    "compatibility_period": "90 days (deprecated parameters still supported)",
    "migration_deadline": "2026-04-01"
  },
  "version_strategy": "Query parameter 'api_version=1' preserves old behavior until deadline"
}
```

### Complete Example: Modifying Number Lookup Endpoint

```json
{
  "path": "/numbers/{msisdn}/details",
  "method": "GET",
  "schema_changes": {
    "description": "Enhancing number details response with carrier information and porting history",
    "request_changes": [
      "Added optional query parameter 'include_porting_history' (default: false)",
      "Added optional query parameter 'include_carrier_details' (default: false)"
    ],
    "response_changes": [
      "Added new field 'current_carrier' with nested carrier object",
      "Added new field 'porting_history' (array of portability events)",
      "Changed field 'status' from string to structured object (BREAKING)",
      "Removed field 'legacy_status_code' (BREAKING)"
    ]
  },
  "breaking_change_rationale": "Previous 'status' field was unstructured string that mixed different status types (allocation status, activation status, porting status). New structure separates these concerns for clarity.",
  "migration_guidance": {
    "consumer_actions": [
      "Replace parsing of 'status' string with structured 'status' object fields",
      "Map old status strings: 'ACTIVE' → status.allocation='ALLOCATED' + status.activation='ACTIVE'",
      "Remove dependencies on 'legacy_status_code' (use 'status.allocation' instead)",
      "Optional: Request porting history with query param for additional context"
    ],
    "code_example": {
      "old": "if (response.status === 'ACTIVE') { ... }",
      "new": "if (response.status.allocation === 'ALLOCATED' && response.status.activation === 'ACTIVE') { ... }"
    },
    "compatibility_period": "120 days",
    "migration_deadline": "2026-05-01"
  },
  "version_strategy": "API version header 'X-API-Version: 1' preserves old response format"
}
```

---

## Endpoints to Deprecate

### Requirements

Every endpoint in `endpoints_to_deprecate` MUST include:

1. **Path and Method**: Identify the endpoint being deprecated
2. **Deprecation Reason**: Clear explanation of why
3. **Replacement**: Recommended alternative endpoint (if any)
4. **Sunset Timeline**: When endpoint will be removed

### Template

```json
{
  "path": "/legacy/endpoint",
  "method": "POST",
  "deprecation_reason": "Clear explanation of why this endpoint is being deprecated",
  "replacement": {
    "path": "/v2/new-endpoint",
    "method": "POST",
    "migration_notes": "Key differences and how to migrate"
  },
  "sunset_timeline": {
    "deprecation_date": "2026-02-01",
    "warning_period": "90 days",
    "removal_date": "2026-05-01"
  },
  "consumer_impact": {
    "estimated_clients": 12,
    "critical_clients": ["CRM-T", "Billing-System"],
    "migration_support": "Contact api-support@telekom.de for migration assistance"
  }
}
```

### Complete Example: Deprecating Legacy Number Allocation

```json
{
  "path": "/numbers/allocate",
  "method": "POST",
  "deprecation_reason": "Legacy endpoint uses synchronous allocation which causes timeout issues for large batch requests. New endpoint supports async processing with better error handling and batch capabilities.",
  "replacement": {
    "path": "/v2/numbers/allocation-requests",
    "method": "POST",
    "migration_notes": "New endpoint returns allocation request ID immediately. Poll /v2/numbers/allocation-requests/{id} for status. Supports batch allocation of up to 1000 numbers per request (vs 10 in legacy endpoint)."
  },
  "sunset_timeline": {
    "deprecation_date": "2026-02-15",
    "warning_period": "120 days (extended for critical clients)",
    "removal_date": "2026-06-15"
  },
  "consumer_impact": {
    "estimated_clients": 8,
    "critical_clients": ["CRM-T", "Partner-Portal", "Self-Service-App"],
    "migration_support": "Migration guide: https://docs.telekom.de/vnrm/migration/number-allocation-v2",
    "backward_compatibility": "Legacy endpoint will return HTTP 301 redirect to new endpoint for 30 days after removal date"
  },
  "technical_debt": "Synchronous allocation blocks database connections, causes cascading failures under load"
}
```

---

## Best Practices

### Version-Safe API Evolution

✅ **DO**: Add new optional fields to request schemas
✅ **DO**: Add new response fields (clients ignore unknown fields per JSON best practices)
✅ **DO**: Create /v2/ endpoints for breaking changes
✅ **DO**: Use API version headers for gradual migration

❌ **DON'T**: Remove required fields from requests (breaking)
❌ **DON'T**: Change response field types (breaking)
❌ **DON'T**: Remove endpoints without deprecation cycle
❌ **DON'T**: Change field semantics without version bump

### Business Rule Integration

- Map every validation error to Phase 3 business rule ID (BR-XXX)
- Include business rule descriptions in error responses
- Reference business rules in endpoint documentation
- Use consistent error codes across endpoints

### RNVS Source Attribution

- Provide exact file path and line number from RNVS legacy code
- Include component name and function name
- Explain semantic mapping (e.g., "RNVS function validates ONKZ → VNRM endpoint validates area code")

### Error Response Consistency

- Use standard error response schema across all endpoints
- Include error_code (business rule ID or system code)
- Include error_message (human-readable)
- Include validation_errors array for 400 responses
- Include correlation_id for tracing

---

## Related Patterns

- See `database-delta-patterns.md` for database changes to support new APIs
- See `event-delta-patterns.md` for events published by API endpoints
- See `dependency-patterns.md` for APIs calling other services
- See `../examples/` for complete integrated examples

---

**Use these patterns to ensure complete, consistent, high-quality API specifications in your delta model.**
