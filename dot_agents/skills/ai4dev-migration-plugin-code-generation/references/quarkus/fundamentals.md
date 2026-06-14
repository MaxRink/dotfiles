# Java Fundamentals for Quarkus

Core Java 17–21: syntax, OOP, records, sealed classes, pattern matching, collections, streams, exception handling.

Quarkus requires **Java 17+** and fully supports Java 21 features.

## Quick Reference

```java
// Record (Java 16+) - Perfect for DTOs
public record UserDto(String name, String email) {}

// Pattern matching (Java 21)
String format(Object obj) {
    return switch (obj) {
        case Integer i -> "Int: %d".formatted(i);
        case String s  -> "String: %s".formatted(s);
        default        -> obj.toString();
    };
}

// Stream operations
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .sorted()
    .toList();

// Optional handling
String name = Optional.ofNullable(user)
    .map(User::getName)
    .orElse("Unknown");
```

## Collection Selection Guide

| Need | Use | Reason |
|------|-----|--------|
| Indexed access | ArrayList | O(1) random access |
| Unique elements | HashSet | O(1) contains |
| Sorted unique | TreeSet | O(log n) sorted |
| Key-value pairs | HashMap | O(1) get/put |
| Thread-safe map | ConcurrentHashMap | Segment locking |
| FIFO queue | ArrayDeque | Fast at both ends |

## Records for DTOs (Java 17+)

Quarkus works exceptionally well with Java records for DTOs:

```java
// Request DTO
public record CreateUserRequest(
    @NotBlank String name,
    @Email String email,
    String role
) {}

// Response DTO
public record UserResponse(
    Long id,
    String name,
    String email,
    LocalDateTime createdAt
) {
    // Factory method from entity
    public static UserResponse from(User user) {
        return new UserResponse(
            user.getId(),
            user.getName(),
            user.getEmail(),
            user.getCreatedAt()
        );
    }
}
```

## Exception Handling

```java
// Custom exception
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long id) {
        super("User not found: " + id);
    }
}

// Exception mapper (Quarkus will pick this up)
@Provider
public class UserNotFoundExceptionMapper implements ExceptionMapper<UserNotFoundException> {
    @Override
    public Response toResponse(UserNotFoundException exception) {
        return Response.status(404)
            .entity(Map.of("error", exception.getMessage()))
            .build();
    }
}
```

## Modern Java Features in Quarkus

### Text Blocks (Java 15+)

```java
String json = """
    {
        "name": "%s",
        "email": "%s"
    }
    """.formatted(name, email);
```

### Sealed Classes (Java 17+)

```java
public sealed interface Result<T> permits Success, Error {
    record Success<T>(T value) implements Result<T> {}
    record Error<T>(String message) implements Result<T> {}
}
```

### Virtual Threads (Java 21+)

Quarkus has excellent virtual thread support:

```java
@Path("/users")
@RunOnVirtualThread  // Enable virtual threads for this endpoint
public class UserResource {
    @GET
    public List<User> getUsers() {
        // Blocking calls are now cheap with virtual threads
        return userRepository.listAll();
    }
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| NullPointerException | Null reference | Use Optional, @NonNull annotations |
| ConcurrentModificationException | Modify during iteration | Use Iterator.remove() or stream operations |
| ClassCastException | Wrong type | Use generics, pattern matching |
| OutOfMemoryError | Large collections | Profile heap, use pagination |
| StackOverflowError | Infinite recursion | Add base case, check circular dependencies |
