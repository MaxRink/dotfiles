# Quarkus Core

Quarkus 3.x: REST APIs (JAX-RS), CDI (dependency injection), Configuration, Health, Metrics, OpenAPI, and cloud-native patterns.

## Quick Reference

```java
// REST Resource
@Path("/users")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class UserResource {

    @Inject
    UserService userService;

    @GET
    public List<UserResponse> list() {
        return userService.findAll();
    }

    @GET
    @Path("/{id}")
    public UserResponse getById(@PathParam("id") Long id) {
        return userService.findById(id)
            .orElseThrow(() -> new NotFoundException("User not found"));
    }

    @POST
    @Transactional
    public Response create(@Valid CreateUserRequest request) {
        User user = userService.create(request);
        return Response.status(201)
            .entity(UserResponse.from(user))
            .build();
    }
}
```

## REST Resources (JAX-RS)

### Annotations

```java
@Path("/api/v1/users")              // Base path
@Produces(MediaType.APPLICATION_JSON) // Default response type
@Consumes(MediaType.APPLICATION_JSON) // Default request type
public class UserResource {

    @GET                             // HTTP GET
    @Path("/{id}")                   // Path parameter
    public User getById(@PathParam("id") Long id) {}

    @GET
    @Path("/search")
    public List<User> search(@QueryParam("name") String name) {}

    @POST
    public Response create(CreateUserRequest request) {}

    @PUT
    @Path("/{id}")
    public User update(@PathParam("id") Long id, UpdateUserRequest request) {}

    @DELETE
    @Path("/{id}")
    public Response delete(@PathParam("id") Long id) {
        return Response.noContent().build();
    }
}
```

### Response Building

```java
// 200 OK
return Response.ok(user).build();

// 201 Created with Location header
URI location = URI.create("/users/" + user.getId());
return Response.created(location).entity(user).build();

// 204 No Content
return Response.noContent().build();

// 400 Bad Request
return Response.status(400).entity(error).build();

// Custom headers
return Response.ok(user)
    .header("X-Total-Count", "100")
    .build();
```

## Dependency Injection (CDI)

### @Inject vs @ApplicationScoped

```java
// Service with application scope
@ApplicationScoped
public class UserService {

    @Inject
    UserRepository userRepository;

    @Inject
    EmailService emailService;

    public User create(CreateUserRequest request) {
        // Business logic
    }
}

// Request-scoped bean
@RequestScoped
public class RequestContext {
    private String requestId = UUID.randomUUID().toString();

    public String getRequestId() {
        return requestId;
    }
}
```

### Bean Scopes

| Scope | Lifecycle | Use Case |
|-------|-----------|----------|
| @ApplicationScoped | One instance per app | Services, repositories, stateless beans |
| @RequestScoped | One per HTTP request | Request-specific data |
| @Dependent | New instance each injection | Stateful, short-lived objects |
| @Singleton | Same as ApplicationScoped | Legacy support, prefer @ApplicationScoped |

### Producer Methods

```java
@ApplicationScoped
public class Configuration {

    @Produces
    @ApplicationScoped
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }

    @Produces
    @Named("userCache")
    public Cache<Long, User> userCache() {
        return Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .build();
    }
}
```

## Configuration

### application.properties

```properties
# Server configuration
quarkus.http.port=8080
quarkus.http.host=0.0.0.0

# Database
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=user
quarkus.datasource.password=${DB_PASSWORD}
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/mydb

# Hibernate
quarkus.hibernate-orm.database.generation=update
quarkus.hibernate-orm.log.sql=true

# Logging
quarkus.log.level=INFO
quarkus.log.category."com.example".level=DEBUG

# CORS
quarkus.http.cors=true
quarkus.http.cors.origins=http://localhost:3000
quarkus.http.cors.methods=GET,POST,PUT,DELETE
```

### Injecting Configuration

```java
@ApplicationScoped
public class AppConfig {

    @ConfigProperty(name = "app.name")
    String appName;

    @ConfigProperty(name = "app.max-users", defaultValue = "1000")
    int maxUsers;

    @ConfigProperty(name = "app.features")
    List<String> features;

    @ConfigProperty(name = "app.api-key")
    Optional<String> apiKey;
}
```

### Config Mapping (Recommended)

```java
@ConfigMapping(prefix = "app")
public interface AppConfiguration {
    String name();
    int maxUsers();
    List<String> features();
    Optional<String> apiKey();

    Database database();

    interface Database {
        String host();
        int port();
        String name();
    }
}

// Inject
@Inject
AppConfiguration config;
```

## Validation

```java
// Request DTO with validation
public record CreateUserRequest(
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    String name,

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    String email,

    @Min(18)
    @Max(120)
    Integer age
) {}

// In Resource - validation happens automatically
@POST
public Response create(@Valid CreateUserRequest request) {
    // request is already validated
}
```

### Custom Validators

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UsernameValidator.class)
public @interface ValidUsername {
    String message() default "Invalid username";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class UsernameValidator implements ConstraintValidator<ValidUsername, String> {
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        return value != null && value.matches("^[a-zA-Z0-9_]{3,20}$");
    }
}
```

## Health Checks

```java
@ApplicationScoped
@Liveness  // or @Readiness
public class DatabaseHealthCheck implements HealthCheck {

    @Inject
    DataSource dataSource;

    @Override
    public HealthCheckResponse call() {
        try (Connection conn = dataSource.getConnection()) {
            boolean isHealthy = conn.isValid(2);
            return HealthCheckResponse
                .named("database")
                .status(isHealthy)
                .withData("connection", "active")
                .build();
        } catch (Exception e) {
            return HealthCheckResponse
                .down("database")
                .withData("error", e.getMessage())
                .build();
        }
    }
}
```

Access health checks:

- Liveness: `GET /q/health/live`
- Readiness: `GET /q/health/ready`
- All: `GET /q/health`

## Metrics

```java
@ApplicationScoped
public class UserService {

    @Inject
    MeterRegistry registry;

    @Counted(name = "users.created")
    @Timed(name = "users.create.time")
    public User create(CreateUserRequest request) {
        Counter counter = registry.counter("users.active");
        counter.increment();

        // Business logic
    }
}
```

Access metrics: `GET /q/metrics`

## OpenAPI & Swagger UI

```java
@Path("/users")
@Tag(name = "Users", description = "User management operations")
public class UserResource {

    @GET
    @Path("/{id}")
    @Operation(summary = "Get user by ID")
    @APIResponse(responseCode = "200", description = "User found")
    @APIResponse(responseCode = "404", description = "User not found")
    public UserResponse getById(@PathParam("id") Long id) {
        // ...
    }
}
```

Access Swagger UI: `http://localhost:8080/q/swagger-ui`

## Exception Handling

```java
// Global exception mapper
@Provider
public class GlobalExceptionMapper implements ExceptionMapper<Exception> {

    private static final Logger LOG = Logger.getLogger(GlobalExceptionMapper.class);

    @Override
    public Response toResponse(Exception exception) {
        LOG.error("Unhandled exception", exception);

        ErrorResponse error = new ErrorResponse(
            "Internal server error",
            exception.getMessage(),
            LocalDateTime.now()
        );

        return Response.status(500).entity(error).build();
    }
}

// Validation exception mapper
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
```

## Filters and Interceptors

```java
// Request filter (e.g., logging)
@Provider
public class LoggingFilter implements ContainerRequestFilter {

    private static final Logger LOG = Logger.getLogger(LoggingFilter.class);

    @Override
    public void filter(ContainerRequestContext context) {
        LOG.infof("Request: %s %s",
            context.getMethod(),
            context.getUriInfo().getPath());
    }
}

// Response filter
@Provider
public class CorsFilter implements ContainerResponseFilter {

    @Override
    public void filter(ContainerRequestContext request, ContainerResponseContext response) {
        response.getHeaders().add("X-Custom-Header", "value");
    }
}
```

## Async Processing

```java
@Path("/users")
public class UserResource {

    @Inject
    UserService userService;

    // CompletionStage (async)
    @GET
    @Path("/async/{id}")
    public CompletionStage<UserResponse> getAsync(@PathParam("id") Long id) {
        return CompletableFuture.supplyAsync(() ->
            userService.findById(id)
                .orElseThrow(() -> new NotFoundException())
        );
    }

    // Uni (reactive with Mutiny)
    @GET
    @Path("/reactive/{id}")
    public Uni<UserResponse> getReactive(@PathParam("id") Long id) {
        return Uni.createFrom().item(
            () -> userService.findById(id)
                .orElseThrow(() -> new NotFoundException())
        );
    }
}
```

## Scheduled Tasks

```java
@ApplicationScoped
public class ScheduledJobs {

    private static final Logger LOG = Logger.getLogger(ScheduledJobs.class);

    @Scheduled(every = "10s")
    void everyTenSeconds() {
        LOG.info("Running every 10 seconds");
    }

    @Scheduled(cron = "0 0 2 * * ?")  // 2 AM daily
    void dailyCleanup() {
        LOG.info("Daily cleanup");
    }
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| CDI injection fails | No @ApplicationScoped on bean | Add scope annotation |
| Config not found | Missing property | Add to application.properties or provide default |
| Validation not working | Missing @Valid annotation | Add @Valid to method parameter |
| 404 on endpoint | Wrong @Path | Check resource paths and HTTP methods |
| Native build fails | Reflection not registered | Add @RegisterForReflection |
