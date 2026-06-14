# Exception Patterns

Patterns for custom business exceptions in VNRM microservices.

---

## Pattern 1: Resource Not Found Exception

Standard 404 exception:

```java
package ${base_package}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Thrown when ${resource_name} is not found.
 */
@ResponseStatus(HttpStatus.NOT_FOUND)
public class ${Resource}NotFoundException extends RuntimeException {

    private final Long ${resource}Id;

    public ${Resource}NotFoundException(Long ${resource}Id) {
        super("${Resource} not found with id: " + ${resource}Id);
        this.${resource}Id = ${resource}Id;
    }

    public ${Resource}NotFoundException(String identifier) {
        super("${Resource} not found: " + identifier);
        this.${resource}Id = null;
    }

    public Long get${Resource}Id() {
        return ${resource}Id;
    }
}
```

---

## Pattern 2: Invalid State Transition Exception

For workflow/state machine violations:

```java
package ${base_package}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Thrown when an invalid status transition is attempted.
 * Implements: ${state_machine_business_rule}
 */
@ResponseStatus(HttpStatus.BAD_REQUEST)
public class InvalidStatusTransitionException extends RuntimeException {

    private final String currentStatus;
    private final String targetStatus;
    private final Long entityId;

    public InvalidStatusTransitionException(String currentStatus, String targetStatus) {
        super(String.format("Invalid status transition from %s to %s", currentStatus, targetStatus));
        this.currentStatus = currentStatus;
        this.targetStatus = targetStatus;
        this.entityId = null;
    }

    public InvalidStatusTransitionException(Long entityId, String currentStatus, String targetStatus) {
        super(String.format("Invalid status transition for entity %d: %s -> %s",
                entityId, currentStatus, targetStatus));
        this.entityId = entityId;
        this.currentStatus = currentStatus;
        this.targetStatus = targetStatus;
    }

    public String getCurrentStatus() {
        return currentStatus;
    }

    public String getTargetStatus() {
        return targetStatus;
    }

    public Long getEntityId() {
        return entityId;
    }
}
```

---

## Pattern 3: External Service Connection Exception

For external API connection failures:

```java
package ${base_package}.exception;

/**
 * Thrown when connection to ${external_system} fails.
 */
public class ${System}ConnectionException extends RuntimeException {

    private final String systemName;
    private final String endpoint;
    private final boolean retryable;

    public ${System}ConnectionException(String message) {
        super(message);
        this.systemName = "${System}";
        this.endpoint = null;
        this.retryable = true;
    }

    public ${System}ConnectionException(String endpoint, String message) {
        super(String.format("Connection to %s failed: %s", endpoint, message));
        this.systemName = "${System}";
        this.endpoint = endpoint;
        this.retryable = true;
    }

    public ${System}ConnectionException(String endpoint, Throwable cause) {
        super(String.format("Connection to %s failed: %s", endpoint, cause.getMessage()), cause);
        this.systemName = "${System}";
        this.endpoint = endpoint;
        this.retryable = true;
    }

    public String getSystemName() {
        return systemName;
    }

    public String getEndpoint() {
        return endpoint;
    }

    public boolean isRetryable() {
        return retryable;
    }
}
```

---

## Pattern 4: External Service Timeout Exception

For external API timeout failures:

```java
package ${base_package}.exception;

import java.time.Duration;

/**
 * Thrown when ${external_system} request times out.
 */
public class ${System}TimeoutException extends RuntimeException {

    private final String operation;
    private final Duration timeout;
    private final boolean retryable;

    public ${System}TimeoutException(String operation, Duration timeout) {
        super(String.format("Operation '%s' timed out after %s", operation, timeout));
        this.operation = operation;
        this.timeout = timeout;
        this.retryable = true;
    }

    public ${System}TimeoutException(String operation, Duration timeout, Throwable cause) {
        super(String.format("Operation '%s' timed out after %s", operation, timeout), cause);
        this.operation = operation;
        this.timeout = timeout;
        this.retryable = true;
    }

    public String getOperation() {
        return operation;
    }

    public Duration getTimeout() {
        return timeout;
    }

    public boolean isRetryable() {
        return retryable;
    }
}
```

---

## Pattern 5: Sync Failed Exception

For synchronization failures:

```java
package ${base_package}.exception;

/**
 * Thrown when synchronization with ${external_system} fails.
 */
public class ${System}SyncFailedException extends RuntimeException {

    private final Long entityId;
    private final String errorCode;
    private final int attemptNumber;
    private final boolean retryable;

    public ${System}SyncFailedException(Long entityId, String errorCode, String message) {
        super(String.format("Sync failed for entity %d: [%s] %s", entityId, errorCode, message));
        this.entityId = entityId;
        this.errorCode = errorCode;
        this.attemptNumber = 1;
        this.retryable = isRetryableError(errorCode);
    }

    public ${System}SyncFailedException(Long entityId, String errorCode, String message,
                                        int attemptNumber, Throwable cause) {
        super(String.format("Sync failed for entity %d (attempt %d): [%s] %s",
                entityId, attemptNumber, errorCode, message), cause);
        this.entityId = entityId;
        this.errorCode = errorCode;
        this.attemptNumber = attemptNumber;
        this.retryable = isRetryableError(errorCode);
    }

    private static boolean isRetryableError(String errorCode) {
        // Non-retryable errors
        return !errorCode.startsWith("VALIDATION_") &&
               !errorCode.equals("NOT_FOUND") &&
               !errorCode.equals("DUPLICATE");
    }

    public Long getEntityId() {
        return entityId;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public int getAttemptNumber() {
        return attemptNumber;
    }

    public boolean isRetryable() {
        return retryable;
    }
}
```

---

## Pattern 6: Business Rule Violation Exception

For business rule violations:

```java
package ${base_package}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

import java.util.List;

/**
 * Thrown when a business rule is violated.
 */
@ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
public class BusinessRuleViolationException extends RuntimeException {

    private final String ruleId;
    private final List<String> violations;

    public BusinessRuleViolationException(String ruleId, String message) {
        super(String.format("[%s] %s", ruleId, message));
        this.ruleId = ruleId;
        this.violations = List.of(message);
    }

    public BusinessRuleViolationException(String ruleId, List<String> violations) {
        super(String.format("[%s] %d violation(s): %s", ruleId, violations.size(),
                String.join("; ", violations)));
        this.ruleId = ruleId;
        this.violations = List.copyOf(violations);
    }

    public String getRuleId() {
        return ruleId;
    }

    public List<String> getViolations() {
        return violations;
    }
}
```

---

## Pattern 7: Validation Exception

For validation failures:

```java
package ${base_package}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * Thrown when request validation fails.
 */
@ResponseStatus(HttpStatus.BAD_REQUEST)
public class ValidationException extends RuntimeException {

    private final Map<String, List<String>> fieldErrors;

    public ValidationException(String message) {
        super(message);
        this.fieldErrors = Collections.emptyMap();
    }

    public ValidationException(String field, String message) {
        super(String.format("Validation failed for '%s': %s", field, message));
        this.fieldErrors = Map.of(field, List.of(message));
    }

    public ValidationException(Map<String, List<String>> fieldErrors) {
        super("Validation failed: " + fieldErrors.size() + " error(s)");
        this.fieldErrors = Map.copyOf(fieldErrors);
    }

    public Map<String, List<String>> getFieldErrors() {
        return fieldErrors;
    }

    public boolean hasFieldErrors() {
        return !fieldErrors.isEmpty();
    }
}
```

---

## Pattern 8: Global Exception Handler

REST API exception handler:

```java
package ${base_package}.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;

/**
 * Global exception handler for REST API.
 * Converts exceptions to RFC 7807 Problem Detail responses.
 */
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(${Resource}NotFoundException.class)
    public ProblemDetail handleNotFound(${Resource}NotFoundException ex) {
        log.warn("Resource not found: {}", ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("${Resource} Not Found");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("${resource}Id", ex.get${Resource}Id());
        return problem;
    }

    @ExceptionHandler(InvalidStatusTransitionException.class)
    public ProblemDetail handleInvalidTransition(InvalidStatusTransitionException ex) {
        log.warn("Invalid status transition: {}", ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setTitle("Invalid Status Transition");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("currentStatus", ex.getCurrentStatus());
        problem.setProperty("targetStatus", ex.getTargetStatus());
        return problem;
    }

    @ExceptionHandler(ValidationException.class)
    public ProblemDetail handleValidation(ValidationException ex) {
        log.warn("Validation failed: {}", ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setTitle("Validation Failed");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("errors", ex.getFieldErrors());
        return problem;
    }

    @ExceptionHandler(BusinessRuleViolationException.class)
    public ProblemDetail handleBusinessRule(BusinessRuleViolationException ex) {
        log.warn("Business rule violation: {}", ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage());
        problem.setTitle("Business Rule Violation");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("ruleId", ex.getRuleId());
        problem.setProperty("violations", ex.getViolations());
        return problem;
    }

    @ExceptionHandler(${System}ConnectionException.class)
    public ProblemDetail handleConnectionError(${System}ConnectionException ex) {
        log.error("External service connection failed: {}", ex.getMessage(), ex);
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.SERVICE_UNAVAILABLE, "External service temporarily unavailable");
        problem.setTitle("Service Unavailable");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("retryable", ex.isRetryable());
        return problem;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGeneric(Exception ex) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "An unexpected error occurred");
        problem.setTitle("Internal Server Error");
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }
}
```

---

## Anti-Patterns to Avoid

1. **Don't use checked exceptions** - Spring Boot works better with runtime exceptions
2. **Don't expose internal details** - Hide stack traces in production
3. **Don't forget logging** - Log exceptions in handler before returning
4. **Don't use generic messages** - Provide specific, actionable error messages
5. **Don't skip `@ResponseStatus`** - Ensures correct HTTP status without handler
6. **Don't forget immutability** - Use `List.copyOf()` for collections
