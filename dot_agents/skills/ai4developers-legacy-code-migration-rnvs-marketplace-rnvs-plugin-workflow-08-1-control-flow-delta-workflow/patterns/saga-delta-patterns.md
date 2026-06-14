# Saga Choreography Delta Patterns

Patterns for adding saga choreography diagrams in Phase 8.1.

---

## When to Create Saga Diagrams

Create saga diagrams when Phase 7.1 introduces:
- **Distributed transactions** spanning 2+ services
- **Compensating actions** required on failure
- **Long-running operations** with rollback needs
- **Cross-service consistency** requirements

---

## Pattern 1: Orchestrated Saga

Central orchestrator manages saga steps:

```plantuml
@startuml
title Saga: Priority Porting with Number Allocation (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  Distributed transaction
  Source: Phase 7.1 changes
end note

participant "Saga Orchestrator" as ORCH #E1BEE7
participant "prt-fcpm" as FCPM #90CAF9
participant "num-fcm" as NUM #FFAB91
participant "spe-coms" as COMS #FFF59D

' Forward transaction
group Forward Phase
  ORCH -> FCPM : 1. createPorting(data)
  activate FCPM
  FCPM --> ORCH : porting_id
  deactivate FCPM

  ORCH -> NUM : 2. allocateNumber(porting_id)
  activate NUM
  NUM --> ORCH : allocation_id
  deactivate NUM

  ORCH -> COMS : 3. sendPDA(porting_id)
  activate COMS
  COMS --> ORCH : pda_sent
  deactivate COMS
end

' Compensation
note over ORCH #FFCCCC
  **Compensation on Failure:**
  3'. cancelPDA(porting_id)
  2'. releaseNumber(allocation_id)
  1'. cancelPorting(porting_id)
end note

@enduml
```

**When to Use**: Clear transaction steps with defined compensation

---

## Pattern 2: Choreographed Saga (Event-Driven)

Services react to events without central orchestrator:

```plantuml
@startuml
title Saga: Priority Porting Choreography (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  Event-driven saga
  Source: Phase 7.1 topics_to_add
end note

participant "prt-fcpm" as FCPM #90CAF9
participant "Message Bus" as MESSAGE_BUS #4CAF50
participant "num-fcm" as NUM #FFAB91
participant "spe-coms" as COMS #FFF59D

' Step 1: Porting created
FCPM ->> MESSAGE_BUS : prt.porting.created
MESSAGE_BUS ->> NUM : consume

' Step 2: Number allocated
NUM -> NUM : allocateNumber()
NUM ->> MESSAGE_BUS : num.number.allocated
MESSAGE_BUS ->> FCPM : consume
MESSAGE_BUS ->> COMS : consume

' Step 3: PDA sent
COMS -> COMS : sendPDA()
COMS ->> MESSAGE_BUS : prt.pda.sent

' Compensation events
note over MESSAGE_BUS #FFCCCC
  **Compensation Events:**
  - num.allocation.failed -> FCPM cancels porting
  - prt.pda.failed -> NUM releases number
end note

@enduml
```

**When to Use**: Loosely coupled services, event-driven architecture

---

## Pattern 3: Saga with Timeout

Saga with deadline handling:

```plantuml
@startuml
title Saga: Porting with Timeout (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  Timeout handling
  Source: Phase 7.1 scheduler_jobs
end note

participant "Saga Orchestrator" as ORCH #E1BEE7
participant "Timer Service" as TIMER #90CAF9
participant "prt-fcpm" as FCPM #90CAF9
participant "num-fcm" as NUM #FFAB91

' Start saga with timeout
ORCH -> TIMER : scheduleTimeout(saga_id, 30min)
activate TIMER

ORCH -> FCPM : createPorting()
FCPM --> ORCH : porting_id

ORCH -> NUM : allocateNumber()

alt Success within timeout
  NUM --> ORCH : allocation_id
  ORCH -> TIMER : cancelTimeout(saga_id)
  deactivate TIMER
else Timeout exceeded
  TIMER --> ORCH : TIMEOUT event
  note right of ORCH #FFCCCC
    **Timeout Compensation:**
    1. Cancel pending operations
    2. Mark saga as TIMED_OUT
    3. Notify administrators
  end note
  ORCH -> FCPM : cancelPorting()
end

@enduml
```

**When to Use**: Operations with SLA or deadline requirements

---

## Pattern 4: Saga with Retry

Saga with retry logic:

```plantuml
@startuml
title Saga: Porting with Retry (NEW in Phase 8.1)

note right #FFFF00
  **NEW in Phase 8.1**
  Retry logic
  Source: Phase 7.1 resilience_patterns
end note

participant "Saga Orchestrator" as ORCH #E1BEE7
participant "num-fcm" as NUM #FFAB91

ORCH -> NUM : allocateNumber()

loop Retry up to 3 times
  alt Success
    NUM --> ORCH : allocation_id
  else Transient failure (5xx)
    NUM --> ORCH : 503 Service Unavailable
    ORCH -> ORCH : exponentialBackoff()
    note right of ORCH
      Backoff: 1s, 2s, 4s
    end note
  else Permanent failure (4xx)
    NUM --> ORCH : 400 Bad Request
    note right of ORCH #FFCCCC
      No retry for client errors
      Proceed to compensation
    end note
  end
end

@enduml
```

**When to Use**: External service calls with retry requirements

---

## Saga Documentation Structure

For each saga, document:

### 1. Saga Overview

```markdown
## Saga: Priority Porting

**Purpose**: Ensure atomic operation across prt-fcpm and num-fcm

**Participants**:
- prt-fcpm: Creates porting record
- num-fcm: Allocates number
- spe-coms: Sends PDA

**Trigger**: POST /portings/priority

**Timeout**: 30 minutes
```

### 2. Forward Steps

```markdown
### Forward Steps

| Step | Service | Action | Success Output |
|------|---------|--------|----------------|
| 1 | prt-fcpm | createPorting() | porting_id |
| 2 | num-fcm | allocateNumber() | allocation_id |
| 3 | spe-coms | sendPDA() | pda_id |
```

### 3. Compensation Steps

```markdown
### Compensation Steps

| Step | Service | Compensation | Trigger |
|------|---------|--------------|---------|
| 3' | spe-coms | cancelPDA() | Step 3 failed |
| 2' | num-fcm | releaseNumber() | Step 2 or 3 failed |
| 1' | prt-fcpm | cancelPorting() | Any step failed |
```

### 4. Edge Cases

```markdown
### Edge Cases

1. **Timeout during step 2**:
   - Cancel allocated number if partially completed
   - Mark porting as TIMED_OUT

2. **Step 3 fails after retries**:
   - Release number allocation
   - Cancel porting
   - Notify administrator

3. **Duplicate saga detection**:
   - Use idempotency key
   - Return existing saga status
```

---

## JSON Structure for sagas_to_add

```json
{
  "diagram_name": "saga-priority-porting.puml",
  "saga_name": "Priority Porting Saga",
  "saga_type": "orchestrated",
  "steps": [
    {
      "order": 1,
      "service": "prt-fcpm",
      "action": "createPorting",
      "compensation": "cancelPorting"
    },
    {
      "order": 2,
      "service": "num-fcm",
      "action": "allocateNumber",
      "compensation": "releaseNumber"
    },
    {
      "order": 3,
      "service": "spe-coms",
      "action": "sendPDA",
      "compensation": "cancelPDA"
    }
  ],
  "timeout_minutes": 30,
  "compensation_required": true,
  "plantuml_content": "@startuml\n...\n@enduml",
  "rationale": "Distributed transaction across prt-fcpm and num-fcm",
  "source_change": "Phase 7.1 dependency_changes + database_changes"
}
```

---

## Best Practices

1. **Document compensation for every step**
2. **Use idempotency keys** for saga operations
3. **Include timeout handling** for long-running sagas
4. **Show both happy path and failure paths**
5. **Use retry for transient failures only**
6. **Annotate ALL saga elements** with yellow notes
