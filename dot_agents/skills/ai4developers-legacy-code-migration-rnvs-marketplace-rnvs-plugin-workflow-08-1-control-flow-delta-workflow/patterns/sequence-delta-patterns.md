# Sequence Diagram Delta Patterns

Patterns for modifying and adding sequence diagrams in Phase 8.1.

---

## Pattern 1: Add New Participant

When Phase 7.1 adds a new service dependency:

```plantuml
@startuml
title Sequence: Export Porting (Modified in Phase 8.1)

' Existing participants
participant "prt-fcpm" as FCPM #90CAF9
participant "spe-coms" as COMS #FFF59D

' NEW PARTICIPANT (Phase 8.1)
participant "num-fcm" as NUM #FFAB91

note right of NUM #FFFF00
  **NEW in Phase 8.1**
  Added number allocation
  Source: Phase 7.1 dependency_changes
end note

' Flow continues...
@enduml
```

**When to Use**: Phase 7.1 added `new_internal_dependencies` or API calls to new service

---

## Pattern 2: Add New Interaction

When Phase 7.1 adds a new API endpoint:

```plantuml
@startuml
' Existing flow
USER -> FCPM : POST /portings
FCPM -> DB : INSERT porting

' NEW INTERACTION (Phase 8.1)
note right of FCPM #FFFF00
  **Phase 8.1 Change**
  Number allocation added
  Source: Phase 7.1 endpoints_to_add
end note

FCPM -> NUM : POST /booking-orders
activate NUM
NUM --> FCPM : allocation_id
deactivate NUM

' Existing flow continues
FCPM -> COMS : Send PDA
@enduml
```

**When to Use**: Phase 7.1 added `endpoints_to_add` that requires new service call

---

## Pattern 3: Modify Existing Interaction

When Phase 7.1 changes request/response schema:

```plantuml
@startuml
' BEFORE (commented for reference)
' FCPM -> COMS : Send PDA {phone_number}

' AFTER (Phase 8.1 modified)
FCPM -> COMS : Send PDA {phone_number, allocation_id}

note right #FFFF00
  **Modified in Phase 8.1**
  Added allocation_id field
  Source: Phase 7.1 endpoints_to_modify
end note
@enduml
```

**When to Use**: Phase 7.1 added `endpoints_to_modify` with schema changes

---

## Pattern 4: Add Error Handling Branch

When Phase 7.1 adds validation or error handling:

```plantuml
@startuml
FCPM -> NUM : POST /booking-orders

alt Success
  NUM --> FCPM : 201 allocation_id
else Failure
  note right of NUM #FFFF00
    **NEW in Phase 8.1**
    Error handling added
    Source: Phase 7.1 error_responses
  end note
  NUM --> FCPM : 409 ALLOCATION_CONFLICT
  FCPM --> USER : 400 Bad Request
end
@enduml
```

**When to Use**: Phase 7.1 added error codes or validation rules

---

## Pattern 5: Add Async Notification

When Phase 7.1 adds Message Bus events:

```plantuml
@startuml
' Synchronous response
FCPM --> USER : 202 Accepted

' NEW ASYNC NOTIFICATION (Phase 8.1)
note right of FCPM #FFFF00
  **NEW in Phase 8.1**
  Async notification added
  Source: Phase 7.1 topics_to_add
end note

FCPM ->> MESSAGE_BUS : publish(prt.priority.requested)
MESSAGE_BUS ->> COMS : consume(prt.priority.requested)
activate COMS
COMS -> EXT : Send notification
deactivate COMS
@enduml
```

**When to Use**: Phase 7.1 added `topics_to_add` with event subscriptions

---

## Pattern 6: New Sequence Diagram

When Phase 7.1 adds a new use case:

```plantuml
@startuml
title Sequence: Priority Porting Request (NEW in Phase 8.1)

' Header note
note right #FFFF00
  **NEW DIAGRAM in Phase 8.1**
  Priority porting flow
  Source: Phase 7.1 endpoints_to_add
end note

' VNRM color scheme
participant "Client" as CLIENT #C8E6C9
participant "prt-fcpm" as FCPM #90CAF9
participant "num-fcm" as NUM #FFAB91
participant "spe-coms" as COMS #FFF59D
participant "Database" as DB #EEEEEE

' Main flow
CLIENT -> FCPM : POST /portings/priority
activate FCPM

' Validate
FCPM -> FCPM : validatePriorityRequest()

' Allocate number
FCPM -> NUM : POST /booking-orders
activate NUM
NUM --> FCPM : allocation_id
deactivate NUM

' Persist
FCPM -> DB : INSERT priority_porting
DB --> FCPM : porting_id

' Notify
FCPM -> COMS : POST /notifications/priority
activate COMS
COMS --> FCPM : 202 Accepted
deactivate COMS

' Publish event
FCPM ->> MESSAGE_BUS : publish(prt.priority.requested)

' Response
FCPM --> CLIENT : 201 Created {porting_id}
deactivate FCPM

' Legend
legend right
  |= Color |= Component |
  | #90CAF9 | PRT (Portability) |
  | #FFAB91 | NUM (Number Mgmt) |
  | #FFF59D | SPE (Special) |
endlegend
@enduml
```

**When to Use**: Phase 7.1 adds new endpoint that represents new use case

---

## VNRM Color Scheme

Use consistent colors for VNRM submodules:

| Submodule | Color | Hex |
|-----------|-------|-----|
| COM (Common) | Light Gray | #CFD8DC |
| COR (Correction) | Light Red | #FFCDD2 |
| NTW (Network) | Light Green | #C8E6C9 |
| NUM (Number) | Light Orange | #FFAB91 |
| PRT (Porting) | Light Blue | #90CAF9 |
| SPE (Special) | Light Yellow | #FFF59D |

---

## JSON Structure for sequences_to_add

```json
{
  "diagram_name": "sequence-priority-porting.puml",
  "use_case": "Priority Porting Request",
  "participants": ["prt-fcpm", "num-fcm", "spe-coms"],
  "description": "Complete flow for priority porting with number allocation",
  "plantuml_content": "@startuml\n...\n@enduml",
  "rationale": "Phase 7.1 added POST /portings/priority endpoint",
  "source_change": "Phase 7.1 endpoints_to_add[0]"
}
```

---

## JSON Structure for sequences_to_modify

```json
{
  "diagram_name": "sequence-export-porting.puml",
  "modifications": {
    "type": "add_interaction",
    "new_participants": ["num-fcm"],
    "new_interactions": [
      {
        "from": "prt-fcpm",
        "to": "num-fcm",
        "message": "POST /booking-orders",
        "response": "allocation_id",
        "insert_after": "INSERT porting"
      }
    ],
    "plantuml_snippet": "FCPM -> NUM : POST /booking-orders\nNUM --> FCPM : allocation_id",
    "rationale": "Add number allocation before PDA transmission"
  },
  "source_change": "Phase 7.1 endpoints_to_add[1]"
}
```

---

## Best Practices

1. **Always use activate/deactivate** for clear lifeline representation
2. **Include legend** for diagrams with 4+ participants
3. **Use alt/else** for branching flows
4. **Use ->>** for async messages (Message Bus)
5. **Use -->** for response messages
6. **Use ->** for request messages
7. **Annotate ALL changes** with yellow notes
