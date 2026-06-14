# Quarkus Coding Standards

Naming conventions, CDI best practices, code style, immutability patterns, exception handling, and logging for Quarkus applications.

## Naming Conventions

### Classes

```java
// PascalCase for classes
public class UserService {}
public class OrderRepository {}
public class ProductResource {}

// Resource classes - suffix with "Resource"
@Path("/users")
public class UserResource {}

// Service classes - suffix with "Service"
@ApplicationScoped
public class UserService {}

// Repository classes - suffix with "Repository"
@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {}

// Configuration classes - suffix with "Config" or "Configuration"
@ConfigMapping(prefix = "app")
public interface AppConfig {}

// DTOs/Records - suffix with "Request", "Response", or "Dto"
public record CreateUserRequest(String name, String email) {}
public record UserResponse(Long id, String name, String email) {}
public record UserDto(Long id, String name) {}

// Exception mappers - suffix with "Mapper"
@Provider
public class ValidationExceptionMapper implements ExceptionMapper<ValidationException> {}
```

### Methods and Variables

```java
// camelCase for methods and variables
public User findUser(Long id) {}
public void updateUserProfile() {}

private String userName;
private LocalDateTime createdAt;
private boolean isActive;

// Boolean methods - prefix with "is", "has", "can", "should"
public boolean isActive() {}
public boolean hasPermission() {}
public boolean canDelete() {}

// Collection methods - use plural or descriptive names
public List<User> getUsers() {}
public Set<String> getRoles() {}
public Map<Long, User> getUserMap() {}
```

### Constants

```java
// UPPER_SNAKE_CASE for constants
public static final String DEFAULT_ROLE = "USER";
public static final int MAX_LOGIN_ATTEMPTS = 3;
public static final Duration SESSION_TIMEOUT = Duration.ofMinutes(30);

// Group related constants in interfaces or classes
public interface UserConstants {
    String DEFAULT_ROLE = "USER";
    int MAX_NAME_LENGTH = 100;
    Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@(.+)$");
}
```

### Packages

```java
// Structure by feature/module, not by layer
com.example.app.user.resource
com.example.app.user.service
com.example.app.user.repository
com.example.app.user.entity
com.example.app.user.dto

// Or by layer for small projects
com.example.app.resource
com.example.app.service
com.example.app.repository
com.example.app.entity
com.example.app.dto
com.example.app.config
com.example.app.exception
```

## CDI Best Practices

### Bean Scopes

```java
// Use @ApplicationScoped for stateless services (default choice)
@ApplicationScoped
public class UserService {
    // Shared across application, single instance
}

// Use @RequestScoped for request-specific state
@RequestScoped
public class RequestContext {
    private String requestId = UUID.randomUUID().toString();
}

// Use @Singleton sparingly (legacy, prefer @ApplicationScoped)
@Singleton
public class LegacyService {}

// Avoid @Dependent unless necessary (new instance per injection)
@Dependent
public class TemporaryProcessor {}
```

### Dependency Injection

```java
// Prefer constructor injection for required dependencies
@ApplicationScoped
public class UserService {

    private final UserRepository userRepository;
    private final EmailService emailService;

    @Inject
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

// Use field injection for optional dependencies or when constructor gets too large
@ApplicationScoped
public class NotificationService {

    @Inject
    EmailService emailService;

    @Inject
    SmsService smsService;

    @Inject
    @ConfigProperty(name = "notification.enabled", defaultValue = "true")
    boolean enabled;
}

// Use @Named for disambiguation
@Inject
@Named("userCache")
Cache<Long, User> cache;
```

### Producers

```java
@ApplicationScoped
public class ProducerConfiguration {

    // Produce application-scoped beans
    @Produces
    @ApplicationScoped
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }

    // Produce with qualifiers
    @Produces
    @Named("userCache")
    @ApplicationScoped
    public Cache<Long, User> userCache() {
        return Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(Duration.ofMinutes(10))
            .build();
    }

    // Dispose when needed
    @Produces
    @ApplicationScoped
    public ExternalClient createClient(@ConfigProperty(name = "api.url") String url) {
        return new ExternalClient(url);
    }

    public void closeClient(@Disposes ExternalClient client) {
        client.close();
    }
}
```

## Immutability Patterns

### Records for DTOs (Recommended)

```java
// Use records for immutable DTOs
public record UserDto(
    Long id,
    String name,
    String email,
    LocalDateTime createdAt
) {
    // Factory method
    public static UserDto from(User user) {
        return new UserDto(
            user.id,
            user.name,
            user.email,
            user.createdAt
        );
    }

    // Validation in compact constructor
    public UserDto {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Name required");
        }
    }
}

// Request DTOs with validation
public record CreateUserRequest(
    @NotBlank @Size(min = 2, max = 100) String name,
    @NotBlank @Email String email,
    @Pattern(regexp = "^(USER|ADMIN)$") String role
) {}
```

### Immutable Collections

```java
// Use List.of(), Set.of(), Map.of() for immutable collections
List<String> roles = List.of("USER", "ADMIN");
Set<String> permissions = Set.of("READ", "WRITE");
Map<String, String> config = Map.of("key1", "value1", "key2", "value2");

// Use Collections.unmodifiableXxx() for legacy code
List<String> immutableList = Collections.unmodifiableList(mutableList);

// Or copy to immutable
List<User> users = getUsersFromDb();
return List.copyOf(users);
```

## Exception Handling

### Custom Exceptions

```java
// Domain-specific exceptions
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long id) {
        super("User not found: " + id);
    }
}

public class InvalidUserException extends RuntimeException {
    public InvalidUserException(String message) {
        super(message);
    }
}

public class DuplicateEmailException extends RuntimeException {
    public DuplicateEmailException(String email) {
        super("Email already exists: " + email);
    }
}
```

### Exception Mappers

```java
// Map exceptions to HTTP responses
@Provider
public class UserNotFoundExceptionMapper implements ExceptionMapper<UserNotFoundException> {

    @Override
    public Response toResponse(UserNotFoundException exception) {
        ErrorResponse error = new ErrorResponse(
            "USER_NOT_FOUND",
            exception.getMessage(),
            LocalDateTime.now()
        );
        return Response.status(404).entity(error).build();
    }
}

@Provider
public class ValidationExceptionMapper implements ExceptionMapper<ConstraintViolationException> {

    @Override
    public Response toResponse(ConstraintViolationException exception) {
        Map<String, String> errors = exception.getConstraintViolations()
            .stream()
            .collect(Collectors.toMap(
                v -> v.getPropertyPath().toString(),
                ConstraintViolation::getMessage
            ));

        return Response.status(400).entity(errors).build();
    }
}

// Generic exception mapper (fallback)
@Provider
@Priority(Priorities.USER + 100)  // Lower priority
public class GenericExceptionMapper implements ExceptionMapper<Exception> {

    private static final Logger LOG = Logger.getLogger(GenericExceptionMapper.class);

    @Override
    public Response toResponse(Exception exception) {
        LOG.error("Unhandled exception", exception);

        ErrorResponse error = new ErrorResponse(
            "INTERNAL_ERROR",
            "An unexpected error occurred",
            LocalDateTime.now()
        );

        return Response.status(500).entity(error).build();
    }
}
```

### Error Response Format

```java
public record ErrorResponse(
    String code,
    String message,
    LocalDateTime timestamp,
    Map<String, String> details
) {
    public ErrorResponse(String code, String message, LocalDateTime timestamp) {
        this(code, message, timestamp, Map.of());
    }
}
```

## Logging

### Logger Setup

```java
// Use JBoss Logging
import org.jboss.logging.Logger;

@ApplicationScoped
public class UserService {

    private static final Logger LOG = Logger.getLogger(UserService.class);

    public User createUser(CreateUserRequest request) {
        LOG.infof("Creating user: %s", request.name());

        try {
            User user = new User();
            user.name = request.name();
            userRepository.persist(user);

            LOG.infof("User created successfully: id=%d, name=%s", user.id, user.name);
            return user;
        } catch (Exception e) {
            LOG.errorf(e, "Failed to create user: %s", request.name());
            throw e;
        }
    }
}
```

### Log Levels

```java
// TRACE - Very detailed debugging
LOG.trace("Entering method with parameters...");

// DEBUG - Debugging information
LOG.debugf("Processing user: %s", userId);

// INFO - General information
LOG.infof("User created: %d", userId);

// WARN - Warning conditions
LOG.warnf("User not found: %d, using default", userId);

// ERROR - Error conditions
LOG.errorf("Failed to process user: %d", userId);
LOG.error("Critical error", exception);

// FATAL - Critical errors (rarely used)
LOG.fatal("System shutdown initiated");
```

### Structured Logging

```java
@ApplicationScoped
public class AuditService {

    private static final Logger LOG = Logger.getLogger(AuditService.class);

    public void logAudit(String action, String userId, Map<String, Object> details) {
        LOG.infof(
            "AUDIT: action=%s, userId=%s, timestamp=%s, details=%s",
            action,
            userId,
            LocalDateTime.now(),
            details
        );
    }
}
```

### Configuration

```properties
# Root log level
quarkus.log.level=INFO

# Package-specific levels
quarkus.log.category."com.example".level=DEBUG
quarkus.log.category."org.hibernate".level=WARN

# Console formatting
quarkus.log.console.format=%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c{3.}] (%t) %s%e%n
quarkus.log.console.color=true

# File logging
quarkus.log.file.enable=true
quarkus.log.file.path=/var/log/app.log
quarkus.log.file.rotation.max-file-size=10M
quarkus.log.file.rotation.max-backup-index=5

# JSON logging (production)
quarkus.log.console.json=true
quarkus.log.console.json.pretty-print=false
```

## Code Style

### Method Length

```java
// Keep methods short and focused (max 20-30 lines)
// Good
public User createUser(CreateUserRequest request) {
    validateRequest(request);
    User user = buildUser(request);
    persistUser(user);
    sendWelcomeEmail(user);
    return user;
}

// Bad - too long
public User createUser(CreateUserRequest request) {
    // 100 lines of code...
}
```

### Avoid Deep Nesting

```java
// Good - early returns
public User findActiveUser(Long id) {
    User user = userRepository.findById(id);
    if (user == null) {
        return null;
    }

    if (!user.active) {
        return null;
    }

    return user;
}

// Bad - deep nesting
public User findActiveUser(Long id) {
    User user = userRepository.findById(id);
    if (user != null) {
        if (user.active) {
            return user;
        }
    }
    return null;
}
```

### Use Optional Properly

```java
// Good - clear intent
public Optional<User> findByEmail(String email) {
    return Optional.ofNullable(
        userRepository.find("email", email).firstResult()
    );
}

// Usage
userService.findByEmail(email)
    .ifPresent(user -> LOG.infof("Found user: %s", user.name));

userService.findByEmail(email)
    .orElseThrow(() -> new UserNotFoundException(email));

// Avoid - unnecessary Optional
public Optional<String> getName() {
    return Optional.ofNullable(this.name);  // Just return String or null
}
```

### Stream Operations

```java
// Good - readable chain
List<String> activeUserNames = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .sorted()
    .toList();

// Use method references when possible
List<String> emails = users.stream()
    .map(User::getEmail)  // Not: u -> u.getEmail()
    .toList();

// Avoid - too complex
List<String> result = users.stream()
    .filter(u -> u.active && u.age > 18)
    .map(u -> u.name.toUpperCase())
    .sorted((a, b) -> b.compareTo(a))
    .limit(10)
    .skip(5)
    .collect(Collectors.toList());
```

## Documentation

### JavaDoc for Public APIs

```java
/**
 * Service for managing user accounts.
 *
 * <p>Provides operations for creating, updating, and deleting users.
 * All operations are transactional and validated.
 */
@ApplicationScoped
public class UserService {

    /**
     * Creates a new user account.
     *
     * @param request the user creation request containing name and email
     * @return the created user with generated ID
     * @throws DuplicateEmailException if email already exists
     * @throws ValidationException if request data is invalid
     */
    @Transactional
    public User createUser(CreateUserRequest request) {
        // ...
    }
}
```

### Comments

```java
// Good - explain why, not what
// Use cached value to avoid database query during session timeout
User cachedUser = sessionCache.get(userId);

// Bad - obvious comment
// Get user from cache
User cachedUser = sessionCache.get(userId);

// Good - document complex logic
// Calculate discount based on loyalty tier (Bronze: 5%, Silver: 10%, Gold: 15%)
// and apply seasonal multiplier during holiday periods (1.5x)
BigDecimal discount = calculateDiscount(user, product, currentDate);

// Use TODO for temporary code
// TODO: Replace with async processing after Kafka integration
processOrderSync(order);
```

## Testing Standards

See [testing.md](testing.md) for comprehensive testing patterns.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| CDI injection fails | Missing scope annotation | Add @ApplicationScoped or appropriate scope |
| Circular dependency | Beans injecting each other | Use @Inject + setter or refactor design |
| Logger not working | Wrong import | Use org.jboss.logging.Logger, not java.util.logging |
| NullPointerException | Null check missing | Use Optional or null checks |
| Memory leak | Holding references | Review object lifecycles and scopes |

## Code Quality Checklist

- [ ] All public classes have JavaDoc
- [ ] Methods are focused and < 30 lines
- [ ] No deep nesting (max 3 levels)
- [ ] Constants defined for magic values
- [ ] Exceptions handled appropriately
- [ ] Logging at appropriate levels
- [ ] Tests cover happy path and edge cases
- [ ] No code duplication
- [ ] Resource classes follow REST conventions
- [ ] DTOs are immutable (records)
- [ ] Proper CDI scopes used
- [ ] Validation annotations on DTOs
- [ ] Transaction boundaries clearly defined
