# VNRM COR (CORRECTION) Architecture Reference

## Overview

The VNRM COR (CORRECTION) submodule provides business error management capabilities through a minimal set of services focused on tracking, analyzing, and resolving business logic errors across all VNRM services. Unlike comprehensive correction systems, COR focuses specifically on business error management rather than data correction or system-wide issue resolution.

COR serves as the central hub for managing business errors that occur during VNRM operations, providing visibility into error patterns, facilitating root cause analysis, and enabling systematic resolution of business logic failures. The service integrates with COM's error catalog to ensure standardized error reporting across the entire VNRM ecosystem.

## Current Deployment Status & Limitations

### Production Deployment Status

**Technical Status:**
- **Deployment**: Deployed to production environment
- **Business Release**: "Technisch in Prod, aber fachlich noch nicht freigegeben"
- **Operational State**: Technically operational but not yet released for full business use
- **Support Level**: Office Time (OT) - 3-day response, business hours only
- **Availability**: No on-call duty required

**Current Scope:**
- **Focus**: Essential business error management only
- **Limitations**: Minimal feature set in current release
- **Functionality**: Order-based error tracking and resolution workflows
- **Integration**: Limited to critical VNRM service integrations

### Future Development Path

**Evolution Strategy:**
- **Phase 1 (Current)**: Core business error management functionality
- **Phase 2 (Planned)**: Expanded analytics and reporting capabilities
- **Phase 3 (Planned)**: Advanced root cause analysis and automated resolution
- **Business Release**: Pending operational validation and business approval

**Known Limitations:**
1. **Limited Automation**: Manual error resolution workflows only
2. **Basic Analytics**: Simple reporting, no advanced ML-based pattern detection
3. **OT Support Only**: Not suitable for critical real-time error handling
4. **Minimal GUI Features**: Essential functionality only, no advanced visualizations
5. **Integration Scope**: Limited to key VNRM services (NUM, PRT, COM, SPE)

## Deployed Microservices

### BEM - Business Error Management

| Service | Version | SLA Level | Purpose | Status |
|---------|---------|-----------|---------|--------|
| cor-bem-business-error-management-api | - | OT | Business error management API | Deployed (not business-released) |
| cor-bem-business-error-management-gui | - | OT | Error management GUI | Deployed (not business-released) |

**Service Level Details:**
- **Response Time**: 3 days
- **Availability**: Business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Impact**: Limited to business error management operations

**Technical Stack:**
- **Backend**: Spring Boot 2.7.x, RESTful API
- **Frontend**: Angular 14+, Angular Material
- **Database**: PostgreSQL 13+
- **Messaging**: Spring Message Bus for event-driven error notifications
- **Security**: OAuth2/OpenID Connect via Tardis/Iris

## Error Classification System

### Business Error Categories

**1. Data Validation Errors**
- Business rule validation failures
- Invalid data formats or values
- Constraint violations (e.g., ONKZ validation, number range checks)
- Reference data inconsistencies (TSP data, ONKZ data)
- Regulatory data validation failures (BNetzA requirements)

**Examples:**
- Invalid callnumber format (missing ONKZ)
- Non-existent TSP reference in porting request
- Number block outside allowed range

**2. Process Workflow Errors**
- Business process execution failures
- Workflow state violations (e.g., invalid state transitions)
- Process timeout errors (e.g., porting deadline violations)
- Incomplete workflow executions (missing mandatory steps)
- State machine errors (callnumber state, porting state)

**Examples:**
- Callnumber reservation timeout after 24 hours
- Porting order in invalid state for operation
- Missing mandatory PDA message field

**3. Integration Errors**
- Cross-service communication failures (NUM ↔ PRT, NUM ↔ COM)
- API call failures (timeout, connection errors)
- Message bus errors (Message Bus consumer failures)
- External system integration issues (RNVS sync, BNetzA API)
- Data synchronization failures

**Examples:**
- NUM service unreachable during PRT porting operation
- RNVS synchronization failure for reference data
- BNetzA API timeout during block validation

**4. Regulatory Compliance Errors**
- BNetzA requirement violations (porting timeline compliance)
- GDPR compliance issues (data retention, privacy)
- Telecommunications regulation breaches (ITEX-PDA specification)
- Audit requirement failures (missing audit trail)
- Data protection violations

**Examples:**
- Porting exceeded maximum allowed duration
- Missing customer consent for data processing
- PDA message non-compliant with ITEX-PDA 20-0-3

## Error Management Workflow

### Order-Based Error Tracking

**Workflow Stages:**

```
1. Error Detection (Automated)
   ↓
2. Order Creation (Error Management Order)
   ↓
3. Assignment (to Analyst/Resolver)
   ↓
4. Analysis Interface (Single Order View)
   ↓
5. Root Cause Investigation
   ↓
6. Resolution Actions (Manual/Retry)
   ↓
7. Completion Verification
   ↓
8. Audit Trail Logging & Closure
```

### Error Management Order Lifecycle

**Order States:**

| State | Description | Available Actions | Next States |
|-------|-------------|-------------------|-------------|
| **CREATED** | Error detected, order created | Assign, Analyze | ASSIGNED |
| **ASSIGNED** | Order assigned to analyst/resolver | Start Analysis, Reassign | IN_ANALYSIS, ASSIGNED |
| **IN_ANALYSIS** | Root cause analysis in progress | Document Findings, Escalate | PENDING_RESOLUTION, ESCALATED |
| **ESCALATED** | Escalated to development team | Resolve, Update | PENDING_RESOLUTION |
| **PENDING_RESOLUTION** | Awaiting resolution action | Apply Fix, Retry, Document | RESOLVED, FAILED |
| **RESOLVED** | Resolution action completed | Verify | VERIFIED, PENDING_RESOLUTION |
| **VERIFIED** | Resolution verified successful | Close | CLOSED |
| **CLOSED** | Order closed with complete audit trail | Reopen (if needed) | IN_ANALYSIS |

**State Transition Rules:**
- Orders cannot skip states (e.g., CREATED → RESOLVED)
- CLOSED orders can be reopened if error recurs
- ESCALATED orders require development team approval to resolve
- All state transitions logged with timestamp and user

### Error Detection and Reporting

**Automated Error Detection:**
```java
// Example: NUM service detects reservation failure
try {
    callnumberService.reserve(callnumber);
} catch (ReservationException ex) {
    // Automatically create error management order
    corErrorReportingClient.reportError(
        ErrorReport.builder()
            .errorCode("NUM-C-0001")
            .service("NUM")
            .operation("RESERVE")
            .context(Map.of(
                "callnumber", callnumber,
                "onkz", onkz,
                "customerId", customerId
            ))
            .exception(ex)
            .build()
    );
}
```

## GUI Architecture

### Order View (List Interface)

**Features:**
- **Error List Display**: Comprehensive listing of all business error orders
- **Filter Capabilities**:
  - By error category (validation, workflow, integration, compliance)
  - By service (NUM, PRT, COM, SPE, NTW)
  - By status (created, assigned, in_analysis, pending_resolution, etc.)
  - By priority (critical, high, medium, low)
  - By date range (created date, updated date)
  - By assigned analyst
  - By error code (from COM catalog)
- **Status Tracking**: Real-time status updates via WebSocket
- **Priority Management**: Color-coded priority indicators (red=critical, orange=high, yellow=medium, green=low)
- **Bulk Operations**:
  - Batch assign to analyst
  - Batch status update
  - Batch export to CSV
  - Batch close (for verified orders)
- **Sorting**: By any column (order ID, created date, priority, status)
- **Pagination**: 25/50/100 orders per page

**Columns:**

| Column | Width | Description | Sortable |
|--------|-------|-------------|----------|
| Order ID | 120px | UUID (shortened display) | Yes |
| Error Code | 100px | COM error catalog code | Yes |
| Service | 80px | NUM/PRT/COM/SPE/NTW | Yes |
| Category | 120px | Validation/Workflow/Integration/Compliance | Yes |
| Status | 100px | Current order state | Yes |
| Priority | 80px | Critical/High/Medium/Low | Yes |
| Created Date | 140px | ISO8601 format | Yes |
| Assigned To | 150px | Analyst username | Yes |
| Last Updated | 140px | Last activity timestamp | Yes |

**Color Coding:**
- **Critical Priority**: Red background, white text
- **High Priority**: Orange background, white text
- **Medium Priority**: Yellow background, black text
- **Low Priority**: Green background, white text

### Single Order Analysis View

**Detailed Error Information:**

**Order Header:**
- Order ID (full UUID)
- Status badge with color
- Priority indicator
- Created date and time
- Last updated timestamp
- Assigned analyst with avatar
- Estimated resolution time

**Error Context:**
- **Error Code and Description**: Retrieved from COM error catalog
  - Error code (e.g., NUM-C-0001)
  - Error title (German and English)
  - Error description (German and English)
  - Recommended resolution actions
- **Service Information**:
  - Service that reported the error (NUM/PRT/COM/SPE/NTW)
  - Service version
  - Service instance ID
- **Timing**:
  - Error occurrence timestamp
  - Correlation ID (for distributed tracing)
  - Request ID
- **User/System Context**:
  - User who triggered the error (if applicable)
  - Customer ID (if applicable)
  - System component that detected error

**Technical Details:**
- **Stack Trace**: Full exception stack trace (if applicable)
- **Request/Response Data**:
  - HTTP request details (method, path, headers)
  - Request payload (JSON)
  - Response payload (JSON)
- **System State**:
  - Database state at time of error
  - Related entity IDs (callnumber, porting order, etc.)
  - Configuration values affecting operation
- **Related Logs and Events**:
  - Application logs from 1 minute before/after error
  - Message Bus events related to operation
  - Database audit logs

**Root Cause Analysis Tools:**
- **Timeline View**:
  - Chronological sequence of events leading to error
  - Service calls visualization
  - State transitions diagram
- **Dependency Analysis**:
  - Affected services and their health status
  - Impacted data entities
  - Downstream effects on other operations
- **Similar Errors**:
  - Historical errors with same error code
  - Errors with similar patterns
  - Resolution success rate for similar errors
- **Impact Assessment**:
  - Number of users affected
  - Operations blocked
  - Business process impact
  - SLA compliance impact

**Resolution Actions:**
- **Manual Corrections**:
  - GUI-driven data corrections
  - Direct database updates (with approval)
  - Reference data corrections
- **Process Retry**:
  - Retry failed workflow steps
  - Resume interrupted processes
  - Replay Message Bus messages
- **Escalation**:
  - Escalate to development team
  - Create JIRA ticket automatically
  - Schedule hotfix deployment
- **Documentation**:
  - Add root cause analysis notes
  - Document resolution steps
  - Link to knowledge base articles
- **Communication**:
  - Notify affected users via email
  - Update external systems (ServiceNow)
  - Publish status to monitoring dashboards

**History Tracking:**
- Complete audit trail of all activities
- Who did what and when (user, timestamp, action)
- Before/after states for all changes
- Resolution effectiveness metrics
- Comments and notes from analysts

### Navigation Map

**Hierarchical Navigation:**
```
COR Dashboard
├── Order View (All Errors)
│   ├── Filter: By Service (NUM/PRT/COM/SPE/NTW)
│   ├── Filter: By Category (Validation/Workflow/Integration/Compliance)
│   ├── Filter: By Status (Created/Assigned/In Analysis/etc.)
│   ├── Filter: By Priority (Critical/High/Medium/Low)
│   ├── Filter: By Date Range
│   └── Filter: By Assigned Analyst
│
├── Single Order Analysis
│   ├── Error Details
│   │   ├── Order Header
│   │   ├── Error Context
│   │   └── Technical Details
│   ├── Root Cause Analysis
│   │   ├── Timeline View
│   │   ├── Dependency Analysis
│   │   ├── Similar Errors
│   │   └── Impact Assessment
│   ├── Resolution Actions
│   │   ├── Manual Corrections
│   │   ├── Process Retry
│   │   ├── Escalation
│   │   └── Documentation
│   └── Audit Trail
│       ├── Activity History
│       ├── State Transitions
│       └── Resolution Metrics
│
├── Reports & Analytics
│   ├── Error Trends
│   │   ├── Error volume by service
│   │   ├── Error volume by category
│   │   └── Error volume over time
│   ├── Service Health
│   │   ├── Error rate per service
│   │   ├── Mean time to resolution
│   │   └── SLA compliance
│   ├── Resolution Metrics
│   │   ├── Analyst performance
│   │   ├── Resolution effectiveness
│   │   └── Recurring error patterns
│   └── Compliance Reports
│       ├── BNetzA compliance violations
│       ├── GDPR incident reports
│       └── Audit trail exports
│
└── Administration
    ├── User Management
    │   ├── Analyst assignments
    │   └── Role management
    ├── Category Configuration
    │   ├── Error category mappings
    │   └── Priority rules
    └── Integration Settings
        ├── COM catalog connection
        ├── Service endpoints
        └── Notification settings
```

## API Specification

### BEM REST API

**Base URL:** `/api/v1/cor/errors`

**Error Order Operations:**

```
# List all error orders with filtering
GET    /api/v1/cor/errors/orders?service=NUM&status=CREATED&priority=CRITICAL

# Get specific error order
GET    /api/v1/cor/errors/orders/{orderId}

# Create new error order (called by VNRM services)
POST   /api/v1/cor/errors/orders

# Update error order status
PATCH  /api/v1/cor/errors/orders/{orderId}/status

# Assign order to analyst
PATCH  /api/v1/cor/errors/orders/{orderId}/assign

# Add resolution notes
POST   /api/v1/cor/errors/orders/{orderId}/notes

# Get order history
GET    /api/v1/cor/errors/orders/{orderId}/history

# Filter by service
GET    /api/v1/cor/errors/orders/by-service/{service}

# Filter by category
GET    /api/v1/cor/errors/orders/by-category/{category}

# Get error statistics
GET    /api/v1/cor/errors/statistics

# Export orders to CSV
GET    /api/v1/cor/errors/orders/export?format=csv
```

**Request/Response Examples:**

**Create Error Order:**
```bash
POST /api/v1/cor/errors/orders
Content-Type: application/json

{
  "errorCode": "NUM-C-0001",
  "service": "NUM",
  "category": "WORKFLOW",
  "priority": "HIGH",
  "context": {
    "callnumber": "03012345678",
    "operation": "RESERVE",
    "customerId": "CUST-001",
    "onkz": "030"
  },
  "exception": {
    "message": "Database constraint violation",
    "stackTrace": "..."
  }
}

# Response
{
  "orderId": "550e8400-e29b-41d4-a716-446655440000",
  "errorCode": "NUM-C-0001",
  "errorTitle": "Call number reservation failed",
  "service": "NUM",
  "category": "WORKFLOW",
  "status": "CREATED",
  "priority": "HIGH",
  "createdAt": "2024-01-15T10:30:45.123Z",
  "assignedTo": null
}
```

**Update Order Status:**
```bash
PATCH /api/v1/cor/errors/orders/550e8400-e29b-41d4-a716-446655440000/status
Content-Type: application/json

{
  "status": "RESOLVED",
  "resolutionNotes": "Manually corrected data constraint violation",
  "resolvedBy": "analyst@telekom.de"
}

# Response
{
  "orderId": "550e8400-e29b-41d4-a716-446655440000",
  "previousStatus": "PENDING_RESOLUTION",
  "newStatus": "RESOLVED",
  "updatedAt": "2024-01-15T11:45:30.456Z",
  "updatedBy": "analyst@telekom.de"
}
```

**Get Error Statistics:**
```bash
GET /api/v1/cor/errors/statistics?service=NUM&dateFrom=2024-01-01&dateTo=2024-01-31

# Response
{
  "service": "NUM",
  "period": {
    "from": "2024-01-01",
    "to": "2024-01-31"
  },
  "totalErrors": 245,
  "byCategory": {
    "VALIDATION": 120,
    "WORKFLOW": 80,
    "INTEGRATION": 35,
    "COMPLIANCE": 10
  },
  "byPriority": {
    "CRITICAL": 15,
    "HIGH": 60,
    "MEDIUM": 120,
    "LOW": 50
  },
  "byStatus": {
    "CREATED": 5,
    "ASSIGNED": 10,
    "IN_ANALYSIS": 15,
    "PENDING_RESOLUTION": 8,
    "RESOLVED": 180,
    "VERIFIED": 150,
    "CLOSED": 142
  },
  "meanResolutionTime": "4.5 hours",
  "slaCompliance": "92%"
}
```

## Database Schema

### Error Management Order Table

```sql
CREATE TABLE vnrm_cor.error_management_order (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  error_code VARCHAR(20) NOT NULL,
  error_title VARCHAR(200) NOT NULL,
  error_description TEXT,
  service VARCHAR(10) NOT NULL CHECK (service IN ('NUM', 'PRT', 'COM', 'SPE', 'NTW', 'COR')),
  category VARCHAR(50) NOT NULL CHECK (category IN ('VALIDATION', 'WORKFLOW', 'INTEGRATION', 'COMPLIANCE')),
  status VARCHAR(20) NOT NULL CHECK (status IN ('CREATED', 'ASSIGNED', 'IN_ANALYSIS', 'ESCALATED', 'PENDING_RESOLUTION', 'RESOLVED', 'VERIFIED', 'CLOSED')),
  priority VARCHAR(10) NOT NULL CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
  context JSONB NOT NULL,
  exception_details TEXT,
  stack_trace TEXT,
  correlation_id VARCHAR(100),
  request_id VARCHAR(100),
  assigned_to VARCHAR(100),
  assigned_at TIMESTAMP,
  resolution_notes TEXT,
  resolved_by VARCHAR(100),
  resolved_at TIMESTAMP,
  verified_by VARCHAR(100),
  verified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(100) DEFAULT 'system',
  updated_by VARCHAR(100),
  CONSTRAINT fk_error_code FOREIGN KEY (error_code)
    REFERENCES vnrm_ecc.error_catalog(error_code)
);

-- Indexes for common queries
CREATE INDEX idx_error_order_status ON vnrm_cor.error_management_order(status);
CREATE INDEX idx_error_order_service ON vnrm_cor.error_management_order(service);
CREATE INDEX idx_error_order_priority ON vnrm_cor.error_management_order(priority);
CREATE INDEX idx_error_order_category ON vnrm_cor.error_management_order(category);
CREATE INDEX idx_error_order_created ON vnrm_cor.error_management_order(created_at DESC);
CREATE INDEX idx_error_order_assigned ON vnrm_cor.error_management_order(assigned_to);
CREATE INDEX idx_error_order_correlation ON vnrm_cor.error_management_order(correlation_id);

-- Example data
INSERT INTO vnrm_cor.error_management_order VALUES
  (gen_random_uuid(), 'NUM-C-0001', 'Call number reservation failed',
   'Call number reservation failed due to a system error.',
   'NUM', 'WORKFLOW', 'CREATED', 'HIGH',
   '{"callnumber": "03012345678", "operation": "RESERVE", "customerId": "CUST-001"}'::jsonb,
   'Database constraint violation', 'at com.telekom.vnrm.num...',
   'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'REQ-2024-0115-001',
   NULL, NULL, NULL, NULL, NULL, NULL, NULL,
   CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'system', NULL);
```

### Order History Table (Audit Trail)

```sql
CREATE TABLE vnrm_cor.error_order_history (
  history_id BIGSERIAL PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES vnrm_cor.error_management_order(order_id),
  action VARCHAR(50) NOT NULL,
  previous_status VARCHAR(20),
  new_status VARCHAR(20),
  notes TEXT,
  performed_by VARCHAR(100) NOT NULL,
  performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for order history lookups
CREATE INDEX idx_order_history_order_id ON vnrm_cor.error_order_history(order_id);
CREATE INDEX idx_order_history_performed_at ON vnrm_cor.error_order_history(performed_at DESC);
```

## Integration Architecture

### Integration with COM Error Catalog

**Error Code Standardization:**
```java
@Service
public class ErrorReportingService {

    @Autowired
    private ErrorCatalogClient errorCatalogClient;

    @Autowired
    private ErrorOrderRepository orderRepository;

    public ErrorManagementOrder createError(ErrorReport report) {
        // 1. Retrieve error details from COM catalog
        ErrorCatalogEntry catalogEntry =
            errorCatalogClient.getError(report.getErrorCode());

        // 2. Determine category based on error code domain and description
        ErrorCategory category = determineCategory(catalogEntry);

        // 3. Determine priority based on severity and service
        ErrorPriority priority = determinePriority(
            catalogEntry.getSeverity(),
            report.getService()
        );

        // 4. Create error management order
        ErrorManagementOrder order = ErrorManagementOrder.builder()
            .errorCode(report.getErrorCode())
            .errorTitle(catalogEntry.getErrorTitleEn())
            .errorDescription(catalogEntry.getErrorDescriptionEn())
            .service(report.getService())
            .category(category)
            .priority(priority)
            .context(report.getContext())
            .exceptionDetails(report.getException() != null ?
                report.getException().getMessage() : null)
            .stackTrace(report.getException() != null ?
                getStackTraceAsString(report.getException()) : null)
            .correlationId(report.getCorrelationId())
            .requestId(report.getRequestId())
            .status(OrderStatus.CREATED)
            .createdAt(LocalDateTime.now())
            .createdBy("system")
            .build();

        // 5. Publish error created event
        message_busTemplate.send("cor.error.created", order);

        return orderRepository.save(order);
    }

    private ErrorCategory determineCategory(ErrorCatalogEntry entry) {
        String domain = entry.getErrorDomain();
        String technical = entry.getTechnicalDetails().toLowerCase();

        if (technical.contains("validation") || technical.contains("constraint")) {
            return ErrorCategory.VALIDATION;
        } else if (technical.contains("workflow") || technical.contains("state")) {
            return ErrorCategory.WORKFLOW;
        } else if (technical.contains("integration") || technical.contains("api")) {
            return ErrorCategory.INTEGRATION;
        } else if (technical.contains("compliance") || technical.contains("regulatory")) {
            return ErrorCategory.COMPLIANCE;
        }

        return ErrorCategory.WORKFLOW; // Default
    }

    private ErrorPriority determinePriority(String severity, String service) {
        // Critical errors always HIGH priority
        if ("C".equals(severity)) {
            return ErrorPriority.CRITICAL;
        }

        // High severity errors from HA services get HIGH priority
        if ("H".equals(severity) && isHAService(service)) {
            return ErrorPriority.HIGH;
        }

        // Medium severity or OT services get MEDIUM priority
        if ("M".equals(severity)) {
            return ErrorPriority.MEDIUM;
        }

        return ErrorPriority.LOW;
    }
}
```

### Cross-Service Error Reporting

**NUM Service Reporting:**
```java
@Service
public class CallnumberReservationService {

    @Autowired
    private CorErrorReportingClient corClient;

    public void reserveCallnumber(String callnumber, String customerId) {
        try {
            // Attempt reservation
            callnumberRepository.reserve(callnumber, customerId);
        } catch (ConstraintViolationException ex) {
            // Report error to COR
            corClient.reportError(
                ErrorReport.builder()
                    .errorCode("NUM-C-0001")
                    .service("NUM")
                    .operation("RESERVE")
                    .context(Map.of(
                        "callnumber", callnumber,
                        "customerId", customerId,
                        "onkz", extractONKZ(callnumber)
                    ))
                    .exception(ex)
                    .correlationId(MDC.get("correlationId"))
                    .build()
            );

            throw new CallnumberReservationException(
                "Reservation failed", ex);
        }
    }
}
```

**PRT Service Reporting:**
```java
@Service
public class PdaMessageProcessingService {

    @Autowired
    private CorErrorReportingClient corClient;

    public void processPdaMessage(PdaMessage message) {
        try {
            // Validate PDA message
            pdaValidator.validate(message);

            // Process porting
            portingService.process(message);
        } catch (PdaValidationException ex) {
            // Report validation error to COR
            corClient.reportError(
                ErrorReport.builder()
                    .errorCode("PRT-H-0042")
                    .service("PRT")
                    .operation("PDA_VALIDATION")
                    .context(Map.of(
                        "pdaMessageId", message.getId(),
                        "pdaType", message.getType(),
                        "validationError", ex.getValidationErrors()
                    ))
                    .exception(ex)
                    .correlationId(MDC.get("correlationId"))
                    .build()
            );

            throw ex; // Re-throw for upstream handling
        }
    }
}
```

### Event-Driven Architecture

**Message Bus Topics:**
```yaml
# Error event topics
cor.error.created:        # Published when error order created
cor.error.assigned:       # Published when order assigned to analyst
cor.error.resolved:       # Published when error resolved
cor.error.closed:         # Published when order closed

# Subscription topics (COR subscribes to these)
num.error.detected:       # NUM service error events
prt.error.detected:       # PRT service error events
com.error.detected:       # COM service error events
spe.error.detected:       # SPE service error events
```

**Event Schema (Avro):**
```json
{
  "type": "record",
  "name": "ErrorCreatedEvent",
  "namespace": "com.telekom.vnrm.cor.events",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "errorCode", "type": "string"},
    {"name": "service", "type": "string"},
    {"name": "category", "type": "string"},
    {"name": "priority", "type": "string"},
    {"name": "createdAt", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "correlationId", "type": ["null", "string"], "default": null}
  ]
}
```

## Monitoring & Metrics

### Key Performance Indicators (KPIs)

**Error Volume Metrics:**
- Total error orders created per hour/day/week
- Error volume by service (NUM, PRT, COM, SPE, NTW)
- Error volume by category (validation, workflow, integration, compliance)
- Error volume by priority (critical, high, medium, low)

**Resolution Metrics:**
- Mean Time To Resolution (MTTR) by priority
- Mean Time To Resolution (MTTR) by service
- Mean Time To Resolution (MTTR) by category
- Resolution success rate
- Escalation rate

**SLA Compliance Metrics:**
- OT SLA compliance (3-day response target)
- Percentage of orders resolved within SLA
- Overdue orders count
- Analyst workload distribution

**Service Health Indicators:**
- Error rate per service (errors/hour)
- Top 10 most frequent error codes
- Recurring error patterns
- Error trend analysis (increasing/decreasing)

### Prometheus Metrics

```yaml
# Error order metrics
cor_error_orders_total{service, category, priority, status}
cor_error_orders_created_total{service, category}
cor_error_orders_resolved_total{service, category}
cor_resolution_time_seconds{service, category, priority}
cor_sla_compliance_ratio{service}

# Analyst metrics
cor_analyst_workload{analyst}
cor_analyst_resolution_rate{analyst}
cor_analyst_avg_resolution_time{analyst}
```

### Grafana Dashboards

**Dashboard 1: Error Overview**
- Total active errors (gauge)
- Errors by service (pie chart)
- Errors by priority (bar chart)
- Error trend over time (time series)
- Top 10 error codes (table)

**Dashboard 2: Resolution Performance**
- Mean Time To Resolution (gauge)
- Resolution rate over time (time series)
- SLA compliance (gauge)
- Overdue orders (table)
- Analyst performance (bar chart)

**Dashboard 3: Service Health**
- Error rate per service (time series)
- Service error distribution (stacked area chart)
- Recurring errors (table)
- Error patterns heatmap

## Technology Stack

### Backend Technologies
- **Spring Boot 2.7.x**: Microservice framework
- **PostgreSQL 13+**: Error order storage
- **Spring Message Bus**: Event-driven error notifications
- **Spring Security**: Authentication and authorization
- **Spring Data JPA**: Database access
- **Liquibase**: Database migration

### Frontend Technologies
- **Angular 14+**: GUI framework
- **Angular Material**: UI components
- **NgRx**: State management (Redux pattern)
- **RxJS**: Reactive programming
- **WebSocket**: Real-time status updates

### Integration Technologies
- **Feign Client**: REST client for COM catalog
- **Message Bus**: Message bus integration
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization

## Best Practices

### Error Reporting
1. **Always use COM error catalog** - Standardized error codes only, never custom codes
2. **Include complete context** - All relevant data for investigation (callnumber, customer ID, operation)
3. **Correlation IDs** - Track errors across service boundaries using distributed tracing
4. **Severity classification** - Accurate priority assignment based on business impact
5. **Immediate reporting** - Report errors as soon as detected, don't batch

### Error Resolution
1. **Root cause first** - Understand the problem before attempting fixes
2. **Document everything** - Complete audit trail with notes, findings, actions
3. **Verify resolution** - Don't close orders without verification that issue is resolved
4. **Learn from errors** - Update processes and documentation to prevent recurrence
5. **Communication** - Notify affected parties promptly

### Integration
1. **Event-driven reporting** - Use message bus for error notifications (non-blocking)
2. **Async processing** - Don't block service operations waiting for COR response
3. **Circuit breakers** - Handle COR service unavailability gracefully
4. **Batch reporting** - For high-volume low-priority errors, batch to reduce load
5. **Retry logic** - Implement exponential backoff for failed error reporting

### Operational Excellence
1. **Monitor error patterns** - Watch for recurring errors and address root causes
2. **Trend analysis** - Identify increasing error rates early
3. **SLA tracking** - Monitor OT SLA compliance (3-day target)
4. **Analyst workload** - Balance assignments to prevent overload
5. **Continuous improvement** - Regular retrospectives on error management effectiveness

---

**See also:**
- [COM Architecture Reference](../vnrm-com-architecture/REFERENCE.md) - Error Catalog Integration
- [NUM Architecture Reference](../vnrm-num-architecture/REFERENCE.md) - Number Management Errors
- [PRT Architecture Reference](../vnrm-prt-architecture/REFERENCE.md) - Porting Errors
- [SPE Architecture Reference](../vnrm-spe-architecture/REFERENCE.md) - Legacy Integration Errors
- [NTW Architecture Reference](../vnrm-ntw-architecture/REFERENCE.md) - Network Errors
