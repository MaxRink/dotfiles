# VNRM NUM (NUMBERMANAGEMENT) Architecture Reference

## Overview

The VNRM NUM (NUMBERMANAGEMENT) submodule handles telephone number resource management through specialized microservices for callnumber lifecycle operations, number block inventory, porting information display, and TMF639-compliant resource management. NUM serves as the central authority for all number-related operations within VNRM, managing everything from individual callnumber allocations to large-scale number block inventory across Germany's telecommunications network.

NUM implements complex state machines for both individual callnumbers and number blocks, ensuring compliance with German telecommunications regulations (BNetzA) and supporting seamless integration with number porting operations (PRT), network routing (NTW), and legacy RNVS systems (SPE).

## Service Level Architecture

### Service Level Classification

**High Availability (HA) Services - 24/7 Support:**
- **Response Time**: 3 hours
- **Availability**: 24/7 on-call duty required
- **Support Channels**: Hotline + ServiceNow + FMB post box
- **Critical Impact**: Service outages affect number allocation and porting operations
- **Business Justification**: Number management is core to telecommunications operations - any downtime prevents new customer activations, porting operations, and revenue-generating activities

**Office Time (OT) Services - Business Hours Support:**
- **Response Time**: 3 days
- **Availability**: Business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Impact**: Limited to administrative and reporting functions
- **Business Justification**: BNetzA ordering and reporting operations are not time-critical and can wait for business hours

## Deployed Microservices

### Production Services (VNRM 1.9.0+)

#### Fixed Callnumber Management (FCM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-fcm-fixednet-callnumber-management-api | v1.6.1 | HA | Individual and range callnumber lifecycle | COM config-server, RDM |
| fixed-net-callnumber-management-backend | v1.6.1 | HA | Backend implementation | PostgreSQL, Message Bus |

**Technology Stack:**
- **Backend**: Spring Boot 2.7.x, Spring Data JPA
- **Database**: PostgreSQL 13+ with HikariCP connection pooling
- **Messaging**: Message Bus via Tardis Horizon
- **API**: RESTful with OpenAPI 3.0 specification

**Core Capabilities:**
- Individual callnumber reservation and activation
- Range callnumber management (normal ≤200, big >200)
- State machine implementation (7 states)
- DuWa (Duration of Waiting) threshold management
- Integration with PRT for porting operations

#### Number Block Inventory Management (NBIM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-nbim-number-block-inventory-management-api | v1.10.0 | HA | Block inventory and utilization tracking | COM config-server, RDM |
| nbm-inventory-service | v1.10.0 | HA | Inventory service implementation | PostgreSQL, BNetzA |

**Critical Dependencies:**
- **BNetzA Integration**: Block allocation validation and ownership verification
- **COM Config-Server**: Essential for service configuration (single point of failure)
- **COM RDM**: ONKZ and TSP reference data validation

**Core Capabilities:**
- Number block state management (5 states)
- Area processing state management (8 states)
- Capacity utilization tracking
- Block ownership management (D-Kennung mapping)
- Integration with NBOM for block ordering

#### Number Block Order Management (NBOM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-nbom-numberblock-order-management-api | v2.3.1 | OT | BNetzA block ordering requests | COM config-server, NBIM |
| num-nbom-numberblock-order-management-gui | v1.9.2 | OT | Order management GUI | NBOM API |
| nbm-order-inventory-backend | v2.3.1 | OT | Backend implementation | PostgreSQL |

**Business Process:**
- Automated capacity threshold monitoring
- Block order request generation
- BNetzA submission and tracking
- Order fulfillment integration with NBIM
- Response processing and inventory updates

**Integration Points:**
- **BNetzA Portal**: Electronic submission of block requests
- **NBIM**: Capacity monitoring and block import
- **FCM**: Number availability updates

#### Callnumber Porting Information (CPIN)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-cpin-callnumber-porting-info-backend | v1.9.1 | HA | Porting status backend | PRT services, PostgreSQL |
| num-cpin-callnumber-porting-info-gui | v1.9.2 | HA | Porting information GUI | CPIN backend |
| callnumber-porting-info-backend | v1.9.1 | HA | Backend implementation | Message Bus, PostgreSQL |

**Target Users:**
- **NUM operations personnel**: Porting oversight and management
- **NZK (Network Control Center)**: Network operations monitoring
- **Customer service representatives**: Porting inquiry support
- **Business analysts**: Performance metrics and reporting

**Display Capabilities:**
- Real-time porting status tracking
- Complete historical porting data
- Detailed process timeline visualization
- Cross-system data integration (NUM + NZK)

#### Callnumber Contingent Information (CACI)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-caci-callnumber-contingent-info-api | v1.9.1 | HA | Contingent management | COM config-server |
| num-caci-callnuber-contingent-info-gui | v1.8.4 | HA | Contingent GUI | CACI API |
| callnumber-contingent-info-backend | v1.9.1 | HA | Backend implementation | PostgreSQL |

**Contingent Management:**
- Number allocation tracking per customer/contract
- Quota enforcement and monitoring
- Utilization reporting and analytics
- Integration with FCM for allocation limits

#### TMF Resource Management (CNRM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| num-cnrm-callnumber-resource-mngmt-api | - | HA | TMF639 compliant resource API | All NUM services |

**TMF639 Compliance:**
- Industry-standard resource inventory management (TMF639 standard)
- Standard telecommunications API interface for interoperability
- Resource lifecycle management (create, read, update, delete)
- Integration with external systems using TMF standards

## Detailed Microservice Implementation Specifications

### FCNM - Fixed Callnumber Management

#### Database Architecture (PostgreSQL)

**Migration from RNVS Oracle:**
FCNM database represents a complete migration from legacy RNVS Oracle database to modern PostgreSQL, with field name standardization, improved constraints, and audit trail enhancements.

**Callnumber Table:**
```sql
CREATE TABLE vnrm_fcm_dev.callnumber (
  local_area_code_callnumber VARCHAR(20) NOT NULL,
  callnumber VARCHAR(15) NOT NULL,
  callnumber_end VARCHAR(15) NOT NULL,
  local_area_code_callnumber_end VARCHAR(20) NOT NULL,
  local_area_code VARCHAR(5) NOT NULL,
  external_pda_porting_id VARCHAR(1) NOT NULL,
  callnumber_type VARCHAR(1) NOT NULL,
  callnumberstate VARCHAR(1) NOT NULL,
  callnumber_block_code VARCHAR(1) NOT NULL,
  callnumber_block_id VARCHAR(13) NOT NULL,
  block_length INTEGER NOT NULL,
  contingent_id INTEGER NOT NULL,
  contingent_main_callnumber VARCHAR(20),
  booking_id_vnrm INTEGER,
  booking_type VARCHAR(1) NOT NULL,
  number_state_model VARCHAR(16) NOT NULL,
  reuse_sign VARCHAR(1) NOT NULL,
  valid_from TIMESTAMP(6) NOT NULL,
  valid_to TIMESTAMP(6) NOT NULL,
  latest_modification_uuid UUID NOT NULL,
  CONSTRAINT callnumber_pkey PRIMARY KEY (local_area_code_callnumber),
  CONSTRAINT fk_callnumber_block FOREIGN KEY (callnumber_block_id)
    REFERENCES vnrm_fcm_dev.number_block(block_id),
  CONSTRAINT fk_contingent FOREIGN KEY (contingent_id)
    REFERENCES vnrm_caci.contingent(contingent_id)
);

-- Performance indexes
CREATE INDEX idx_callnumber_onkz ON vnrm_fcm_dev.callnumber(local_area_code);
CREATE INDEX idx_callnumber_state ON vnrm_fcm_dev.callnumber(callnumberstate);
CREATE INDEX idx_callnumber_block ON vnrm_fcm_dev.callnumber(callnumber_block_id);
CREATE INDEX idx_callnumber_booking ON vnrm_fcm_dev.callnumber(booking_id_vnrm);
CREATE INDEX idx_callnumber_type ON vnrm_fcm_dev.callnumber(callnumber_type);
CREATE INDEX idx_callnumber_valid ON vnrm_fcm_dev.callnumber(valid_from, valid_to);
```

**Callnumber Modification Table (Audit Trail):**
```sql
CREATE TABLE vnrm_fcm_dev.callnumber_modification (
  modification_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  local_area_code_callnumber VARCHAR(20) NOT NULL,
  x_business_correlation_id VARCHAR(255) NOT NULL,
  reuse_comment VARCHAR(255) NOT NULL,
  update TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "user" VARCHAR(60) NOT NULL,
  change_reason INTEGER NOT NULL,
  comment VARCHAR(255) NOT NULL,
  external_booking_reference VARCHAR(40),
  previous_state VARCHAR(1),
  new_state VARCHAR(1),
  CONSTRAINT fk_callnumber FOREIGN KEY (local_area_code_callnumber)
    REFERENCES vnrm_fcm_dev.callnumber(local_area_code_callnumber)
);

-- Audit indexes
CREATE INDEX idx_modification_callnumber ON vnrm_fcm_dev.callnumber_modification(local_area_code_callnumber);
CREATE INDEX idx_modification_timestamp ON vnrm_fcm_dev.callnumber_modification(update DESC);
CREATE INDEX idx_modification_user ON vnrm_fcm_dev.callnumber_modification("user");
CREATE INDEX idx_modification_correlation ON vnrm_fcm_dev.callnumber_modification(x_business_correlation_id);
```

#### Data Model Migration (RNVS to VNRM)

**Field Mapping:**

| RNVS Field | RNVS Table | VNRM Field | VNRM Table | Transformation |
|------------|------------|------------|------------|----------------|
| TR_RUFNR | T_RUFNR | callnumber | callnumber | Direct mapping |
| TR_ONKZ | T_RUFNR | local_area_code | callnumber | Direct mapping |
| TR_BUCHUNGSKZ | T_RUFNR | booking_type | callnumber | Code mapping (A/B/C) |
| TR_SPERRE | T_RUFNR | callnumberstate | callnumber | State mapping (see state model) |
| TR_GUELTIG_VON | T_RUFNR | valid_from | callnumber | Oracle DATE → PostgreSQL TIMESTAMP |
| TR_GUELTIG_BIS | T_RUFNR | valid_to | callnumber | Oracle DATE → PostgreSQL TIMESTAMP |
| TR_RNBID | T_RUFNR | callnumber_block_id | callnumber | Direct mapping (VARCHAR) |
| TR_KONTINGENT_ID | T_RUFNR | contingent_id | callnumber | Direct mapping (INTEGER) |

**Migration Challenges:**
- **Timestamp Precision**: Oracle DATE vs PostgreSQL TIMESTAMP(6) - requires precision handling
- **Character Encoding**: UTF-8 migration for German characters (ä, ö, ü, ß)
- **State Code Mapping**: RNVS used numeric codes, VNRM uses VARCHAR(1) codes
- **Constraint Migration**: Foreign key relationships rebuilt with proper cascading

#### Callnumber State Model Implementation

**State Machine (7 States):**

| State | German | Code | Definition | Business Logic | Timeout |
|-------|--------|------|------------|----------------|---------|
| AVAILABLE | frei | A | Number can be booked/reserved | Not in telephony network, ready for allocation | - |
| RESERVED | reserviert | R | Reserved with time limit | 24h for single, variable for DuWa >200 | 24h / variable |
| BLOCKED | blockiert/Fehler | B | Manual block or system error | Error analysis required, manual intervention | Manual release |
| WAITING | warten | W | Terminated with reuse deadline | Aftercare process, reuse waiting period | Variable |
| PROCESSING | in Verarbeitung | P | Porting without TSP change | No time limit, internal porting | - |
| ACTIVATED | gebucht/vergeben | V | Connected to customer | Active in network, live service | - |
| BNETZA | BNETZA | Z | Cannot be used by carriers | BNetzA ownership, regulatory control | - |

**State Transition Rules:**
```
AVAILABLE → RESERVED:
  - Trigger: Customer reserves number
  - Validation: ONKZ exists, number not in use
  - Timeout: 24h (single), variable (range >200)

RESERVED → ACTIVATED:
  - Trigger: Customer confirms and activates
  - Action: Network routing configured
  - Integration: NTW routing update

RESERVED → AVAILABLE:
  - Trigger: Reservation timeout expires
  - Action: Automatic state rollback
  - Notification: None (silent expiration)

ACTIVATED → WAITING:
  - Trigger: Customer terminates service
  - Action: Reuse period starts
  - Business Rule: Number enters aftercare

WAITING → AVAILABLE:
  - Trigger: Reuse period expires
  - Validation: No customer complaints
  - Action: Number available for new allocation

ACTIVATED → PROCESSING:
  - Trigger: Internal porting starts
  - Condition: TSP remains same
  - Note: No timeout limit

PROCESSING → ACTIVATED:
  - Trigger: Porting completes
  - Integration: PRT porting workflow
  - Action: State synchronized

ANY → BLOCKED:
  - Trigger: Error occurs or manual block
  - Reason: Data inconsistency, fraud, technical issue
  - Resolution: Manual intervention required

BLOCKED → AVAILABLE:
  - Trigger: Error resolved
  - Validation: Data consistency verified
  - Authorization: Admin role required
```

#### Callnumber Types Management

**Type Classifications:**

| Type | German | Code | Description | Business Rules | Timeout |
|------|--------|------|-------------|----------------|---------|
| Single | Einzelrufnummer | S | Individual number for DTAG network | Standard 24h reservation | 24h |
| Range Normal | Rufnummernbereich | R | ≤200 numbers in ascending sequence | Standard range rules | 24h |
| Range Big (DuWa) | Großer Bereich | D | >200 numbers in ascending sequence | Variable reservation time | Variable |
| Old Stock | Altbestand | O | Numbers with unwanted arity | Special handling, no new allocation | - |
| Technical | Technische Rufnummer | T | Technical numbers in 032 range | 032 range only, special rules | - |

**DuWa (Duration of Waiting) Threshold:**
- **Threshold**: 200 numbers
- **Single/Range Normal (≤200)**: Fixed 24-hour reservation timeout
- **Range Big (>200)**: Variable timeout based on size calculation
- **Formula**: `timeout_hours = 24 + ((size - 200) / 10)`
  - Example: 500 numbers = 24 + ((500-200)/10) = 54 hours
- **Configuration**: `vnrm.fcm.duwa.threshold=200` (configurable via COM config-server)

**Type-Specific Business Logic:**
```java
public int calculateReservationTimeout(int numberCount, CallnumberType type) {
    if (type == CallnumberType.SINGLE ||
        (type == CallnumberType.RANGE && numberCount <= duwaThreshold)) {
        return 24; // Standard 24-hour timeout
    } else if (type == CallnumberType.RANGE && numberCount > duwaThreshold) {
        // Variable timeout for DuWa ranges
        return 24 + ((numberCount - duwaThreshold) / 10);
    }
    return 24; // Default fallback
}
```

#### FCM API Specification

**RESTful Endpoints:**

**Callnumber Operations:**
```
GET    /api/v1/callnumbers                          # List callnumbers (paginated)
GET    /api/v1/callnumbers/{onkz}/{number}          # Get specific callnumber
POST   /api/v1/callnumbers/reserve                  # Reserve callnumber
POST   /api/v1/callnumbers/activate                 # Activate callnumber
DELETE /api/v1/callnumbers/{onkz}/{number}/reserve  # Cancel reservation
PATCH  /api/v1/callnumbers/{onkz}/{number}/state    # Update state
GET    /api/v1/callnumbers/search                   # Search with filters
GET    /api/v1/callnumbers/{onkz}/{number}/history  # Get modification history
```

**Range Operations:**
```
POST   /api/v1/ranges/reserve                       # Reserve number range
POST   /api/v1/ranges/activate                      # Activate range
GET    /api/v1/ranges/{onkz}/{start}/{end}          # Get range info
DELETE /api/v1/ranges/{onkz}/{start}/{end}/reserve  # Cancel range reservation
GET    /api/v1/ranges/{onkz}/{start}/{end}/numbers  # List numbers in range
```

**Batch Operations:**
```
POST   /api/v1/callnumbers/batch/reserve            # Batch reserve (async)
POST   /api/v1/callnumbers/batch/activate           # Batch activate (async)
GET    /api/v1/callnumbers/batch/{batch_id}/status  # Get batch job status
```

**Example Request/Response:**

**Reserve a Single Callnumber:**
```bash
POST /api/v1/callnumbers/reserve
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "onkz": "030",
  "callnumber": "12345678",
  "callnumberType": "SINGLE",
  "contingentId": 1001,
  "customerId": "CUST-001",
  "reservationDuration": 1440,
  "businessCorrelationId": "ORDER-2024-001"
}

# Response (201 Created)
{
  "local_area_code_callnumber": "03012345678",
  "callnumber": "12345678",
  "local_area_code": "030",
  "callnumberstate": "R",
  "callnumber_type": "S",
  "booking_id_vnrm": 123456,
  "booking_type": "A",
  "contingent_id": 1001,
  "valid_from": "2024-01-15T10:30:00.000Z",
  "valid_to": "2024-01-16T10:30:00.000Z",
  "reservation_expires_at": "2024-01-16T10:30:00.000Z",
  "modification_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "_links": {
    "self": {
      "href": "/api/v1/callnumbers/030/12345678"
    },
    "activate": {
      "href": "/api/v1/callnumbers/activate",
      "method": "POST"
    },
    "cancel": {
      "href": "/api/v1/callnumbers/030/12345678/reserve",
      "method": "DELETE"
    }
  }
}
```

**Reserve a Range (DuWa):**
```bash
POST /api/v1/ranges/reserve
Content-Type: application/json

{
  "onkz": "089",
  "start": "20000000",
  "end": "20000499",
  "count": 500,
  "callnumberType": "RANGE_BIG",
  "contingentId": 2001,
  "customerId": "CUST-CORP-001"
}

# Response (201 Created)
{
  "range_id": "089-20000000-20000499",
  "onkz": "089",
  "callnumber_start": "20000000",
  "callnumber_end": "20000499",
  "count": 500,
  "callnumberstate": "R",
  "callnumber_type": "D",
  "booking_id_vnrm": 123457,
  "contingent_id": 2001,
  "reservation_timeout_hours": 54,
  "valid_from": "2024-01-15T10:30:00.000Z",
  "valid_to": "2024-01-17T16:30:00.000Z",
  "modification_uuid": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
  "duwa_threshold_applied": true
}
```

### NBIM - Number Block Inventory Management

#### Business Data Model

**Number Block Table:**
```sql
CREATE TABLE vnrm_nbim.number_block (
  block_id VARCHAR(13) PRIMARY KEY,
  ndc VARCHAR(5) NOT NULL,  -- ONKZ (Ortsnetzkennzahl)
  block_start VARCHAR(10) NOT NULL,
  block_end VARCHAR(10) NOT NULL,
  block_size INTEGER NOT NULL,
  block_owner_legal VARCHAR(10),  -- TSP D-Kennung (legal owner)
  block_owner_new VARCHAR(10),    -- Current effective owner
  reg_order_id VARCHAR(20),  -- BNetzA registry order ID
  oldstock_sign VARCHAR(1),
  status_v14 VARCHAR(3),
  block_state VARCHAR(20) NOT NULL,
  area_processing_state VARCHAR(20),
  process_release_date DATE,
  network_release_date DATE,
  load_capacity INTEGER DEFAULT 0,
  free_numbers INTEGER GENERATED ALWAYS AS (block_size - load_capacity) STORED,
  utilization_percent NUMERIC(5,2) GENERATED ALWAYS AS
    (CASE WHEN block_size > 0 THEN (load_capacity::NUMERIC / block_size * 100) ELSE 0 END) STORED,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_onkz FOREIGN KEY (ndc) REFERENCES vnrm_rdm.onkz(onkz_id),
  CONSTRAINT fk_owner_legal FOREIGN KEY (block_owner_legal) REFERENCES vnrm_rdm.tsp(tsp_id),
  CONSTRAINT check_capacity CHECK (load_capacity >= 0 AND load_capacity <= block_size)
);

-- Performance and query indexes
CREATE INDEX idx_block_onkz ON vnrm_nbim.number_block(ndc);
CREATE INDEX idx_block_owner ON vnrm_nbim.number_block(block_owner_legal);
CREATE INDEX idx_block_state ON vnrm_nbim.number_block(block_state);
CREATE INDEX idx_block_capacity ON vnrm_nbim.number_block(load_capacity);
CREATE INDEX idx_block_utilization ON vnrm_nbim.number_block(
  (CASE WHEN block_size > 0 THEN (load_capacity::NUMERIC / block_size * 100) ELSE 0 END)
);
```

#### Number Block State Model

**Block States with Business Logic:**

| State | German | Code | Definition | Detection Logic | Auto Transition |
|-------|--------|------|------------|-----------------|-----------------|
| FREE | frei | FREE | Ready for DTAG use, load capacity = 0 | legal_owner = 'D001' AND load_capacity = 0 | No |
| USED | belegt | USED | Contains activated/deactivated numbers | legal_owner ≠ 'D001' OR load_capacity > 0 | Yes (on number activation) |
| RESERVED | reserviert | RESERVED | Bound to specific customer order | VNRM business logic only | No (manual) |
| LOCKED | gesperrt | LOCKED | Not for use, return to BNetzA when empty | status_v14 = '400' OR manual flag | No (manual) |
| BNETZA | BNETZA | BNETZA | No user or BNetzA ownership | legal_owner = 'BNETZA' OR legal_owner IS NULL | No |

**State Transition Logic:**
```java
public void updateBlockState(NumberBlock block) {
    // Automatic state detection based on business rules
    if (block.getLegalOwner().equals("BNETZA") || block.getLegalOwner() == null) {
        block.setState(BlockState.BNETZA);
    } else if (block.getStatusV14().equals("400") || block.isManuallyLocked()) {
        block.setState(BlockState.LOCKED);
    } else if (block.getLegalOwner().equals("D001") && block.getLoadCapacity() == 0) {
        block.setState(BlockState.FREE);
    } else if (!block.getLegalOwner().equals("D001") || block.getLoadCapacity() > 0) {
        block.setState(BlockState.USED);
    }
    // RESERVED state is manual only, set via business logic
}
```

#### Area Processing State Model

**Detailed Area Processing States:**

| State | German | Code | Description | Business Logic | Allowed Operations |
|-------|--------|------|-------------|----------------|-------------------|
| BLOCKED | gesperrt | BLOCKED | Block not to be used | Manual intervention, restructuring planned | None |
| CLOSED | geschlossen | CLOSED | Returns to BNetzA | Block retirement process | None |
| CLOSE_REQ | Rückgabeanforderung | CLOSE_REQ | Return request to BNetzA | Preparation for return | None |
| WAITING | warten | WAITING | Can be used when released | Pending activation, manual/auto release | Manual release only |
| ALL | alles | ALL | Single and range booking allowed | Full operation mode | All operations |
| SINGLE | Einzelrufnummer | SINGLE | Only single number booking | Limited by count_free_numbers | Single only |
| TEC | technisch | TEC | Technical single number booking | Technical numbers only | Technical numbers |
| FULL | ausgebucht | FULL | Block fully allocated | No more numbers available, capacity reached | None (read-only) |

**State Business Rules:**
- **BLOCKED**: Requires admin intervention to unblock
- **CLOSED/CLOSE_REQ**: Irreversible, block will be returned to BNetzA
- **WAITING**: Transition to ALL or SINGLE when manually released
- **ALL**: Automatic transition when free capacity > threshold
- **SINGLE**: Automatic transition when free capacity < range_threshold
- **TEC**: Manual setting for technical number blocks (032 range)
- **FULL**: Automatic when `load_capacity == block_size`

#### RNVS to VNRM Field Mapping

**Complete Migration Mapping:**

| VNRM GUI | VNRM DB | RNVS Table | RNVS Field | Data Type | Description |
|----------|---------|------------|------------|-----------|-------------|
| ONKZ | ndc | T_RNB | RNB_ONRNBID | VARCHAR(5) | Area code (Ortsnetzkennzahl) |
| RNB ID | block_id | T_RNB | RNB_RNBID | VARCHAR(13) | Block identifier |
| BNetzA ID | reg_order_id | T_RNB | RNB_REGAUFTRAGSNR | VARCHAR(20) | Registry order number |
| Altbestand | oldstock_sign | T_RNB | RNB_STATUSV14 | VARCHAR(1) | Legacy status flag |
| RNB Besitzer | block_owner_new | T_RNB | - | VARCHAR(10) | Block owner (TSP) |
| Veröffentlichungsdatum | process_release_date | T_RNB | RNB_VEROEFFENTLICHT | DATE | Publication date (PDA) |
| Netzwirksamkeit | network_release_date | T_RNB | RNB_NETZWIRKSAM | DATE | Network activation date |
| Block Größe | block_size | T_RNB | RNB_GROESSE | INTEGER | Number of numbers in block |
| Kapazität | load_capacity | T_RUFNR | COUNT(*) | INTEGER | Calculated from callnumbers |

#### NBIM API Specification

**RESTful Endpoints:**
```
GET    /api/v1/blocks                      # List all number blocks (paginated)
GET    /api/v1/blocks/{block_id}           # Get specific block
GET    /api/v1/blocks/by-onkz/{onkz}       # Blocks by area code
GET    /api/v1/blocks/by-owner/{tsp_id}    # Blocks by owner
GET    /api/v1/blocks/by-state/{state}     # Blocks by state
GET    /api/v1/blocks/capacity/summary     # Capacity summary report
POST   /api/v1/blocks                      # Create block (admin)
PUT    /api/v1/blocks/{block_id}           # Update block (admin)
PATCH  /api/v1/blocks/{block_id}/state     # Update block state
PATCH  /api/v1/blocks/{block_id}/area-state # Update area processing state
GET    /api/v1/blocks/{block_id}/capacity  # Get capacity info
GET    /api/v1/blocks/{block_id}/numbers   # List numbers in block
```

**Example Queries:**

**Get All Free Blocks for Berlin (030):**
```bash
GET /api/v1/blocks/by-onkz/030?state=FREE&page=1&size=20

# Response
{
  "blocks": [
    {
      "block_id": "030123",
      "ndc": "030",
      "block_start": "1230000",
      "block_end": "1239999",
      "block_size": 10000,
      "block_owner_legal": "D001",
      "block_owner_new": "D001",
      "block_state": "FREE",
      "area_processing_state": "ALL",
      "load_capacity": 0,
      "free_numbers": 10000,
      "utilization_percent": 0.00,
      "process_release_date": "2024-01-01",
      "network_release_date": "2024-01-15",
      "_links": {
        "self": {"href": "/api/v1/blocks/030123"},
        "numbers": {"href": "/api/v1/blocks/030123/numbers"}
      }
    }
  ],
  "page": {
    "size": 20,
    "totalElements": 5,
    "totalPages": 1,
    "number": 0
  }
}
```

**Capacity Summary Report:**
```bash
GET /api/v1/blocks/capacity/summary?onkz=030

# Response
{
  "onkz": "030",
  "total_blocks": 150,
  "by_state": {
    "FREE": {"count": 25, "numbers": 250000},
    "USED": {"count": 100, "numbers": 1000000},
    "RESERVED": {"count": 10, "numbers": 100000},
    "LOCKED": {"count": 10, "numbers": 50000},
    "BNETZA": {"count": 5, "numbers": 50000}
  },
  "total_capacity": 1450000,
  "used_capacity": 1200000,
  "free_capacity": 250000,
  "utilization_percent": 82.76,
  "capacity_threshold_alert": false
}
```

### NBOM - Number Block Order Management

#### Business Process Integration

**BNetzA Integration Workflow (4-Step Process):**

```
Step 1: Capacity Monitoring
├─ NBIM monitors block utilization across all ONKZs
├─ Threshold: Free capacity < 10% triggers alert
├─ Automated analysis: Trend projection for next 6 months
└─ Decision: Generate order if capacity will be exhausted

Step 2: Order Generation
├─ NBOM creates formal block request
├─ Required fields:
│  ├─ ONKZ (area code requiring additional capacity)
│  ├─ Desired block size (typically 10,000 numbers)
│  ├─ Business justification (growth projection)
│  └─ Contact information
└─ Order validation before submission

Step 3: BNetzA Submission
├─ Electronic submission via BNetzA portal API
├─ Order tracking number assigned
├─ Acknowledgment received (24-48h)
└─ Status: SUBMITTED → PENDING

Step 4: Order Tracking & Fulfillment
├─ Status monitoring (pending, approved, rejected)
├─ BNetzA decision processing
├─ If APPROVED:
│  ├─ BNetzA allocates new block
│  ├─ Block data transmitted to VNRM
│  ├─ NBIM imports block
│  └─ FCM makes numbers AVAILABLE
└─ If REJECTED:
   ├─ Rejection reason analysis
   ├─ Resubmission with corrections
   └─ Escalation if needed
```

#### Order Management Lifecycle

**Order States:**

| State | Description | Actions Available | Duration |
|-------|-------------|-------------------|----------|
| DRAFT | Order being prepared | Edit, Submit, Delete | No limit |
| SUBMITTED | Sent to BNetzA | View, Cancel | 24-48h |
| PENDING | Awaiting BNetzA decision | View, Follow-up | 2-4 weeks |
| APPROVED | Allocation approved by BNetzA | Import to NBIM | 24h |
| FULFILLED | Block imported to NBIM | View only | Final |
| REJECTED | Request denied by BNetzA | View, Resubmit | Final |
| CANCELLED | Order cancelled before decision | View only | Final |

**Order Tracking:**
```java
@Service
public class BlockOrderService {

    @Scheduled(fixedDelay = 3600000) // Every hour
    public void checkCapacityThresholds() {
        List<String> onkzList = getAllONKZ();

        for (String onkz : onkzList) {
            CapacitySummary capacity = nbimClient.getCapacitySummary(onkz);

            // Check threshold: free capacity < 10%
            if (capacity.getUtilizationPercent() > 90.0) {
                log.warn("ONKZ {} capacity threshold exceeded: {}%",
                         onkz, capacity.getUtilizationPercent());

                // Create order if none exists
                if (!hasOpenOrder(onkz)) {
                    createBlockOrder(onkz, capacity);
                }
            }
        }
    }
}
```

### CPIN - Callnumber Porting Information

#### Porting Information Display System

**Display Capabilities:**
- **Current Porting Status**: Real-time status of ongoing porting operations from PRT services
- **Historical Porting Data**: Complete porting history for any callnumber
- **Process Timeline**: Detailed workflow progress tracking with PDA message timestamps
- **Cross-System Integration**: Unified data from NUM FCM and NZK (Network Control Center)

**Data Sources & Integration:**
- **PRT FBPM**: PDA message processing and porting workflows
- **PRT FCPM**: Porting state machine and carrier coordination
- **NUM FCM**: Callnumber state changes during porting
- **Message Bus Message Bus**: Real-time event streaming for status updates

**User Access Patterns:**

| User Role | Access Level | Use Cases |
|-----------|--------------|-----------|
| NUM Operations | Full access | Porting oversight, exception handling |
| NZK (Network Control Center) | Read-only | Network monitoring, capacity planning |
| Customer Service | Limited | Customer inquiry support, status checks |
| Business Analysts | Read-only | Performance metrics, reporting, KPIs |

#### CPIN API Specification

**RESTful Endpoints:**
```
GET    /api/v1/porting/callnumbers/{onkz}/{number}        # Get porting info
GET    /api/v1/porting/callnumbers/{onkz}/{number}/history # Get porting history
GET    /api/v1/porting/orders                              # List porting orders
GET    /api/v1/porting/orders/{order_id}                   # Get specific order
GET    /api/v1/porting/orders/by-status/{status}           # Filter by status
GET    /api/v1/porting/statistics                          # Porting statistics
```

## Integration Dependencies

### Internal VNRM Dependencies

**COM Submodule Integration:**
- **Configuration Server (com-cs-config-server-api)**: Critical single point of failure for all NUM services
  - Service startup configuration
  - Runtime configuration refresh
  - Feature flags and toggles
  - Business rule parameters (DuWa threshold, reservation timeout)
- **Reference Data (RDM)**: ONKZ and TSP validation via RDM API
  - ONKZ validation before number allocation
  - TSP D-Kennung validation for block ownership
  - Carrier reference data for porting
- **Error Catalog (com-ecc-errorcode-catalog-api)**: NUM errors mapped to standardized codes
  - NUM-C-0001: Callnumber reservation failed
  - NUM-H-0042: Block capacity threshold exceeded
- **Portal (vnrm-container)**: NUM GUIs integrated into main portal
  - CPIN GUI for porting information
  - CACI GUI for contingent management
  - NBOM GUI for block ordering

**PRT Submodule Integration:**
- **Porting Workflows**: NUM provides callnumber status to PRT for porting validation
- **CPIN Display**: Shows real-time porting information from PRT FBPM and FCPM services
- **State Synchronization**: Callnumber states update during porting (ACTIVATED → PROCESSING → ACTIVATED)
- **Event Bus Integration**: Message Bus events for porting completion trigger NUM state updates

**COR Submodule Integration:**
- **Error Management**: NUM business errors tracked in COR BEM
- **Correction Workflows**: Number data corrections via COR order management
- **Audit Trail**: Complete error resolution history

**NTW Network Integration:**
- **Routing Updates**: NUM activation events trigger network routing configuration
- **I-BCF Integration**: Network element configuration for new numbers
- **M-TAS Integration**: Application service activation for callnumbers

**SPE Submodule Integration:**
- **RNVS Synchronization**: Bidirectional data sync with legacy system
- **Database Integration**: Direct database access via spe-vnrm-rnvs-db-api
- **Migration Support**: Gradual migration from RNVS to VNRM NUM services

### External System Dependencies

**BNetzA (Federal Network Agency):**
- **Block Allocation**: New number block requests via NBOM
- **Regulatory Compliance**: Block ownership validation
- **Order Processing**: Electronic submission and tracking
- **Publication Data**: PDA process dates and network activation dates

**FCM Integration (Fixed Callnumber Management):**
- Critical for porting workflows
- Carrier operations coordination
- Inter-carrier routing management

**Network Control Center (NZK):**
- Porting information display via CPIN
- Network operations monitoring
- Real-time status dashboards

## Advanced Technical Implementation

### Database Design Patterns

**PostgreSQL Optimization:**
- **Partitioning**: Time-based partitioning for `callnumber_modification` audit trail
  ```sql
  CREATE TABLE callnumber_modification_2024_01 PARTITION OF callnumber_modification
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
  ```
- **Indexing Strategy**: Composite indexes for common query patterns
  - `idx_callnumber_onkz_state` on `(local_area_code, callnumberstate)`
  - `idx_block_onkz_state` on `(ndc, block_state)`
- **Constraints**: Enforce data integrity with CHECK constraints
- **Generated Columns**: Automatic calculation of utilization_percent and free_numbers
- **Audit Trails**: UUID-based modification tracking with complete history

### API Design Patterns

**RESTful Standards:**
- **Resource-Based URLs**: `/api/v1/callnumbers/{onkz}/{number}`
- **HTTP Method Mapping**:
  - GET: Retrieve resources
  - POST: Create new resources
  - PUT: Complete resource replacement
  - PATCH: Partial resource updates
  - DELETE: Resource removal
- **Status Codes**: Proper HTTP response codes
  - 200: Success
  - 201: Created
  - 204: No Content
  - 400: Bad Request
  - 404: Not Found
  - 409: Conflict (reservation collision)
  - 500: Internal Server Error
- **Pagination**: Cursor-based pagination for large datasets
- **Filtering**: Query parameter filtering for complex searches
- **HATEOAS**: Hypermedia links for API navigation

### Event-Driven Architecture

**Message Bus Integration:**

**State Change Events:**
```java
// Callnumber state transition event
@Data
public class CallnumberStateChangedEvent {
    private String callnumber;
    private String onkz;
    private String previousState;
    private String newState;
    private LocalDateTime timestamp;
    private String correlationId;
    private String userId;
}

// Publish on state change
message_busTemplate.send("num.callnumber.state.changed", event);
```

**Porting Events:**
```java
// Listen to PRT porting events
@Message BusListener(topics = "prt.porting.completed")
public void handlePortingCompleted(PortingCompletedEvent event) {
    // Update callnumber state
    callnumberService.updateStateForPorting(event.getCallnumber());

    // Publish NUM event
    publishCallnumberStateChanged(event.getCallnumber(), "PROCESSING", "ACTIVATED");
}
```

**Block Events:**
```java
// Block capacity threshold event
@Scheduled(fixedRate = 3600000) // Hourly
public void checkBlockCapacity() {
    List<NumberBlock> nearFullBlocks = blockRepository.findByUtilizationGreaterThan(90);

    for (NumberBlock block : nearFullBlocks) {
        BlockCapacityThresholdEvent event = new BlockCapacityThresholdEvent(
            block.getBlockId(),
            block.getNdc(),
            block.getUtilizationPercent()
        );
        message_busTemplate.send("num.block.capacity.threshold", event);
    }
}
```

### Performance Optimization

**Scalability Patterns:**
- **Read Replicas**: Database read scaling for reporting queries and CPIN displays
- **Caching Strategy**:
  - **Redis**: Cache RDM reference data (ONKZ, TSP) with 1-hour TTL
  - **Caffeine**: In-memory caching for block state lookups
- **Async Processing**: Background jobs for bulk operations
  ```java
  @Async
  public CompletableFuture<BatchResult> reserveCallnumbersBatch(List<ReservationRequest> requests) {
      // Process batch asynchronously
      return CompletableFuture.completedFuture(result);
  }
  ```
- **Circuit Breakers**: Resilience patterns for external service calls
  ```java
  @CircuitBreaker(name = "rdm-api", fallbackMethod = "rdmApiFallback")
  public Onkz validateOnkz(String onkz) {
      return rdmClient.getOnkz(onkz);
  }
  ```

**Database Query Optimization:**
- **Prepared Statements**: Prevent SQL injection and improve performance
- **Query Plan Analysis**: `EXPLAIN ANALYZE` for slow queries
- **Connection Pooling**: HikariCP with optimized settings
  ```yaml
  spring.datasource.hikari:
    maximum-pool-size: 20
    minimum-idle: 5
    connection-timeout: 30000
  ```
- **Batch Operations**: Batch inserts for bulk number allocation

## Technology Stack & Implementation Details

### Backend Technologies

**Spring Boot Ecosystem:**
- **Version**: Spring Boot 2.7.x
- **Spring Data JPA**: Database access with query method derivation
- **Spring Security**: OAuth2/JWT authentication, role-based authorization
- **Spring Message Bus**: Event streaming via Tardis Horizon
- **Spring Cloud Config**: Client for COM config-server integration
- **Spring Actuator**: Health checks, metrics, management endpoints

**Database:**
- **PostgreSQL 13+**: Primary relational database
- **HikariCP**: High-performance connection pooling
- **Liquibase**: Database schema migration and versioning
- **Partitioning**: Time-based partitioning for audit tables

**Messaging & Events:**
- **Message Bus**: Event streaming via Tardis Horizon
- **Event Sourcing**: Complete audit trail and event replay capability
- **Schema Registry**: Avro schemas for event serialization
- **Dead Letter Queue**: Failed message handling

## Best Practices

### Callnumber Management
1. **Always validate ONKZ** via COM RDM before allocation to prevent invalid area codes
2. **Track all state transitions** in callnumber_modification table for complete audit trail
3. **Implement idempotent operations** for retry scenarios (reservation, activation)
4. **Handle DuWa threshold correctly** - different timeout logic for ranges >200 numbers
5. **Monitor reservation timeouts** - automatic cleanup required to prevent leaked reservations
6. **Validate TSP ownership** - ensure proper carrier assignment for porting operations
7. **Use correlation IDs** - track operations across VNRM services for debugging

### Number Block Management
1. **Synchronize with BNetzA regularly** - validate block ownership and allocation status
2. **Track capacity thresholds** - trigger NBOM orders proactively (>90% utilization)
3. **Maintain block state consistency** - ensure block states match aggregated callnumber states
4. **Document block migrations** - complete audit trail for regulatory compliance
5. **Monitor area processing states** - ensure proper progression through lifecycle
6. **Prevent over-allocation** - enforce capacity constraints at database level
7. **Regular capacity reports** - proactive capacity planning to prevent exhaustion

### Integration Patterns
1. **Depend on COM configuration** - config-server is critical, implement circuit breakers
2. **Cache RDM reference data** - reduce latency and load on COM services
3. **Use event bus for state changes** - notify PRT, NTW, and other services asynchronously
4. **Implement circuit breakers** - handle COM/PRT failures gracefully with fallback logic
5. **Validate before operations** - check ONKZ, TSP, block availability before allocation
6. **Use distributed tracing** - correlation IDs across all service boundaries
7. **Handle RNVS sync carefully** - bidirectional sync requires conflict resolution strategy

### Operational Excellence
1. **Monitor state machine health** - track state distribution and unusual transitions
2. **Alert on capacity thresholds** - prevent number exhaustion with early warnings
3. **Regular database maintenance** - vacuum, reindex, analyze for PostgreSQL health
4. **Audit log retention** - maintain modification history for regulatory compliance
5. **Performance monitoring** - track API response times and database query performance
6. **Backup and recovery** - regular backups with tested recovery procedures
7. **Capacity planning** - project future needs based on historical growth trends

---

**See also:**
- [COM Architecture Reference](../vnrm-com-architecture/REFERENCE.md) - Configuration and Reference Data
- [PRT Architecture Reference](../vnrm-prt-architecture/REFERENCE.md) - Porting Integration
- [COR Architecture Reference](../vnrm-cor-architecture/REFERENCE.md) - Error Management
- [SPE Architecture Reference](../vnrm-spe-architecture/REFERENCE.md) - Legacy RNVS Integration
- [NTW Architecture Reference](../vnrm-ntw-architecture/REFERENCE.md) - Network Routing
