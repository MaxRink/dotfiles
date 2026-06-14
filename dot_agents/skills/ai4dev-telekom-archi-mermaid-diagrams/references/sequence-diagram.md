# Sequence Diagrams

Perfect for showing service-to-service interactions, API call flows, authentication flows.

## Syntax

```mermaid
sequenceDiagram
  participant A as Service A
  participant B as Service B
  actor U as User

  U->>A: Request            %% Solid arrow
  A-->>U: Response           %% Dashed arrow
  A-xB: Async message        %% Cross arrow (lost)
  A-)B: Async open arrow

  Note over A,B: Shared note
  Note right of A: Side note

  rect rgb(200, 220, 255)
    A->>B: Within highlight
  end

  alt Condition
    A->>B: Path A
  else Other
    A->>B: Path B
  end

  loop Every 5 min
    A->>B: Heartbeat
  end

  par Parallel
    A->>B: Request 1
  and
    A->>C: Request 2
  end

  critical Establish connection
    A->>B: Connect
  option Connection timeout
    A->>A: Retry
  end

  break When error
    A-->>U: Error response
  end

  activate A
  deactivate A
```

## Activate/Deactivate — Two Syntaxes

1. **Explicit:** `activate X` / `deactivate X` as standalone lines
2. **Shorthand (preferred):** Append `+`/`-` to message arrows:
```
  A->>+B: Request    %% activates B
  B-->>-A: Response  %% deactivates B
```

## Activate/Deactivate Rules (critical — common source of syntax errors)

- Every `activate X` needs exactly one `deactivate X` — they must be balanced
- **Never deactivate inside both branches of `alt/else`** — this causes "inactivate an inactive participant" errors
- Instead, deactivate BEFORE the `alt` or AFTER the `end`:
- Activations can be stacked on the same participant (shows recursive/re-entrant calls)

```
  %% WRONG — RL deactivated in both branches = error in second branch:
  activate RL
  alt Condition
    RL-->>GW: A
    deactivate RL
  else
    RL-->>GW: B
    deactivate RL    %% ERROR: already inactive
  end

  %% CORRECT — deactivate before the branch:
  activate RL
  RL-->>GW: Response
  deactivate RL
  alt Condition
    GW-->>Client: Path A
  else
    GW-->>Client: Path B
  end
```

## Example — OAuth2 Flow

```mermaid
sequenceDiagram
  actor User
  participant App as Client App
  participant Auth as Auth Server
  participant API as Resource Server

  User->>App: Login request
  App->>Auth: Authorization request
  Auth->>User: Login page
  User->>Auth: Credentials
  Auth-->>App: Authorization code
  App->>Auth: Exchange code for token
  Auth-->>App: Access token + Refresh token

  rect rgb(200, 255, 200)
    Note over App,API: Authenticated requests
    App->>API: Request + Bearer token
    API->>Auth: Validate token
    Auth-->>API: Token valid
    API-->>App: Protected resource
  end
```
