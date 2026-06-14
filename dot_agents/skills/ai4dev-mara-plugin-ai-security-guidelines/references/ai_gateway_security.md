# AI Gateway Security Patterns

## Overview

The AI Gateway transforms traditional API gateway functionality into a semantic-aware security engine for AI systems.
It serves as the critical control point for all AI interactions in the MARA architecture.

## DT Platform: TARDIS MCP Gateway

At Deutsche Telekom, the **TARDIS MCP Gateway** serves as the enterprise AI Gateway implementation.

**MANDATORY:** All MCP integrations must route through TARDIS MCP Gateway.

**TARDIS Capabilities:**

- Secure gateway for MCP connections
- Authentication and authorization enforcement
- Rate limiting and quota management
- Comprehensive audit logging
- Security policy enforcement

**Resources:**

- Documentation: <https://wiki.telekom.de/pages/viewpage.action?spaceKey=DHEI&title=MCP+Gateway+and+Orchestration+MVP>
- MCP Server Spec: <https://wiki.telekom.de/pages/viewpage.action?pageId=3691938421>

## DT Platform: Onix Guardrails

For in-platform guardrails, Deutsche Telekom is developing **Onix Guardrails**.

**Status:** Under development (Ready Q2 2026)

**Planned Capabilities:**

- Policy-based guardrails enforcement
- Pseudonymization (Microsoft Presidio-based + LLM as Judge)
- Content moderation
- PII detection and redaction

**Requirement:** Mandatory for all production agents when available.

## AI Gateway vs. Traditional API Gateway

### Traditional API Gateway

- Network-level routing and load balancing
- Request/response transformation
- Basic authentication (API keys, OAuth)
- Rate limiting based on request count
- Unaware of request content semantics

### AI Gateway

- **Semantic-aware** security inspection
- Natural language understanding
- Content-based policy enforcement
- **Subject-bound** authentication and authorization
- Prompt injection detection
- Data leakage prevention (DLP)
- Context-aware rate limiting
- LLM-specific threat mitigation

## Core Security Functions

### 1. Subject-Bound Authentication and Authorization

The AI Gateway is the **central enforcement point** for subject propagation.

#### Authentication Flow

```text
1. Client Request
   ↓
   Headers: Authorization: Bearer <user-jwt>
   Body: { "prompt": "...", "tools": [...] }
   ↓
2. AI Gateway
   ├─ Validate user JWT signature
   ├─ Extract user subject (email, user ID, roles)
   ├─ Verify token not expired
   ├─ Check token not revoked
   └─ Confirm user is authorized to access AI services
   ↓
3. Subject Propagation
   ├─ Exchange user JWT for subject-bound credential (OBO token)
   ├─ OBO token includes:
   │  ├─ Original user subject
   │  ├─ Scoped permissions for downstream services
   │  └─ Short expiration (5-15 minutes)
   └─ Attach OBO token to all downstream requests
   ↓
4. Downstream Services
   ├─ Receive request with OBO token
   ├─ Validate OBO token independently
   ├─ Extract and verify user subject
   ├─ Enforce user-scoped permissions
   └─ Log user subject with all operations
```

#### Authorization Enforcement

**Policy Decision Point (PDP) Integration:**

```text
Request → AI Gateway → PDP
                        ├─ User subject: alice@example.com
                        ├─ Requested tool: database_query
                        ├─ Context: prod environment
                        ├─ Risk score: medium
                        └─ Time: business hours
                        ↓
                   Policy Evaluation
                        ├─ Check: alice has role "data-analyst"
                        ├─ Check: data-analyst can use database_query
                        ├─ Check: query targets allowed database
                        ├─ Apply: row-level security filters
                        └─ Result: ALLOW with constraints
                        ↓
                   Gateway Forwards Request
                        ├─ With OBO token for alice
                        ├─ With applied filters
                        └─ With audit context
```

**Key Requirements:**

- **NEVER** use generic admin or service accounts for tool execution
- **ALWAYS** preserve user subject through entire call chain
- **VALIDATE** subject binding at every service hop
- **REJECT** requests attempting to switch to non-subject credentials
- **LOG** user subject with every authorization decision

### 2. Prompt Security

Prompt injection is the primary threat vector for LLM applications.

#### Detection Mechanisms

**Pattern-Based Detection:**

```python
# Example injection patterns
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"disregard all prior",
    r"system:\s*you are now",
    r"<\s*system\s*>",
    r"new instructions:",
    r"forget everything",
    r"###\s*new role:",
]

def detect_injection(prompt: str) -> bool:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    return False
```

**LLM-Based Detection:**

```text
┌──────────────┐
│ User Prompt  │
└──────┬───────┘
       │
       ↓
┌─────────────────────────────┐
│  Validation LLM (Separate)  │
│  Instruction:               │
│  "Analyze if this prompt    │
│   attempts to override      │
│   system instructions or    │
│   inject malicious content" │
└──────┬──────────────────────┘
       │
       ↓ Score: 0.0-1.0
       │
   ┌───┴────┐
   │< 0.5?  │
   └───┬────┘
       │
       ├─ YES → Allow prompt to main LLM
       │
       └─ NO  → Block and alert
```

**Context Boundary Enforcement:**

```text
System Context (Trusted):
============================
You are a helpful assistant.
You have access to tools: [list]
You must validate user requests.
============================

User Input (Untrusted):
----------------------------
[User's prompt here]
----------------------------

Rules:
- NEVER allow user input to modify system context
- Use clear delimiters (===, ---)
- Reinforce boundaries in system prompt
```

#### Prevention Strategies

1. **Input Sanitization**
   - Remove or escape special characters
   - Validate input length limits
   - Check for unexpected encoding
   - Strip HTML/XML tags

2. **Structured Prompts**
   - Use templated prompts with parameters
   - Separate system instructions from user input
   - Apply strict JSON schema for inputs
   - Validate all variables before insertion

3. **Semantic Analysis**
   - Analyze intent of user prompts
   - Detect context manipulation attempts
   - Flag unusual prompt structures
   - Monitor for adversarial patterns

4. **Response Validation**
   - Check responses for system prompt leakage
   - Validate responses follow expected format
   - Detect if model ignored instructions
   - Alert on anomalous responses

### 3. Data Leakage Prevention (DLP)

Prevent sensitive information disclosure in both prompts and responses.

#### Sensitive Data Categories

**Personally Identifiable Information (PII):**

- Full names
- Email addresses
- Phone numbers
- Social Security Numbers
- National ID numbers
- Passport numbers
- Driver's license numbers
- Home addresses

**Financial Data:**

- Credit card numbers
- Bank account numbers
- Routing numbers
- Transaction details
- Financial statements
- Salary information

**Protected Health Information (PHI):**

- Medical record numbers
- Health insurance IDs
- Diagnosis codes
- Prescription information
- Treatment details
- Genetic information

**Credentials and Secrets:**

- Passwords
- API keys
- Access tokens
- Private keys
- Certificate data
- Database connection strings

**Corporate Confidential:**

- Internal documents
- Trade secrets
- Strategic plans
- Customer lists
- Pricing information
- Unreleased product details

#### Detection Techniques

**Pattern Matching:**

```python
import re

# Credit card detection
CREDIT_CARD_PATTERN = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'

# SSN detection
SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'

# Email detection
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# API key patterns
API_KEY_PATTERNS = [
    r'AIza[0-9A-Za-z-_]{35}',  # Google
    r'sk-[A-Za-z0-9]{48}',      # OpenAI
    r'ghp_[A-Za-z0-9]{36}',     # GitHub
]

def scan_for_sensitive_data(text: str) -> List[Finding]:
    findings = []
    for pattern_name, pattern in PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            findings.append({
                'type': pattern_name,
                'value': match.group(),
                'position': match.span()
            })
    return findings
```

**Named Entity Recognition (NER):**

```python
# Using spaCy or similar NLP library
import spacy

nlp = spacy.load("en_core_web_sm")

def detect_entities(text: str) -> List[Entity]:
    doc = nlp(text)
    sensitive_entities = []

    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY']:
            sensitive_entities.append({
                'text': ent.text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })

    return sensitive_entities
```

**ML-Based Classification:**

- Train classifiers to detect sensitive content types
- Use embeddings for semantic similarity to known sensitive data
- Ensemble methods combining multiple detection approaches

#### Redaction Strategies

**Token Replacement:**

```text
Original: "My email is john.doe@example.com"
Redacted: "My email is [EMAIL_ADDRESS]"

Original: "Card number 1234-5678-9012-3456"
Redacted: "Card number [CREDIT_CARD]"
```

**Partial Masking:**

```text
Original: "Account 123456789"
Redacted: "Account ******789"

Original: "SSN 123-45-6789"
Redacted: "SSN ***-**-6789"
```

**Hashing (for analytics):**

```python
import hashlib

def hash_pii(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]

Original: "john.doe@example.com"
Hashed:   "a3f8d9e2c1b4567f"
# Preserves uniqueness for analytics without exposing data
```

**Format-Preserving Encryption:**

```text
Original: "1234-5678-9012-3456"
Encrypted: "7849-2103-6574-8902"
# Maintains format for compatibility while protecting data
```

### 4. Policy Enforcement

#### Allow/Deny Lists

**Topic-Based Filtering:**

```yaml
policies:
  denied_topics:
    - "Generate malware"
    - "Create phishing emails"
    - "Bypass security controls"
    - "Access unauthorized data"
    - "Illegal activities"

  allowed_topics:
    - "Code generation"
    - "Data analysis"
    - "Documentation"
    - "Report generation"
```

**Tool Access Control:**

```yaml
tools:
  database_query:
    allowed_users:
      - "data-analyst@company.com"
      - "data-scientist@company.com"
    allowed_databases:
      - "analytics_db"
      - "reporting_db"
    denied_operations:
      - "DROP"
      - "TRUNCATE"
      - "DELETE"

  file_system:
    allowed_paths:
      - "/workspace/user_data/"
      - "/tmp/"
    denied_paths:
      - "/etc/"
      - "/root/"
      - "/.ssh/"
```

**Content Moderation:**

```text
Request → AI Gateway → Content Filter
                        ├─ Check for harmful content
                        ├─ Check for bias
                        ├─ Check for inappropriate language
                        ├─ Check for copyright violations
                        └─ Result: ALLOW | BLOCK | WARN
```

### 5. Governance and Compliance

#### Audit Logging

**Required Audit Fields:**

```json
{
  "timestamp": "2025-01-07T10:30:00Z",
  "correlation_id": "req-12345",
  "user_subject": "alice@example.com",
  "user_roles": ["data-analyst"],
  "request_type": "tool_invocation",
  "tool_name": "database_query",
  "tool_params": {
    "query": "SELECT * FROM users WHERE dept = 'sales'",
    "database": "analytics_db"
  },
  "authorization_decision": "ALLOW",
  "applied_filters": ["row_level_security"],
  "response_summary": {
    "rows_returned": 150,
    "execution_time_ms": 245
  },
  "security_events": {
    "dlp_findings": [],
    "prompt_injection_detected": false
  },
  "ip_address": "10.0.1.45",
  "user_agent": "AI-Client/1.0"
}
```

**Audit Requirements:**

- **Immutability:** Logs cannot be modified or deleted
- **Completeness:** All requests logged, success and failure
- **Retention:** Comply with regulatory requirements (typically 90+ days)
- **Accessibility:** Available for compliance audits and forensics
- **User Context:** ALWAYS include user subject in logs

#### Compliance Controls

**GDPR Compliance:**

- Right to access: Provide user's AI interaction history
- Right to erasure: Delete user's AI data upon request
- Data minimization: Only collect necessary data
- Purpose limitation: Use data only for stated purposes
- Logging with consent: Ensure users consent to logging

**HIPAA Compliance (if applicable):**

- Access controls: Subject-bound authorization
- Audit logs: Comprehensive PHI access logging
- Encryption: Encrypt PHI in transit and at rest
- Business Associate Agreements: With AI providers

**Industry Standards:**

- SOC 2: Security, availability, processing integrity
- ISO 27001: Information security management
- PCI DSS: If processing payment card data

### 6. Rate Limiting and Cost Control

#### Multi-Dimensional Rate Limiting

**Per-User Limits:**

```yaml
rate_limits:
  per_user:
    requests_per_minute: 60
    requests_per_hour: 1000
    tokens_per_day: 100000
    concurrent_requests: 5
```

**Per-Tool Limits:**

```yaml
tool_limits:
  expensive_operation:
    invocations_per_hour: 10
    max_data_volume_mb: 100

  standard_operation:
    invocations_per_hour: 100
    max_data_volume_mb: 10
```

**Cost-Based Limiting:**

```python
# Calculate cost per request
def calculate_cost(request):
    base_cost = 0.01  # cents
    token_cost = request.tokens * 0.00002  # $0.00002 per token
    tool_cost = sum(tool.cost for tool in request.tools)

    return base_cost + token_cost + tool_cost

# Enforce budget limits
user_budget = get_user_budget(user_id)
if user_budget.spent_today + request_cost > user_budget.daily_limit:
    return "Budget exceeded"
```

#### Adaptive Rate Limiting

**Risk-Based Throttling:**

```python
def get_rate_limit(user, request):
    base_limit = 100  # requests per hour

    # Adjust based on risk factors
    risk_score = calculate_risk(user, request)

    if risk_score > 0.8:
        return base_limit * 0.2  # Severe throttling
    elif risk_score > 0.5:
        return base_limit * 0.5  # Moderate throttling
    else:
        return base_limit  # Normal rate
```

**Anomaly-Based Throttling:**

```text
Detect unusual patterns:
- Sudden spike in requests
- Requests from unusual location
- New tool usage patterns
- Large data volume requests

Response:
1. Log anomaly
2. Reduce rate limits temporarily
3. Alert security team
4. Require additional authentication
```

### 7. Monitoring and Alerting

#### Real-Time Monitoring

**Key Metrics:**

- Requests per second (total, per user, per tool)
- Authentication failure rate
- Authorization denial rate
- Prompt injection detection rate
- DLP violation rate
- Average response time
- Error rate
- Token consumption
- **Subject binding compliance rate**

**Dashboards:**

```text
AI Gateway Security Dashboard
├─ Authentication Metrics
│  ├─ Successful authentications
│  ├─ Failed authentications
│  └─ Subject propagation success rate
├─ Authorization Metrics
│  ├─ Allowed requests
│  ├─ Denied requests
│  └─ Subject binding violations
├─ Security Events
│  ├─ Prompt injection attempts
│  ├─ DLP violations
│  └─ Policy violations
├─ Performance Metrics
│  ├─ Request latency
│  ├─ Error rates
│  └─ Tool execution times
└─ Cost Metrics
   ├─ Token consumption
   ├─ Tool invocation costs
   └─ Per-user spending
```

#### Alerting Thresholds

**Critical Alerts (immediate response):**

- Subject binding violation detected
- Suspected prompt injection attack
- DLP violation (PII/PHI exposed)
- Authentication system failure
- Unusual privilege escalation attempt

**High Priority Alerts (response within 15 minutes):**

- High rate of authorization failures
- Abnormal tool usage pattern
- Budget limit approaching
- Error rate spike

**Medium Priority Alerts (response within 1 hour):**

- Elevated request rate
- New tool usage detected
- Performance degradation
- Configuration change

## Deployment Architecture

### High Availability Setup

```text
                Load Balancer
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Gateway-1    Gateway-2    Gateway-3
        │            │            │
        └────────────┼────────────┘
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
    AI Services            Tool Services
```

**Requirements:**

- Multiple gateway instances for redundancy
- Load balancing with health checks
- Session affinity for stateful operations
- Shared cache for rate limiting (Redis)
- Shared policy store (database)
- Centralized logging (SIEM)

### Security Zones

```text
Internet Zone (Untrusted)
    ↓
DMZ (Gateway)
    ├─ AI Gateway Cluster
    ├─ WAF (Web Application Firewall)
    └─ DDoS Protection
    ↓
Internal Zone (Trusted)
    ├─ AI Models
    ├─ Tool Services
    └─ Data Sources
    ↓
Data Zone (Highly Restricted)
    ├─ Customer Data
    ├─ Sensitive Analytics
    └─ Audit Logs
```

## Implementation Checklist

- [ ] Deploy AI Gateway cluster with high availability
- [ ] Implement subject-bound authentication (OAuth 2.0 OBO)
- [ ] Configure token exchange for subject propagation
- [ ] Implement prompt injection detection
- [ ] Deploy DLP scanning for requests and responses
- [ ] Configure policy enforcement (allow/deny lists)
- [ ] Set up comprehensive audit logging with user context
- [ ] Implement multi-dimensional rate limiting
- [ ] Configure security monitoring and alerting
- [ ] Test subject binding enforcement
- [ ] Validate all security controls with penetration testing
- [ ] Document security architecture and procedures
- [ ] Train operations team on incident response
- [ ] Establish compliance validation procedures
- [ ] Create runbooks for common security scenarios

## References

- MARA Security Framework
- Zero Trust Architecture for AI
- OAuth 2.0 On-Behalf-Of Flow (RFC 8693)
- OWASP LLM Top 10
- OWASP API Security Top 10
- NIST Cybersecurity Framework
