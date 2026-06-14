# Observability Patterns for AI Agents

This reference provides comprehensive observability patterns for monitoring, tracing, and debugging AI agents using OpenTelemetry and semantic conventions for generative AI systems.

## AI Agent Observability Pattern

**AI Agent Observability is a behavioral design pattern that lets you pass telemetry data (traces, metrics, and logs) along a chain of AI agent components.**

Upon executing a task, each component—such as the agent orchestrator, task executor, model inference, or external service adapter—decides either to enrich the
telemetry with its own contextual information or simply forward it downstream. A central Telemetry Collector acts as an observer, receiving all emitted telemetry
for aggregation, correlation, and analysis.

This approach allows AI agents to be instrumented for end-to-end observability without tightly coupling the components to the monitoring infrastructure.

---

## Key Points

- Each agent component participates in the chain, contributing its own telemetry attributes
- Telemetry is propagated along the execution path, maintaining trace and context
- The Telemetry Collector observes all events, acting as a centralized monitoring endpoint
- Semantic conventions standardize the attributes, enabling consistent analysis across tasks, agents, and models

---

## The Problem

AI agents are complex, autonomous entities that orchestrate multiple tasks, perform model inference, and interact with external services. Without standardized observability:

- It is difficult to debug failures or track reasoning behind decisions
- Metrics and logs are inconsistent, making system-wide monitoring unreliable
- Distributed operations cannot be correlated, obscuring performance bottlenecks

By applying this pattern, each agent action, task, and inference is **instrumented as a traceable span**, enriched with **metrics and logs**, all using
**[OpenTelemetry semantic conventions for generative AI systems](https://opentelemetry.io/docs/specs/semconv/gen-ai/)**.

Engineers can then:

- Understand task flow and dependencies (tracing)
- Measure performance and reliability (metrics)
- Debug and audit actions (structured logs)

---

## Key Metrics to Track

### Throughput Metrics

- **Throughput (RPS / TPS):** Number of tasks handled per second
- Helps identify capacity limits and scaling needs

### Latency Metrics

- **Total task execution time:** End-to-end latency
- **LLM inference time:** Time spent in model inference
- **Vector DB search time:** Time for retrieval operations
- **External Tool call time:** Time for API/tool invocations
- **Tool Call Latency Breakdown:** p90, p98 per tool

### Agent and Tool Reliability

- **Agent Availability:** Failed calls or timeouts
- **Tool Availability:** Error rate or downtime of each external integration
- **Retry / Backoff Stats:** How often retries resolve errors

### Resource Usage

- **CPU utilization:** Percentage of CPU used
- **Memory utilization:** Amount of memory consumed
- **GPU utilization:** For GPU-accelerated operations (if applicable)

### Token Usage (for LLMs)

- **Prompt token counts:** Input tokens sent to LLM
- **Completion token counts:** Output tokens received from LLM
- **Total tokens per request:** Combined token usage
- **Cost estimates:** Token-based pricing calculations

### Vector DB Statistics

- **Query latency:** Time to retrieve documents
- **Number of retrieved documents:** Count of results
- **Match scores:** Relevance scores of retrieved docs
- **Context Utilization:** Fraction of retrieved docs actually referenced in final answer

### Orchestration Statistics

- **Classifier results:** Which agent was picked to handle the task and why
- **Routing decisions:** How tasks are distributed
- **Agent selection accuracy:** Correctness of routing decisions

### Cost Efficiency Metrics

- **Token-based cost estimates:** LLM API costs
- **Storage and retrieval costs:** Vector DB costs
- **Compute time per task:** Infrastructure costs (if billed)

### Quality Signals

- **User feedback / ratings:** Direct user satisfaction
- **Semantic similarity scores:** Retrieved vs. expected results
- **Hallucination detection:** Frequency of incorrect claims
- **Relevance scores:** From vector DB or rerankers
- **Guardrail / Safety Check Results:** Toxicity, jailbreak attempts, policy violations
- **Deflection Rate:** % of tasks not requiring human intervention
- **User Escalation Rate:** % of tasks requiring human intervention

---

## Log Attributes to Capture

### LLM Interaction Logs

- **Input/output payloads** (sanitized if needed)
- **Prompt templates used**
- **Model version and provider**
- **Temperature and sampling parameters**

### Vector DB Logs

- **Query parameters:** Search parameters and filters
- **Retrieved document IDs:** Which documents were found
- **Similarity scores:** Relevance scores

### Error Logs

- **Error messages:** Detailed error descriptions
- **Stack traces:** For debugging failures
- **Retry attempts:** Number and timing of retries
- **Failure context:** What was being attempted when error occurred

---

## Technical Integration Patterns

### 1. Zero-/Low-Code Auto-Instrumentation

**What it is:**
Attach a language-specific agent or bootstrapper that automatically instruments popular frameworks and libraries at runtime—for example, HTTP clients/servers,
database drivers, or messaging systems.

**How it works:**
Uses mechanisms like bytecode/profiler agents (Java, .NET), import-time patches (Python, Node.js), or startup flags to inject instrumentation dynamically.
Configuration is typically handled via environment variables.

**Pros:**

- Fastest path to value — enables telemetry with minimal setup
- Requires little to no code changes
- Broad coverage for standard technologies and frameworks

**Cons:**

- Limited control and granularity
- Business-specific spans and attributes still require manual instrumentation
- Potential version coupling with framework updates

**When to Use:**

- Rapid prototyping or POC
- Standard frameworks and libraries
- Quick telemetry coverage
- Teams with limited observability expertise

**Example (Python):**

```bash
# Install auto-instrumentation
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Run with auto-instrumentation
opentelemetry-instrument python your_agent.py
```

---

### 2. "Manual" Code Instrumentation

**What it is:**
Integrate the OpenTelemetry (OTel) SDK and API directly into your codebase to explicitly create spans, metrics, and logs.

**How it works:**
Initialize tracer, meter, and logger providers; wrap key business logic with spans; attach attributes and events; record metrics; and propagate context across service boundaries.

**Pros:**

- Fine-grained control over telemetry data
- Enables rich domain context (e.g., orders, payments, SLAs)
- More durable across framework or runtime changes

**Cons:**

- Requires code modifications and developer time
- Higher maintenance overhead
- Risk of excessive or inconsistent instrumentation if not governed

**When to Use:**

- Production-grade systems
- Need for business-specific metrics
- Custom workflows and logic
- Fine-grained performance optimization

**Example (Python):**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Create spans
with tracer.start_as_current_span("agent_task") as span:
    span.set_attribute("task.type", "retrieval")
    span.set_attribute("task.id", task_id)

    # Your business logic here
    result = execute_task()

    span.set_attribute("task.status", "success")
```

---

## Structure and Participants

### 1. Agent Orchestrator (Root Span Creator)

**Role:** Receives tasks/queries and generates root spans, when not provided by the client

**Responsibilities:**

- Start the trace
- Propagate context downstream
- Record task-level attributes (task ID, user ID, priority)
- Emit root span metrics

**Example Attributes:**

- `agent.task.id`
- `agent.task.type`
- `agent.user.id`
- `agent.orchestrator.version`

---

### 2. Task Executor / Agent (Child Span Creator)

**Role:** Executes individual tasks assigned by the orchestrator

**Responsibilities:**

- Create child spans for each task
- Record task-specific metrics (success ratio, latency)
- Propagate context to downstream components
- Log task execution details

**Example Attributes:**

- `task.name`
- `task.status`
- `task.duration_ms`
- `task.retry_count`

---

### 3. Model Inference Component (Instrumentation Target)

**Role:** Performs model inference or reasoning

**Responsibilities:**

- Record inference duration
- Log model name/version
- Track token usage
- Generate spans for each inference call
- Capture errors and exceptions

**Example Attributes:**

- `gen_ai.request.model` (e.g., "claude-3-sonnet")
- `gen_ai.request.temperature`
- `gen_ai.usage.input_tokens`
- `gen_ai.usage.output_tokens`
- `gen_ai.response.finish_reasons`

---

### 4. External Service Adapter (Optional Span Creator)

**Role:** Handles calls to APIs, databases, or messaging systems

**Responsibilities:**

- Instrument calls with HTTP/messaging semantic conventions
- Track external service latency
- Log request/response details
- Correlate with agent spans
- Handle failures and retries

**Example Attributes:**

- `http.method`
- `http.url`
- `http.status_code`
- `messaging.system`
- `db.system`

---

### 5. Telemetry Collector (OpenTelemetry SDK / Backend)

**Role:** Aggregates spans, metrics, and logs

**Responsibilities:**

- Receive telemetry from all components
- Correlate distributed traces
- Store telemetry data
- Provide dashboards, alerts, and analytics
- Support querying and analysis

**Example Backends:**

- Jaeger (tracing)
- Prometheus (metrics)
- Grafana (visualization)
- Datadog, New Relic (commercial APM)

---

## Protocol: W3C Trace Context

OpenTelemetry (OTel) uses the **W3C Trace Context specification** to propagate trace information (such as trace and span IDs) between services.

See: <https://opentelemetry.io/docs/concepts/context-propagation>

The **W3C Trace Context** is a standard defined by the World Wide Web Consortium (W3C) that specifies how distributed tracing context should be passed between services — typically via HTTP headers.

It ensures that different tracing systems can interoperate by using a common propagation format.

### HTTP Headers

OTel follows this specification by sending and receiving the following HTTP headers:

#### 1. `traceparent` — contains the tracing identifiers

**Example:**

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

**Breakdown:**

- `00` – version
- `4bf92f3577b34da6a3ce929d0e0e4736` – trace ID (128-bit)
- `00f067aa0ba902b7` – parent (span) ID (64-bit)
- `01` – trace flags (e.g., sampled or not)

#### 2. `tracestate` — optional, carries vendor-specific data

**Example:**

```text
tracestate: vendorname=value,othervendor=value2
```

Used for:

- Sampling priorities
- Custom vendor IDs
- Additional metadata

### Context Propagation Flow

When a request leaves one service instrumented with OpenTelemetry:

1. The OTel SDK **injects** the `traceparent` and `tracestate` headers into the outgoing request
2. The receiving service **extracts** those headers
3. The receiving service continues the same trace context instead of starting a new trace
4. Each service adds its own spans as children of the parent span

This creates a distributed trace that spans multiple services and components.

---

## Participants & Responsibilities Table

| Component | Responsibility |
|-----------|---------------|
| **Agent Orchestrator** | Start root spans when not provided by the client |
| **Task Executor** | Execute tasks, create child spans, record task-specific metrics |
| **Model Inference Component** | Perform inference, record model-level metrics, span attributes |
| **External Service Adapter** | Instrument API/messaging calls, propagate trace context |
| **Telemetry Collector (OTel)** | Aggregate traces, metrics, logs; provide observability dashboards & alerts |

---

## OpenTelemetry Semantic Conventions for Gen AI

Use standardized attribute names for consistency across tools and platforms.

### Gen AI Request Attributes

- `gen_ai.system` - The AI system (e.g., "openai", "anthropic")
- `gen_ai.request.model` - Model identifier (e.g., "claude-3-sonnet")
- `gen_ai.request.temperature` - Sampling temperature
- `gen_ai.request.top_p` - Nucleus sampling parameter
- `gen_ai.request.max_tokens` - Maximum tokens to generate

### Gen AI Response Attributes

- `gen_ai.response.id` - Unique response identifier
- `gen_ai.response.model` - Actual model used
- `gen_ai.response.finish_reasons` - Why generation stopped
- `gen_ai.usage.input_tokens` - Prompt tokens
- `gen_ai.usage.output_tokens` - Completion tokens

### Vector DB Attributes

- `db.system` - Database type (e.g., "pinecone", "weaviate")
- `db.operation` - Operation type (e.g., "query", "upsert")
- `db.vector.query.top_k` - Number of results requested
- `db.vector.query.filter` - Query filters applied

---

## Implementation Checklist

### Initial Setup

- [ ] Choose instrumentation approach (auto vs. manual)
- [ ] Select telemetry backend (Jaeger, Prometheus, etc.)
- [ ] Define semantic conventions for your domain
- [ ] Set up telemetry collector infrastructure

### Instrumentation

- [ ] Add root span creation in orchestrator
- [ ] Instrument task executors with child spans
- [ ] Add model inference instrumentation
- [ ] Instrument external service calls
- [ ] Propagate context across boundaries

### Metrics & Logging

- [ ] Define key metrics to track
- [ ] Set up metric collection and aggregation
- [ ] Configure structured logging
- [ ] Add log correlation with traces

### Monitoring & Alerting

- [ ] Create dashboards for key metrics
- [ ] Set up alerts for failures and anomalies
- [ ] Define SLOs and error budgets
- [ ] Configure on-call rotation

### Optimization

- [ ] Review instrumentation overhead
- [ ] Optimize sampling rates
- [ ] Reduce cardinality of attributes
- [ ] Archive old telemetry data

---

## DT Platform Integration: LUMINA

For Deutsche Telekom implementations, integrate with the **LUMINA Platform** for agentic observability.

### LUMINA Capabilities

- OpenTelemetry-native support
- Agentic-specific dashboards and visualizations
- Trace correlation across agent workflows
- Metrics aggregation and alerting
- Log management with AI-specific context

### Integration Pattern

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure LUMINA as the telemetry backend
exporter = OTLPSpanExporter(
    endpoint="lumina.dt.com:4317",
    headers={"authorization": "Bearer <token>"}
)
```

### MARA Technology Blueprint Alignment

Per the MARA Technology Blueprint:

- **Standard:** OpenTelemetry (and possibly Open Inference)
- **Primary Platform:** LUMINA with support for Agentic Observability
- **Alternatives:** Arize, LangFuse (with OpenTelemetry)

### Additional DT Observability Tools

| Tool | Purpose | Status |
|------|---------|--------|
| LUMINA | Agentic observability | Under development |
| Arize | ML observability, evaluation | Available |
| LangFuse | LLM observability | Available |

---

## Best Practices

### Span Design

- Keep spans focused on a single operation
- Use descriptive span names (e.g., "agent.execute_retrieval_task")
- Add meaningful attributes for filtering and analysis
- Minimize span creation overhead

### Attribute Naming

- Follow OpenTelemetry semantic conventions
- Use dot notation for hierarchy (e.g., "agent.task.id")
- Avoid high-cardinality attributes in span names
- Sanitize sensitive data before logging

### Context Propagation

- Always propagate context to downstream services
- Use standard W3C headers for HTTP
- Extract context at service entry points
- Inject context before external calls

### Performance

- Use sampling for high-volume traces
- Batch telemetry exports
- Minimize attribute payload size
- Monitor instrumentation overhead (aim for <5%)

### Security

- Sanitize PII from logs and traces
- Secure telemetry transport (TLS)
- Implement access controls on telemetry data
- Audit telemetry access
