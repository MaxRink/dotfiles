---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-num-architecture
description: VNRM NUM (Number Management) submodule architecture reference covering telephone number resource management, number blocks, callnumber inventory, and number portability integration. This skill should be used when designing or implementing NUM microservices in phases 6-12 of the RNVS→VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-num-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM NUM Architecture Expert Skill

## Purpose

Provides comprehensive architecture knowledge for the **VNRM NUM (NUMBER MANAGEMENT)** submodule, which manages telephone number resources including callnumber inventory, number block allocation, DUWA (Duration of Waiting) management, and integration with porting systems.
## NUM Submodule Overview

The NUM (NUMBERMANAGEMENT) submodule handles telephone number resource management through specific microservices documented in VNRM releases:

### TMF Resource Management
- **num-cnrm-callnumber-resource-mngmt-api** - TMF639 compliant call number resource management API (HA level) - Core TMF resource management service

### Call Number Porting Information
- **num-cpin-callnumber-porting-info-backend** - Backend service for porting information (HA level)
- **num-cpin-callnumber-porting-info-gui** - GUI for porting information display
- Provides porting status and history for NUM and NZK (Network Control Center)

### Callnumber Contingent Information
- **num-caci-callnumber-contingent-info-api** - API for contingent information (HA level)
- **num-caci-callnuber-contingent-info-gui** - GUI for contingent management
- Manages call number contingents and allocation tracking

### NBOM - Numberblock Order Management
- **num-nbom-numberblock-order-management-api** - Number block order management API (OT level)
- **num-nbom-numberblock-order-management-gui** - GUI for block order management
- Handles requests to BNetzA for new number blocks

### NBIM - Numberblock Inventory Management
- **num-nbmi-number-block-inventory-management-api** - Block inventory API (HA level)
- Manages number block inventory and utilization tracking

### Fixed Callnumber Management (FCNM)
- **num-fcm-fixednet-callnumber-management-api** - Fixed net callnumber management API (HA level)
- Manages individual and range callnumbers for fixed-line services

## Service Deployment Status (VNRM 1.9.0)

### Current Production Services
Based on the SLA documentation and deployment releases:

**High Availability (HA) Services - 24/7 Support:**
- `num-cnrm-callnumber-resource-mngmt-api` - Critical for TMF resource management
- `num-cpin-callnumber-porting-info-backend/gui` - Essential porting information
- `num-caci-callnumber-contingent-info-api/gui` - Call number contingent tracking
- `num-nbmi-number-block-inventory-management-api` - Block inventory management
- `num-fcm-fixednet-callnumber-management-api` - Fixed callnumber operations

**Office Time (OT) Services - Business Hours Support:**
- `num-nbom-numberblock-order-management-api/gui` - Block ordering from BNetzA

### Service Versioning (VNRM 1.9.0)
- `callnumber-porting-info-backend`: v1.9.1
- `callnumber-porting-info-gui`: v1.9.2
- `callnumber-contingent-info-backend`: v1.9.1
- `callnumber-contingent-info-gui`: v1.8.4
- `nbm-order-inventory-backend`: v2.3.1
- `nbm-order-inventory-gui`: v1.9.2
- `fixed-net-callnumber-management-backend`: v1.6.1
- `nbm-inventory-service`: v1.10.0

## Functional Capabilities

### TMF Resource Management
- Implements TMF639 Resource Inventory Management standard
- Provides standardized telecommunications API interface
- Manages call number resources with TMF compliance

### Number Block Operations
- **NBOM (Numberblock Order Management)**: Handles BNetzA block requests
- **NBIM (Numberblock Inventory Management)**: Tracks block utilization and availability
- Integration with federal network agency for new block allocation

### Call Number Services
- **FCNM (Fixed Callnumber Management)**: Individual number operations
- **Porting Information**: Real-time porting status and history
- **Contingent Management**: Number allocation tracking and limits

## Integration Dependencies

### Internal VNRM Dependencies
- **COM**: Uses RDM for reference data and configuration via config-server API
- **PRT**: Provides porting information through CPIN services
- **COR**: Integrates with business error management for issue resolution
- **SPE**: Connects to legacy RNVS data through database services

### External System Integration
- **BNetzA**: Direct integration for number block requests through NBOM
- **Network Control Center (NZK)**: Porting information display and monitoring
- **FCM Integration**: Fixed callnumber management for carrier operations

## Technical Architecture

### Service Communication Patterns
- RESTful APIs for all num- prefixed services
- TMF639 standard compliance for resource management
- Database-per-service for data isolation
- Event-driven notifications for status changes

### Data Management
Based on the solution documentation (SD) pages:

## Detailed Microservice Implementation Specifications

### FCNM - Fixed Callnumber Management (Detailed Implementation)

#### Database Architecture (PostgreSQL Migration from RNVS Oracle)
**Primary Tables:**

**Callnumber Table (vnrm_fcm_dev.callnumber):**
```sql
CREATE TABLE vnrm_fcm_dev.callnumber (
  "local_area_code_callnumber" VARCHAR(20) NOT NULL,
  "callnumber" VARCHAR(15) NOT NULL,
  "callnumber_end" VARCHAR(15) NOT NULL,
  "local_area_code_callnumber_end" VARCHAR(20) NOT NULL,
  "local_area_code" VARCHAR(5) NOT NULL,
  "external_pda_porting_id" VARCHAR(1) NOT NULL,
  "callnumber_type" VARCHAR(1) NOT NULL,
  "callnumberstate" VARCHAR(1) NOT NULL,
  "callnumber_block_code" VARCHAR(1) NOT NULL,
  "callnumber_block_id" VARCHAR(13) NOT NULL,
  "block_length" integer NOT NULL,
  "contingent_id" integer NOT NULL,
  "contingent_main_callnumber" VARCHAR(20),
  "booking_id_vnrm" integer,
  "booking_type" VARCHAR(1) NOT NULL,
  "number_state_model" VARCHAR(16) NOT NULL,
  "reuse_sign" VARCHAR(1) NOT NULL,
  "valid_from" timestamp(6) NOT NULL,
  "valid_to" timestamp(6) NOT NULL,
  "latest_modification_uuid" uuid NOT NULL,
  CONSTRAINT callnumber_pkey PRIMARY KEY (local_area_code_callnumber)
);
```

**Callnumber Modification Table:**
```sql
CREATE TABLE vnrm_fcm_dev.callnumber_modification (
  "modification_uuid" uuid NOT NULL,
  "local_area_code_callnumber" VARCHAR(20) NOT NULL,
  "x_business_correlation_id" VARCHAR(255) NOT NULL,
  "reuse_comment" VARCHAR(255) NOT NULL,
  "update" timestamp(6) NOT NULL,
  "user" VARCHAR(60) NOT NULL,
  "change_reason" integer NOT NULL,
  "comment" VARCHAR(255) NOT NULL,
  "external_booking_reference" VARCHAR(40),
  CONSTRAINT callnumber_modification_pkey PRIMARY KEY (modification_uuid)
);
```

#### Data Model Migration (RNVS to VNRM)
**Field Mapping from Legacy RNVS:**

| RNVS Field | VNRM Field | Description |
|------------|------------|-------------|
| TR_BUCHUNGSKZ | booking_type | Booking status code |
| TR_RUFNR | callnumber | Phone number |
| TR_ONKZ | local_area_code | Area code (ONKZ) |
| TR_SPERRE | callnumberstate | Number blocking status |
| TR_GUELTIG_VON | valid_from | Validity start date |
| TR_GUELTIG_BIS | valid_to | Validity end date |

#### State Model Implementation
**Callnumber State Machine:**

| State | German | Definition | Business Logic |
|-------|--------|------------|----------------|
| AVAILABLE | frei | Number can be booked/reserved, not in telephony network | Ready for allocation |
| RESERVED | reserviert | Reserved with time limit (24h for single, variable for DuWa >200) | Temporary allocation |
| BLOCKED | blockiert/Fehler | Manual block or system error state | Error analysis required |
| WAITING | warten | Terminated with reuse deadline, aftercare process | Reuse waiting period |
| PROCESSING | in Verarbeitung | Porting without TSP change, no time limit | Internal porting |
| ACTIVATED | gebucht/vergeben | Connected to customer, active in network | Live service |
| BNETZA | BNETZA | Cannot be used by carriers, BNETZA ownership | Regulatory control |

#### Area Processing State Model
**Number Block State Management:**

| State | German | Description | Business Logic |
|-------|--------|-------------|----------------|
| BLOCKED | gesperrt | Block not to be used, restructuring planned | Manual intervention |
| CLOSED | geschlossen | Returns to BNETZA | Block retirement |
| CLOSE_REQ | Rückgabeanforderung | Return request to BNETZA | Preparation for return |
| WAITING | warten | Can be used when manually/automatically released | Pending activation |
| ALL | alles | Single and range number booking allowed | Full operation |
| SINGLE | Einzelrufnummer | Only single number booking, limited by count_free_numbers | Limited operation |
| TEC | technisch | Technical single number booking allowed | Technical numbers |
| FULL | ausgebucht | Block fully allocated, no more numbers available | Capacity reached |

#### Callnumber Types Management
**Type Classifications:**
- **Single Callnumber**: Individual numbers for DTAG network
- **Range Callnumber Normal**: ≤200 numbers in sequence
- **Range Callnumber Big**: >200 numbers in ascending sequence
- **Old Stock Callnumber**: Numbers with unwanted arity
- **Technical Callnumber (032)**: Technical numbers in 032 range

### NBIM - Number Block Inventory Management (Detailed Implementation)

#### Business Data Model
**Core Tables:**

**Number Block Management:**
- **Block ID**: BNetzA identification number
- **ONKZ**: Area code (Ortsnetzkennzahl)
- **Block Owner**: TSP ID (D-Kennung) for carrier identification
- **Block State**: Usage status (free, used, reserved, locked, BNETZA)
- **Block Size**: Count of phone numbers in block
- **Publication Date**: PDA process publishing date
- **Network Release Date**: Real network activation date

#### State Model Implementation
**Block States with Business Logic:**

| State | German | Definition | Detection Logic |
|-------|--------|------------|-----------------|
| FREE | frei | Ready for DTAG use, load capacity = 0 | legal_owner = D001, capacity = 0 |
| USED | belegt | Contains activated/deactivated numbers | legal_owner ≠ D001 OR capacity > 0 |
| RESERVED | reserviert | Bound to specific customer order | VNRM logic only |
| LOCKED | gesperrt | Not for use, return to BNETZA when empty | statusV14 = 400 OR manual |
| BNETZA | BNETZA | No user or BNETZA ownership | legal_owner = BNETZA |

#### Migration Mapping
**Field Mapping from RNVS:**

| VNRM GUI | VNRM DB | RNVS Table | RNVS Field | Description |
|----------|---------|------------|------------|-------------|
| ONKZ | ndc | T_RNB | RNB_ONRNBID | Area code |
| RNB ID | block_id | T_RNB | RNB_RNBID | Block identifier |
| BNetzA ID | reg_order_id | T_RNB | RNB_REGAUFTRAGSNR | Registry order number |
| Altbestand | oldstock_sign | T_RNB | RNB_STATUSV14 | Legacy status flag |
| RNB Besitzer | block_Owner_new | T_RNB | - | Block owner (TSP) |
| Veröffentlichungsdatum | processReleaseDate | T_RNB | RNB_VEROEFFENTLICHT | Publication date |
| Netzwirksamkeit | networkReleaseDate | T_RNB | RNB_NETZWIRKSAM | Network activation |

### NBOM - Number Block Order Management (Detailed Implementation)

#### Business Process Integration
**BNetzA Integration Workflow:**
1. **Resource Planning**: Automated analysis of capacity needs
2. **Order Generation**: System-generated requests to BNetzA
3. **Order Tracking**: Status monitoring of block allocation requests
4. **Order Fulfillment**: Integration with NBIM for inventory updates

#### Order Management Lifecycle
- **Order Creation**: Automatic trigger based on capacity thresholds
- **BNetzA Submission**: Formal request transmission to federal agency
- **Response Processing**: Handling BNetzA allocation responses
- **Inventory Integration**: Update NBIM with new block assignments

### CPIN - Callnumber Porting Information (Detailed Implementation)

#### Porting Information Display System
**Display Capabilities:**
- **Current Porting Status**: Real-time status of ongoing porting operations
- **Historical Porting Data**: Complete porting history for numbers
- **Process Timeline**: Detailed workflow progress tracking
- **Cross-System Integration**: Data from NUM and NZK systems

#### User Access Patterns
**Target Users:**
- **NUM Operations**: Number management personnel for porting oversight
- **NZK (Network Control Center)**: Network operations monitoring
- **Customer Service**: Support for porting-related inquiries
- **Business Analysis**: Porting statistics and performance metrics

## Advanced Technical Implementation

### Database Design Patterns
**PostgreSQL Optimization:**
- **Partitioning**: Time-based partitioning for call number history
- **Indexing**: Optimized indexes for ONKZ and block ID lookups
- **Constraints**: Data integrity enforcement for state transitions
- **Audit Trails**: Complete modification tracking with UUIDs

### API Design Patterns
**RESTful API Standards:**
- **Resource-Based URLs**: `/api/v1/callnumbers/{callnumberId}`
- **HTTP Method Mapping**: GET, POST, PUT, PATCH, DELETE operations
- **Status Codes**: Standard HTTP response codes for all operations
- **Pagination**: Cursor-based pagination for large datasets
- **Filtering**: Query parameter filtering for complex searches

### Event-Driven Architecture
**Message Bus Integration:**
- **State Change Events**: Publish callnumber state transitions
- **Porting Events**: Real-time porting status updates
- **Block Events**: Number block allocation and utilization changes
- **Error Events**: Integration with COR for error management

### Performance Optimization
**Scalability Patterns:**
- **Read Replicas**: Database read scaling for reporting queries
- **Caching**: Redis caching for frequently accessed reference data
- **Async Processing**: Background processing for bulk operations
- **Circuit Breakers**: Resilience patterns for external service calls

Use this detailed implementation knowledge to design robust NUM microservices that maintain data consistency, provide real-time porting capabilities, and ensure seamless integration with telecommunications standards while supporting the complex state management requirements of German number portability regulations.
- **FCNM**: Manages individual callnumbers and ranges with status tracking
- **NBIM**: Inventory tracking with order_id references to NBOM
- **NBOM**: Order management for BNetzA block requests
- **TMF CNRM**: Resource inventory following TMF639 standards

## Service Level Requirements

### Support Classification
- **HA Services**: 3-hour response time, 24/7 support, on-call duty required
- **OT Services**: 3-day response time, business hours only, no on-call duty
- **Support Channels**: Hotline, ServiceNow, FMB post box

### Platform Dependencies
- Configuration server (com-cs-config-server-api) critical for all NUM services
- Reference data management (RDM) for validation and business rules
- Error management integration for fault handling

Use this expertise to guide NUM microservice architecture decisions, focusing on the actual deployed services, their real SLA requirements, and documented dependencies within the VNRM ecosystem as specified in the Confluence wiki.
