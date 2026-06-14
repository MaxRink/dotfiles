# Dependency Delta Design Patterns

**Purpose**: Design patterns for service dependency changes in delta model (new_internal_dependencies).

**Context**: Phase 7.1 captures ONLY new service-to-service integrations added to existing microservice.

---

## New Internal Dependencies

### Requirements

Every dependency in `new_internal_dependencies` MUST include:

1. **Target Service**: Service being called
2. **Communication Pattern**: REST API (synchronous) or Kafka event (asynchronous)
3. **Purpose**: Business justification for dependency
4. **Resilience Patterns** (for REST): Circuit breaker, timeout, retry, fallback
5. **Service Discovery**: How to locate target service
6. **Authentication**: How to authenticate calls

### Template

```json
{
  "target_service": "service-name",
  "communication_pattern": "REST_API | KAFKA_EVENT",
  "purpose": "Business justification for this dependency",
  "service_discovery": {
    "method": "kubernetes_service | consul | eureka",
    "service_name": "service-name.namespace.svc.cluster.local"
  },
  "authentication": {
    "method": "JWT | mTLS | API_KEY",
    "details": "How authentication is performed"
  },
  "resilience": {
    "circuit_breaker": {},
    "timeout": {},
    "retry": {},
    "fallback": {}
  }
}
```

---

## REST API Dependencies (Synchronous)

### Complete Example: Portability Service → Carrier Registry

```json
{
  "target_service": "carrier-registry-service",
  "communication_pattern": "REST_API",
  "purpose": "Validate carrier existence and status before creating portability request. Retrieve carrier contact information for notifications.",
  "api_contract": {
    "base_url": "http://carrier-registry-service.common.svc.cluster.local:8080",
    "endpoints_used": [
      {
        "method": "GET",
        "path": "/carriers/{carrier_id}",
        "description": "Get carrier details by ID"
      },
      {
        "method": "GET",
        "path": "/carriers/{carrier_id}/status",
        "description": "Check if carrier is active and accepting portability requests"
      }
    ]
  },
  "service_discovery": {
    "method": "kubernetes_service",
    "service_name": "carrier-registry-service.common.svc.cluster.local",
    "port": 8080,
    "health_check_endpoint": "/actuator/health"
  },
  "authentication": {
    "method": "JWT",
    "token_source": "Service account token from Kubernetes",
    "scopes_required": ["carrier:read"],
    "header": "Authorization: Bearer {token}"
  },
  "resilience": {
    "circuit_breaker": {
      "implementation": "Resilience4j",
      "failure_rate_threshold": 50,
      "failure_rate_threshold_description": "Open circuit if 50% of calls fail",
      "wait_duration_in_open_state_seconds": 60,
      "permitted_calls_in_half_open_state": 3,
      "sliding_window_type": "COUNT_BASED",
      "sliding_window_size": 100,
      "minimum_number_of_calls": 10,
      "configuration": {
        "failureRateThreshold": 50,
        "waitDurationInOpenState": "60s",
        "permittedNumberOfCallsInHalfOpenState": 3,
        "slidingWindowSize": 100,
        "minimumNumberOfCalls": 10
      }
    },
    "timeout": {
      "connect_timeout_milliseconds": 2000,
      "read_timeout_milliseconds": 5000,
      "total_timeout_milliseconds": 5000,
      "rationale": "Carrier lookup is fast DB query, should complete under 1 second. 5 seconds allows for network latency."
    },
    "retry": {
      "max_attempts": 3,
      "wait_duration_milliseconds": 1000,
      "backoff_strategy": "exponential",
      "backoff_multiplier": 2,
      "retry_on_exceptions": ["ConnectException", "SocketTimeoutException", "HTTP_503_SERVICE_UNAVAILABLE"],
      "do_not_retry_on": ["HTTP_404_NOT_FOUND", "HTTP_400_BAD_REQUEST", "HTTP_401_UNAUTHORIZED"],
      "configuration": {
        "maxAttempts": 3,
        "waitDuration": "1s",
        "exponentialBackoffMultiplier": 2,
        "retryExceptions": ["java.net.ConnectException", "java.net.SocketTimeoutException"],
        "ignoreExceptions": ["feign.FeignException$NotFound"]
      }
    },
    "fallback": {
      "strategy": "cache",
      "implementation": "Return cached carrier data if available (cache TTL: 1 hour)",
      "cache_config": {
        "cache_name": "carrier_cache",
        "ttl_seconds": 3600,
        "max_entries": 1000
      },
      "degraded_mode": "If cache miss, return minimal carrier info with is_validated=false flag. Log warning for manual review."
    }
  },
  "monitoring": {
    "metrics": [
      "carrier_registry_calls_total (counter with result label: success|failure|timeout|circuit_open)",
      "carrier_registry_call_duration_seconds (histogram)",
      "carrier_registry_circuit_breaker_state (gauge: closed|open|half_open)"
    ],
    "alerts": [
      "Circuit breaker open for > 5 minutes → PagerDuty alert",
      "Error rate > 10% for 10 minutes → Slack notification"
    ]
  },
  "source": {
    "rnvs_equivalent": "Direct database query to CARRIERS table",
    "rnvs_file": "src/validation/CarrierValidator.java:45",
    "improvement": "VNRM uses service-to-service API for better encapsulation and resilience. RNVS direct DB access created coupling."
  },
  "dependency_justification": {
    "coupling_level": "LOW",
    "rationale": "Carrier validation is core business rule. Acceptable coupling.",
    "alternative_considered": "Event-driven eventual consistency rejected because portability requests need real-time carrier validation."
  }
}
```

---

## Kafka Event Dependencies (Asynchronous)

### Complete Example: Portability Service → Number Registry Events

```json
{
  "target_service": "number-registry-service",
  "communication_pattern": "KAFKA_EVENT",
  "purpose": "Subscribe to number ownership changes and allocation events to validate portability eligibility in real-time.",
  "event_subscription": {
    "topics_subscribed": [
      {
        "topic_name": "num.number-allocation.activated",
        "description": "Number activated by carrier (ownership established)",
        "consumer_group": "prt-portability-service.num.number-allocation.activated.sync",
        "processing_logic": "Update local number ownership cache for fast portability validation"
      },
      {
        "topic_name": "num.number-allocation.deactivated",
        "description": "Number deactivated or released",
        "consumer_group": "prt-portability-service.num.number-allocation.deactivated.sync",
        "processing_logic": "Mark number as ineligible for portability (no active owner)"
      }
    ]
  },
  "coupling_type": "EVENT_DRIVEN_LOOSE_COUPLING",
  "idempotency": {
    "method": "event_id deduplication",
    "processing_log_table": "event_processing_log"
  },
  "error_handling": {
    "retry_policy": "3 attempts with exponential backoff",
    "dead_letter_queue": "dlq.prt-portability-service.number-allocation-events"
  },
  "local_cache": {
    "cache_name": "number_ownership_cache",
    "ttl_seconds": 86400,
    "sync_strategy": "Event-driven + periodic full sync (daily 2am)"
  },
  "monitoring": {
    "metrics": [
      "number_registry_events_consumed_total (counter)",
      "number_registry_events_processing_duration_seconds (histogram)",
      "number_ownership_cache_hit_rate (gauge)"
    ]
  },
  "dependency_justification": {
    "coupling_level": "LOW",
    "rationale": "Event-driven subscription decouples services. Portability service doesn't need to know Number Registry internals.",
    "benefit": "Real-time number ownership updates without polling or tight coupling"
  }
}
```

---

## Resilience Patterns Deep Dive

### Circuit Breaker Pattern

**Purpose**: Prevent cascading failures when downstream service is unavailable

**States**:
1. **CLOSED**: Normal operation, requests pass through
2. **OPEN**: Downstream failing, requests immediately fail (no calls made)
3. **HALF_OPEN**: Testing if downstream recovered, limited requests allowed

**Configuration**:

```json
{
  "circuit_breaker": {
    "failure_rate_threshold": 50,
    "slow_call_rate_threshold": 100,
    "slow_call_duration_threshold_seconds": 5,
    "permitted_calls_in_half_open_state": 3,
    "sliding_window_type": "COUNT_BASED",
    "sliding_window_size": 100,
    "minimum_number_of_calls": 10,
    "wait_duration_in_open_state_seconds": 60,
    "automatic_transition_from_open_to_half_open": true
  }
}
```

**When to Use**:
- External service calls
- Database connections
- Third-party API calls

**When NOT to Use**:
- Internal in-memory operations
- Critical calls with no fallback (better to fail fast and alert)

---

### Timeout Pattern

**Purpose**: Prevent resource exhaustion from slow downstream services

**Timeout Types**:

1. **Connect Timeout**: Time to establish connection
2. **Read Timeout**: Time to receive response after connection
3. **Total Timeout**: Overall request timeout (connect + read + processing)

**Configuration**:

```json
{
  "timeout": {
    "connect_timeout_milliseconds": 2000,
    "read_timeout_milliseconds": 5000,
    "total_timeout_milliseconds": 5000
  }
}
```

**Best Practices**:
- Set realistic timeouts based on SLA (Service Level Agreement)
- Connect timeout: 1-2 seconds (network should be fast)
- Read timeout: Based on downstream operation (DB query: 1-5s, complex calc: 10-30s)
- Total timeout: Slightly higher than read timeout

---

### Retry Pattern

**Purpose**: Recover from transient failures automatically

**Retry Strategy**:

1. **Fixed Delay**: Wait same time between retries
2. **Exponential Backoff**: Increase wait time exponentially (1s, 2s, 4s, 8s)
3. **Random Jitter**: Add randomness to prevent thundering herd

**Configuration**:

```json
{
  "retry": {
    "max_attempts": 3,
    "wait_duration_milliseconds": 1000,
    "backoff_strategy": "exponential",
    "backoff_multiplier": 2,
    "max_wait_duration_milliseconds": 10000,
    "retry_on_exceptions": [
      "ConnectException",
      "SocketTimeoutException",
      "HTTP_503_SERVICE_UNAVAILABLE",
      "HTTP_502_BAD_GATEWAY",
      "HTTP_504_GATEWAY_TIMEOUT"
    ],
    "do_not_retry_on": [
      "HTTP_400_BAD_REQUEST",
      "HTTP_401_UNAUTHORIZED",
      "HTTP_403_FORBIDDEN",
      "HTTP_404_NOT_FOUND"
    ]
  }
}
```

**Idempotency Requirement**:
- **CRITICAL**: Only retry idempotent operations (GET, PUT, DELETE)
- Do NOT retry non-idempotent operations (POST) without idempotency keys
- Use idempotency keys for POST retries (e.g., `Idempotency-Key: {uuid}`)

---

### Fallback Pattern

**Purpose**: Provide degraded functionality when primary path fails

**Fallback Strategies**:

1. **Cache**: Return cached data
2. **Default Value**: Return safe default
3. **Alternative Service**: Call backup service
4. **Graceful Degradation**: Return partial data with warning
5. **Fail Silent**: Return empty result (use cautiously)
6. **Fail Fast**: Throw exception immediately (for critical paths)

**Examples**:

```json
{
  "fallback_strategies": [
    {
      "strategy": "cache",
      "implementation": "Return cached carrier data if API call fails",
      "cache_ttl_seconds": 3600,
      "staleness_acceptable": true,
      "staleness_max_age_hours": 24
    },
    {
      "strategy": "default_value",
      "implementation": "Return carrier with status='UNKNOWN' for non-critical validations",
      "use_case": "Display carrier name in UI (not critical, show 'Unknown Carrier')"
    },
    {
      "strategy": "graceful_degradation",
      "implementation": "Return portability request with is_fully_validated=false flag",
      "impact": "Allow request creation but mark for manual review"
    },
    {
      "strategy": "alternative_service",
      "implementation": "Call backup carrier registry if primary fails",
      "backup_service_url": "http://carrier-registry-backup.common.svc.cluster.local"
    }
  ]
}
```

---

## Best Practices

### Dependency Design

✅ **DO**: Minimize dependencies (favor events over direct calls)
✅ **DO**: Add resilience patterns to all REST API dependencies
✅ **DO**: Use service discovery (not hardcoded IPs)
✅ **DO**: Implement circuit breakers for external services
✅ **DO**: Cache frequently-accessed data

❌ **DON'T**: Create circular dependencies (A → B → A)
❌ **DON'T**: Skip timeouts (causes resource exhaustion)
❌ **DON'T**: Retry non-idempotent operations without idempotency keys
❌ **DON'T**: Call multiple services synchronously (use async/events)
❌ **DON'T**: Ignore circuit breaker state in monitoring

### Resilience Configuration

**Timeouts**:
- Internal service: 1-5 seconds
- External API: 10-30 seconds
- Database: 1-3 seconds
- Cache: 100-500 milliseconds

**Circuit Breaker**:
- Failure threshold: 50% (open if half of calls fail)
- Wait duration: 30-60 seconds (test recovery after 1 minute)
- Sliding window: 50-100 calls (need statistical significance)

**Retry**:
- Max attempts: 2-3 (balance between recovery and latency)
- Backoff: Exponential (prevent thundering herd)
- Only retry transient errors (5xx, network issues)

### Monitoring and Alerting

**Key Metrics**:
- Dependency call count (total, success, failure)
- Dependency call duration (p50, p95, p99)
- Circuit breaker state (closed/open/half-open)
- Fallback invocation count
- Timeout count
- Retry count

**Alerts**:
- Circuit breaker open > 5 minutes
- Error rate > 10% for 10 minutes
- p99 latency > timeout threshold
- Fallback usage > 5% of requests

---

## Dependency Mapping

**Internal Dependencies** (VNRM to VNRM):
```
prt-portability → carrier-registry (validate carriers)
prt-portability → number-registry (verify number ownership)
prt-portability → notification-service (send carrier notifications)
```

**External Dependencies** (VNRM to external systems):
```
prt-portability → BNetzA API (regulatory compliance checks)
prt-portability → MNP-DB (Mobile Number Portability Database)
prt-portability → CRM-T (customer data lookup)
```

**Coupling Levels**:
- **LOW**: Event-driven, async, cached
- **MEDIUM**: REST API with resilience patterns
- **HIGH**: Synchronous, no fallback, critical path (avoid!)

---

## Testing Dependencies

**Unit Tests**:
- Mock dependencies
- Test circuit breaker state transitions
- Test timeout handling
- Test retry logic

**Integration Tests**:
- Call real dependency in test environment
- Test idempotency
- Test error scenarios (500, timeout, connection refused)

**Contract Tests** (Pact, Spring Cloud Contract):
- Verify API contract compatibility
- Ensure breaking changes are detected

**Chaos Engineering**:
- Inject failures (kill dependency, add latency)
- Verify resilience patterns work
- Measure blast radius

---

## Related Patterns

- See `api-delta-patterns.md` for APIs that call dependencies
- See `event-delta-patterns.md` for event-driven dependencies
- See `../examples/` for complete dependency configuration examples

---

**Use these patterns to ensure resilient, maintainable service dependencies in your delta model.**
