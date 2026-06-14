# VNRM COM Architecture - Usage Examples

This document provides practical examples of how agents use the COM architecture expert skill during the RNVS→VNRM migration workflow.

## Example 1: microservice-architect Agent (Phase 6)

### Scenario
The microservice-architect agent is designing the Reference Data Management (RDM) microservice during Phase 6 of the workflow.

### Agent Workflow
```markdown
User invokes: /phase6-design-microservice for RDM component

Agent consults vnrm-com-architecture-expert:
1. Reviews RDM functional requirements
2. Identifies deployed services (com-rdm-reference-data-management-api/gui)
3. Examines database schemas (onkz, tsp, rnb_reference tables)
4. Understands integration patterns (PDA, KLS, RNVS sync)
5. Notes service level (OT currently, HA evaluation pending)

Agent produces:
- Architecture diagram showing RDM service boundaries
- Database schema with ONKZ, TSP, RNB tables
- REST API specification with endpoints
- Integration diagram with NUM, PRT, SPE dependencies
- Non-functional requirements (SLA, performance, security)
```

### Key Knowledge Used
- **RDM Interface Architecture**: Communication patterns with PDA, KLS, RNVS
- **Database Schemas**: PostgreSQL table structures for reference data
- **Service Level Requirements**: OT level with HA re-evaluation plan
- **Technology Stack**: Spring Boot, PostgreSQL, REST APIs

---

## Example 2: code-generator Agent (Phase 12)

### Scenario
The code-generator agent is implementing the Configuration Server API during Phase 12.

### Agent Workflow
```markdown
User invokes: /phase12-generate-source-code for Configuration Server API

Agent consults vnrm-com-architecture-expert:
1. Reviews Configuration Server (CONFS) technical implementation
2. Examines Spring Cloud Config architecture patterns
3. Studies configuration repository structure
4. Understands encryption support (symmetric/asymmetric)
5. Reviews dynamic refresh mechanisms

Agent generates:
- Spring Boot application with @EnableConfigServer
- Git-based configuration backend
- Encryption/decryption endpoints
- Health check and actuator endpoints
- Docker containerization setup
```

### Generated Code Example
```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}

// application.yml
spring:
  application:
    name: com-cs-config-server-api
  cloud:
    config:
      server:
        git:
          uri: https://gitlab.telekom.de/vnrm/config-repo
          default-label: main
          search-paths: '{application}'
          clone-on-start: true
        encrypt:
          enabled: true
  profiles:
    active: native
```

### Key Knowledge Used
- **Spring Cloud Config Implementation**: Git backend, profiles, labels
- **Encryption Patterns**: {cipher} prefix, keystore configuration
- **Dynamic Refresh**: Spring Cloud Bus, Message Bus integration
- **Actuator Endpoints**: Health checks, refresh endpoint

---

## Example 3: Integration Pattern - NUM Depends on COM RDM

### Scenario
Designing NUM microservices that need ONKZ and TSP validation.

### Integration Design
```markdown
NUM Service: num-fcm-fixednet-callnumber-management-api

Dependencies on COM:
1. Configuration Server (com-cs-config-server-api)
   - Retrieves database connection settings
   - Gets business rule thresholds (reservation timeout, DuWa threshold)

2. Reference Data Management (com-rdm-reference-data-management-api)
   - Validates ONKZ before callnumber allocation
   - Retrieves TSP information for porting operations
   - Checks number block ownership

3. Error Catalog (com-ecc-errorcode-catalog-api)
   - Retrieves standardized NUM error codes
   - Returns localized error messages (German/English)
```

### API Integration Example
```java
@Service
public class CallnumberValidationService {

    @Autowired
    private RdmClient rdmClient;  // Feign client to RDM API

    @Autowired
    private ErrorCatalogClient errorCatalogClient;

    public void validateCallnumber(String onkz, String callnumber) {
        // Validate ONKZ exists in RDM
        OnkzDto onkzData = rdmClient.getOnkz(onkz)
            .orElseThrow(() -> createError("NUM-H-0010"));

        // Validate callnumber format
        if (!callnumber.matches("\\d{7,10}")) {
            throw createError("NUM-M-0023");
        }
    }

    private CallnumberException createError(String errorCode) {
        ErrorCatalogEntry error = errorCatalogClient.getError(errorCode);
        return new CallnumberException(error);
    }
}
```

---

## Example 4: Configuration Management Workflow

### Scenario
Updating FCM service configuration to change reservation timeout.

### Step-by-Step Process
```bash
# 1. Update configuration in Git repository
cat > config-repo/num-fcm-fixednet-callnumber-management-api-prod.yml <<EOF
vnrm:
  fcm:
    reservation:
      timeout:
        minutes: 2880  # Changed from 1440 to 2880 (48 hours)
    duwa:
      threshold: 200
EOF

# 2. Commit and push to Git
git add config-repo/num-fcm-fixednet-callnumber-management-api-prod.yml
git commit -m "Increase FCM reservation timeout to 48 hours"
git push origin main

# 3. Config Server automatically detects change
# (Polling interval: every 5 seconds)

# 4. Trigger refresh on FCM service
curl -X POST https://vnrm.telekom.de/num-fcm/actuator/refresh \
  -H "Authorization: Bearer $JWT_TOKEN"

# 5. Verify new configuration
curl https://vnrm.telekom.de/num-fcm/actuator/env | \
  jq '.propertySources[] | select(.name | contains("config-server"))'

# Output shows new timeout value:
{
  "name": "configServer:file:///config-repo/num-fcm-fixednet-callnumber-management-api-prod.yml",
  "properties": {
    "vnrm.fcm.reservation.timeout.minutes": {
      "value": 2880
    }
  }
}
```

---

## Example 5: Reference Data Synchronization with Legacy RNVS

### Scenario
Synchronizing ONKZ reference data between VNRM RDM and legacy RNVS.

### Synchronization Job
```java
@Component
@Slf4j
public class OnkzSynchronizationJob {

    @Autowired
    private OnkzRepository vnrmOnkzRepository;

    @Autowired
    private RnvsDataSource rnvsDataSource;

    @Scheduled(cron = "0 0 2 * * *")  // Daily at 2 AM
    public void synchronizeOnkz() {
        log.info("Starting ONKZ synchronization with RNVS");

        // 1. Fetch ONKZ data from RNVS Oracle database
        List<RnvsOnkz> rnvsOnkzList = rnvsDataSource.query(
            "SELECT ONKZ_ID, ONKZ_NAME, BUNDESLAND, REGION " +
            "FROM T_ONKZ WHERE GUELTIG_BIS IS NULL",
            (rs, rowNum) -> RnvsOnkz.builder()
                .onkzId(rs.getString("ONKZ_ID"))
                .onkzName(rs.getString("ONKZ_NAME"))
                .federalState(rs.getString("BUNDESLAND"))
                .region(rs.getString("REGION"))
                .build()
        );

        // 2. Transform to VNRM model
        List<Onkz> vnrmOnkzList = rnvsOnkzList.stream()
            .map(this::transformToVnrm)
            .collect(Collectors.toList());

        // 3. Upsert to VNRM database
        vnrmOnkzList.forEach(onkz -> {
            vnrmOnkzRepository.findById(onkz.getOnkzId())
                .ifPresentOrElse(
                    existing -> updateOnkz(existing, onkz),
                    () -> vnrmOnkzRepository.save(onkz)
                );
        });

        log.info("ONKZ synchronization completed: {} records", vnrmOnkzList.size());
    }

    private Onkz transformToVnrm(RnvsOnkz rnvsOnkz) {
        return Onkz.builder()
            .onkzId(rnvsOnkz.getOnkzId())
            .onkzName(rnvsOnkz.getOnkzName())
            .federalState(rnvsOnkz.getFederalState())
            .region(rnvsOnkz.getRegion())
            .validFrom(LocalDate.now())
            .validTo(null)
            .build();
    }
}
```

---

## Example 6: Error Catalog Usage in PRT Services

### Scenario
PRT porting service encounters a PDA message validation error.

### Error Handling Flow
```java
@Service
public class PdaMessageValidator {

    @Autowired
    private ErrorCatalogService errorCatalogService;

    public void validatePdaMessage(PdaMessage message) {
        // Validate porting date
        if (message.getPortingDate().isBefore(LocalDate.now())) {
            throw createPortingError(
                "PRT-H-0042",
                Map.of(
                    "portingDate", message.getPortingDate().toString(),
                    "currentDate", LocalDate.now().toString(),
                    "pdaMessageId", message.getMessageId()
                )
            );
        }

        // Validate PK (Portierungskennung)
        if (!isValidPK(message.getPkAb()) || !isValidPK(message.getPkAuf())) {
            throw createPortingError(
                "PRT-H-0015",
                Map.of(
                    "pkAb", message.getPkAb(),
                    "pkAuf", message.getPkAuf()
                )
            );
        }
    }

    private PortingException createPortingError(
            String errorCode,
            Map<String, String> details) {

        ErrorCatalogEntry error = errorCatalogService.getError(errorCode);

        return PortingException.builder()
            .errorCode(error.getErrorCode())
            .severity(error.getSeverity())
            .messageDE(error.getErrorTitleDe())
            .messageEN(error.getErrorTitleEn())
            .details(details)
            .timestamp(LocalDateTime.now())
            .build();
    }
}
```

---

## Example 7: Portal Micro-UI Integration

### Scenario
Integrating RDM GUI as a micro-UI into the main VNRM portal.

### Portal Configuration
```typescript
// portal-routing.module.ts
const routes: Routes = [
  {
    path: 'rdm',
    loadChildren: () => import('@vnrm/rdm-gui').then(m => m.RdmModule),
    canActivate: [AuthGuard],
    data: {
      roles: ['VNRM_SYSA', 'VNRM_RDM_EDITOR'],
      title: 'Reference Data Management'
    }
  },
  {
    path: 'config',
    loadChildren: () => import('@vnrm/config-gui').then(m => m.ConfigModule),
    canActivate: [AuthGuard],
    data: {
      roles: ['VNRM_SYSA', 'VNRM_SYSA_NON_PROD'],
      title: 'Configuration Management'
    }
  }
];

// Navigation menu integration
export const COM_MENU_ITEMS: MenuItem[] = [
  {
    id: 'com-portal',
    label: 'COM - Common Services',
    icon: 'settings',
    children: [
      {
        id: 'rdm',
        label: 'Reference Data Management',
        route: '/rdm',
        icon: 'database',
        roles: ['VNRM_SYSA', 'VNRM_RDM_EDITOR']
      },
      {
        id: 'config',
        label: 'Configuration Server',
        route: '/config',
        icon: 'tune',
        roles: ['VNRM_SYSA']
      },
      {
        id: 'errors',
        label: 'Error Catalog',
        route: '/errors',
        icon: 'error_outline',
        roles: ['VNRM_SYSA', 'VNRM_SUPPORT']
      }
    ]
  }
];
```

---

## Example 8: TMF639 Resource Inventory API Usage

### Scenario
Querying callnumber resources using TMF639-compliant API.

### API Client Example
```bash
# Get all callnumber resources in Berlin (ONKZ 030)
curl -X GET "https://vnrm.telekom.de/tmf-api/resourceInventoryManagement/v4/resource? \
category=CallNumber&resourceCharacteristic.name=ONKZ&resourceCharacteristic.value=030" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Response
{
  "resource": [
    {
      "id": "RES-030-12345678-001",
      "href": "/tmf-api/resourceInventoryManagement/v4/resource/RES-030-12345678-001",
      "category": "CallNumber",
      "name": "Berlin Callnumber 030-12345678",
      "resourceCharacteristic": [
        {
          "name": "ONKZ",
          "value": "030"
        },
        {
          "name": "callnumber",
          "value": "12345678"
        },
        {
          "name": "callnumberType",
          "value": "SINGLE"
        }
      ],
      "resourceStatus": "AVAILABLE",
      "place": [
        {
          "id": "PLACE-BERLIN-001",
          "name": "Berlin",
          "role": "ServiceArea"
        }
      ]
    }
  ]
}
```

---

## Key Takeaways

1. **Configuration is Foundational**: All VNRM services depend on config-server
2. **Reference Data is Critical**: NUM, PRT, SPE all validate against RDM
3. **Error Catalog Standardizes**: Consistent error handling across submodules
4. **Portal Integration**: Micro-UI pattern for seamless user experience
5. **Legacy Synchronization**: Bidirectional sync with RNVS during migration
6. **TMF639 Compliance**: Industry-standard resource inventory management

---

**See also:**
- [SKILL.md](SKILL.md) - Overview and when to use this skill
- [REFERENCE.md](REFERENCE.md) - Complete architecture specifications
- [NUM Examples](../vnrm-num-architecture-expert/examples.md)
- [PRT Examples](../vnrm-prt-architecture-expert/examples.md)
