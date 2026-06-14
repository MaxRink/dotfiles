# PlantUML Control Flow Patterns

Domain-specific PlantUML patterns for RNVS control flow diagrams.

---

## Technical Diagram Pattern (No Swimlanes)

```plantuml
@startuml control-flow-technical-auth
title Authentication - Technical Implementation Flow

start
:RnvsAuthManager.validateCredentials(username, password);

:Call pack_body_auth.check_password();
note right
  PL/SQL: SELECT password_hash FROM T_USER
  WHERE username = ?
end note

if (Password Hash Match?) then (yes)
  :LDAP_CLIENT.query(username);
  note right: LDAPS:636 external call

  if (LDAP Success?) then (yes)
    :RnvsAuthManager.createSession();
    :Call pack_body_session.create_token();
    :INSERT INTO T_SESSION (session_id, user_id, created_at);
    stop
  else (no)
    :Log LDAP Error;
    stop
  endif
else (no)
  :Increment failed_attempts IN T_USER;

  if (failed_attempts >= 5?) then (yes)
    :UPDATE T_USER SET locked_until = NOW() + 15min;
    :Log Security Event;
    stop
  else (no)
    stop
  endif
endif

@enduml
```

---

## Business Diagram Pattern (With Swimlanes)

```plantuml
@startuml control-flow-business-auth
title User Authentication - Business Process Flow

|Customer|
start
:Enter Username and Password;

|Authentication Services Team|
:Validate Credentials;
note right
  Rules: AUTH-BR-001, AUTH-BR-002
  Source: Phase 4 BP-AUTH-001 Step 1
end note

if (Credentials Valid?) then (yes)
  :Create Session Token;
  note right: AUTH-BR-010

  |Customer|
  :Display Dashboard;
  stop

else (no)
  :Increment Failed Attempt Counter;

  if (Failed Attempts >= 5?) then (yes)
    :Lock Account for 15 minutes;
    note right: AUTH-BR-001

    |IT Security Department|
    :Monitor Lockout Event;

    |Customer|
    :Display Account Locked Message;
    stop

  else (no)
    |Customer|
    :Display Invalid Credentials Error;
    stop
  endif
endif

@enduml
```

---

## Key PlantUML Elements

| Element | Syntax | Count as Node? |
|---------|--------|----------------|
| Start | `start` | Yes |
| Stop/End | `stop` | Yes |
| Activity | `:Activity Name;` | Yes |
| Decision | `if (Condition?) then (yes) ... else (no) ... endif` | Yes (1 per if) |
| Swimlane | `\|Stakeholder Name\|` | No |
| Note | `note right ... end note` | No |
| Parallel | `fork ... fork again ... end fork` | Yes (3 total) |

---

## Sub-Diagram Referencing

When a diagram exceeds 15 nodes, extract complex sub-processes:

```plantuml
' Main diagram
:User Login Request;

:Execute Authentication Workflow;
note right
  **See sub-diagram**: control-flow-diagram-auth-validation.puml
  Details: Credential validation, LDAP integration, error handling
  Nodes: 8 (under 15 limit)
end note

:Display Dashboard;
```

---

## Source Citation Annotations

Always cite Phase sources in notes:

```plantuml
:Validate Credentials;
note right
  Rules: AUTH-BR-001, AUTH-BR-002
  Source: Phase 4 BP-AUTH-001 Step 1
  Owner: Authentication Services Team
end note
```

For technical diagrams:

```plantuml
:pack_body_auth.check_password();
note right
  PL/SQL Procedure
  Database: SELECT FROM T_USER
  Source: Phase 1 dependency-graph.json
end note
```

---

## RNVS-Specific Patterns

### BNetzA Integration (KCODE Processing)

```plantuml
|BNetzA Gateway|
:Receive KCODE Message;

|RNVS RNB Team|
:Parse KCODE Header;

if (KCODE Type?) then (20-Assignment)
  :Process Number Block Assignment;
  note right: KCODE 20 - NBM-BR-001
else (2100-Modification)
  :Process Block Modification;
  note right: KCODE 2100 - NBM-BR-015
endif
```

### Porting Workflow (PDA)

```plantuml
|Carrier A (Abgebend)|
:Send PDA Portierungsanfrage;

|RNVS Porting System|
:Validate PDA Message Syntax;
note right: PDA-BR-001 - AT timing rules

if (Valid Syntax?) then (yes)
  :Check Number Ownership;
  if (Owner Matches?) then (yes)
    :Schedule Porting Date;
    |Carrier B (Aufnehmend)|
    :Confirm Porting Request;
    stop
  else (no)
    :Reject - Invalid Owner;
    stop
  endif
else (no)
  :Reject - Syntax Error;
  stop
endif
```
