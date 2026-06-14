# Activity Diagram Patterns

## Critical PlantUML Syntax Rules

### PROHIBITED Syntax in Activity Diagrams

**DO NOT use the following in activity diagrams - they cause syntax errors:**

```plantuml
== Section Name ==          ❌ INVALID - Sequence diagram syntax only!
```

### VALID Alternatives for Section Separators

```plantuml
floating note: **Section Name**                    ✅ VALID
note right: **Section Name**                        ✅ VALID
partition "Section Name" { ... }                    ✅ VALID
|Swimlane Name|                                     ✅ VALID
' Comment: Section Name                             ✅ VALID (not rendered)
```

**Recommended approach**: Use `floating note: **Section Name**` for visual separators.

---

## Standard Activity Diagram Template

```plantuml
@startuml
!pragma layout smetana
!theme plain
title [Service Name] - [Operation Name] Activity Flow

|Service Layer|
start
:Receive API Request\nPOST /api/v1/[endpoint];

|Validation Layer|
floating note: **Input Validation**

:Validate Request Schema;
if (Schema Valid?) then (yes)
  :Extract Request Parameters;
else (no)
  |Service Layer|
  :Return 400 Bad Request\n{error_code: INVALID_SCHEMA};
  stop
endif

|Business Logic Layer|
floating note: **Business Rule Validation**

:Check BR-017: Porting Date RUZ Tolerance;

note right
  **BR-017 Validation**:
  - portingDate >= now()
  - portingDate <= now() + 2 months
  - Regulatory requirement (RUZ)
end note

if (portingDate >= now() AND\nportingDate <= now() + 2 months?) then (yes)
  :✓ BR-017 Passed;
else (no)
  |Service Layer|
  :Return 400 Bad Request\n{error_code: PORT_DATE_RUZ_VIOLATION};
  stop
endif

:Check BR-018: Business Day Validation;

if (portingDate is business day?) then (yes)
  :✓ BR-018 Passed;
else (no)
  |Service Layer|
  :Return 400 Bad Request\n{error_code: INVALID_BUSINESS_DAY};
  stop
endif

:All Business Rules Passed;

|Database Layer|
floating note: **Database Transaction**

:BEGIN TRANSACTION;
note right
  **Isolation Level**: READ_COMMITTED
  **Timeout**: 30 seconds
  **Optimistic Locking**: version column
end note

:INSERT INTO porting_operations\nSET status='PENDING', version=0;

:INSERT INTO porting_history\nSET event_type='CREATED';

if (All Inserts Successful?) then (yes)
  :COMMIT TRANSACTION;
else (no)
  :ROLLBACK TRANSACTION;
  |Service Layer|
  :Return 500 Internal Error;
  stop
endif

|Service Layer|
:Return 201 Created\n{porting_id, status};
stop

@enduml
```

---

## Parallel Processing Pattern

```plantuml
|Processing Layer|
fork
  :Process Porting Request\nUpdate Database;
fork again
  :Publish Kafka Event\nprt.porting.created;
fork again
  :Update Audit Trail\nporting_history table;
end fork

:Synchronize Results;
```

---

## Saga Compensation Pattern

```plantuml
partition "Saga Step: Allocate Number Block" {
  |num-fcm Service|
  :POST /booking-orders;

  if (Allocation Successful?) then (yes)
    :Store allocation_id;
    :Continue to Next Saga Step;
  else (no)
    partition "Compensation" {
      :Trigger Saga Rollback;
      |prt-fcpm Service|
      :Update porting_operations\nSET status='FAILED';
      :Publish prt.porting.failed event;
      |Service Layer|
      :Return 500 Number Allocation Failed;
      stop
    }
  endif
}
```

---

## Error Handling Pattern

```plantuml
|Integration Layer|
:Call External Carrier API\nPDA Transmission;

if (API Call Successful?) then (yes)
  :Continue;
else (no)
  partition "Error Handling" {
    :Log Error to problem_messages table;

    if (Retryable Error?) then (yes)
      :Schedule Retry\nExponential Backoff;
      note right
        **Retry Policy**:
        - Attempt 1: 100ms delay
        - Attempt 2: 500ms delay
        - Attempt 3: 2s delay
        - Max attempts: 3
      end note
      :Retry API Call;
    else (no)
      :Move to Dead Letter Queue;
      :Publish prt.porting.failed event;
      |Service Layer|
      :Return 500 External Integration Failed;
      stop
    endif
  }
endif
```

---

## Validation Checklist

Before generating activity diagrams, verify:

- [ ] No `== Section ==` syntax used
- [ ] Section separators use `floating note:` or `partition { }`
- [ ] Swimlanes properly declared with `|Name|`
- [ ] Business rules annotated with rule IDs
- [ ] Database operations show transaction boundaries
- [ ] Error paths end with `stop`
- [ ] All branches properly closed with `endif`
