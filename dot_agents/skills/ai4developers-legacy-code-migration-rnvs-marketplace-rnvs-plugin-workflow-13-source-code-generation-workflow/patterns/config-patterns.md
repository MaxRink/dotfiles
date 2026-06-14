# Configuration Patterns

Patterns for Spring Boot configuration classes in VNRM microservices.

---

## Pattern 1: Feature Configuration Properties

Type-safe configuration using `@ConfigurationProperties`:

```java
package ${base_package}.config;

import jakarta.validation.constraints.*;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Configuration properties for ${feature_name}.
 * Implements: ${business_rule}
 *
 * @see application.yml for property values
 */
@Data
@Validated
@ConfigurationProperties(prefix = "${prefix}")
public class ${Feature}Properties {

    /**
     * Whether ${feature_name} is enabled.
     * Default: true
     */
    private boolean enabled = true;

    /**
     * Maximum number of retry attempts.
     * Default: 3
     */
    @Min(1)
    @Max(10)
    private int maxRetries = 3;

    /**
     * Timeout for external API calls.
     * Default: 30 seconds
     */
    @NotNull
    private Duration timeout = Duration.ofSeconds(30);

    /**
     * Batch size for bulk operations.
     * Default: 100
     */
    @Min(1)
    @Max(1000)
    private int batchSize = 100;

    /**
     * Cron expression for scheduled tasks.
     * Default: every hour
     */
    @NotBlank
    private String scheduleCron = "0 0 * * * *";

    /**
     * Nested configuration for sub-features.
     */
    private SubFeature subFeature = new SubFeature();

    @Data
    public static class SubFeature {
        private boolean enabled = true;
        private String endpoint;
        private Duration cacheExpiry = Duration.ofMinutes(5);
    }
}
```

**application.yml**:
```yaml
${prefix}:
  enabled: true
  max-retries: 3
  timeout: 30s
  batch-size: 100
  schedule-cron: "0 0 * * * *"
  sub-feature:
    enabled: true
    endpoint: https://api.example.com
    cache-expiry: 5m
```

---

## Pattern 2: Escalation Configuration

For SLA and escalation rules:

```java
package ${base_package}.config;

import jakarta.validation.constraints.*;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;

/**
 * Configuration for escalation workflow.
 * Implements: ${escalation_business_rule}
 */
@Data
@Validated
@ConfigurationProperties(prefix = "${module}.escalation")
public class EscalationProperties {

    /**
     * Whether auto-escalation is enabled.
     */
    private boolean autoEscalationEnabled = true;

    /**
     * Time before escalating to Level 1.
     */
    @NotNull
    private Duration level1Threshold = Duration.ofHours(24);

    /**
     * Time before escalating to Level 2.
     */
    @NotNull
    private Duration level2Threshold = Duration.ofHours(48);

    /**
     * Time before escalating to Level 3 (critical).
     */
    @NotNull
    private Duration level3Threshold = Duration.ofHours(72);

    /**
     * Cron expression for escalation check job.
     */
    @NotBlank
    private String checkCron = "0 0 * * * *";

    /**
     * Email recipients for each escalation level.
     */
    private List<String> level1Recipients = List.of();
    private List<String> level2Recipients = List.of();
    private List<String> level3Recipients = List.of();

    /**
     * Get threshold for given level.
     */
    public Duration getThresholdForLevel(int level) {
        return switch (level) {
            case 1 -> level1Threshold;
            case 2 -> level2Threshold;
            case 3 -> level3Threshold;
            default -> throw new IllegalArgumentException("Invalid escalation level: " + level);
        };
    }

    /**
     * Get recipients for given level.
     */
    public List<String> getRecipientsForLevel(int level) {
        return switch (level) {
            case 1 -> level1Recipients;
            case 2 -> level2Recipients;
            case 3 -> level3Recipients;
            default -> List.of();
        };
    }
}
```

**application.yml**:
```yaml
${module}:
  escalation:
    auto-escalation-enabled: true
    level1-threshold: 24h
    level2-threshold: 48h
    level3-threshold: 72h
    check-cron: "0 0 * * * *"
    level1-recipients:
      - team-lead@telekom.de
    level2-recipients:
      - manager@telekom.de
    level3-recipients:
      - director@telekom.de
```

---

## Pattern 3: Notification Configuration

For email/SMS notification settings:

```java
package ${base_package}.config;

import jakarta.validation.constraints.*;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Configuration for notification service.
 * Implements: ${notification_business_rule}
 */
@Data
@Validated
@ConfigurationProperties(prefix = "${module}.notification")
public class NotificationProperties {

    /**
     * Whether notifications are enabled.
     */
    private boolean enabled = true;

    /**
     * Sender email address.
     */
    @NotBlank
    @Email
    private String fromAddress;

    /**
     * Reply-to email address.
     */
    @Email
    private String replyToAddress;

    /**
     * Maximum retry attempts for failed notifications.
     */
    @Min(1)
    @Max(5)
    private int maxRetries = 3;

    /**
     * Delay between retry attempts.
     */
    @NotNull
    private Duration retryDelay = Duration.ofMinutes(1);

    /**
     * SLA for notification delivery.
     */
    @NotNull
    private Duration deliverySla = Duration.ofMinutes(5);

    /**
     * Email template location.
     */
    private String templatePath = "classpath:/templates/email/";

    /**
     * Whether to include stack traces in error notifications.
     */
    private boolean includeStackTrace = false;
}
```

---

## Pattern 4: External API Configuration

For external system integrations:

```java
package ${base_package}.config;

import jakarta.validation.constraints.*;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Configuration for ${external_system} API integration.
 * Implements: ${integration_business_rule}
 */
@Data
@Validated
@ConfigurationProperties(prefix = "${module}.${system}")
public class ${System}ApiProperties {

    /**
     * Base URL for the API.
     */
    @NotBlank
    private String baseUrl;

    /**
     * API key for authentication.
     */
    private String apiKey;

    /**
     * Connection timeout.
     */
    @NotNull
    private Duration connectTimeout = Duration.ofSeconds(10);

    /**
     * Read timeout.
     */
    @NotNull
    private Duration readTimeout = Duration.ofSeconds(30);

    /**
     * Maximum connections in pool.
     */
    @Min(1)
    @Max(100)
    private int maxConnections = 20;

    /**
     * Whether to use connection pooling.
     */
    private boolean connectionPoolEnabled = true;

    /**
     * Circuit breaker configuration.
     */
    private CircuitBreaker circuitBreaker = new CircuitBreaker();

    @Data
    public static class CircuitBreaker {
        private boolean enabled = true;
        private int failureRateThreshold = 50;
        private int minimumNumberOfCalls = 5;
        private Duration waitDurationInOpenState = Duration.ofSeconds(30);
        private int permittedNumberOfCallsInHalfOpenState = 2;
    }
}
```

---

## Pattern 5: Enable Configuration Properties

Main application class or configuration:

```java
package ${base_package}.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Enables type-safe configuration properties for ${module}.
 */
@Configuration
@EnableConfigurationProperties({
    ${Feature}Properties.class,
    EscalationProperties.class,
    NotificationProperties.class,
    ${System}ApiProperties.class
})
public class ${Module}PropertiesConfiguration {
    // Configuration properties are automatically bound
}
```

---

## Pattern 6: Conditional Bean Configuration

Beans created based on configuration:

```java
package ${base_package}.config;

import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Conditional configuration for ${feature}.
 */
@Configuration
@RequiredArgsConstructor
public class ${Feature}Configuration {

    private final ${Feature}Properties properties;

    /**
     * Create scheduler only if auto-escalation is enabled.
     */
    @Bean
    @ConditionalOnProperty(
            prefix = "${module}.escalation",
            name = "auto-escalation-enabled",
            havingValue = "true",
            matchIfMissing = true)
    public ${Feature}Scheduler ${feature}Scheduler(${Feature}Service service) {
        return new ${Feature}Scheduler(service, properties);
    }

    /**
     * Create circuit breaker only if enabled.
     */
    @Bean
    @ConditionalOnProperty(
            prefix = "${module}.${system}.circuit-breaker",
            name = "enabled",
            havingValue = "true",
            matchIfMissing = true)
    public io.github.resilience4j.circuitbreaker.CircuitBreaker ${system}CircuitBreaker() {
        return CircuitBreakerConfig.custom()
                .failureRateThreshold(properties.getCircuitBreaker().getFailureRateThreshold())
                .minimumNumberOfCalls(properties.getCircuitBreaker().getMinimumNumberOfCalls())
                .waitDurationInOpenState(properties.getCircuitBreaker().getWaitDurationInOpenState())
                .build();
    }
}
```

---

## Anti-Patterns to Avoid

1. **Don't hardcode values** - Use configuration properties
2. **Don't skip validation** - Use `@Validated` and constraints
3. **Don't use raw strings for Duration** - Use `Duration` type
4. **Don't forget defaults** - Provide sensible defaults
5. **Don't expose secrets** - Use environment variables or vaults
6. **Don't duplicate config** - Use nested classes for related settings
