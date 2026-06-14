# Repository Change Patterns

Patterns for adding and modifying Spring Data JPA repositories in CHANGE mode.

## Pattern 1: Add Custom Query to Existing Repository

When adding a new query method to an existing repository:

```java
// MODIFICATION: Add to existing repository interface

    /**
     * ${query_description}
     * Used by: ${service_method}
     * Implements: ${business_rule_id}
     */
    @Query("SELECT e FROM ${Entity} e WHERE ${where_clause}")
    List<${Entity}> ${findByCondition}(@Param("${param}") ${ParamType} ${param});
```

### Example: Add status filter query

```java
// File: src/main/java/com/vnrm/feature/repository/FeatureRepository.java
// EDIT: Add after line 25 (after existsByName method)

    /**
     * Find features by status with date range filter.
     * Used by: FeatureServiceImpl.findByStatusAndDateRange()
     * Implements: BR-FEAT-012
     */
    @Query("SELECT f FROM Feature f WHERE f.status = :status " +
           "AND f.createdAt >= :fromDate AND f.createdAt <= :toDate " +
           "ORDER BY f.createdAt DESC")
    List<Feature> findByStatusAndDateRange(
            @Param("status") FeatureStatus status,
            @Param("fromDate") Instant fromDate,
            @Param("toDate") Instant toDate);

    /**
     * Count features by status.
     * Used by: FeatureServiceImpl.getStatusCounts()
     */
    @Query("SELECT f.status, COUNT(f) FROM Feature f GROUP BY f.status")
    List<Object[]> countByStatus();
```

---

## Pattern 2: Create New Repository

When creating a new repository interface:

```java
package ${base_package}.repository;

import ${base_package}.entity.${Entity};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for ${entity_name} entity operations.
 * RNVS Source: ${rnvs_source}
 *
 * @since ${version}
 */
@Repository
public interface ${Entity}Repository extends JpaRepository<${Entity}, Long> {

    /**
     * Check if ${entity_name} exists by name.
     * Used by: ${ServiceImpl}.create()
     */
    boolean existsByName(String name);

    /**
     * Find ${entity_name} by name.
     * Used by: ${ServiceImpl}.findByName()
     */
    Optional<${Entity}> findByName(String name);

    /**
     * Find all ${entity_plural} by status.
     * Used by: ${ServiceImpl}.findByStatus()
     */
    List<${Entity}> findByStatus(${StatusEnum} status);

    /**
     * Find ${entity_plural} by ${parent_entity}.
     * Used by: ${ServiceImpl}.findBy${ParentEntity}Id()
     */
    List<${Entity}> findBy${ParentEntity}Id(Long ${parentEntity}Id);

    /**
     * Custom query for ${description}.
     * Used by: ${ServiceImpl}.${method}()
     * Implements: ${business_rule}
     */
    @Query("SELECT e FROM ${Entity} e WHERE ${where_clause} ORDER BY ${order_by}")
    List<${Entity}> ${customQueryMethod}(@Param("${param}") ${ParamType} ${param});
}
```

---

## Pattern 3: Add Native Query

When adding a native SQL query (for complex operations):

```java
// MODIFICATION: Add native query

    /**
     * ${query_description}
     * Uses native SQL for performance optimization.
     * Used by: ${service_method}
     */
    @Query(value = "SELECT * FROM ${table_name} WHERE ${where_clause} LIMIT :limit",
           nativeQuery = true)
    List<${Entity}> ${findByNativeQuery}(@Param("param") ${ParamType} param,
                                         @Param("limit") int limit);
```

---

## Pattern 4: Add Modifying Query

When adding an update/delete query:

```java
// MODIFICATION: Add modifying query

    /**
     * ${operation_description}
     * Used by: ${service_method}
     * Implements: ${business_rule}
     */
    @Modifying
    @Query("UPDATE ${Entity} e SET e.status = :newStatus WHERE e.status = :oldStatus")
    int updateStatus(@Param("oldStatus") ${StatusEnum} oldStatus,
                     @Param("newStatus") ${StatusEnum} newStatus);

    /**
     * Soft delete ${entity_plural} older than specified date.
     * Used by: ${service_method}
     */
    @Modifying
    @Query("UPDATE ${Entity} e SET e.deletedAt = CURRENT_TIMESTAMP WHERE e.createdAt < :date")
    int softDeleteOlderThan(@Param("date") Instant date);
```

---

## Pattern 5: Add Specification Query

When adding dynamic query support:

```java
// File: ${Entity}Repository.java
// MODIFICATION: Extend JpaSpecificationExecutor

public interface ${Entity}Repository extends
        JpaRepository<${Entity}, Long>,
        JpaSpecificationExecutor<${Entity}> {  // ADDED

    // ... existing methods
}

// New file: ${Entity}Specification.java
package ${base_package}.repository.specification;

import ${base_package}.entity.${Entity};
import org.springframework.data.jpa.domain.Specification;

import java.time.Instant;

/**
 * Specifications for dynamic ${entity_name} queries.
 */
public class ${Entity}Specification {

    public static Specification<${Entity}> hasStatus(${StatusEnum} status) {
        return (root, query, cb) ->
            status == null ? null : cb.equal(root.get("status"), status);
    }

    public static Specification<${Entity}> createdAfter(Instant date) {
        return (root, query, cb) ->
            date == null ? null : cb.greaterThanOrEqualTo(root.get("createdAt"), date);
    }

    public static Specification<${Entity}> nameLike(String name) {
        return (root, query, cb) ->
            name == null ? null : cb.like(cb.lower(root.get("name")),
                "%" + name.toLowerCase() + "%");
    }
}
```

---

## Pattern 6: Entity Modification

When modifying an existing entity:

```java
// File: src/main/java/com/vnrm/feature/entity/Feature.java
// EDIT: Add new field after line 35

    /**
     * Configuration validation status.
     * ADDED for: BR-FEAT-005
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "validation_status", length = 50)
    private ValidationStatus validationStatus;

    /**
     * Last validation timestamp.
     * ADDED for: BR-FEAT-005
     */
    @Column(name = "validated_at")
    private Instant validatedAt;

// EDIT: Add getter/setter (or use Lombok @Data)
```

---

## Anti-Patterns to Avoid

1. **Don't use SELECT * in native queries**: Explicitly list columns
2. **Don't forget @Modifying**: Required for UPDATE/DELETE queries
3. **Don't use camelCase in native SQL**: Use snake_case column names
4. **Don't skip indexes**: Add @Index for frequently queried columns
5. **Don't mix entity state**: Use DTOs for projections when possible
