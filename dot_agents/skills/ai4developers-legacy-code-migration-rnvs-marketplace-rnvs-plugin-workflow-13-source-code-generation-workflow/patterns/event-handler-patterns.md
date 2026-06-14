# Event Handler Patterns (Horizon)

Patterns for Horizon (Telekom Event Bus) event handlers in VNRM microservices.

**IMPORTANT**: VNRM uses **Horizon** (Telekom's Event Bus), NOT Kafka.

---

## Pattern 1: Create Event Handler

Standard Horizon event handler:

```java
package ${base_package}.event;

import de.telekom.horizon.client.HorizonClient;
import de.telekom.horizon.client.HorizonEvent;
import de.telekom.horizon.client.annotation.HorizonEventListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * Handles ${event_type} events from Horizon Event Bus.
 * Implements: ${business_rule_ids}
 * RNVS Source: ${rnvs_source}
 *
 * Tested by: ${EventHandler}Test
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ${EventName}Handler {

    private final ${ProcessingService} processingService;
    private final HorizonClient horizonClient;

    /**
     * Handle incoming ${event_type} events.
     * Implements: ${business_rule}
     * Tested by: ${EventHandler}Test.shouldHandle${EventName}()
     *
     * @param event The incoming Horizon event
     */
    @HorizonEventListener(eventType = "${event.type.name}")
    public void handle(HorizonEvent<${EventPayload}> event) {
        String correlationId = event.getCorrelationId();
        log.info("Received {} event with correlationId: {}", event.getEventType(), correlationId);

        try {
            ${EventPayload} payload = event.getPayload();

            // Validate payload
            validatePayload(payload);

            // Process the event
            ${ResultType} result = processingService.process(payload);

            // Publish success event
            publishSuccessEvent(correlationId, result);

            log.info("Successfully processed {} event: {}", event.getEventType(), correlationId);

        } catch (ValidationException e) {
            log.warn("Validation failed for event {}: {}", correlationId, e.getMessage());
            publishErrorEvent(correlationId, "VALIDATION_ERROR", e.getMessage());

        } catch (ProcessingException e) {
            log.error("Processing failed for event {}: {}", correlationId, e.getMessage(), e);
            publishErrorEvent(correlationId, "PROCESSING_ERROR", e.getMessage());

        } catch (Exception e) {
            log.error("Unexpected error processing event {}: {}", correlationId, e.getMessage(), e);
            publishErrorEvent(correlationId, "INTERNAL_ERROR", "Unexpected error occurred");
        }
    }

    private void validatePayload(${EventPayload} payload) {
        if (payload == null) {
            throw new ValidationException("Event payload cannot be null");
        }
        if (payload.get${RequiredField}() == null) {
            throw new ValidationException("${RequiredField} is required");
        }
    }

    private void publishSuccessEvent(String correlationId, ${ResultType} result) {
        ${SuccessEvent} successPayload = ${SuccessEvent}.builder()
                .${resultField}(result.get${ResultField}())
                .processedAt(Instant.now())
                .build();

        HorizonEvent<${SuccessEvent}> successEvent = HorizonEvent.<${SuccessEvent}>builder()
                .withEventType("${event.type.success}")
                .withPayload(successPayload)
                .withCorrelationId(correlationId)
                .build();

        horizonClient.publish(successEvent);
        log.debug("Published success event for correlationId: {}", correlationId);
    }

    private void publishErrorEvent(String correlationId, String errorCode, String errorMessage) {
        ${ErrorEvent} errorPayload = ${ErrorEvent}.builder()
                .errorCode(errorCode)
                .errorMessage(errorMessage)
                .occurredAt(Instant.now())
                .build();

        HorizonEvent<${ErrorEvent}> errorEvent = HorizonEvent.<${ErrorEvent}>builder()
                .withEventType("${event.type.error}")
                .withPayload(errorPayload)
                .withCorrelationId(correlationId)
                .build();

        horizonClient.publish(errorEvent);
        log.debug("Published error event for correlationId: {}", correlationId);
    }
}
```

---

## Pattern 2: Multi-Event Handler

Handler that processes multiple event types:

```java
package ${base_package}.event;

import de.telekom.horizon.client.HorizonClient;
import de.telekom.horizon.client.HorizonEvent;
import de.telekom.horizon.client.annotation.HorizonEventListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * Handles multiple ${domain} event types.
 * Implements: ${business_rule_ids}
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ${Domain}EventHandler {

    private final ${Domain}Service ${domain}Service;
    private final HorizonClient horizonClient;

    /**
     * Handle ${resource} created events.
     * Tested by: ${Domain}EventHandlerTest.shouldHandleCreated()
     */
    @HorizonEventListener(eventType = "${domain}.${resource}.created")
    public void handleCreated(HorizonEvent<${Resource}CreatedEvent> event) {
        log.info("Handling {}.{}.created: {}", "${domain}", "${resource}", event.getCorrelationId());
        ${domain}Service.onCreate(event.getPayload());
        publishAck(event.getCorrelationId(), "created");
    }

    /**
     * Handle ${resource} updated events.
     * Tested by: ${Domain}EventHandlerTest.shouldHandleUpdated()
     */
    @HorizonEventListener(eventType = "${domain}.${resource}.updated")
    public void handleUpdated(HorizonEvent<${Resource}UpdatedEvent> event) {
        log.info("Handling {}.{}.updated: {}", "${domain}", "${resource}", event.getCorrelationId());
        ${domain}Service.onUpdate(event.getPayload());
        publishAck(event.getCorrelationId(), "updated");
    }

    /**
     * Handle ${resource} deleted events.
     * Tested by: ${Domain}EventHandlerTest.shouldHandleDeleted()
     */
    @HorizonEventListener(eventType = "${domain}.${resource}.deleted")
    public void handleDeleted(HorizonEvent<${Resource}DeletedEvent> event) {
        log.info("Handling {}.{}.deleted: {}", "${domain}", "${resource}", event.getCorrelationId());
        ${domain}Service.onDelete(event.getPayload());
        publishAck(event.getCorrelationId(), "deleted");
    }

    private void publishAck(String correlationId, String action) {
        // Optional: publish acknowledgment event
    }
}
```

---

## Pattern 3: Event Handler with Retry

Handler with manual retry logic for transient failures:

```java
package ${base_package}.event;

import de.telekom.horizon.client.HorizonClient;
import de.telekom.horizon.client.HorizonEvent;
import de.telekom.horizon.client.annotation.HorizonEventListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Component;

/**
 * Handles ${event_type} events with retry support.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ${EventName}RetryHandler {

    private final ${ProcessingService} processingService;

    /**
     * Handle event with automatic retry on transient failures.
     * Retries up to 3 times with exponential backoff.
     */
    @HorizonEventListener(eventType = "${event.type.name}")
    @Retryable(
            retryFor = {TransientException.class, ConnectionException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 1000, multiplier = 2))
    public void handle(HorizonEvent<${EventPayload}> event) {
        log.info("Processing event: {}", event.getCorrelationId());
        processingService.process(event.getPayload());
    }
}
```

---

## Pattern 4: Async Event Publisher Service

Service for publishing events asynchronously:

```java
package ${base_package}.event;

import de.telekom.horizon.client.HorizonClient;
import de.telekom.horizon.client.HorizonEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Async event publishing service for ${domain} events.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ${Domain}EventPublisher {

    private final HorizonClient horizonClient;

    /**
     * Publish ${resource} sync completed event.
     * Implements: ${business_rule}
     */
    @Async
    public CompletableFuture<Void> publishSyncCompleted(Long ${resource}Id, String externalRef) {
        String correlationId = UUID.randomUUID().toString();

        ${Resource}SyncCompletedEvent payload = ${Resource}SyncCompletedEvent.builder()
                .${resource}Id(${resource}Id)
                .externalReference(externalRef)
                .syncedAt(Instant.now())
                .build();

        HorizonEvent<${Resource}SyncCompletedEvent> event = HorizonEvent.<${Resource}SyncCompletedEvent>builder()
                .withEventType("${domain}.${resource}.sync.completed")
                .withPayload(payload)
                .withCorrelationId(correlationId)
                .build();

        return horizonClient.publishAsync(event)
                .thenAccept(v -> log.info("Published sync.completed event: {}", correlationId))
                .exceptionally(e -> {
                    log.error("Failed to publish sync.completed event: {}", correlationId, e);
                    return null;
                });
    }

    /**
     * Publish ${resource} sync error event.
     */
    @Async
    public CompletableFuture<Void> publishSyncError(Long ${resource}Id, String errorCode, String errorMessage) {
        String correlationId = UUID.randomUUID().toString();

        ${Resource}SyncErrorEvent payload = ${Resource}SyncErrorEvent.builder()
                .${resource}Id(${resource}Id)
                .errorCode(errorCode)
                .errorMessage(errorMessage)
                .occurredAt(Instant.now())
                .build();

        HorizonEvent<${Resource}SyncErrorEvent> event = HorizonEvent.<${Resource}SyncErrorEvent>builder()
                .withEventType("${domain}.${resource}.sync.error")
                .withPayload(payload)
                .withCorrelationId(correlationId)
                .build();

        return horizonClient.publishAsync(event)
                .thenAccept(v -> log.info("Published sync.error event: {}", correlationId))
                .exceptionally(e -> {
                    log.error("Failed to publish sync.error event: {}", correlationId, e);
                    return null;
                });
    }
}
```

---

## Event Type Naming Convention

| Event Category | Pattern | Example |
|----------------|---------|---------|
| Entity lifecycle | `{domain}.{resource}.{action}` | `rnb.block.created` |
| Sync status | `{domain}.{resource}.sync.{status}` | `rnb.block.sync.completed` |
| Ownership change | `{domain}.{resource}.ownership.{action}` | `rnb.block.ownership.changed` |
| Error events | `{domain}.{resource}.error` | `rnb.block.error` |

---

## Anti-Patterns to Avoid

1. **Don't use Kafka** - VNRM uses Horizon Event Bus
2. **Don't block in handlers** - Use async processing for long operations
3. **Don't forget error events** - Always publish error events on failure
4. **Don't skip correlation IDs** - Required for tracing and debugging
5. **Don't swallow exceptions** - Log and publish error events
6. **Don't hardcode event types** - Use constants or configuration
