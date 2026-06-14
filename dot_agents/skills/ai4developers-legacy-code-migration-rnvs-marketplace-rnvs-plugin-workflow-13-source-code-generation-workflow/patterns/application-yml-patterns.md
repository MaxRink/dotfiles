# Application Configuration Patterns

Patterns for Spring Boot application.yml files in VNRM microservices.

---

## Pattern 1: Complete Application Configuration (NEW Mode)

Standard application.yml for a new VNRM microservice:

```yaml
# application.yml
# ${Module Name} Service Configuration

spring:
  application:
    name: ${module-name}-service

  profiles:
    active: ${SPRING_PROFILES_ACTIVE:local}

  # Database Configuration
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:vnrm}
    username: ${DB_USERNAME:vnrm}
    password: ${DB_PASSWORD:vnrm}
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: ${DB_POOL_SIZE:10}
      minimum-idle: ${DB_MIN_IDLE:2}
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  jpa:
    hibernate:
      ddl-auto: none  # Managed by Liquibase
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        jdbc:
          time_zone: UTC
    open-in-view: false

  # Liquibase Configuration
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
    contexts: ${LIQUIBASE_CONTEXTS:default}

  # Cache Configuration
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=10m

# Server Configuration
server:
  port: ${SERVER_PORT:8080}
  servlet:
    context-path: /api/v1/${module-name}
  compression:
    enabled: true
    mime-types: application/json,application/xml,text/html,text/xml,text/plain

# Actuator Configuration
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when_authorized
      probes:
        enabled: true
  health:
    circuitbreakers:
      enabled: true

# Horizon Event Bus Configuration (Telekom)
horizon:
  enabled: true
  client:
    id: ${module-name}-service
    environment: ${HORIZON_ENV:development}
  publisher:
    enabled: true
  subscriber:
    enabled: true
    topics:
      - ${domain}.${resource}.created
      - ${domain}.${resource}.updated
      - ${domain}.${resource}.deleted

# Resilience4j Configuration
resilience4j:
  circuitbreaker:
    configs:
      default:
        register-health-indicator: true
        sliding-window-size: 10
        minimum-number-of-calls: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
    instances:
      rnps:
        base-config: default
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
      carrier:
        base-config: default
        failure-rate-threshold: 60
        wait-duration-in-open-state: 60s

  retry:
    configs:
      default:
        max-attempts: 3
        wait-duration: 1s
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2
        retry-exceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
    instances:
      rnps:
        base-config: default
        max-attempts: 3
      carrier:
        base-config: default
        max-attempts: 5

  timelimiter:
    configs:
      default:
        timeout-duration: 10s
        cancel-running-future: true

# Application-Specific Configuration
${module}:
  escalation:
    level1-threshold-hours: 24
    level2-threshold-hours: 48
    auto-escalation-enabled: true
  notification:
    enabled: true
    from-address: ${module}-noreply@telekom.de
    sla-minutes: 5
    max-retries: 3
  sync:
    enabled: true
    batch-size: 100
    cron: "0 */15 * * * *"  # Every 15 minutes

# Logging Configuration
logging:
  level:
    root: INFO
    de.telekom.vnrm: DEBUG
    org.springframework.web: INFO
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql: TRACE
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"

# OpenAPI Documentation
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    operations-sorter: method
```

---

## Pattern 2: Local Development Profile

application-local.yml for local development:

```yaml
# application-local.yml
# Local development overrides

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/vnrm_local
    username: postgres
    password: postgres

  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true

  liquibase:
    contexts: local,default

horizon:
  client:
    environment: local
  mock-mode: true  # Use mock for local development

resilience4j:
  circuitbreaker:
    instances:
      rnps:
        failure-rate-threshold: 100  # Disable in local
      carrier:
        failure-rate-threshold: 100

logging:
  level:
    de.telekom.vnrm: TRACE
    org.springframework.web: DEBUG
```

---

## Pattern 3: Production Profile

application-prod.yml for production:

```yaml
# application-prod.yml
# Production configuration

spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

  jpa:
    show-sql: false
    properties:
      hibernate:
        format_sql: false

  liquibase:
    contexts: prod,default

server:
  compression:
    enabled: true

management:
  endpoint:
    health:
      show-details: never

logging:
  level:
    root: WARN
    de.telekom.vnrm: INFO
    org.hibernate.SQL: WARN
```

---

## Pattern 4: Add Configuration Properties (CHANGE Mode)

When adding new configuration to existing application.yml:

```yaml
# MODIFICATION: Add under existing configuration

# Feature-specific configuration
${feature}:
  queue:
    enabled: true
    max-size: 1000
    poll-interval-seconds: 30

  validation:
    enabled: true
    strict-mode: false
    rules:
      - RULE_001
      - RULE_002

  integration:
    timeout-seconds: 30
    retry-attempts: 3
    circuit-breaker-enabled: true
```

---

## Pattern 5: Resilience4j Instance Configuration

Add new circuit breaker instance:

```yaml
# MODIFICATION: Add under resilience4j.circuitbreaker.instances

resilience4j:
  circuitbreaker:
    instances:
      ${service-name}:
        base-config: default
        failure-rate-threshold: 50
        minimum-number-of-calls: 5
        wait-duration-in-open-state: 30s
        sliding-window-size: 10
        record-exceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
          - ${package}.exception.${Service}ConnectionException
```

---

## Anti-Patterns to Avoid

1. **Don't use Kafka configuration** - VNRM uses Horizon Event Bus
2. **Don't hardcode secrets** - Use environment variables
3. **Don't enable ddl-auto in production** - Use Liquibase
4. **Don't expose all actuator endpoints** - Limit to health, info, metrics
5. **Don't use show-sql in production** - Performance impact
6. **Don't skip circuit breaker health indicators** - Required for monitoring
