# Quarkus Testing

Testing in Quarkus: @QuarkusTest, REST Assured, Mockito, TDD workflow, test profiles, Testcontainers, and coverage.

## Quick Reference

```java
@QuarkusTest
public class UserResourceTest {

    @Test
    public void testListUsers() {
        given()
            .when().get("/users")
            .then()
            .statusCode(200)
            .body("size()", greaterThan(0));
    }

    @Test
    public void testCreateUser() {
        CreateUserRequest request = new CreateUserRequest(
            "John Doe",
            "john@example.com"
        );

        given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(201)
            .body("name", equalTo("John Doe"));
    }
}
```

## @QuarkusTest

### Basic Test

```java
@QuarkusTest
public class UserResourceTest {

    @Test
    public void testGetAllUsers() {
        given()
            .when().get("/users")
            .then()
            .statusCode(200)
            .contentType(MediaType.APPLICATION_JSON)
            .body("size()", greaterThan(0));
    }

    @Test
    public void testGetUserById() {
        given()
            .pathParam("id", 1)
            .when().get("/users/{id}")
            .then()
            .statusCode(200)
            .body("id", equalTo(1))
            .body("name", notNullValue());
    }

    @Test
    public void testGetUserNotFound() {
        given()
            .pathParam("id", 99999)
            .when().get("/users/{id}")
            .then()
            .statusCode(404);
    }
}
```

### Test Lifecycle

```java
@QuarkusTest
public class UserServiceTest {

    @Inject
    UserService userService;

    @BeforeEach
    public void setup() {
        // Runs before each test
    }

    @AfterEach
    public void cleanup() {
        // Runs after each test
    }

    @BeforeAll
    public static void init() {
        // Runs once before all tests
    }

    @AfterAll
    public static void teardown() {
        // Runs once after all tests
    }

    @Test
    public void testCreateUser() {
        CreateUserRequest request = new CreateUserRequest("John", "john@test.com");
        User user = userService.create(request);
        assertNotNull(user.getId());
        assertEquals("John", user.getName());
    }
}
```

## REST Assured

### Request/Response Testing

```java
@QuarkusTest
public class UserResourceTest {

    @Test
    public void testCreateUser() {
        CreateUserRequest request = new CreateUserRequest(
            "Alice",
            "alice@example.com"
        );

        UserResponse response = given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(201)
            .header("Location", notNullValue())
            .extract().as(UserResponse.class);

        assertNotNull(response.id());
        assertEquals("Alice", response.name());
        assertEquals("alice@example.com", response.email());
    }

    @Test
    public void testUpdateUser() {
        UpdateUserRequest update = new UpdateUserRequest("Alice Updated");

        given()
            .contentType(ContentType.JSON)
            .pathParam("id", 1)
            .body(update)
            .when().put("/users/{id}")
            .then()
            .statusCode(200)
            .body("name", equalTo("Alice Updated"));
    }

    @Test
    public void testDeleteUser() {
        given()
            .pathParam("id", 1)
            .when().delete("/users/{id}")
            .then()
            .statusCode(204);
    }
}
```

### Query Parameters

```java
@Test
public void testSearchUsers() {
    given()
        .queryParam("name", "John")
        .queryParam("page", 0)
        .queryParam("size", 10)
        .when().get("/users/search")
        .then()
        .statusCode(200)
        .body("size()", lessThanOrEqualTo(10))
        .body("[0].name", containsString("John"));
}
```

### Headers and Authentication

```java
@Test
public void testAuthenticatedEndpoint() {
    given()
        .header("Authorization", "Bearer " + getTestToken())
        .when().get("/users/me")
        .then()
        .statusCode(200)
        .body("email", notNullValue());
}

@Test
public void testUnauthorized() {
    given()
        .when().get("/users/me")
        .then()
        .statusCode(401);
}
```

## Mocking with @InjectMock

```java
@QuarkusTest
public class UserResourceTest {

    @InjectMock
    UserService userService;

    @Test
    public void testGetUserWithMock() {
        User mockUser = new User(1L, "Mock User", "mock@test.com");

        when(userService.findById(1L))
            .thenReturn(Optional.of(mockUser));

        given()
            .pathParam("id", 1)
            .when().get("/users/{id}")
            .then()
            .statusCode(200)
            .body("name", equalTo("Mock User"));

        verify(userService).findById(1L);
    }

    @Test
    public void testCreateUserWithMock() {
        CreateUserRequest request = new CreateUserRequest("Test", "test@test.com");
        User mockUser = new User(1L, "Test", "test@test.com");

        when(userService.create(any(CreateUserRequest.class)))
            .thenReturn(mockUser);

        given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(201);

        verify(userService).create(any(CreateUserRequest.class));
    }
}
```

## Test Profiles

### Custom Test Profile

```java
public class IntegrationTestProfile implements QuarkusTestProfile {

    @Override
    public Map<String, String> getConfigOverrides() {
        return Map.of(
            "quarkus.datasource.db-kind", "postgresql",
            "quarkus.datasource.jdbc.url", "jdbc:postgresql://localhost:5432/testdb",
            "quarkus.hibernate-orm.database.generation", "drop-and-create"
        );
    }

    @Override
    public Set<Class<?>> getEnabledAlternatives() {
        return Set.of(MockEmailService.class);
    }
}

// Use the profile
@QuarkusTest
@TestProfile(IntegrationTestProfile.class)
public class UserIntegrationTest {

    @Test
    public void testIntegration() {
        // Test with custom configuration
    }
}
```

### Test Resources (Testcontainers)

```java
public class PostgresTestResource implements QuarkusTestResourceLifecycleManager {

    private static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Override
    public Map<String, String> start() {
        POSTGRES.start();
        return Map.of(
            "quarkus.datasource.jdbc.url", POSTGRES.getJdbcUrl(),
            "quarkus.datasource.username", POSTGRES.getUsername(),
            "quarkus.datasource.password", POSTGRES.getPassword()
        );
    }

    @Override
    public void stop() {
        POSTGRES.stop();
    }
}

// Use the test resource
@QuarkusTest
@QuarkusTestResource(PostgresTestResource.class)
public class UserRepositoryTest {

    @Inject
    UserRepository userRepository;

    @Test
    @Transactional
    public void testPersistUser() {
        User user = new User("Test", "test@example.com");
        userRepository.persist(user);

        assertNotNull(user.getId());
        assertTrue(user.isPersistent());
    }
}
```

## Transaction Testing

```java
@QuarkusTest
public class TransactionTest {

    @Inject
    UserRepository userRepository;

    @Test
    @Transactional
    public void testTransactionalOperation() {
        User user = new User("Transactional", "trans@test.com");
        userRepository.persist(user);

        // Transaction commits after test
        assertNotNull(user.getId());
    }

    @Test
    @Transactional
    public void testRollback() {
        User user = new User("Rollback", "rollback@test.com");
        userRepository.persist(user);

        // Throw exception to rollback
        throw new RuntimeException("Test rollback");
    }
}
```

## Database Testing

```java
@QuarkusTest
public class UserRepositoryTest {

    @Inject
    UserRepository userRepository;

    @BeforeEach
    @Transactional
    public void setupData() {
        userRepository.deleteAll();
        userRepository.persist(new User("Alice", "alice@test.com"));
        userRepository.persist(new User("Bob", "bob@test.com"));
    }

    @Test
    public void testFindAll() {
        List<User> users = userRepository.listAll();
        assertEquals(2, users.size());
    }

    @Test
    public void testFindByEmail() {
        Optional<User> user = userRepository.findByEmail("alice@test.com");
        assertTrue(user.isPresent());
        assertEquals("Alice", user.get().getName());
    }

    @Test
    @Transactional
    public void testCustomQuery() {
        List<User> users = userRepository.find("name like ?1", "A%").list();
        assertEquals(1, users.size());
        assertEquals("Alice", users.get(0).getName());
    }
}
```

## Security Testing

```java
@QuarkusTest
public class SecureResourceTest {

    @Test
    @TestSecurity(user = "testUser", roles = "user")
    public void testUserAccess() {
        given()
            .when().get("/users/me")
            .then()
            .statusCode(200);
    }

    @Test
    @TestSecurity(user = "admin", roles = "admin")
    public void testAdminAccess() {
        given()
            .when().get("/admin/users")
            .then()
            .statusCode(200);
    }

    @Test
    @TestSecurity(user = "user", roles = "user")
    public void testForbiddenAccess() {
        given()
            .when().get("/admin/users")
            .then()
            .statusCode(403);
    }

    @Test
    public void testUnauthenticatedAccess() {
        given()
            .when().get("/users/me")
            .then()
            .statusCode(401);
    }
}
```

## Parameterized Tests

```java
@QuarkusTest
public class ValidationTest {

    @ParameterizedTest
    @ValueSource(strings = {"", "a", "ab"})
    public void testInvalidNameLength(String name) {
        CreateUserRequest request = new CreateUserRequest(name, "test@example.com");

        given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(400);
    }

    @ParameterizedTest
    @CsvSource({
        "invalid,400",
        "notanemail,400",
        "@example.com,400",
        "test@,400"
    })
    public void testInvalidEmails(String email, int expectedStatus) {
        CreateUserRequest request = new CreateUserRequest("Test", email);

        given()
            .contentType(ContentType.JSON)
            .body(request)
            .when().post("/users")
            .then()
            .statusCode(expectedStatus);
    }
}
```

## TDD Workflow

### Red-Green-Refactor

```java
// 1. RED: Write failing test first
@QuarkusTest
public class UserServiceTest {

    @Inject
    UserService userService;

    @Test
    public void testFindActiveUsers() {
        // This will fail initially
        List<User> activeUsers = userService.findActiveUsers();
        assertTrue(activeUsers.stream().allMatch(User::isActive));
    }
}

// 2. GREEN: Implement minimum code to pass
@ApplicationScoped
public class UserService {

    @Inject
    UserRepository userRepository;

    public List<User> findActiveUsers() {
        return userRepository.find("active = true").list();
    }
}

// 3. REFACTOR: Improve implementation
public List<User> findActiveUsers() {
    return userRepository.findByActive(true);  // Use custom query method
}
```

## Code Coverage (JaCoCo)

### Configuration

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

Run coverage:

```bash
./mvnw clean test jacoco:report
# Report: target/site/jacoco/index.html
```

## Native Tests

```java
@QuarkusIntegrationTest
public class NativeUserResourceIT extends UserResourceTest {
    // Inherits all tests from UserResourceTest
    // Runs against native executable
}
```

Run native tests:

```bash
./mvnw verify -Pnative
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Test dependencies not injected | Missing @QuarkusTest | Add @QuarkusTest annotation |
| Database not reset between tests | Transactions not rolled back | Use @Transactional or @QuarkusTestResource |
| Mock not working | Wrong annotation | Use @InjectMock, not @Mock |
| Port already in use | Previous test still running | Set quarkus.http.test-port=0 for random port |
| Native test fails | Reflection not registered | Add @RegisterForReflection to classes |

## Best Practices

1. **Test naming**: `test<MethodName>_<Condition>_<Expected>` (e.g., `testCreateUser_InvalidEmail_Returns400`)
2. **One assertion focus**: Each test should verify one behavior
3. **Use test profiles**: Separate configurations for different test scenarios
4. **Clean test data**: Reset database state between tests
5. **Mock external dependencies**: Use @InjectMock for external services
6. **Test security**: Always test authorization rules
7. **Aim for 80%+ coverage**: Use JaCoCo to track coverage
