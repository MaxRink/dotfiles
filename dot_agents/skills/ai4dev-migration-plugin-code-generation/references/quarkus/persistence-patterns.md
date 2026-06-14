# Hibernate with Panache

Hibernate ORM with Panache: entity design, Active Record pattern, Repository pattern, queries, transactions, and database patterns.

## Quick Reference

```java
// Entity with Active Record pattern
@Entity
public class User extends PanacheEntity {
    public String name;
    public String email;
    public boolean active;

    // Static methods for queries
    public static User findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public static List<User> findActive() {
        return list("active", true);
    }
}

// Repository pattern
@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {

    public User findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public List<User> findActive() {
        return list("active", true);
    }
}
```

## Entity Design

### Active Record Pattern

```java
@Entity
@Table(name = "users")
public class User extends PanacheEntity {
    // id, persist(), delete() inherited from PanacheEntity

    @Column(nullable = false, length = 100)
    public String name;

    @Column(nullable = false, unique = true)
    public String email;

    @Column(nullable = false)
    public boolean active = true;

    @CreationTimestamp
    public LocalDateTime createdAt;

    @UpdateTimestamp
    public LocalDateTime updatedAt;

    // Custom queries
    public static User findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public static List<User> findByNameLike(String pattern) {
        return list("name like ?1", "%" + pattern + "%");
    }

    public static long countActive() {
        return count("active", true);
    }

    public static void deleteInactive() {
        delete("active", false);
    }
}
```

### Custom ID (Not Using PanacheEntity)

```java
@Entity
public class User extends PanacheEntityBase {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    public UUID id;

    public String name;
    public String email;

    // Rest of the entity...
}
```

### Composite Key

```java
@Embeddable
public class OrderLineId implements Serializable {
    public Long orderId;
    public Long productId;

    // equals() and hashCode() required
}

@Entity
public class OrderLine extends PanacheEntityBase {

    @EmbeddedId
    public OrderLineId id;

    public int quantity;
    public BigDecimal price;
}
```

## Repository Pattern

### Basic Repository

```java
@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {

    public User findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public List<User> findActive() {
        return list("active", true);
    }

    public List<User> searchByName(String name) {
        return list("LOWER(name) LIKE LOWER(?1)", "%" + name + "%");
    }

    public Optional<User> findByIdOptional(Long id) {
        return findByIdOptional(id);
    }

    @Transactional
    public User create(CreateUserRequest request) {
        User user = new User();
        user.name = request.name();
        user.email = request.email();
        user.active = true;
        persist(user);
        return user;
    }

    @Transactional
    public User update(Long id, UpdateUserRequest request) {
        User user = findById(id);
        if (user == null) {
            throw new EntityNotFoundException("User not found: " + id);
        }
        user.name = request.name();
        return user;
    }

    @Transactional
    public boolean deleteById(Long id) {
        return deleteById(id);
    }
}
```

### Generic Base Repository

```java
public abstract class BaseRepository<T extends PanacheEntityBase> implements PanacheRepository<T> {

    public Optional<T> findByIdOptional(Object id) {
        return Optional.ofNullable(findById(id));
    }

    @Transactional
    public T create(T entity) {
        persist(entity);
        return entity;
    }

    @Transactional
    public T update(T entity) {
        return getEntityManager().merge(entity);
    }

    @Transactional
    public boolean deleteById(Object id) {
        return deleteById(id);
    }

    public Page<T> findPage(int page, int size) {
        return findAll()
            .page(page, size)
            .list();
    }
}

// Usage
@ApplicationScoped
public class UserRepository extends BaseRepository<User> {

    public User findByEmail(String email) {
        return find("email", email).firstResult();
    }
}
```

## Queries

### Query Methods

```java
// By field name
List<User> users = User.list("name", "John");

// By field name with parameters
List<User> users = User.list("name = ?1 and active = ?2", "John", true);

// Named parameters
List<User> users = User.list("name = :name and active = :active",
    Parameters.with("name", "John").and("active", true));

// Sort
List<User> users = User.list("active", Sort.by("name").and("createdAt"));

// Pagination
List<User> users = User.findAll()
    .page(0, 10)  // page 0, size 10
    .list();

// Count
long count = User.count("active", true);

// Exists
boolean exists = User.count("email", "john@example.com") > 0;

// Stream (for large datasets)
User.streamAll()
    .filter(u -> u.active)
    .forEach(u -> System.out.println(u.name));
```

### JPQL Queries

```java
@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {

    public List<User> findByDomain(String domain) {
        return find("email LIKE ?1", "%" + domain).list();
    }

    public List<User> findCreatedAfter(LocalDateTime date) {
        return find("createdAt > ?1", date)
            .page(0, 100)
            .list();
    }

    public UserStats getStats() {
        return find(
            "SELECT new com.example.UserStats(COUNT(u), AVG(u.age)) FROM User u"
        ).project(UserStats.class).firstResult();
    }

    // Join queries
    public List<User> findUsersWithOrders() {
        return find("SELECT DISTINCT u FROM User u JOIN u.orders o").list();
    }
}
```

### Native Queries

```java
@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {

    public List<User> findByCustomQuery(String criteria) {
        return getEntityManager()
            .createNativeQuery(
                "SELECT * FROM users WHERE name ILIKE :criteria",
                User.class
            )
            .setParameter("criteria", "%" + criteria + "%")
            .getResultList();
    }

    public int updateBulk(boolean active) {
        return getEntityManager()
            .createNativeQuery("UPDATE users SET active = :active WHERE created_at < NOW() - INTERVAL '1 year'")
            .setParameter("active", active)
            .executeUpdate();
    }
}
```

## Relationships

### One-to-Many

```java
@Entity
public class User extends PanacheEntity {
    public String name;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    public List<Order> orders = new ArrayList<>();

    public void addOrder(Order order) {
        orders.add(order);
        order.user = this;
    }

    public void removeOrder(Order order) {
        orders.remove(order);
        order.user = null;
    }
}

@Entity
public class Order extends PanacheEntity {
    public LocalDateTime orderDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    public User user;
}
```

### Many-to-Many

```java
@Entity
public class User extends PanacheEntity {
    public String name;

    @ManyToMany
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    public Set<Role> roles = new HashSet<>();
}

@Entity
public class Role extends PanacheEntity {
    public String name;

    @ManyToMany(mappedBy = "roles")
    public Set<User> users = new HashSet<>();
}
```

### One-to-One

```java
@Entity
public class User extends PanacheEntity {
    public String name;

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    public UserProfile profile;
}

@Entity
public class UserProfile extends PanacheEntity {
    public String bio;
    public String avatar;

    @OneToOne
    @JoinColumn(name = "user_id")
    public User user;
}
```

## Transactions

### Declarative Transactions

```java
@ApplicationScoped
public class UserService {

    @Inject
    UserRepository userRepository;

    @Transactional
    public User createUser(CreateUserRequest request) {
        User user = new User();
        user.name = request.name();
        user.email = request.email();
        userRepository.persist(user);
        return user;
    }

    @Transactional
    public User updateUser(Long id, UpdateUserRequest request) {
        User user = userRepository.findById(id);
        if (user == null) {
            throw new EntityNotFoundException();
        }
        user.name = request.name();
        return user;  // Auto-persisted due to @Transactional
    }

    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
```

### Programmatic Transactions

```java
@ApplicationScoped
public class UserService {

    @Inject
    UserRepository userRepository;

    @Inject
    UserTransaction transaction;

    public void complexOperation() throws Exception {
        try {
            transaction.begin();

            // Multiple operations
            User user = new User();
            userRepository.persist(user);

            // More operations...

            transaction.commit();
        } catch (Exception e) {
            transaction.rollback();
            throw e;
        }
    }
}
```

### Transaction Boundaries

```java
// Read-only transactions (optimization)
@Transactional(Transactional.TxType.SUPPORTS)
public List<User> findAll() {
    return userRepository.listAll();
}

// Require new transaction
@Transactional(Transactional.TxType.REQUIRES_NEW)
public void auditLog(String event) {
    // Always in separate transaction
}

// Never in transaction
@Transactional(Transactional.TxType.NEVER)
public void backgroundTask() {
    // Not transactional
}
```

## Database Migrations (Flyway)

### Configuration

```properties
# Flyway
quarkus.flyway.migrate-at-start=true
quarkus.flyway.baseline-on-migrate=true
quarkus.flyway.locations=db/migration

# Disable Hibernate auto-generation (use Flyway instead)
quarkus.hibernate-orm.database.generation=none
```

### Migration Files

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(active);
```

```sql
-- V2__create_orders_table.sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_date TIMESTAMP NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
```

## Performance Patterns

### Lazy vs Eager Loading

```java
@Entity
public class User extends PanacheEntity {
    public String name;

    // Lazy loading (default for collections)
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    public List<Order> orders;

    // Eager loading (use sparingly)
    @ManyToOne(fetch = FetchType.EAGER)
    public Department department;
}

// Fetch join to avoid N+1
public List<User> findUsersWithOrders() {
    return find("SELECT u FROM User u LEFT JOIN FETCH u.orders").list();
}
```

### Batch Operations

```java
@Transactional
public void createBatch(List<CreateUserRequest> requests) {
    for (int i = 0; i < requests.size(); i++) {
        User user = new User();
        user.name = requests.get(i).name();
        user.email = requests.get(i).email();
        persist(user);

        // Flush batch every 20 items
        if (i % 20 == 0) {
            getEntityManager().flush();
            getEntityManager().clear();
        }
    }
}
```

### Pagination

```java
public record PageResult<T>(List<T> content, long total, int page, int size) {}

public PageResult<User> findPage(int page, int size) {
    List<User> users = findAll()
        .page(page, size)
        .list();

    long total = count();

    return new PageResult<>(users, total, page, size);
}
```

## Validation

```java
@Entity
public class User extends PanacheEntity {

    @NotBlank
    @Size(min = 2, max = 100)
    public String name;

    @NotBlank
    @Email
    @Column(unique = true)
    public String email;

    @Min(18)
    @Max(120)
    public Integer age;

    @Pattern(regexp = "^[A-Z]{2}$")
    public String countryCode;

    @PrePersist
    @PreUpdate
    public void validate() {
        // Custom validation logic
        if (email != null && !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
    }
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| LazyInitializationException | Accessing lazy field outside transaction | Use @Transactional or fetch join |
| N+1 queries | Missing fetch join | Use JOIN FETCH in query |
| DetachedEntityException | Entity not managed | Merge entity or use @Transactional |
| Unique constraint violation | Duplicate entry | Check for existing records first |
| Transaction rollback | Unchecked exception | Catch and handle exceptions properly |

## Best Practices

1. **Use Repository pattern** for better separation of concerns
2. **Avoid N+1 queries** with fetch joins or batch loading
3. **Keep transactions short** to reduce lock contention
4. **Use Flyway/Liquibase** for database migrations, not Hibernate auto-DDL
5. **Lazy load by default** for collections, eager only when necessary
6. **Index frequently queried columns** for performance
7. **Use pagination** for large result sets
8. **Validate at entity level** with Bean Validation annotations
