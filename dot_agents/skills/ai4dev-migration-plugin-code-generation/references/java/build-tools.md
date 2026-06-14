# Java Build Tools — Maven & Gradle

Maven and Gradle: dependency management, plugins, multi-module projects, CI/CD pipelines.

---

## Maven

### POM Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        <spring-boot.version>3.2.1</spring-boot.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-enforcer-plugin</artifactId>
                <version>3.4.1</version>
            </plugin>
        </plugins>
    </build>
</project>
```

### Multi-Module POM

```xml
<!-- parent/pom.xml -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <modules>
        <module>common</module>
        <module>service-api</module>
        <module>service-impl</module>
    </modules>

    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>3.2.1</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

### Build Lifecycle

- Default lifecycle phases (validate → deploy)
- Clean lifecycle
- Site lifecycle
- Plugin goals and execution binding

### Key Plugins

- **maven-compiler-plugin** — Java version, annotation processing
- **maven-surefire-plugin** — Unit test execution (`*Test.java`)
- **maven-failsafe-plugin** — Integration test execution (`*IT.java`)
- **maven-enforcer-plugin** — Build rules enforcement
- **maven-shade-plugin** — Uber JAR creation
- **spring-boot-maven-plugin** — Spring Boot packaging

### Enforcer Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <version>3.4.1</version>
    <executions>
        <execution>
            <id>enforce</id>
            <goals><goal>enforce</goal></goals>
            <configuration>
                <rules>
                    <requireMavenVersion>
                        <version>[3.9.0,)</version>
                    </requireMavenVersion>
                    <requireJavaVersion>
                        <version>[21,)</version>
                    </requireJavaVersion>
                    <banDuplicatePomDependencyVersions/>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### Maven Commands

```bash
mvn dependency:tree                          # Dependency tree
mvn dependency:analyze                       # Unused/undeclared deps
mvn versions:display-dependency-updates      # Available updates
mvn versions:display-plugin-updates          # Plugin updates
mvn help:effective-pom                       # Resolved POM
mvn help:effective-settings                  # Resolved settings
mvn -pl module-name -am install              # Build module with deps
mvn -rf :module-name install                 # Resume from module
```

---

## Gradle

### Kotlin DSL (build.gradle.kts)

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
    jacoco
}

group = "com.example"
version = "1.0.0-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:junit-jupiter")
}

tasks.test {
    useJUnitPlatform()
    maxParallelForks = Runtime.getRuntime().availableProcessors() / 2
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
}
```

### Version Catalog (gradle/libs.versions.toml)

```toml
[versions]
spring-boot = "3.2.1"
junit = "5.10.1"
testcontainers = "1.19.3"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
spring-boot-starter-test = { module = "org.springframework.boot:spring-boot-starter-test", version.ref = "spring-boot" }
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }
testcontainers-junit = { module = "org.testcontainers:junit-jupiter", version.ref = "testcontainers" }

[bundles]
testing = ["spring-boot-starter-test", "junit-jupiter", "testcontainers-junit"]

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

### settings.gradle.kts

```kotlin
rootProject.name = "my-project"

include("common", "service-api", "service-impl")

dependencyResolutionManagement {
    versionCatalogs {
        create("libs") {
            from(files("gradle/libs.versions.toml"))
        }
    }
}
```

### Build Optimization

```properties
# gradle.properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.daemon=true
org.gradle.jvmargs=-Xmx4g -XX:+UseG1GC
org.gradle.configuration-cache=true
```

### Gradle Commands

```bash
gradle dependencies                              # Dependency tree
gradle dependencyInsight --dependency log4j       # Transitive dependency
gradle build --scan                              # Build scan
gradle build --build-cache                       # With cache
gradle tasks --all                               # All tasks
gradle wrapper --gradle-version=8.5              # Update wrapper
```

---

## CI/CD Templates

```yaml
# GitHub Actions
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'maven'
      - run: ./mvnw -B verify
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Dependency not found | Wrong version | Check Maven Central |
| Version conflict | Transitive deps | Use BOM or enforcer |
| Build OOM | Heap too small | Set MAVEN_OPTS / org.gradle.jvmargs |
| Slow builds | No caching | Enable build cache |
| Plugin not found | Wrong groupId/ID | Check plugin documentation |
| Test not running | Naming convention | Surefire: `*Test.java`, Failsafe: `*IT.java` |
| Configuration cache miss | Non-serializable task | Fix task serialization |
