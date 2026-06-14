---
name: ai4dev-mara-plugin-ai-security-guidelines
description: Comprehensive security guidelines for implementing AI systems within the MARA framework. Use this skill when implementing Zero Trust architecture for AI systems, mitigating OWASP LLM Top 10 vulnerabilities, securing Agent-to-Agent (A2A) communication, implementing Model Context Protocol (MCP) security, configuring AI Gateways, or applying subject-bound authorization and JIT/JEA access control for autonomous AI agents and LLM-based applications.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/ai-security-guidelines by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# AI Security Guidelines

## Overview

Implement comprehensive security controls for AI-native architectures using the MARA (Magenta Architecture Reference for AI) security framework.
This skill provides detailed guidance for securing autonomous AI agents, Large Language Models (LLMs), and AI-enabled microservices based on Zero
Trust principles and industry standards including OWASP LLM Top 10.

## When to Use This Skill

Apply this skill when:

- Designing security architecture for AI systems with autonomous agents
- Implementing Zero Trust principles for LLM applications
- Mitigating specific OWASP LLM Top 10 vulnerabilities (prompt injection, sensitive information disclosure, insecure output handling, etc.)
- Securing Agent-to-Agent (A2A) communication protocols
- Implementing Model Context Protocol (MCP) security controls
- Deploying and configuring AI Gateways for LLM traffic
- Applying subject-bound authorization for AI operations
- Implementing Just-in-Time (JIT) and Just-Enough-Access (JEA) controls
- Conducting security reviews of AI system architectures
- Responding to AI-specific security incidents

## Core Security Principles

### Zero Trust for AI Systems

Apply Zero Trust principles with AI-specific extensions:

1. **Verify Explicitly**
   - Authenticate AI agents as distinct principals
   - Verify agent identity and provenance
   - Validate model versions and integrity
   - Confirm the authenticated end-user on whose behalf the agent acts

2. **Use Least Privilege**
   - Apply Just-in-Time (JIT) access provisioning
   - Implement Just-Enough-Access (JEA) scoping
   - Use dynamic, context-aware authorization
   - Confine agents to intended domains and specific tasks
   - Grant permissions per-task, not per-agent lifecycle

3. **Assume Breach**
   - Isolate AI workloads in secure sandboxes
   - Monitor agent behavior for anomalies
   - Detect prompt injection and jailbreak attempts
   - Implement blast radius containment
   - Prepare for model poisoning scenarios

**Critical Requirement: Subject-Bound Authorization**

All AI operations must preserve end-user identity throughout the call chain:

- Authorization decisions MUST be bound to the authenticated human user
- Static "admin" or broad service roles MUST NOT be used for runtime authorization except in strictly defined break-glass scenarios
- AI agents must invoke downstream capabilities using On-Behalf-Of (OBO) credentials that preserve the end-user's identity and context
- This enables least-privilege, auditable decisions across all service hops

For detailed Zero Trust implementation guidance, reference `references/zero_trust_ai_principles.md`.

### Defense in Depth

Implement multiple layers of security controls:

- AI Gateway for centralized policy enforcement
- Prompt security at the application layer
- Subject-bound authorization at the service layer
- Data encryption in transit and at rest
- Secure sandboxing for code execution
- Comprehensive monitoring and alerting

## OWASP LLM Top 10 Mitigation

### 1. Prompt Injection

**Threat:** Malicious input overrides model's original instructions.

**Mitigation:**

- Implement input validation with rule-based filters and validation LLMs
- Use contextual separation with unique delimiters between trusted system prompts and untrusted user inputs
- Apply internal prompt engineering with explicit directives and self-reminders
- Ensure subject-bound authorization for all LLM-initiated actions

### 2. Sensitive Information Disclosure

**Threat:** Model inadvertently reveals confidential data from training, memory, or system prompts.

**Mitigation:**

- Deploy Data Leakage Prevention (DLP) solutions for real-time inspection
- Apply data masking and anonymization techniques
- NEVER embed sensitive data directly in system prompts
- Externalize sensitive data to secure systems (vaults, secret managers)

### 3. Insecure Output Handling

**Threat:** LLM responses not properly validated before downstream processing, leading to code injection.

**Mitigation:**

- Treat ALL LLM outputs as untrusted
- Implement output validation and sanitization before processing
- Ensure tool execution occurs under subject-bound authorization context
- Apply strict privilege separation - LLM operates with minimum necessary privileges

### 4. Supply Chain Vulnerabilities

**Threat:** Compromised components, services, or datasets undermine system integrity.

**Mitigation:**

- Vet training data sources and third-party assets for integrity
- Use hash-checking (SHA-256) for models and datasets
- Implement automated security testing in CI/CD pipelines
- Maintain software bill of materials (SBOM) for all components

### 5. Excessive Agency

**Threat:** AI agent takes unintended actions without proper oversight.

**Mitigation:**

- Enforce least-privilege access dynamically
- Implement human-in-the-loop checkpoints for sensitive operations
- Use secure sandboxing for all code execution
- Define explicit action boundaries and rate limiting

### 6. System Prompt Leakage

**Threat:** System prompt containing sensitive data is revealed to users.

**Mitigation:**

- Design prompts assuming they will be exposed
- NEVER include sensitive data (API keys, credentials, internal URLs) in prompts
- Implement security controls independent of LLM (outside prompt instructions)
- Use environment variables and external secure stores for configuration

For detailed mitigation strategies for all OWASP LLM Top 10 vulnerabilities, reference `references/owasp_llm_top_10_mitigations.md`.

## Agent-to-Agent (A2A) Security

### A2A Protocol Security Risks

Key threats in A2A communication:

- Agent impersonation and shadowing (cloning legitimate agents)
- Agent card management vulnerabilities (poor version control, weak authentication)
- Agent card context poisoning (malicious content in agent manifests)
- Task replay attacks (captured requests retransmitted)

### Critical A2A Security Controls

1. **Rigorous Authentication and Authorization**
   - Strong credential validation with certificate-based authentication
   - Mutual TLS (mTLS) for all agent-to-agent connections
   - **Subject-Bound Authorization:** A2A servers MUST enforce subject-bound authorization - requests must carry and validate the authenticated end-user subject
   - Generic admin/service identities are PROHIBITED for business-data operations
   - Independent backend authorization checks based on least privilege

2. **Secure Communications**
   - ALL A2A traffic over HTTPS with TLS 1.3+
   - Strong cipher suites only (ECDHE-based, AES-GCM)
   - Mutual TLS (mTLS) between agents reduces replay attack risk

3. **Replay Attack Mitigation**
   - Use unique nonces in all requests
   - Implement timestamp verification (±5 minutes tolerance)
   - Apply Message Authentication Codes (HMAC-SHA256 or stronger)

4. **Agent Card Security**
   - Protect Agent Card endpoints with mTLS and network restrictions
   - NEVER include credentials directly in agent cards
   - Sign agent cards with publisher's private key
   - Validate agent card signatures and schema before processing

For comprehensive A2A security requirements, reference `references/a2a_security_checklist.md`.

## Model Context Protocol (MCP) Security

### MCP Security Architecture

MCP enables dynamic, discovery-based interactions between AI models and tools/data sources. Security is enforced through the **AI Gateway** - a semantic-aware security engine.

### AI Gateway Functions

The AI Gateway serves as the critical control point for all MCP interactions:

1. **Subject-Bound Authentication and Authorization**
   - Terminates user authentication
   - Performs token exchange to obtain subject-bound tokens (OBO flow)
   - Validates permissions before forwarding to MCP servers
   - Rejects calls attempting to use non-subject, "admin-like" privileges
   - Enforces OBO as default with explicit exceptions requiring enhanced audit trails

2. **Prompt Security**
   - Real-time inspection to prevent prompt injection attacks
   - Pattern-based and LLM-based detection
   - Context boundary enforcement

3. **Data Leakage Prevention (DLP)**
   - Detects and redacts PII, PHI, credentials in prompts and responses
   - Compliance with GDPR, HIPAA, and other privacy regulations

4. **Governance and Control**
   - Enforces policies using allow/deny lists
   - Built-in content moderation
   - Tool access control based on user permissions

5. **Monitoring and Audit**
   - Comprehensive logging with user subject
   - Real-time security event detection
   - Compliance reporting

### MCP Security Patterns

Key implementation patterns:

- **Pattern 1:** Centralized authentication and authorization
- **Pattern 2:** Prompt security and validation
- **Pattern 3:** Data leakage prevention (DLP)
- **Pattern 4:** Tool invocation security with subject-bound execution
- **Pattern 5:** Resource access control with row-level security
- **Pattern 6:** Secure tool discovery with approved registry
- **Pattern 7:** Context injection prevention
- **Pattern 8:** Rate limiting and abuse prevention

For detailed MCP security patterns and implementations, reference `references/mcp_security_patterns.md`.

For AI Gateway-specific security controls and deployment architecture, reference `references/ai_gateway_security.md`.

## Subject-Bound Authorization Implementation

### Core Principle

Every AI operation must execute under the authenticated end-user's identity, never using generic service accounts.

### Implementation Flow

```text
1. User authenticates to application → Receives user token (JWT/OAuth)
2. AI agent makes request with user token
3. AI Gateway validates user token and extracts user subject
4. AI Gateway exchanges token for subject-bound credential (OBO token)
5. Gateway forwards request with OBO token to downstream services
6. Each service validates OBO token and user subject
7. Tools execute with user's permissions (not admin/service account)
8. All operations logged with user subject for audit trail
```

### Token Flow Requirements

**User Token (JWT):**

- Contains user claims: subject, email, roles
- Validated by AI Gateway
- Used for initial authentication

**OBO Token (On-Behalf-Of):**

- Contains original user subject from user token
- Scoped to specific tool/resource being accessed
- Time-limited with short expiration (5-15 minutes)
- Verified at each service hop in the call chain

**Downstream Services:**

- Receive and validate OBO token
- Extract and verify user subject
- Enforce user-scoped permissions
- Log all operations with user context

### Prohibited Patterns

❌ **Generic Service Accounts:** Tool executes as "mcp-service-account" with admin privileges - REJECTED

❌ **Credential Switching:** Agent receives user token but executes as admin - REJECTED

❌ **Token Dropping:** Agent uses user token initially but drops it downstream - REJECTED

### Approved Pattern

✅ **Subject-Bound Execution:** User "<alice@example.com>" → All tools execute as "<alice@example.com>" → Permissions checked against Alice's privileges →
Audit logs record "<alice@example.com>" as actor

### Break-Glass Procedures

For rare emergency scenarios requiring non-subject operations:

- Document explicit policy exceptions
- Require approval workflow
- Enhanced audit trails with justification
- Time-limited emergency access
- Automatic security team notification
- Mandatory post-incident review

## Dynamic, Context-Aware Authorization

Traditional static role-based access control (RBAC) is insufficient for AI systems. Implement dynamic authorization considering:

### Context Factors

- **User Context:** Authenticated end-user requesting the action
- **Agent Context:** Which agent is performing the action
- **Task Context:** Specific task being performed
- **Data Context:** Data being accessed
- **Time Context:** When the action occurs
- **Location Context:** Request origination
- **Risk Context:** Calculated risk level of the action

### Authorization Decision Flow

1. Request initiated by AI agent
2. Extract authenticated user subject (mandatory)
3. Evaluate all context factors
4. Calculate risk score
5. Check policies for user + agent + task + data combination
6. Apply time-based constraints
7. Grant/deny with minimum necessary permissions (JIT/JEA)
8. Log decision with full context
9. Set expiration and revocation triggers

## Monitoring and Incident Response

### Essential Audit Events

Log all of the following with user subject:

1. **Authentication Events:** User/agent authentication success/failure, subject extraction
2. **Authorization Events:** Permission checks, tool access grants/denials, subject-bound validation results
3. **Tool Invocation Events:** Tool discovery, execution requests, parameters (sanitized), execution results
4. **Security Events:** Prompt injection attempts, DLP violations, rate limit breaches, subject binding failures
5. **Data Access Events:** Resources requested, data returned (metadata), filtering applied

### Key Monitoring Metrics

- Request rate per user
- Authentication/authorization failure rates
- Prompt injection detection rate
- DLP violation rate
- Subject binding compliance rate (target: 100%)
- Average response times
- Token consumption per user

### Alerting Priorities

**Critical (immediate response):**

- Subject binding violation detected
- Suspected prompt injection attack
- DLP violation (PII/PHI exposed)
- Authentication system failure
- Unusual privilege escalation attempt

**High Priority (15 min response):**

- High rate of authorization failures
- Abnormal tool usage patterns
- Budget limits approaching
- Error rate spikes

## Implementation Checklist

### Zero Trust Foundation

- [ ] Deploy AI Gateway cluster with high availability
- [ ] Implement subject-bound authentication (OAuth 2.0 OBO flow)
- [ ] Configure token exchange for subject propagation
- [ ] Apply JIT/JEA principles to all agent permissions
- [ ] Prohibit generic "admin" accounts; require subject binding
- [ ] Deploy agents in isolated sandbox environments
- [ ] Configure continuous monitoring for all agent activities

### LLM Security Controls

- [ ] Implement prompt injection detection (pattern-based and LLM-based)
- [ ] Deploy DLP scanning for requests and responses
- [ ] Configure output validation and sanitization
- [ ] Externalize all sensitive data from system prompts
- [ ] Implement human-in-the-loop for high-risk operations

### A2A Communication Security

- [ ] Implement mutual TLS (mTLS) for all A2A connections
- [ ] Deploy agent identity registry with verification
- [ ] Enforce subject-bound authorization on A2A servers
- [ ] Implement replay attack prevention (nonce + timestamp + MAC)
- [ ] Secure agent card endpoints with authentication and network restrictions
- [ ] Validate agent card signatures and content

### MCP Security

- [ ] Deploy AI Gateway as central control point
- [ ] Configure subject propagation and OBO token exchange
- [ ] Implement tool authorization with user permissions
- [ ] Secure tool discovery with approved registry
- [ ] Apply resource access controls with row-level security
- [ ] Implement rate limiting (per-user, per-tool, cost-based)

### Monitoring and Compliance

- [ ] Set up comprehensive audit logging with user context
- [ ] Configure SIEM with AI-specific detection rules
- [ ] Implement behavioral anomaly detection
- [ ] Establish incident response procedures for AI threats
- [ ] Validate subject propagation across all service hops
- [ ] Create compliance validation procedures (GDPR, HIPAA, etc.)
- [ ] Test all security controls with penetration testing

## References

This skill includes comprehensive reference documentation:

### references/owasp_llm_top_10_mitigations.md

Detailed mitigation strategies for all OWASP LLM Top 10 vulnerabilities including:

- Prompt injection prevention techniques (validation, contextual separation, prompt engineering)
- Sensitive information disclosure controls (DLP, data masking, strict separation)
- Insecure output handling safeguards (validation, sanitization, privilege separation)
- Supply chain security (vetting, integrity verification, CI/CD security)
- Excessive agency mitigation (least privilege, human-in-the-loop, sandboxing)
- System prompt leakage prevention (design for exposure, independent guardrails)

### references/zero_trust_ai_principles.md

Zero Trust architecture principles extended for AI systems:

- Core tenets: Verify Explicitly, Least Privilege, Assume Breach
- Subject-bound authorization implementation with OBO token flow
- Dynamic, context-aware authorization decision framework
- AI-specific challenges (non-deterministic behavior, autonomous decisions, dynamic tool usage)
- Zero Trust components (AI Gateway, Identity Provider, Policy Decision Point, SIEM)
- Continuous monitoring and validation requirements
- Implementation checklist for Zero Trust AI

### references/a2a_security_checklist.md

Comprehensive security checklist for Agent-to-Agent (A2A) protocol:

- Authentication and identity verification requirements
- Subject-bound authorization enforcement for A2A servers
- Secure communications (TLS 1.3+, mTLS, message signing)
- Replay attack prevention (nonces, timestamps, MAC)
- Agent card security (endpoint protection, content validation, version management)
- Input validation and prompt injection prevention
- Monitoring, logging, and audit requirements
- Supply chain security for third-party agents
- Implementation priorities (critical, high, medium)

### references/mcp_security_patterns.md

Model Context Protocol (MCP) security implementation patterns:

- Pattern 1: Centralized authentication and authorization with subject binding
- Pattern 2: Prompt security and validation techniques
- Pattern 3: Data leakage prevention (DLP) with sensitive data detection
- Pattern 4: Tool invocation security with subject-bound execution
- Pattern 5: Resource access control with row-level security
- Pattern 6: Secure tool discovery with approved registries
- Pattern 7: Context injection prevention strategies
- Pattern 8: Rate limiting and abuse prevention (per-user, per-tool, cost-based)
- Subject-bound authorization token flow and requirements
- Monitoring metrics and alerting thresholds

### references/ai_gateway_security.md

AI Gateway security controls and deployment architecture:

- Subject-bound authentication and authorization flows
- Prompt security (pattern-based and LLM-based detection)
- Data leakage prevention with comprehensive sensitive data categories
- Policy enforcement (allow/deny lists, content moderation)
- Governance and compliance (audit logging, GDPR/HIPAA controls)
- Rate limiting and cost control (multi-dimensional, adaptive, cost-based)
- Monitoring and alerting (dashboards, thresholds, incident response)
- Deployment architecture (high availability, security zones)
- Implementation checklist for AI Gateway deployment

## Summary

Apply these guidelines to implement defense-in-depth security for AI systems within the MARA framework. The core principles are:

1. **Zero Trust:** Verify explicitly, use least privilege, assume breach
2. **Subject-Bound:** All operations preserve end-user identity
3. **Defense in Depth:** Multiple security layers (gateway, application, service, data)
4. **Continuous Monitoring:** Real-time validation and audit logging
5. **Dynamic Authorization:** Context-aware, just-in-time permission granting

Always start with subject-bound authorization as the foundation, then layer additional controls based on specific threats and compliance requirements.
