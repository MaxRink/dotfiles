# Event Delta Design Patterns

**Purpose**: Design patterns for Kafka event changes in delta model (topics_to_add, subscriptions_to_add).

**Context**: Phase 7.1 captures ONLY changes to existing microservice event flows, not complete event architectures.

---

## Topics to Add

### Requirements

Every topic in `topics_to_add` MUST include:

1. **Topic Name**: Following VNRM naming convention (submodule.entity.event-type)
2. **Description**: When event is published and business context
3. **Avro Schema**: Complete schema with standard event fields
4. **Partitioning Key**: For Kafka partitioning strategy
5. **Retention Policy**: How long events are retained
6. **Replication Factor**: For fault tolerance
7. **Business Context**: Why this event exists
8. **RNVS Source**: Attribution to legacy event/trigger

### Kafka Topic Naming Convention

**Pattern**: `{submodule}.{entity}.{event-type}`

**Examples**:
- `prt.portability-request.created`
- `prt.portability-request.validated`
- `prt.portability-request.completed`
- `num.number-allocation.reserved`
- `num.number-allocation.activated`

**Event Types** (use past tense):
- `created` - Entity created
- `updated` - Entity modified
- `deleted` - Entity removed (soft delete)
- `completed` - Process finished successfully
- `failed` - Process failed
- `cancelled` - Process cancelled by user
- `validated` - Validation completed

### Avro Schema Template

```json
{
  "type": "record",
  "name": "EntityEventType",
  "namespace": "com.telekom.vnrm.submodule.events",
  "doc": "Event description - when published, why, business context",
  "fields": [
    {
      "name": "event_id",
      "type": "string",
      "doc": "Unique event identifier (UUID) - for idempotency and deduplication"
    },
    {
      "name": "event_timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "Event creation timestamp in milliseconds since epoch"
    },
    {
      "name": "event_version",
      "type": "string",
      "default": "1.0",
      "doc": "Schema version for evolution tracking"
    },
    {
      "name": "correlation_id",
      "type": ["null", "string"],
      "default": null,
      "doc": "For distributed tracing across services"
    },
    {
      "name": "causation_id",
      "type": ["null", "string"],
      "default": null,
      "doc": "ID of command/event that caused this event (event sourcing)"
    },
    {
      "name": "entity_id",
      "type": "string",
      "doc": "Business entity identifier (primary key of entity)"
    },
    {
      "name": "entity_type",
      "type": "string",
      "doc": "Entity type for polymorphic consumers"
    },
    {
      "name": "business_field_1",
      "type": "string",
      "doc": "Business-specific field documentation"
    },
    {
      "name": "business_field_2",
      "type": ["null", "int"],
      "default": null,
      "doc": "Optional business field (union with null for optional)"
    },
    {
      "name": "metadata",
      "type": {
        "type": "map",
        "values": "string"
      },
      "default": {},
      "doc": "Extensible metadata for additional context"
    }
  ]
}
```

### Complete Example: Portability Request Created Event

```json
{
  "topic_name": "prt.portability-request.created",
  "description": "Published when a new number portability request is successfully created and persisted. Triggers validation workflow and notifications to involved carriers.",
  "partitioning_key": "msisdn",
  "partitioning_strategy": "Hash by MSISDN to ensure ordering for same phone number",
  "replication_factor": 3,
  "retention_days": 30,
  "retention_policy": "Standard domain event retention (30 days for audit trail)",
  "avro_schema": {
    "type": "record",
    "name": "PortabilityRequestCreated",
    "namespace": "com.telekom.vnrm.portability.events",
    "doc": "Event published when portability request is created. Consumed by validation service, notification service, and audit service.",
    "fields": [
      {
        "name": "event_id",
        "type": "string",
        "doc": "Unique event identifier (UUID v4)"
      },
      {
        "name": "event_timestamp",
        "type": {
          "type": "long",
          "logicalType": "timestamp-millis"
        },
        "doc": "Event creation timestamp (epoch millis)"
      },
      {
        "name": "event_version",
        "type": "string",
        "default": "1.0",
        "doc": "Schema version"
      },
      {
        "name": "correlation_id",
        "type": ["null", "string"],
        "default": null,
        "doc": "Request correlation ID for distributed tracing"
      },
      {
        "name": "causation_id",
        "type": ["null", "string"],
        "default": null,
        "doc": "API request ID that caused this event"
      },
      {
        "name": "request_id",
        "type": "string",
        "doc": "Portability request ID (UUID)"
      },
      {
        "name": "msisdn",
        "type": "string",
        "doc": "Phone number being ported (E.164 format)"
      },
      {
        "name": "donor_carrier_id",
        "type": "string",
        "doc": "Current carrier UUID"
      },
      {
        "name": "recipient_carrier_id",
        "type": "string",
        "doc": "Requesting carrier UUID"
      },
      {
        "name": "desired_port_date",
        "type": {
          "type": "int",
          "logicalType": "date"
        },
        "doc": "Requested porting date (days since epoch)"
      },
      {
        "name": "customer_consent",
        "type": "boolean",
        "doc": "Customer consent flag"
      },
      {
        "name": "priority",
        "type": {
          "type": "enum",
          "name": "PortingPriority",
          "symbols": ["LOW", "NORMAL", "HIGH", "EMERGENCY"]
        },
        "default": "NORMAL",
        "doc": "Request priority level"
      },
      {
        "name": "created_by",
        "type": ["null", "string"],
        "default": null,
        "doc": "User or system that created the request"
      },
      {
        "name": "metadata",
        "type": {
          "type": "map",
          "values": "string"
        },
        "default": {},
        "doc": "Additional context (source system, API version, etc.)"
      }
    ]
  },
  "kafka_config": {
    "partitions": 10,
    "compression_type": "snappy",
    "min_in_sync_replicas": 2
  },
  "consumers": [
    "prt-validation-service (validates request and updates status)",
    "notification-service (notifies carriers)",
    "audit-service (compliance logging)"
  ],
  "source": {
    "rnvs_trigger": "AFTER INSERT ON PORTIERUNGSANTRAEGE",
    "rnvs_file": "triggers/portierung_created_trigger.sql:23",
    "mapping_notes": "RNVS used database triggers for event propagation. VNRM uses application-level event publishing for better control and observability."
  },
  "business_context": "Portability request creation is the starting point for number porting workflow. Event enables asynchronous validation and carrier notifications without blocking API response."
}
```

---

## Subscriptions to Add

### Requirements

Every subscription in `subscriptions_to_add` MUST include:

1. **Topic Name**: Kafka topic being subscribed to
2. **Source Service**: Service that publishes the event
3. **Consumer Group**: Unique consumer group ID
4. **Description**: Why this service needs this event
5. **Idempotency Strategy**: How duplicate events are handled
6. **Error Handling**: Dead letter queue, retry policy
7. **Business Logic**: What the consumer does with the event

### Consumer Group Naming Convention

**Pattern**: `{consuming-service}.{topic-name}.{purpose}`

**Examples**:
- `prt-validation-service.prt.portability-request.created.validator`
- `notification-service.prt.portability-request.created.notifier`
- `audit-service.prt.portability-request.created.auditor`

### Template

```json
{
  "topic_name": "submodule.entity.event-type",
  "source_service": "publishing-service-name",
  "consumer_group": "consuming-service.topic.purpose",
  "description": "Why this service needs to consume this event",
  "idempotency_strategy": {
    "method": "event_id deduplication",
    "implementation": "Processing log table tracks processed event_ids"
  },
  "error_handling": {
    "retry_policy": "3 attempts with exponential backoff (1s, 2s, 4s)",
    "dead_letter_queue": "dlq.consuming-service.topic",
    "alert_threshold": "10 failures in 5 minutes"
  },
  "business_logic": "What happens when event is consumed"
}
```

### Complete Example: Validation Service Subscribes to Portability Request Created

```json
{
  "topic_name": "prt.portability-request.created",
  "source_service": "prt-portability-service",
  "consumer_group": "prt-validation-service.prt.portability-request.created.validator",
  "description": "Validation service consumes new portability requests to perform comprehensive validation: carrier eligibility, number ownership verification, business rule checks, and BNetzA compliance validation.",
  "processing_mode": "async",
  "concurrency": "10 parallel consumers",
  "idempotency_strategy": {
    "method": "event_id deduplication with processing log",
    "implementation": "Table: event_processing_log (event_id PK, processed_at, consumer_group). Check before processing.",
    "handling": "If event_id already processed, skip and acknowledge (no error)"
  },
  "error_handling": {
    "retry_policy": {
      "max_attempts": 3,
      "backoff": "exponential (1s, 2s, 4s)",
      "retryable_errors": ["NETWORK_ERROR", "TIMEOUT", "SERVICE_UNAVAILABLE"]
    },
    "dead_letter_queue": {
      "topic": "dlq.prt-validation-service.portability-request-created",
      "retention_days": 14,
      "alert_on_message": true
    },
    "non_retryable_errors": ["INVALID_SCHEMA", "CORRUPT_DATA"],
    "alert_threshold": "10 failures in 5 minutes trigger PagerDuty"
  },
  "business_logic": {
    "steps": [
      "1. Verify donor carrier exists and is active",
      "2. Verify recipient carrier exists and is active",
      "3. Check number ownership (donor carrier owns MSISDN)",
      "4. Validate desired port date (≥7 days in future, not on weekend/holiday)",
      "5. Check for existing active portability requests for MSISDN",
      "6. Validate business rules (BR-PORT-001 through BR-PORT-007)",
      "7. Check BNetzA compliance regulations",
      "8. Update portability request status to VALIDATED or FAILED",
      "9. Publish validation result event (prt.portability-request.validated or prt.portability-request.failed)"
    ],
    "average_processing_time": "500ms",
    "external_dependencies": ["carrier-registry-service", "number-registry-service", "bnetza-api"]
  },
  "event_processing_log_table": {
    "ddl": "CREATE TABLE event_processing_log (\n  event_id VARCHAR(36) PRIMARY KEY,\n  consumer_group VARCHAR(200) NOT NULL,\n  processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  processing_duration_ms INTEGER,\n  status VARCHAR(20) NOT NULL,\n  error_message TEXT\n);"
  },
  "monitoring": {
    "metrics": [
      "events_processed_total (counter)",
      "events_processing_duration_seconds (histogram)",
      "events_failed_total (counter by error_type)",
      "events_deduplicated_total (counter)"
    ],
    "dashboards": ["Kafka Consumer Health", "Portability Validation Pipeline"]
  },
  "source": {
    "rnvs_equivalent": "Database trigger calling validation stored procedure synchronously",
    "rnvs_file": "procedures/validate_portierung.sql:89",
    "improvement": "VNRM uses async event processing for better scalability and fault tolerance. RNVS synchronous approach caused timeouts under load."
  }
}
```

---

## Avro Schema Evolution Best Practices

### Forward Compatibility (Recommended)

**New consumers can read old data**

✅ **DO**: Add optional fields (with defaults)
✅ **DO**: Remove optional fields
❌ **DON'T**: Add required fields (breaks old producers)
❌ **DON'T**: Change field types

```json
{
  "name": "new_optional_field",
  "type": ["null", "string"],
  "default": null,
  "doc": "Added in version 1.1 - optional field"
}
```

### Backward Compatibility

**Old consumers can read new data**

✅ **DO**: Add required fields with defaults
✅ **DO**: Remove required fields (deprecated)
❌ **DON'T**: Rename fields
❌ **DON'T**: Change field types

### Full Compatibility (Safest)

**Both forward and backward compatible**

Only add optional fields with defaults, never remove.

---

## Idempotency Patterns

### Pattern 1: Event ID Deduplication (Recommended)

```sql
-- Check if event already processed
SELECT EXISTS(
  SELECT 1 FROM event_processing_log
  WHERE event_id = ? AND consumer_group = ?
);

-- If not exists, process and log
INSERT INTO event_processing_log (event_id, consumer_group, status)
VALUES (?, ?, 'SUCCESS');
```

### Pattern 2: Correlation ID + Entity Version

```sql
-- Check if entity already at this version
SELECT version FROM portability_requests WHERE id = ?;

-- Only process if event version > entity version
UPDATE portability_requests SET ...
WHERE id = ? AND version < ?;
```

### Pattern 3: Natural Idempotency

Design business logic to be naturally idempotent:
- `SET status = 'COMPLETED'` (idempotent - setting same value multiple times is safe)
- `UPDATE counter = counter + 1` (NOT idempotent - need event_id check)

---

## Error Handling Patterns

### Retry Strategy Decision Tree

```
Event Processing Failed
├─ Transient Error (network, timeout)?
│  ├─ YES → Retry with exponential backoff
│  └─ Retry count exceeded? → Send to DLQ
└─ Permanent Error (invalid data, schema mismatch)?
   └─ Send to DLQ immediately (no retry)
```

### Dead Letter Queue Processing

```json
{
  "dead_letter_queue": {
    "topic": "dlq.service-name.original-topic",
    "retention_days": 14,
    "monitoring": {
      "alert_on_any_message": true,
      "alert_threshold": "1 message triggers investigation"
    },
    "reprocessing": {
      "manual_replay": "After fixing root cause, replay from DLQ to original topic",
      "tool": "kafka-console-producer or custom replay script"
    }
  }
}
```

---

## Kafka Configuration Best Practices

### Topic Configuration

```json
{
  "partitions": 10,
  "replication_factor": 3,
  "min_in_sync_replicas": 2,
  "retention_ms": 2592000000,
  "compression_type": "snappy",
  "cleanup_policy": "delete"
}
```

**Partitions**: Based on throughput (10-50 for most VNRM topics)
**Replication**: 3 for production (fault tolerance)
**Min ISR**: 2 (ensures durability - at least 2 replicas acknowledge)
**Retention**: 30 days (2592000000 ms) for domain events
**Compression**: Snappy (good balance of speed and compression ratio)

### Producer Configuration

```json
{
  "acks": "all",
  "retries": 3,
  "max_in_flight_requests_per_connection": 1,
  "enable_idempotence": true,
  "compression_type": "snappy"
}
```

### Consumer Configuration

```json
{
  "enable_auto_commit": false,
  "auto_offset_reset": "earliest",
  "max_poll_records": 100,
  "session_timeout_ms": 30000
}
```

**Manual commit**: Only commit after successful processing (at-least-once delivery)

---

## Event Ordering Guarantees

### Same Partition = Guaranteed Order

**Partition by entity ID** to ensure ordering for same entity:

```json
{
  "partitioning_key": "request_id",
  "guarantee": "All events for same portability request go to same partition → ordered processing"
}
```

### Cross-Partition = No Order Guarantee

If events for same entity can go to different partitions, ordering is not guaranteed.

**Solution**: Use correlation_id + version fields for out-of-order handling:

```java
if (event.version > current.version) {
  apply(event);
} else {
  log.warn("Out of order event ignored: {} < {}", event.version, current.version);
}
```

---

## Monitoring and Observability

### Key Metrics

- **Consumer Lag**: How far behind consumer is from latest message
- **Processing Rate**: Messages/second
- **Error Rate**: Failed messages/total messages
- **Processing Duration**: Latency histogram

### Kafka Consumer Lag Alerting

```
Alert: Consumer lag > 1000 messages for > 5 minutes
Action: Scale up consumer instances or investigate slow processing
```

---

## Related Patterns

- See `api-delta-patterns.md` for APIs that publish events
- See `database-delta-patterns.md` for database changes triggered by events
- See `dependency-patterns.md` for event-driven service communication
- See `../examples/` for complete event flow examples

---

**Use these patterns to ensure reliable, scalable, maintainable event-driven architectures in your delta model.**
