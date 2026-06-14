# VNRM COM (COMMON) Architecture Reference

## Overview

The VNRM COM (COMMON) submodule serves as the foundational layer of the Voice Number & Routing Management system, providing shared services and infrastructure used across all other VNRM submodules (NUM, PRT, COR, NTW, SPE). COM enables centralized management of portal access, platform services, reference data, configuration, and error management.

COM provides the essential infrastructure that makes VNRM a cohesive platform rather than a collection of independent microservices. It ensures consistency in configuration management, reference data access, error handling, and user experience across all VNRM operations.

## Architecture Building Blocks

Based on the VNRM architecture documentation, COM is organized into four foundational clusters that serve distinct but complementary purposes:

### Portal Management Cluster

Central access point for all VNRM functionality, serving as the unified user interface:

**Core Functions:**
- **User Interface Gateway**: Single entry point at `vnrm.telekom.de`
- **Display and Reporting**: Individual reports with data analysis capabilities
- **User Management**: User concept and access control
- **Reference Data Maintenance**: GUI-based data management
- **Configuration Interface**: System and control parameter configuration
- **File Operations**: Download and upload capabilities
- **Trouble Ticket Integration**: Integration with incident management
- **Business Application Links**: Credential transfer support for external systems
- **Documentation Access**: System documentation, interface specifications, user guides

**Integration Pattern:**
- **Micro Frontend Architecture**: Each functional area as independent micro UI
- **Portal Embedding**: Seamless integration within main portal framework
- **Single Sign-On**: Centralized authentication via Tardis/Iris
- **Monitoring Integration**: Tool views, links, or frontend embedding for operational monitoring

### Platform Management Cluster

Management of resource ownership distribution and shared services across the VNRM ecosystem:

**Core Functions:**
- **Resource Ownership Distribution**: Management across all VNRM microservices
- **Shared Functionalities**: Services used by multiple microservices
- **Statistics & Analytics**: Direct function triggering and working results analysis
- **TMF639 Facade**: Resource Inventory Management standard compliance
- **Configuration Distribution**: Centralized configuration for all services
- **Service Coordination**: Cross-microservice orchestration

**Strategic Importance:**
- Enables horizontal scaling of VNRM platform
- Prevents resource conflicts through centralized coordination
- Provides foundation for microservices autonomy with central governance

### Reference Data Management Cluster

Business reference data lifecycle management for the entire VNRM platform:

**Core Functions:**
- **Frontend as Micro UI**: Called from portal for seamless user experience
- **CRUD Operations**: Create, read, update, delete for reference data
- **Code Reference Setpoints**: Update and maintenance of system parameters
- **Master Data Management**: Business reference data stewardship
- **ONKZ Management**: German area code (Ortsnetzkennzahl) administration
- **TSP Information**: Telephony service provider data and carrier mapping
- **Data Synchronization**: Integration with legacy RNVS and external systems

**Data Flow Architecture:**
```
External Sources → RDM → VNRM Services
    ↓              ↓           ↓
- PDA Distributor  ├─ NUM (callnumber validation)
- KLS              ├─ PRT (porting operations)
- BNetzA           ├─ COR (error management)
- C@T              └─ SPE (legacy integration)
    ↓
Legacy RNVS (until retirement)
```

### Error Management Cluster

Centralized error handling providing consistency across all VNRM services:

**Core Functions:**
- **Error Code Catalog**: Standardized error codes for all VNRM domains
- **Error Versioning**: Catalog maintenance and version control
- **Localization**: German and English error messages
- **Resolution Actions**: Recommended corrective actions
- **Integration Point**: Foundation for COR business error management

**Strategic Value:**
- Consistent error handling improves user experience
- Standardized codes enable cross-service error correlation
- Facilitates troubleshooting and support operations
- Enables automated error analysis and alerting

## Service Level Architecture & Critical Dependencies

### Service Level Classification

**High Availability (HA) Services - 24/7 Support:**
- **Response Time**: 3 hours
- **Availability**: 24/7 on-call duty required
- **Support Channels**: Hotline + ServiceNow + FMB post box
- **Critical Impact**: Service outages affect multiple VNRM submodules

**Office Time (OT) Services - Business Hours Support:**
- **Response Time**: 3 days
- **Availability**: Business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Impact**: Limited to specific functional areas

### Critical Dependencies

**Single Points of Failure (HA Level Required):**

1. **com-cs-config-server-api** - Configuration server API
   - All VNRM microservices depend on configuration distribution
   - Failure cascades across entire VNRM platform
   - Real-time configuration updates required
   - **Business Impact**: Without config server, no service can start or refresh settings

2. **com-tsp-telephony-service-provider-api** - TSP API
   - Required for FCM (Fixed Callnumber Management) integration
   - Essential for number porting and carrier operations
   - Critical for PRT submodule functionality
   - **Business Impact**: Porting operations halt without TSP data

3. **vnrm-container** - Main portal container
   - Central access point for all VNRM operations
   - User interface gateway (vnrm.telekom.de)
   - Integration hub for microservice frontends
   - **Business Impact**: Users cannot access any VNRM functionality

**Service Level Dependencies:**
- **RDM API**: Currently OT level, planned for HA re-evaluation when porting process goes live
- **Error Catalog API**: OT level sufficient for current business operations

## Deployed Microservices

### Production Services (VNRM 1.9.0+)

#### Portal Management

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| vnrm-container | v2.4.0 | HA | Main VNRM portal container at vnrm.telekom.de | All COM services |
| vnrm-portal-gui | v1.9.0 | HA | Angular-based portal GUI | vnrm-container |
| vnrm-portal-backend-for-frontend | v1.9.0 | HA | Portal B4F pattern implementation | config-server, RDM |
| com-port-support-page | v1.5.0 | OT | Support page for user assistance | vnrm-container |

**Technical Stack:**
- **Frontend**: Angular 14+, TypeScript, Angular Material
- **Backend**: Spring Boot, Spring Cloud Gateway
- **Authentication**: OAuth2/OpenID Connect via Tardis/Iris
- **Authorization**: Role-based access control (RBAC)

**Deprecated Components (being removed from MTR):**
- `com-port-ra-root-application` - Replaced by vnrm-container v2.4.0
- `com-port-helper-ui` - Functionality integrated into main portal GUI

#### Platform Management

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| configserver | v1.8.0 | HA | Central configuration management using Spring Cloud Config | Git repository |
| com-cs-config-server-api | - | HA | Configuration server API (NBIM critical dependency) | configserver |
| com-rdb-resource-distribution-backend | v1.8.2 | OT | Resource distribution service | config-server |
| com-tmf-tmf639-facade-api | - | OT | TMF639 facade layer | RDM, NUM services |
| pfm-service | - | OT | Platform management service for resource coordination | config-server |

**Configuration Server Architecture:**
- **Backend**: Spring Cloud Config Server
- **Storage**: Git-based configuration repository
- **Encryption**: Symmetric/asymmetric encryption for sensitive values
- **Refresh**: Dynamic configuration refresh via Spring Cloud Bus
- **Profiles**: Environment-specific profiles (dev, test, prod)

#### Reference Data Management (RDM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| com-rdm-reference-data-management-api | - | OT | Reference data API (ONKZ, TSP, carrier) | PostgreSQL |
| com-rdm-reference-data-management-gui | - | OT | Reference data management GUI | RDM API |
| com-tsp-telephony-service-provider-api | - | HA | TSP API (HA level due to FCM integration) | PostgreSQL, RDM |
| tsp-gui | v1.9.0 | OT | Telephony service provider GUI | TSP API |

**RDM Data Categories:**
- **ONKZ (Ortsnetzkennzahl)**: German area codes (e.g., 030 for Berlin, 089 for Munich)
- **TSP (Telephony Service Provider)**: Carrier identification and D-Kennung mapping
- **Number Blocks (RNB)**: Block metadata and ownership information
- **Network Codes**: Routing and network element identifiers
- **Regulatory Data**: BNetzA compliance data

**External Integration Points:**
- **PDA Distributor**: TNB file exchange (TNB sends files with carrier information)
- **KLS**: Local area reference from DTAG fixed line network
- **BNetzA (FNA)**: Manual upload of porting IDs via GUI
- **C@T**: TNB/RNB external reference wholesale
- **Legacy RNVS**: Data synchronization until system retirement

#### Error Management

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| com-ecc-errorcode-catalog-api | - | OT | Error code catalog API | PostgreSQL |
| com-ecc-errorcode-catalog-gui | - | OT | Error catalog management GUI | ECC API |

**Error Catalog Structure:**
- **Error Domains**: NUM, PRT, COR, SPE, NTW, COM
- **Severity Levels**: CRITICAL, HIGH, MEDIUM, LOW, INFO
- **Error Codes**: Standardized 4-digit codes per domain
- **Localization**: German and English error messages
- **Actions**: Recommended resolution actions

## Detailed Microservice Implementation Specifications

### Portal Management - VNRM Container

#### Architecture Pattern: Backend for Frontend (B4F)

**Component Structure:**
```
vnrm.telekom.de
    ├── vnrm-container (Spring Boot)
    │   ├── Authentication & Authorization
    │   ├── Session Management
    │   ├── API Gateway Routing
    │   └── Security Filters
    ├── vnrm-portal-backend-for-frontend
    │   ├── Aggregation Layer (combines multiple backend APIs)
    │   ├── Data Transformation
    │   ├── Caching Layer (Redis)
    │   └── Rate Limiting
    └── vnrm-portal-gui (Angular SPA)
        ├── User Interface Components
        ├── State Management (NgRx)
        ├── Routing
        └── API Integration
```

**Authentication Flow:**
1. User accesses vnrm.telekom.de
2. Redirect to Tardis/Iris OAuth2 login
3. Authorization code exchange for JWT token
4. Token validation and session creation
5. Role-based menu and feature enablement

**Supported User Roles:**
- **VNRM_SYSA**: System administrator (full access)
- **VNRM_NUM_E**: Number management expert
- **VNRM_PRT_E**: Porting management expert
- **VNRM_COR_E**: Correction management expert
- **VNRM_SYSA_NON_PROD**: Non-production system administrator
- **LOCAL_ADMIN**: Local environment administrator

**Integration Pattern:**
- **Single Sign-On (SSO)**: Tardis/Iris integration for Telekom-wide identity
- **Token Refresh**: Automatic token refresh before expiration
- **Logout**: Centralized logout across all VNRM services
- **Audit Logging**: All user actions logged for compliance

### Platform Management - Configuration Server (CONFS)

#### Spring Cloud Config Server Implementation

**Git Repository Structure:**
```
vnrm-config-repo/
├── application.yml                    # Global defaults
├── application-dev.yml                # Development environment
├── application-test.yml               # Test environment
├── application-prod.yml               # Production environment
├── num-fcm-fixednet-callnumber-management-api.yml
├── num-nbim-number-block-inventory-management-api.yml
├── prt-fbpm-fixed-net-business-process-management-api.yml
└── com-rdm-reference-data-management-api.yml
```

**Configuration Properties:**
- **Database Connections**: JDBC URLs, credentials, pool sizes
- **Message Bus**: Message Bus broker addresses, topics, consumer groups
- **External APIs**: Endpoint URLs, timeout values, retry policies
- **Feature Flags**: Enable/disable features dynamically
- **Business Rules**: Configurable thresholds, validation rules (e.g., DUWA threshold, reservation timeout)

**Encryption Support:**
```yaml
# Encrypted values using {cipher} prefix
spring:
  datasource:
    password: '{cipher}AQA8FJ3x...'

# Symmetric encryption (default)
encrypt.key: my-secret-key

# Asymmetric encryption (recommended for production)
encrypt.key-store:
  location: classpath:config-server.jks
  password: store-password
  alias: config-server-key
  secret: key-password
```

**Dynamic Refresh:**
- **Actuator Endpoint**: POST /actuator/refresh
- **Spring Cloud Bus**: Broadcast refresh to all instances
- **Message Bus Integration**: Publish RefreshRemoteApplicationEvent
- **Client Support**: @RefreshScope annotation on beans

#### Configuration Server User Interface Workflow

**Portal Integration:**

**1. Access Control:**
- Users need specific roles (VNRM_SYSA, VNRM_NUM_E, VNRM_SYSA_NON_PROD, LOCAL_ADMIN)
- Page blocked for unauthorized users with error message
- Role validation occurs before any data loading

**2. Initialization Process:**
1. User navigates to Configuration Server page in VNRM portal
2. Backend call to retrieve available application/profile/label combinations
3. Dropdowns populated with available options
4. User ready to select configuration parameters

**3. Parameter Selection Workflow:**

**Step 1: Application Selection**
- User chooses application name from dropdown (e.g., num-fcm-fixednet-callnumber-management-api)
- Dropdown contains all microservice application names registered with config server

**Step 2: Profile Selection**
- User chooses profile for selected application (dev, test, prod)
- Profile dropdown is dependent on application selection
- Shows only valid profiles for the chosen application

**Step 3: Label Selection**
- User chooses label (typically Git branch: main, develop, release)
- Label dropdown dependent on application and profile combination
- Determines which version of configuration to retrieve

**Step 4: Parameter Retrieval**
- User clicks "Get extended parameters" button
- Backend fetches full configuration data for application/profile/label combination
- Configuration parameters displayed in editable table format

**4. Data Editing Capabilities:**

**Edit Mode Operations:**
- **Table Editing**: Double-click table cell to enter edit mode
- **Change Application**: Apply changes with Enter key
- **Validation**: Real-time validation of parameter values
- **Save**: Save applied changes to Git repository
- **Cancel**: Discard changes and return to initial state
- **Refresh**: Reload table data from config server
- **Browser Refresh**: Returns to initialization step (all selections reset)

**5. Error Handling:**

**Error Scenarios:**
- **Pre-Save Errors**: No changes applied, refresh returns initial data
- **Post-Save Errors**: Changes applied for successful fields, failed fields remain unchanged
- **Backend Errors**: No changes applied on save failure, error message displayed
- **Invalid Role**: Config service completely blocked with authorization error
- **Connection Errors**: Timeout or connectivity issues displayed to user

**6. Configuration Update Workflow:**
```
User Edit → Validation → Save to Git → Config Server Detects Change
    ↓
Config Server Publishes Refresh Event → Spring Cloud Bus (Message Bus)
    ↓
All Microservice Instances → Consume Event → Refresh @RefreshScope Beans
    ↓
Configuration Active → Services Use New Settings
```

#### Configuration API (com-cs-config-server-api)

**RESTful Endpoints:**
```
GET /{application}/{profile}[/{label}]
GET /{application}-{profile}.yml
GET /{application}-{profile}.properties
GET /{application}-{profile}.json
```

**Response Format:**
```json
{
  "name": "num-fcm-fixednet-callnumber-management-api",
  "profiles": ["prod"],
  "label": "main",
  "version": "a3f5b7c",
  "state": null,
  "propertySources": [
    {
      "name": "file:///config-repo/num-fcm-fixednet-callnumber-management-api-prod.yml",
      "source": {
        "spring.datasource.url": "jdbc:postgresql://prod-db:5432/vnrm_fcm_prod",
        "spring.datasource.username": "fcm_user",
        "vnrm.fcm.reservation.timeout.minutes": "1440",
        "vnrm.fcm.duwa.threshold": "200"
      }
    }
  ]
}
```

**Example Configuration Properties:**
```yaml
# num-fcm-fixednet-callnumber-management-api-prod.yml
spring:
  datasource:
    url: jdbc:postgresql://prod-db:5432/vnrm_fcm_prod
    username: fcm_user
    password: '{cipher}AQA8FJ3x...'
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

vnrm:
  fcm:
    reservation:
      timeout:
        minutes: 1440  # 24 hours
    duwa:
      threshold: 200  # Duration of waiting threshold in days
    validation:
      enabled: true
      strict-mode: true
```

### Reference Data Management (RDM/RDMA)

#### Business Context & Strategic Importance

RDM serves as the single source of truth for all reference data across VNRM, ensuring consistency in:
- **Number Validation**: ONKZ validation ensures callnumbers use valid German area codes
- **Carrier Operations**: TSP data enables porting between 160+ German telecommunications providers
- **Regulatory Compliance**: BNetzA data ensures compliance with Federal Network Agency requirements
- **Legacy Integration**: Synchronizes with RNVS until complete migration, preventing data divergence

**Micro User Interface (MUI) Functions:**
- **CRUD Operations**: Read, update, delete for every reference data set
- **Bulk Operations**: Single update and bulk operation capabilities
- **Data Export**: Download as XML or CSV formats for external processing
- **Data Analysis**: TSP and RNB functions include data analysis between different sources
- **Manual Upload**: BNetzA porting IDs uploaded manually via GUI

#### Database Schema (PostgreSQL)

**ONKZ (Area Code) Table:**
```sql
CREATE TABLE vnrm_rdm.onkz (
  onkz_id VARCHAR(5) PRIMARY KEY,
  onkz_name VARCHAR(100) NOT NULL,
  federal_state VARCHAR(50),
  region VARCHAR(100),
  valid_from DATE NOT NULL,
  valid_to DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT valid_dates CHECK (valid_to IS NULL OR valid_to > valid_from)
);

-- Example data
INSERT INTO vnrm_rdm.onkz VALUES
  ('030', 'Berlin', 'Berlin', 'Berlin', '1998-01-01', NULL),
  ('089', 'München', 'Bayern', 'Oberbayern', '1998-01-01', NULL),
  ('040', 'Hamburg', 'Hamburg', 'Hamburg', '1998-01-01', NULL);
```

**TSP (Telephony Service Provider) Table:**
```sql
CREATE TABLE vnrm_rdm.tsp (
  tsp_id VARCHAR(10) PRIMARY KEY,
  tsp_name VARCHAR(200) NOT NULL,
  d_kennung VARCHAR(4) UNIQUE NOT NULL,  -- D001 for DTAG
  pda_portierungskennung VARCHAR(4) UNIQUE,
  address TEXT,
  contact_email VARCHAR(100),
  contact_phone VARCHAR(20),
  active BOOLEAN DEFAULT TRUE,
  valid_from DATE NOT NULL,
  valid_to DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example data
INSERT INTO vnrm_rdm.tsp VALUES
  ('TSP001', 'Deutsche Telekom AG', 'D001', 'P001',
   'Friedrich-Ebert-Allee 140, 53113 Bonn',
   'vnrm@telekom.de', '+49-228-1810', TRUE, '1998-01-01', NULL),
  ('TSP002', 'Vodafone GmbH', 'D002', 'P002',
   'Ferdinand-Braun-Platz 1, 40549 Düsseldorf',
   'porting@vodafone.de', '+49-211-5330', TRUE, '2002-01-01', NULL);
```

**Number Block Reference Table:**
```sql
CREATE TABLE vnrm_rdm.rnb_reference (
  rnb_id VARCHAR(13) PRIMARY KEY,
  onkz VARCHAR(5) REFERENCES vnrm_rdm.onkz(onkz_id),
  block_start VARCHAR(10) NOT NULL,
  block_end VARCHAR(10) NOT NULL,
  block_size INTEGER NOT NULL,
  owner_tsp VARCHAR(10) REFERENCES vnrm_rdm.tsp(tsp_id),
  bnetza_order_id VARCHAR(20),
  status VARCHAR(20) NOT NULL,  -- FREE, USED, RESERVED, LOCKED, BNETZA
  published_date DATE,
  network_release_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### RDM API Specification

**RESTful Endpoints:**

**ONKZ Operations:**
```
GET    /api/v1/onkz                       # List all area codes
GET    /api/v1/onkz/{onkz_id}             # Get specific area code
GET    /api/v1/onkz/{onkz_id}/blocks      # Get all blocks for area code
POST   /api/v1/onkz                       # Create new area code (admin)
PUT    /api/v1/onkz/{onkz_id}             # Update area code (admin)
DELETE /api/v1/onkz/{onkz_id}             # Deactivate area code (admin)
```

**TSP Operations:**
```
GET    /api/v1/tsp                        # List all TSPs
GET    /api/v1/tsp/{tsp_id}               # Get specific TSP
GET    /api/v1/tsp/by-dkennung/{d_kennung} # Find TSP by D-Kennung
GET    /api/v1/tsp/by-pda/{pda_kennung}  # Find TSP by PDA Kennung
POST   /api/v1/tsp                        # Register new TSP (admin)
PUT    /api/v1/tsp/{tsp_id}               # Update TSP (admin)
PATCH  /api/v1/tsp/{tsp_id}/status        # Activate/deactivate TSP
```

**Number Block Reference Operations:**
```
GET    /api/v1/rnb                        # List all number blocks
GET    /api/v1/rnb/{rnb_id}               # Get specific block
GET    /api/v1/rnb/by-onkz/{onkz}         # Blocks by area code
GET    /api/v1/rnb/by-owner/{tsp_id}      # Blocks by owner
POST   /api/v1/rnb                        # Create block (admin)
PUT    /api/v1/rnb/{rnb_id}               # Update block (admin)
PATCH  /api/v1/rnb/{rnb_id}/status        # Update block status
```

**Example Request/Response:**
```bash
# Get TSP by D-Kennung
GET /api/v1/tsp/by-dkennung/D001

# Response
{
  "tsp_id": "TSP001",
  "tsp_name": "Deutsche Telekom AG",
  "d_kennung": "D001",
  "pda_portierungskennung": "P001",
  "address": "Friedrich-Ebert-Allee 140, 53113 Bonn",
  "contact_email": "vnrm@telekom.de",
  "contact_phone": "+49-228-1810",
  "active": true,
  "valid_from": "1998-01-01",
  "valid_to": null
}
```

#### Legacy RNVS Synchronization

**Synchronization Strategy:**
- **Frequency**: Nightly batch synchronization + real-time delta updates
- **Direction**: Bidirectional during transition, VNRM-primary post-migration
- **Validation**: Data consistency checks and reconciliation reports
- **Conflict Resolution**: VNRM takes precedence for conflicting updates

**RNVS Table Mapping:**

| RNVS Table | RNVS Field | VNRM Table | VNRM Field | Transformation |
|------------|------------|------------|------------|----------------|
| T_ONKZ | ONKZ_ID | vnrm_rdm.onkz | onkz_id | Direct mapping |
| T_ONKZ | ONKZ_NAME | vnrm_rdm.onkz | onkz_name | Direct mapping |
| T_TNB | TNB_DKENNUNG | vnrm_rdm.tsp | d_kennung | Direct mapping |
| T_TNB | TNB_NAME | vnrm_rdm.tsp | tsp_name | Direct mapping |
| T_RNB | RNB_RNBID | vnrm_rdm.rnb_reference | rnb_id | Direct mapping |
| T_RNB | RNB_ONRNBID | vnrm_rdm.rnb_reference | onkz | FK reference |

**Key Abbreviations:**
- **KLS**: Interface partner for terrestrial information of DTAG fixed line network
- **RNB**: Phone number range (Rufnummernblock)
- **TNB**: Fixed line network operator (Teilnehmernetzbetreiber) - equivalent to TSP
- **TSP**: Telephony service provider
- **ONKZ**: Area code identifying geographic region (Ortsnetzkennzahl)
- **RNVS**: Legacy call number management system to be retired
- **PDA**: Porting data exchange distributor for FNO data file exchange
- **FNA (BNetzA)**: Federal network agency controlling fixed line networks

### Error Management - Error Code Catalog (ECC)

#### Error Code Structure

**Standardized Format:**
```
[DOMAIN][SEVERITY][NUMBER]

Examples:
- NUM-C-0001: NUM Critical Error 0001
- PRT-H-0042: PRT High Severity Error 0042
- COM-M-0103: COM Medium Severity Error 0103
```

**Domain Codes:**
- **NUM**: Number Management errors
- **PRT**: Porting Management errors
- **COR**: Correction/Business Error Management errors
- **COM**: Common/Platform errors
- **SPE**: Special Functions errors
- **NTW**: Network errors

**Severity Levels:**
- **C (Critical)**: Service disruption, immediate action required
- **H (High)**: Major functionality impaired, urgent resolution needed
- **M (Medium)**: Partial functionality affected, scheduled resolution
- **L (Low)**: Minor issues, cosmetic defects
- **I (Info)**: Informational messages, no action required

#### Error Catalog Database Schema

```sql
CREATE TABLE vnrm_ecc.error_catalog (
  error_code VARCHAR(20) PRIMARY KEY,
  error_domain VARCHAR(10) NOT NULL,
  severity VARCHAR(1) NOT NULL CHECK (severity IN ('C', 'H', 'M', 'L', 'I')),
  error_title_de VARCHAR(200) NOT NULL,
  error_title_en VARCHAR(200) NOT NULL,
  error_description_de TEXT,
  error_description_en TEXT,
  resolution_action_de TEXT,
  resolution_action_en TEXT,
  technical_details TEXT,
  related_services VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(100),
  active BOOLEAN DEFAULT TRUE
);

-- Example error entries
INSERT INTO vnrm_ecc.error_catalog VALUES
  ('NUM-C-0001', 'NUM', 'C',
   'Rufnummer reservierung fehlgeschlagen',
   'Call number reservation failed',
   'Die Reservierung der Rufnummer ist aufgrund eines Systemfehlers fehlgeschlagen.',
   'Call number reservation failed due to a system error.',
   'Kontaktieren Sie den Support und geben Sie die Fehlerreferenz an.',
   'Contact support and provide the error reference.',
   'Database constraint violation or connection timeout',
   'num-fcm-fixednet-callnumber-management-api',
   CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'system', TRUE),

  ('PRT-H-0042', 'PRT', 'H',
   'PDA Nachricht Validierung fehlgeschlagen',
   'PDA message validation failed',
   'Die eingehende PDA-Nachricht konnte nicht validiert werden.',
   'Incoming PDA message could not be validated.',
   'Prüfen Sie das PDA-Nachrichtenformat gemäß ITEX-PDA Spezifikation.',
   'Check PDA message format according to ITEX-PDA specification.',
   'XML schema validation error or missing mandatory fields',
   'prt-fbpm-fixed-net-business-process-management-api',
   CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'system', TRUE);
```

#### Error Catalog API

**RESTful Endpoints:**
```
GET    /api/v1/errors                     # List all error codes
GET    /api/v1/errors/{error_code}        # Get specific error
GET    /api/v1/errors/by-domain/{domain}  # Errors by domain
GET    /api/v1/errors/by-severity/{sev}   # Errors by severity
POST   /api/v1/errors                     # Create new error (admin)
PUT    /api/v1/errors/{error_code}        # Update error (admin)
DELETE /api/v1/errors/{error_code}        # Deactivate error (admin)
```

**Example API Usage:**
```bash
# Get error by code
GET /api/v1/errors/NUM-C-0001

# Response
{
  "error_code": "NUM-C-0001",
  "error_domain": "NUM",
  "severity": "C",
  "error_title_de": "Rufnummer reservierung fehlgeschlagen",
  "error_title_en": "Call number reservation failed",
  "error_description_de": "Die Reservierung der Rufnummer ist aufgrund eines Systemfehlers fehlgeschlagen.",
  "error_description_en": "Call number reservation failed due to a system error.",
  "resolution_action_de": "Kontaktieren Sie den Support und geben Sie die Fehlerreferenz an.",
  "resolution_action_en": "Contact support and provide the error reference.",
  "technical_details": "Database constraint violation or connection timeout",
  "related_services": "num-fcm-fixednet-callnumber-management-api",
  "active": true
}
```

## Integration Dependencies

### Internal VNRM Dependencies

**NUM Submodule Integration:**
- **Configuration**: All NUM services require config-server access for settings
- **Reference Data**: ONKZ and TSP validation via RDM API
- **Error Management**: NUM errors mapped to error catalog
- **Portal**: NUM GUIs integrated into vnrm-container

**PRT Submodule Integration:**
- **TSP API**: Critical dependency for Fixed Callnumber Management (FCM)
- **Reference Data**: TSP and carrier data validation for porting operations
- **Error Catalog**: Porting error standardization (PDA validation, state machine errors)
- **Configuration**: PRT service configuration via config-server

**COR Submodule Integration:**
- **Error Catalog**: Primary integration for business error management
- **Configuration**: Error management service settings
- **Portal**: Error management GUI in main portal

**SPE Submodule Integration:**
- **Configuration Server**: Settings for legacy RNVS integration
- **Reference Data**: Synchronization with RNVS reference data
- **Portal**: SPE administrative interfaces

**NTW Submodule Integration:**
- **Configuration**: Network element configuration
- **Reference Data**: Network routing data
- **Error Management**: Network error reporting

### External System Dependencies

**Tardis Platform Services:**
- **Iris**: Identity and authentication management (OAuth2/OpenID Connect)
- **Stargate**: API gateway and authorization
- **Horizon**: Event streaming (Message Bus-based) for config refresh and cross-service events
- **Spacegate**: Service mesh and traffic management

**Infrastructure Services:**
- **PostgreSQL**: Primary data store for all COM services
- **Redis**: Session management and caching (multi-level cache strategy)
- **Message Bus**: Event streaming and asynchronous messaging
- **Git**: Configuration repository backend

**Monitoring & Operations:**
- **Prometheus**: Metrics collection
- **Grafana**: Operational dashboards
- **ELK Stack**: Centralized logging (Elasticsearch, Logstash, Kibana)
- **Dynatrace**: Application performance monitoring

## Technology Stack & Implementation Details

### Backend Technologies

**Spring Boot Ecosystem:**
- **Version**: Spring Boot 2.7.x / 3.0.x
- **Spring Cloud**: 2021.0.x (Jubilee) / 2022.0.x (Kilburn)
- **Spring Cloud Config**: Configuration management
- **Spring Cloud Gateway**: API gateway and routing
- **Spring Security**: Authentication and authorization
- **Spring Data JPA**: Data access layer

**Database:**
- **PostgreSQL 13+**: Primary relational database
- **Liquibase/Flyway**: Database migration and versioning
- **HikariCP**: Connection pooling
- **Query Optimization**: Indexes, partitioning, materialized views

**Messaging:**
- **Message Bus**: Event streaming via Tardis Horizon
- **Spring Message Bus**: Message Bus integration
- **Schema Registry**: Avro schema management
- **Event Sourcing**: Audit trail and event replay

### Frontend Technologies

**Portal GUI:**
- **Angular 14+**: Modern web framework
- **TypeScript**: Type-safe JavaScript
- **Angular Material**: Material Design components
- **NgRx**: State management (Redux pattern)
- **RxJS**: Reactive programming

**Build & Deploy:**
- **Node.js 16+**: JavaScript runtime
- **npm/yarn**: Package management
- **Webpack**: Module bundler
- **Docker**: Containerization

### Security Implementation

**Authentication:**
- **OAuth 2.0/OpenID Connect**: Industry-standard protocols
- **Tardis/Iris Integration**: Telekom-wide SSO
- **JWT Tokens**: Stateless authentication
- **Token Refresh**: Automatic token renewal

**Authorization:**
- **RBAC**: Role-based access control
- **Fine-grained Permissions**: Feature-level authorization
- **Resource-level Security**: Data access control
- **Audit Logging**: Complete security audit trail

**Data Protection:**
- **Encryption at Rest**: Database-level encryption
- **Encryption in Transit**: TLS 1.3 for all communication
- **Secret Management**: Encrypted configuration values using Spring Cloud Config encryption
- **GDPR Compliance**: Personal data protection

### DevOps & Deployment

**CI/CD Pipeline:**
- **GitLab CI**: Continuous integration
- **Automated Testing**: Unit, integration, E2E tests
- **Code Quality**: SonarQube analysis
- **Security Scanning**: Dependency and vulnerability scanning

**Containerization:**
- **Docker**: Container runtime
- **Kubernetes**: Container orchestration
- **Helm Charts**: Kubernetes deployment templates
- **ArgoCD**: GitOps-based deployment

**Monitoring:**
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and alerting
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation and analysis

## Advanced Integration Patterns

### Configuration Distribution Pattern

**Workflow:**
```
1. Configuration Change:
   Developer → Git Commit → Config Repository

2. Detection:
   Config Server → Polls Git → Detects Change

3. Distribution:
   Config Server → Spring Cloud Bus → Message Bus Topic

4. Refresh:
   All Services → Consume Event → Refresh @RefreshScope Beans

5. Validation:
   Each Service → Validate Config → Log Status
```

**Implementation:**
```java
// Microservice configuration client
@RefreshScope
@ConfigurationProperties(prefix = "vnrm.fcm")
public class FcmProperties {
    private Duration reservationTimeout = Duration.ofMinutes(1440);
    private int duwaThreshold = 200;

    // Getters and setters
}

// Configuration refresh endpoint
@RestController
public class ConfigRefreshController {

    @Autowired
    private RefreshEndpoint refreshEndpoint;

    @PostMapping("/refresh")
    public Collection<String> refresh() {
        return refreshEndpoint.refresh();
    }
}
```

### Cross-Domain Service Orchestration

**Configuration Distribution Architecture:**

**Centralized Configuration Benefits:**
- **Single Source of Truth**: All VNRM microservice settings in one Git repository
- **Version Control**: Complete configuration history and rollback capability
- **Environment Management**: Different configuration sets for DEV, TEST, PROD
- **Validation**: Configuration validation before distribution prevents service failures
- **Audit Trail**: Track who changed what configuration when

**Dynamic Configuration Updates:**
```
1. Operations Team Updates Config:
   GitLab → Commit Config Change → Push to Repository

2. Config Server Detects Change:
   Polls Git Repository → Detects New Commit → Loads Updated Config

3. Broadcast to All Services:
   Config Server → Publish RefreshRemoteApplicationEvent → Message Bus Topic

4. Services Refresh Configuration:
   Each Service Instance → Consumes Message Bus Event → Refresh @RefreshScope Beans

5. Validation & Monitoring:
   Services Log Refresh Status → Prometheus Metrics → Grafana Alerts
```

**Implementation Best Practices:**
- Use `@RefreshScope` only for configuration beans, not stateful services
- Implement circuit breakers for config server unavailability
- Cache last known good configuration locally as fallback
- Monitor refresh success rates via Prometheus metrics
- Alert on configuration refresh failures

### Reference Data Caching Pattern

**Multi-Level Cache Strategy:**
```
Level 1: Application Cache (Caffeine/Guava)
  ↓ (Cache Miss)
Level 2: Distributed Cache (Redis)
  ↓ (Cache Miss)
Level 3: Database (PostgreSQL)
```

**Implementation:**
```java
@Service
public class OnkzService {

    @Cacheable(value = "onkz", key = "#onkzId")
    public Onkz getOnkz(String onkzId) {
        return onkzRepository.findById(onkzId)
            .orElseThrow(() -> new OnkzNotFoundException(onkzId));
    }

    @CacheEvict(value = "onkz", key = "#onkz.onkzId")
    public Onkz updateOnkz(Onkz onkz) {
        return onkzRepository.save(onkz);
    }
}
```

**Cache Configuration:**
```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000  # 1 hour
      cache-null-values: false
  redis:
    host: redis-cluster.vnrm.svc.cluster.local
    port: 6379
    password: ${REDIS_PASSWORD}
    cluster:
      nodes:
        - redis-1:6379
        - redis-2:6379
        - redis-3:6379
```

### Error Propagation Pattern

**Standardized Error Response:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "path": "/api/v1/callnumbers/030123456789",
  "status": 500,
  "error": "Internal Server Error",
  "errorCode": "NUM-C-0001",
  "message": "Call number reservation failed",
  "details": {
    "callnumber": "030123456789",
    "onkz": "030",
    "operation": "RESERVE"
  },
  "correlationId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "supportReference": "SR-2024-0115-001"
}
```

**Implementation:**
```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @Autowired
    private ErrorCatalogService errorCatalogService;

    @ExceptionHandler(CallnumberReservationException.class)
    public ResponseEntity<ErrorResponse> handleReservationError(
            CallnumberReservationException ex,
            HttpServletRequest request) {

        ErrorCatalogEntry errorEntry = errorCatalogService
            .getError("NUM-C-0001");

        ErrorResponse response = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .path(request.getRequestURI())
            .status(500)
            .error("Internal Server Error")
            .errorCode(errorEntry.getErrorCode())
            .message(errorEntry.getErrorTitleEn())
            .correlationId(UUID.randomUUID().toString())
            .supportReference(generateSupportReference())
            .build();

        return ResponseEntity.status(500).body(response);
    }
}
```

### TMF639 Resource Inventory Management Compliance

**TMF639 Resource Model:**
```json
{
  "id": "RES-030-12345678-001",
  "href": "/api/v1/resources/RES-030-12345678-001",
  "category": "CallNumber",
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
  ],
  "resourceRelationship": [
    {
      "relationshipType": "belongsTo",
      "resource": {
        "id": "BLOCK-030-123-001",
        "name": "Berlin Number Block 030-123"
      }
    }
  ]
}
```

**TMF639 API Endpoints:**
```
GET    /tmf-api/resourceInventoryManagement/v4/resource
GET    /tmf-api/resourceInventoryManagement/v4/resource/{id}
POST   /tmf-api/resourceInventoryManagement/v4/resource
PATCH  /tmf-api/resourceInventoryManagement/v4/resource/{id}
DELETE /tmf-api/resourceInventoryManagement/v4/resource/{id}
```

**Strategic Importance:**
- **Standard API Compliance**: Telecommunications Management Forum standard adherence
- **Resource Inventory**: Standardized resource management across VNRM ecosystem
- **Interoperability**: Industry-standard integration patterns for external systems
- **Partner Integration**: Enables third-party systems to integrate with VNRM using standard APIs

### Legacy System Integration Bridge

**RNVS Synchronization Strategy:**

**Bidirectional Sync Pattern:**
- **VNRM → RNVS**: Push reference data changes to legacy system
- **RNVS → VNRM**: Import legacy data for validation and comparison
- **Conflict Resolution**: VNRM takes precedence for conflicting updates
- **Migration Support**: Gradual migration with data consistency validation

**Synchronization Workflow:**
```
1. Reference Data Change in VNRM:
   RDM API → Database Update → Trigger Sync Event

2. Legacy Sync Service:
   Consume Event → Transform Data → Call RNVS API

3. Validation:
   Compare VNRM Data ↔ RNVS Data → Log Discrepancies

4. Reconciliation:
   Daily Batch Job → Compare All Records → Generate Report
```

**Fallback Strategy:**
- RNVS can operate independently during VNRM maintenance
- Local cache of critical reference data in each system
- Manual reconciliation process for edge cases
- Data format translation between modern and legacy formats

## Best Practices

### Configuration Management
1. **Externalize all environment-specific values** - Never hardcode in application
2. **Use encryption for sensitive data** - Passwords, API keys, certificates
3. **Version control all configuration** - Git history for audit and rollback
4. **Test configuration changes in non-prod first** - Validate before production
5. **Monitor configuration refresh success** - Alert on failed updates

### Reference Data Management
1. **Maintain data quality** - Regular validation and cleanup
2. **Synchronize with legacy RNVS** - Until complete migration
3. **Cache frequently accessed data** - Improve performance with multi-level caching
4. **Version reference data changes** - Track historical changes
5. **Validate against external sources** - BNetzA, carrier databases

### Error Management
1. **Use standardized error codes** - Consistent error handling across all services
2. **Provide actionable error messages** - Help users resolve issues
3. **Log all errors with context** - Enable debugging and analysis
4. **Monitor error rates** - Detect trends and anomalies
5. **Localize error messages** - German and English support

### Portal Management
1. **Implement responsive design** - Support various screen sizes
2. **Optimize performance** - Lazy loading, code splitting
3. **Ensure accessibility** - WCAG 2.1 compliance
4. **Monitor user experience** - Performance metrics, error tracking
5. **Regular security updates** - Patch vulnerabilities promptly

### Service Level Management
1. **Document HA requirements clearly** - Ensure 24/7 support for critical services
2. **Regular SLA review** - Re-evaluate as business needs change (e.g., RDM for porting go-live)
3. **Dependency mapping** - Understand cascade effects of service failures
4. **Circuit breakers** - Implement fallback patterns for critical dependencies
5. **Health checks** - Comprehensive monitoring of all COM services

---

**See also:**
- [NUM Architecture Reference](../vnrm-num-architecture/REFERENCE.md)
- [PRT Architecture Reference](../vnrm-prt-architecture/REFERENCE.md)
- [COR Architecture Reference](../vnrm-cor-architecture/REFERENCE.md)
- [SPE Architecture Reference](../vnrm-spe-architecture/REFERENCE.md)
- [NTW Architecture Reference](../vnrm-ntw-architecture/REFERENCE.md)
