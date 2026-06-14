# Java JPA & Hibernate

Entity design, relationships, N+1 prevention, transactions, auditing, HikariCP, Flyway migrations.

## Quick Reference

```java
// Entity with auditing, indexes, and enum mapping
@Entity
@Table(name = "orders", indexes = {
    @Index(name = "idx_orders_status", columnList = "status"),
    @Index(name = "idx_orders_customer", columnList = "customer_id")
})
@EntityListeners(AuditingEntityListener.class)
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.PENDING;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    @BatchSize(size = 20)
    private List<OrderItem> items = new ArrayList<>();

    @Version
    private Long version;

    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;
}

// Enable auditing
@Configuration
@EnableJpaAuditing
class JpaConfig {}

// Repository with custom query
public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customer.id = :customerId")
    List<Order> findByCustomerWithItems(@Param("customerId") Long customerId);

    @EntityGraph(attributePaths = {"customer", "items"})
    Optional<Order> findWithDetailsById(Long id);
}

// Specification pattern
public class OrderSpecifications {

    public static Specification<Order> hasStatus(OrderStatus status) {
        return (root, query, cb) -> cb.equal(root.get("status"), status);
    }

    public static Specification<Order> createdAfter(LocalDate date) {
        return (root, query, cb) -> cb.greaterThan(root.get("createdDate"), date);
    }
}
```

## Projections

Use interface-based projections for lightweight read queries — avoids loading full entities:

```java
public interface OrderSummary {
    Long getId();
    OrderStatus getStatus();
    Instant getCreatedAt();
}

Page<OrderSummary> findAllBy(Pageable pageable);
```

## Pagination

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<Order> orders = repo.findByStatus(OrderStatus.ACTIVE, page);
```

For cursor-like pagination, include `id > :lastId` in JPQL with ordering.

## Indexing and Performance

- Add indexes for common filters (`status`, `slug`, foreign keys)
- Use composite indexes matching query patterns (`status, created_at`)
- Avoid `select *`; project only needed columns
- Batch writes with `saveAll` and `hibernate.jdbc.batch_size`

## Hibernate Configuration

```yaml
spring:
  jpa:
    open-in-view: false
    properties:
      hibernate:
        jdbc.batch_size: 50
        jdbc.lob.non_contextual_creation: true  # PostgreSQL LOB handling
        order_inserts: true
        order_updates: true
        generate_statistics: false
        default_batch_fetch_size: 20
    hibernate:
      ddl-auto: validate
```

## Connection Pooling (HikariCP)

```properties
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.validation-timeout=5000
```

## Migrations

- Use Flyway or Liquibase; never rely on Hibernate auto DDL in production
- Keep migrations idempotent and additive; avoid dropping columns without a plan

## Testing Data Access

- Prefer `@DataJpaTest` with Testcontainers to mirror production
- Assert SQL efficiency with logging:

```properties
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| N+1 queries | Lazy fetch without JOIN | Use JOIN FETCH or @EntityGraph |
| LazyInitializationException | Session closed | Use @Transactional or DTO projection |
| Slow inserts | Missing batch config | Enable hibernate.jdbc.batch_size |
| Optimistic lock exception | Concurrent modification | Retry with @Retryable |
| Connection pool exhaustion | Long-running txns | Split reads/writes, tune pool |
| Dirty checking overhead | Large entity graphs | Use read-only transactions |

**Remember**: Keep entities lean, queries intentional, and transactions short. Prevent N+1 with fetch strategies and projections, and index for your read/write paths.
