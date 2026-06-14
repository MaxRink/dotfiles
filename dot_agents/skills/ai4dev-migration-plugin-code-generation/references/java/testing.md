# Java Testing

JUnit 5, Mockito, AssertJ, Spring Boot test slices, Testcontainers, TDD workflow, JaCoCo coverage, ArchUnit, Pact, PIT mutation testing.

## TDD Workflow

1. **Write tests first** — they should fail (Red)
2. **Implement minimal code** to pass (Green)
3. **Refactor** with tests green
4. **Enforce coverage** with JaCoCo (80%+ line coverage)

## Unit Tests (JUnit 5 + Mockito)

### BDD-Style Unit Test

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock private UserRepository userRepository;
    @InjectMocks private UserService userService;

    @Test
    @DisplayName("Should find user by ID")
    void shouldFindUserById() {
        given(userRepository.findById(1L)).willReturn(Optional.of(new User(1L, "John")));

        Optional<User> result = userService.findById(1L);

        assertThat(result).isPresent()
            .hasValueSatisfying(u -> assertThat(u.getName()).isEqualTo("John"));
        then(userRepository).should().findById(1L);
    }
}
```

### Spring Boot Service Test (Arrange-Act-Assert)

```java
@ExtendWith(MockitoExtension.class)
class MarketServiceTest {
  @Mock MarketRepository repo;
  @InjectMocks MarketService service;

  @Test
  void createsMarket() {
    when(repo.save(any())).thenAnswer(inv -> inv.getArgument(0));

    Market result = service.create(new CreateMarketRequest("name", "desc", Instant.now(), List.of("cat")));

    assertThat(result.name()).isEqualTo("name");
    verify(repo).save(any());
  }
}
```

### Parameterized Test

```java
@ParameterizedTest
@CsvSource({"valid@email.com, true", "invalid-email, false", "'', false"})
void shouldValidateEmail(String email, boolean expected) {
    assertThat(validator.isValid(email)).isEqualTo(expected);
}
```

## Web Layer Tests (MockMvc)

```java
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;

  @Test
  void returnsMarkets() throws Exception {
    when(marketService.list(any())).thenReturn(Page.empty());

    mockMvc.perform(get("/api/markets"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.content").isArray());
  }
}
```

## Integration Tests (@SpringBootTest)

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class MarketIntegrationTest {
  @Autowired MockMvc mockMvc;

  @Test
  void createsMarket() throws Exception {
    mockMvc.perform(post("/api/markets")
        .contentType(MediaType.APPLICATION_JSON)
        .content("""
          {"name":"Test","description":"Desc","endDate":"2030-01-01T00:00:00Z","categories":["general"]}
        """))
      .andExpect(status().isCreated());
  }
}
```

## Persistence Tests (@DataJpaTest)

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainersConfig.class)
class MarketRepositoryTest {
  @Autowired MarketRepository repo;

  @Test
  void savesAndFinds() {
    MarketEntity entity = new MarketEntity();
    entity.setName("Test");
    repo.save(entity);

    Optional<MarketEntity> found = repo.findByName("Test");
    assertThat(found).isPresent();
  }
}
```

## Testcontainers

Use reusable containers for Postgres/Redis to mirror production.

```java
@Testcontainers
@SpringBootTest
class OrderRepositoryIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired private OrderRepository repository;

    @Test
    void shouldPersistOrder() {
        Order saved = repository.save(new Order("item", 100.0));
        assertThat(saved.getId()).isNotNull();
    }
}
```

### Testcontainers — Kafka

```java
@Testcontainers
@SpringBootTest
class OrderEventIT {

    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Autowired private KafkaTemplate<String, String> template;

    @Test
    void shouldPublishOrderEvent() {
        template.send("orders", "{\"orderId\": 1}").get(10, TimeUnit.SECONDS);
        // verify consumer received event
    }
}
```

## Test Data Builders

```java
public class UserTestBuilder {
    private Long id = 1L;
    private String name = "John Doe";
    private String email = "john@example.com";
    private boolean active = true;

    public static UserTestBuilder aUser() { return new UserTestBuilder(); }
    public UserTestBuilder withName(String name) { this.name = name; return this; }
    public UserTestBuilder inactive() { this.active = false; return this; }
    public User build() { return new User(id, name, email, active); }
}

class MarketBuilder {
  private String name = "Test";
  MarketBuilder withName(String name) { this.name = name; return this; }
  Market build() { return new Market(null, name, MarketStatus.ACTIVE); }
}
```

## Coverage (JaCoCo)

### Coverage Rules

```xml
<!-- JaCoCo minimum 80% line coverage -->
<configuration>
    <rules>
        <rule>
            <element>BUNDLE</element>
            <limits>
                <limit>
                    <counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.80</minimum>
                </limit>
            </limits>
        </rule>
    </rules>
</configuration>
```

### Maven Plugin

```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.14</version>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals><goal>report</goal></goals>
    </execution>
  </executions>
</plugin>
```

## CI Commands

- Maven: `mvn -T 4 test` or `mvn verify`
- Gradle: `./gradlew test jacocoTestReport`

## Architecture Testing (ArchUnit)

```java
@AnalyzeClasses(packages = "com.example")
class ArchitectureTest {

    @ArchTest
    static final ArchRule layerDependencies = layeredArchitecture()
        .consideringAllDependencies()
        .layer("Controller").definedBy("..controller..")
        .layer("Service").definedBy("..service..")
        .layer("Repository").definedBy("..repository..")
        .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
        .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller")
        .whereLayer("Repository").mayOnlyBeAccessedByLayers("Service");

    @ArchTest
    static final ArchRule noFieldInjection = noFields()
        .should().beAnnotatedWith("org.springframework.beans.factory.annotation.Autowired")
        .because("Use constructor injection instead");
}
```

## Contract Testing (Pact)

```java
@ExtendWith(PactConsumerTestExt.class)
class OrderClientContractTest {

    @Pact(consumer = "order-ui", provider = "order-service")
    V4Pact getOrderPact(PactDslWithProvider builder) {
        return builder
            .given("order 1 exists")
            .uponReceiving("get order by id")
            .path("/api/orders/1")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(newJsonBody(body -> {
                body.integerType("id", 1);
                body.stringType("status", "CONFIRMED");
            }).build())
            .toPact(V4Pact.class);
    }

    @Test
    @PactTestFor(pactMethod = "getOrderPact")
    void shouldGetOrder(MockServer mockServer) {
        OrderClient client = new OrderClient(mockServer.getUrl());
        OrderDto order = client.getOrder(1L);
        assertThat(order.getStatus()).isEqualTo("CONFIRMED");
    }
}
```

## Mutation Testing (PIT)

```xml
<plugin>
    <groupId>org.pitest</groupId>
    <artifactId>pitest-maven</artifactId>
    <version>1.15.3</version>
    <dependencies>
        <dependency>
            <groupId>org.pitest</groupId>
            <artifactId>pitest-junit5-plugin</artifactId>
            <version>1.2.1</version>
        </dependency>
    </dependencies>
    <configuration>
        <targetClasses>
            <param>com.example.service.*</param>
        </targetClasses>
        <mutationThreshold>80</mutationThreshold>
    </configuration>
</plugin>
```

## Testing Pyramid

```text
        /  E2E  \         — Few, slow, expensive
       / Contract \       — API boundaries
      / Integration \     — Real infrastructure
     /    Unit Tests  \   — Many, fast, isolated
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Mock not working | Missing @ExtendWith | Add MockitoExtension |
| NPE in test | Mock not initialized | Check @InjectMocks |
| Flaky test | Shared state | Isolate test data |
| Context fails | Missing bean | Use @MockBean |
| Slow suite | Too many contexts | Share context |
| Container startup slow | Image pull | Pre-pull images, use reusable containers |
| Mutation score low | Weak assertions | Add boundary/edge case tests |
| ArchUnit rule violation | Architecture drift | Fix design or update rules |
| Pact verification fails | Contract drift | Regenerate consumer pact |

**Remember**: Keep tests fast, isolated, and deterministic. Test behavior, not implementation details.
