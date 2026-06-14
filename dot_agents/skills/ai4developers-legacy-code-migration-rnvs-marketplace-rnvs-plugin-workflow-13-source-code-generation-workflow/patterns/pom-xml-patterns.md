# Maven POM Patterns

Patterns for Maven pom.xml files in VNRM microservices.

---

## Pattern 1: Complete Microservice POM (NEW Mode)

Standard pom.xml for a new VNRM microservice:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>de.telekom.vnrm</groupId>
        <artifactId>vnrm-parent</artifactId>
        <version>${vnrm.parent.version}</version>
        <relativePath/>
    </parent>

    <artifactId>${module-name}-service</artifactId>
    <version>${project.version}</version>
    <packaging>jar</packaging>

    <name>VNRM ${Module Name} Service</name>
    <description>${Module description} for VNRM platform</description>

    <properties>
        <java.version>21</java.version>
        <spring-boot.version>3.2.0</spring-boot.version>
        <mapstruct.version>1.5.5.Final</mapstruct.version>
        <lombok.version>1.18.30</lombok.version>
        <resilience4j.version>2.1.0</resilience4j.version>
        <horizon.version>3.0.0</horizon.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-cache</artifactId>
        </dependency>

        <!-- Horizon Event Bus (Telekom) - NOT Kafka -->
        <dependency>
            <groupId>de.telekom.horizon</groupId>
            <artifactId>horizon-client-spring-boot-starter</artifactId>
            <version>${horizon.version}</version>
        </dependency>

        <!-- Resilience4j -->
        <dependency>
            <groupId>io.github.resilience4j</groupId>
            <artifactId>resilience4j-spring-boot3</artifactId>
            <version>${resilience4j.version}</version>
        </dependency>
        <dependency>
            <groupId>io.github.resilience4j</groupId>
            <artifactId>resilience4j-circuitbreaker</artifactId>
            <version>${resilience4j.version}</version>
        </dependency>
        <dependency>
            <groupId>io.github.resilience4j</groupId>
            <artifactId>resilience4j-retry</artifactId>
            <version>${resilience4j.version}</version>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.liquibase</groupId>
            <artifactId>liquibase-core</artifactId>
        </dependency>

        <!-- Lombok & MapStruct -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.mapstruct</groupId>
            <artifactId>mapstruct</artifactId>
            <version>${mapstruct.version}</version>
        </dependency>

        <!-- OpenAPI Documentation -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.2.0</version>
        </dependency>

        <!-- Test Dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                            <version>${lombok.version}</version>
                        </path>
                        <path>
                            <groupId>org.mapstruct</groupId>
                            <artifactId>mapstruct-processor</artifactId>
                            <version>${mapstruct.version}</version>
                        </path>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok-mapstruct-binding</artifactId>
                            <version>0.2.0</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.liquibase</groupId>
                <artifactId>liquibase-maven-plugin</artifactId>
                <configuration>
                    <changeLogFile>src/main/resources/db/changelog/db.changelog-master.yaml</changeLogFile>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Pattern 2: Add Dependencies (CHANGE Mode)

When adding new dependencies to existing pom.xml:

```xml
<!-- MODIFICATION: Add after existing dependencies -->

<!-- Resilience4j for circuit breaker (if not present) -->
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>${resilience4j.version}</version>
</dependency>

<!-- Spring Retry (if not present) -->
<dependency>
    <groupId>org.springframework.retry</groupId>
    <artifactId>spring-retry</artifactId>
</dependency>

<!-- Cache support (if not present) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
```

---

## Pattern 3: Properties Section

Standard properties for VNRM microservices:

```xml
<properties>
    <!-- Java version -->
    <java.version>21</java.version>

    <!-- Spring Boot -->
    <spring-boot.version>3.2.0</spring-boot.version>

    <!-- Code generation -->
    <mapstruct.version>1.5.5.Final</mapstruct.version>
    <lombok.version>1.18.30</lombok.version>

    <!-- Resilience -->
    <resilience4j.version>2.1.0</resilience4j.version>

    <!-- Telekom Event Bus -->
    <horizon.version>3.0.0</horizon.version>

    <!-- Database -->
    <postgresql.version>42.6.0</postgresql.version>

    <!-- Testing -->
    <testcontainers.version>1.19.3</testcontainers.version>

    <!-- Code quality -->
    <jacoco.version>0.8.11</jacoco.version>
    <sonar.coverage.jacoco.xmlReportPaths>
        ${project.build.directory}/site/jacoco/jacoco.xml
    </sonar.coverage.jacoco.xmlReportPaths>
</properties>
```

---

## Anti-Patterns to Avoid

1. **Don't use Kafka dependencies** - VNRM uses Horizon Event Bus
2. **Don't skip annotation processor order** - Lombok must come before MapStruct
3. **Don't forget test dependencies** - Include TestContainers for integration tests
4. **Don't hardcode versions** - Use properties for version management
5. **Don't skip actuator** - Required for health checks and monitoring
6. **Don't use old Java versions** - VNRM uses Java 21
