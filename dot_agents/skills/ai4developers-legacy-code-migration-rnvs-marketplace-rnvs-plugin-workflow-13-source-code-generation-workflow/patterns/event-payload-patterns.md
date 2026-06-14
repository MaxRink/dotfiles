# Event Payload Patterns (Horizon)

Patterns for Horizon event payload DTOs in VNRM microservices.

---

## Pattern 1: Incoming Event Payload

Event received from external systems:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;

/**
 * Payload for ${event_type} incoming events.
 * Source: ${source_system}
 * Implements: ${business_rule}
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Resource}ChangeEvent {

    /**
     * Unique identifier of the ${resource}.
     */
    @JsonProperty("${resource}_id")
    private Long ${resource}Id;

    /**
     * Type of change that occurred.
     */
    @JsonProperty("change_type")
    private ChangeType changeType;

    /**
     * Previous value (for updates).
     */
    @JsonProperty("old_value")
    private String oldValue;

    /**
     * New value (for creates/updates).
     */
    @JsonProperty("new_value")
    private String newValue;

    /**
     * Timestamp when the change occurred.
     */
    @JsonProperty("changed_at")
    private Instant changedAt;

    /**
     * User or system that triggered the change.
     */
    @JsonProperty("changed_by")
    private String changedBy;

    /**
     * Additional context/metadata.
     */
    @JsonProperty("metadata")
    private java.util.Map<String, Object> metadata;

    public enum ChangeType {
        CREATED,
        UPDATED,
        DELETED,
        OWNERSHIP_CHANGED,
        STATUS_CHANGED
    }
}
```

---

## Pattern 2: Success Event Payload

Event published on successful processing:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;

/**
 * Payload for ${event_type}.completed events.
 * Published when ${process_description} completes successfully.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Process}CompletedEvent {

    /**
     * ID of the processed ${resource}.
     */
    @JsonProperty("${resource}_id")
    private Long ${resource}Id;

    /**
     * External reference from target system.
     */
    @JsonProperty("external_reference")
    private String externalReference;

    /**
     * Processing result status.
     */
    @JsonProperty("result_status")
    @Builder.Default
    private String resultStatus = "SUCCESS";

    /**
     * When processing completed.
     */
    @JsonProperty("completed_at")
    private Instant completedAt;

    /**
     * Processing duration in milliseconds.
     */
    @JsonProperty("duration_ms")
    private Long durationMs;

    /**
     * Optional result details.
     */
    @JsonProperty("details")
    private java.util.Map<String, Object> details;
}
```

---

## Pattern 3: Error Event Payload

Event published on processing failure:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;
import java.util.List;

/**
 * Payload for ${event_type}.error events.
 * Published when ${process_description} fails.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Process}ErrorEvent {

    /**
     * ID of the ${resource} that failed processing.
     */
    @JsonProperty("${resource}_id")
    private Long ${resource}Id;

    /**
     * Error code for categorization.
     * Examples: VALIDATION_ERROR, CONNECTION_ERROR, TIMEOUT, BUSINESS_RULE_VIOLATION
     */
    @JsonProperty("error_code")
    private String errorCode;

    /**
     * Human-readable error message.
     */
    @JsonProperty("error_message")
    private String errorMessage;

    /**
     * Detailed error information (for debugging).
     */
    @JsonProperty("error_details")
    private String errorDetails;

    /**
     * When the error occurred.
     */
    @JsonProperty("occurred_at")
    private Instant occurredAt;

    /**
     * Whether the operation can be retried.
     */
    @JsonProperty("retryable")
    @Builder.Default
    private Boolean retryable = false;

    /**
     * Suggested retry delay in seconds (if retryable).
     */
    @JsonProperty("retry_after_seconds")
    private Integer retryAfterSeconds;

    /**
     * Validation errors (for VALIDATION_ERROR code).
     */
    @JsonProperty("validation_errors")
    private List<ValidationError> validationErrors;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ValidationError {
        private String field;
        private String message;
        private Object rejectedValue;
    }
}
```

---

## Pattern 4: Sync Request Event Payload

Event requesting synchronization with external system:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;

/**
 * Payload for ${system}.sync.requested events.
 * Published to request synchronization with ${external_system}.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${System}SyncRequestEvent {

    /**
     * ID of the ${resource} to sync.
     */
    @JsonProperty("${resource}_id")
    private Long ${resource}Id;

    /**
     * Type of sync operation.
     */
    @JsonProperty("sync_type")
    private SyncType syncType;

    /**
     * Priority of this sync request.
     */
    @JsonProperty("priority")
    @Builder.Default
    private Priority priority = Priority.NORMAL;

    /**
     * When this sync was requested.
     */
    @JsonProperty("requested_at")
    private Instant requestedAt;

    /**
     * Deadline for sync completion (for SLA tracking).
     */
    @JsonProperty("deadline")
    private Instant deadline;

    /**
     * Data to be synced.
     */
    @JsonProperty("payload")
    private Object payload;

    public enum SyncType {
        FULL,
        INCREMENTAL,
        RECONCILIATION
    }

    public enum Priority {
        LOW,
        NORMAL,
        HIGH,
        CRITICAL
    }
}
```

---

## Pattern 5: Notification Event Payload

Event for triggering notifications:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Payload for notification events.
 * Published to trigger email/SMS/push notifications.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NotificationRequestEvent {

    /**
     * Type of notification to send.
     */
    @JsonProperty("notification_type")
    private NotificationType notificationType;

    /**
     * Template ID for the notification content.
     */
    @JsonProperty("template_id")
    private String templateId;

    /**
     * Recipients of the notification.
     */
    @JsonProperty("recipients")
    private List<String> recipients;

    /**
     * Subject line (for email).
     */
    @JsonProperty("subject")
    private String subject;

    /**
     * Template variables for content generation.
     */
    @JsonProperty("template_vars")
    private Map<String, Object> templateVars;

    /**
     * When notification should be sent (null = immediate).
     */
    @JsonProperty("scheduled_at")
    private Instant scheduledAt;

    /**
     * Priority level.
     */
    @JsonProperty("priority")
    @Builder.Default
    private Priority priority = Priority.NORMAL;

    /**
     * Reference to the source entity.
     */
    @JsonProperty("source_entity_type")
    private String sourceEntityType;

    @JsonProperty("source_entity_id")
    private Long sourceEntityId;

    public enum NotificationType {
        EMAIL,
        SMS,
        PUSH,
        IN_APP
    }

    public enum Priority {
        LOW,
        NORMAL,
        HIGH,
        URGENT
    }
}
```

---

## Pattern 6: Batch Event Payload

Event containing multiple items for batch processing:

```java
package ${base_package}.event;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;
import java.util.List;

/**
 * Payload for batch ${process} events.
 * Used for bulk operations.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Batch${Resource}Event {

    /**
     * Batch operation ID.
     */
    @JsonProperty("batch_id")
    private String batchId;

    /**
     * Type of batch operation.
     */
    @JsonProperty("operation")
    private BatchOperation operation;

    /**
     * Items in this batch.
     */
    @JsonProperty("items")
    private List<${Resource}Item> items;

    /**
     * Total items in full batch (for pagination).
     */
    @JsonProperty("total_items")
    private Integer totalItems;

    /**
     * Current batch number (1-based).
     */
    @JsonProperty("batch_number")
    private Integer batchNumber;

    /**
     * Total number of batches.
     */
    @JsonProperty("total_batches")
    private Integer totalBatches;

    /**
     * When batch was created.
     */
    @JsonProperty("created_at")
    private Instant createdAt;

    public enum BatchOperation {
        CREATE,
        UPDATE,
        DELETE,
        SYNC
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ${Resource}Item {
        private Long id;
        private String externalRef;
        private Object data;
    }
}
```

---

## JSON Serialization Notes

1. **Use `@JsonProperty`** for snake_case JSON field names
2. **Use `Instant`** for timestamps (serializes to ISO-8601)
3. **Use `@Builder.Default`** for default values
4. **Use nested classes** for complex structures
5. **Use enums** for fixed value sets

---

## Anti-Patterns to Avoid

1. **Don't use `Date`** - Use `Instant` or `LocalDateTime`
2. **Don't use raw `Object`** - Use typed fields or generics
3. **Don't forget null handling** - Use `Optional` or `@JsonInclude`
4. **Don't include sensitive data** - No passwords, tokens in events
5. **Don't use mutable collections** - Use immutable or defensive copies
