# Java / Spring Boot Code Patterns

## Project Structure

```
<service-name>/
├── pom.xml (or build.gradle)
├── Dockerfile
├── src/main/java/com/example/<service>/
│   ├── <Service>Application.java
│   ├── controller/
│   │   └── <Entity>Controller.java
│   ├── service/
│   │   └── <Entity>Service.java
│   ├── domain/
│   │   ├── <Entity>.java
│   │   └── <ValueObject>.java
│   ├── repository/
│   │   └── <Entity>Repository.java
│   ├── dto/
│   │   ├── <Entity>Request.java
│   │   └── <Entity>Response.java
│   ├── event/
│   │   └── <Entity>EventPublisher.java
│   ├── exception/
│   │   ├── <Domain>Exception.java
│   │   └── GlobalExceptionHandler.java
│   └── config/
│       └── <Feature>Config.java
├── src/main/resources/
│   ├── application.yml
│   └── db/migration/
│       └── V1__create_<table>.sql
└── src/test/java/com/example/<service>/
    ├── service/
    │   └── <Entity>ServiceTest.java
    └── controller/
        └── <Entity>ControllerTest.java
```

## Entity (Domain Model)

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String customerId;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal total;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderLine> lines = new ArrayList<>();
}
```

## Repository

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(String customerId);
    Optional<Order> findByIdAndStatus(Long id, OrderStatus status);

    @Query("SELECT o FROM Order o WHERE o.total > :amount AND o.status = :status")
    List<Order> findHighValueByStatus(@Param("amount") BigDecimal amount, @Param("status") OrderStatus status);
}
```

## Service (Business Logic)

```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    private final OrderValidator validator;
    private final OrderEventPublisher eventPublisher;

    // Implements: BR-001
    public Order createOrder(CreateOrderRequest request) {
        validator.validateCreditLimit(request);
        Order order = mapToEntity(request);
        order.setStatus(OrderStatus.PENDING);
        Order saved = orderRepository.save(order);
        eventPublisher.publishOrderCreated(saved);
        return saved;
    }
}
```

## Controller

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService orderService;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody CreateOrderRequest request) {
        Order order = orderService.createOrder(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(OrderResponse.from(order));
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrderResponse> getOrder(@PathVariable Long id) {
        return orderService.findById(id)
            .map(OrderResponse::from)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

## DTO (Request/Response)

```java
public record CreateOrderRequest(
    @NotBlank String customerId,
    @NotEmpty List<OrderLineRequest> lines
) {}

public record OrderResponse(
    Long id,
    String customerId,
    BigDecimal total,
    String status,
    Instant createdAt
) {
    public static OrderResponse from(Order order) {
        return new OrderResponse(order.getId(), order.getCustomerId(),
            order.getTotal(), order.getStatus().name(), order.getCreatedAt());
    }
}
```

## Exception Handling

```java
public class CreditLimitExceededException extends RuntimeException {
    private final String customerId;
    private final BigDecimal requested;
    private final BigDecimal available;

    public CreditLimitExceededException(String customerId, BigDecimal requested, BigDecimal available) {
        super("Credit limit exceeded for customer " + customerId);
        this.customerId = customerId;
        this.requested = requested;
        this.available = available;
    }
}

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(CreditLimitExceededException.class)
    public ResponseEntity<ErrorResponse> handleCreditLimit(CreditLimitExceededException ex) {
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(new ErrorResponse("CREDIT_LIMIT_EXCEEDED", ex.getMessage()));
    }
}
```

## Event Publishing

```java
@Component
public class OrderEventPublisher {
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public void publishOrderCreated(Order order) {
        OrderEvent event = new OrderEvent(order.getId(), "CREATED", Instant.now());
        kafkaTemplate.send("orders.events", order.getId().toString(), event);
    }
}
```

## Test Patterns

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock private OrderRepository orderRepository;
    @Mock private OrderValidator validator;
    @Mock private OrderEventPublisher eventPublisher;
    @InjectMocks private OrderService orderService;

    // Covers: TC-001
    @Test
    void createOrder_validRequest_returnsCreatedOrder() {
        CreateOrderRequest request = new CreateOrderRequest("CUST-1", List.of(...));
        when(orderRepository.save(any())).thenAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(1L);
            return o;
        });

        Order result = orderService.createOrder(request);

        assertThat(result.getStatus()).isEqualTo(OrderStatus.PENDING);
        verify(eventPublisher).publishOrderCreated(any());
    }

    // Covers: TC-002
    @Test
    void createOrder_creditExceeded_throwsException() {
        CreateOrderRequest request = new CreateOrderRequest("CUST-1", List.of(...));
        doThrow(new CreditLimitExceededException("CUST-1", new BigDecimal("300"), new BigDecimal("200")))
            .when(validator).validateCreditLimit(request);

        assertThrows(CreditLimitExceededException.class, () -> orderService.createOrder(request));
    }
}
```

## Migration (Flyway)

```sql
-- V1__create_orders.sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
```
