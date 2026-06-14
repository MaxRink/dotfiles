# VNRM SPE (SPECIAL FUNCTIONS) Architecture Reference

## Overview

The VNRM SPE (SPECIAL FUNCTIONS) submodule serves as the critical bridge between modern VNRM microservices and legacy RNVS systems during the transition period, providing database integration, communication management, and backend automation capabilities. SPE enables gradual migration from legacy systems while maintaining business continuity and ensuring data consistency across system boundaries.

SPE implements three specialized services: database synchronization (VNRM-RNVS DB API), file-based partner communication (Communication Server), and external system proxy capabilities (Backend Automation Adapter). All SPE services operate at Office Time (OT) service level, providing essential legacy integration during business hours while VNRM microservices gradually replace RNVS functionality.

## Service Level Architecture

### Service Level Classification

**Office Time (OT) Services - Business Hours Support:**
- **Response Time**: 3 days
- **Availability**: Business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Impact**: Limited to legacy system integration and communication functions
- **Business Justification**: SPE services are transitional - designed for decommissioning after RNVS retirement, not requiring 24/7 support

### Strategic Service Positioning

**Transitional Nature:**
- **Temporary Role**: SPE services are explicitly designed for gradual migration period
- **Planned Decommissioning**: All SPE services will be retired after complete RNVS migration
- **Migration Support**: Facilitates phased transition without business disruption
- **Fallback Capability**: Provides rollback options if migration issues occur

**Service Timeline:**
```
Current State: RNVS + VNRM (both operational, SPE bridges)
    ↓
Migration Phase: Gradual RNVS functionality migration to VNRM
    ↓
Target State: VNRM only (SPE decommissioned, RNVS retired)
```

## Deployed Microservices

### Production Services (VNRM 1.9.0+)

#### VNRM-RNVS Database API

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| spe-vnrm-rnvs-db-api | v1.8.3 | OT | Database bridge between VNRM and RNVS | COM config-server, RNVS Oracle DB |

**Technology Stack:**
- **Backend**: Spring Boot 2.7.x, Spring Data JPA
- **Database Access**: Dual connectivity (PostgreSQL for VNRM, Oracle for RNVS)
- **Transaction Management**: Distributed transaction support
- **API**: RESTful with OpenAPI 3.0 specification

**Core Capabilities:**
- Bidirectional data synchronization between VNRM PostgreSQL and RNVS Oracle databases
- Schema translation and data format conversion (modern ↔ legacy)
- Transaction management with consistency guarantees
- Migration support tools and validation APIs
- Complete audit trail for all synchronization operations

**Critical Dependencies:**
- **RNVS Oracle Database**: Legacy database (critical external dependency)
- **VNRM PostgreSQL**: Modern database (internal dependency)
- **COM Config-Server**: Configuration for sync rules and mappings
- **Network Connectivity**: Secure connection to legacy RNVS infrastructure

#### Communication Server API (COMS)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| spe-coms-communication-server-api | v1.7.1 | OT | File-based partner communication | COM config-server, File system |

**Technology Stack:**
- **Backend**: Spring Boot 2.7.x
- **File System**: Structured directory hierarchy with role-based access
- **Protocols**: SFTP, FTP, HTTP file transfer
- **Security**: Certificate-based authentication, encryption at rest and in transit

**Core Capabilities:**
- File-based communication with external partners (Internet, Hitnet)
- Role-based file system access control (5 user role types)
- Archive management with long-term retention
- SFTP secure file transfer support
- File monitoring and automated processing triggers

**Network Connectivity:**
- **Internet**: External partner integration (BNetzA, carriers, third-party systems)
- **Hitnet**: Internal Telekom network access (internal systems)
- **VNRM Internal**: Internal microservice communication

**File System Architecture:**
- **User-Specific Folders**: Dedicated directories per user type
- **Archive Integration**: Links to archive folders for historical data
- **Working Directories**: Active file processing areas
- **Log Directories**: System and access logging

#### Backend Automation Adapter API (BEAA)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| spe-beaa-backend-automation-adapter-api | v1.9.0 | OT | CRM-T and external system proxy | COM config-server, CRM-T, Tardis |

**Technology Stack:**
- **Backend**: Spring Cloud Gateway (same as VNRM Portal B4F)
- **Routing**: Configuration-driven dynamic routing
- **Security**: Tardis M2M authentication (Iris + Stargate)
- **Monitoring**: Request/response tracking for all proxy operations

**Core Capabilities:**
- Pure proxy pattern with no business logic or data transformation
- View-only access to CRM-T (Product Inventory, Orders, Provider Change, Agreements)
- Configuration-driven target system addition (no code changes required)
- Bidirectional M2M authentication (consumer ↔ BEAA ↔ target system)
- Complete monitoring of inbound and outbound requests

**Integration Pattern:**
```
Request Flow:
Consumer → <Tardis-Url>/<Tardis-Path-Bea-Adapter>/<Target-System-Name>/<Path>
Forward → <Tardis-Url>/<Tardis-Path-Target-System>/<Path>

Example:
Consumer: /beaa/crm-t/productInventory/products?phoneNumber=03012345678
Forward:  /productInventory/products?phoneNumber=03012345678 (to CRM-T)
```

## Detailed Microservice Implementation Specifications

### BEAA - Backend Automation Adapter

#### System Use Cases

**Primary Functions:**
- **NUM BEA Access**: Enables NUM Backend Automation access to hub external systems via API (like CRM-T)
- **Response Forwarding**: Contains no business logic, forwards complete response of hub external systems to consumer
- **View-Only Operations**: Intention is to enable data views, Write and Update functions not enabled for consumers

**Business Rationale:**
- Provide NUM services with read-only access to customer data in CRM-T
- Eliminate direct CRM-T integration for each VNRM microservice
- Centralized security and monitoring for external system access
- Standardized interface for multiple target systems

#### API Endpoint Specifications

**Product Inventory Management:**
```
GET /beaa/crm-t/productInventory/products?phoneNumber={phoneNumber}
Description: Retrieve all products associated with a phone number
Parameters:
  - phoneNumber (required): Phone number in full format (e.g., 03012345678)
Response: ProductInventoryResponse with list of products
Security: Tardis M2M authentication required
```

**Order Information:**
```
GET /beaa/crm-t/orderInformation/productOrders?phoneNumber={phoneNumber}
Description: Retrieve all product orders for a phone number
Parameters:
  - phoneNumber (required): Phone number in full format
Response: ProductOrdersResponse with list of orders
Security: Tardis M2M authentication required

GET /beaa/crm-t/orderInformation/productOrder/{productOrderId}
Description: Retrieve specific product order by ID
Parameters:
  - productOrderId (required): Unique product order identifier
Response: ProductOrderResponse with order details
Security: Tardis M2M authentication required
```

**Provider Change:**
```
GET /beaa/crm-t/providerChange/vaoid/{vaoId}
Description: Retrieve provider change data by VAO (Vorabauskunft) ID
Parameters:
  - vaoId (required): Unique VAO identifier for provider change process
Response: ProviderChangeResponse with change details
Security: Tardis M2M authentication required
```

**Agreement Management:**
```
GET /beaa/ws/agreementData/agreement
Description: Retrieve all customer agreements
Query Parameters: Optional filters for agreement search
Response: AgreementListResponse with agreements
Security: Tardis M2M authentication required

GET /beaa/ws/agreementData/agreement/{agreementId}
Description: Retrieve specific agreement by ID
Parameters:
  - agreementId (required): Unique agreement identifier
Response: AgreementResponse with agreement details
Security: Tardis M2M authentication required
```

#### Security Implementation

**Tardis M2M Authentication Flow:**
```
1. Consumer Authentication:
   Consumer → Iris (Identity Provider) → Obtain JWT Token

2. Request to BEAA:
   Consumer → BEAA (with JWT Token)
   BEAA validates token via Stargate (Authorization)

3. Target System Authentication:
   BEAA → Iris (Identity Provider) → Obtain Target System JWT Token

4. Forward Request:
   BEAA → Target System (CRM-T) with Target System JWT Token

5. Response Flow:
   Target System → BEAA → Consumer (complete response forwarded)
```

**Authentication Components:**
- **Iris**: Telekom identity provider for authentication
- **Stargate**: Authorization gateway for access control
- **JWT Tokens**: Secure token-based authentication
- **Certificate Authentication**: Client certificates for system-to-system communication

#### Spring Cloud Gateway Configuration

**Routing Configuration:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        # CRM-T Product Inventory
        - id: crm-t-product-inventory
          uri: ${tardis.crm-t.base-url}
          predicates:
            - Path=/beaa/crm-t/productInventory/**
          filters:
            - StripPrefix=2  # Remove /beaa/crm-t
            - AddRequestHeader=X-Source-System, VNRM-BEAA
            - CircuitBreaker=name=crm-t,fallbackUri=forward:/fallback/crm-t

        # CRM-T Order Information
        - id: crm-t-order-info
          uri: ${tardis.crm-t.base-url}
          predicates:
            - Path=/beaa/crm-t/orderInformation/**
          filters:
            - StripPrefix=2
            - AddRequestHeader=X-Source-System, VNRM-BEAA
            - CircuitBreaker=name=crm-t,fallbackUri=forward:/fallback/crm-t

        # CRM-T Provider Change
        - id: crm-t-provider-change
          uri: ${tardis.crm-t.base-url}
          predicates:
            - Path=/beaa/crm-t/providerChange/**
          filters:
            - StripPrefix=2
            - AddRequestHeader=X-Source-System, VNRM-BEAA
            - CircuitBreaker=name=crm-t,fallbackUri=forward:/fallback/crm-t

        # Agreement Data Service
        - id: agreement-data
          uri: ${tardis.agreement-service.base-url}
          predicates:
            - Path=/beaa/ws/agreementData/**
          filters:
            - StripPrefix=2
            - AddRequestHeader=X-Source-System, VNRM-BEAA
            - CircuitBreaker=name=agreement-service,fallbackUri=forward:/fallback/agreement

      # Global filters
      default-filters:
        - name: Retry
          args:
            retries: 3
            statuses: BAD_GATEWAY,SERVICE_UNAVAILABLE
            methods: GET
            backoff:
              firstBackoff: 500ms
              maxBackoff: 5000ms
              factor: 2
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 100
            redis-rate-limiter.burstCapacity: 200
```

**Circuit Breaker Configuration:**
```java
@Configuration
public class CircuitBreakerConfiguration {

    @Bean
    public Customizer<ReactiveResilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id -> new Resilience4JConfigBuilder(id)
            .circuitBreakerConfig(CircuitBreakerConfig.custom()
                .slidingWindowSize(10)
                .minimumNumberOfCalls(5)
                .failureRateThreshold(50)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .permittedNumberOfCallsInHalfOpenState(3)
                .automaticTransitionFromOpenToHalfOpenEnabled(true)
                .build())
            .timeLimiterConfig(TimeLimiterConfig.custom()
                .timeoutDuration(Duration.ofSeconds(10))
                .build())
            .build());
    }
}
```

#### Monitoring and Observability

**Request Tracking:**
```java
@Component
public class BeaaRequestLogger implements GlobalFilter {

    @Autowired
    private MeterRegistry meterRegistry;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();

        // Log request details
        log.info("BEAA Request: method={}, path={}, source={}",
                 request.getMethod(),
                 request.getPath(),
                 request.getRemoteAddress());

        // Metrics
        Counter requestCounter = meterRegistry.counter("beaa.requests.total",
            "method", request.getMethod().toString(),
            "target_system", extractTargetSystem(request.getPath())
        );
        requestCounter.increment();

        long startTime = System.currentTimeMillis();

        return chain.filter(exchange).doFinally(signalType -> {
            long duration = System.currentTimeMillis() - startTime;

            // Record response time
            meterRegistry.timer("beaa.request.duration",
                "method", request.getMethod().toString(),
                "target_system", extractTargetSystem(request.getPath())
            ).record(duration, TimeUnit.MILLISECONDS);

            log.info("BEAA Response: path={}, duration={}ms, status={}",
                     request.getPath(),
                     duration,
                     exchange.getResponse().getStatusCode());
        });
    }

    private String extractTargetSystem(RequestPath path) {
        String pathStr = path.toString();
        if (pathStr.startsWith("/beaa/crm-t/")) {
            return "CRM-T";
        } else if (pathStr.startsWith("/beaa/ws/")) {
            return "AGREEMENT-SERVICE";
        }
        return "UNKNOWN";
    }
}
```

### COMS - Communication Server

#### File System Architecture

**Directory Structure:**
```
/communication-server/
├── users/
│   ├── comserv-admin/           # Admin user (full rights)
│   │   ├── inbox/
│   │   ├── outbox/
│   │   └── scripts/
│   ├── technical-int-sst/       # Internal technical SST (read + new)
│   │   ├── inbox/
│   │   └── outbox/
│   ├── consumer-api-tardis/     # API consumer (read + new)
│   │   ├── inbox/
│   │   └── outbox/
│   ├── technical-vnrm-system/   # VNRM system user (read + update + new + delete)
│   │   ├── inbox/
│   │   ├── outbox/
│   │   └── processing/
│   └── technical-ext-sst/       # External technical SST (read + new + delete)
│       ├── inbox/
│       ├── outbox/
│       └── uploads/
├── archive/
│   ├── 2024/
│   │   ├── 01-january/
│   │   ├── 02-february/
│   │   └── ...
│   └── 2023/
├── logs/
│   ├── access-logs/
│   ├── error-logs/
│   └── audit-logs/
└── config/
    └── user-permissions.yml
```

#### User Role Management

**Permission Matrix:**

| Role | Read Files | Update Files | New Files | Delete Files | Full Rights | Scripts | CRUD |
|------|------------|--------------|-----------|--------------|-------------|---------|------|
| **ComServ admin** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Technical Int. SST** | ✓ | - | ✓ | - | - | - | - |
| **Consumer API (TARDIS)** | ✓ | - | ✓ | - | - | - | - |
| **Technical VNRM System** | ✓ | ✓ | ✓ | ✓ | - | - | - |
| **Technical Ext. SST** | ✓ | - | ✓ | ✓ | - | - | - |

**Role Descriptions:**
- **ComServ admin**: Full administrative access including scripts and CRUD operations
- **Technical Int. SST**: Internal technical support team (read and upload new files)
- **Consumer API (TARDIS)**: API-based access via Tardis integration (read and upload)
- **Technical VNRM System**: VNRM microservices system user (read/update/new/delete)
- **Technical Ext. SST**: External technical support team (read/upload/delete)

#### Communication Flow Architecture

**Network Integration:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Communication Server                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   Internet       │    │   Hitnet         │              │
│  │   Connectivity   │    │   Connectivity   │              │
│  └────────┬─────────┘    └────────┬─────────┘              │
│           │                       │                         │
│           ↓                       ↓                         │
│  ┌────────────────────────────────────────┐                │
│  │         SFTP/FTP Gateway               │                │
│  │  - External Partners (BNetzA, TSPs)    │                │
│  │  - Internal Telekom Systems            │                │
│  └────────────────┬───────────────────────┘                │
│                   │                                         │
│                   ↓                                         │
│  ┌────────────────────────────────────────┐                │
│  │      File System Access Layer          │                │
│  │  - Role-based access control           │                │
│  │  - File validation                     │                │
│  │  - Virus scanning                      │                │
│  └────────────────┬───────────────────────┘                │
│                   │                                         │
│                   ↓                                         │
│  ┌────────────────────────────────────────┐                │
│  │    User-Specific Directories           │                │
│  │  - Inbox/Outbox per user role          │                │
│  │  - Archive management                  │                │
│  └────────────────┬───────────────────────┘                │
│                   │                                         │
│                   ↓                                         │
│  ┌────────────────────────────────────────┐                │
│  │      VNRM Microservice Access          │                │
│  │  - PRT: PDA file processing            │                │
│  │  - NUM: Block import/export            │                │
│  │  - COR: Error file logging             │                │
│  └────────────────────────────────────────┘                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**File Processing Workflow:**
```
1. External Partner Upload:
   Partner → SFTP → Communication Server → User Inbox

2. File Validation:
   Communication Server → Virus Scan → Format Validation

3. VNRM Processing:
   File Monitor → Detect New File → Trigger Processing
   VNRM Service → Read File → Process Data → Move to Archive

4. Response Generation:
   VNRM Service → Generate Response File → Write to Outbox
   Communication Server → SFTP → Partner Retrieval
```

#### SFTP Server Configuration

**Spring Integration SFTP:**
```java
@Configuration
public class SftpConfiguration {

    @Bean
    public SessionFactory<SftpClient.DirEntry> sftpSessionFactory() {
        DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory(true);
        factory.setHost(sftpHost);
        factory.setPort(sftpPort);
        factory.setUser(sftpUser);
        factory.setPrivateKey(new ClassPathResource("sftp-private-key"));
        factory.setPrivateKeyPassphrase(privateKeyPassphrase);
        factory.setAllowUnknownKeys(false);
        return new CachingSessionFactory<>(factory);
    }

    @Bean
    public SftpInboundFileSynchronizer sftpInboundFileSynchronizer() {
        SftpInboundFileSynchronizer synchronizer =
            new SftpInboundFileSynchronizer(sftpSessionFactory());
        synchronizer.setDeleteRemoteFiles(false);
        synchronizer.setRemoteDirectory("/upload");
        synchronizer.setFilter(new SftpSimplePatternFileListFilter("*.pda"));
        return synchronizer;
    }

    @Bean
    @InboundChannelAdapter(channel = "sftpChannel", poller = @Poller(fixedDelay = "60000"))
    public MessageSource<File> sftpMessageSource() {
        SftpInboundFileSynchronizingMessageSource source =
            new SftpInboundFileSynchronizingMessageSource(sftpInboundFileSynchronizer());
        source.setLocalDirectory(new File("/communication-server/users/technical-ext-sst/inbox"));
        source.setAutoCreateLocalDirectory(true);
        source.setLocalFilter(new AcceptOnceFileListFilter<>());
        return source;
    }

    @ServiceActivator(inputChannel = "sftpChannel")
    public void handleInboundFile(File file) {
        log.info("Received file via SFTP: {}", file.getName());
        fileProcessingService.processInboundFile(file);
    }
}
```

#### Archive Management

**Automated Archival:**
```java
@Service
@Slf4j
public class FileArchivalService {

    @Scheduled(cron = "0 0 2 * * ?")  // Daily at 2 AM
    public void archiveProcessedFiles() {
        LocalDate archiveDate = LocalDate.now().minusDays(7);

        // Archive files older than 7 days
        Path[] userDirectories = {
            Paths.get("/communication-server/users/technical-vnrm-system/processing"),
            Paths.get("/communication-server/users/technical-ext-sst/uploads")
        };

        for (Path userDir : userDirectories) {
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(userDir)) {
                for (Path file : stream) {
                    FileTime lastModified = Files.getLastModifiedTime(file);
                    LocalDate fileDate = lastModified.toInstant()
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate();

                    if (fileDate.isBefore(archiveDate)) {
                        archiveFile(file);
                    }
                }
            } catch (IOException e) {
                log.error("Error archiving files from directory: {}", userDir, e);
            }
        }
    }

    private void archiveFile(Path file) throws IOException {
        LocalDate fileDate = Files.getLastModifiedTime(file)
            .toInstant()
            .atZone(ZoneId.systemDefault())
            .toLocalDate();

        String yearMonth = fileDate.format(DateTimeFormatter.ofPattern("yyyy/MM-MMMM"));
        Path archiveDir = Paths.get("/communication-server/archive/" + yearMonth);

        Files.createDirectories(archiveDir);
        Path archivePath = archiveDir.resolve(file.getFileName());

        Files.move(file, archivePath, StandardCopyOption.REPLACE_EXISTING);

        log.info("Archived file: {} to {}", file.getFileName(), archivePath);
    }
}
```

### VNRM-RNVS Database API

#### Database Bridge Architecture

**Dual Database Connectivity:**
```java
@Configuration
public class DatabaseConfiguration {

    // VNRM PostgreSQL Configuration
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.vnrm")
    public DataSource vnrmDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean vnrmEntityManagerFactory(
            @Qualifier("vnrmDataSource") DataSource dataSource) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource);
        em.setPackagesToScan("com.telekom.vnrm.domain");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        em.setPersistenceUnitName("vnrm");
        return em;
    }

    // RNVS Oracle Configuration
    @Bean
    @ConfigurationProperties("spring.datasource.rnvs")
    public DataSource rnvsDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean rnvsEntityManagerFactory(
            @Qualifier("rnvsDataSource") DataSource dataSource) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource);
        em.setPackagesToScan("com.telekom.rnvs.domain");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        em.setPersistenceUnitName("rnvs");
        return em;
    }

    // Transaction Managers
    @Bean
    @Primary
    public PlatformTransactionManager vnrmTransactionManager(
            @Qualifier("vnrmEntityManagerFactory") EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }

    @Bean
    public PlatformTransactionManager rnvsTransactionManager(
            @Qualifier("rnvsEntityManagerFactory") EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }

    // Distributed Transaction Manager
    @Bean
    public ChainedTransactionManager chainedTransactionManager(
            @Qualifier("vnrmTransactionManager") PlatformTransactionManager vnrmTxManager,
            @Qualifier("rnvsTransactionManager") PlatformTransactionManager rnvsTxManager) {
        return new ChainedTransactionManager(vnrmTxManager, rnvsTxManager);
    }
}
```

#### Data Synchronization Patterns

**1. Dual-Write Pattern:**
```java
@Service
public class DualWriteSyncService {

    @Autowired
    @Qualifier("vnrmTransactionManager")
    private PlatformTransactionManager vnrmTxManager;

    @Autowired
    @Qualifier("rnvsTransactionManager")
    private PlatformTransactionManager rnvsTxManager;

    @Transactional("chainedTransactionManager")
    public void syncCallnumberUpdate(Callnumber vnrmCallnumber) {
        try {
            // 1. Update VNRM database
            vnrmCallnumberRepository.save(vnrmCallnumber);

            // 2. Transform to RNVS format
            RnvsRufnummer rnvsRufnummer = transformToRnvs(vnrmCallnumber);

            // 3. Update RNVS database
            rnvsRufnummerRepository.save(rnvsRufnummer);

            // 4. Log successful sync
            syncAuditRepository.save(createSyncAudit(vnrmCallnumber, SyncStatus.SUCCESS));

        } catch (Exception ex) {
            // Rollback both transactions on failure
            log.error("Dual-write sync failed for callnumber: {}",
                      vnrmCallnumber.getCallnumber(), ex);
            syncAuditRepository.save(createSyncAudit(vnrmCallnumber, SyncStatus.FAILED));
            throw ex;
        }
    }

    private RnvsRufnummer transformToRnvs(Callnumber vnrmCallnumber) {
        return RnvsRufnummer.builder()
            .trOnkz(vnrmCallnumber.getLocalAreaCode())
            .trRufnr(vnrmCallnumber.getCallnumber())
            .trSperre(mapStateToRnvs(vnrmCallnumber.getCallnumberstate()))
            .trBuchungskz(vnrmCallnumber.getBookingType())
            .trGueltigVon(Date.from(vnrmCallnumber.getValidFrom()
                .atZone(ZoneId.systemDefault()).toInstant()))
            .trGueltigBis(Date.from(vnrmCallnumber.getValidTo()
                .atZone(ZoneId.systemDefault()).toInstant()))
            .trRnbid(vnrmCallnumber.getCallnumberBlockId())
            .trKontingentId(vnrmCallnumber.getContingentId())
            .build();
    }

    private String mapStateToRnvs(String vnrmState) {
        // Map VNRM VARCHAR(1) state to RNVS VARCHAR(1) state
        return switch (vnrmState) {
            case "A" -> "F";  // AVAILABLE → frei
            case "R" -> "R";  // RESERVED → reserviert
            case "V" -> "V";  // ACTIVATED → vergeben
            case "B" -> "B";  // BLOCKED → blockiert
            case "W" -> "W";  // WAITING → warten
            case "P" -> "P";  // PROCESSING → in Verarbeitung
            default -> "F";   // Default to frei
        };
    }
}
```

**2. Event Sourcing Pattern:**
```java
@Service
public class EventSourcingSyncService {

    @Autowired
    private Message BusTemplate<String, SyncEvent> message_busTemplate;

    @Message BusListener(topics = "vnrm.num.callnumber-updated")
    public void handleCallnumberUpdate(CallnumberUpdatedEvent event) {
        // 1. Persist event to event store
        SyncEvent syncEvent = SyncEvent.builder()
            .eventType(EventType.CALLNUMBER_UPDATED)
            .aggregateId(event.getCallnumber())
            .eventData(objectMapper.writeValueAsString(event))
            .timestamp(LocalDateTime.now())
            .processed(false)
            .build();

        eventStoreRepository.save(syncEvent);

        // 2. Process synchronization
        try {
            syncToRnvs(event);
            syncEvent.setProcessed(true);
            syncEvent.setProcessedAt(LocalDateTime.now());
        } catch (Exception ex) {
            syncEvent.setFailed(true);
            syncEvent.setErrorMessage(ex.getMessage());
        }

        eventStoreRepository.save(syncEvent);
    }

    // Event replay capability
    public void replayEvents(LocalDateTime from, LocalDateTime to) {
        List<SyncEvent> unprocessedEvents = eventStoreRepository
            .findByProcessedFalseAndTimestampBetween(from, to);

        for (SyncEvent event : unprocessedEvents) {
            try {
                CallnumberUpdatedEvent callnumberEvent =
                    objectMapper.readValue(event.getEventData(), CallnumberUpdatedEvent.class);
                syncToRnvs(callnumberEvent);
                event.setProcessed(true);
            } catch (Exception ex) {
                log.error("Event replay failed for event: {}", event.getEventId(), ex);
            }
        }
    }
}
```

**3. CQRS Pattern:**
```java
// Command side (Write model) - VNRM
@Service
public class CallnumberCommandService {

    @Autowired
    private CallnumberRepository vnrmRepository;

    @Autowired
    private RnvsSyncService rnvsSyncService;

    @Transactional("vnrmTransactionManager")
    public void updateCallnumber(CallnumberCommand command) {
        // Update VNRM (write model)
        Callnumber callnumber = vnrmRepository.findById(command.getCallnumber())
            .orElseThrow(() -> new CallnumberNotFoundException(command.getCallnumber()));

        callnumber.setCallnumberstate(command.getState());
        callnumber.setUpdatedAt(LocalDateTime.now());
        vnrmRepository.save(callnumber);

        // Async sync to RNVS
        rnvsSyncService.syncAsync(callnumber);
    }
}

// Query side (Read model) - Supports both VNRM and RNVS
@Service
public class CallnumberQueryService {

    @Autowired
    @Qualifier("vnrmEntityManagerFactory")
    private EntityManager vnrmEntityManager;

    @Autowired
    @Qualifier("rnvsEntityManagerFactory")
    private EntityManager rnvsEntityManager;

    public CallnumberView getCallnumber(String callnumber, DataSource source) {
        if (source == DataSource.VNRM) {
            return queryFromVnrm(callnumber);
        } else {
            return queryFromRnvs(callnumber);
        }
    }

    public ComparisonResult compareCallnumber(String callnumber) {
        CallnumberView vnrmView = queryFromVnrm(callnumber);
        CallnumberView rnvsView = queryFromRnvs(callnumber);
        return new ComparisonResult(vnrmView, rnvsView, calculateDifferences(vnrmView, rnvsView));
    }
}
```

**4. Saga Pattern:**
```java
@Service
@Slf4j
public class PortingSagaCoordinator {

    @Autowired
    private CallnumberCommandService callnumberService;

    @Autowired
    private RnvsSyncService rnvsSyncService;

    @Autowired
    private NetworkRoutingService networkService;

    @Transactional
    public void executePortingSaga(PortingOrder order) {
        SagaState state = new SagaState();

        try {
            // Step 1: Update callnumber in VNRM
            state.callnumberUpdated = true;
            callnumberService.updateCallnumberState(
                order.getCallnumber(),
                CallnumberState.PROCESSING
            );

            // Step 2: Sync to RNVS
            state.rnvsSynced = true;
            rnvsSyncService.syncPortingState(order.getCallnumber());

            // Step 3: Update network routing
            state.routingUpdated = true;
            networkService.updateRoutingForPorting(
                order.getCallnumber(),
                order.getPkAb(),
                order.getPkAuf()
            );

            // Step 4: Mark porting complete
            callnumberService.updateCallnumberState(
                order.getCallnumber(),
                CallnumberState.ACTIVATED
            );

            log.info("Porting saga completed successfully for: {}", order.getCallnumber());

        } catch (Exception ex) {
            log.error("Porting saga failed, executing compensating actions", ex);
            compensate(state, order);
            throw ex;
        }
    }

    private void compensate(SagaState state, PortingOrder order) {
        // Compensating actions in reverse order
        if (state.routingUpdated) {
            try {
                networkService.rollbackRouting(order.getCallnumber());
            } catch (Exception ex) {
                log.error("Routing rollback failed", ex);
            }
        }

        if (state.rnvsSynced) {
            try {
                rnvsSyncService.rollbackSync(order.getCallnumber());
            } catch (Exception ex) {
                log.error("RNVS sync rollback failed", ex);
            }
        }

        if (state.callnumberUpdated) {
            try {
                callnumberService.updateCallnumberState(
                    order.getCallnumber(),
                    CallnumberState.ACTIVATED  // Restore previous state
                );
            } catch (Exception ex) {
                log.error("Callnumber state rollback failed", ex);
            }
        }
    }

    @Data
    private static class SagaState {
        boolean callnumberUpdated = false;
        boolean rnvsSynced = false;
        boolean routingUpdated = false;
    }
}
```

#### Schema Translation and Mapping

**VNRM to RNVS Field Mapping:**

| VNRM Table | VNRM Field | VNRM Type | RNVS Table | RNVS Field | RNVS Type | Transformation |
|------------|------------|-----------|------------|------------|-----------|----------------|
| callnumber | callnumber | VARCHAR(15) | T_RUFNR | TR_RUFNR | VARCHAR2(20) | Direct mapping |
| callnumber | local_area_code | VARCHAR(5) | T_RUFNR | TR_ONKZ | VARCHAR2(5) | Direct mapping |
| callnumber | callnumberstate | VARCHAR(1) | T_RUFNR | TR_SPERRE | VARCHAR2(1) | State code mapping |
| callnumber | booking_type | VARCHAR(1) | T_RUFNR | TR_BUCHUNGSKZ | VARCHAR2(1) | Direct mapping |
| callnumber | valid_from | TIMESTAMP(6) | T_RUFNR | TR_GUELTIG_VON | DATE | PostgreSQL TIMESTAMP → Oracle DATE |
| callnumber | valid_to | TIMESTAMP(6) | T_RUFNR | TR_GUELTIG_BIS | DATE | PostgreSQL TIMESTAMP → Oracle DATE |
| callnumber | callnumber_block_id | VARCHAR(13) | T_RUFNR | TR_RNBID | VARCHAR2(13) | Direct mapping |
| callnumber | contingent_id | INTEGER | T_RUFNR | TR_KONTINGENT_ID | NUMBER(10) | PostgreSQL INTEGER → Oracle NUMBER |

**State Code Mapping:**
```java
public class StateCodeMapper {

    // VNRM → RNVS
    public static String vnrmToRnvs(String vnrmState) {
        return switch (vnrmState) {
            case "A" -> "F";  // AVAILABLE → frei
            case "R" -> "R";  // RESERVED → reserviert
            case "V" -> "V";  // ACTIVATED → vergeben
            case "B" -> "B";  // BLOCKED → blockiert
            case "W" -> "W";  // WAITING → warten
            case "P" -> "P";  // PROCESSING → in Verarbeitung
            case "Z" -> "Z";  // BNETZA → BNETZA
            default -> "F";
        };
    }

    // RNVS → VNRM
    public static String rnvsToVnrm(String rnvsState) {
        return switch (rnvsState) {
            case "F" -> "A";  // frei → AVAILABLE
            case "R" -> "R";  // reserviert → RESERVED
            case "V" -> "V";  // vergeben → ACTIVATED
            case "B" -> "B";  // blockiert → BLOCKED
            case "W" -> "W";  // warten → WAITING
            case "P" -> "P";  // in Verarbeitung → PROCESSING
            case "Z" -> "Z";  // BNETZA → BNETZA
            default -> "A";
        };
    }
}
```

## Migration Strategy & Decommissioning

### Phased Migration Approach

**Phase 1: Parallel Operation (Current State)**
```
Timeline: 2024-2025
Status: VNRM and RNVS both operational

Architecture:
┌────────────┐
│   VNRM     │ ←→ SPE DB API ←→ ┌────────────┐
│ PostgreSQL │                   │   RNVS     │
└────────────┘                   │  Oracle    │
                                 └────────────┘

Characteristics:
- Dual-write to both systems
- RNVS remains system of record
- VNRM validates against RNVS
- Complete bidirectional sync
```

**Phase 2: Gradual Migration (2025-2026)**
```
Timeline: 2025-2026
Status: Migrating functionality from RNVS to VNRM

Migration Sequence:
1. NUM services migration (callnumber management)
2. PRT services migration (porting operations)
3. Block management migration
4. Reporting migration
5. RNVS decommissioning

Validation:
- Data consistency checks
- Parallel processing validation
- Performance benchmarking
- Rollback capability maintained
```

**Phase 3: VNRM Primary (2026-2027)**
```
Timeline: 2026-2027
Status: VNRM becomes system of record

Architecture:
┌────────────┐
│   VNRM     │ ──→ SPE DB API ──→ ┌────────────┐
│ PostgreSQL │ (read-only sync)   │   RNVS     │
└────────────┘                     │  Oracle    │
                                   └────────────┘

Characteristics:
- VNRM is primary system
- RNVS receives read-only sync
- Gradual RNVS feature deprecation
- SPE services transition plan
```

**Phase 4: SPE Decommissioning (2027+)**
```
Timeline: 2027+
Status: RNVS retired, SPE services decommissioned

Architecture:
┌────────────┐
│   VNRM     │ (standalone)
│ PostgreSQL │
└────────────┘

Characteristics:
- RNVS completely retired
- SPE database API decommissioned
- BEAA integrated directly with CRM-T
- COMS becomes standalone file service
```

### Incremental Data Sync Strategy

**Initial Data Migration:**
```java
@Service
@Slf4j
public class InitialDataMigrationService {

    @Autowired
    private RnvsCallnumberRepository rnvsRepository;

    @Autowired
    private VnrmCallnumberRepository vnrmRepository;

    @Async
    public CompletableFuture<MigrationResult> migrateCallnumbers(
            String onkz, int batchSize) {

        MigrationResult result = new MigrationResult();
        int offset = 0;
        boolean hasMore = true;

        while (hasMore) {
            try {
                // Fetch batch from RNVS
                List<RnvsRufnummer> rnvsBatch = rnvsRepository
                    .findByOnkzWithPagination(onkz, offset, batchSize);

                if (rnvsBatch.isEmpty()) {
                    hasMore = false;
                    break;
                }

                // Transform and insert to VNRM
                List<Callnumber> vnrmBatch = rnvsBatch.stream()
                    .map(this::transformToVnrm)
                    .collect(Collectors.toList());

                vnrmRepository.saveAll(vnrmBatch);

                result.incrementProcessed(vnrmBatch.size());
                offset += batchSize;

                log.info("Migrated batch: ONKZ={}, offset={}, count={}",
                         onkz, offset, vnrmBatch.size());

            } catch (Exception ex) {
                log.error("Migration batch failed: ONKZ={}, offset={}",
                          onkz, offset, ex);
                result.incrementFailed(batchSize);
            }
        }

        return CompletableFuture.completedFuture(result);
    }

    private Callnumber transformToVnrm(RnvsRufnummer rnvsRufnr) {
        return Callnumber.builder()
            .localAreaCodeCallnumber(rnvsRufnr.getTrOnkz() + rnvsRufnr.getTrRufnr())
            .callnumber(rnvsRufnr.getTrRufnr())
            .localAreaCode(rnvsRufnr.getTrOnkz())
            .callnumberstate(StateCodeMapper.rnvsToVnrm(rnvsRufnr.getTrSperre()))
            .bookingType(rnvsRufnr.getTrBuchungskz())
            .validFrom(rnvsRufnr.getTrGueltigVon().toLocalDateTime())
            .validTo(rnvsRufnr.getTrGueltigBis().toLocalDateTime())
            .callnumberBlockId(rnvsRufnr.getTrRnbid())
            .contingentId(rnvsRufnr.getTrKontingentId())
            .build();
    }
}
```

**Continuous Sync Validation:**
```java
@Service
public class SyncValidationService {

    @Scheduled(cron = "0 0 * * * ?")  // Every hour
    public void validateDataConsistency() {
        // Sample random callnumbers
        List<String> sampleCallnumbers = selectRandomSample(1000);

        int inconsistencies = 0;
        for (String callnumber : sampleCallnumbers) {
            CallnumberView vnrmView = vnrmQueryService.getCallnumber(callnumber);
            CallnumberView rnvsView = rnvsQueryService.getCallnumber(callnumber);

            if (!areConsistent(vnrmView, rnvsView)) {
                inconsistencies++;
                logInconsistency(callnumber, vnrmView, rnvsView);
            }
        }

        double consistencyRate = ((double) (sampleCallnumbers.size() - inconsistencies) /
                                  sampleCallnumbers.size()) * 100;

        meterRegistry.gauge("spe.sync.consistency.rate", consistencyRate);

        if (consistencyRate < 99.9) {
            alertService.sendAlert(
                AlertType.DATA_CONSISTENCY,
                String.format("Sync consistency rate below threshold: %.2f%%", consistencyRate)
            );
        }
    }

    private boolean areConsistent(CallnumberView vnrm, CallnumberView rnvs) {
        return Objects.equals(vnrm.getCallnumber(), rnvs.getCallnumber())
            && Objects.equals(vnrm.getState(), rnvs.getState())
            && Objects.equals(vnrm.getBookingType(), rnvs.getBookingType())
            && Objects.equals(vnrm.getValidFrom(), rnvs.getValidFrom())
            && Objects.equals(vnrm.getValidTo(), rnvs.getValidTo());
    }
}
```

### Rollback and Disaster Recovery

**Rollback Strategy:**
```java
@Service
public class RollbackService {

    @Transactional
    public RollbackResult rollbackToRnvs(String callnumber) {
        // 1. Fetch authoritative data from RNVS
        RnvsRufnummer rnvsData = rnvsRepository.findByCallnumber(callnumber)
            .orElseThrow(() -> new CallnumberNotFoundException(callnumber));

        // 2. Transform to VNRM format
        Callnumber vnrmData = transformToVnrm(rnvsData);

        // 3. Override VNRM data with RNVS data
        vnrmRepository.save(vnrmData);

        // 4. Log rollback action
        RollbackLog log = RollbackLog.builder()
            .callnumber(callnumber)
            .rollbackType(RollbackType.SINGLE_CALLNUMBER)
            .timestamp(LocalDateTime.now())
            .performedBy(SecurityContextHolder.getContext().getAuthentication().getName())
            .build();

        rollbackLogRepository.save(log);

        return RollbackResult.success(callnumber);
    }

    public RollbackResult rollbackAllToRnvs() {
        // Emergency rollback: restore all VNRM data from RNVS
        log.warn("Executing full database rollback to RNVS");

        // Disable ongoing sync
        syncService.disableSync();

        // Perform bulk rollback in batches
        // ... implementation ...

        return RollbackResult.success("ALL");
    }
}
```

## Integration Dependencies

### Internal VNRM Dependencies

**NUM Submodule Integration:**
- **Database Sync**: SPE synchronizes NUM callnumber data with RNVS
- **Event Consumption**: SPE listens to NUM state change events for sync triggers
- **Validation**: SPE validates NUM data against RNVS for consistency checks
- **BEAA Access**: NUM uses BEAA to access CRM-T product inventory

**PRT Submodule Integration:**
- **Porting Data Sync**: SPE synchronizes porting orders with RNVS
- **File Exchange**: COMS handles PDA file exchange for porting operations
- **State Synchronization**: PRT porting states synchronized to RNVS via SPE
- **Event Bus**: SPE publishes porting events consumed by PRT

**COM Submodule Integration:**
- **Configuration Server**: SPE uses COM config-server for sync rules and mappings
- **RDM**: SPE validates ONKZ and TSP data via COM RDM
- **Error Catalog**: SPE integration errors reported using COM error codes
- **Portal**: SPE admin interfaces embedded in COM portal

**COR Correction Integration:**
- **Error Reporting**: SPE sync failures reported to COR for tracking
- **Manual Correction**: COR provides manual correction workflows for sync issues
- **Audit Integration**: Complete sync error history in COR

### External System Dependencies

**Legacy RNVS (Critical External Dependency):**
- **Purpose**: Legacy call number management system (Oracle database)
- **Integration**:
  - Direct database access via JDBC
  - Bidirectional data synchronization
  - Schema translation (PostgreSQL ↔ Oracle)
  - Transaction coordination
- **Network**: Secure connection to legacy RNVS infrastructure
- **Availability**: RNVS availability critical for SPE operations

**CRM-T (Customer Relationship Management):**
- **Purpose**: Customer data and contract management (external to VNRM)
- **Integration**:
  - BEAA provides proxy access to CRM-T APIs
  - View-only access (read operations only)
  - Product Inventory, Order Information, Provider Change, Agreement Data
- **Security**: Tardis M2M authentication (Iris + Stargate)
- **Communication**: RESTful API via Tardis gateway

**External Partners (via COMS):**
- **BNetzA**: Federal Network Agency file exchange
- **TSPs**: Carrier PDA file exchange (~160 German TSPs)
- **Third-Party Systems**: Various external system integrations
- **Communication**: SFTP file-based exchange

## Technology Stack & Implementation Details

### Backend Technologies

**Spring Boot Ecosystem:**
- **Version**: Spring Boot 2.7.x
- **Spring Cloud Gateway**: Routing and proxy for BEAA
- **Spring Integration**: SFTP file handling for COMS
- **Spring Data JPA**: Multi-datasource support (PostgreSQL + Oracle)
- **Spring Batch**: Bulk data migration and synchronization
- **Spring Security**: Authentication and authorization

**Database:**
- **PostgreSQL 13+**: VNRM primary database
- **Oracle 12c+**: RNVS legacy database (read/write access)
- **HikariCP**: High-performance connection pooling (dual datasources)
- **Distributed Transactions**: Chained transaction manager for consistency

**Messaging & Events:**
- **Message Bus**: Event-driven sync triggers
- **Event Store**: Persist sync events for replay capability
- **Schema Registry**: Avro schemas for event serialization

### Integration Technologies

**SFTP Support (COMS):**
- **Spring Integration SFTP**: File synchronization and transfer
- **Apache SSHD**: SFTP server implementation
- **File System API (NIO.2)**: High-performance file operations
- **Scheduled Polling**: Periodic directory scanning for new files

**Security:**
- **Tardis M2M**: Machine-to-machine authentication
- **Iris**: Telekom identity provider
- **Stargate**: Authorization gateway
- **JWT Tokens**: Token-based authentication
- **Certificate Authentication**: Client certificates for SFTP

**Monitoring:**
- **Prometheus**: Metrics collection (sync rates, consistency, latency)
- **Grafana**: Operational dashboards
- **ELK Stack**: Centralized logging
- **Distributed Tracing**: Correlation IDs across systems

## Monitoring & Operational Excellence

### Prometheus Metrics

```yaml
# Database sync metrics
spe_sync_operations_total{direction, entity_type, status}
spe_sync_duration_seconds{direction, entity_type}
spe_sync_consistency_rate  # Percentage (0-100)
spe_sync_lag_seconds  # Replication lag between VNRM and RNVS

# BEAA proxy metrics
beaa_requests_total{target_system, endpoint, status}
beaa_request_duration_seconds{target_system, endpoint}
beaa_circuit_breaker_state{target_system}  # open/closed/half_open

# COMS file metrics
coms_files_processed_total{direction, file_type, status}
coms_file_processing_duration_seconds{file_type}
coms_sftp_connections_active
coms_archive_size_bytes{year_month}

# Migration progress metrics
spe_migration_progress_percent{entity_type}
spe_migration_remaining_records{entity_type}
```

### Operational Dashboards

**Dashboard 1: Database Sync Health**
- Sync consistency rate (gauge with 99.9% threshold)
- Replication lag (time series)
- Sync operations per minute (time series)
- Failed sync operations (table with details)
- Dual-write transaction success rate (gauge)

**Dashboard 2: BEAA Proxy Health**
- Request volume by target system (bar chart)
- Response time distribution (histogram)
- Circuit breaker status (indicator)
- Error rate by endpoint (time series)
- CRM-T availability (gauge)

**Dashboard 3: COMS File Processing**
- Files processed per hour (time series)
- Processing duration by file type (box plot)
- SFTP connection status (indicator)
- Archive growth trend (time series)
- Failed file processing (table)

**Dashboard 4: Migration Progress**
- Overall migration progress (gauge)
- Entity type migration status (multi-bar)
- Estimated completion time (calculated)
- Data validation results (table)

## Best Practices

### Database Synchronization
1. **Dual-write consistency** - Ensure both VNRM and RNVS updated in single transaction
2. **Idempotent sync operations** - Support retry without side effects
3. **Complete audit trail** - Log all sync operations with full context
4. **Data validation** - Verify consistency with scheduled validation jobs
5. **Schema evolution** - Plan for schema changes in both systems
6. **Performance monitoring** - Track sync latency and throughput

### Legacy System Integration
1. **Circuit breakers** - Handle RNVS unavailability gracefully with fallback strategies
2. **Retry logic** - Exponential backoff for transient failures
3. **Connection pooling** - Optimize database connections for both datasources
4. **Transaction isolation** - Proper isolation levels for consistency
5. **Error propagation** - Report integration errors to COR for tracking
6. **Rollback capability** - Maintain RNVS as fallback system of record

### Backend Automation (BEAA)
1. **View-only access** - Never enable write operations to CRM-T via proxy
2. **Request monitoring** - Log all proxy requests for audit and troubleshooting
3. **Security validation** - Strict M2M authentication for all requests
4. **Rate limiting** - Prevent abuse and manage load on target systems
5. **Cache where appropriate** - Cache CRM-T responses for frequently accessed data
6. **Timeout configuration** - Set appropriate timeouts for external system calls

### Communication Server (COMS)
1. **Role-based access** - Strict enforcement of user permissions
2. **File validation** - Virus scanning and format validation for all uploads
3. **Archive management** - Automated archival with retention policies
4. **Network security** - Secure SFTP with certificate authentication
5. **Monitoring** - Track file processing metrics and failures
6. **Disaster recovery** - Regular backups of file system

### Migration Strategy
1. **Phased approach** - Gradual migration to minimize business disruption
2. **Data validation** - Continuous validation between VNRM and RNVS
3. **Rollback readiness** - Maintain ability to revert to RNVS if needed
4. **Performance benchmarking** - Ensure VNRM meets or exceeds RNVS performance
5. **Knowledge transfer** - Document all integration patterns for future reference
6. **Decommissioning plan** - Clear timeline and criteria for SPE retirement

### Operational Excellence
1. **OT service awareness** - Business hours support only (3-day response)
2. **Legacy system monitoring** - Track RNVS health and availability
3. **Sync health tracking** - Monitor data consistency rates (>99.9% target)
4. **Capacity planning** - Ensure adequate resources for migration peaks
5. **Documentation** - Maintain comprehensive integration documentation
6. **Sunset planning** - Prepare for SPE decommissioning after RNVS retirement

---

**See also:**
- [NUM Architecture Reference](../vnrm-num-architecture/REFERENCE.md) - Number Management Data Sync
- [PRT Architecture Reference](../vnrm-prt-architecture/REFERENCE.md) - Porting Data Sync
- [COM Architecture Reference](../vnrm-com-architecture/REFERENCE.md) - Configuration and Reference Data
- [COR Architecture Reference](../vnrm-cor-architecture/REFERENCE.md) - Error Management Integration
