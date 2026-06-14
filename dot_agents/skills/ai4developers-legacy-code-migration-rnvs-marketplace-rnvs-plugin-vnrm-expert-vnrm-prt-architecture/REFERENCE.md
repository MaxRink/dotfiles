# VNRM PRT (PORTING MANAGEMENT) Architecture Reference

## Overview

The VNRM PRT (PORTING MANAGEMENT) submodule handles all aspects of telephone number portability in the German telecommunications market, managing porting operations for approximately 160 TSPs (Telephony Service Providers) through automated PDA (Portierungsdaten Austausch) message processing, carrier coordination, and BNetzA regulatory compliance.

PRT implements the complex business logic required for number portability operations, including automated import/export workflows, paired message validation (L+P records), LWL-triggered porting automation, manual intervention capabilities, and complete audit trails for regulatory compliance. The submodule processes thousands of porting operations daily while maintaining strict compliance with ITEX-PDA 20-0-3 specification and BNetzA timeline requirements.

## Service Level Architecture

### Service Level Classification

**High Availability (HA) Services - 24/7 Support:**
- **Response Time**: 3 hours
- **Availability**: 24/7 on-call duty required
- **Support Channels**: Hotline + ServiceNow + FMB post box
- **Critical Impact**: Service outages affect number portability operations across German telecommunications market
- **Business Justification**: Number porting is legally mandated by BNetzA - any downtime prevents customer migrations and violates regulatory requirements

**Office Time (OT) Services - Business Hours Support:**
- **Response Time**: 3 days
- **Availability**: Business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Impact**: Limited to administrative and clearing functions
- **Business Justification**: Clearing and dispute resolution operations are not time-critical

## Deployed Microservices

### Production Services (VNRM 1.9.0+)

#### Fixednet Block Porting Management (FBPM)

| Service                                            | Version | SLA Level | Purpose | Dependencies |
|----------------------------------------------------|---------|-----------|---------|--------------|
| prt-fbpm-fixednet-block-porting-management-api     | v1.9.3 | HA | Core porting business logic and PDA processing | COM config-server, RDM |
| prt-fbpm-fixednet-block-porting-management-backend | v1.9.3 | HA | Backend implementation | PostgreSQL, Message Bus |

**Technology Stack:**
- **Backend**: Spring Boot 2.7.x, Spring Data JPA
- **Database**: PostgreSQL 13+ with partitioning by porting_date
- **Messaging**: Message Bus via Tardis Horizon
- **API**: RESTful with OpenAPI 3.0 specification

**Core Capabilities:**
- PDA file import from carrier partners (~160 TSPs)
- Multi-layered validation (syntax, business rules, regulatory)
- Order creation for RNB (Rufnummernblock) changes
- Event distribution to message bus for cross-service coordination
- ITEX-PDA 20-0-3 specification compliance

**PDA File Processing:**
- **File Format**: Structured text format per ITEX-PDA specification
- **Import Frequency**: Real-time processing as files arrive
- **Batch Size**: Up to 10,000 porting records per file
- **Validation**: Syntax → Business Rules → Regulatory Compliance
- **Error Handling**: Automatic retry for transient failures, dead letter queue for persistent errors

#### Fixednet Callnumber Porting Management (FCPM)

| Service                                    | Version | SLA Level | Purpose | Dependencies |
|--------------------------------------------|---------|-----------|---------|--------------|
| fixednet-callnumber-porting-management-api | v1.9.5 | HA | Automated/manual porting workflows | COM config-server, NUM FCM |
| fixednet-callnumber-porting-management-gui | v1.9.4 | HA | Porting management GUI | FCPM API |
| fixednet-callnumber-porting-management-backend | v1.9.5 | HA | Backend implementation | PostgreSQL, Message Bus, LWL |

**Critical Dependencies:**
- **LWL (Leitweglenkung)**: Routing (external system)
- **CRM-T**: Customer relationship management integration (external system)
- **NUM FCM**: Callnumber inventory synchronization
- **COM Config-Server**: Essential for service configuration (single point of failure)

**Core Capabilities:**
- Automated import workflow (LWL-triggered with parallel processing)
- Automated export workflow (carrier coordination)
- Manual import/export GUI capabilities
- Provisional import status management ("vi" status)
- PDA message generation (Status "P" distribution to all TNBs)

**Workflow Processing:**
- **Automated Import**: LWL notification → Parallel import/booking → CRM-T confirmation → "vi" status → PDA_MESSAGE_OUT
- **Manual Import**: GUI-driven import → Validation → Approval workflow → Execution → Audit trail
- **Export Operations**: Automated or manual export → Carrier notification → Status tracking → Completion confirmation

#### Fixed Callnumber Clearing Management (FCCM)

| Service | Version | SLA Level | Purpose | Dependencies |
|---------|---------|-----------|---------|--------------|
| fixed-callnumber-clearing-management-api | v1.8.2 | OT | Dispute resolution and TNB communication | COM config-server |
| fixed-callnumber-clearing-management-backend | v1.8.2 | OT | Backend implementation | PostgreSQL, SMTP |

**Business Process:**
- TNB communication via automated email handling
- Porting dispute resolution workflows
- Clarification requests and responses
- Documentation and audit trail logging

**Target Users:**
- **PRT operations personnel**: Dispute management and TNB coordination
- **Customer service representatives**: Customer complaint handling
- **Business analysts**: Clearing metrics and reporting

## Detailed Microservice Implementation Specifications

### FBPM - Fixednet Block Porting Management

#### Database Architecture (PostgreSQL)

**Porting Order Table:**
```sql
CREATE TABLE vnrm_fbpm.porting_order (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  callnumber VARCHAR(20) NOT NULL,
  onkz VARCHAR(5) NOT NULL,
  number_range_start VARCHAR(15) NOT NULL,
  number_range_end VARCHAR(15) NOT NULL,
  pk_ab VARCHAR(4) NOT NULL,  -- Delivering TSP (PK_ab = abgebend)
  pk_auf VARCHAR(4) NOT NULL,  -- Receiving TSP (PK_auf = aufnehmend)
  porting_date DATE NOT NULL,
  pda_message_type VARCHAR(1) NOT NULL CHECK (pda_message_type IN ('Z', 'L', 'P')),
  order_state VARCHAR(20) NOT NULL,
  pda_file_id VARCHAR(100) NOT NULL,
  validation_errors JSONB,
  paired_order_id UUID,  -- Reference to paired L/P order
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_by VARCHAR(100),
  CONSTRAINT fk_onkz FOREIGN KEY (onkz) REFERENCES vnrm_rdm.onkz(onkz_id),
  CONSTRAINT fk_pk_ab FOREIGN KEY (pk_ab) REFERENCES vnrm_rdm.tsp(pda_portierungskennung),
  CONSTRAINT fk_pk_auf FOREIGN KEY (pk_auf) REFERENCES vnrm_rdm.tsp(pda_portierungskennung),
  CONSTRAINT check_porting_date CHECK (porting_date >= CURRENT_DATE)
);

-- Partitioning by porting_date for performance
CREATE TABLE vnrm_fbpm.porting_order_2024_01 PARTITION OF vnrm_fbpm.porting_order
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Performance indexes
CREATE INDEX idx_porting_order_callnumber ON vnrm_fbpm.porting_order(callnumber);
CREATE INDEX idx_porting_order_state ON vnrm_fbpm.porting_order(order_state);
CREATE INDEX idx_porting_order_date ON vnrm_fbpm.porting_order(porting_date);
CREATE INDEX idx_porting_order_pk ON vnrm_fbpm.porting_order(pk_ab, pk_auf);
CREATE INDEX idx_porting_order_paired ON vnrm_fbpm.porting_order(paired_order_id);
CREATE INDEX idx_porting_order_file ON vnrm_fbpm.porting_order(pda_file_id);
```

**PDA File Processing Log:**
```sql
CREATE TABLE vnrm_fbpm.pda_file_log (
  file_id VARCHAR(100) PRIMARY KEY,
  file_name VARCHAR(255) NOT NULL,
  source_tsp VARCHAR(4) NOT NULL,
  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_size_bytes BIGINT NOT NULL,
  record_count INTEGER NOT NULL,
  validation_status VARCHAR(20) NOT NULL,
  processing_duration_ms INTEGER,
  error_message TEXT,
  CONSTRAINT fk_source_tsp FOREIGN KEY (source_tsp)
    REFERENCES vnrm_rdm.tsp(pda_portierungskennung)
);

CREATE INDEX idx_pda_file_received ON vnrm_fbpm.pda_file_log(received_at DESC);
CREATE INDEX idx_pda_file_status ON vnrm_fbpm.pda_file_log(validation_status);
```

#### PDA Message Processing Logic

**Message Type Definitions:**

| Type | German | Code | Purpose | Sender | Receiver | Business Logic |
|------|--------|------|---------|--------|----------|----------------|
| Return | Rückgabe | Z | Return callnumber to owner | Receiving TSP | Delivering TSP | Number returns to original owner (TSP) |
| Export | Abgabe | L | Export from delivering TSP | Delivering TSP | All TSPs | Delivering TSP announces export of numbers |
| Import | Übernahme | P | Import by receiving TSP | Receiving TSP | All TSPs | Receiving TSP announces import of numbers |

**PDA Data Exchange Standard (ITEX-PDA 20-0-3):**

**Mandatory Fields:**
```yaml
PdaMessage:
  portierte_rufnummer_1: "03012345678"     # Start of number range
  portierte_rufnummer_2: "03012345689"     # End of number range (can equal start for single number)
  portierungsdatum: "2024-01-20"           # Scheduled porting execution date (YYYY-MM-DD)
  pk_ab: "P001"                            # Portierungskennung abgebend (delivering TSP)
  pk_auf: "P002"                           # Portierungskennung aufnehmend (receiving TSP)
  status: "L"                              # Porting notification type (Z/L/P)
  timestamp: "2024-01-15T10:30:00Z"        # Message generation timestamp
```

**Validation Rules Implementation:**

**1. Paired Message Validation (L+P):**
```java
@Service
public class PairedMessageValidator {

    public ValidationResult validatePairedMessages(PdaMessage lMessage, PdaMessage pMessage) {
        List<ValidationError> errors = new ArrayList<>();

        // Rule 1: Porting dates must match
        if (!lMessage.getPortingDate().equals(pMessage.getPortingDate())) {
            errors.add(new ValidationError(
                "PORTING_DATE_MISMATCH",
                "L message date: " + lMessage.getPortingDate() +
                ", P message date: " + pMessage.getPortingDate()
            ));
        }

        // Rule 2: PK_ab must match (same delivering TSP)
        if (!lMessage.getPkAb().equals(pMessage.getPkAb())) {
            errors.add(new ValidationError(
                "PK_AB_MISMATCH",
                "L message PK_ab: " + lMessage.getPkAb() +
                ", P message PK_ab: " + pMessage.getPkAb()
            ));
        }

        // Rule 3: PK_auf must match (same receiving TSP)
        if (!lMessage.getPkAuf().equals(pMessage.getPkAuf())) {
            errors.add(new ValidationError(
                "PK_AUF_MISMATCH",
                "L message PK_auf: " + lMessage.getPkAuf() +
                ", P message PK_auf: " + pMessage.getPkAuf()
            ));
        }

        // Rule 4: Number ranges must match
        if (!lMessage.getNumberRangeStart().equals(pMessage.getNumberRangeStart()) ||
            !lMessage.getNumberRangeEnd().equals(pMessage.getNumberRangeEnd())) {
            errors.add(new ValidationError(
                "NUMBER_RANGE_MISMATCH",
                "L range: " + lMessage.getNumberRangeStart() + "-" + lMessage.getNumberRangeEnd() +
                ", P range: " + pMessage.getNumberRangeStart() + "-" + pMessage.getNumberRangeEnd()
            ));
        }

        // Rule 5: PK_ab ≠ PK_auf (different TSPs)
        if (lMessage.getPkAb().equals(lMessage.getPkAuf())) {
            errors.add(new ValidationError(
                "SAME_TSP_ERROR",
                "PK_ab and PK_auf cannot be the same: " + lMessage.getPkAb()
            ));
        }

        return new ValidationResult(errors.isEmpty(), errors);
    }
}
```

**2. PDA File Import Workflow:**
```java
@Service
public class PdaFileProcessor {

    @Autowired
    private PdaParser pdaParser;

    @Autowired
    private PortingOrderRepository orderRepository;

    @Autowired
    private PairedMessageMatcher messageMatcher;

    @Transactional
    public PdaProcessingResult processPdaFile(File pdaFile, String sourceTsp) {
        PdaProcessingResult result = new PdaProcessingResult();

        try {
            // Step 1: Parse PDA file
            List<PdaMessage> messages = pdaParser.parse(pdaFile);
            result.setTotalRecords(messages.size());

            // Step 2: Validate each message
            for (PdaMessage message : messages) {
                ValidationResult validation = validateMessage(message);

                if (validation.isValid()) {
                    // Create order with CHECKED state
                    PortingOrder order = createOrder(message, OrderState.CHECKED);
                    result.addValidOrder(order);
                } else {
                    // Create order with PROBLEM state
                    PortingOrder order = createOrder(message, OrderState.PROBLEM);
                    order.setValidationErrors(validation.getErrors());
                    result.addInvalidOrder(order);
                }
            }

            // Step 3: Match paired messages (L+P)
            List<PortingOrder> matchedOrders = messageMatcher.matchPairs(result.getValidOrders());
            matchedOrders.forEach(order -> {
                order.setState(OrderState.PORTED);
                orderRepository.save(order);
            });
            result.setMatchedOrders(matchedOrders.size());

            // Step 4: Identify waiting orders (single L or P)
            List<PortingOrder> waitingOrders = messageMatcher.findWaiting(result.getValidOrders());
            waitingOrders.forEach(order -> {
                order.setState(OrderState.WAITING);
                orderRepository.save(order);
            });
            result.setWaitingOrders(waitingOrders.size());

            // Step 5: Publish events to message bus
            publishProcessingEvents(result);

            return result;

        } catch (Exception ex) {
            log.error("PDA file processing failed for file: {}", pdaFile.getName(), ex);
            result.setSuccess(false);
            result.setErrorMessage(ex.getMessage());
            return result;
        }
    }

    private PortingOrder createOrder(PdaMessage message, OrderState state) {
        PortingOrder order = PortingOrder.builder()
            .callnumber(message.getNumberRangeStart())
            .onkz(extractOnkz(message.getNumberRangeStart()))
            .numberRangeStart(message.getNumberRangeStart())
            .numberRangeEnd(message.getNumberRangeEnd())
            .pkAb(message.getPkAb())
            .pkAuf(message.getPkAuf())
            .portingDate(message.getPortingDate())
            .pdaMessageType(message.getStatus())
            .orderState(state)
            .pdaFileId(message.getFileId())
            .createdAt(LocalDateTime.now())
            .build();

        return orderRepository.save(order);
    }
}
```

### FCPM - Fixed Callnumber Porting Management

#### Porting State Machine Implementation

**Complete State Model:**

| State | German | Code | Definition | Trigger | Business Logic | Timeout |
|-------|--------|------|------------|---------|----------------|---------|
| CHECKED | Integrität geprüft | CHK | PDA file validated, no syntax errors | PDA import success | Syntactic validation passed, internal order created | 24h (move to PROBLEM) |
| PROVISIONAL_IMPORT | vorläufiger Import | VI | Parallel import/booking process | CRM-T booking confirmed | Waiting for LWL implementation | 7 days (escalate) |
| WAITING | wartend | WAT | Waiting for second TSP notification | Single PDA record | Awaiting paired L or P message | 30 days (expire) |
| PORTED | Portierung abgeschlossen | PRT | Porting completed with paired records | Both L+P records matched | Final state, successful porting | - (final) |
| PROBLEM | ungültig | PRB | Invalid porting order | Various error conditions | Manual intervention required | Manual resolution |
| REJECTED | abgelehnt | REJ | Porting rejected due to problems | Manual rejection decision | Final state, failed porting | - (final) |
| CORRECTION | Korrekturmeldung | COR | Correction message triggered | Manual correction initiated | Returns to CHECKED after correction | - |

**State Transition Rules:**
```java
@Service
public class PortingStateMachine {

    public void transitionState(PortingOrder order, PortingEvent event) {
        OrderState currentState = order.getState();
        OrderState newState = null;

        switch (currentState) {
            case CHECKED:
                if (event == PortingEvent.CRM_T_CONFIRMED) {
                    newState = OrderState.PROVISIONAL_IMPORT;
                } else if (event == PortingEvent.SINGLE_MESSAGE_RECEIVED) {
                    newState = OrderState.WAITING;
                } else if (event == PortingEvent.VALIDATION_ERROR) {
                    newState = OrderState.PROBLEM;
                }
                break;

            case PROVISIONAL_IMPORT:
                if (event == PortingEvent.LWL_IMPLEMENTED) {
                    newState = OrderState.PORTED;
                    // Trigger PDA_MESSAGE_OUT with status "P"
                    triggerPdaMessageOut(order, PdaStatus.P);
                } else if (event == PortingEvent.TIMEOUT_EXCEEDED) {
                    newState = OrderState.PROBLEM;
                    escalateToManual(order, "LWL implementation timeout exceeded");
                }
                break;

            case WAITING:
                if (event == PortingEvent.PAIRED_MESSAGE_RECEIVED) {
                    // Validate paired messages
                    if (validatePairedMessage(order)) {
                        newState = OrderState.PORTED;
                    } else {
                        newState = OrderState.PROBLEM;
                    }
                } else if (event == PortingEvent.TIMEOUT_EXCEEDED) {
                    newState = OrderState.PROBLEM;
                    escalateToManual(order, "Paired message not received within 30 days");
                }
                break;

            case PROBLEM:
                if (event == PortingEvent.MANUAL_CORRECTION_INITIATED) {
                    newState = OrderState.CORRECTION;
                } else if (event == PortingEvent.MANUAL_REJECTION) {
                    newState = OrderState.REJECTED;
                }
                break;

            case CORRECTION:
                if (event == PortingEvent.CORRECTION_COMPLETED) {
                    newState = OrderState.CHECKED;
                    // Restart validation workflow
                    revalidateOrder(order);
                }
                break;

            case PORTED:
            case REJECTED:
                // Final states - no transitions allowed
                log.warn("Attempted state transition from final state {} for order {}",
                         currentState, order.getOrderId());
                return;
        }

        if (newState != null && newState != currentState) {
            // Update order state
            order.setState(newState);
            order.setUpdatedAt(LocalDateTime.now());
            orderRepository.save(order);

            // Log state transition
            auditService.logStateTransition(order, currentState, newState, event);

            // Publish state change event
            publishStateChangeEvent(order, currentState, newState);
        }
    }
}
```

#### Automated Import Workflow (LWL-triggered)

**Complete Workflow Implementation:**
```java
@Service
public class AutomatedPortingService {

    @Autowired
    private CallnumberImportService importService;

    @Autowired
    private CallnumberBookingService bookingService;

    @Autowired
    private CrmTClient crmTClient;

    @Autowired
    private LwlImplementationTracker lwlTracker;

    @Autowired
    private PdaMessageGenerator pdaGenerator;

    @Transactional
    public PortingResult handleLwlTrigger(LwlPortingNotification notification) {
        PortingResult result = new PortingResult();

        try {
            // Step 1: Parallel Processing - Import + Booking
            log.info("Starting parallel import/booking for callnumber: {}",
                     notification.getCallnumber());

            CompletableFuture<ImportResult> importFuture = CompletableFuture.supplyAsync(() ->
                importService.importCallnumber(
                    notification.getCallnumber(),
                    notification.getOnkz(),
                    notification.getSourceTsp()
                )
            );

            CompletableFuture<BookingResult> bookingFuture = CompletableFuture.supplyAsync(() ->
                bookingService.bookCallnumber(
                    notification.getCallnumber(),
                    notification.getCustomerId(),
                    notification.getContractId()
                )
            );

            // Wait for both operations to complete
            CompletableFuture.allOf(importFuture, bookingFuture).join();

            ImportResult importResult = importFuture.get();
            BookingResult bookingResult = bookingFuture.get();

            if (!importResult.isSuccess() || !bookingResult.isSuccess()) {
                throw new PortingException(
                    "Parallel processing failed: Import=" + importResult.getStatus() +
                    ", Booking=" + bookingResult.getStatus()
                );
            }

            // Step 2: CRM-T Integration - Confirm number allocation
            CrmTConfirmation confirmation = crmTClient.confirmNumberAllocation(
                notification.getCallnumber(),
                notification.getCustomerId(),
                notification.getContractId()
            );

            if (!confirmation.isConfirmed()) {
                throw new PortingException(
                    "CRM-T confirmation failed: " + confirmation.getErrorMessage()
                );
            }

            // Step 3: Status Assignment - Set "vi" (vorläufiger Import)
            Callnumber callnumber = callnumberRepository.findById(notification.getCallnumber())
                .orElseThrow(() -> new CallnumberNotFoundException(notification.getCallnumber()));

            callnumber.setState(CallnumberState.PROVISIONAL_IMPORT);
            callnumber.setProvisionalImportDate(LocalDateTime.now());
            callnumberRepository.save(callnumber);

            // Step 4: Register for LWL implementation tracking
            lwlTracker.register(
                notification.getCallnumber(),
                notification.getExpectedImplementationDate()
            );

            result.setSuccess(true);
            result.setCallnumber(notification.getCallnumber());
            result.setState(CallnumberState.PROVISIONAL_IMPORT);

            log.info("Automated import completed successfully for callnumber: {}",
                     notification.getCallnumber());

            return result;

        } catch (Exception ex) {
            log.error("Automated import failed for callnumber: {}",
                      notification.getCallnumber(), ex);
            result.setSuccess(false);
            result.setErrorMessage(ex.getMessage());
            escalateToManual(notification, ex);
            return result;
        }
    }

    @EventListener
    @Transactional
    public void handleLwlImplementation(LwlImplementationEvent event) {
        log.info("LWL implementation completed for callnumber: {}", event.getCallnumber());

        try {
            // Step 5: Update state to PORTED
            Callnumber callnumber = callnumberRepository.findById(event.getCallnumber())
                .orElseThrow(() -> new CallnumberNotFoundException(event.getCallnumber()));

            callnumber.setState(CallnumberState.ACTIVATED);
            callnumber.setActivationDate(LocalDateTime.now());
            callnumberRepository.save(callnumber);

            // Step 6: Generate PDA_MESSAGE_OUT with status "P"
            PdaMessage pdaMessage = pdaGenerator.generateMessage(
                callnumber,
                PdaStatus.P,  // Import (Übernahme)
                event.getPortingDate()
            );

            // Step 7: Distribute to all TNBs (160 TSPs)
            pdaDistributionService.distributeToAllTnbs(pdaMessage);

            // Step 8: Publish porting completed event
            publishPortingCompletedEvent(callnumber, event);

            log.info("PDA message distributed successfully for callnumber: {}",
                     event.getCallnumber());

        } catch (Exception ex) {
            log.error("LWL implementation handling failed for callnumber: {}",
                      event.getCallnumber(), ex);
            escalateToManual(event, ex);
        }
    }
}
```

#### Manual Porting Capabilities

**GUI-Driven Manual Workflow:**
```java
@RestController
@RequestMapping("/api/v1/prt/manual-porting")
public class ManualPortingController {

    @Autowired
    private ManualPortingService manualPortingService;

    @PostMapping("/import")
    @PreAuthorize("hasRole('VNRM_PRT_E')")
    public ResponseEntity<ManualPortingResult> manualImport(
            @RequestBody @Valid ManualImportRequest request) {

        // Multi-step manual import workflow
        ManualPortingResult result = manualPortingService.executeManualImport(
            request.getCallnumber(),
            request.getSourceTsp(),
            request.getTargetTsp(),
            request.getPortingDate(),
            request.getCustomerId(),
            request.getJustification(),
            request.getApprover()
        );

        return ResponseEntity.ok(result);
    }

    @PostMapping("/export")
    @PreAuthorize("hasRole('VNRM_PRT_E')")
    public ResponseEntity<ManualPortingResult> manualExport(
            @RequestBody @Valid ManualExportRequest request) {

        // Manual export with validation
        ManualPortingResult result = manualPortingService.executeManualExport(
            request.getCallnumber(),
            request.getSourceTsp(),
            request.getTargetTsp(),
            request.getPortingDate(),
            request.getJustification(),
            request.getApprover()
        );

        return ResponseEntity.ok(result);
    }
}
```

### FCPM API Specification

**RESTful Endpoints:**

**Porting Order Operations:**
```
GET    /api/v1/prt/orders                          # List all porting orders (paginated)
GET    /api/v1/prt/orders/{orderId}                # Get specific porting order
GET    /api/v1/prt/orders/by-callnumber/{cn}       # Get orders for callnumber
GET    /api/v1/prt/orders/by-state/{state}         # Filter orders by state
GET    /api/v1/prt/orders/by-tsp/{tsp}             # Filter orders by TSP
POST   /api/v1/prt/orders/search                   # Search with complex filters
GET    /api/v1/prt/orders/{orderId}/history        # Get order state transition history
PATCH  /api/v1/prt/orders/{orderId}/state          # Update order state (manual)
```

**Automated Porting Operations:**
```
POST   /api/v1/prt/automated/import                # Trigger automated import (LWL)
POST   /api/v1/prt/automated/export                # Trigger automated export
GET    /api/v1/prt/automated/status/{orderId}      # Get automated workflow status
```

**Manual Porting Operations:**
```
POST   /api/v1/prt/manual/import                   # Manual import workflow
POST   /api/v1/prt/manual/export                   # Manual export workflow
POST   /api/v1/prt/manual/correction               # Manual correction workflow
GET    /api/v1/prt/manual/pending-approval         # Get orders pending manual approval
```

**PDA Message Operations:**
```
GET    /api/v1/prt/pda/files                       # List processed PDA files
GET    /api/v1/prt/pda/files/{fileId}              # Get PDA file details
POST   /api/v1/prt/pda/validate                    # Validate PDA message format
GET    /api/v1/prt/pda/paired-messages/{cn}        # Get paired L+P messages
```

**Example Request/Response:**

**Get Porting Order:**
```bash
GET /api/v1/prt/orders/550e8400-e29b-41d4-a716-446655440000

# Response (200 OK)
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "callnumber": "03012345678",
  "onkz": "030",
  "number_range_start": "03012345678",
  "number_range_end": "03012345678",
  "pk_ab": "P001",  // Deutsche Telekom
  "pk_auf": "P002",  // Vodafone
  "porting_date": "2024-01-20",
  "pda_message_type": "L",  // Export (Abgabe)
  "order_state": "WAITING",
  "pda_file_id": "PDA_2024-01-15_001.txt",
  "paired_order_id": null,  // Waiting for P message
  "validation_errors": null,
  "created_at": "2024-01-15T10:30:45.123Z",
  "updated_at": "2024-01-15T10:30:45.123Z",
  "_links": {
    "self": {"href": "/api/v1/prt/orders/550e8400-e29b-41d4-a716-446655440000"},
    "history": {"href": "/api/v1/prt/orders/550e8400-e29b-41d4-a716-446655440000/history"},
    "paired-messages": {"href": "/api/v1/prt/pda/paired-messages/03012345678"}
  }
}
```

**Trigger Automated Import:**
```bash
POST /api/v1/prt/automated/import
Content-Type: application/json

{
  "callnumber": "03012345678",
  "onkz": "030",
  "source_tsp": "P001",
  "customer_id": "CUST-001",
  "contract_id": "CONTRACT-2024-001",
  "porting_date": "2024-01-20",
  "expected_implementation_date": "2024-01-20T08:00:00Z",
  "lwl_notification_id": "LWL-2024-0115-001"
}

# Response (202 Accepted)
{
  "order_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "callnumber": "03012345678",
  "state": "PROVISIONAL_IMPORT",
  "import_result": {
    "success": true,
    "import_timestamp": "2024-01-15T10:35:12.456Z"
  },
  "booking_result": {
    "success": true,
    "booking_id": "BOOK-2024-0115-001",
    "booking_timestamp": "2024-01-15T10:35:13.789Z"
  },
  "crm_t_confirmation": {
    "confirmed": true,
    "confirmation_id": "CRMT-2024-0115-001"
  },
  "lwl_tracking": {
    "registered": true,
    "expected_implementation": "2024-01-20T08:00:00Z"
  },
  "_links": {
    "self": {"href": "/api/v1/prt/automated/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
  }
}
```

## German Market Porting Principles

### Market Structure and TSP Coordination

**160 TSPs in Germany:**
- **BNetzA Assignment**: Each TSP receives unique Portierungskennung (PK) identifier
- **Database Maintenance**: Each TSP maintains own porting database (distributed model)
- **DTAG Approach**: Distributed model without central porting service provider
- **PDA Distribution**: Real-time message distribution to all ~160 TSPs

**Distributed vs. Central Model:**

| Aspect | DTAG Distributed Model | Central Service Model |
|--------|------------------------|----------------------|
| **Database Ownership** | Each TSP owns database | Central provider manages |
| **Autonomy** | Full carrier independence | Dependent on central service |
| **Scalability** | Horizontal, distributed scaling | Vertical, central bottleneck |
| **Failure Impact** | No single point of failure | Central service outage affects all |
| **Communication** | Direct TSP-to-TSP via PDA | Via central service |
| **Complexity** | Higher integration complexity | Simpler for individual TSPs |

**Advantages of Distributed Model:**
- **Carrier Independence**: Each TSP maintains complete control over porting database
- **Scalability**: Distributed architecture scales horizontally across 160 TSPs
- **Resilience**: No single point of failure for porting operations
- **Direct Communication**: TSP-to-TSP PDA file exchange without intermediary
- **Regulatory Compliance**: Meets BNetzA requirements for carrier autonomy

### PDA File Exchange Workflow

**TSP-to-TSP Communication:**
```
Delivering TSP (DTAG)
    ↓
Generate PDA File (L message - Export)
    ↓
Distribute to ALL 160 TSPs via SFTP
    ↓
Each TSP processes PDA file
    ↓
Receiving TSP (Vodafone)
    ↓
Generate PDA File (P message - Import)
    ↓
Distribute to ALL 160 TSPs via SFTP
    ↓
DTAG matches L+P messages
    ↓
State: PORTED (Porting completed)
```

## Integration Dependencies

### Internal VNRM Dependencies

**NUM Submodule Integration:**
- **Callnumber Validation**: NUM provides callnumber existence and availability checks before porting
- **State Synchronization**: PRT updates NUM callnumber state (ACTIVATED → PROCESSING → ACTIVATED during porting)
- **CPIN Display**: NUM CPIN service displays real-time porting information from PRT
- **Inventory Updates**: PRT notifies NUM of completed porting for number inventory updates

**COM Submodule Integration:**
- **TSP API (com-tsp-telephony-service-provider-api)**: Critical HA dependency for carrier data validation
  - TSP reference data (PK to carrier mapping)
  - Carrier contact information
  - Valid PK validation for PDA messages
- **Error Catalog (com-ecc-errorcode-catalog-api)**: Standardized PRT error codes
  - PRT-H-0042: PDA message validation failed
  - PRT-C-0003: Porting order state machine error
- **Configuration Server (com-cs-config-server-api)**: PRT service configuration
  - PDA file processing rules
  - Timeout thresholds (PROVISIONAL_IMPORT: 7 days, WAITING: 30 days)
  - LWL integration settings
- **RDM (com-rdm-reference-data-management-api)**: ONKZ and carrier reference data

**NTW Network Integration:**
- **Routing Updates**: PRT triggers network routing table updates for ported numbers
  - I-BCF routing configuration for carrier interconnects
  - B-GCF gateway updates for carrier connections
- **Service Continuity**: NTW ensures uninterrupted service during porting execution
- **Real-time Coordination**: Porting completion event triggers immediate routing updates

**COR Correction Integration:**
- **Error Management**: Failed porting operations reported to COR for business error tracking
- **Manual Correction**: COR provides manual correction workflows for PRT errors
- **Audit Trail**: Complete porting error history maintained in COR

### External System Dependencies

**LWL (Leitweglenkung) System:**
- **Purpose**: Routing (external to VNRM)
- **Integration**:
  - LWL sends porting notifications to trigger automated import
  - LWL realization messages trigger PDA_MESSAGE_OUT generation
  - Status "P" (Import) distribution to all TNBs
- **Communication**: Event-driven integration via message bus

**CRM-T (Customer Relationship Management):**
- **Purpose**: Customer data and contract management (external to VNRM)
- **Integration**:
  - Number allocation confirmation to CRM-T
  - Customer notification workflows
  - Contract status synchronization
- **Communication**: RESTful API integration with retry logic

**PDA Network (Industry-wide):**
- **Purpose**: Porting data exchange with ~160 German TSPs
- **Specification**: ITEX-PDA 20-0-3 (https://www.aknn.de/fileadmin/uploads/oeffentlich/24-06-26_ITEX-PDA_Spezifikation_PDA_20-0-3.pdf)
- **Communication**: File-based exchange via SFTP
- **Message Types**: Z (Return), L (Export), P (Import)
- **Distribution**: Real-time broadcast to all participating TSPs

**Carrier Systems (160 TSPs):**
- **Purpose**: Direct integration with other German telecommunications carriers
- **Integration**:
  - SFTP file transfer for PDA exchange
  - RESTful APIs for real-time coordination (where available)
  - Secure carrier-to-carrier communication
- **Security**: End-to-end encryption, certificate-based authentication

## Technology Stack & Implementation Details

### Backend Technologies

**Spring Boot Ecosystem:**
- **Version**: Spring Boot 2.7.x
- **Spring Data JPA**: Database access with complex queries for paired message matching
- **Spring Message Bus**: Event streaming via Tardis Horizon
- **Spring Security**: OAuth2/JWT authentication, role-based authorization
- **Spring Cloud Config**: Client for COM config-server integration
- **Spring Actuator**: Health checks, metrics, management endpoints
- **Spring Batch**: PDA file batch processing for high-volume operations

**Database:**
- **PostgreSQL 13+**: Primary relational database
- **Partitioning**: Time-based partitioning by porting_date for performance
  - Monthly partitions for porting_order table
  - Automatic partition creation for future months
- **HikariCP**: High-performance connection pooling
- **Query Optimization**: Composite indexes for paired message queries
- **Audit Tables**: Complete porting history with modification tracking

**Messaging & Events:**
- **Message Bus**: Event streaming via Tardis Horizon
- **Event Sourcing**: Complete audit trail and event replay capability
- **Schema Registry**: Avro schemas for event serialization
- **Dead Letter Queue**: Failed message handling for PDA processing errors

### Integration Technologies

**PDA File Processing:**
- **File Format**: Structured text format per ITEX-PDA 20-0-3 specification
- **SFTP**: Secure file transfer for carrier communication
- **Parsing**: Custom PDA parser with multi-layered validation
- **Validation Layers**:
  1. Syntax validation (file format compliance)
  2. Business rule validation (paired messages, date validation)
  3. Regulatory compliance validation (BNetzA requirements)
- **Error Handling**: Automatic retry with exponential backoff, dead letter queue for persistent failures

**API Integration:**
- **RESTful APIs**: Internal VNRM service communication
- **OpenAPI 3.0**: API specification and documentation
- **Circuit Breakers**: Resilience4j for external system failures
- **Retry Logic**: Configurable retry policies for transient failures

## Advanced Integration Patterns

### Event-Driven Porting Coordination

**Porting Lifecycle Events:**
```java
// PRT publishes porting events
@Service
public class PortingEventPublisher {

    @Autowired
    private Message BusTemplate<String, PortingEvent> message_busTemplate;

    public void publishPortingCompleted(PortingOrder order) {
        PortingEvent event = PortingEvent.builder()
            .eventType(EventType.PORTING_COMPLETED)
            .orderId(order.getOrderId())
            .callnumber(order.getCallnumber())
            .onkz(order.getOnkz())
            .pkOld(order.getPkAb())
            .pkNew(order.getPkAuf())
            .portingDate(order.getPortingDate())
            .state(PortingState.COMPLETED)
            .timestamp(LocalDateTime.now())
            .correlationId(MDC.get("correlationId"))
            .build();

        // Publish to Message Bus topic for consumption by NUM, NTW, COR
        message_busTemplate.send("vnrm.prt.porting-completed",
                          order.getCallnumber(),
                          event);

        log.info("Published porting completed event for callnumber: {}",
                 order.getCallnumber());
    }
}

// NUM consumes porting events
@Service
public class NumPortingEventConsumer {

    @Message BusListener(topics = "vnrm.prt.porting-completed")
    public void handlePortingCompleted(PortingEvent event) {
        log.info("Received porting completed event for callnumber: {}",
                 event.getCallnumber());

        // Update callnumber state in NUM
        Callnumber cn = callnumberRepository.findById(event.getCallnumber())
            .orElseThrow(() -> new CallnumberNotFoundException(event.getCallnumber()));

        cn.setState(CallnumberState.ACTIVATED);
        cn.setPortingDate(event.getPortingDate());
        cn.setCurrentTsp(event.getPkNew());
        callnumberRepository.save(cn);

        // Log modification
        modificationService.logPortingCompleted(cn, event);

        log.info("Updated NUM callnumber state to ACTIVATED for: {}",
                 event.getCallnumber());
    }
}

// NTW consumes porting events for routing updates
@Service
public class NtwPortingEventConsumer {

    @Autowired
    private IBcfIntegrationService ibcfService;

    @Message BusListener(topics = "vnrm.prt.porting-completed")
    public void handlePortingCompleted(PortingEvent event) {
        log.info("Triggering network routing update for ported callnumber: {}",
                 event.getCallnumber());

        // Update I-BCF routing tables
        ibcfService.updateRoutingForPortedNumber(
            event.getCallnumber(),
            event.getPkOld(),  // From TSP
            event.getPkNew()   // To TSP
        );

        log.info("Network routing updated for ported callnumber: {}",
                 event.getCallnumber());
    }
}
```

### Paired Message Matching Algorithm

**Complex Matching Logic:**
```java
@Service
public class PairedMessageMatcher {

    @Autowired
    private PortingOrderRepository orderRepository;

    public List<PortingOrder> matchPairs(List<PortingOrder> orders) {
        List<PortingOrder> matchedOrders = new ArrayList<>();

        // Group orders by callnumber for efficient matching
        Map<String, List<PortingOrder>> groupedOrders = orders.stream()
            .collect(Collectors.groupingBy(PortingOrder::getCallnumber));

        groupedOrders.forEach((callnumber, orderList) -> {
            // Find L message (Export)
            PortingOrder lOrder = orderList.stream()
                .filter(o -> "L".equals(o.getPdaMessageType()))
                .findFirst()
                .orElse(null);

            // Find P message (Import)
            PortingOrder pOrder = orderList.stream()
                .filter(o -> "P".equals(o.getPdaMessageType()))
                .findFirst()
                .orElse(null);

            if (lOrder != null && pOrder != null) {
                // Validate paired messages
                if (isPairedMessageValid(lOrder, pOrder)) {
                    // Link paired orders
                    lOrder.setPairedOrderId(pOrder.getOrderId());
                    pOrder.setPairedOrderId(lOrder.getOrderId());

                    // Update state to PORTED
                    lOrder.setState(OrderState.PORTED);
                    pOrder.setState(OrderState.PORTED);

                    orderRepository.save(lOrder);
                    orderRepository.save(pOrder);

                    matchedOrders.add(lOrder);
                    matchedOrders.add(pOrder);

                    log.info("Matched L+P messages for callnumber: {}", callnumber);
                }
            }
        });

        return matchedOrders;
    }

    private boolean isPairedMessageValid(PortingOrder lOrder, PortingOrder pOrder) {
        // Comprehensive validation of paired messages
        return lOrder.getPortingDate().equals(pOrder.getPortingDate())
            && lOrder.getPkAb().equals(pOrder.getPkAb())
            && lOrder.getPkAuf().equals(pOrder.getPkAuf())
            && lOrder.getNumberRangeStart().equals(pOrder.getNumberRangeStart())
            && lOrder.getNumberRangeEnd().equals(pOrder.getNumberRangeEnd())
            && !lOrder.getPkAb().equals(lOrder.getPkAuf());  // Different TSPs
    }

    public List<PortingOrder> findWaiting(List<PortingOrder> orders) {
        List<PortingOrder> waitingOrders = new ArrayList<>();

        Map<String, List<PortingOrder>> groupedOrders = orders.stream()
            .collect(Collectors.groupingBy(PortingOrder::getCallnumber));

        groupedOrders.forEach((callnumber, orderList) -> {
            // If only L or only P message exists (not paired)
            if (orderList.size() == 1) {
                PortingOrder singleOrder = orderList.get(0);
                singleOrder.setState(OrderState.WAITING);
                orderRepository.save(singleOrder);
                waitingOrders.add(singleOrder);

                log.info("Single {} message waiting for pair: callnumber={}",
                         singleOrder.getPdaMessageType(), callnumber);
            }
        });

        return waitingOrders;
    }
}
```

## BNetzA Regulatory Compliance

### Compliance Requirements Implementation

**Porting Timeline Monitoring:**
```java
@Service
@Slf4j
public class PortingTimelineMonitor {

    @Autowired
    private PortingOrderRepository orderRepository;

    @Autowired
    private AlertService alertService;

    @Scheduled(cron = "0 0 * * * *")  // Every hour
    public void monitorPortingTimelines() {
        // BNetzA requirement: Maximum porting duration compliance
        LocalDate today = LocalDate.now();

        // Find orders exceeding timeline thresholds
        List<PortingOrder> overdueProvisional = orderRepository
            .findByStateAndCreatedAtBefore(
                OrderState.PROVISIONAL_IMPORT,
                today.minusDays(7)
            );

        List<PortingOrder> overdueWaiting = orderRepository
            .findByStateAndCreatedAtBefore(
                OrderState.WAITING,
                today.minusDays(30)
            );

        // Alert on overdue orders
        if (!overdueProvisional.isEmpty()) {
            alertService.sendAlert(
                AlertType.PORTING_TIMELINE_EXCEEDED,
                "Provisional import orders exceeding 7-day threshold: " +
                overdueProvisional.size()
            );
        }

        if (!overdueWaiting.isEmpty()) {
            alertService.sendAlert(
                AlertType.PORTING_TIMELINE_EXCEEDED,
                "Waiting orders exceeding 30-day threshold: " +
                overdueWaiting.size()
            );
        }

        log.info("Porting timeline monitoring completed: " +
                 "Overdue PROVISIONAL_IMPORT={}, Overdue WAITING={}",
                 overdueProvisional.size(), overdueWaiting.size());
    }
}
```

**Data Protection (GDPR Compliance):**
- **Encryption**: All PDA messages encrypted in transit (TLS 1.3) and at rest (PostgreSQL encryption)
- **Access Control**: Role-based access (VNRM_PRT_E for porting operations)
- **Audit Logging**: Complete audit trail of all porting operations and data access
- **Data Retention**: Automatic deletion of personal data after regulatory retention period (10 years)
- **Customer Rights**: Support for GDPR rights (access, rectification, erasure, data portability)

**Quality Standards Monitoring:**
```java
@Service
public class PortingQualityMonitor {

    @Autowired
    private PortingOrderRepository orderRepository;

    @Autowired
    private MeterRegistry meterRegistry;

    @Scheduled(fixedRate = 300000)  // Every 5 minutes
    public void collectQualityMetrics() {
        // Porting success rate
        long totalOrders = orderRepository.countByCreatedAtAfter(
            LocalDateTime.now().minusDays(1)
        );
        long completedOrders = orderRepository.countByStateAndCreatedAtAfter(
            OrderState.PORTED,
            LocalDateTime.now().minusDays(1)
        );
        long failedOrders = orderRepository.countByStateAndCreatedAtAfter(
            OrderState.REJECTED,
            LocalDateTime.now().minusDays(1)
        );

        double successRate = totalOrders > 0
            ? (double) completedOrders / totalOrders * 100
            : 0;

        // Update Prometheus metrics
        meterRegistry.gauge("prt_porting_success_rate", successRate);
        meterRegistry.gauge("prt_porting_total", totalOrders);
        meterRegistry.gauge("prt_porting_completed", completedOrders);
        meterRegistry.gauge("prt_porting_failed", failedOrders);

        log.info("Porting quality metrics: Total={}, Completed={}, Failed={}, Success Rate={}%",
                 totalOrders, completedOrders, failedOrders, successRate);
    }
}
```

### Industry Integration and Dispute Resolution

**TNB Coordination (160 TSPs):**
- **Complete Coverage**: Support for all ~160 German telecommunications service providers
- **PDA Distribution**: Real-time broadcast of porting messages to all participating TSPs
- **Carrier Validation**: Validate PK (Portierungskennung) against BNetzA-registered carriers
- **Dispute Mechanisms**: Integration with industry dispute resolution workflows via FCCM

**Clearing Process (FCCM):**
```java
@Service
public class PortingClearingService {

    @Autowired
    private EmailService emailService;

    @Autowired
    private ClearingRequestRepository clearingRepository;

    public ClearingRequest initiateClearingProcess(PortingOrder order, String reason) {
        // Create clearing request
        ClearingRequest clearing = ClearingRequest.builder()
            .orderId(order.getOrderId())
            .callnumber(order.getCallnumber())
            .sourceTsp(order.getPkAb())
            .targetTsp(order.getPkAuf())
            .reason(reason)
            .status(ClearingStatus.INITIATED)
            .createdAt(LocalDateTime.now())
            .build();

        clearingRepository.save(clearing);

        // Send clearing email to involved TSPs
        emailService.sendClearingNotification(
            order.getPkAb(),
            order.getPkAuf(),
            clearing
        );

        log.info("Initiated clearing process for porting order: {} (callnumber: {})",
                 order.getOrderId(), order.getCallnumber());

        return clearing;
    }
}
```

## Performance Optimization & Scalability

### High-Volume PDA Processing

**Batch Processing Architecture:**
```java
@Configuration
@EnableBatchProcessing
public class PdaBatchConfiguration {

    @Bean
    public Job pdaFileProcessingJob(JobBuilderFactory jobBuilderFactory,
                                     Step pdaProcessingStep) {
        return jobBuilderFactory.get("pdaFileProcessingJob")
            .incrementer(new RunIdIncrementer())
            .flow(pdaProcessingStep)
            .end()
            .build();
    }

    @Bean
    public Step pdaProcessingStep(StepBuilderFactory stepBuilderFactory,
                                   ItemReader<PdaMessage> reader,
                                   ItemProcessor<PdaMessage, PortingOrder> processor,
                                   ItemWriter<PortingOrder> writer) {
        return stepBuilderFactory.get("pdaProcessingStep")
            .<PdaMessage, PortingOrder>chunk(100)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            .retry(TransientDataAccessException.class)
            .retryLimit(3)
            .build();
    }
}
```

**Database Performance Optimization:**
- **Partitioning**: Monthly partitions by porting_date for porting_order table
- **Indexing Strategy**: Composite indexes for paired message queries
  - `idx_paired_messages` on `(callnumber, pda_message_type, porting_date)`
  - `idx_state_date` on `(order_state, porting_date)`
- **Query Optimization**: Prepared statements and query plan analysis
- **Connection Pooling**: HikariCP with optimized settings for high concurrency

**Caching Strategy:**
```java
@Configuration
@EnableCaching
public class PrtCacheConfiguration {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .disableCachingNullValues();

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .withCacheConfiguration("tsp-data",
                config.entryTtl(Duration.ofHours(24)))
            .withCacheConfiguration("onkz-data",
                config.entryTtl(Duration.ofHours(24)))
            .build();
    }
}

@Service
public class TspService {

    @Cacheable(value = "tsp-data", key = "#pk")
    public Tsp getTspByPk(String pk) {
        return tspRepository.findByPk(pk)
            .orElseThrow(() -> new TspNotFoundException(pk));
    }
}
```

## Monitoring & Metrics

### Prometheus Metrics

```yaml
# Porting order metrics
prt_porting_orders_total{state, tsp_source, tsp_target}
prt_porting_orders_created_total{message_type}
prt_porting_orders_completed_total{tsp_source, tsp_target}
prt_porting_duration_seconds{state}
prt_porting_success_rate

# PDA file processing metrics
prt_pda_files_processed_total{source_tsp}
prt_pda_messages_total{message_type}
prt_pda_validation_errors_total{error_type}
prt_pda_processing_duration_seconds

# Paired message metrics
prt_paired_messages_matched_total
prt_paired_messages_waiting_total
prt_paired_messages_timeout_total

# LWL integration metrics
prt_lwl_triggers_total
prt_lwl_implementation_duration_seconds
prt_lwl_failures_total

# State machine metrics
prt_state_transitions_total{from_state, to_state}
prt_state_duration_seconds{state}
```

### Operational Dashboards

**Dashboard 1: Porting Overview**
- Total active porting orders (gauge)
- Porting orders by state (pie chart)
- Porting success rate (gauge with threshold alerts)
- Porting volume over time (time series)
- Top 10 TSP pairs by porting volume (bar chart)

**Dashboard 2: PDA Processing**
- PDA files processed per hour (time series)
- PDA validation error rate (gauge)
- Paired message matching rate (gauge)
- L+P message waiting duration (histogram)
- PDA processing duration distribution (heatmap)

**Dashboard 3: SLA Compliance**
- Porting timeline compliance (gauge with BNetzA threshold)
- Orders exceeding timeline thresholds (table)
- Average porting duration by TSP pair (bar chart)
- Manual intervention rate (gauge)

## Best Practices

### PDA Message Processing
1. **Strict ITEX-PDA compliance** - Follow specification exactly (version 20-0-3)
2. **Validate paired messages** - L+P records must match on date, PK_ab, PK_auf, number range
3. **Handle all 160 TSPs** - Complete German carrier ecosystem support
4. **Implement retry logic** - Exponential backoff for transient failures
5. **Log all PDA operations** - Complete audit trail for regulatory compliance
6. **Monitor paired message timeouts** - Alert on WAITING state exceeding 30 days

### Porting Workflow Management
1. **Automate where possible** - Reduce manual intervention for standard porting scenarios
2. **Support manual override** - Complex scenarios require human decision-making
3. **Monitor state transitions** - Track all porting state changes with timestamps
4. **Alert on anomalies** - Proactive error detection for failed automatic workflows
5. **Maintain event history** - Event sourcing for replay and audit
6. **Implement rollback procedures** - Compensating actions for failed porting attempts

### Integration Patterns
1. **Event-driven communication** - Use Message Bus message bus for cross-service coordination
2. **Asynchronous processing** - Non-blocking porting workflows for high volume
3. **Circuit breakers** - Handle external system failures (LWL, CRM-T) gracefully
4. **Idempotent operations** - Support message replay without side effects
5. **Complete correlation IDs** - End-to-end request tracking across VNRM services
6. **Cache TSP reference data** - Reduce latency for carrier lookups

### Operational Excellence
1. **BNetzA timeline compliance** - Monitor maximum porting duration requirements
2. **Quality metrics tracking** - Measure porting success rate, duration, error rate
3. **Regular TSP coordination** - Maintain communication with all ~160 carriers
4. **Disaster recovery procedures** - Regular backups, tested recovery processes
5. **Capacity planning** - Project future porting volumes based on historical trends
6. **Security audits** - Regular security assessments for PDA message encryption

---

**See also:**
- [NUM Architecture Reference](../vnrm-num-architecture/REFERENCE.md) - Number Management Integration
- [COM Architecture Reference](../vnrm-com-architecture/REFERENCE.md) - TSP API and Configuration
- [NTW Architecture Reference](../vnrm-ntw-architecture/REFERENCE.md) - Network Routing Updates
- [COR Architecture Reference](../vnrm-cor-architecture/REFERENCE.md) - Error Correction Integration
