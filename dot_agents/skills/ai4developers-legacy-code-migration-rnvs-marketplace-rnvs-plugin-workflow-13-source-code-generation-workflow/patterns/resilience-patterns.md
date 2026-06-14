# Resilience Patterns

Patterns for Resilience4j circuit breakers, retries, and rate limiting in VNRM microservices.

---

## Pattern 1: Circuit Breaker on External Service

Standard circuit breaker for external API calls:

```java
package ${base_package}.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.timelimiter.annotation.TimeLimiter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;

/**
 * Service for ${external_system} integration with circuit breaker protection.
 * Implements: ${business_rule_ids}
 * RNVS Source: ${rnvs_source}
 *
 * Tested by: ${Service}Test
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ${ExternalSystem}IntegrationService {

    private final ${ExternalSystem}Client client;
    private final ${ExternalSystem}FallbackHandler fallbackHandler;

    /**
     * Call ${external_system} with circuit breaker and retry.
     * Implements: ${business_rule}
     * Tested by: ${Service}Test.shouldCall${ExternalSystem}WithCircuitBreaker()
     *
     * Circuit Breaker: Opens after 50% failure rate (5 calls minimum)
     * Retry: 3 attempts with exponential backoff
     * Timeout: 10 seconds
     */
    @CircuitBreaker(name = "${externalSystem}", fallbackMethod = "handleFallback")
    @Retry(name = "${externalSystem}", fallbackMethod = "handleRetryExhausted")
    @TimeLimiter(name = "${externalSystem}")
    public CompletableFuture<${ResponseType}> call${ExternalSystem}(${RequestType} request) {
        log.info("Calling ${external_system} with request: {}", request.getId());

        return CompletableFuture.supplyAsync(() -> {
            try {
                ${ResponseType} response = client.execute(request);
                log.info("${ExternalSystem} call successful: {}", response.getStatus());
                return response;
            } catch (Exception e) {
                log.error("${ExternalSystem} call failed: {}", e.getMessage());
                throw e;
            }
        });
    }

    /**
     * Fallback when circuit breaker is open.
     */
    private CompletableFuture<${ResponseType}> handleFallback(
            ${RequestType} request,
            Throwable throwable) {
        log.warn("Circuit breaker open for ${external_system}, using fallback. Error: {}",
                throwable.getMessage());
        return CompletableFuture.completedFuture(
                fallbackHandler.handleCircuitBreakerOpen(request, throwable));
    }

    /**
     * Fallback when all retries are exhausted.
     */
    private CompletableFuture<${ResponseType}> handleRetryExhausted(
            ${RequestType} request,
            Throwable throwable) {
        log.error("All retries exhausted for ${external_system} call. Error: {}",
                throwable.getMessage());
        return CompletableFuture.completedFuture(
                fallbackHandler.handleRetryExhausted(request, throwable));
    }
}
```

---

## Pattern 2: Synchronous Circuit Breaker

For synchronous operations:

```java
package ${base_package}.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Service with synchronous circuit breaker.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ${Resource}SyncService {

    private final ${External}Client externalClient;

    /**
     * Sync ${resource} with external system.
     * Implements: ${business_rule}
     * Tested by: ${Service}Test.shouldSyncWithCircuitBreaker()
     */
    @CircuitBreaker(name = "sync", fallbackMethod = "syncFallback")
    @Retry(name = "sync")
    @Cacheable(value = "syncCache", key = "#resourceId", unless = "#result == null")
    public ${SyncResult} syncResource(Long resourceId) {
        log.info("Syncing resource: {}", resourceId);

        ${ExternalData} externalData = externalClient.fetchData(resourceId);

        // Process and return result
        return ${SyncResult}.builder()
                .resourceId(resourceId)
                .externalReference(externalData.getReference())
                .syncedAt(Instant.now())
                .status(SyncStatus.SUCCESS)
                .build();
    }

    /**
     * Fallback for sync operation.
     */
    private ${SyncResult} syncFallback(Long resourceId, Throwable throwable) {
        log.warn("Sync fallback triggered for resource {}: {}",
                resourceId, throwable.getMessage());

        return ${SyncResult}.builder()
                .resourceId(resourceId)
                .syncedAt(Instant.now())
                .status(SyncStatus.DEFERRED)
                .errorMessage(throwable.getMessage())
                .build();
    }
}
```

---

## Pattern 3: Fallback Handler

Dedicated fallback handler service:

```java
package ${base_package}.resilience;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * Fallback handler for ${external_system} integration.
 * Provides graceful degradation when circuit breaker is open.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ${ExternalSystem}FallbackHandler {

    private final ${FallbackRepository} fallbackRepository;
    private final ${NotificationService} notificationService;

    /**
     * Handle circuit breaker open state.
     * Returns cached response or queues request for later processing.
     */
    public ${ResponseType} handleCircuitBreakerOpen(
            ${RequestType} request,
            Throwable throwable) {
        log.warn("Circuit breaker open, attempting fallback for: {}", request.getId());

        // Strategy 1: Try to return cached response
        Optional<${ResponseType}> cached = fallbackRepository
                .findCachedResponse(request.getId());

        if (cached.isPresent()) {
            log.info("Returning cached response for: {}", request.getId());
            return cached.get().withStale(true);
        }

        // Strategy 2: Queue for later processing
        fallbackRepository.queueForRetry(request);

        // Strategy 3: Notify operations team
        notificationService.notifyCircuitBreakerOpen("${externalSystem}", throwable);

        // Return degraded response
        return ${ResponseType}.degraded()
                .withMessage("Service temporarily unavailable, request queued")
                .withRetryAfter(Duration.ofMinutes(5))
                .build();
    }

    /**
     * Handle retry exhaustion.
     */
    public ${ResponseType} handleRetryExhausted(
            ${RequestType} request,
            Throwable throwable) {
        log.error("Retry exhausted for: {}", request.getId());

        // Queue for manual processing
        fallbackRepository.queueForManualReview(request, throwable);

        return ${ResponseType}.failed()
                .withMessage("Request failed after maximum retries")
                .withErrorCode("RETRY_EXHAUSTED")
                .build();
    }
}
```

---

## Pattern 4: Circuit Breaker Registry Configuration

Programmatic circuit breaker configuration:

```java
package ${base_package}.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import io.github.resilience4j.retry.RetryRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;
import java.net.ConnectException;
import java.net.SocketTimeoutException;

/**
 * Resilience4j configuration for ${module}.
 */
@Configuration
public class ResilienceConfig {

    /**
     * Custom circuit breaker registry with module-specific configuration.
     */
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig defaultConfig = CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .slidingWindowSize(10)
                .minimumNumberOfCalls(5)
                .permittedNumberOfCallsInHalfOpenState(3)
                .automaticTransitionFromOpenToHalfOpenEnabled(true)
                .recordExceptions(
                        ConnectException.class,
                        SocketTimeoutException.class,
                        ${ExternalSystem}ConnectionException.class)
                .ignoreExceptions(
                        ${ValidationException}.class,
                        ${NotFoundException}.class)
                .build();

        // Stricter config for critical services
        CircuitBreakerConfig criticalConfig = CircuitBreakerConfig.custom()
                .failureRateThreshold(30)
                .waitDurationInOpenState(Duration.ofMinutes(1))
                .slidingWindowSize(20)
                .minimumNumberOfCalls(10)
                .build();

        return CircuitBreakerRegistry.of(defaultConfig)
                .addConfiguration("critical", criticalConfig);
    }

    /**
     * Custom retry registry.
     */
    @Bean
    public RetryRegistry retryRegistry() {
        RetryConfig defaultConfig = RetryConfig.custom()
                .maxAttempts(3)
                .waitDuration(Duration.ofSeconds(1))
                .exponentialBackoffMultiplier(2)
                .retryExceptions(
                        ConnectException.class,
                        SocketTimeoutException.class)
                .ignoreExceptions(
                        ${ValidationException}.class)
                .build();

        return RetryRegistry.of(defaultConfig);
    }

    /**
     * Create named circuit breaker for ${external_system}.
     */
    @Bean
    public CircuitBreaker ${externalSystem}CircuitBreaker(
            CircuitBreakerRegistry registry) {
        return registry.circuitBreaker("${externalSystem}");
    }

    /**
     * Create named retry for ${external_system}.
     */
    @Bean
    public Retry ${externalSystem}Retry(RetryRegistry registry) {
        return registry.retry("${externalSystem}");
    }
}
```

---

## Pattern 5: Health Indicator

Custom health indicator for circuit breaker status:

```java
package ${base_package}.health;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * Health indicator for circuit breaker status.
 */
@Component
public class CircuitBreakerHealthIndicator implements HealthIndicator {

    private final CircuitBreakerRegistry registry;

    public CircuitBreakerHealthIndicator(CircuitBreakerRegistry registry) {
        this.registry = registry;
    }

    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();
        boolean allHealthy = true;

        for (CircuitBreaker cb : registry.getAllCircuitBreakers()) {
            CircuitBreaker.State state = cb.getState();
            details.put(cb.getName(), Map.of(
                    "state", state.name(),
                    "failureRate", cb.getMetrics().getFailureRate(),
                    "bufferedCalls", cb.getMetrics().getNumberOfBufferedCalls(),
                    "failedCalls", cb.getMetrics().getNumberOfFailedCalls()
            ));

            if (state == CircuitBreaker.State.OPEN) {
                allHealthy = false;
            }
        }

        if (allHealthy) {
            return Health.up().withDetails(details).build();
        } else {
            return Health.down()
                    .withDetail("message", "One or more circuit breakers are open")
                    .withDetails(details)
                    .build();
        }
    }
}
```

---

## Application.yml Configuration Reference

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        register-health-indicator: true
        sliding-window-type: COUNT_BASED
        sliding-window-size: 10
        minimum-number-of-calls: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
        record-exceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
          - ${package}.exception.ConnectionException
        ignore-exceptions:
          - ${package}.exception.ValidationException
    instances:
      ${service-name}:
        base-config: default
        failure-rate-threshold: 50

  retry:
    configs:
      default:
        max-attempts: 3
        wait-duration: 1s
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2
    instances:
      ${service-name}:
        base-config: default

  timelimiter:
    configs:
      default:
        timeout-duration: 10s
        cancel-running-future: true
    instances:
      ${service-name}:
        base-config: default
```

---

## Anti-Patterns to Avoid

1. **Don't ignore all exceptions** - Only ignore non-transient exceptions
2. **Don't use same config for all services** - Tune per service characteristics
3. **Don't skip fallback methods** - Always provide graceful degradation
4. **Don't forget to log** - Log circuit breaker state changes
5. **Don't use blocking calls with TimeLimiter** - Use CompletableFuture
6. **Don't skip health indicators** - Essential for monitoring
