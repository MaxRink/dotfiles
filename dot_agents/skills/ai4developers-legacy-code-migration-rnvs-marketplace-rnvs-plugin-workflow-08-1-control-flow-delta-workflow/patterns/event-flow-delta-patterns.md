# Event Flow Delta Patterns

Patterns for modifying event architecture diagrams in Phase 8.1.

---

## When to Modify Event Architecture

Modify event architecture when Phase 7.1 introduces:
- **New Message Bus topics**
- **New event subscriptions**
- **New event publishers**
- **Modified event schemas**

---

## Pattern 1: Add New Topic

When Phase 7.1 adds `topics_to_add`:

```plantuml
@startuml
title Event Architecture (Modified in Phase 8.1)

' Services
rectangle "prt-fcpm" as FCPM #90CAF9
rectangle "num-fcm" as NUM #FFAB91
rectangle "spe-coms" as COMS #FFF59D

' Existing topics
queue "prt.porting.created" as T1 #C8E6C9

' NEW TOPIC (Phase 8.1)
queue "prt.priority.requested" as T2 #FFFF00

note right of T2 #FFFF00
  **NEW in Phase 8.1**
  Priority porting events
  Source: Phase 7.1 topics_to_add
end note

' Publish relationships
FCPM --> T1 : publishes
FCPM --> T2 : publishes

' Subscribe relationships
T1 --> COMS : subscribes
T2 --> COMS : subscribes

@enduml
```

**When to Use**: Phase 7.1 added `topics_to_add` array

---

## Pattern 2: Add New Subscription

When Phase 7.1 adds `subscriptions_to_add`:

```plantuml
@startuml
title Event Subscriptions (Modified in Phase 8.1)

' Services
rectangle "prt-fcpm" as FCPM #90CAF9
rectangle "num-fcm" as NUM #FFAB91
rectangle "spe-coms" as COMS #FFF59D
rectangle "cor-fcm" as COR #FFCDD2

' Topics
queue "prt.porting.created" as T1 #C8E6C9
queue "prt.priority.requested" as T2 #FFFF00

' Existing subscriptions
T1 --> COMS : subscribes

' NEW SUBSCRIPTION (Phase 8.1)
note right of COR #FFFF00
  **NEW in Phase 8.1**
  Correction service subscription
  Source: Phase 7.1 subscriptions_to_add
end note

T1 --> COR : subscribes
T2 --> COR : subscribes

@enduml
```

**When to Use**: Phase 7.1 added `subscriptions_to_add` array

---

## Pattern 3: Event Flow Sequence

Show event processing flow:

```plantuml
@startuml
title Event Flow: Priority Porting (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  Priority event flow
  Source: Phase 7.1 event_changes
end note

participant "prt-fcpm" as FCPM #90CAF9
participant "Message Bus" as MESSAGE_BUS #4CAF50
participant "spe-coms" as COMS #FFF59D
participant "cor-fcm" as COR #FFCDD2

' Event 1
FCPM ->> MESSAGE_BUS : publish(prt.priority.requested)
note right
  **Event Schema:**
  - event_id: UUID
  - porting_id: UUID
  - priority_level: HIGH/MEDIUM
  - timestamp: ISO8601
end note

' Fan-out
MESSAGE_BUS ->> COMS : consume(prt.priority.requested)
MESSAGE_BUS ->> COR : consume(prt.priority.requested)

' Processing
activate COMS
COMS -> COMS : processPriorityNotification()
COMS ->> MESSAGE_BUS : publish(spe.notification.sent)
deactivate COMS

activate COR
COR -> COR : queuePriorityCorrection()
deactivate COR

@enduml
```

**When to Use**: Show event-driven business process

---

## Pattern 4: Event with Dead Letter Queue

Show error handling:

```plantuml
@startuml
title Event Error Handling (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  DLQ handling
  Source: Phase 7.1 event_error_handling
end note

participant "Message Bus" as MESSAGE_BUS #4CAF50
participant "spe-coms" as COMS #FFF59D
database "DLQ" as DLQ #FFCCCC
participant "Alert Service" as ALERT #FF5722

' Normal processing
MESSAGE_BUS ->> COMS : consume(prt.priority.requested)
activate COMS

alt Success
  COMS -> COMS : processEvent()
  COMS --> MESSAGE_BUS : commit offset
else Transient failure (retry 3x)
  COMS -> COMS : retry with backoff
  COMS --> MESSAGE_BUS : retry
else Permanent failure
  COMS ->> DLQ : send to dead letter queue
  DLQ ->> ALERT : trigger alert
  note right of DLQ #FFCCCC
    DLQ: prt.priority.requested.dlq
    Retention: 7 days
    Alert: PagerDuty
  end note
end

deactivate COMS

@enduml
```

**When to Use**: Phase 7.1 added error handling for events

---

## Pattern 5: Complete Event Architecture

Overview of all topics and subscriptions:

```plantuml
@startuml
title VNRM Event Architecture (Modified in Phase 8.1)

' Services
rectangle "prt-fcpm" as FCPM #90CAF9
rectangle "num-fcm" as NUM #FFAB91
rectangle "spe-coms" as COMS #FFF59D
rectangle "cor-fcm" as COR #FFCDD2
rectangle "ntw-inventory" as NTW #C8E6C9

' Existing Topics
package "Existing Topics" {
  queue "prt.porting.created" as T1 #C8E6C9
  queue "prt.porting.completed" as T2 #C8E6C9
  queue "num.number.allocated" as T3 #C8E6C9
}

' NEW Topics (Phase 8.1)
package "NEW Topics (Phase 8.1)" #FFFDE7 {
  queue "prt.priority.requested" as T4 #FFFF00
  queue "prt.number.allocated" as T5 #FFFF00

  note right of T4 #FFFF00
    **NEW in Phase 8.1**
    Priority events
  end note
}

' Publishing
FCPM --> T1 : publishes
FCPM --> T2 : publishes
FCPM --> T4 : publishes
NUM --> T3 : publishes
NUM --> T5 : publishes

' Subscribing
T1 --> COMS : subscribes
T1 --> COR : subscribes
T2 --> NTW : subscribes
T3 --> FCPM : subscribes
T4 --> COMS : subscribes
T4 --> COR : subscribes
T5 --> FCPM : subscribes
T5 --> COMS : subscribes

' Legend
legend right
  |= Color |= Meaning |
  | #C8E6C9 | Existing |
  | #FFFF00 | NEW (Phase 8.1) |
endlegend

@enduml
```

**When to Use**: Comprehensive event architecture view

---

## Event Schema Documentation

For each new topic, document:

```markdown
### Topic: prt.priority.requested

**Purpose**: Notify subscribers of priority porting request

**Publisher**: prt-fcpm

**Subscribers**:
- spe-coms: Send priority notification
- cor-fcm: Queue priority correction check

**Avro Schema**:
```json
{
  "type": "record",
  "name": "PriorityPortingRequested",
  "namespace": "com.telekom.vnrm.prt.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "event_timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "correlation_id", "type": "string"},
    {"name": "porting_id", "type": "string"},
    {"name": "priority_level", "type": {"type": "enum", "name": "PriorityLevel", "symbols": ["HIGH", "MEDIUM", "LOW"]}},
    {"name": "customer_id", "type": "string"},
    {"name": "phone_number", "type": "string"}
  ]
}
```

**Partitioning**: By `porting_id` (ensures ordering per porting)

**Retention**: 30 days

**Replication Factor**: 3
```

---

## JSON Structure for event_flows_to_modify

```json
{
  "diagram_name": "event-architecture.puml",
  "new_topics": [
    {
      "topic_name": "prt.priority.requested",
      "publisher": "prt-fcpm",
      "partition_key": "porting_id",
      "retention_days": 30,
      "replication_factor": 3
    }
  ],
  "new_subscriptions": [
    {
      "consumer": "spe-coms",
      "topic": "prt.priority.requested",
      "consumer_group": "spe-coms-priority-consumer",
      "idempotency": "event_id deduplication"
    },
    {
      "consumer": "cor-fcm",
      "topic": "prt.priority.requested",
      "consumer_group": "cor-fcm-priority-consumer",
      "idempotency": "event_id deduplication"
    }
  ],
  "plantuml_content": "@startuml\n...\n@enduml",
  "rationale": "Phase 7.1 added priority porting events",
  "source_change": "Phase 7.1 topics_to_add: prt.priority.requested"
}
```

---

## Topic Naming Convention

```
{submodule}.{entity}.{event-type}
```

| Component | Values |
|-----------|--------|
| submodule | prt, num, cor, ntw, spe, com |
| entity | porting, number, correction, etc. |
| event-type | created, updated, completed, failed, requested |

**Examples**:
- `prt.porting.created`
- `prt.priority.requested`
- `num.number.allocated`
- `cor.correction.completed`

---

## Best Practices

1. **Use consistent topic naming** following convention
2. **Include standard event fields** (event_id, timestamp, correlation_id)
3. **Document partitioning strategy** for ordering guarantees
4. **Specify idempotency strategy** for consumers
5. **Include DLQ configuration** for error handling
6. **Annotate ALL new topics/subscriptions** with yellow notes
