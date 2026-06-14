# Java Microservices

Spring Cloud: Config Server, service discovery, API Gateway, Resilience4j, event-driven (Kafka/RabbitMQ), observability.

## Quick Reference

```java
// Feign Client with Resilience4j
@FeignClient(name = "order-service", fallback = OrderClientFallback.class)
public interface OrderClient {
    @GetMapping("/api/orders/{id}")
    OrderDto getOrder(@PathVariable Long id);
}

@Component
public class OrderClientFallback implements OrderClient {
    @Override
    public OrderDto getOrder(Long id) {
        return OrderDto.empty();
    }
}

// Circuit Breaker
@CircuitBreaker(name = "orderService", fallbackMethod = "getOrderFallback")
@Retry(name = "orderService")
public OrderDto getOrder(Long orderId) {
    return orderClient.getOrder(orderId);
}

public OrderDto getOrderFallback(Long orderId, Exception ex) {
    log.warn("Fallback for order {}: {}", orderId, ex.getMessage());
    return OrderDto.empty();
}

// Event-driven with Spring Cloud Stream
@Bean
public Function<Flux<OrderCreatedEvent>, Flux<NotificationEvent>> processOrders() {
    return events -> events
        .map(event -> new NotificationEvent(event.orderId(), "Order confirmed"))
        .onErrorContinue((ex, obj) -> log.error("Processing failed", ex));
}
```

## Service Configuration

```yaml
spring:
  application:
    name: order-service
  cloud:
    config:
      uri: ${CONFIG_SERVER_URL:http://localhost:8888}
      fail-fast: true

eureka:
  client:
    service-url:
      defaultZone: ${EUREKA_URL:http://localhost:8761/eureka}
  instance:
    prefer-ip-address: true

resilience4j:
  circuitbreaker:
    instances:
      orderService:
        sliding-window-size: 10
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
  retry:
    instances:
      orderService:
        max-attempts: 3
        wait-duration: 1s
        exponential-backoff-multiplier: 2
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Service not discovered | Registration delay | Check eureka heartbeat |
| Circuit breaker stuck open | Failure threshold reached | Adjust sliding window |
| Message lost | Missing ack/commit | Enable manual acknowledgement |
| Timeout cascade | Missing per-service timeouts | Configure individual timeouts |
| Config not refreshing | Missing @RefreshScope | Add annotation, use Spring Bus |
