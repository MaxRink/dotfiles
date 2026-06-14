# Agent-to-Agent (A2A) Security Checklist

## Overview

The Agent-to-Agent (A2A) protocol enables direct, dynamic collaboration between autonomous AI agents.
This checklist provides comprehensive security requirements for implementing secure A2A communication in MARA-based systems.

## A2A Protocol Security Risks

### 1. Agent Impersonation and Shadowing

Attackers clone or mimic legitimate agents through:

- Flawed identity verification
- Typosquatting on agent names/domains
- Man-in-the-middle attacks on discovery services
- Replay of captured authentication credentials

### 2. Agent Card Management Vulnerabilities

- Poor version control allowing outdated/vulnerable agents
- Weak authentication in agent card endpoints
- Exposure of sensitive metadata in agent cards
- Unauthorized modification of agent capabilities

### 3. Agent Card Context Poisoning

- Malicious content embedded in agent cards
- Injection attacks through agent descriptions
- Compromised capability declarations
- Trojan horse tool definitions

### 4. Task Replay Attacks

- Captured legitimate requests retransmitted
- Lack of request uniqueness validation
- Missing timestamp verification
- Insufficient request binding to session

## Security Checklist

### Authentication and Identity

- [ ] **Strong Agent Authentication**
  - [ ] Implement certificate-based authentication for all agents
  - [ ] Use mutual TLS (mTLS) for agent-to-agent connections
  - [ ] Deploy agent identity registry with verification
  - [ ] Validate agent certificates against trusted CA
  - [ ] Implement certificate pinning where appropriate
  - [ ] Configure short-lived certificates (24-72 hours max)

- [ ] **Agent Identity Verification**
  - [ ] Verify agent identity against central registry before interaction
  - [ ] Check agent identity has not been revoked
  - [ ] Validate agent domain ownership
  - [ ] Implement anti-typosquatting checks (edit distance, known malicious patterns)
  - [ ] Cross-reference agent identity with known good agents
  - [ ] Log all identity verification attempts

- [ ] **Authentication Credentials Management**
  - [ ] Rotate agent credentials regularly (daily or per-session)
  - [ ] Store credentials in secure vaults (not in code or config files)
  - [ ] Use separate credentials per agent instance
  - [ ] Implement credential revocation mechanisms
  - [ ] Monitor for credential compromise indicators

### Authorization and Access Control

- [ ] **Subject-Bound Authorization**
  - [ ] ALL A2A requests MUST carry authenticated end-user subject
  - [ ] Implement OAuth 2.0 On-Behalf-Of (OBO) flow
  - [ ] Validate user subject at EVERY service hop
  - [ ] Reject requests using generic "admin" or service accounts
  - [ ] Propagate user claims through entire call chain
  - [ ] Log user subject with all authorization decisions

- [ ] **Granular Authorization Checks**
  - [ ] Perform independent backend authorization on A2A servers
  - [ ] Do not trust client-side permission claims
  - [ ] Validate permissions for specific requested operations
  - [ ] Implement per-tool/per-resource authorization
  - [ ] Apply least privilege principle to all agent interactions
  - [ ] Use dynamic, context-aware authorization policies

- [ ] **Break-Glass Procedures**
  - [ ] Document explicit exceptions to subject-bound auth
  - [ ] Require approval for non-subject operations
  - [ ] Enhanced audit trails for emergency access
  - [ ] Time-limited emergency credentials
  - [ ] Automatic security team notification
  - [ ] Post-incident review of all break-glass usage

### Secure Communications

- [ ] **Transport Security**
  - [ ] ALL A2A traffic MUST use HTTPS/TLS
  - [ ] Enforce TLS 1.3 or higher (disable TLS 1.2 and below)
  - [ ] Use strong cipher suites only (ECDHE-based, AES-GCM)
  - [ ] Implement certificate validation (no self-signed in production)
  - [ ] Enable HSTS (HTTP Strict Transport Security)
  - [ ] Configure certificate transparency logging

- [ ] **Message Security**
  - [ ] Sign all A2A messages with sender's private key
  - [ ] Validate message signatures before processing
  - [ ] Implement message integrity checks (HMAC)
  - [ ] Encrypt sensitive data in message payloads
  - [ ] Use structured message formats (JSON, Protobuf)
  - [ ] Validate message schemas before processing

- [ ] **Network Security**
  - [ ] Implement network segmentation for agent communications
  - [ ] Use private networks where possible (VPC, VPN)
  - [ ] Configure firewall rules for agent-to-agent traffic
  - [ ] Deploy intrusion detection systems (IDS)
  - [ ] Monitor network traffic for anomalies
  - [ ] Implement rate limiting at network layer

### Replay Attack Prevention

- [ ] **Request Uniqueness**
  - [ ] Include unique nonce in every A2A request
  - [ ] Validate nonce has not been seen before
  - [ ] Maintain nonce cache with TTL (time-to-live)
  - [ ] Reject requests with duplicate nonces
  - [ ] Use cryptographically random nonce generation
  - [ ] Implement nonce expiration (5-10 minutes)

- [ ] **Timestamp Verification**
  - [ ] Include timestamp in every request
  - [ ] Validate timestamp is within acceptable window (±5 minutes)
  - [ ] Reject requests with old timestamps
  - [ ] Synchronize clocks using NTP
  - [ ] Log timestamp validation failures
  - [ ] Implement clock skew tolerance

- [ ] **Message Authentication Codes (MAC)**
  - [ ] Compute MAC over entire request (headers + body + nonce + timestamp)
  - [ ] Use HMAC-SHA256 or stronger
  - [ ] Include MAC in request headers
  - [ ] Validate MAC before processing request
  - [ ] Use shared secrets or derived keys for MAC
  - [ ] Rotate MAC keys regularly

### Agent Card Security

- [ ] **Agent Card Endpoint Protection**
  - [ ] Serve agent cards over HTTPS with valid certificates
  - [ ] Implement authentication for agent card access (mTLS preferred)
  - [ ] Apply network restrictions (IP allowlisting, VPC)
  - [ ] Use separate, dedicated endpoints for agent cards
  - [ ] Implement rate limiting on agent card requests
  - [ ] Log all agent card access attempts

- [ ] **Agent Card Content Security**
  - [ ] NEVER include credentials directly in agent cards
  - [ ] Validate agent card schema before processing
  - [ ] Sanitize all content from agent cards
  - [ ] Implement content security policy for agent cards
  - [ ] Version agent cards with semantic versioning
  - [ ] Sign agent cards with publisher's private key
  - [ ] Verify agent card signatures before use

- [ ] **Agent Card Version Management**
  - [ ] Maintain version history for all agent cards
  - [ ] Implement deprecation policies for old versions
  - [ ] Notify consumers of agent card updates
  - [ ] Support backward compatibility when possible
  - [ ] Document breaking changes clearly
  - [ ] Implement automatic security updates

- [ ] **Agent Card Validation**
  - [ ] Validate JSON/YAML structure against schema
  - [ ] Check for required fields (name, version, endpoint, capabilities)
  - [ ] Validate endpoint URLs are HTTPS
  - [ ] Check authentication methods are supported and secure
  - [ ] Verify capabilities are reasonable and expected
  - [ ] Scan for malicious content (XSS, injection patterns)

### Input Validation and Sanitization

- [ ] **Request Validation**
  - [ ] Validate all incoming A2A requests against schema
  - [ ] Implement input sanitization for all parameters
  - [ ] Check data types match expected types
  - [ ] Validate string lengths are within limits
  - [ ] Reject requests with unexpected fields
  - [ ] Implement allow-lists for enumerated values

- [ ] **Prompt Injection Prevention**
  - [ ] Treat all A2A request content as untrusted
  - [ ] Scan for prompt injection patterns
  - [ ] Use separate validation LLM for input analysis
  - [ ] Implement contextual separation in prompts
  - [ ] Apply content filtering before LLM processing
  - [ ] Log potential injection attempts

- [ ] **Data Validation**
  - [ ] Validate all data from agent cards before use
  - [ ] Sanitize tool descriptions and metadata
  - [ ] Check URLs for validity and safe schemes (https only)
  - [ ] Validate agent capabilities against known patterns
  - [ ] Implement max payload size limits
  - [ ] Reject oversized or malformed requests

### Monitoring and Logging

- [ ] **Comprehensive Logging**
  - [ ] Log all A2A authentication attempts (success and failure)
  - [ ] Log all authorization decisions with user subject
  - [ ] Log all agent-to-agent communications (summary, not full payload)
  - [ ] Log agent card accesses and updates
  - [ ] Log security events (injection attempts, validation failures)
  - [ ] Include correlation IDs for distributed tracing

- [ ] **Security Monitoring**
  - [ ] Monitor for failed authentication patterns
  - [ ] Alert on repeated authorization failures
  - [ ] Detect anomalous agent behavior
  - [ ] Monitor for replay attack indicators
  - [ ] Track agent communication patterns
  - [ ] Alert on subject binding violations

- [ ] **Audit Requirements**
  - [ ] Maintain tamper-proof audit logs
  - [ ] Include user subject in all audit entries
  - [ ] Retain logs per regulatory requirements (typically 90+ days)
  - [ ] Implement log aggregation and centralization (SIEM)
  - [ ] Regular audit log reviews
  - [ ] Support forensic investigations

### Error Handling and Resilience

- [ ] **Secure Error Handling**
  - [ ] Never expose internal errors to external agents
  - [ ] Return generic error messages to callers
  - [ ] Log detailed errors internally
  - [ ] Implement error rate limiting
  - [ ] Gracefully handle authentication failures
  - [ ] Avoid information leakage in error responses

- [ ] **Resilience and Availability**
  - [ ] Implement circuit breakers for agent dependencies
  - [ ] Configure timeouts for all A2A calls
  - [ ] Implement retry logic with exponential backoff
  - [ ] Deploy redundant agent instances
  - [ ] Implement health checks and monitoring
  - [ ] Plan for graceful degradation

- [ ] **DDoS and Abuse Prevention**
  - [ ] Implement rate limiting per agent identity
  - [ ] Configure request throttling
  - [ ] Deploy DDoS protection services
  - [ ] Monitor for abuse patterns
  - [ ] Implement automatic blocking for abusive agents
  - [ ] Maintain agent reputation scores

### Supply Chain Security

- [ ] **Agent Provenance Verification**
  - [ ] Verify agent publisher identity
  - [ ] Check agent digital signatures
  - [ ] Maintain trusted agent registry
  - [ ] Implement agent reputation system
  - [ ] Review agent source code when possible
  - [ ] Monitor agent behavior post-deployment

- [ ] **Dependency Management**
  - [ ] Audit all agent dependencies
  - [ ] Use software bill of materials (SBOM)
  - [ ] Monitor for dependency vulnerabilities
  - [ ] Implement automated dependency updates
  - [ ] Use private registries for internal agents
  - [ ] Verify checksums for all dependencies

- [ ] **Third-Party Agent Vetting**
  - [ ] Review security practices of third-party agent providers
  - [ ] Require security certifications where applicable
  - [ ] Conduct security assessments before integration
  - [ ] Monitor third-party agent behavior
  - [ ] Maintain vendor security questionnaires
  - [ ] Implement third-party risk management

### Testing and Validation

- [ ] **Security Testing**
  - [ ] Conduct penetration testing of A2A interfaces
  - [ ] Test for common vulnerabilities (OWASP Top 10)
  - [ ] Validate authentication and authorization logic
  - [ ] Test replay attack prevention mechanisms
  - [ ] Verify input validation effectiveness
  - [ ] Test error handling for information leakage

- [ ] **Compliance Validation**
  - [ ] Verify subject-bound authorization enforcement
  - [ ] Validate audit logging completeness
  - [ ] Check encryption standards compliance
  - [ ] Review access control configurations
  - [ ] Test incident response procedures
  - [ ] Validate data handling practices

## Implementation Priority

### Critical (Implement First)

1. Subject-bound authorization
2. Mutual TLS (mTLS) for all A2A connections
3. Agent identity verification
4. Request validation and sanitization
5. Comprehensive audit logging with user context

### High Priority (Implement Soon)

1. Replay attack prevention (nonce + timestamp)
2. Agent card security
3. Error handling and resilience
4. Security monitoring and alerting
5. Rate limiting and abuse prevention

### Medium Priority (Implement as Resources Allow)

1. Agent reputation system
2. Advanced threat detection
3. Automated security testing
4. Supply chain security enhancements
5. Performance optimization

## References

- A2A Protocol Specification
- MARA Security Framework
- Zero Trust Architecture for AI
- OWASP API Security Top 10
- OAuth 2.0 On-Behalf-Of Flow (RFC 8693)
