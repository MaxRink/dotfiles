# Flowcharts

Flowcharts visualize processes, algorithms, decision trees, and user journeys. They show step-by-step progression through a system or workflow.

## Contents

- [Basic Syntax](#basic-syntax)
- [Node Shapes](#node-shapes)
- [Connections](#connections)
- [Subgraphs](#subgraphs)
- [Styling](#styling)
- [Complete Example: User Registration Flow](#complete-example-user-registration-flow)
- [Algorithm Example: Binary Search](#algorithm-example-binary-search)
- [CI/CD Pipeline](#cicd-pipeline)
- [E-Commerce Checkout](#e-commerce-checkout)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
flowchart TD
    A --> B
```

**Directions:**

- `TD` or `TB` - Top to Bottom (default)
- `BT` - Bottom to Top
- `LR` - Left to Right
- `RL` - Right to Left

## Node Shapes

### Standard Shapes

```mermaid
flowchart LR
    A[Rectangle - Process]
    B([Rounded - Terminal])
    C((Circle))
    D{Diamond - Decision}
    E[(Database)]
    F[[Subroutine]]
    G[/Parallelogram - I/O/]
    H{{Hexagon}}
```

| Shape | Syntax | Use Case |
|-------|--------|----------|
| Rectangle | `[text]` | Process steps |
| Rounded | `([text])` | Start/End terminals |
| Diamond | `{text}` | Decisions |
| Circle | `((text))` | Connectors |
| Cylinder | `[(text)]` | Database |
| Subroutine | `[[text]]` | Predefined process |
| Parallelogram | `[/text/]` | Input/Output |
| Hexagon | `{{text}}` | Preparation |
| Asymmetric | `>text]` | Flags, signals |
| Double circle | `(((text)))` | End events |

### Extended Shapes (v11.3.0+)

```mermaid
flowchart LR
    A@{ shape: lean-r, label: "Lean Right" }
    B@{ shape: trap-b, label: "Trapezoid" }
    C@{ shape: dbl-circ, label: "Double Circle" }
    D@{ shape: doc, label: "Document" }
    E@{ shape: cyl, label: "Cylinder" }
```

Available extended shapes: `lean-l`, `lean-r`, `trap-t`, `trap-b`, `dbl-circ`, `doc`, `lin-doc`, `docs`, `cyl`, `h-cyl`, `lin-cyl`, `rect`, `lin-rect`, `div-rect`, `st-rect`, `bow-rect`

## Connections

### Basic Arrow

```mermaid
flowchart LR
    A --> B
```

### With Labels

```mermaid
flowchart LR
    A -->|Label| B
    C ---|No arrow| D
```

### Dotted Lines

```mermaid
flowchart LR
    A -.-> B
    C -.Label.-> D
```

### Thick Lines

```mermaid
flowchart LR
    A ==> B
    C ==Label==> D
```

### Invisible Links

```mermaid
flowchart LR
    A ~~~ B
```

Useful for layout control without visible connections.

### Special End Markers

```mermaid
flowchart LR
    A ---o B
    C ---x D
    E o--o F
    G x--x H
```

- `o` — circle end
- `x` — cross end

### Chaining

```mermaid
flowchart LR
    A --> B --> C --> D
    E --> F & G --> H
```

### Edge Animations (v11.0+)

```mermaid
flowchart LR
    A --> B
    e1@-->A-->B
    e1@{ animate: true }
```

## Subgraphs

```mermaid
flowchart TB
    A[Start]

    subgraph Processing
        B[Step 1]
        C[Step 2]
        D[Step 3]
    end

    E[End]

    A --> B
    D --> E
```

### Nested Subgraphs

```mermaid
flowchart TB
    subgraph Outer
        A[Node A]
        subgraph Inner
            B[Node B]
            C[Node C]
        end
    end
```

### Subgraph Direction

```mermaid
flowchart LR
    subgraph one
        direction TB
        A1 --> A2
    end

    subgraph two
        direction TB
        B1 --> B2
    end

    one --> two
```

## Styling

### Individual Nodes

```mermaid
flowchart LR
    A[Normal]
    B[Styled]

    style B fill:#ff6b6b,stroke:#333,stroke-width:4px,color:#fff
```

### Class-based

```mermaid
flowchart LR
    A[Success]:::success
    B[Warning]:::warning
    C[Error]:::error

    classDef success fill:#00b894,stroke:#00a383,color:#fff
    classDef warning fill:#fdcb6e,stroke:#e8b923,color:#333
    classDef error fill:#ff6b6b,stroke:#ee5253,color:#fff
```

### Link Styling

```mermaid
flowchart LR
    A --> B --> C

    linkStyle 0 stroke:#ff3,stroke-width:4px
    linkStyle 1 stroke:#0ff,stroke-width:2px
```

## Complete Example: User Registration Flow

```mermaid
flowchart TD
    Start([User visits registration]) --> Form[Show registration form]
    Form --> Input[User enters details]
    Input --> Validate{Valid input?}

    Validate -->|No| ShowError[Show validation errors]
    ShowError --> Form

    Validate -->|Yes| CheckEmail{Email exists?}

    CheckEmail -->|Yes| EmailError[Show 'Email registered']
    EmailError --> Form

    CheckEmail -->|No| CreateAccount[Create user account]
    CreateAccount --> Hash[Hash password]
    Hash --> SaveDB[(Save to database)]
    SaveDB --> GenerateToken[Generate verification token]
    GenerateToken --> SendEmail[Send verification email]
    SendEmail --> ShowSuccess[Show success message]
    ShowSuccess --> End([Redirect to login])

    style Start fill:#90EE90,stroke:#333
    style End fill:#90EE90,stroke:#333
    style SaveDB fill:#FFD700,stroke:#333
```

## Algorithm Example: Binary Search

```mermaid
flowchart TD
    Start([Start]) --> Init[low = 0, high = length - 1]
    Init --> Check{low <= high?}

    Check -->|No| NotFound[Return -1]
    NotFound --> End([End])

    Check -->|Yes| CalcMid[mid = low + high / 2]
    CalcMid --> Compare{"arr#91;mid#93; == target?"}

    Compare -->|Yes| Found[Return mid]
    Found --> End

    Compare -->|No| CheckLess{"arr#91;mid#93; < target?"}

    CheckLess -->|Yes| MoveLow[low = mid + 1]
    MoveLow --> Check

    CheckLess -->|No| MoveHigh[high = mid - 1]
    MoveHigh --> Check

    style Found fill:#FFD700
    style NotFound fill:#FF6B6B
```

## CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Development
        Commit[Commit code] --> Push[Push to repo]
    end

    subgraph CI
        Push --> Trigger[Trigger pipeline]
        Trigger --> Checkout[Checkout]
        Checkout --> Install[Install deps]
        Install --> Lint[Run linters]
        Lint --> Test[Run tests]
        Test --> Build[Build app]
    end

    subgraph QA
        Build --> DeployStaging[Deploy staging]
        DeployStaging --> E2E[E2E tests]
        E2E --> ManualQA{QA approval?}
    end

    subgraph Production
        ManualQA -->|Approved| DeployProd[Deploy prod]
        DeployProd --> HealthCheck{Health OK?}
        HealthCheck -->|Yes| Success([Done])
        HealthCheck -->|No| Rollback[Rollback]
    end

    ManualQA -->|Rejected| FixIssues[Fix issues]
    FixIssues --> Development
    Test -->|Failed| NotifyDev[Notify dev]
    NotifyDev --> FixIssues
```

## E-Commerce Checkout

```mermaid
flowchart TD
    Start([Checkout]) --> Auth{Authenticated?}

    Auth -->|No| Login[Redirect to login]
    Login --> Auth

    Auth -->|Yes| Cart{Cart empty?}
    Cart -->|Yes| EmptyCart[Show empty message]
    EmptyCart --> Browse[Browse products]

    Cart -->|No| Address[Shipping address]
    Address --> ValidateAddr{Valid?}
    ValidateAddr -->|No| Address
    ValidateAddr -->|Yes| Shipping[Select shipping]

    Shipping --> Payment[Payment details]
    Payment --> ValidatePay{Valid?}
    ValidatePay -->|No| Payment

    ValidatePay -->|Yes| Review[Order review]
    Review --> Confirm{Confirm?}

    Confirm -->|No| Edit{Edit what?}
    Edit -->|Address| Address
    Edit -->|Shipping| Shipping
    Edit -->|Payment| Payment

    Confirm -->|Yes| ProcessPay[Process payment]
    ProcessPay --> PayResult{Success?}

    PayResult -->|No| PayError[Payment error]
    PayError --> RetryPay{Retry?}
    RetryPay -->|Yes| Payment
    RetryPay -->|No| Cancel([Cancelled])

    PayResult -->|Yes| CreateOrder[(Create order)]
    CreateOrder --> ReduceStock[Update inventory]
    ReduceStock --> SendConfirm[Send confirmation]
    SendConfirm --> Success([Order complete])

    style Success fill:#90EE90
    style Cancel fill:#FF6B6B
```

## Common Patterns

### Linear Flow

```mermaid
flowchart LR
    A[Step 1] --> B[Step 2] --> C[Step 3]
```

### Branching Decision

```mermaid
flowchart TD
    A[Input] --> B{Condition?}
    B -->|Yes| C[Path 1]
    B -->|No| D[Path 2]
    C --> E[Merge]
    D --> E
```

### Loop

```mermaid
flowchart TD
    A[Initialize] --> B[Process]
    B --> C{Continue?}
    C -->|Yes| B
    C -->|No| D[Exit]
```

### Error Handling

```mermaid
flowchart TD
    A[Try] --> B{Success?}
    B -->|Yes| C[Continue]
    B -->|No| D[Handle error]
    D --> E{Retry?}
    E -->|Yes| A
    E -->|No| F[Abort]
```

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Use meaningful labels** — Action-oriented node text
3. **Consistent shapes** — Same shapes for same action types
4. **Diamonds for decisions** — Standard yes/no convention
5. **Natural flow direction** — Top-to-bottom or left-to-right
6. **Mark terminals** — Stadium shapes for start/end
7. **Group related steps** — Use subgraphs logically
8. **Color code** — Highlight different action types
9. **Minimize crossing lines** — Reorganize for clarity
10. **Keep focused** — One process per diagram
