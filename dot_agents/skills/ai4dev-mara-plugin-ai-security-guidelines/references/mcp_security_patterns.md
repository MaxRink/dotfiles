# Model Context Protocol (MCP) Security Patterns

## Overview

The Model Context Protocol (MCP) enables dynamic, flexible interactions between AI models and various tools and data sources.
Unlike rigid APIs, MCP supports discovery-based interactions, making security more complex but also more critical.

## CRITICAL: TARDIS MCP Gateway Requirement

**Per the MARA Technology Blueprint, all MCP integrations at Deutsche Telekom MUST route through the TARDIS MCP Gateway.**

### TARDIS MCP Gateway

**Owner:** DHEI
**Status:** Production
**Requirement:** MANDATORY for all MCP integrations

**Capabilities:**

- Secure gateway for MCP connections
- Authentication and authorization enforcement
- Rate limiting and quota management
- Comprehensive audit logging
- Security policy enforcement

**Documentation:**

- MCP Gateway: <https://wiki.telekom.de/pages/viewpage.action?spaceKey=DHEI&title=MCP+Gateway+and+Orchestration+MVP>
- MCP Server Specification: <https://wiki.telekom.de/pages/viewpage.action?pageId=3691938421>

**Integration Requirement:**

```text
Agent → TARDIS MCP Gateway → MCP Server → External Service
```

No direct MCP server connections are permitted in production without TARDIS Gateway.

## MCP Architecture Security

### Key Components

1. **MCP Client** - AI model or agent consuming tools/data
2. **MCP Server** - Provider of tools, resources, and prompts
3. **MCP Gateway** - Security and policy enforcement layer
4. **Transport Layer** - Communication mechanism (stdio, SSE, WebSocket)

### Security Challenges

- Dynamic tool discovery increases attack surface
- Natural language interfaces complicate input validation
- Context passing can leak sensitive information
- Tool invocations may have unintended side effects
- No built-in authentication in base protocol

## MCP Gateway Security Patterns

The MCP Gateway (AI Gateway) is the critical security component for protecting MCP-based systems.

### Pattern 1: Centralized Authentication and Authorization

**Purpose:** Enforce consistent authentication and authorization across all MCP interactions.

**Implementation:**

```text
┌─────────────┐
│   Client    │
│ (AI Agent)  │
└──────┬──────┘
       │ 1. Request with user token
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  ┌─────────────────────────────┐   │
│  │ Authentication              │   │
│  │ - Verify user token         │   │
│  │ - Extract user subject      │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Authorization               │   │
│  │ - Check user permissions    │   │
│  │ - Validate tool access      │   │
│  │ - Apply context constraints │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │ 2. Authorized request with user context
       ↓
┌─────────────┐
│ MCP Server  │
│   (Tools)   │
└─────────────┘
```

**Requirements:**

- Gateway terminates user authentication
- Gateway performs token exchange for subject-bound credentials
- Gateway validates permissions before forwarding to MCP server
- Gateway propagates user subject to downstream services
- Gateway rejects non-subject-bound privilege attempts

**Benefits:**

- Single point of authentication enforcement
- Consistent authorization policies
- Centralized audit logging
- Subject-bound security across all tools

### Pattern 2: Prompt Security and Validation

**Purpose:** Prevent prompt injection and validate all natural language inputs.

**Implementation:**

```text
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ User prompt + tool request
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  ┌─────────────────────────────┐   │
│  │ Prompt Security Scanner     │   │
│  │ - Detect injection patterns │   │
│  │ - Validate input safety     │   │
│  │ - Check content policy      │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Input Sanitization          │   │
│  │ - Remove malicious content  │   │
│  │ - Apply allow/deny lists    │   │
│  │ - Enforce input constraints │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │ Validated prompt
       ↓
┌─────────────┐
│ MCP Server  │
└─────────────┘
```

**Detection Techniques:**

- Pattern matching for common injection attempts
- Separate validation LLM for semantic analysis
- Behavioral anomaly detection
- Context boundary verification

**Validation Rules:**

- Maximum prompt length limits
- Character encoding validation
- Forbidden keyword detection
- Structural integrity checks

### Pattern 3: Data Leakage Prevention (DLP)

**Purpose:** Prevent sensitive information disclosure in prompts and responses.

**Implementation:**

```text
┌─────────────┐         ┌─────────────┐
│   Client    │ ──────→ │ MCP Gateway │ ──────→ │ MCP Server  │
└─────────────┘   1     └──────┬──────┘    3    └─────────────┘
                                │
                         ┌──────┴──────┐
                         │  DLP Engine │
                         │  - Scan in  │
                         │  - Scan out │
                         │  - Redact   │
                         └─────────────┘
                                2

Flow:
1. Request passes through gateway
2. DLP scans for sensitive data (both directions)
3. Redacted request forwarded to server
4. Response scanned and redacted before returning to client
```

**Sensitive Data Types to Detect:**

- Personally Identifiable Information (PII)
  - Names, addresses, phone numbers
  - Social Security Numbers, national IDs
  - Email addresses, usernames
- Protected Health Information (PHI)
  - Medical record numbers
  - Health insurance IDs
  - Diagnosis codes
- Financial Data
  - Credit card numbers
  - Bank account numbers
  - Transaction details
- Credentials
  - API keys, tokens
  - Passwords, secrets
  - Private keys, certificates

**Redaction Strategies:**

- Token replacement: "John Doe" → "[NAME]"
- Partial masking: "1234-5678-9012-3456" → "****-****-****-3456"
- Hashing for analytics: preserve structure without exposing data
- Complete removal: delete sensitive content entirely

### Pattern 4: Tool Invocation Security

**Purpose:** Secure the execution of tools discovered and invoked via MCP.

**Implementation:**

```text
┌─────────────┐
│   Client    │ Requests tool execution
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  ┌─────────────────────────────┐   │
│  │ Tool Authorization          │   │
│  │ - Verify tool access        │   │
│  │ - Validate parameters       │   │
│  │ - Check rate limits         │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Execution Context           │   │
│  │ - Subject-bound execution   │   │
│  │ - Least privilege           │   │
│  │ - Resource constraints      │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │ Execute with user context
       ↓
┌─────────────┐
│ Tool Server │ Executes under user permissions
└─────────────┘
```

**Security Controls:**

- **Pre-Execution Validation:**
  - Verify user has permission to invoke tool
  - Validate all tool parameters
  - Check parameter values against constraints
  - Verify tool is in approved list
  - Confirm subject-bound credentials present

- **Execution Isolation:**
  - Execute in sandboxed environment
  - Apply resource limits (CPU, memory, time)
  - Restrict network access
  - Limit file system access
  - Run with minimum necessary privileges
  - Enforce user-scoped permissions

- **Post-Execution Validation:**
  - Validate tool output format
  - Scan output for sensitive data
  - Check for error conditions
  - Log execution results with user context
  - Update rate limit counters

### Pattern 5: Resource Access Control

**Purpose:** Control access to data sources and resources via MCP.

**Implementation:**

```text
┌─────────────┐
│   Client    │ Requests resource
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  ┌─────────────────────────────┐   │
│  │ Resource Policy Engine      │   │
│  │ - Check resource permissions│   │
│  │ - Apply data filters        │   │
│  │ - Enforce row-level security│   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │ Filtered resource request
       ↓
┌─────────────┐
│  Resource   │ Returns allowed data only
│   Server    │
└─────────────┘
```

**Access Control Mechanisms:**

- **Resource-Level Permissions:**
  - User can access specific resources
  - Role-based access control (RBAC)
  - Attribute-based access control (ABAC)

- **Data-Level Filtering:**
  - Row-level security (RLS)
  - Column-level masking
  - Query result filtering
  - Data classification enforcement

- **Context-Aware Authorization:**
  - Time-based access restrictions
  - Location-based access control
  - Purpose-based access (GDPR Article 6)
  - Data minimization principles

### Pattern 6: Secure Tool Discovery

**Purpose:** Prevent malicious tool injection and ensure only authorized tools are discoverable.

**Implementation:**

```text
┌─────────────┐
│   Client    │ Discovers available tools
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  │ Tool Registry               │   │
│  ┌─────────────────────────────┐   │
│  │ - Approved tools list       │   │
│  │ - Tool metadata validation  │   │
│  │ - Version control           │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Discovery Filter            │   │
│  │ - User-specific tools       │   │
│  │ - Permission-based filtering│   │
│  │ - Context-aware results     │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │ Filtered tool list
       ↓
┌─────────────┐
│   Client    │ Receives authorized tools only
└─────────────┘
```

**Security Requirements:**

- Maintain curated registry of approved tools
- Validate tool metadata and signatures
- Filter tools based on user permissions
- Version control and deprecation management
- Tool provenance verification
- Regular security audits of available tools

### Pattern 7: Context Injection Prevention

**Purpose:** Prevent attackers from injecting malicious context into MCP sessions.

**Implementation:**

```text
User Context: [TRUSTED]
─────────────────────────
System Instructions
User Authentication Data
Approved Tool Definitions
─────────────────────────

            ↓ Clear Separation ↓

User Input: [UNTRUSTED]
─────────────────────────
Natural Language Prompts
Tool Parameters
User-Provided Data
─────────────────────────
```

**Separation Techniques:**

- Use distinct markers for trusted vs. untrusted content
- Implement contextual boundaries in prompts
- Validate that untrusted input doesn't override trusted context
- Apply strict parsing rules for context boundaries
- Monitor for context boundary violations

### Pattern 8: Rate Limiting and Abuse Prevention

**Purpose:** Prevent abuse and ensure fair resource usage.

**Implementation:**

```text
┌─────────────┐
│   Client    │ Makes request
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│         MCP Gateway                 │
│  ┌─────────────────────────────┐   │
│  │ Rate Limiter                │   │
│  │ - Per-user limits           │   │
│  │ - Per-tool limits           │   │
│  │ - Global system limits      │   │
│  └─────────────────────────────┘   │
│           │ Within limits?          │
│           ↓                          │
│  ┌─────────────────────────────┐   │
│  │ Request Processing          │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
       │
       ↓
┌─────────────┐
│ MCP Server  │
└─────────────┘
```

**Rate Limiting Dimensions:**

- Requests per minute/hour per user
- Token consumption per user per day
- Concurrent requests per user
- Tool invocations per user per time window
- Data volume accessed per user per period

**Abuse Prevention:**

- Anomaly detection for unusual usage patterns
- Automatic throttling for suspicious behavior
- IP-based rate limiting as additional layer
- Cost-based limiting for expensive operations
- Graduated response (warn → throttle → block)

## Subject-Bound Authorization in MCP

### Core Principle

Every MCP operation must execute under the authenticated end-user's identity, not a generic service account.

### Implementation Pattern

```text
1. User authenticates to client application
   ↓
2. Client receives user token (JWT, OAuth)
   ↓
3. Client makes MCP request with user token
   ↓
4. MCP Gateway validates user token
   ↓
5. MCP Gateway exchanges for subject-bound credential (OBO token)
   ↓
6. MCP Gateway forwards request with OBO token
   ↓
7. MCP Server validates OBO token
   ↓
8. Tool executes with user permissions
   ↓
9. Response returned through chain
   ↓
10. All layers log with user subject
```

### Token Flow

```text
User Token (JWT)
├─ Validated by MCP Gateway
├─ Contains user claims: sub, email, roles
└─ Exchanged for OBO token

OBO Token (On-Behalf-Of)
├─ Contains original user subject
├─ Scoped to specific tool/resource
├─ Time-limited (short expiration)
└─ Verified at each service hop

Downstream Service
├─ Receives OBO token
├─ Validates user subject
├─ Enforces user permissions
└─ Logs with user context
```

### Prohibited Patterns

❌ **Generic Service Accounts:**

```text
Tool executes as "mcp-service-account" with admin privileges
→ REJECTED: No user accountability, excessive privilege
```

❌ **Credential Switching:**

```text
Agent receives user token but executes as admin
→ REJECTED: Breaks subject binding, enables privilege escalation
```

❌ **Token Dropping:**

```text
Agent uses user token initially but drops it downstream
→ REJECTED: Loss of user context, audit trail breaks
```

### Approved Pattern

✅ **Subject-Bound Execution:**

```text
1. User "alice@example.com" makes request
2. All tools execute as "alice@example.com"
3. Permissions checked against Alice's privileges
4. Audit logs record "alice@example.com" as actor
5. Data access filtered to Alice's allowed data
```

## Monitoring and Auditing

### Essential Audit Events

1. **Authentication Events**
   - User authentication success/failure
   - Token validation results
   - Subject extraction and propagation

2. **Authorization Events**
   - Permission checks and results
   - Tool access grants/denials
   - Resource access attempts
   - Subject-bound validation results

3. **Tool Invocation Events**
   - Tool discovery requests
   - Tool execution requests
   - Tool parameters (sanitized)
   - Execution results (summary)
   - User subject for all operations

4. **Security Events**
   - Prompt injection attempts
   - DLP policy violations
   - Rate limit breaches
   - Context boundary violations
   - Subject binding failures

5. **Data Access Events**
   - Resources requested
   - Data returned (metadata, not content)
   - Filtering applied
   - User subject for all accesses

### Monitoring Metrics

- Request rate per user
- Error rate per tool
- Authentication failure rate
- Authorization denial rate
- DLP detection rate
- Prompt injection attempt rate
- Average response time
- Token consumption per user
- Subject binding compliance rate

### Alerting Thresholds

- High authentication failure rate (>10/min per user)
- Repeated authorization failures (>5 in 10 min)
- DLP violations (any occurrence)
- Prompt injection detected (any occurrence)
- Unusual tool usage patterns
- Rate limit violations
- Subject binding violations (critical alert)

## Best Practices

1. **Always Use MCP Gateway**
   - Never allow direct client-to-server MCP connections
   - Gateway is the security enforcement point
   - All policies applied consistently at gateway

2. **Implement Defense in Depth**
   - Security at gateway AND at MCP servers
   - Multiple validation layers
   - Fail securely at each layer

3. **Apply Least Privilege**
   - Minimum permissions for each tool
   - Subject-bound execution for all operations
   - Time-limited credentials
   - Scope credentials to specific tools/resources

4. **Validate Everything**
   - Authenticate all requests
   - Authorize all operations
   - Validate all inputs
   - Sanitize all outputs

5. **Monitor Continuously**
   - Real-time security monitoring
   - Anomaly detection
   - Compliance validation
   - Subject propagation verification

6. **Log Comprehensively**
   - All security events
   - User context in all logs
   - Correlation IDs for tracing
   - Tamper-proof audit logs

7. **Test Regularly**
   - Penetration testing
   - Security scanning
   - Policy compliance audits
   - Subject binding validation

## Implementation Checklist

- [ ] Deploy MCP Gateway for all MCP traffic
- [ ] Implement subject-bound authentication and authorization
- [ ] Configure prompt security scanning
- [ ] Enable DLP for sensitive data detection
- [ ] Implement tool invocation security controls
- [ ] Configure resource access policies
- [ ] Secure tool discovery mechanism
- [ ] Prevent context injection attacks
- [ ] Implement rate limiting and abuse prevention
- [ ] Configure comprehensive audit logging
- [ ] Set up security monitoring and alerting
- [ ] Test all security controls
- [ ] Document security architecture
- [ ] Train team on MCP security patterns
- [ ] Establish incident response procedures

## References

- Model Context Protocol Specification
- MARA AI Gateway Architecture
- Zero Trust for AI Systems
- OAuth 2.0 On-Behalf-Of Flow (RFC 8693)
- OWASP API Security Top 10
