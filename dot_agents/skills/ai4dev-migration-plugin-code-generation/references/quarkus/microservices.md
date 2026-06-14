# Quarkus Microservices

MicroProfile and microservices patterns: REST Client, fault tolerance, health checks, service discovery, and distributed tracing.

## Quick Reference

```java
// REST Client
@RegisterRestClient(configKey = "user-service")
@Path("/users")
public interface UserServiceClient {

    @GET
    @Path("/{id}")
    UserDto getUser(@PathParam("id") Long id);

    @POST
    User createUser(CreateUserRequest request);
}

// Fault tolerance
@ApplicationScoped
public class UserService {

    @Inject
    @RestClient
    UserServiceClient userServiceClient;

    @Retry(maxRetries = 3)
    @Timeout(value = 2, unit = ChronoUnit.SECONDS)
    @Fallback(fallbackMethod = "getUserFallback")
    public UserDto getUser(Long id) {
        return userServiceClient.getUser(id);
    }

    public UserDto getUserFallback(Long id) {
        return new UserDto(id, "Fallback User", "fallback@example.com");
    }
}
```

## REST Client

### Define Client Interface

```java
@RegisterRestClient(configKey = "product-service")
@Path("/api/v1/products")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public interface ProductServiceClient {

    @GET
    List<ProductDto> getAllProducts();

    @GET
    @Path("/{id}")
    ProductDto getProduct(@PathParam("id") Long id);

    @POST
    ProductDto createProduct(CreateProductRequest request);

    @PUT
    @Path("/{id}")
    ProductDto updateProduct(@PathParam("id") Long id, UpdateProductRequest request);

    @DELETE
    @Path("/{id}")
    void deleteProduct(@PathParam("id") Long id);

    @GET
    @Path("/search")
    List<ProductDto> search(@QueryParam("q") String query,
                            @QueryParam("page") int page,
                            @QueryParam("size") int size);
}
```

### Configuration

```properties
# REST Client configuration
quarkus.rest-client.product-service.url=http://localhost:8081
quarkus.rest-client.product-service.scope=jakarta.inject.Singleton
quarkus.rest-client.product-service.connect-timeout=5000
quarkus.rest-client.product-service.read-timeout=10000

# With service discovery (Consul/Kubernetes)
quarkus.rest-client.product-service.url=stork://product-service
```

### Using REST Client

```java
@ApplicationScoped
public class OrderService {

    @Inject
    @RestClient
    ProductServiceClient productServiceClient;

    @Inject
    @RestClient
    UserServiceClient userServiceClient;

    public OrderDto createOrder(CreateOrderRequest request) {
        // Call user service
        UserDto user = userServiceClient.getUser(request.userId());

        // Call product service
        ProductDto product = productServiceClient.getProduct(request.productId());

        // Create order
        Order order = new Order();
        order.userId = user.id();
        order.productId = product.id();
        order.total = product.price();

        return OrderDto.from(order);
    }
}
```

### Custom Headers and Filters

```java
// Client filter for authentication
@Provider
public class AuthenticationFilter implements ClientRequestFilter {

    @ConfigProperty(name = "api.key")
    String apiKey;

    @Override
    public void filter(ClientRequestContext context) {
        context.getHeaders().add("Authorization", "Bearer " + apiKey);
        context.getHeaders().add("X-API-Key", apiKey);
    }
}

// Logging filter
@Provider
public class LoggingFilter implements ClientRequestFilter, ClientResponseFilter {

    private static final Logger LOG = Logger.getLogger(LoggingFilter.class);

    @Override
    public void filter(ClientRequestContext request) {
        LOG.infof("Request: %s %s", request.getMethod(), request.getUri());
    }

    @Override
    public void filter(ClientRequestContext request, ClientResponseContext response) {
        LOG.infof("Response: %d", response.getStatus());
    }
}
```

## Fault Tolerance

### Retry

```java
@ApplicationScoped
public class ExternalService {

    @Inject
    @RestClient
    ExternalApiClient apiClient;

    @Retry(
        maxRetries = 3,
        delay = 1000,
        delayUnit = ChronoUnit.MILLIS,
        maxDuration = 10000,
        durationUnit = ChronoUnit.MILLIS,
        jitter = 200
    )
    public Response callExternalApi() {
        return apiClient.getData();
    }
}
```

### Timeout

```java
@Timeout(
    value = 5,
    unit = ChronoUnit.SECONDS
)
public ProductDto getProduct(Long id) {
    return productServiceClient.getProduct(id);
}
```

### Fallback

```java
@ApplicationScoped
public class UserService {

    @Inject
    @RestClient
    UserServiceClient userServiceClient;

    @Fallback(fallbackMethod = "getUserFromCache")
    public UserDto getUser(Long id) {
        return userServiceClient.getUser(id);
    }

    public UserDto getUserFromCache(Long id) {
        // Return cached data or default
        return cache.get(id).orElse(new UserDto(id, "Unknown", ""));
    }
}
```

### Circuit Breaker

```java
@CircuitBreaker(
    requestVolumeThreshold = 4,      // Min requests before evaluation
    failureRatio = 0.5,               // 50% failure rate to open
    delay = 10000,                    // Wait 10s before half-open
    delayUnit = ChronoUnit.MILLIS,
    successThreshold = 2              // 2 successes to close
)
@Fallback(fallbackMethod = "fallbackMethod")
public Response callUnreliableService() {
    return externalClient.call();
}

public Response fallbackMethod() {
    return Response.status(503)
        .entity(Map.of("error", "Service temporarily unavailable"))
        .build();
}
```

### Bulkhead

```java
// Limit concurrent executions
@Bulkhead(value = 5)  // Max 5 concurrent calls
public Response processRequest() {
    return heavyProcessing();
}

// With waiting queue
@Bulkhead(value = 5, waitingTaskQueue = 10)
public Response processWithQueue() {
    return heavyProcessing();
}
```

### Combined Resilience

```java
@ApplicationScoped
public class OrderService {

    @Inject
    @RestClient
    PaymentServiceClient paymentClient;

    @Retry(maxRetries = 2)
    @Timeout(value = 3, unit = ChronoUnit.SECONDS)
    @CircuitBreaker(
        requestVolumeThreshold = 4,
        failureRatio = 0.5,
        delay = 5000
    )
    @Fallback(fallbackMethod = "paymentFallback")
    public PaymentResult processPayment(PaymentRequest request) {
        return paymentClient.process(request);
    }

    public PaymentResult paymentFallback(PaymentRequest request) {
        LOG.warn("Payment service unavailable, queuing payment");
        queuePayment(request);
        return new PaymentResult("QUEUED", "Payment queued for processing");
    }
}
```

## Service Discovery (Stork)

### Configuration

```properties
# Stork service discovery
quarkus.stork.user-service.service-discovery=consul
quarkus.stork.user-service.service-discovery.consul-host=localhost
quarkus.stork.user-service.service-discovery.consul-port=8500

# Load balancing
quarkus.stork.user-service.load-balancer=round-robin

# Kubernetes service discovery
quarkus.stork.product-service.service-discovery=kubernetes
quarkus.stork.product-service.service-discovery.k8s-namespace=default
```

### Using with REST Client

```java
@RegisterRestClient(configKey = "user-service")
@Path("/users")
public interface UserServiceClient {
    @GET
    List<UserDto> getUsers();
}
```

```properties
# Use stork:// protocol for service discovery
quarkus.rest-client.user-service.url=stork://user-service
```

## Health Checks

### Liveness Check

```java
@Liveness
@ApplicationScoped
public class LivenessCheck implements HealthCheck {

    @Override
    public HealthCheckResponse call() {
        // Check if application is alive
        return HealthCheckResponse.up("application-liveness");
    }
}
```

### Readiness Check

```java
@Readiness
@ApplicationScoped
public class DatabaseReadinessCheck implements HealthCheck {

    @Inject
    DataSource dataSource;

    @Override
    public HealthCheckResponse call() {
        try (Connection conn = dataSource.getConnection()) {
            boolean isHealthy = conn.isValid(2);
            return HealthCheckResponse
                .named("database-readiness")
                .status(isHealthy)
                .withData("connection", "active")
                .build();
        } catch (SQLException e) {
            return HealthCheckResponse
                .down("database-readiness")
                .withData("error", e.getMessage())
                .build();
        }
    }
}
```

### Startup Check

```java
@Startup
@ApplicationScoped
public class StartupCheck implements HealthCheck {

    @Inject
    CacheService cacheService;

    @Override
    public HealthCheckResponse call() {
        boolean cacheReady = cacheService.isInitialized();
        return HealthCheckResponse
            .named("cache-startup")
            .status(cacheReady)
            .withData("cache_size", cacheService.size())
            .build();
    }
}
```

## Distributed Tracing

### Configuration

```properties
# OpenTelemetry tracing
quarkus.otel.exporter.otlp.traces.endpoint=http://jaeger:4317
quarkus.otel.traces.sampler=always_on
quarkus.application.name=my-service

# Or Jaeger directly
quarkus.jaeger.service-name=my-service
quarkus.jaeger.sampler-type=const
quarkus.jaeger.sampler-param=1
quarkus.jaeger.endpoint=http://localhost:14268/api/traces
```

### Custom Spans

```java
@ApplicationScoped
public class UserService {

    @Inject
    Tracer tracer;

    public User processUser(Long id) {
        Span span = tracer.spanBuilder("process-user")
            .setAttribute("user.id", id)
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Business logic
            User user = fetchUser(id);
            span.setAttribute("user.name", user.name);
            return user;
        } catch (Exception e) {
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

## Event-Driven (Kafka)

### Configuration

```properties
# Kafka configuration
kafka.bootstrap.servers=localhost:9092

# Incoming channel (consumer)
mp.messaging.incoming.orders.connector=smallrye-kafka
mp.messaging.incoming.orders.topic=orders
mp.messaging.incoming.orders.group.id=order-processor
mp.messaging.incoming.orders.auto.offset.reset=earliest

# Outgoing channel (producer)
mp.messaging.outgoing.notifications.connector=smallrye-kafka
mp.messaging.outgoing.notifications.topic=notifications
mp.messaging.outgoing.notifications.value.serializer=org.apache.kafka.common.serialization.StringSerializer
```

### Consumer

```java
@ApplicationScoped
public class OrderProcessor {

    private static final Logger LOG = Logger.getLogger(OrderProcessor.class);

    @Incoming("orders")
    @Acknowledgment(Acknowledgment.Strategy.POST_PROCESSING)
    public CompletionStage<Void> processOrder(Message<OrderEvent> message) {
        OrderEvent event = message.getPayload();
        LOG.infof("Processing order: %s", event.orderId());

        return CompletableFuture.runAsync(() -> {
            // Process order
            processOrderInternal(event);
        });
    }

    // Blocking consumer
    @Incoming("orders")
    @Blocking
    public void processOrderBlocking(OrderEvent event) {
        LOG.infof("Processing order: %s", event.orderId());
        processOrderInternal(event);
    }
}
```

### Producer

```java
@ApplicationScoped
public class NotificationService {

    @Inject
    @Channel("notifications")
    Emitter<NotificationEvent> notificationEmitter;

    public void sendNotification(String userId, String message) {
        NotificationEvent event = new NotificationEvent(userId, message);
        notificationEmitter.send(event);
    }

    // With acknowledgement
    public CompletionStage<Void> sendNotificationAsync(NotificationEvent event) {
        return notificationEmitter.send(event);
    }
}
```

## API Gateway Pattern

```java
@Path("/api/v1")
public class ApiGatewayResource {

    @Inject
    @RestClient
    UserServiceClient userService;

    @Inject
    @RestClient
    ProductServiceClient productService;

    @Inject
    @RestClient
    OrderServiceClient orderService;

    @GET
    @Path("/dashboard/{userId}")
    public DashboardDto getDashboard(@PathParam("userId") Long userId) {
        // Aggregate data from multiple services
        UserDto user = userService.getUser(userId);
        List<OrderDto> orders = orderService.getUserOrders(userId);
        List<ProductDto> recommendations = productService.getRecommendations(userId);

        return new DashboardDto(user, orders, recommendations);
    }
}
```

## Config Server Pattern

```java
@ConfigMapping(prefix = "app")
public interface AppConfig {
    String name();
    String version();
    Database database();

    interface Database {
        String host();
        int port();
        String name();
    }
}

// Inject and use
@Inject
AppConfig config;

String dbHost = config.database().host();
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| REST Client 404 | Wrong base URL | Check quarkus.rest-client.*.url |
| Circuit breaker always open | Too low threshold | Adjust requestVolumeThreshold and failureRatio |
| Timeout exceptions | Service slow | Increase timeout or optimize service |
| Service discovery fails | Consul/K8s not configured | Verify Stork configuration |
| Kafka consumer not starting | Wrong configuration | Check topic name and bootstrap servers |

## Best Practices

1. **Use circuit breakers** to prevent cascading failures
2. **Implement health checks** for liveness, readiness, and startup
3. **Add distributed tracing** for request correlation across services
4. **Use service discovery** instead of hardcoded URLs
5. **Implement fallbacks** for critical operations
6. **Set timeouts** on all external calls
7. **Use async/reactive** patterns for better resource utilization
8. **Monitor metrics** for circuit breaker states and latencies
