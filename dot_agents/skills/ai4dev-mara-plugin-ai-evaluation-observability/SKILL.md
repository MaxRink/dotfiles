---
name: ai4dev-mara-plugin-ai-evaluation-observability
description: This skill should be used when implementing evaluation frameworks, testing strategies, observability patterns, or guardrails for AI agents. It provides comprehensive guidance on choosing evaluation metrics (Task Success Rate, F1 Score, Retrieval Accuracy, LLM-as-Judge, etc.), implementing test patterns (Unit, Integration, Functional, Regression, Safety), setting up OpenTelemetry-based observability, and integrating guardrails with 8 different architectural patterns. Use this when building quality assurance frameworks, monitoring systems, or safety mechanisms for AI agent platforms.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/ai-evaluation-observability by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# AI Evaluation & Observability

## Overview

This skill enables implementation of comprehensive evaluation, testing, observability, and guardrail frameworks for AI agents. It provides structured patterns and best
practices for assessing agent performance, ensuring reliability, monitoring behavior, and enforcing safety constraints at the LLM level.

The skill is based on the MARA (Multi-Agent Reference Architecture) framework and provides practical guidance for:

- Selecting and implementing evaluation patterns to measure agent quality
- Designing test suites that validate functionality and safety
- Instrumenting agents with OpenTelemetry for end-to-end observability
- Integrating guardrails to prevent harmful outputs and ensure compliance

## Core Capabilities

### 1. Evaluation Framework Selection

Choose appropriate evaluation patterns based on what needs to be measured:

**For Task Success Measurement:**

- Use **Task Success Rate** pattern when measuring end-to-end workflow completion
- Target: ≥90% success rate for production systems
- Reference: `references/evaluation-patterns.md` for detailed rubrics

**For Classification and Extraction:**

- Use **F1 Score / Precision & Recall** pattern for intent classification and entity extraction
- Target: F1 ≥0.85 for high-quality systems
- Consider confusion matrix analysis for bias detection

**For Knowledge Retrieval:**

- Use **Retrieval Accuracy** pattern for RAG and knowledge-base systems
- Target: ≥85% correct retrieval
- Track semantic similarity scores to measure meaning alignment

**For Subjective Quality:**

- Use **LLM as Judge** pattern for clarity, helpfulness, and reasoning quality
- Target: ≥4/5 average rating
- Implement comparison against gold standards

**For Safety and Trust:**

- Use **Hallucination Rate** pattern to track factual correctness
- Target: <5% hallucination rate
- Implement **Calibration Error** measurement for confidence vs. accuracy alignment

### 2. Test Pattern Implementation

Organize testing into five layers, each with specific patterns:

#### Unit Testing

- **Prompt Template Logic Test**: Validate template formatting and placeholders
- **Utility Function Test**: Verify core functions (token counting, formatting, memory)
- Tools: pytest, unittest, coverage.py
- Target: 100% unit test coverage with edge case handling

#### Integration Testing

- **LLM Endpoint Integration Test**: Verify API connectivity and schema validation
- **External API Chaining Test**: Test tool and plugin integrations
- Tools: Postman, LangSmith, Pact, WireMock
- Target: <1% failure rate, responses within latency threshold

#### Functional Testing

- **End-to-End Agent Task Test**: Validate complete workflows
- **Memory Recall Consistency Test**: Ensure context retention
- Tools: LangSmith, Playwright, Selenium
- Target: ≥95% success in defined flows

#### Regression Testing

- **Version Output Diff Test**: Compare current vs. previous outputs
- Tools: Snapshot testing, LangTest, diff-match-patch
- Target: No significant quality degradation

#### Safety Testing

- **Jailbreak Prompt Resistance Test**: Test against adversarial prompts
- **Toxic Content Handling Test**: Validate content safety
- Tools: PromptBench, Perspective API, Detoxify, LlamaGuard
- Target: <1% jailbreak rate, toxicity score <0.2

Refer to `references/test-patterns.md` for detailed test scenarios, pass criteria, and recommended tools for each pattern.

### 3. Observability Pattern Implementation

Implement OpenTelemetry-based observability for distributed AI agent tracing:

#### Instrumentation Approach Selection

**Choose Auto-Instrumentation when:**

- Rapid prototyping or POC stage
- Using standard frameworks and libraries
- Need quick telemetry coverage
- Limited observability expertise

**Choose Manual Instrumentation when:**

- Building production-grade systems
- Need business-specific metrics
- Require fine-grained performance optimization
- Custom workflows and logic

#### Key Metrics to Track

**Throughput & Latency:**

- Throughput (RPS/TPS): Requests per second
- Total task execution time (end-to-end)
- LLM inference time, Vector DB search time, Tool call time
- Track p90, p95, p99 latency percentiles

**Reliability & Quality:**

- Agent/Tool availability and error rates
- Retry and backoff statistics
- Hallucination detection rates
- Guardrail violation counts
- User escalation rate

**Resource & Cost:**

- CPU/GPU/Memory utilization
- Token usage (prompt + completion)
- Cost per request estimates
- Storage and retrieval costs

**Context Propagation:**

- Implement W3C Trace Context standard
- Use `traceparent` and `tracestate` headers
- Propagate context across all service boundaries
- Follow OpenTelemetry semantic conventions for Gen AI

#### Observability Architecture

Implement the following participant structure:

1. **Agent Orchestrator**: Create root spans, record task-level attributes
2. **Task Executor**: Create child spans, track task metrics
3. **Model Inference Component**: Log model name/version, token usage, inference duration
4. **External Service Adapter**: Instrument API calls with HTTP/messaging conventions
5. **Telemetry Collector**: Aggregate traces/metrics/logs for analysis

Refer to `references/observability-patterns.md` for detailed architecture, semantic conventions, and implementation checklist.

### 4. Guardrails Integration

Select appropriate guardrail integration pattern based on requirements:

#### Pattern Selection Guide

**Latency-Driven:**

- <10ms required: Library or Sidecar
- <50ms acceptable: Filter or Gateway Plugin
- <200ms acceptable: Microservice or Proxy
- No latency impact: Event Processor (async)

**Scale-Driven:**

- Millions of requests/sec: Event Processor, Sidecar
- Thousands of requests/sec: Microservice, Gateway Plugin
- Hundreds of requests/sec: Any pattern

**Architecture-Driven:**

- Monolith: Library or Filter
- Microservices: Microservice or Sidecar
- Serverless: Library or Microservice
- Edge/IoT: Library
- Kubernetes: Sidecar

#### The 8 Guardrail Patterns

1. **Guardrail as Proxy**: Centralized enforcement, simple deployment
2. **Guardrail as Microservice**: Independent scaling, reusable across teams
3. **Guardrail as Filter (Middleware)**: Composable, per-route customization
4. **Guardrail as Sidecar**: Low latency, per-agent configuration
5. **Guardrail as Event Processor**: Async audit, zero latency impact
6. **Guardrail as Library/SDK**: Lowest latency, embedded in-process
7. **Guardrail as API Gateway Plugin**: Leverages existing infrastructure
8. **Hybrid - Layered Guardrails**: Defense-in-depth, optimized per-layer

Each pattern has different trade-offs in terms of latency, scalability, flexibility, and operational complexity.

Refer to `references/guardrails-patterns.md` for detailed architecture diagrams, decision matrices, and implementation guidance for each pattern.

## Workflow: Building a Complete Quality Framework

When building a comprehensive AI agent quality framework, follow this workflow:

### Step 1: Define Quality Requirements

Identify what needs to be measured and enforced:

- Performance requirements (latency, throughput)
- Quality requirements (accuracy, relevance)
- Safety requirements (toxicity, jailbreaks)
- Compliance requirements (PII, regulatory)

### Step 2: Select Evaluation Patterns

Choose evaluation patterns from `references/evaluation-patterns.md` based on:

- Agent type (chatbot, task executor, retrieval agent)
- Use case criticality (customer-facing vs. internal)
- Quality dimensions to measure (accuracy, helpfulness, safety)

Map each requirement to specific evaluation patterns with scoring rubrics.

### Step 3: Design Test Suite

Structure tests across all five layers:

- Start with unit tests for core components
- Add integration tests for external dependencies
- Implement end-to-end functional tests
- Set up regression tests for version comparison
- Add safety tests for adversarial scenarios

Refer to `references/test-patterns.md` for test patterns, recommended tools, and pass criteria.

### Step 4: Implement Observability

Instrument agents with OpenTelemetry:

- Choose instrumentation approach (auto vs. manual)
- Define key metrics to track (throughput, latency, quality)
- Implement trace context propagation
- Set up telemetry collector and dashboards
- Configure alerts for anomalies

Follow the architecture in `references/observability-patterns.md` with proper semantic conventions.

### Step 5: Integrate Guardrails

Select and implement guardrail pattern(s):

- Evaluate latency, scale, and ops constraints
- Choose pattern from decision matrix
- Implement guardrail integration
- Configure fail-open vs. fail-closed behavior
- Add monitoring for guardrail effectiveness

Use `references/guardrails-patterns.md` for pattern selection and implementation guidance.

### Step 6: Validate and Monitor

After implementation:

- Run full test suite and validate pass rates
- Monitor evaluation metrics in production
- Track observability dashboards
- Review guardrail effectiveness (false positive/negative rates)
- Iterate based on findings

## Quick Reference: Evaluation Pattern Selection

Use this quick reference to select evaluation patterns:

| What to Measure | Pattern to Use | Target Metric | Reference Section |
|-----------------|---------------|---------------|-------------------|
| End-to-end task completion | Task Success Rate | ≥90% success | Evaluation Patterns #1 |
| Classification accuracy | F1 Score | F1 ≥0.85 | Evaluation Patterns #2 |
| Document retrieval quality | Retrieval Accuracy | ≥85% correct | Evaluation Patterns #3 |
| Semantic meaning alignment | Semantic Similarity | ≥0.85 similarity | Evaluation Patterns #4 |
| Subjective quality (clarity, helpfulness) | LLM as Judge | ≥4/5 rating | Evaluation Patterns #5 |
| Fairness across demographics | Bias Detection | <5% variance | Evaluation Patterns #6 |
| Factual correctness | Hallucination Rate | <5% hallucination | Evaluation Patterns #7 |
| Confidence reliability | Calibration Error | ≤5% error | Evaluation Patterns #8 |

## Quick Reference: Test Pattern Selection

| Test Type | When to Use | Tools | Pass Criteria |
|-----------|------------|-------|---------------|
| Unit: Prompt Template | Before LLM calls | pytest, LangChain TestKit | Expected output structure |
| Unit: Utility Function | Backend functions | pytest, unittest | 100% coverage, no errors |
| Integration: LLM Endpoint | API connectivity | Postman, LangSmith | <1% failure rate |
| Integration: API Chaining | External tools | Pact, WireMock | Within latency threshold |
| Functional: End-to-End | Real user scenarios | Playwright, Selenium | ≥95% success rate |
| Functional: Memory Recall | Context retention | LangChain Memory | ≥90% recall accuracy |
| Regression: Version Diff | Before version rollout | Snapshot testing | No quality degradation |
| Safety: Jailbreak Resistance | Adversarial testing | PromptBench, LlamaGuard | <1% jailbreak rate |
| Safety: Toxic Content | Content safety | Perspective API, Detoxify | Toxicity <0.2 |

## Quick Reference: Guardrail Pattern Selection

| Pattern | Latency | Best For | Complexity |
|---------|---------|----------|------------|
| Proxy | Medium | Uniform enforcement, simple ops | Low |
| Microservice | Medium | Multi-team, reusability | Medium |
| Filter | Low | Composable stacks, per-route control | Medium |
| Sidecar | Low | Kubernetes, per-agent config | High |
| Event Processor | None (async) | Audit, compliance, no latency tolerance | High |
| Library/SDK | Very Low | Edge deployment, offline, simple rules | Very Low |
| Gateway Plugin | Low | Infrastructure-first, existing gateway | Low |
| Hybrid Layered | Variable | Complex systems, defense-in-depth | High |

## Resources

This skill includes comprehensive reference documentation:

### references/evaluation-patterns.md

Complete evaluation pattern catalog with:

- 8 core evaluation patterns with scoring rubrics
- Technical, functional, and model evaluation matrices
- Quality metrics definitions
- Pattern selection guidance
- Recommended tools and evaluation stages

### references/test-patterns.md

Comprehensive test pattern guide with:

- Unit, integration, functional, regression, and safety test patterns
- Test scenarios and pass criteria
- Recommended tools and libraries
- Test data requirements
- Best practices for test coverage, automation, and maintenance

### references/observability-patterns.md

OpenTelemetry implementation guide with:

- AI Agent Observability behavioral pattern
- Key metrics to track (throughput, latency, reliability, quality, cost)
- Auto-instrumentation vs. manual instrumentation comparison
- W3C Trace Context protocol
- OpenTelemetry semantic conventions for Gen AI
- Architecture and participant responsibilities
- Implementation checklist and best practices

### references/guardrails-patterns.md

Guardrail integration architecture guide with:

- 8 integration patterns with detailed architectures
- Decision matrix for pattern selection
- Selection criteria (latency, scale, ops, architecture)
- Trade-off analysis for each pattern
- External service integration examples
- Implementation checklist and best practices

## Best Practices

### Evaluation

- Start with objective metrics before subjective ones
- Establish baselines before optimization
- Track metrics over time to detect drift
- Use multiple evaluation patterns for comprehensive coverage

### Testing

- Automate regression tests for every deployment
- Test with both benign and adversarial inputs
- Maintain at least 80% code coverage
- Include edge cases and failure scenarios

### Observability

- Follow OpenTelemetry semantic conventions
- Keep instrumentation overhead <5%
- Use sampling for high-volume traces
- Sanitize PII from logs and traces

### Guardrails

- Design for graceful degradation
- Monitor false positive/negative rates
- Version guardrail configurations
- Regularly review and update rules

### Integration

- Prioritize patterns based on requirements
- Measure baseline performance before changes
- Implement incrementally with validation
- Document decisions and rationale
