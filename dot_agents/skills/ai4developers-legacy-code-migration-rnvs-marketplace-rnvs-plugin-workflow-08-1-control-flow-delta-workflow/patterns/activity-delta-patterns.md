# Activity Diagram Delta Patterns

Patterns for modifying and adding activity diagrams in Phase 8.1.

**CRITICAL**: Do NOT use `==` separators in activity diagrams (PlantUML syntax issue).

---

## Pattern 1: New Validation Activity

When Phase 7.1 adds complex validation logic:

```plantuml
@startuml
title Activity: Priority Porting Validation (NEW in Phase 8.1)

start

note right #FFFF00
  **NEW in Phase 8.1**
  Priority validation logic
  Source: Phase 7.1 tables_to_add
end note

:Receive priority porting request;

partition "Validate Customer" {
  if (Is VIP customer?) then (yes)
    :Mark as expedited;
  else (no)
    :Standard processing;
  endif
}

partition "Validate Request" {
  :Check phone number format;

  if (Valid format?) then (yes)
    :Proceed;
  else (no)
    :Return FORMAT_ERROR;
    stop
  endif

  :Check carrier eligibility;

  if (Eligible carrier?) then (yes)
    :Proceed;
  else (no)
    :Return CARRIER_INELIGIBLE;
    stop
  endif
}

partition "Create Record" {
  :Insert priority_porting record;
  :Generate porting_id;
}

:Publish prt.priority.requested event;

stop

@enduml
```

**When to Use**: Phase 7.1 added database table with complex business rules

---

## Pattern 2: Add Decision Point

When Phase 7.1 adds new business rule:

```plantuml
@startuml
' Existing flow
:Process porting request;

' NEW DECISION (Phase 8.1)
note right #FFFF00
  **NEW in Phase 8.1**
  Priority check added
  Source: Phase 7.1 business_rules
end note

if (Is priority request?) then (yes)
  :Apply priority processing;
  :Allocate number immediately;
else (no)
  :Standard queue processing;
endif

:Continue processing;
@enduml
```

**When to Use**: Phase 7.1 added new business rule requiring branching logic

---

## Pattern 3: Add Parallel Processing

When Phase 7.1 enables concurrent operations:

```plantuml
@startuml
:Start processing;

' NEW PARALLEL (Phase 8.1)
note right #FFFF00
  **NEW in Phase 8.1**
  Parallel processing
  Source: Phase 7.1 async_operations
end note

fork
  :Validate with carrier A;
fork again
  :Validate with carrier B;
fork again
  :Check number availability;
end fork

:Aggregate results;

if (All validations passed?) then (yes)
  :Proceed with porting;
else (no)
  :Return aggregated errors;
  stop
endif

stop
@enduml
```

**When to Use**: Phase 7.1 added async/parallel operations

---

## Pattern 4: Add Error Handling

When Phase 7.1 adds error codes or exception handling:

```plantuml
@startuml
:Attempt number allocation;

' NEW ERROR HANDLING (Phase 8.1)
note right #FFFF00
  **NEW in Phase 8.1**
  Error handling
  Source: Phase 7.1 error_responses
end note

if (Allocation successful?) then (yes)
  :Store allocation_id;
  :Continue;
else (no)
  if (Retryable error?) then (yes)
    :Wait exponential backoff;
    :Retry allocation;
  else (no)
    :Log error;
    :Send alert;
    :Return ALLOCATION_FAILED;
    stop
  endif
endif
@enduml
```

**When to Use**: Phase 7.1 added error handling or retry logic

---

## Pattern 5: State Machine Activity

When Phase 7.1 adds state transitions:

```plantuml
@startuml
title Activity: Porting State Transitions (NEW in Phase 8.1)

start

note right #FFFF00
  **NEW in Phase 8.1**
  State machine logic
  Source: Phase 7.1 state_machine_changes
end note

:Initial state: CREATED;

while (Not terminal state?)
  switch (Current state)
    case (CREATED)
      :Validate request;
      :Transition to VALIDATED;
    case (VALIDATED)
      :Allocate number;
      :Transition to ALLOCATED;
    case (ALLOCATED)
      :Send PDA;
      :Transition to PDA_SENT;
    case (PDA_SENT)
      :Wait for confirmation;
      if (Confirmed?) then (yes)
        :Transition to COMPLETED;
      else (no)
        :Transition to FAILED;
      endif
  endswitch
endwhile

:Terminal state reached;

stop
@enduml
```

**When to Use**: Phase 7.1 added `new_states` or `new_transitions`

---

## Pattern 6: Timer/Deadline Activity

When Phase 7.1 adds deadline-based logic:

```plantuml
@startuml
:Start deadline monitoring;

' NEW TIMER (Phase 8.1)
note right #FFFF00
  **NEW in Phase 8.1**
  Deadline monitoring
  Source: Phase 7.1 scheduler_jobs
end note

repeat
  :Check current time;
  :Query pending portings past deadline;

  while (More portings?) is (yes)
    :Get next porting;
    :Send deadline notification;
    :Update status to DEADLINE_APPROACHING;
  endwhile (no)

  :Sleep 1 hour;

repeat while (Service running?)

stop
@enduml
```

**When to Use**: Phase 7.1 added scheduled jobs or deadline handling

---

## VNRM Partition Colors

Use partitions to group related activities:

```plantuml
partition "Validation" #E3F2FD {
  :Validate input;
}

partition "Processing" #E8F5E9 {
  :Process request;
}

partition "Persistence" #FFF3E0 {
  :Save to database;
}
```

| Partition | Color | Purpose |
|-----------|-------|---------|
| Validation | #E3F2FD | Input validation |
| Processing | #E8F5E9 | Business logic |
| Persistence | #FFF3E0 | Database operations |
| Notification | #FCE4EC | Outbound communication |
| Error | #FFEBEE | Error handling |

---

## JSON Structure for activities_to_add

```json
{
  "diagram_name": "activity-priority-validation.puml",
  "operation": "Priority Porting Validation",
  "table_name": "priority_porting_requests",
  "decision_points": [
    "Is VIP customer?",
    "Valid format?",
    "Eligible carrier?"
  ],
  "plantuml_content": "@startuml\n...\n@enduml",
  "rationale": "Phase 7.1 added complex validation for priority porting",
  "source_change": "Phase 7.1 tables_to_add: priority_porting_requests"
}
```

---

## Syntax Rules

| Do | Don't |
|----|-------|
| ✅ `start` / `stop` | ❌ `==` separators |
| ✅ `if () then` | ❌ `switch` without `case` |
| ✅ `partition "Name"` | ❌ Deeply nested conditions |
| ✅ `fork` / `end fork` | ❌ `|swimlane|` (limited support) |
| ✅ `repeat` / `repeat while` | ❌ Complex loops |
| ✅ `note right` | ❌ Notes inside conditions |

---

## Best Practices

1. **Use partitions** to group related activities
2. **Keep conditions simple** (max 2 levels nesting)
3. **Use parallel forks** for concurrent operations
4. **Include error branches** for all operations
5. **Annotate ALL new logic** with yellow notes
6. **Avoid swimlanes** (limited PlantUML support)
