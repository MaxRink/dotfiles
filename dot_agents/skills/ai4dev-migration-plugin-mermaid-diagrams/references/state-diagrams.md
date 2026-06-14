# State Diagrams

State diagrams model state machines, lifecycle transitions, and workflow states. Use `stateDiagram-v2` for the modern syntax.

> **NEVER use literal `\n`** — use `<br>` for multi-line labels.

## Contents

- [Basic Syntax](#basic-syntax)
- [States](#states)
- [Transitions](#transitions)
- [Start and End](#start-and-end)
- [Composite States](#composite-states)
- [Fork and Join](#fork-and-join)
- [Choice](#choice)
- [Concurrency](#concurrency)
- [Notes](#notes)
- [Direction](#direction)
- [Complete Example: Order Lifecycle](#complete-example-order-lifecycle)
- [Authentication Flow](#authentication-flow)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Active
    Active --> Inactive : deactivate
    Inactive --> Active : activate
    Inactive --> [*]
```

## States

### Simple State

```mermaid
stateDiagram-v2
    stateId
```

### Named State

```mermaid
stateDiagram-v2
    state "Waiting for Input" as waiting
    [*] --> waiting
```

### State with Description

```mermaid
stateDiagram-v2
    Processing : Processing the request
```

## Transitions

```mermaid
stateDiagram-v2
    Idle --> Processing : start
    Processing --> Complete : finish
    Processing --> Failed : error
    Failed --> Idle : retry
```

## Start and End

```mermaid
stateDiagram-v2
    [*] --> First
    First --> Second
    Second --> [*]
```

- `[*]` at the start = initial state
- `[*]` at the end = final state

## Composite States

Nested states within a parent:

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Processing : request
        Processing --> Idle : done
    }

    Active --> Closed : close
    Closed --> [*]
```

### Deeply Nested

```mermaid
stateDiagram-v2
    state Application {
        state Running {
            state Foreground {
                [*] --> Visible
            }
            state Background {
                [*] --> Suspended
            }
        }
    }
```

## Fork and Join

Parallel execution paths:

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    state join_state <<join>>

    [*] --> fork_state
    fork_state --> TaskA
    fork_state --> TaskB
    fork_state --> TaskC

    TaskA --> join_state
    TaskB --> join_state
    TaskC --> join_state
    join_state --> Complete
    Complete --> [*]
```

## Choice

Conditional branching:

```mermaid
stateDiagram-v2
    state check <<choice>>

    [*] --> Validate
    Validate --> check
    check --> Approved : valid
    check --> Rejected : invalid
    Approved --> [*]
    Rejected --> [*]
```

## Concurrency

Parallel regions within a state (separated by `--`):

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Processing
        --
        [*] --> Monitoring
    }
```

## Notes

```mermaid
stateDiagram-v2
    State1 --> State2

    note right of State1
        Important information
        about this state
    end note

    note left of State2 : Short note
```

## Direction

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B
    B --> [*]
```

Directions: `TB` (default), `LR`, `RL`, `BT`

## Complete Example: Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft

    state "Order Processing" as processing {
        Draft --> Submitted : submit
        Submitted --> Validated : validate

        state check <<choice>>
        Validated --> check
        check --> Approved : passes rules
        check --> Rejected : fails rules

        Rejected --> Draft : revise
    }

    state "Fulfillment" as fulfillment {
        Approved --> Paid : payment received

        state fork_ship <<fork>>
        Paid --> fork_ship
        fork_ship --> Picking
        fork_ship --> Invoicing

        state join_ship <<join>>
        Picking --> Packed : pack
        Packed --> join_ship
        Invoicing --> join_ship

        join_ship --> Shipped : dispatch
    }

    Shipped --> Delivered : confirm delivery
    Delivered --> [*]

    Submitted --> Cancelled : cancel
    Approved --> Cancelled : cancel
    Cancelled --> [*]

    note right of Draft
        Customer can edit
        order details
    end note
```

## Authentication Flow

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Unauthenticated

    state Unauthenticated {
        [*] --> LoginForm
        LoginForm --> Validating : submit credentials
    }

    state check <<choice>>
    Validating --> check
    check --> Authenticated : valid
    check --> Unauthenticated : invalid

    state Authenticated {
        [*] --> Active
        Active --> Idle : timeout warning
        Idle --> Active : user activity
        Idle --> Expired : session timeout
    }

    Expired --> Unauthenticated : redirect to login
    Authenticated --> Unauthenticated : logout
```

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Use `[*]` for start/end** — Clearly mark entry and exit points
3. **Label transitions** — Describe the trigger/event for each transition
4. **Use composite states** — Group related states logically
5. **Use `<<choice>>`** — For conditional branching instead of multiple transitions
6. **Use `<<fork>>`/`<<join>>`** — For parallel execution paths
7. **Add notes** — Explain business rules or constraints
8. **Keep flat when possible** — Only nest when it adds clarity
9. **Show error/cancel paths** — Don't just model the happy path
