# Evaluation Patterns for AI Agents

This reference provides comprehensive evaluation patterns for systematically assessing the performance, reliability, and trustworthiness of AI agents. These patterns cover both objective metrics.

## Core Evaluation Patterns

### 1. Task Success Rate (End-to-End)

**Purpose:** Assess overall utility and reliability of the agent

**What It Measures:** Percentage of workflows completed correctly without escalation or human intervention

**Typical Use Cases:**

- End-to-end task automation
- Customer support flows
- Workflow completion

**Scoring Rubric:**

- **High:** ≥90% success
- **Medium:** 70–89%
- **Low:** <70%

---

### 2. F1 Score / Precision & Recall

**Purpose:** Balance correctness and completeness in classification tasks

**What It Measures:**

- Precision (correct positives)
- Recall (coverage of actual positives)
- F1 (harmonic mean of both)

**Typical Use Cases:**

- Intent classification
- Entity extraction
- Decision-making accuracy

**Scoring Rubric:**

- **High:** F1 ≥0.85
- **Medium:** 0.70–0.84
- **Low:** <0.70

---

### 3. Retrieval Accuracy

**Purpose:** Ensure correctness of retrieved knowledge

**What It Measures:** Percentage of correct documents, facts, or evidence retrieved compared to ground truth

**Typical Use Cases:**

- Retrieval-Augmented Generation (RAG)
- Knowledge base queries
- Fact retrieval

**Scoring Rubric:**

- **High:** ≥85% correct retrieval
- **Medium:** 65–84%
- **Low:** <65%

---

### 4. Semantic Similarity

**Purpose:** Capture meaning alignment beyond exact words

**What It Measures:** Embedding-based cosine similarity between generated output and reference output

**Typical Use Cases:**

- Summarization
- Paraphrasing
- Translation
- Answer quality checks

**Scoring Rubric:**

- **High:** ≥0.85 similarity
- **Medium:** 0.70–0.84
- **Low:** <0.70

---

### 5. LLM as Judge

**Purpose:** Scale human-like judgment for subjective evaluation

**What It Measures:** Comparison of outputs against gold standards or preferences using an LLM

**Typical Use Cases:**

- Clarity assessment
- Helpfulness evaluation
- Reasoning soundness
- Style compliance
- Subjective quality review

**Scoring Rubric:**

- **High:** ≥4/5 average rating
- **Medium:** 3–3.9
- **Low:** <3

---

### 6. Bias Detection (via Confusion Matrices)

**Purpose:** Identify systematic unfairness across groups

**What It Measures:** Distribution of false positives/negatives across user cohorts

**Typical Use Cases:**

- Fairness testing
- Demographic bias detection
- Regulatory compliance

**Scoring Rubric:**

- **Good:** <5% variance across groups
- **Medium:** 5–15% variance
- **Poor:** >15% variance

---

### 7. Hallucination Rate

**Purpose:** Track factual correctness and trustworthiness

**What It Measures:** Frequency of unsupported or incorrect claims in agent responses

**Typical Use Cases:**

- Factual QA
- Knowledge-grounded tasks
- Compliance-heavy use cases

**Scoring Rubric:**

- **Good:** <5% hallucination
- **Acceptable:** 5–10%
- **Poor:** >10%

---

### 8. Calibration Error (Confidence vs Accuracy)

**Purpose:** Measure reliability of agent confidence

**What It Measures:** Difference between predicted confidence scores and actual correctness

**Typical Use Cases:**

- Risk-sensitive workflows
- Decision support
- Safety-critical applications

**Scoring Rubric:**

- **Well-calibrated:** Error ≤5%
- **Moderate:** 6–15%
- **Poor:** >15%

---

## Technical Evaluation Patterns

| # | Pattern Title | Purpose | Key Metrics | What It Measures | Typical Use Case | Scoring Rubric | Required Data | Recommended Tools | Evaluation Stage |
|---|--------------|---------|-------------|-----------------|------------------|----------------|---------------|-------------------|------------------|
| 1 | Scalability Evaluation | Ensure the platform can handle increased load and grow smoothly | Throughput, Latency, CPU/GPU usage, Autoscaling success rate | How well the system scales with more users or data | When anticipating higher traffic or larger workloads | High: Handles large scale with <10% degradation. Medium: 10-25% degradation. Low: >25% degradation | Synthetic load data, performance logs | Locust, JMeter, Kubernetes HPA | Pre-deployment & Post |
| 2 | Integration Robustness | Ensure smooth and reliable integration with external services | Error rate, Retry count, Timeout %, Integration latency | Reliability and stability of third-party integrations | Connecting to APIs, databases, or external systems | High: Rare integration issues. Medium: Occasional minor issues. Low: Frequent integration failures | API call logs, integration health checks | Postman, Pact, WireMock | Pre & Post |
| 3 | Reliability & Availability | Ensure the platform is consistently available and reliable | Uptime %, MTTR, Incident frequency, SLA compliance | Uptime and ability to recover from failures | Critical services needing high availability | High: >99.9% uptime. Medium: 99-99.9%. Low: <99% uptime | Uptime monitoring logs, incident reports | Prometheus, Grafana, Sentry | Post |
| 4 | Performance Bottleneck | Identify and resolve performance bottlenecks in the platform | Latency, Queue size, Timeout rate, Resource utilization | Response times, latency, and throughput under load | Optimizing for speed and user experience | High: Minimal bottlenecks. Medium: Occasional slowdowns. Low: Frequent performance issues | Latency traces, CPU/memory usage | Jaeger, New Relic, Datadog | Pre & Post |
| 5 | Deployment Consistency | Ensure consistent behavior across different deployment environments | Config drift %, Test pass rate, Log/trace differences | Configuration drift and environment consistency | Deploying across dev, test, and production | High: Minimal discrepancies. Medium: Some differences. Low: Frequent inconsistencies | Config snapshots across environments | Terraform drift detection, diff tools | Pre |

---

## Functional Evaluation Patterns

| # | Pattern Title | Purpose | Key Metrics | Typical Use Case | Scoring Rubric | Required Data | Recommended Tools | Evaluation Stage |
|---|--------------|---------|-------------|-----------------|----------------|---------------|-------------------|------------------|
| 1 | User Experience Evaluation | Ensure users find the system easy, clear, and helpful | Task Completion Rate, CSAT, Sentiment Score, Confusion Events, Talk Ratio | Launching user-facing features or interfaces | High: Clear, fast, no confusion. Medium: Some confusion. Low: Frustrating UX | User session recordings, feedback forms | Hotjar, FullStory, UXCam, surveys | Post |
| 2 | Functional Capability Evaluation | Check if system features work correctly and meet intended needs | Feature success rate, Error rate, Task success rate, Instruction-following | Testing if users can complete goals using the system | High: Features fully work. Medium: Minor bugs. Low: Frequent failures | Task completion logs, feature usage data | Playwright, Selenium, LangChain TestKit | Pre & Post |

---

## Model Evaluation Patterns

| # | Pattern Title | Purpose | Key Metrics | Typical Use Case | Scoring Rubric | Required Data | Recommended Tools | Evaluation Stage |
|---|--------------|---------|-------------|-----------------|----------------|---------------|-------------------|------------------|
| 1 | Model Accuracy Evaluation | Measure how correct the model's predictions are | Accuracy, Precision/Recall, F1 Score, Hallucination Rate | Model validation before deployment | High: >90% accuracy. Medium: 70–90%. Low: <70% | Labeled test dataset, evaluation scripts | Sklearn, HuggingFace Eval, LLM-as-a-judge | Pre |
| 2 | Model Stability Evaluation | Check if model performs consistently over time or across contexts | Cross-dataset accuracy, Confidence variance, Drift over time | Periodic re-evaluation or after fine-tuning | High: Stable across contexts. Medium: Some variation. Low: Unstable | Multiple datasets over time, inference logs | Evidently, Alibi Detect, WandB | Pre & Post |
| 3 | User Feedback Integration | Incorporate human/user signals into model evaluation | CSAT, Feedback comments, Empathy Score, Responsiveness | Interactive AI (chatbots, copilots) | High: Positive feedback. Medium: Mixed. Low: Negative/low engagement | User feedback, CSAT scores, human ratings | Google Forms, LangSmith, Feedback APIs | Post |
| 4 | Model Behavior Monitoring | Monitor live model behavior in production | Drift detection, Hallucination rate, Latency, Outlier %, Instruction-following, Interruptions, Voice Clarity | Production monitoring and alerting | High: Stable, no alerts. Medium: Minor drift. Low: Frequent failures | Live traffic logs, drift stats, alert data | Arize, Fiddler, Seldon Core, Prometheus | Post |

---

## Model Accuracy Evaluation Pattern (Detailed)

**Description:** This pattern provides a structured approach to evaluate the accuracy of AI models using standard metrics like precision, recall, and
F1-score.
It helps ensure that the model's predictions are consistently measured and compared across different datasets and conditions.

**Key Points:**

- Standardizes the metrics used to evaluate model performance
- Ensures repeatable and consistent evaluation across different runs
- Facilitates comparison between multiple models and versions

**Problem:** Without a standardized evaluation method, it's difficult to reliably measure and compare the accuracy of AI models.
Different teams might use different metrics or inconsistent datasets, leading to unclear or incomparable results.

**Solution:** By applying this pattern, every evaluation cycle uses the same set of metrics and follows a consistent process.
Each model's performance is logged and traced in a uniform way, making it easier to identify which models are more accurate and under what conditions.

**Structure and Participants:**

- **Evaluation Coordinator:** Sets up the evaluation criteria and metrics
- **Data Collector:** Gathers the test datasets and ensures they're consistent
- **Metrics Calculator:** Computes precision, recall, F1-score, and other relevant metrics
- **Result Logger:** Records the evaluation results in a standardized format for future comparison

---

## Quality Metrics Definitions

### Performance Metrics

- **Throughput (RPS/TPS):** Number of requests/tasks processed per second
- **Latency:** Time taken to complete a request or task
- **p90/p95/p99 Latency:** 90th/95th/99th percentile latency values

### Accuracy Metrics

- **Precision:** Ratio of correct positive predictions to total positive predictions
- **Recall:** Ratio of correct positive predictions to total actual positives
- **F1 Score:** Harmonic mean of precision and recall

### Quality Metrics

- **CSAT (Customer Satisfaction Score):** User satisfaction rating
- **Sentiment Score:** Emotional tone of user feedback
- **Confusion Events:** Instances where users struggled or became confused
- **Task Completion Rate:** Percentage of tasks successfully completed

### Reliability Metrics

- **Uptime %:** Percentage of time the system is operational
- **MTTR (Mean Time To Recovery):** Average time to recover from failures
- **Error Rate:** Percentage of requests that result in errors
- **Retry Count:** Number of retries needed for successful completion

### Resource Metrics

- **CPU/GPU Utilization:** Percentage of compute resources used
- **Memory Usage:** Amount of memory consumed
- **Token Usage:** Number of prompt and completion tokens used
- **Cost per Request:** Financial cost per API call or operation

---

## DT Platform Integration

### Onix Evaluation Suite

For Deutsche Telekom implementations, the **Onix Evaluation Suite** provides integrated evaluation capabilities.

**Status:** Under development (Ready Q1 2026)

**Planned Capabilities:**

- Performance benchmarking
- Quality assessment
- Behavioral validation
- Business metric tracking

### Onix Test Automation Module

**Status:** Under development (Ready Q1 2026)

**Planned Capabilities:**

- Golden dataset creation
- Test case management
- Automated testing pipelines
- Regression testing

### Alternative Tools (per MARA Technology Blueprint)

| Tool | Purpose | Status |
|------|---------|--------|
| DeepEval | Evaluation framework | Available |
| Arize | ML observability, evaluation | Available |
| Cekura | Testing | Available |
| Label Studio | Annotation | Available |
| Argilla | Annotation | Available |

### DeepEval Integration Example

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase

# Define metrics
relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
hallucination_metric = HallucinationMetric(threshold=0.5)

# Create test case
test_case = LLMTestCase(
    input="What is the TARDIS MCP Gateway?",
    actual_output=agent_response,
    expected_output="The TARDIS MCP Gateway is DT's mandatory enterprise MCP implementation.",
    context=["MARA Technology Blueprint documentation"]
)

# Run evaluation
evaluate([test_case], [relevancy_metric, hallucination_metric])
```
