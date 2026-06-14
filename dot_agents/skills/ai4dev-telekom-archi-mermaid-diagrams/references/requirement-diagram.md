# Requirement Diagrams

SysML v1.6-style requirements traceability diagrams. Use to link requirements to elements and show how they relate.

## Diagram Declaration

```mermaid
requirementDiagram
```

Optionally specify direction:

```mermaid
requirementDiagram
%%{init: {"layout": "elk"}}%%
```

Valid directions: `TB` (default), `BT`, `LR`, `RL`.

## Requirement Types

| Type | Use |
|---|---|
| `requirement` | Generic requirement |
| `functionalRequirement` | Functional behavior |
| `interfaceRequirement` | Interface/API constraints |
| `performanceRequirement` | Performance constraints |
| `physicalRequirement` | Physical/hardware constraints |
| `designConstraint` | Design or implementation constraint |

## Requirement Syntax

```
<type> name {
    id: user_defined_id
    text: descriptive text
    risk: Low | Medium | High
    verifymethod: Analysis | Inspection | Test | Demonstration
}
```

## Element Syntax

Elements represent design artifacts that fulfill requirements.

```
element name {
    type: user_defined_type
    docref: user_defined_ref
}
```

## Relationship Types

| Keyword | Meaning |
|---|---|
| `contains` | Parent requirement contains child |
| `copies` | Requirement is copied from another |
| `derives` | Requirement is derived from another |
| `satisfies` | Element satisfies a requirement |
| `verifies` | Element verifies a requirement |
| `refines` | Requirement refines another |
| `traces` | Traceability link |

## Relationship Syntax

```
{source} - <type> -> {destination}
{destination} <- <type> - {source}
```

## Full Example

```mermaid
requirementDiagram

  requirement SystemAuth {
    id: REQ-001
    text: The system shall authenticate all users.
    risk: High
    verifymethod: Test
  }

  functionalRequirement OAuthLogin {
    id: REQ-002
    text: Users shall authenticate via OAuth2.
    risk: Medium
    verifymethod: Demonstration
  }

  performanceRequirement TokenExpiry {
    id: REQ-003
    text: Access tokens shall expire within 15 minutes.
    risk: Low
    verifymethod: Inspection
  }

  interfaceRequirement APIContract {
    id: REQ-004
    text: The API shall conform to OpenAPI 3.1.
    risk: Low
    verifymethod: Analysis
  }

  element AuthService {
    type: Microservice
    docref: docs/auth-service-spec.md
  }

  element TokenStore {
    type: Component
    docref: docs/token-store-spec.md
  }

  SystemAuth - contains -> OAuthLogin
  SystemAuth - contains -> TokenExpiry
  OAuthLogin - derives -> SystemAuth
  AuthService - satisfies -> OAuthLogin
  AuthService - satisfies -> TokenExpiry
  TokenStore - verifies -> TokenExpiry
  APIContract - traces -> OAuthLogin
```

## Styling

Apply styles with `classDef` and `:::` shorthand or inline `style`:

```mermaid
requirementDiagram

  classDef critical fill:#E20074,color:#fff,stroke:#a00052

  requirement CriticalReq {
    id: REQ-010
    text: Must not fail under load.
    risk: High
    verifymethod: Test
  }:::critical
```
