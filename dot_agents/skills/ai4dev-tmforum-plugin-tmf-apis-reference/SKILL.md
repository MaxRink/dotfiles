---
name: ai4dev-tmforum-plugin-tmf-apis-reference
description: Complete catalog of TM Forum Open APIs (93+ specifications) for telecommunications architecture design. Use this skill when designing API integrations, selecting TMF APIs for business capabilities, mapping processes to APIs, or needing reference to TMF API specifications, resource models, and integration patterns.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/tmforum-plugin/skills/tmf-apis-reference by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# TMF APIs Reference

## Overview

This skill provides comprehensive reference to TM Forum Open APIs - a catalog of 93+ standardized RESTful API specifications for telecommunications operations.
TMF Open APIs enable interoperability across telecommunications ecosystems,covering product management,
customer management, service operations, resource management, operations & trouble, and finance.

## When to Use This Skill

Use this skill when:

- Designing API integrations for telecommunications systems
- Selecting appropriate TMF APIs for specific business capabilities
- Mapping business processes to technical API implementations
- Understanding TMF API resource models and operations
- Implementing standards-compliant telecommunications platforms
- Integrating with TMF-compliant vendor systems
- Creating ODA components with TMF API exposures
- Modernizing legacy systems with standards-based APIs

## TMF Open API Catalog

### Major API Families

TMF Open APIs are organized into families based on business domains:

#### 1. Product Management APIs

APIs for managing product offerings, orders, and inventory.

**Key APIs:**

- **TMF620** - Product Catalog Management: Manage product offerings, specifications, categories
- **TMF622** - Product Ordering Management: Submit, track, and manage product orders
- **TMF637** - Product Inventory Management: Track and manage product instances
- **TMF679** - Product Qualification Management: Check product availability and feasibility
- **TMF760** - Product Configuration: Configure complex product offerings

**Common Use Cases:**

- Product catalog browsing and management
- E-commerce product ordering
- Subscription management
- Product instance tracking
- Feasibility checks before ordering

#### 2. Customer Management APIs

APIs for managing customer data, parties, and accounts.

**Key APIs:**

- **TMF629** - Customer Management: CRUD operations on customer entities
- **TMF632** - Party Management: Manage individuals and organizations
- **TMF666** - Account Management: Customer accounts and balances
- **TMF667** - Document Management: Customer documents and attachments
- **TMF668** - Contact Management: Customer interactions and touchpoints

**Common Use Cases:**

- Customer onboarding and KYC
- Customer profile management
- Account setup and management
- Customer 360 views
- Document management

#### 3. Service Management APIs

APIs for managing service catalogs, orders, and instances.

**Key APIs:**

- **TMF633** - Service Catalog Management: Service offerings and specifications
- **TMF638** - Service Inventory Management: Active service instances
- **TMF640** - Service Activation and Configuration: Activate and configure services
- **TMF641** - Service Ordering Management: Service provisioning orders
- **TMF645** - Service Qualification: Service availability checks

**Common Use Cases:**

- Service provisioning and activation
- Service catalog management
- Service inventory tracking
- Configuration management
- Service ordering workflows

#### 4. Resource Management APIs

APIs for managing network and IT resources.

**Key APIs:**

- **TMF634** - Resource Catalog Management: Resource specifications
- **TMF639** - Resource Inventory Management: Physical and logical resources
- **TMF685** - Resource Pool Management: Resource pools and allocation
- **TMF664** - Resource Order Management: Resource provisioning orders
- **TMF652** - Resource Function Activation Configuration: Activate resource functions

**Common Use Cases:**

- Network resource management
- Infrastructure inventory
- Resource allocation and planning
- Network element tracking
- Capacity management

#### 5. Operations & Trouble APIs

APIs for operational management, trouble ticketing, and incident management.

**Key APIs:**

- **TMF621** - Trouble Ticket Management: Create and track trouble tickets
- **TMF656** - Alarm Management: Network alarms and events
- **TMF724** - Incident Management: Incident tracking and resolution
- **TMF623** - Service Level Agreement Management: SLA definitions and monitoring
- **TMF625** - Service Level Objective Management: SLO tracking

**Common Use Cases:**

- Trouble ticket management
- Alarm processing
- Incident response
- SLA monitoring
- Network operations center (NOC) operations

#### 6. Finance & Revenue Management APIs

APIs for billing, payment, and revenue management.

**Key APIs:**

- **TMF678** - Customer Bill Management: Generate and deliver customer bills
- **TMF676** - Payment Management: Process payments and refunds
- **TMF688** - Event Management: Usage events for billing
- **TMF635** - Usage Management: Usage data collection and rating
- **TMF654** - Prepay Balance Management: Prepaid account balances

**Common Use Cases:**

- Billing and invoicing
- Payment processing
- Usage-based charging
- Prepaid services
- Revenue assurance

#### 7. Advanced Capabilities APIs

APIs for advanced telecommunications services.

**Key APIs:**

- **TMF730** - Software and Compute Management: Cloud resources and VNFs
- **TMF663** - Shopping Cart Management: Multi-item cart management
- **TMF699** - Communication Management: Notifications and messaging
- **TMF669** - Party Role Management: Party roles and relationships
- **TMF931** - Open Gateway Onboarding: Network-as-a-Service APIs

**Common Use Cases:**

- Cloud service management
- E-commerce cart functionality
- Customer communications
- Network-as-a-Service offerings
- Multi-party collaborations

### Complete API List by Family

For detailed reference, see `references/api_catalog.md` which contains:

- Complete list of all 93+ TMF APIs
- Detailed descriptions for each API
- Version information
- Resource models
- Common operations
- Integration patterns
- Examples

## TMF API Common Patterns

All TMF Open APIs follow consistent patterns for interoperability:

### RESTful Design

- **HTTP Methods**: GET (retrieve), POST (create), PATCH (partial update), DELETE (remove)
- **Resource-Based URLs**: `/resource/{id}` patterns
- **Status Codes**: Standard HTTP response codes (200, 201, 400, 404, 500, etc.)
- **Content Type**: JSON (application/json)

### Resource Structure

```json
{
  "id": "unique-identifier",
  "href": "/resourceType/unique-identifier",
  "name": "Resource Name",
  "@type": "ResourceType",
  "@baseType": "BaseType",
  "@schemaLocation": "schema-url",
  // Resource-specific attributes
  "relatedParty": [
    {
      "id": "party-id",
      "role": "customer",
      "@referredType": "Individual"
    }
  ]
}
```

### HATEOAS Links

Resources include hyperlinks for navigation:

```json
{
  "id": "PO-123",
  "href": "/productOrdering/v5/productOrder/PO-123",
  "productOrderItem": [
    {
      "id": "1",
      "product": {
        "productOffering": {
          "id": "OFFER-5G",
          "href": "/productCatalog/v5/productOffering/OFFER-5G"
        }
      }
    }
  ]
}
```

### Pagination

For large result sets:

```text
GET /productOffering?offset=0&limit=20
```

Response includes:

```json
{
  "items": [...],
  "totalCount": 150,
  "offset": 0,
  "limit": 20
}
```

### Filtering

Query parameters for filtering:

```text
GET /productOffering?category=mobile&lifecycleStatus=Active
GET /customer?name.like=John&status=Active
```

### Event Notifications

TMF APIs support event-driven patterns:

- **Event Types**: created, attributeValueChange, stateChange, deleted
- **Hub Pattern**: Subscribe to event hubs for notifications
- **Event Structure**: Consistent event payload format

Example event:

```json
{
  "eventId": "evt-123",
  "eventTime": "2025-01-07T10:30:00Z",
  "eventType": "ProductOrderCreatedEvent",
  "event": {
    "productOrder": {
      "id": "PO-123",
      "href": "/productOrdering/v5/productOrder/PO-123"
    }
  }
}
```

### Error Responses

Standardized error format:

```json
{
  "code": "400",
  "reason": "Bad Request",
  "message": "Invalid product offering reference",
  "status": "400",
  "referenceError": "https://api.example.com/errors/400",
  "@type": "Error"
}
```

### Versioning

- APIs use semantic versioning (e.g., v4.0.0, v5.0.0)
- Version in URL path: `/productCatalogManagement/v5/productOffering`
- Backward compatibility within major versions

### Role-Based Access

Many APIs have role variants:

- **Admin APIs**: Full CRUD operations (create, read, update, delete)
- **Regular APIs**: Limited operations (typically read-only or restricted create)

## API Selection Guide

### By Business Capability

To select appropriate TMF APIs, map business capabilities:

| Business Capability | Primary TMF APIs | Supporting APIs |
|---------------------|------------------|-----------------|
| Product Catalog Management | TMF620 | TMF679 (qualification) |
| Order Management | TMF622, TMF641 | TMF620 (catalog), TMF637 (inventory) |
| Customer Management | TMF629, TMF632 | TMF666 (accounts), TMF668 (contacts) |
| Service Provisioning | TMF641, TMF640 | TMF638 (inventory), TMF633 (catalog) |
| Trouble Management | TMF621 | TMF656 (alarms), TMF724 (incidents) |
| Billing & Payment | TMF678, TMF676 | TMF688 (events), TMF635 (usage) |
| Resource Management | TMF639 | TMF634 (catalog), TMF685 (pools) |
| Network Operations | TMF656, TMF639 | TMF621 (tickets), TMF724 (incidents) |

### By eTOM Process

TMF APIs align with eTOM business processes:

**Operations → Fulfillment:**

- Order Handling: TMF622 (product orders), TMF641 (service orders)
- CRM Support: TMF629 (customer), TMF632 (party)
- Selling: TMF620 (catalog), TMF663 (shopping cart)

**Operations → Assurance:**

- Service Problem Management: TMF621 (trouble tickets)
- Service Management: TMF638 (service inventory), TMF640 (activation)
- Alarm Management: TMF656 (alarms)

**Operations → Billing:**

- Billing Management: TMF678 (customer bills)
- Payment Collection: TMF676 (payments)
- Usage Management: TMF688 (events), TMF635 (usage)

### By Integration Pattern

**Synchronous API Calls:**
Use for immediate responses:

- Catalog browsing (TMF620)
- Customer lookups (TMF629)
- Order submission (TMF622)
- Service queries (TMF638)

**Asynchronous Event-Driven:**
Use for long-running operations:

- Order fulfillment completion events
- Service activation notifications
- Alarm notifications
- Bill generation events

**Hub-Based Notifications:**
Subscribe to event hubs for:

- Product order state changes
- Service activation updates
- Alarm notifications
- Trouble ticket updates

## Integration Patterns

### Pattern 1: Catalog-Order-Inventory Flow

**Use Case**: Customer orders a product

**APIs**:

1. **TMF620** - Browse product catalog
2. **TMF679** - Check product qualification/feasibility
3. **TMF622** - Submit product order
4. **TMF641** - Provision service (triggered by order)
5. **TMF637** - Update product inventory (order completion)

**Flow**:

```text
Customer → GET /productOffering (TMF620)
         → POST /productQualification (TMF679)
         → POST /productOrder (TMF622)
[Order Processing]
         → Event: ProductOrderCreated
Fulfillment → POST /serviceOrder (TMF641)
         → Event: ServiceOrderCompleted
Inventory → POST /product (TMF637)
         → Event: ProductCreated
Customer ← Notification: Order Complete
```

### Pattern 2: Trouble-to-Resolution Flow

**Use Case**: Customer reports service problem

**APIs**:

1. **TMF621** - Create trouble ticket
2. **TMF638** - Query affected services
3. **TMF639** - Check resource status
4. **TMF656** - Review related alarms
5. **TMF621** - Update and close ticket

**Flow**:

```text
Customer → POST /troubleTicket (TMF621)
NOC → GET /service (TMF638) - identify affected services
    → GET /resource (TMF639) - check infrastructure
    → GET /alarm (TMF656) - review alarms
    → [Perform remediation]
    → PATCH /troubleTicket/{id} (TMF621) - update status
    → Event: TroubleTicketResolved
Customer ← Notification: Issue Resolved
```

### Pattern 3: Usage-to-Bill Flow

**Use Case**: Generate customer bill from usage

**APIs**:

1. **TMF688** - Capture usage events
2. **TMF635** - Rate usage
3. **TMF678** - Generate customer bill
4. **TMF676** - Collect payment

**Flow**:

```text
Network → POST /event (TMF688) - capture usage events
Rating Engine → POST /usage (TMF635) - rate usage
Billing → POST /customerBill (TMF678) - generate bill
        → Event: CustomerBillCreated
Customer ← GET /customerBill (TMF678) - view bill
         → POST /payment (TMF676) - make payment
         → Event: PaymentCreated
```

## API Design Best Practices

### 1. Start with Business Capabilities

- Identify business capabilities first
- Map capabilities to TMF APIs
- Don't force-fit APIs; extend if needed

### 2. Use Standard Resource Models

- Align entities with SID model
- Use TMF attribute names and types
- Extend via `characteristic` arrays for custom attributes

### 3. Implement Proper Error Handling

- Use standard HTTP status codes
- Return TMF error response format
- Provide actionable error messages
- Log errors for debugging

### 4. Design for Scalability

- Implement pagination for large result sets
- Use filtering to reduce payload sizes
- Cache reference data (catalogs, specifications)
- Consider async patterns for long operations

### 5. Leverage Events

- Publish events for state changes
- Enable event-driven orchestration
- Reduce polling with notifications
- Support loosely coupled systems

### 6. Ensure Security

- Implement OAuth2/OpenID Connect
- Use role-based access control
- Validate all inputs
- Encrypt sensitive data
- Rate limit API calls

### 7. Version Properly

- Use semantic versioning
- Maintain backward compatibility in minor versions
- Deprecate gracefully with notice
- Document breaking changes

### 8. Document Thoroughly

- Provide OpenAPI/Swagger specs
- Include request/response examples
- Document error scenarios
- Explain business logic and workflows

## Resources

### references/api_catalog.md

Complete catalog of all 93+ TMF Open APIs with detailed descriptions, resource models, operations, versions, and integration examples.

**Use when**: Detailed API reference needed for specific APIs, understanding resource structures, or exploring complete API capabilities.

### references/api_examples.md

Real-world API request/response examples for common use cases across different API families.

**Use when**: Implementing specific integration scenarios, understanding API payload structures, or learning by example.

## Quick Reference

**Most Common APIs:**

- TMF620 (Product Catalog) - Product offerings
- TMF622 (Product Ordering) - Orders
- TMF629 (Customer) - Customer data
- TMF638 (Service Inventory) - Active services
- TMF621 (Trouble Ticket) - Problem management
- TMF678 (Customer Bill) - Billing

**API Versions:**

- v4.x (older, widely adopted)
- v5.x (current, recommended for new implementations)

**Base URL Pattern:**

```text
https://api.example.com/{apiName}/{version}/{resource}
Example: https://api.example.com/productCatalogManagement/v5/productOffering
```

**Authentication:**
Typically OAuth2 Bearer tokens:

```text
Authorization: Bearer {access_token}
```

---

**Remember**: TMF Open APIs provide standardization, but implementation details vary. Always consult actual API specifications and vendor documentation for deployment-specific information.
