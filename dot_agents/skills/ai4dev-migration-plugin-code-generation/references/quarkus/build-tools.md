# Quarkus Build Tools

Maven and Gradle configuration for Quarkus projects, native compilation, and CI/CD integration.

## Maven (Recommended)

### pom.xml Template

```xml
<?xml version="1.0"?>
<project xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd"
         xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-quarkus-app</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <compiler-plugin.version>3.12.1</compiler-plugin.version>
        <maven.compiler.release>17</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.version>3.8.1</quarkus.platform.version>
        <skipITs>true</skipITs>
        <surefire-plugin.version>3.2.5</surefire-plugin.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>${quarkus.platform.artifact-id}</artifactId>
                <version>${quarkus.platform.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- Core Quarkus -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest-jackson</artifactId>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-hibernate-orm-panache</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-jdbc-postgresql</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-flyway</artifactId>
        </dependency>

        <!-- Security -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-oidc</artifactId>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-hibernate-validator</artifactId>
        </dependency>

        <!-- Health & Metrics -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-smallrye-health</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-micrometer-registry-prometheus</artifactId>
        </dependency>

        <!-- OpenAPI -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-smallrye-openapi</artifactId>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${quarkus.platform.version}</version>
                <extensions>true</extensions>
                <executions>
                    <execution>
                        <goals>
                            <goal>build</goal>
                            <goal>generate-code</goal>
                            <goal>generate-code-tests</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${compiler-plugin.version}</version>
                <configuration>
                    <parameters>true</parameters>
                </configuration>
            </plugin>
            <plugin>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>${surefire-plugin.version}</version>
                <configuration>
                    <systemPropertyVariables>
                        <java.util.logging.manager>org.jboss.logmanager.LogManager</java.util.logging.manager>
                        <maven.home>${maven.home}</maven.home>
                    </systemPropertyVariables>
                </configuration>
            </plugin>
            <plugin>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>${surefire-plugin.version}</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <systemPropertyVariables>
                        <native.image.path>${project.build.directory}/${project.build.finalName}-runner</native.image.path>
                        <java.util.logging.manager>org.jboss.logmanager.LogManager</java.util.logging.manager>
                        <maven.home>${maven.home}</maven.home>
                    </systemPropertyVariables>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <profiles>
        <profile>
            <id>native</id>
            <activation>
                <property>
                    <name>native</name>
                </property>
            </activation>
            <properties>
                <skipITs>false</skipITs>
                <quarkus.package.type>native</quarkus.package.type>
            </properties>
        </profile>
    </profiles>
</project>
```

## Gradle (Kotlin DSL)

### build.gradle.kts Template

```kotlin
plugins {
    java
    id("io.quarkus") version "3.8.1"
}

repositories {
    mavenCentral()
    mavenLocal()
}

val quarkusPlatformGroupId: String by project
val quarkusPlatformArtifactId: String by project
val quarkusPlatformVersion: String by project

dependencies {
    implementation(enforcedPlatform("${quarkusPlatformGroupId}:${quarkusPlatformArtifactId}:${quarkusPlatformVersion}"))

    // Core
    implementation("io.quarkus:quarkus-rest")
    implementation("io.quarkus:quarkus-rest-jackson")

    // Database
    implementation("io.quarkus:quarkus-hibernate-orm-panache")
    implementation("io.quarkus:quarkus-jdbc-postgresql")
    implementation("io.quarkus:quarkus-flyway")

    // Security
    implementation("io.quarkus:quarkus-oidc")

    // Validation
    implementation("io.quarkus:quarkus-hibernate-validator")

    // Health & Metrics
    implementation("io.quarkus:quarkus-smallrye-health")
    implementation("io.quarkus:quarkus-micrometer-registry-prometheus")

    // OpenAPI
    implementation("io.quarkus:quarkus-smallrye-openapi")

    // Testing
    testImplementation("io.quarkus:quarkus-junit5")
    testImplementation("io.rest-assured:rest-assured")
    testImplementation("org.testcontainers:postgresql")
}

group = "com.example"
version = "1.0.0-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.withType<Test> {
    systemProperty("java.util.logging.manager", "org.jboss.logmanager.LogManager")
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
    options.compilerArgs.add("-parameters")
}
```

## Common Quarkus Extensions

### Add Extensions

```bash
# Maven
./mvnw quarkus:add-extension -Dextensions="extension-name"

# Gradle
./gradlew addExtension --extensions="extension-name"
```

### Popular Extensions

| Extension | Artifact ID | Purpose |
|-----------|------------|---------|
| REST | quarkus-rest | JAX-RS REST endpoints |
| JSON | quarkus-rest-jackson | JSON serialization |
| Hibernate ORM | quarkus-hibernate-orm-panache | JPA with Panache |
| PostgreSQL | quarkus-jdbc-postgresql | PostgreSQL driver |
| MySQL | quarkus-jdbc-mysql | MySQL driver |
| Flyway | quarkus-flyway | Database migrations |
| Liquibase | quarkus-liquibase | Database migrations |
| OIDC | quarkus-oidc | OpenID Connect auth |
| JWT | quarkus-smallrye-jwt | JWT authentication |
| Validator | quarkus-hibernate-validator | Bean validation |
| Health | quarkus-smallrye-health | Health checks |
| Metrics | quarkus-micrometer-registry-prometheus | Prometheus metrics |
| OpenAPI | quarkus-smallrye-openapi | OpenAPI/Swagger |
| Redis | quarkus-redis-client | Redis client |
| Kafka | quarkus-smallrye-reactive-messaging-kafka | Kafka messaging |
| REST Client | quarkus-rest-client-reactive | Reactive REST client |
| Scheduler | quarkus-scheduler | Scheduled tasks |
| Cache | quarkus-cache | Application caching |

## Build Commands

### Development Mode

```bash
# Maven
./mvnw quarkus:dev

# Gradle
./gradlew quarkusDev

# Features in dev mode:
# - Live reload (automatic recompilation)
# - Dev UI: http://localhost:8080/q/dev
# - Continuous testing
# - Debug mode on port 5005
```

### Build JVM Application

```bash
# Maven
./mvnw clean package

# Gradle
./gradlew build

# Output: target/quarkus-app/
# Run: java -jar target/quarkus-app/quarkus-run.jar
```

### Build Native Executable

```bash
# Maven
./mvnw clean package -Pnative

# Gradle
./gradlew build -Dquarkus.package.type=native

# With Docker (no GraalVM install needed)
./mvnw clean package -Pnative -Dquarkus.native.container-build=true

# Output: target/*-runner
# Run: ./target/*-runner
```

### Run Tests

```bash
# Unit tests only
./mvnw test

# Integration tests
./mvnw verify

# Native tests
./mvnw verify -Pnative

# Continuous testing (in dev mode)
./mvnw quarkus:dev
# Press 'r' to run tests
```

## Native Compilation

### Configuration

```properties
# application.properties

# Native build options
quarkus.native.additional-build-args=--initialize-at-run-time=org.example.MyClass
quarkus.native.enable-https-url-handler=true
quarkus.native.enable-all-security-services=true

# Resources to include
quarkus.native.resources.includes=*.properties,*.yaml,*.json

# Container build (no local GraalVM needed)
quarkus.native.container-build=true
quarkus.native.builder-image=quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21
```

### Register for Reflection

```java
// For classes used with reflection
@RegisterForReflection
public class MyDto {
    // ...
}

// For external classes
@RegisterForReflection(targets = {
    com.example.ExternalClass.class,
    com.example.AnotherClass.class
})
public class ReflectionConfiguration {
}
```

## Docker Containerization

### Dockerfile.jvm

```dockerfile
FROM registry.access.redhat.com/ubi8/openjdk-17:1.18

ENV LANGUAGE='en_US:en'

COPY --chown=185 target/quarkus-app/lib/ /deployments/lib/
COPY --chown=185 target/quarkus-app/*.jar /deployments/
COPY --chown=185 target/quarkus-app/app/ /deployments/app/
COPY --chown=185 target/quarkus-app/quarkus/ /deployments/quarkus/

EXPOSE 8080
USER 185
ENV JAVA_OPTS="-Dquarkus.http.host=0.0.0.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager"
ENV JAVA_APP_JAR="/deployments/quarkus-run.jar"

ENTRYPOINT [ "/opt/jboss/container/java/run/run-java.sh" ]
```

### Dockerfile.native

```dockerfile
FROM registry.access.redhat.com/ubi8/ubi-minimal:8.9

WORKDIR /work/
RUN chown 1001 /work \
    && chmod "g+rwX" /work \
    && chown 1001:root /work

COPY --chown=1001:root target/*-runner /work/application

EXPOSE 8080
USER 1001

CMD ["./application", "-Dquarkus.http.host=0.0.0.0"]
```

### Build and Run

```bash
# JVM
docker build -f src/main/docker/Dockerfile.jvm -t my-app:jvm .
docker run -i --rm -p 8080:8080 my-app:jvm

# Native
docker build -f src/main/docker/Dockerfile.native -t my-app:native .
docker run -i --rm -p 8080:8080 my-app:native
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Quarkus CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: maven

    - name: Build with Maven
      run: ./mvnw clean verify

    - name: Build native image
      run: ./mvnw clean package -Pnative -Dquarkus.native.container-build=true

    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: native-executable
        path: target/*-runner
```

### GitLab CI

```yaml
image: maven:3.9-eclipse-temurin-17

stages:
  - build
  - test
  - package

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

cache:
  paths:
    - .m2/repository

build:
  stage: build
  script:
    - ./mvnw clean compile

test:
  stage: test
  script:
    - ./mvnw test
  artifacts:
    reports:
      junit: target/surefire-reports/TEST-*.xml

package:
  stage: package
  script:
    - ./mvnw clean package
  artifacts:
    paths:
      - target/quarkus-app/
    expire_in: 1 week
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Dev mode port conflict | Port 8080 in use | Use quarkus.http.port=8081 |
| Native build fails | Missing reflection config | Add @RegisterForReflection |
| Slow startup | Large dependency tree | Analyze with quarkus:dependency-tree |
| Tests fail in CI | Missing test resources | Configure test resources properly |
| Container build fails | Docker not running | Start Docker daemon |

## Performance Tips

1. **Use fast-jar packaging** (default in Quarkus 3+)
2. **Enable build caching**: `quarkus.package.jar.compress=false`
3. **Native builds**: Use container-build for reproducibility
4. **Dev mode**: Use continuous testing instead of manual test runs
5. **Dependencies**: Keep extensions minimal, add only what you need
