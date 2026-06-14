# Entity and Enum Patterns

Patterns for creating JPA entities and enum types in VNRM microservices.

---

## Pattern 1: Create Status Enum

When creating a status enum for workflow states:

```java
package ${base_package}.entity;

/**
 * Status values for ${resource_name} workflow.
 * Implements: ${business_rule_id}
 * RNVS Source: ${rnvs_source}
 */
public enum ${ResourceName}Status {

    /**
     * Initial state - newly created.
     */
    NEW,

    /**
     * Work in progress.
     */
    IN_PROGRESS,

    /**
     * Escalated to higher level.
     */
    ESCALATED,

    /**
     * Successfully completed.
     */
    RESOLVED,

    /**
     * Cancelled or rejected.
     */
    CANCELLED;

    /**
     * Check if this status allows transition to target status.
     * Implements: ${transition_business_rule}
     */
    public boolean canTransitionTo(${ResourceName}Status target) {
        return switch (this) {
            case NEW -> target == IN_PROGRESS || target == CANCELLED;
            case IN_PROGRESS -> target == RESOLVED || target == ESCALATED || target == CANCELLED;
            case ESCALATED -> target == IN_PROGRESS || target == RESOLVED;
            case RESOLVED, CANCELLED -> false; // Terminal states
        };
    }
}
```

---

## Pattern 2: Create Sync Status Enum

For synchronization tracking:

```java
package ${base_package}.entity;

/**
 * Synchronization status values.
 * Implements: ${business_rule_id}
 */
public enum SyncStatus {

    /**
     * Waiting to be synced.
     */
    PENDING,

    /**
     * Currently syncing.
     */
    IN_PROGRESS,

    /**
     * Successfully synced.
     */
    SUCCESS,

    /**
     * Sync failed - will retry.
     */
    FAILED,

    /**
     * Max retries exceeded.
     */
    EXHAUSTED;

    public boolean isTerminal() {
        return this == SUCCESS || this == EXHAUSTED;
    }

    public boolean isRetryable() {
        return this == FAILED;
    }
}
```

---

## Pattern 3: Create JPA Entity

Standard JPA entity with auditing:

```java
package ${base_package}.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;

/**
 * ${entity_description}
 * Implements: ${business_rule_ids}
 * RNVS Source: ${rnvs_source}
 *
 * @since ${version}
 */
@Entity
@Table(name = "T_${TABLE_NAME}",
       indexes = {
           @Index(name = "idx_${table}_status", columnList = "status"),
           @Index(name = "idx_${table}_created_at", columnList = "created_at")
       })
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${EntityName} {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Business fields
    @Column(name = "${column_name}", nullable = false, length = ${length})
    private String ${fieldName};

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 50)
    private ${EntityName}Status status;

    // Relationships
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "${parent}_id")
    private ${ParentEntity} ${parentField};

    @OneToMany(mappedBy = "${this_field}", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<${ChildEntity}> ${childrenField} = new ArrayList<>();

    // Audit fields
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private Instant updatedAt;

    @CreatedBy
    @Column(name = "created_by", length = 255)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by", length = 255)
    private String updatedBy;

    // Soft delete
    @Column(name = "deleted_at")
    private Instant deletedAt;

    /**
     * Business method: ${method_description}
     * Implements: ${business_rule}
     */
    public void ${businessMethod}() {
        // Implementation
    }
}
```

---

## Pattern 4: Create History/Audit Entity

For tracking state changes:

```java
package ${base_package}.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

/**
 * Audit trail for ${parent_entity} status changes.
 * Implements: ${audit_business_rule}
 */
@Entity
@Table(name = "T_${PARENT}_HISTORY",
       indexes = {
           @Index(name = "idx_${parent}_history_${parent}_id", columnList = "${parent}_id"),
           @Index(name = "idx_${parent}_history_changed_at", columnList = "changed_at")
       })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${ParentEntity}History {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "${parent}_id", nullable = false)
    private ${ParentEntity} ${parentField};

    @Enumerated(EnumType.STRING)
    @Column(name = "old_status", length = 50)
    private ${ParentEntity}Status oldStatus;

    @Enumerated(EnumType.STRING)
    @Column(name = "new_status", nullable = false, length = 50)
    private ${ParentEntity}Status newStatus;

    @Column(name = "changed_at", nullable = false)
    private Instant changedAt;

    @Column(name = "changed_by", length = 255)
    private String changedBy;

    @Column(name = "reason", length = 1000)
    private String reason;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    /**
     * Factory method to record a status change.
     */
    public static ${ParentEntity}History recordChange(
            ${ParentEntity} entity,
            ${ParentEntity}Status oldStatus,
            ${ParentEntity}Status newStatus,
            String changedBy,
            String reason) {
        return ${ParentEntity}History.builder()
                .${parentField}(entity)
                .oldStatus(oldStatus)
                .newStatus(newStatus)
                .changedAt(Instant.now())
                .changedBy(changedBy)
                .reason(reason)
                .build();
    }
}
```

---

## Pattern 5: Create Sync Tracking Entity

For external system synchronization:

```java
package ${base_package}.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

/**
 * Tracks synchronization status with ${external_system}.
 * Implements: ${sync_business_rule}
 */
@Entity
@Table(name = "T_${RESOURCE}_SYNC_STATUS",
       indexes = {
           @Index(name = "idx_sync_${resource}_id", columnList = "${resource}_id"),
           @Index(name = "idx_sync_status", columnList = "status")
       })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Resource}SyncStatus {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "${resource}_id", nullable = false, unique = true)
    private ${Resource} ${resourceField};

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 50)
    @Builder.Default
    private SyncStatus status = SyncStatus.PENDING;

    @Column(name = "retry_count")
    @Builder.Default
    private Integer retryCount = 0;

    @Column(name = "max_retries")
    @Builder.Default
    private Integer maxRetries = 3;

    @Column(name = "last_attempt_at")
    private Instant lastAttemptAt;

    @Column(name = "next_attempt_at")
    private Instant nextAttemptAt;

    @Column(name = "last_error", length = 2000)
    private String lastError;

    @Column(name = "external_reference", length = 255)
    private String externalReference;

    @Column(name = "synced_at")
    private Instant syncedAt;

    /**
     * Record a successful sync.
     */
    public void markSuccess(String externalRef) {
        this.status = SyncStatus.SUCCESS;
        this.externalReference = externalRef;
        this.syncedAt = Instant.now();
        this.lastAttemptAt = Instant.now();
        this.lastError = null;
    }

    /**
     * Record a failed sync attempt.
     */
    public void markFailed(String error) {
        this.lastAttemptAt = Instant.now();
        this.lastError = error;
        this.retryCount++;

        if (this.retryCount >= this.maxRetries) {
            this.status = SyncStatus.EXHAUSTED;
        } else {
            this.status = SyncStatus.FAILED;
            // Exponential backoff: 1min, 2min, 4min, etc.
            long delayMinutes = (long) Math.pow(2, this.retryCount - 1);
            this.nextAttemptAt = Instant.now().plusSeconds(delayMinutes * 60);
        }
    }

    /**
     * Check if sync can be retried.
     */
    public boolean canRetry() {
        return this.status == SyncStatus.FAILED &&
               this.retryCount < this.maxRetries &&
               (this.nextAttemptAt == null || Instant.now().isAfter(this.nextAttemptAt));
    }
}
```

---

## Pattern 6: Add Fields to Existing Entity (MODIFY)

When adding new fields to an existing entity:

```java
// File: src/main/java/${package}/entity/${Entity}.java
// EDIT: Add after existing fields (before audit fields)

    // === NEW FIELDS for ${FEATURE} ===

    /**
     * Queue status for workflow tracking.
     * ADDED for: ${business_rule}
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "queue_status", length = 50)
    private QueueStatus queueStatus;

    /**
     * Escalation level (0 = none, 1 = L1, 2 = L2).
     * ADDED for: ${escalation_rule}
     */
    @Column(name = "escalation_level")
    @Builder.Default
    private Integer escalationLevel = 0;

    /**
     * User currently assigned to this item.
     * ADDED for: ${assignment_rule}
     */
    @Column(name = "assigned_to", length = 255)
    private String assignedTo;

    /**
     * Deadline for resolution.
     * ADDED for: ${sla_rule}
     */
    @Column(name = "deadline")
    private Instant deadline;

    // === END NEW FIELDS ===
```

---

## Anti-Patterns to Avoid

1. **Don't use primitive types for nullable fields** - Use `Integer` not `int` if nullable
2. **Don't forget `@Builder.Default`** - Required for default values with Lombok @Builder
3. **Don't use eager fetching** - Default to `FetchType.LAZY` for relationships
4. **Don't skip indexes** - Add indexes for frequently queried columns
5. **Don't forget cascade/orphanRemoval** - Configure properly for parent-child relationships
6. **Don't hardcode table names** - Use `T_` prefix per VNRM convention
