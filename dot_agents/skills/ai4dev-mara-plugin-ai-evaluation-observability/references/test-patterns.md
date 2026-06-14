# Test Patterns for AI Agents

This reference provides comprehensive test patterns for validating AI agent functionality, integration, and safety. Use these patterns to ensure agents work
correctly, handle edge cases, and maintain quality standards.

## Unit Testing Patterns

Unit tests validate individual components and functions in isolation.

### Pattern 1: Prompt Template Logic Test

**What It Tests:** Correct formatting, logic conditions, and placeholders in prompt templates

**Key Metrics:**

- Test pass/fail
- Placeholder correctness
- Template coverage %

**Typical Use Case:** Ensuring deterministic behavior of prompt templates before LLM call

**Pass Criteria:** All prompts generate expected structured output

**Test Data Required:** Prompt templates with test variables

**Recommended Tools/Libraries:** pytest, LangChain TestKit, PromptLayer

**Test Stage:** Pre-deployment

**Example Test Scenario:**

```python
def test_prompt_template_formatting():
    template = "Hello {name}, your order {order_id} is ready."
    variables = {"name": "Alice", "order_id": "12345"}
    result = format_prompt(template, variables)
    assert result == "Hello Alice, your order 12345 is ready."
```

---

### Pattern 2: Utility Function Test

**What It Tests:** Core functions like token counting, string formatting, or memory retrieval

**Key Metrics:**

- Function accuracy
- Edge case coverage
- Runtime errors

**Typical Use Case:** Validating backend utilities used by agents

**Pass Criteria:** 100% unit test coverage, no exceptions raised

**Test Data Required:** Synthetic inputs for functions, edge cases

**Recommended Tools/Libraries:** pytest, unittest, coverage.py

**Test Stage:** Pre-deployment

**Example Test Scenarios:**

- Empty string inputs
- Maximum length inputs
- Special character handling
- Null/None handling
- Unicode character handling

---

## Integration Testing Patterns

Integration tests validate how components work together and interact with external systems.

### Pattern 1: LLM Endpoint Integration Test

**What It Tests:** Agent's ability to connect and send/receive to/from LLMs (OpenAI, Anthropic, etc.)

**Key Metrics:**

- API response time
- Error rate
- Schema validation

**Typical Use Case:** Verifying integration with LLM providers in staging

**Pass Criteria:** Valid response schema with <1% failure rate

**Test Data Required:** Valid and invalid LLM request/response samples

**Recommended Tools/Libraries:** Postman, LangSmith, FastAPI TestClient

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Successful API call with valid payload
- API call with invalid authentication
- API call with malformed request
- Timeout handling
- Rate limit handling
- Response schema validation

---

### Pattern 2: External API Chaining Test

**What It Tests:** Agent integration with external APIs (tools, plugins, retrievers)

**Key Metrics:**

- Success rate
- Response delay
- Error handling

**Typical Use Case:** Testing when agents query external knowledge or actions

**Pass Criteria:** API returns expected value within latency threshold

**Test Data Required:** External API mocks and test payloads

**Recommended Tools/Libraries:** Pact, WireMock, requests-mock

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Sequential API calls
- Parallel API calls
- API call failure and retry logic
- Partial response handling
- Data transformation between APIs

---

## Functional Testing Patterns

Functional tests validate end-to-end workflows and user-facing capabilities.

### Pattern 1: End-to-End Agent Task Test

**What It Tests:** Whether an agent completes a task successfully from prompt to final output

**Key Metrics:**

- Task success rate
- Response correctness
- Retry count

**Typical Use Case:** Simulating real user scenario across multiple steps

**Pass Criteria:** Success in at least 95% of defined flows

**Test Data Required:** Simulated user scenarios and success criteria

**Recommended Tools/Libraries:** LangSmith, Playwright, Selenium

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Happy path completion
- Multi-step workflows
- Context retention across steps
- Error recovery and retry
- Timeout handling

---

### Pattern 2: Memory Recall Consistency Test

**What It Tests:** If an agent can retrieve previously stored context or memory accurately

**Key Metrics:**

- Recall accuracy
- Memory hit/miss ratio

**Typical Use Case:** Testing agent with memory-enabled architecture

**Pass Criteria:** Recall must match stored values in 90%+ cases

**Test Data Required:** Memory-enabled agent conversation history

**Recommended Tools/Libraries:** LangChain Memory + TestKit, JSON comparison tools

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Short-term memory recall (within session)
- Long-term memory recall (across sessions)
- Memory priority and relevance
- Memory conflict resolution
- Memory size limits

---

## Regression Testing Patterns

Regression tests ensure new changes don't break existing functionality.

### Pattern 1: Version Output Diff Test

**What It Tests:** Compare output of current vs previous model or prompt version

**Key Metrics:**

- Delta in correctness
- Hallucination rate change

**Typical Use Case:** Before rolling out new agent version

**Pass Criteria:** No significant drop in quality or trust scores

**Test Data Required:** Output logs from current and previous versions

**Recommended Tools/Libraries:** Snapshot testing, LangTest, diff-match-patch

**Test Stage:** Pre-deployment

**Test Scenarios:**

- Output quality comparison
- Response time comparison
- Cost per request comparison
- Error rate comparison
- User satisfaction score comparison

---

## Guardrail Safety Testing Patterns

Safety tests validate that agents resist malicious inputs and avoid harmful outputs.

### Pattern 1: Jailbreak Prompt Resistance Test

**What It Tests:** Whether the agent can be tricked into unsafe or restricted behavior

**Key Metrics:**

- Jailbreak success rate
- Response severity
- Blocklist coverage

**Typical Use Case:** Testing safety filters against adversarial prompts

**Pass Criteria:** <1% jailbreak rate across known scenarios

**Test Data Required:** Jailbreak prompt sets, blocked query samples

**Recommended Tools/Libraries:** PromptBench, OpenAI Guardrails, RAIL, LlamaGuard

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Role-play jailbreak attempts
- Instruction injection attacks
- Prompt injection attacks
- System message override attempts
- Multi-turn manipulation attempts

---

### Pattern 2: Toxic Content Handling Test

**What It Tests:** Whether the agent avoids generating or echoing offensive content

**Key Metrics:**

- Toxicity score
- Moderation trigger rate

**Typical Use Case:** Evaluating content safety in open-ended generation

**Pass Criteria:** All responses below toxicity threshold (e.g., <0.2)

**Test Data Required:** Toxic phrases, prompt-response examples

**Recommended Tools/Libraries:** Perspective API, Detoxify, Anthropic filters

**Test Stage:** Pre & Post-deployment

**Test Scenarios:**

- Profanity filtering
- Hate speech detection
- Sexual content filtering
- Violence and gore filtering
- Personal attacks detection

---

## Test Pattern Selection Guide

### By Test Complexity

- **Simple/Quick:** Unit tests (Prompt Template, Utility Function)
- **Medium:** Integration tests (LLM Endpoint, API Chaining)
- **Complex/Slow:** Functional tests (End-to-End, Memory Recall)

### By Test Stage

- **Pre-deployment:** All unit tests, integration tests, regression tests, safety tests
- **Post-deployment:** Integration tests, functional tests, behavior monitoring

### By Risk Level

- **High Risk:** Safety tests, end-to-end tests, regression tests
- **Medium Risk:** Integration tests, functional tests
- **Low Risk:** Unit tests

### By Automation Level

- **Fully Automated:** Unit tests, integration tests with mocks
- **Partially Automated:** End-to-end tests, regression tests
- **Manual Required:** User experience evaluation, subjective quality assessment

---

## Test Data Requirements

### Essential Test Data

- **Valid inputs:** Typical user queries and requests
- **Invalid inputs:** Malformed, missing, or incorrect data
- **Edge cases:** Boundary conditions, extreme values
- **Ground truth:** Expected outputs for comparison

### Safety Test Data

- **Jailbreak prompts:** Known adversarial patterns
- **Toxic content:** Examples of harmful text
- **Policy violations:** Content that violates guidelines
- **Blocklists:** Known restricted terms and patterns

### Performance Test Data

- **Load profiles:** Different traffic patterns
- **Synthetic data:** Generated test cases at scale
- **Historical data:** Real production data (anonymized)

---

## Best Practices

### Test Coverage

- Aim for 80%+ code coverage for unit tests
- Include at least 5 edge cases per function
- Test both success and failure paths
- Validate error messages and status codes

### Test Automation

- Automate all regression tests
- Run tests on every code commit
- Set up CI/CD pipelines for test execution
- Monitor test execution time and optimize slow tests

### Test Maintenance

- Review and update tests quarterly
- Archive obsolete tests
- Document test intent and scenarios
- Refactor tests when production code changes

### Test Reporting

- Track test pass/fail rates over time
- Report on test coverage metrics
- Alert on test failures immediately
- Analyze failure patterns for insights
