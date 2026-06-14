# Reactive Programming with Mutiny

Reactive patterns in Quarkus using Mutiny: Uni, Multi, reactive REST, reactive database access, and backpressure.

## Quick Reference

```java
// Uni - Single async value (like CompletableFuture)
@GET
@Path("/{id}")
public Uni<User> getUser(@PathParam("id") Long id) {
    return userRepository.findById(id)
        .onItem().ifNull().failWith(NotFoundException::new);
}

// Multi - Multiple async values (like Stream)
@GET
@Produces(MediaType.SERVER_SENT_EVENTS)
public Multi<User> streamUsers() {
    return userRepository.streamAll();
}

// Reactive composition
public Uni<OrderDto> createOrder(CreateOrderRequest request) {
    return userRepository.findById(request.userId())
        .onItem().ifNull().failWith(() -> new NotFoundException("User not found"))
        .chain(user -> productRepository.findById(request.productId()))
        .onItem().ifNull().failWith(() -> new NotFoundException("Product not found"))
        .chain(product -> saveOrder(request, product));
}
```

## Uni - Single Async Value

### Creating Uni

```java
// From item
Uni<String> uni = Uni.createFrom().item("hello");

// From supplier (lazy)
Uni<String> uni = Uni.createFrom().item(() -> expensiveOperation());

// From CompletionStage
Uni<String> uni = Uni.createFrom().completionStage(completableFuture);

// From failure
Uni<String> uni = Uni.createFrom().failure(new RuntimeException("Error"));

// Void/null result
Uni<Void> uni = Uni.createFrom().voidItem();
```

### Transforming Uni

```java
// Map (sync transformation)
Uni<String> result = uni
    .onItem().transform(value -> value.toUpperCase());

// Chain (async transformation)
Uni<UserDto> result = userRepository.findById(id)
    .onItem().transform(User::toDto);

// FlatMap/Chain (async that returns Uni)
Uni<Order> result = userRepository.findById(userId)
    .chain(user -> orderRepository.findByUser(user.id));

// Multiple transformations
Uni<String> result = uni
    .onItem().transform(String::toLowerCase)
    .onItem().transform(s -> s + " world")
    .onItem().transform(String::toUpperCase);
```

### Error Handling

```java
// Handle failures
Uni<User> result = userRepository.findById(id)
    .onFailure().recoverWithItem(new User("default"))
    .onFailure().transform(e -> new CustomException("User fetch failed", e));

// Retry on failure
Uni<User> result = userRepository.findById(id)
    .onFailure().retry().atMost(3)
    .onFailure().retry().withBackOff(Duration.ofSeconds(1));

// Timeout
Uni<User> result = userRepository.findById(id)
    .ifNoItem().after(Duration.ofSeconds(5))
    .fail();
```

### Conditional Logic

```java
// If null, fail
Uni<User> result = userRepository.findById(id)
    .onItem().ifNull().failWith(NotFoundException::new);

// If null, use default
Uni<User> result = userRepository.findById(id)
    .onItem().ifNull().continueWith(new User("guest"));

// If condition, fail
Uni<User> result = userRepository.findById(id)
    .onItem().invoke(user -> {
        if (!user.active) {
            throw new IllegalStateException("User inactive");
        }
    });
```

### Combining Unis

```java
// Combine 2 Unis
Uni<OrderDto> result = Uni.combine()
    .all()
    .unis(userRepository.findById(userId), productRepository.findById(productId))
    .asTuple()
    .onItem().transform(tuple -> {
        User user = tuple.getItem1();
        Product product = tuple.getItem2();
        return new OrderDto(user, product);
    });

// Combine multiple Unis
Uni<DashboardDto> result = Uni.combine()
    .all()
    .unis(
        userService.getUser(id),
        orderService.getOrders(id),
        productService.getRecommendations(id)
    )
    .combinedWith((user, orders, products) ->
        new DashboardDto(user, orders, products)
    );

// First to complete (race)
Uni<String> result = Uni.combine()
    .any()
    .of(service1.call(), service2.call())
    .with(String::valueOf);
```

## Multi - Multiple Async Values

### Creating Multi

```java
// From items
Multi<String> multi = Multi.createFrom().items("a", "b", "c");

// From iterable
Multi<User> multi = Multi.createFrom().iterable(userList);

// From range
Multi<Integer> multi = Multi.createFrom().range(1, 100);

// From ticks (periodic)
Multi<Long> multi = Multi.createFrom().ticks().every(Duration.ofSeconds(1));

// From Uni
Multi<User> multi = Multi.createFrom().uni(userRepository.findById(id));
```

### Transforming Multi

```java
// Map
Multi<String> result = multi
    .onItem().transform(User::getName);

// Filter
Multi<User> result = multi
    .select().where(User::isActive);

// FlatMap (async transformation)
Multi<Order> result = userMulti
    .onItem().transformToMulti(user ->
        orderRepository.findByUserId(user.id)
    );

// Skip and take
Multi<User> result = multi
    .select().first(10)
    .skip().first(5);  // Skip first 5, take next 10
```

### Collecting Multi

```java
// To list
Uni<List<User>> result = multi.collect().asList();

// To set
Uni<Set<User>> result = multi.collect().asSet();

// To map
Uni<Map<Long, User>> result = multi.collect().asMap(User::getId);

// Custom collector
Uni<String> result = multi
    .onItem().transform(User::getName)
    .collect().in(
        () -> new StringJoiner(", "),
        StringJoiner::add
    )
    .onItem().transform(StringJoiner::toString);
```

### Combining Multi

```java
// Merge (interleave)
Multi<User> result = Multi.createBy()
    .merging()
    .streams(multi1, multi2, multi3);

// Concatenate (sequential)
Multi<User> result = Multi.createBy()
    .concatenating()
    .streams(multi1, multi2, multi3);

// Combine latest
Multi<String> result = Multi.createBy()
    .combining()
    .streams(nameMulti, emailMulti)
    .using((name, email) -> name + " <" + email + ">");
```

### Backpressure

```java
// Buffer overflow strategy
Multi<User> result = multi
    .onOverflow().buffer(100);

// Drop on overflow
Multi<User> result = multi
    .onOverflow().drop();

// Request items explicitly
Multi<User> result = multi
    .capDemandsTo(10);  // Request max 10 items at a time
```

## Reactive REST Endpoints

### Simple Reactive Endpoint

```java
@Path("/users")
public class UserResource {

    @Inject
    UserRepository userRepository;

    @GET
    public Uni<List<User>> listUsers() {
        return userRepository.listAll();
    }

    @GET
    @Path("/{id}")
    public Uni<User> getUser(@PathParam("id") Long id) {
        return userRepository.findById(id)
            .onItem().ifNull().failWith(NotFoundException::new);
    }

    @POST
    public Uni<Response> createUser(@Valid CreateUserRequest request) {
        return userRepository.persist(
            new User(request.name(), request.email())
        )
        .onItem().transform(user ->
            Response.status(201).entity(user).build()
        );
    }

    @DELETE
    @Path("/{id}")
    public Uni<Response> deleteUser(@PathParam("id") Long id) {
        return userRepository.deleteById(id)
            .onItem().transform(deleted ->
                deleted ? Response.noContent().build()
                        : Response.status(404).build()
            );
    }
}
```

### Server-Sent Events (SSE)

```java
@Path("/events")
public class EventResource {

    @GET
    @Path("/users")
    @Produces(MediaType.SERVER_SENT_EVENTS)
    public Multi<User> streamUsers() {
        return Multi.createFrom().ticks().every(Duration.ofSeconds(1))
            .onItem().transformToUni(tick -> userRepository.findAll())
            .concatenate();
    }

    @GET
    @Path("/notifications")
    @Produces(MediaType.SERVER_SENT_EVENTS)
    @RestStreamElementType(MediaType.APPLICATION_JSON)
    public Multi<Notification> streamNotifications() {
        return notificationService.subscribe();
    }
}
```

### Streaming Responses

```java
@GET
@Path("/large-file")
@Produces(MediaType.APPLICATION_OCTET_STREAM)
public Multi<Buffer> downloadLargeFile() {
    return fileService.readFileChunks()
        .onItem().transform(chunk -> Buffer.buffer(chunk));
}
```

## Reactive Database Access

### Hibernate Reactive with Panache

```java
@Entity
public class User extends PanacheEntityBase {

    @Id
    @GeneratedValue
    public Long id;

    public String name;
    public String email;

    // Reactive queries
    public static Uni<User> findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public static Uni<List<User>> findActive() {
        return list("active", true);
    }

    public static Multi<User> streamAll() {
        return stream("active", true);
    }
}

// Repository
@ApplicationScoped
public class UserRepository implements PanacheRepositoryBase<User, Long> {

    public Uni<User> findByEmail(String email) {
        return find("email", email).firstResult();
    }

    public Uni<Long> countActive() {
        return count("active", true);
    }

    public Multi<User> streamActive() {
        return stream("active", true);
    }

    @WithTransaction
    public Uni<User> create(CreateUserRequest request) {
        User user = new User();
        user.name = request.name();
        user.email = request.email();
        return persist(user);
    }
}
```

### Reactive Transactions

```java
@ApplicationScoped
public class UserService {

    @Inject
    Mutiny.SessionFactory sessionFactory;

    public Uni<User> createUser(CreateUserRequest request) {
        return sessionFactory.withTransaction((session, tx) -> {
            User user = new User();
            user.name = request.name();
            user.email = request.email();
            return session.persist(user)
                .replaceWith(user);
        });
    }

    public Uni<Void> updateUserWithOrders(Long userId, List<Order> orders) {
        return sessionFactory.withTransaction((session, tx) ->
            session.find(User.class, userId)
                .chain(user -> {
                    if (user == null) {
                        return Uni.createFrom().failure(new NotFoundException());
                    }
                    // Update user and persist orders
                    return Multi.createFrom().iterable(orders)
                        .onItem().transformToUni(session::persist)
                        .concatenate()
                        .collect().asList()
                        .replaceWithVoid();
                })
        );
    }
}
```

## Reactive REST Client

```java
@RegisterRestClient(configKey = "user-service")
@Path("/users")
public interface ReactiveUserClient {

    @GET
    Uni<List<UserDto>> getAllUsers();

    @GET
    @Path("/{id}")
    Uni<UserDto> getUser(@PathParam("id") Long id);

    @POST
    Uni<UserDto> createUser(CreateUserRequest request);

    @DELETE
    @Path("/{id}")
    Uni<Void> deleteUser(@PathParam("id") Long id);
}

// Usage
@ApplicationScoped
public class OrderService {

    @Inject
    @RestClient
    ReactiveUserClient userClient;

    public Uni<OrderDto> createOrder(CreateOrderRequest request) {
        return userClient.getUser(request.userId())
            .onItem().ifNull().failWith(() -> new NotFoundException("User not found"))
            .chain(user -> {
                Order order = new Order();
                order.userId = user.id();
                return orderRepository.persist(order);
            })
            .onItem().transform(OrderDto::from);
    }
}
```

## Reactive Messaging (Kafka)

```java
@ApplicationScoped
public class OrderProcessor {

    @Inject
    @Channel("orders-out")
    Emitter<OrderEvent> orderEmitter;

    // Reactive consumer
    @Incoming("orders-in")
    public Uni<Void> processOrder(OrderEvent event) {
        return orderService.processOrder(event)
            .onItem().invoke(result ->
                LOG.infof("Order processed: %s", result.orderId())
            )
            .replaceWithVoid();
    }

    // Stream processing
    @Incoming("orders-in")
    @Outgoing("notifications-out")
    public Multi<NotificationEvent> processOrders(Multi<OrderEvent> orders) {
        return orders
            .onItem().transformToUni(this::processOrder)
            .concatenate()
            .onItem().transform(this::createNotification);
    }

    // Publish event
    public Uni<Void> publishOrder(OrderEvent event) {
        return Uni.createFrom().completionStage(
            orderEmitter.send(event)
        );
    }
}
```

## Advanced Patterns

### Retry with Exponential Backoff

```java
public Uni<User> getUserWithRetry(Long id) {
    return userClient.getUser(id)
        .onFailure().retry()
        .withBackOff(Duration.ofSeconds(1), Duration.ofSeconds(30))
        .withJitter(0.2)
        .atMost(5);
}
```

### Circuit Breaker (with Mutiny)

```java
@ApplicationScoped
public class ResilientService {

    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicBoolean circuitOpen = new AtomicBoolean(false);

    public Uni<Response> callWithCircuitBreaker() {
        if (circuitOpen.get()) {
            return Uni.createFrom().failure(
                new CircuitBreakerOpenException()
            );
        }

        return externalService.call()
            .onItem().invoke(() -> {
                failureCount.set(0);
                circuitOpen.set(false);
            })
            .onFailure().invoke(() -> {
                if (failureCount.incrementAndGet() >= 5) {
                    circuitOpen.set(true);
                    // Schedule reset after delay
                    scheduleCircuitReset();
                }
            });
    }
}
```

### Parallel Processing

```java
public Uni<List<UserDto>> processUsersInParallel(List<Long> userIds) {
    return Multi.createFrom().iterable(userIds)
        .onItem().transformToUni(id ->
            userService.enrichUser(id)  // Process each user
        )
        .merge(10)  // Process 10 in parallel
        .collect().asList();
}
```

### Caching with Uni

```java
@ApplicationScoped
public class CachedUserService {

    private final Map<Long, Uni<User>> cache = new ConcurrentHashMap<>();

    public Uni<User> getUser(Long id) {
        return cache.computeIfAbsent(id, userId ->
            userRepository.findById(userId)
                .memoize().indefinitely()  // Cache the Uni result
        );
    }

    public void invalidate(Long id) {
        cache.remove(id);
    }
}
```

## Testing Reactive Code

```java
@QuarkusTest
public class ReactiveUserResourceTest {

    @Test
    public void testGetUser() {
        User user = given()
            .pathParam("id", 1)
            .when().get("/users/{id}")
            .then()
            .statusCode(200)
            .extract().as(User.class);

        assertNotNull(user);
        assertEquals(1L, user.id);
    }

    @Test
    public void testCreateUser() {
        CreateUserRequest request = new CreateUserRequest("Test", "test@example.com");

        User user = given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(201)
            .extract().as(User.class);

        assertNotNull(user.id);
    }

    @Test
    public void testStreamUsers() {
        // SSE testing
        Client client = ClientBuilder.newClient();
        WebTarget target = client.target("http://localhost:8081/users/stream");

        SseEventSource source = SseEventSource.target(target).build();
        List<User> users = new CopyOnWriteArrayList<>();

        source.register(event -> {
            User user = Json.decodeValue(event.readData(), User.class);
            users.add(user);
        });

        source.open();
        await().atMost(10, TimeUnit.SECONDS).until(() -> users.size() > 0);
        source.close();

        assertTrue(users.size() > 0);
    }
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Blocking operation warning | Blocking call on IO thread | Use @Blocking or offload to worker thread |
| Memory leak with Multi | Not cancelling subscriptions | Use .select().first(N) or cancel properly |
| NullPointerException | Accessing null item | Use .onItem().ifNull() |
| Deadlock | Blocking reactive chain | Never block reactive pipelines |
| Slow performance | Too many concurrent operations | Limit concurrency with merge(N) |

## Best Practices

1. **Never block** reactive pipelines - use async operations
2. **Handle nulls explicitly** with .onItem().ifNull()
3. **Limit concurrency** for external calls with .merge(N)
4. **Use memoization** for expensive operations that can be cached
5. **Implement backpressure** for Multi streams
6. **Test with TestSubscriber** for fine-grained control
7. **Use @WithTransaction** for reactive database operations
8. **Prefer Uni over CompletionStage** in Quarkus for better composition
