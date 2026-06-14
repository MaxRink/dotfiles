
# Non-Functional Requirements Generation Reference

## Your Task

Generate non-functional requirements for performance, security, reliability, scalability, and compliance.

**Output:** `.migration/<feature>/spec-specification/nonfunctional-requirements.md`

## Input Context

Your prompt provides:

- Feature name
- `.migration/<feature>/plan/plan.json` (focus_areas, constraints, target_stack)
- `.migration/<feature>/architect/target-architecture.md` (Sections 6, 7, 8)
- `.migration/<feature>/gap-analysis/gaps.json` (security/performance gaps)

## Workflow

### 1. Extract NFR Context

From **plan.json:**

- Priority areas (performance, security, reliability, scalability)
- Technology stack constraints
- Deployment constraints
- Compliance requirements

From **architect target-architecture.md:**

- Section 6: Security architecture
- Section 7: Cross-cutting concerns
- Section 8: Performance considerations

From **gap-analysis gaps.json:**

- Security gaps
- Performance gaps
- Reliability gaps

### 2. Generate Performance Requirements (NFR-P)

Categories: Response time, throughput, resource utilization, scalability

```markdown
NFR-P{ID}: {Performance Requirement Title}

**Category:** Performance
**Priority:** {High|Medium|Low}
**Requirement:** System shall respond to X within Y ms under Z load
**Measurement:** {How to measure}
**Target Metric:** {Specific numerical target}
**Test Scenario:** {How to validate}
```

### 3. Generate Security Requirements (NFR-S)

Categories: Authentication, authorization, encryption, audit logging, compliance

```markdown
NFR-S{ID}: {Security Requirement Title}

**Category:** Security
**Priority:** {High|Medium|Low}
**Requirement:** System shall protect X using Y mechanism
**Implementation:** {Technical approach from architect}
**Compliance:** {Regulatory standards: GDPR, HIPAA, PCI-DSS}
**Validation:** {How to test}
```

### 4. Generate Reliability Requirements (NFR-R)

Categories: Availability, fault tolerance, disaster recovery, error handling

```markdown
NFR-R{ID}: {Reliability Requirement Title}

**Category:** Reliability
**Priority:** {High|Medium|Low}
**Requirement:** System shall be available X% of the time
**Implementation:** {Resilience patterns from architect}
**Target Metric:** {SLA, uptime, MTTR}
**Validation:** {Chaos engineering, fault injection}
```

### 5. Generate Scalability Requirements (NFR-SC)

Categories: Concurrent users, load capacity

```markdown
NFR-SC{ID}: {Scalability Requirement Title}

**Category:** Scalability
**Priority:** {High|Medium|Low}
**Requirement:** System shall scale to handle X concurrent users/requests
**Implementation:** {Scaling approach from architect}
**Target Metric:** {Specific capacity targets}
**Validation:** {Load testing scenarios}
```

### 6. Document Known Gaps

From **gaps.json**, extract gaps where category matches:

- security
- performance
- reliability

For each gap:

- Gap ID and description
- Severity
- Impact on NFR compliance
- Mitigation strategy or acceptance decision

### 7. Pre-Write Validation

Before writing, verify:

- ✓ All focus areas from plan.json have corresponding NFR categories
- ✓ Every NFR has a specific, measurable target metric
- ✓ Implementation approach references architect output
- ✓ Gaps from gap-analysis are documented
- ✓ Compliance requirements are complete

## Output Format

```markdown
# Non-Functional Requirements

## Executive Summary
- Total NFRs: N
- Categories: Performance (N), Security (N), Reliability (N), Scalability (N)
- Priority distribution: High (N), Medium (N), Low (N)

## 1. Performance Requirements
## 2. Security Requirements
## 3. Reliability Requirements
## 4. Scalability Requirements
## 5. Compliance Requirements
## 6. Known Gaps Impacting NFRs
## 7. NFR Traceability

| NFR ID | Category | Priority | Component | Target Metric | Test Approach |
|--------|----------|----------|-----------|---------------|---------------|
| NFR-P001 | Performance | High | ComponentA | <100ms p95 | Load test |
```

## Completion

Return to orchestrator:

```text
DONE: nonfunctional-requirements.md written
- Performance NFRs: N
- Security NFRs: N
- Reliability NFRs: N
- Scalability NFRs: N
- Compliance NFRs: N
- Gaps documented: N
```
