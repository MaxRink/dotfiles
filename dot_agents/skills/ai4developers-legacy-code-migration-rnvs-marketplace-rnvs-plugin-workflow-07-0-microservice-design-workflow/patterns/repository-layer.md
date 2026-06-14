# Repository Layer Patterns

Spring Data JPA repository patterns for VNRM microservices.

## Repository Template

```java
package com.telekom.vnrm.${submodule}.${service}.repository;

import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName};
import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName}Status;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository for ${EntityName}
 */
@Repository
public interface ${EntityName}Repository
    extends JpaRepository<${EntityName}, Long>,
            JpaSpecificationExecutor<${EntityName}> {

    // Find by unique business key
    Optional<${EntityName}> findBy${UniqueField}(String ${uniqueField});

    // Find by status
    List<${EntityName}> findByStatus(${EntityName}Status status);

    // Find by status with pagination
    Page<${EntityName}> findByStatus(${EntityName}Status status, Pageable pageable);

    // Custom JPQL query
    @Query("SELECT e FROM ${EntityName} e WHERE e.status = :status AND e.createdAt > :since")
    List<${EntityName}> findActiveCreatedSince(
        @Param("status") ${EntityName}Status status,
        @Param("since") LocalDateTime since
    );

    // Native query for complex joins
    @Query(value = """
        SELECT e.* FROM ${table_name} e
        JOIN ${related_table} r ON e.id = r.${entity}_id
        WHERE r.${condition_field} = :value
        """, nativeQuery = true)
    List<${EntityName}> findByRelatedCondition(@Param("value") String value);

    // Check existence
    boolean existsBy${UniqueField}(String ${uniqueField});

    // Count by status
    long countByStatus(${EntityName}Status status);

    // Delete by condition
    void deleteByStatusAndCreatedAtBefore(${EntityName}Status status, LocalDateTime before);
}
```

## Specification Pattern

```java
package com.telekom.vnrm.${submodule}.${service}.repository;

import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName};
import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName}Status;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDateTime;

/**
 * Specifications for dynamic ${EntityName} queries
 */
public class ${EntityName}Specifications {

    public static Specification<${EntityName}> hasStatus(${EntityName}Status status) {
        return (root, query, cb) ->
            status == null ? cb.conjunction() : cb.equal(root.get("status"), status);
    }

    public static Specification<${EntityName}> createdAfter(LocalDateTime date) {
        return (root, query, cb) ->
            date == null ? cb.conjunction() : cb.greaterThan(root.get("createdAt"), date);
    }

    public static Specification<${EntityName}> containsText(String text) {
        return (root, query, cb) -> {
            if (text == null || text.isBlank()) {
                return cb.conjunction();
            }
            String pattern = "%" + text.toLowerCase() + "%";
            return cb.like(cb.lower(root.get("${searchableField}")), pattern);
        };
    }
}
```

## Projection Pattern

```java
package com.telekom.vnrm.${submodule}.${service}.repository;

/**
 * Projection for summary view of ${EntityName}
 */
public interface ${EntityName}Summary {
    Long getId();
    String get${UniqueField}();
    String getStatus();
    String getCreatedAt();
}
```

```java
// In repository
List<${EntityName}Summary> findSummaryByStatus(${EntityName}Status status);
```

## VNRM-Specific Repository Patterns

### Callnumber Repository (NUM submodule)

```java
@Repository
public interface CallnumberRepository extends JpaRepository<Callnumber, Long> {

    Optional<Callnumber> findByCallnumber(String callnumber);

    List<Callnumber> findByAreaCode(String areaCode);

    @Query("SELECT c FROM Callnumber c WHERE c.callnumber LIKE :prefix%")
    List<Callnumber> findByCallnumberPrefix(@Param("prefix") String prefix);

    @Query("SELECT COUNT(c) FROM Callnumber c WHERE c.areaCode = :areaCode AND c.status = 'ACTIVE'")
    long countActiveByAreaCode(@Param("areaCode") String areaCode);
}
```

### Porting Repository (PRT submodule)

```java
@Repository
public interface PortingRepository extends JpaRepository<Porting, Long> {

    Optional<Porting> findByPortingId(String portingId);

    List<Porting> findByDonorProviderAndStatus(String donorProvider, PortingStatus status);

    @Query("""
        SELECT p FROM Porting p
        WHERE p.portingDate BETWEEN :startDate AND :endDate
        AND p.portingStatus = :status
        """)
    List<Porting> findByDateRangeAndStatus(
        @Param("startDate") LocalDate startDate,
        @Param("endDate") LocalDate endDate,
        @Param("status") PortingStatus status
    );
}
```

## Query Performance Guidelines

1. **Use pagination** for large result sets
2. **Add database indexes** for query columns
3. **Use projections** when full entity not needed
4. **Prefer JPQL over native queries** for portability
5. **Use specifications** for dynamic queries
6. **Avoid N+1 queries** with fetch joins

## Fetch Join Example

```java
@Query("SELECT e FROM ${EntityName} e LEFT JOIN FETCH e.children WHERE e.id = :id")
Optional<${EntityName}> findByIdWithChildren(@Param("id") Long id);
```
